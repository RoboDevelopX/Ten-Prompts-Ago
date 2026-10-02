"""Ten Prompts Ago: log decisions and fixed bugs, export a CONTEXT.md for your agent."""

import os

from flask import Flask, Response, abort, redirect, render_template, request, url_for

import db
from context_export import build_context

# SQLite's largest integer: bigger ids in a URL can't exist, so they 404 instead of erroring.
MAX_ID = 2**63 - 1

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

    def render_page(form=None, errors=None, status=200, export_open=False,
                    edit_id=None, edit_form=None, edit_errors=None):
        entries = db.list_entries(database(), LOCAL_OWNER)
        groups = {kind: [e for e in entries if e["kind"] == kind] for kind in db.KINDS}
        if edit_id is not None and edit_form is None:
            # Open the edit form with the entry's saved values (ignore stale ids).
            entry = next((e for e in entries if e["id"] == edit_id), None)
            edit_form = entry
            if entry is None:
                edit_id = None
        page = render_template(
            "index.html",
            groups=groups,
            total=len(entries),
            form=form or {"kind": "decision", "text": "", "reason": ""},
            errors=errors or {},
            edit_id=edit_id,
            edit_form=edit_form,
            edit_errors=edit_errors or {},
            text_max=TEXT_MAX,
            reason_max=REASON_MAX,
            export_open=export_open,
            context=build_context(entries) if export_open else None,
        )
        return page, status

    @app.get("/")
    def index():
        return render_page(
            export_open=request.args.get("export") == "1",
            edit_id=request.args.get("edit", type=int),
        )

    @app.post("/entries")
    def add():
        form, errors = read_entry_form(request.form)
        if errors:
            return render_page(form=form, errors=errors, status=400)
        db.add_entry(database(), LOCAL_OWNER, form["kind"], form["text"], form["reason"])
        return redirect(url_for("index") + "#entries")

    @app.post(f"/entries/<int(max={MAX_ID}):entry_id>/edit")
    def edit(entry_id):
        if db.get_entry(database(), LOCAL_OWNER, entry_id) is None:
            abort(404)
        form, errors = read_entry_form(request.form)
        if errors:
            return render_page(edit_id=entry_id, edit_form=form, edit_errors=errors, status=400)
        if not db.update_entry(database(), LOCAL_OWNER, entry_id, form["kind"], form["text"], form["reason"]):
            abort(404)
        return redirect(url_for("index") + f"#entry-{entry_id}")

    @app.post(f"/entries/<int(max={MAX_ID}):entry_id>/delete")
    def delete(entry_id):
        if not db.delete_entry(database(), LOCAL_OWNER, entry_id):
            abort(404)
        return redirect(url_for("index") + "#entries")

    @app.get("/export/CONTEXT.md")
    def download():
        context = build_context(db.list_entries(database(), LOCAL_OWNER))
        if context is None:
            # Nothing logged: show the friendly message instead of an empty file.
            return redirect(url_for("index", export=1) + "#export")
        return Response(
            context,
            mimetype="text/markdown",
            headers={"Content-Disposition": "attachment; filename=CONTEXT.md"},
        )

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
