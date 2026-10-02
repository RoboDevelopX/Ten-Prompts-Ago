"""Ten Prompts Ago: log decisions and fixed bugs, export a CONTEXT.md for your agent."""

import os

from flask import Flask, redirect, render_template, request, url_for

import db

# Until each visitor gets their own list (slice 4), everything belongs to one local owner.
LOCAL_OWNER = "local"

TEXT_MAX = 280
REASON_MAX = 500


def create_app(config=None):
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = os.environ.get("DATABASE_PATH") or os.path.join(
        app.instance_path, "ten_prompts_ago.db"
    )
    if config:
        app.config.update(config)
    db.init_db(app.config["DATABASE_PATH"])

    def database():
        return app.config["DATABASE_PATH"]

    def render_page(form=None, errors=None, status=200):
        entries = db.list_entries(database(), LOCAL_OWNER)
        groups = {kind: [e for e in entries if e["kind"] == kind] for kind in db.KINDS}
        page = render_template(
            "index.html",
            groups=groups,
            total=len(entries),
            form=form or {"kind": "decision", "text": "", "reason": ""},
            errors=errors or {},
            text_max=TEXT_MAX,
            reason_max=REASON_MAX,
        )
        return page, status

    @app.get("/")
    def index():
        return render_page()

    @app.post("/entries")
    def add():
        form, errors = read_entry_form(request.form)
        if errors:
            return render_page(form=form, errors=errors, status=400)
        db.add_entry(database(), LOCAL_OWNER, form["kind"], form["text"], form["reason"])
        return redirect(url_for("index") + "#entries")

    return app


def one_line(value):
    """Collapse line breaks and repeated spaces: each entry becomes one line in CONTEXT.md."""
    return " ".join(value.split())


def read_entry_form(data):
    """Clean the submitted fields and return (form, errors)."""
    form = {
        "kind": data.get("kind", "").strip(),
        "text": one_line(data.get("text", "")),
        "reason": one_line(data.get("reason", "")),
    }
    errors = {}
    if form["kind"] not in db.KINDS:
        errors["kind"] = "Choose Decision or Fixed bug."
        form["kind"] = "decision"
    if not form["text"]:
        errors["text"] = "Write what was decided or fixed."
    elif len(form["text"]) > TEXT_MAX:
        errors["text"] = f"Keep it to one sentence ({TEXT_MAX} characters max)."
    if not form["reason"]:
        errors["reason"] = "Add the reason, so your agent knows why."
    elif len(form["reason"]) > REASON_MAX:
        errors["reason"] = f"Keep the reason short ({REASON_MAX} characters max)."
    return form, errors


app = create_app()
