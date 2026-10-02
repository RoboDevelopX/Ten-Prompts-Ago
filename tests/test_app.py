import re

from app import create_app
from conftest import add


def entry_texts(html, kind):
    """Entry sentences shown under one group, in page order."""
    group = re.search(rf'id="group-{kind}".*?(?=id="group-|</section>)', html, re.S)
    assert group, f"group {kind} not rendered"
    return re.findall(r'<p class="entry-text">(.*?)</p>', group.group(0))


def test_first_visit_shows_empty_prompt(client):
    html = client.get("/").get_data(as_text=True)
    assert "Nothing logged yet" in html
    assert 'id="group-decision"' not in html


def test_add_decision_and_bug_land_in_their_groups(client):
    assert add(client, "decision", "Use SQLite, not Postgres", "One user, no server to run").status_code == 302
    assert add(client, "bug", "Export sent an empty file", "Users pasted a blank file").status_code == 302

    html = client.get("/").get_data(as_text=True)
    assert entry_texts(html, "decision") == ["Use SQLite, not Postgres"]
    assert entry_texts(html, "bug") == ["Export sent an empty file"]
    assert "One user, no server to run" in html
    assert "Decisions <span class=\"count\">· 1</span>" in html
    assert "Fixed bugs <span class=\"count\">· 1</span>" in html
    assert "Nothing logged yet" not in html


def test_newest_entry_first_within_group(client):
    add(client, "decision", "First decision", "r1")
    add(client, "decision", "Second decision", "r2")
    add(client, "decision", "Third decision", "r3")
    html = client.get("/").get_data(as_text=True)
    assert entry_texts(html, "decision") == ["Third decision", "Second decision", "First decision"]
    assert "No fixed bugs yet." in html


def test_redirect_after_save_returns_to_list(client):
    response = add(client, "decision", "No login for v1", "Single local user")
    assert response.headers["Location"].endswith("/#entries")


def test_whitespace_is_trimmed(client):
    add(client, "decision", "   Use Flask   ", "  Full control of the page  ")
    html = client.get("/").get_data(as_text=True)
    assert entry_texts(html, "decision") == ["Use Flask"]
    assert "Why:</span> Full control of the page<" in html


def test_empty_sentence_is_rejected_and_reason_kept(client):
    response = add(client, "bug", "   ", "Because it broke twice")
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Write what was decided or fixed." in html
    assert ">Because it broke twice</textarea>" in html
    assert 'value="bug" checked' in html
    assert "Nothing logged yet" in html


def test_empty_reason_is_rejected_and_sentence_kept(client):
    response = add(client, "decision", "Use SQLite", "")
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Add the reason, so your agent knows why." in html
    assert 'value="Use SQLite"' in html
    assert "Nothing logged yet" in client.get("/").get_data(as_text=True)


def test_line_breaks_collapse_to_one_line(client):
    # Browsers submit textarea line breaks as CRLF; each entry must stay one line.
    reason = "a" * 498 + "\r\n" + "b"
    assert add(client, "decision", "Keep it\r\non one line", reason).status_code == 302
    html = client.get("/").get_data(as_text=True)
    assert entry_texts(html, "decision") == ["Keep it on one line"]
    assert "a" * 498 + " b<" in html


def test_unknown_kind_is_rejected(client):
    response = add(client, "feature", "Add tags", "Nice to have")
    assert response.status_code == 400
    assert "Choose Decision or Fixed bug." in response.get_data(as_text=True)


def test_overlong_sentence_is_rejected(client):
    response = add(client, "decision", "x" * 281, "too long")
    assert response.status_code == 400
    assert "280 characters max" in response.get_data(as_text=True)


def test_html_in_entries_is_escaped(client):
    add(client, "decision", "<script>alert(1)</script>", "<b>bold</b>")
    html = client.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_entries_survive_a_restart(db_path, client):
    add(client, "decision", "Use SQLite, not Postgres", "One user")
    add(client, "bug", "Login page crept back in", "No login for v1")

    restarted = create_app({"TESTING": True, "DATABASE_PATH": db_path}).test_client()
    html = restarted.get("/").get_data(as_text=True)
    assert entry_texts(html, "decision") == ["Use SQLite, not Postgres"]
    assert entry_texts(html, "bug") == ["Login page crept back in"]


def test_export_button_is_shown_before_export_is_opened(client):
    html = client.get("/").get_data(as_text=True)
    assert 'href="/?export=1#export"' in html
    assert "context-preview" not in html


def test_export_with_nothing_logged_shows_message(client):
    html = client.get("/?export=1").get_data(as_text=True)
    assert "Nothing to export yet. Log a decision or a fixed bug first." in html
    assert "context-preview" not in html


def test_download_with_nothing_logged_redirects_to_message(client):
    response = client.get("/export/CONTEXT.md")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/?export=1#export")


def test_export_preview_shows_grouped_context(client):
    add(client, "decision", "Use SQLite, not Postgres", "One user, no server to run")
    add(client, "bug", "Export sent an empty file", "Users pasted a blank file")
    html = client.get("/?export=1").get_data(as_text=True)
    assert '<pre id="context-preview"' in html
    assert "## Decisions\n- Use SQLite, not Postgres. Why: One user, no server to run." in html
    assert "## Don&#39;t repeat these\n- Export sent an empty file. Do not reintroduce this." in html
    assert 'data-copy-target="context-preview"' in html
    assert 'href="/export/CONTEXT.md"' in html
    # No `download` attribute: with it, a browser would save the empty-export
    # redirect page as CONTEXT.md instead of showing the message.
    assert re.search(r'<a [^>]*href="/export/CONTEXT.md"[^>]*\bdownload\b', html) is None


def test_download_returns_the_same_file(client):
    add(client, "decision", "Use SQLite, not Postgres", "One user")
    add(client, "bug", "Export sent an empty file", "Users pasted a blank file")
    response = client.get("/export/CONTEXT.md")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=CONTEXT.md"
    assert response.mimetype == "text/markdown"
    body = response.get_data(as_text=True)
    assert body.startswith("# Project context\n")
    assert "- Use SQLite, not Postgres. Why: One user.\n" in body
    assert "## Don't repeat these\n" in body


def test_export_lists_newest_first(client):
    add(client, "decision", "First", "r")
    add(client, "decision", "Second", "r")
    body = client.get("/export/CONTEXT.md").get_data(as_text=True)
    assert body.index("Second") < body.index("First")


def test_export_reflects_entries_added_later(client):
    add(client, "decision", "Use SQLite", "One user")
    first = client.get("/export/CONTEXT.md").get_data(as_text=True)
    add(client, "bug", "Login page came back", "No login for v1")
    second = client.get("/export/CONTEXT.md").get_data(as_text=True)
    assert "Login page came back" not in first
    assert "Login page came back" in second


def test_export_escapes_html_in_preview(client):
    add(client, "decision", "<img src=x onerror=alert(1)>", "r")
    html = client.get("/?export=1").get_data(as_text=True)
    assert "<img src=x" not in html
    body = client.get("/export/CONTEXT.md").get_data(as_text=True)
    assert "- <img src=x onerror=alert(1)>. Why: r.\n" in body
