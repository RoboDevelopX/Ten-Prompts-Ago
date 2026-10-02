---
doc: checklist
status: approved
---

# Build Checklist

Build mode: learn (learner: "I have forgotten parts of it since I had done it long time back")

## Slices

- [ ] **1. You can log a decision or fixed bug and see it in the grouped list**
  Becomes usable: A running Flask app with the Apple-style page; typing a sentence and reason, picking Decision or Fixed bug, and saving shows the entry at the top of its group. Entries are already saved in SQLite, so they survive a restart.
  Why now: Proves the whole path (scaffold, form, route, SQLite, template, styling) on the first slice, so every later slice has a working page to land on. SQLite is folded in here because it is the store, not a separate layer.
  PRD ref: `prd.md > The Core Journey` (steps 1-3, 7), `prd.md > Adding an entry`, `prd.md > Viewing the running list`, `prd.md > Look and Feel`
  Spec ref: `spec.md > Flask app and routes (app.py)`, `spec.md > Storage (db.py)`, `spec.md > Page template (templates/index.html)`, `spec.md > Styles and script (static/style.css, static/app.js)`, `spec.md > Data Model`, `spec.md > File Structure`
  Build: Create `requirements.txt`, `.gitignore` entries, `db.py` (table with `owner` column; a fixed local owner id until slice 4), `app.py` with `GET /` and `POST /entries` (validation, inline error, typed text kept), `templates/index.html` (header, form, two groups with counts, empty prompt), `static/style.css` per Look and Feel, and a README with run instructions.
  Verify (mechanical): `pytest tests/test_app.py` covers add (decision and bug), grouping, newest-first, counts, empty-field rejection, and persistence across a fresh app instance; start `flask --app app run` and fetch `/` with no errors; take a screenshot of the page with two entries.
  Learner check: Run the app (README steps), open http://127.0.0.1:5000, add "Use SQLite, not Postgres" as a Decision with a reason and one Fixed bug, restart the app, and confirm both are still there and the page feels like the Apple-style look you pictured.
  Commit: `Log decisions and fixed bugs in a grouped list`

- [ ] **2. You can export an agent-ready CONTEXT.md, copy it, or download it**
  Becomes usable: Export shows the generated `CONTEXT.md` (intro line, Decisions, Don't repeat these, one imperative line plus "Why:" each) with Copy and Download; with nothing logged it shows "Nothing to export yet. Log a decision or a fixed bug first."
  Why now: This is the kernel. It comes right after the first usable list so the most important behavior, and the story's open question of whether an agent actually follows the file, gets tested early.
  PRD ref: `prd.md > Exporting CONTEXT.md`, `prd.md > The Core Journey` (steps 5-6), `prd.md > States and Boundaries` (first use)
  Spec ref: `spec.md > Context export (context_export.py)`, `spec.md > Flask app and routes (app.py)`, `spec.md > Styles and script (static/style.css, static/app.js)`, `spec.md > Important Failure Modes`, `spec.md > Decisions and Open Issues` (useful unknown)
  Build: `context_export.py` with `build_context(entries)`; `?export=1` preview area; `GET /export/CONTEXT.md` download (redirect to the empty message when nothing is logged); `static/app.js` Copy button with "Copied" and a select-text fallback.
  Verify (mechanical): `pytest tests/test_export.py` checks section order, newest-first, "Why:" lines, trailing periods, omitted empty sections, and `None` for no entries; `tests/test_app.py` checks the download headers and the empty-export message; a browser run (Playwright) clicks Copy and reads the clipboard. Paste a real export into a coding agent and ask it to do something a logged decision rules out; record what it did under Revisions.
  Learner check: Click Export, check the preview reads like instructions you'd want your agent to follow, click Copy and paste it somewhere, click Download and open the file; then clear your entries (or use a fresh browser) and confirm Export shows the "Nothing to export yet" message.
  Commit: `Export an agent-ready CONTEXT.md with copy and download`

- [ ] **3. You can edit or delete an entry**
  Becomes usable: Each entry has Edit (inline form to change type, sentence, reason; Save or Cancel) and Delete (with an "are you sure?" prompt); changes show in the list and in the next export.
  Why now: Builds on a working list and export, and matters because the export must stay accurate when decisions change. Lower risk than the kernel, so it comes after it.
  PRD ref: `prd.md > Editing and deleting an entry`, `prd.md > The Core Journey` (step 4)
  Spec ref: `spec.md > Flask app and routes (app.py)`, `spec.md > Storage (db.py)`, `spec.md > Page template (templates/index.html)`, `spec.md > Styles and script (static/style.css, static/app.js)`
  Build: `?edit=<id>` inline form, `POST /entries/<id>/edit` (same validation as add), `POST /entries/<id>/delete`, delete confirmation in `app.js`, 404 for unknown ids.
  Verify (mechanical): `pytest` covers edit (including switching type), edit validation, delete, 404 on a missing id, and that export reflects edits and deletions.
  Learner check: Edit an entry's reason and switch a Decision to a Fixed bug, delete another (cancel the prompt once first), then Export and confirm the file matches the list.
  Commit: `Edit and delete entries`

- [ ] **4. Each visitor on the public link gets their own list**
  Becomes usable: Two different browsers see two separate lists; neither can see, edit, or delete the other's entries. With `PUBLIC_DEMO=1`, a footer note says it's a demo whose entries reset.
  Why now: Only matters once the app is public, and it wraps every route that already works, so it lands last and is checked against all of them.
  PRD ref: `prd.md > States and Boundaries` (who can see what)
  Spec ref: `spec.md > Flask app and routes (app.py)` (visitor id), `spec.md > Data Model`, `spec.md > Where It Runs and How Someone Tries It`
  Build: `tpa_visitor` cookie (uuid4, HttpOnly, SameSite=Lax, one year) set on first request; replace the fixed local owner with it in every route; `PUBLIC_DEMO` footer; `gunicorn app:app` start check.
  Verify (mechanical): `pytest` uses two test clients: each sees only its own entries, and editing, deleting, or exporting with another visitor's id returns 404 or omits the entry; the cookie is set with HttpOnly and SameSite=Lax; `gunicorn app:app` starts and serves `/`.
  Learner check: Open the app in a normal window and a private window, add different entries in each, and confirm each window only shows its own.
  Commit: `Give each visitor their own list`

## Hands-on Checkpoints

- [ ] Early usable behavior explored — after slice 2 (list plus export, the kernel)
- [ ] Final kick-the-tires exploration and feedback completed

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence: not started
Route and stops: not started
Edit outcome: not started
Reflection: not started
Activity mode: not started

## Revisions
