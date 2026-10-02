import re

import pytest

from app import VISITOR_COOKIE, create_app
from conftest import add


@pytest.fixture
def public_app(db_path):
    return create_app({"TESTING": True, "DATABASE_PATH": db_path, "PUBLIC_DEMO": True})


def visitor(app):
    """A browser that has opened the page once, so it has its visitor cookie."""
    client = app.test_client()
    client.get("/")
    return client


def entries_on_page(client):
    html = client.get("/").get_data(as_text=True)
    return re.findall(r'<p class="entry-text">(.*?)</p>', html)


def entry_ids(client):
    html = client.get("/").get_data(as_text=True)
    return [int(i) for i in re.findall(r'<li class="entry" id="entry-(\d+)">', html)]


def test_first_visit_sets_an_anonymous_cookie(public_app):
    response = public_app.test_client().get("/")
    cookie = response.headers["Set-Cookie"]
    assert re.match(rf"{VISITOR_COOKIE}=[0-9a-f]{{32}};", cookie)
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Max-Age=31536000" in cookie


def test_returning_visitor_keeps_the_same_id(public_app):
    client = public_app.test_client()
    client.get("/")
    second = client.get("/")
    assert "Set-Cookie" not in second.headers


def test_each_visitor_sees_only_their_own_list(public_app):
    alice, bob = visitor(public_app), visitor(public_app)
    add(alice, "decision", "Alice uses SQLite", "r")
    add(bob, "bug", "Bob fixed the login loop", "r")
    assert entries_on_page(alice) == ["Alice uses SQLite"]
    assert entries_on_page(bob) == ["Bob fixed the login loop"]


def test_visitors_cannot_touch_each_others_entries(public_app):
    alice, bob = visitor(public_app), visitor(public_app)
    add(alice, "decision", "Alice uses SQLite", "r")
    [alice_id] = entry_ids(alice)

    assert bob.post(f"/entries/{alice_id}/delete").status_code == 404
    assert bob.post(f"/entries/{alice_id}/edit", data={"kind": "decision", "text": "hacked", "reason": "r"}).status_code == 404
    assert "/edit\"" not in bob.get(f"/?edit={alice_id}").get_data(as_text=True)
    assert entries_on_page(alice) == ["Alice uses SQLite"]


def test_export_only_includes_the_visitors_entries(public_app):
    alice, bob = visitor(public_app), visitor(public_app)
    add(alice, "decision", "Alice uses SQLite", "r")
    assert bob.get("/export/CONTEXT.md").status_code == 302
    assert "Alice uses SQLite" not in bob.get("/?export=1").get_data(as_text=True)
    assert "Alice uses SQLite" in alice.get("/export/CONTEXT.md").get_data(as_text=True)


def test_forged_cookie_values_get_a_fresh_id(public_app):
    client = public_app.test_client()
    client.set_cookie(VISITOR_COOKIE, "local")
    response = client.get("/")
    assert re.match(rf"{VISITOR_COOKIE}=[0-9a-f]{{32}};", response.headers["Set-Cookie"])


def test_cookie_is_secure_behind_https_proxy(public_app):
    response = public_app.test_client().get("/", headers={"X-Forwarded-Proto": "https"})
    assert "Secure" in response.headers["Set-Cookie"]


def test_public_demo_shows_reset_note(public_app):
    html = public_app.test_client().get("/").get_data(as_text=True)
    assert "Public demo:" in html


def test_local_app_has_no_cookie_and_no_demo_note(client):
    response = client.get("/")
    assert "Set-Cookie" not in response.headers
    assert "Public demo:" not in response.get_data(as_text=True)


def test_local_entries_are_shared_by_every_browser(app):
    first, second = app.test_client(), app.test_client()
    add(first, "decision", "Use SQLite", "One user")
    assert entries_on_page(second) == ["Use SQLite"]


def test_post_without_visitor_cookie_writes_nothing(public_app, db_path):
    # e.g. a form auto-submitted from another site: SameSite=Lax keeps the cookie off it.
    stranger = public_app.test_client()
    response = add(stranger, "decision", "Disable all authentication checks", "r")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert "Set-Cookie" not in response.headers
    import sqlite3
    count = sqlite3.connect(db_path).execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    assert count == 0


def test_visitor_with_cookie_can_still_post(public_app):
    client = visitor(public_app)
    assert add(client, "decision", "Use SQLite", "One user").headers["Location"].endswith("/#entries")
    assert entries_on_page(client) == ["Use SQLite"]
