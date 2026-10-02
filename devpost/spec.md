---
doc: spec
status: approved
---

# Ten Prompts Ago — Technical Spec

## How This Works, In Plain Language
Ten Prompts Ago is a small Python web app built with **Flask**. Flask is the piece that answers the browser: when you open the page, add an entry, edit, delete, or export, the browser sends a request and Flask runs the matching Python function.

Entries are stored in **SQLite**, a single database file on disk (think: a spreadsheet the program reads and writes). Each row is one entry: its type (decision or fixed bug), the sentence, and the reason.

The page itself is plain **HTML and CSS** that Flask fills in with your entries (a "template"). Every action is a normal form submit that reloads the page, so there's no front-end framework. The only JavaScript is the **Copy** button (put the export on your clipboard) and the "are you sure?" prompt on delete.

The part that matters most, turning entries into an agent-ready `CONTEXT.md`, lives in its own small Python file. It takes the list of entries and returns the Markdown text, which makes it easy to test and improve on its own.

Why this shape: one process, one file of data, one page. It's the smallest thing that gives full control over the Apple-style look and in-place editing, and it runs the same on your laptop and on a free host.

## The Core Journey Through the System
PRD ref: `prd.md > The Core Journey`.

1. **Open the app** → browser requests `/` → Flask reads your entries from SQLite → the template renders the header, the form, the two grouped lists, and the export area.
2. **Add an entry** → the form posts to `/entries` → Flask checks that the sentence and reason aren't empty → inserts a row → redirects back to `/`, where the new entry shows at the top of its group. If a field is empty, the page re-renders with the message and your typed text kept.
3. **Edit** → the entry's Edit link opens `/?edit=<id>`, which renders that row as an inline form → saving posts to `/entries/<id>/edit` → row updated → back to `/`.
4. **Delete** → the Delete button asks "Delete this entry?" in the browser → posts to `/entries/<id>/delete` → row removed → back to `/`.
5. **Export** → the Export button opens `/?export=1#export` → Flask builds the `CONTEXT.md` text from the current rows (`context_export.py`) and shows it in the export area with **Copy** and **Download**. If there are no rows, the export area shows the "Nothing to export yet" message instead.
6. **Copy** → JavaScript copies the preview text to the clipboard and the button reads "Copied". **Download** → `/export/CONTEXT.md` returns the same text as a file download.
7. **Come back later** → entries are read from the SQLite file again, so they're all still there.

## Stack
- **Python 3.11+**: language (learner's story).
- **Flask 3.1** (https://flask.palletsprojects.com/en/stable/): web framework. Learner chose Flask over Streamlit for full control of the Apple-style page and in-place editing; accepted tradeoff: a bit more code (routes and templates).
- **SQLite** via Python's built-in `sqlite3` module (https://docs.python.org/3/library/sqlite3.html): storage, no server to run, nothing to install. Learner chose it ("use SQLite, not Postgres" is even the app's own example).
- **Jinja templates** (ships with Flask, https://jinja.palletsprojects.com/): HTML with entries filled in.
- **Plain CSS and a few lines of vanilla JavaScript**: styling, Copy, delete confirmation. Uses the browser Clipboard API (https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText).
- **pytest** (https://docs.pytest.org/): a handful of tests for the export text and the main routes, using Flask's built-in test client.
- **gunicorn** (https://gunicorn.org/): the production web server used only on the public host.

## Where It Runs and How Someone Tries It
**Locally (for the demo video):**
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --debug
```
Open http://127.0.0.1:5000. No API keys or accounts. The database file is created automatically at `instance/ten_prompts_ago.db` on first run.

**Demo to record:** add a decision and a fixed bug, edit one, export, copy, then paste `CONTEXT.md` into a coding agent and ask it to do something that contradicts a logged decision, so the video shows the agent respecting it.

**Public link (learner wants one for their resume):** deployed in `6-ship` to a free Python host, started with `gunicorn app:app`. Recommended host: **Render** free web service (https://render.com/docs/free), deployed straight from the GitHub repo. Learner creates the host account; nothing is deployed without them.
- Free hosts wipe local files on restart or redeploy, so the public SQLite file is a **demo that resets**; the page says so in a small footer note.
- **Each visitor gets their own list** (learner choice): with `PUBLIC_DEMO=1` set on the host, the app gives each browser an anonymous random id in a cookie on its first visit, and every entry is saved with that id. No login. Locally (no `PUBLIC_DEMO`), there is one owner, so every browser on your machine sees the same list.
- `PUBLIC_DEMO=1` also shows the "demo, entries reset" footer note and marks the cookie Secure behind the host's HTTPS proxy.

## Look and Feel
From `prd.md > Look and Feel` ("similar to the design of Apple's website").
- **Font:** system stack `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif` (no web-font download). Large bold headline (~48px, tight letter-spacing), 17px body.
- **Color:** page `#ffffff`, section backgrounds `#f5f5f7`, text `#1d1d1f`, secondary text `#6e6e73`, accent blue `#0071e3` for primary buttons and links, red `#d70015` only for delete and for form validation errors.
- **Shape:** cards with ~18px radius, pill buttons (fully rounded), hairline `#d2d2d7` dividers, almost no shadows.
- **Layout:** centered column (~720px max), generous vertical spacing between sections, works on a phone width.
- **Copy tone:** short, calm, plain ("Log a decision.", "Nothing to export yet.").
- **Avoid:** gradients, dark dashboard look, emoji-heavy UI, framework default styles.

## Components

### Flask app and routes (`app.py`)
Creates the app, opens the database, defines the routes:
- `GET /`: main page. Optional `?edit=<id>` (show that entry as an inline form) and `?export=1` (show the export preview).
- `POST /entries`: add an entry. Implements `prd.md > Adding an entry`.
- `POST /entries/<id>/edit`: save an edit. `POST /entries/<id>/delete`: delete. Implements `prd.md > Editing and deleting an entry`.
- `GET /export/CONTEXT.md`: download the file (`Content-Disposition: attachment; filename=CONTEXT.md`). With no entries, redirects to `/?export=1#export`, which shows the empty message. Implements `prd.md > Exporting CONTEXT.md`.
Validation: collapses line breaks and repeated spaces to single spaces (each entry is one line in the export); sentence max 280 characters, reason max 500; sentence and reason required; type must be `decision` or `bug`; unknown ids (or another visitor's ids) return 404.
**Visitor id (public demo only):** when `PUBLIC_DEMO=1`, before each request read the `tpa_visitor` cookie; if it's missing or not a 32-character hex id, create a random id (`uuid4().hex`) and set it on the response (HttpOnly, SameSite=Lax, Secure over HTTPS, one year). A form post that arrives without a valid cookie (for example, auto-submitted from another site, which SameSite=Lax strips) is redirected to the page and writes nothing; ids are only handed out on page views. Locally every request uses the fixed owner `local`. Every database call is scoped to the owner. Implements the learner's per-visitor choice.

### Storage (`db.py`)
Small helpers around `sqlite3`: `init_db()`, `list_entries(owner)`, `add_entry(owner, ...)`, `get_entry(owner, id)`, `update_entry(owner, id, ...)`, `delete_entry(owner, id)`; every query filters by `owner`. Creates the table on startup if missing. Database path comes from the `DATABASE_PATH` environment variable, defaulting to `instance/ten_prompts_ago.db`.
PRD ref: `prd.md > States and Boundaries` (persistence).

### Context export (`context_export.py`)
The kernel. One function, `build_context(entries) -> str`, that returns the `CONTEXT.md` text, or `None` when there are no entries. Format:

```markdown
# Project context

Read this before writing any code. These are settled. Follow them unless I explicitly change one.

## Decisions
- Use SQLite, not Postgres. Why: one user, no server to run.

## Don't repeat these
- The export button sent an empty file when nothing was logged. Do not reintroduce this. Why: users ended up pasting a blank file.
```
Rules: an intro that tells the agent how to treat the file; Decisions first, then Don't repeat these; newest first within each group; each item one line, the learner's sentence, then "Why: " plus the reason; fixed bugs also get "Do not reintroduce this."; a trailing period added if missing (a trailing comma, semicolon, or colon becomes a period); an empty group is left out.
PRD ref: `prd.md > Exporting CONTEXT.md`, `scope.md > The Unique Kernel`.

### Page template (`templates/index.html`)
One page: header (name and tagline), add form (type, sentence, reason, Save), two grouped lists with counts and an empty prompt, each row with Edit and Delete (inline edit form when `?edit=<id>`), and the export area (Export button, preview in a read-only `<pre>`, Copy, Download, or the empty message). Error messages show next to the form.
PRD ref: `prd.md > Screens and Layout`, `prd.md > Viewing the running list`.

### Styles and script (`static/style.css`, `static/app.js`)
`style.css` implements `Look and Feel`. `app.js` wires the Copy button (`navigator.clipboard.writeText`, label switches to "Copied" for ~2 seconds; falls back to selecting the text if the clipboard is blocked), the delete confirmation, and puts the cursor in the inline edit form (on the field with an error, if any).

## Data Model
One SQLite table, `entries`:

| column | type | notes |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | auto |
| `owner` | TEXT NOT NULL | the visitor's anonymous cookie id (indexed) |
| `kind` | TEXT NOT NULL | `decision` or `bug` (CHECK constraint) |
| `text` | TEXT NOT NULL | the sentence |
| `reason` | TEXT NOT NULL | the why |
| `created_at` | TEXT NOT NULL | ISO timestamp, used for newest-first |
| `updated_at` | TEXT NOT NULL | ISO timestamp |

- **Where it lives:** the SQLite file on disk.
- **How it's updated:** each add, edit, or delete is one SQL statement, committed straight away.
- **Leaving and coming back:** locally, everything is still there. On the free public host, the file resets when the service restarts. A visitor who clears cookies or switches browsers starts a new, empty list.
- The page itself keeps no state: what's in edit mode or whether the export is open is only in the URL.

## File Structure
```
ten-prompts-ago/
├── app.py                 # Flask app and routes
├── db.py                  # SQLite helpers (create table, add/list/edit/delete)
├── context_export.py      # builds CONTEXT.md text from entries (the kernel)
├── templates/
│   └── index.html         # the one page
├── static/
│   ├── style.css          # Apple-style look
│   └── app.js             # Copy button + delete confirmation
├── tests/
│   ├── test_export.py     # CONTEXT.md format rules
│   └── test_app.py        # add/edit/delete/export routes via Flask test client
├── instance/              # local SQLite file lives here (git-ignored)
├── requirements.txt       # flask, gunicorn, pytest
├── README.md              # what it is, how to run it
├── devpost/               # Devpost learning workspace (scope, prd, spec, checklist)
└── .gitignore
```
Host config (e.g. `render.yaml`) is added in `6-ship` if Render is used.

## External Services and Dependencies
- **None at runtime.** No APIs, no keys, no accounts.
- **Public host (optional, `6-ship`):** Render free web service. Build command `pip install -r requirements.txt`, start command `gunicorn app:app`. Free instances sleep when idle (first visit after a while takes a few seconds) and have no persistent disk. Free-tier terms change; recheck https://render.com/docs/free when deploying.

## Important Failure Modes
- **Export with nothing logged** → "Nothing to export yet. Log a decision or a fixed bug first." No empty file is downloaded.
- **Empty sentence or reason** → nothing saved; inline message names the missing field; typed text kept.
- **Clipboard blocked** (non-HTTPS page or browser permission) → the preview text is selected and the button says "Press Ctrl/Cmd+C to copy".
- **Public host restarted** → entries reset to empty; footer note on the public site says it's a demo that resets.

## What Was Simplified and Why
- **Full-page form submits** instead of a JavaScript front end. Every action reloads the page, which keeps the code small and the behavior easy to follow. A fuller version would update the list without reloading.
- **Edit mode in the URL** (`?edit=<id>`) instead of client-side inline editing. Same experience for the user, no front-end state.
- **Export built on request** instead of stored export files. Always reflects the current list; versioning is a scope "Later" item.
- **SQLite on the host's temporary disk** instead of a hosted database. The public link is a demo; a persistent version would need a paid disk or a hosted database.

## Decisions and Open Issues
- **Flask + SQLite + plain HTML/CSS + a little JS** (learner, on agent recommendation): full control of the Apple-style look and in-place editing; accepted more code than Streamlit.
- **Runs locally for the video, plus a public link** (learner): the link is for their resume.
- **Render as the host** (agent recommendation, to confirm in `6-ship`): free, deploys from GitHub; tradeoff is sleep on idle and no persistent disk.
- **Useful unknown (from the learner's story):** what makes a `CONTEXT.md` that an agent actually follows, given "my first `CONTEXT.md` was just a dump of entries, and the agent mostly ignored it." Approach chosen: grouped sections, an instruction line up top, short imperative items with the reason. **Checked during slice 2** (`devpost/context-experiment.md`): six fresh agents got either no context, a plain notes dump, or the grouped export, plus a request that tempts a login. With no context, both added logins. With either the dump or the export, all four named the no-login decision and checked first. Writing decisions down made the difference; in this small test the grouped format did not beat a careful dump. Still open: whether the format matters with weaker agents or longer logs.
- **Each visitor gets their own list** (learner, on agent recommendation): an anonymous cookie id scopes every entry, so strangers on the public link can't see or edit each other's entries. Tradeoff: an `owner` column and a cookie; clearing cookies means a fresh list.
