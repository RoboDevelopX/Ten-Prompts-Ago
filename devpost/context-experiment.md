# Does an agent follow the export? A small check

Run during slice 2 to answer the open question in `spec.md > Decisions and Open Issues`: the story says a plain dump of entries got mostly ignored. This compares three ways of starting a session.

**Setup.** Six fresh Claude agents, each told it is starting a session on this Flask app and given no access to the repo. Each got one of three starts: no context, a plain notes dump, or the grouped `CONTEXT.md` this app exports. All three used the same three entries: no login for v1, SQLite not Postgres, and the login page that crept back in. Each was then given one of two tempting requests: "get it ready to share with a few teammates" and "add a profile page where each person sees only their own entries." A separate judge scored the six plans without knowing which start each came from.

**Caveat.** One run per cell, one model family. This shows a direction, not a measured effect.

| Request | Start | Proposes login/accounts | Proposes a server database | Names the earlier decision and checks first |
|---|---|---|---|---|
| profile | none | yes | no | no |
| profile | dump | no | no | yes |
| profile | grouped | no | no | yes |
| teammates | none | yes | no | no |
| teammates | dump | no | no | yes |
| teammates | grouped | no | no | yes |

**What it shows.**

- With no context, both agents planned Flask-Login, registration, and passwords, and neither knew about the no-login decision. This is the failure the app exists to prevent.
- With either the dump or the grouped `CONTEXT.md`, all four agents named the no-login decision, kept SQLite and no login, and asked before reversing anything.
- In this small test the dump did as well as the grouped file. Having the decisions written down at all made the difference. The grouped format's advantages (it's scannable, has an explicit "follow these" instruction, and gives the reason with each item) are still the design, but this run doesn't show they beat a careful dump.

## The plans, verbatim

### profile / none

I haven't opened the code yet. My first step would be reading app.py and db.py to see whether the app has any idea of a user today. This plan assumes it doesn't.

**Libraries:** Flask-Login for sessions and werkzeug.security, which comes with Flask, for password hashing. No outside auth service. SECRET_KEY would come from an environment variable.

**Changes:**
- db.py: a users table (id, username, password_hash, display_name), a user_id column on entries, and helpers create_user, get_user, set_display_name and entries_for_user.
- app.py: register, login and logout routes, plus GET/POST /profile. Entry routes would require login, and new entries would be saved with the user's id.
- templates/: new profile.html, login.html and register.html, plus nav links in index.html.
- static/style.css: styles for the profile page and forms.
- tests/test_profile.py: changing the display name, user A can't see user B's entries, and logged-out visitors get redirected.

**Questions for you first:**
1. Do you want real logins, or is a simple "pick a name" with no password enough for the proof of concept?
2. Is this in your scope doc, or is it a stretch goal?
3. Who should own the entries that already exist?
4. Should the main list and the CONTEXT.md export also show only your own entries?

### profile / dump

Before I start: this request conflicts with your notes. "Each person sees only their own entries" means multiple users, so the app would need to know who is who. That means logins, and your notes say "no login for v1, single local user." They also say a login page already crept back in once after a refactor, and I don't want to repeat that.

**What I'd build unless you tell me otherwise (single user, no login):**
- **Libraries/services:** none new. Flask and the existing SQLite database only. No Postgres, no Flask-Login, no auth service.
- **db.py:** add a one-row `settings` table holding `display_name`, plus `get_display_name()` and `set_display_name()`.
- **app.py:** add a `/profile` route that shows and saves the name.
- **templates/profile.html** (new): a name field and a list of entries. Every entry belongs to you, so no filtering is needed.
- **templates/index.html:** add a link to the profile page and greet you by name.
- **CONTEXT.md export:** include the display name.
- **tests/:** test saving and reading the name, and check that no login route exists.

**What I'd check with you first:**
1. Do you really need several people, each seeing only their own entries? That reverses the no-login decision and adds a user table, sessions and password handling. It's a v2-sized change.
2. Or is the single-user profile above what you meant?

### profile / grouped

I need to check one thing with you first. If each person sees only their own entries, the app has to know who is using it, which means a login. Your CONTEXT.md says "No login for v1" and lists the login page creeping back in as a mistake not to repeat. So I won't build per-person accounts unless you tell me the decision has changed.

My plan, keeping the no-login rule:
- Libraries and services: nothing new. I'll keep Flask and SQLite, with no Flask-Login, no auth service and no Postgres.
- db.py: add a one-row `profile` table, plus `get_display_name()` and `set_display_name()` helpers.
- app.py: add a `/profile` route that shows and saves the name. It won't redirect anywhere and nothing needs to be unlocked. The entry list stays the same, since every entry belongs to the one local user.
- templates/profile.html: a new page with the name form. index.html gets a link to it and shows the name.
- static/style.css: small styling for the form.
- tests/test_profile.py: tests that the name saves and loads, that empty or too-long names are rejected, and that no login route or redirect exists.

Questions for you:
1. Are you changing the no-login decision? If so, real per-person entries need logins, a user ID on each entry and a database change. I'd update CONTEXT.md before writing any code.
2. Should the display name appear in the exported CONTEXT.md?

### teammates / none

Plan (I haven't opened any files yet, so I'd read db.py and app.py first to see the current setup):

**Libraries**
- Storage: Python's built-in `sqlite3` in a single file. No new service. That's enough for a few teammates. I'd move to Postgres only if the host wipes local files on restart.
- Users: Flask-Login for sessions. Passwords hashed with Werkzeug, which already comes with Flask.
- `SECRET_KEY` read from an environment variable, not written in the code.

**Files**
- `db.py`: add a `users` table, add a `user_id` (or `team_id`) column to decisions and bugs, plus a small migration so existing entries stay.
- `app.py`: login, logout and register routes; `@login_required` on every route; every query and the CONTEXT.md export limited to the signed-in user or team.
- `templates/login.html` (new), plus a logout link in `index.html`.
- `requirements.txt`: add Flask-Login.
- `tests/test_auth.py` (new): check that users can't see each other's entries and that logged-out visitors are redirected.

**To check with you first**
1. Is there one shared team log, or does each person keep a private log?
2. Where will it run (your laptop, Render, something else)? That decides SQLite or Postgres.
3. Open sign-up, invite-only, or a single shared team password? The password is the simplest option.
4. Who should own the entries already in the app?
5. Is this inside your hackathon scope, or a later add-on?

### teammates / dump

Before I change anything: this request conflicts with two decisions you already made. The first is no login for v1. The second is SQLite, not Postgres. The login page has already come back once after a refactor, so I won't reverse either decision unless you say so.

**Questions for you first:**
1. Does "share" mean each teammate runs their own copy, or does everyone use one shared copy?
2. Do entries need to show who logged them?
3. Does "no login" still hold for this release?

**My plan, which keeps both decisions:**
- **Libraries:** Nothing new. I'd keep Flask and Python's built-in sqlite3. No Postgres, no Flask-Login and no outside login service.
- **db.py:** Let a setting choose where the database file lives. Turn on SQLite's WAL mode so a few people can save at the same time. If you answer yes to question 2, add an `author` column.
- **app.py and templates/index.html:** Only if you answer yes to question 2, add an optional "your name" field that the browser remembers. It shows who wrote an entry but proves nothing about who they are.
- **tests/:** Add a test that fails if a /login route or a login page shows up, so it can't slip back in unnoticed.
- **README:** Explain that a shared copy should only run on a trusted network, because it has no login.

If you want real accounts, that changes a decision. I'd record the change first and plan it separately.

### teammates / grouped

This request runs into two decisions your CONTEXT.md marks as settled: no login for v1, and SQLite instead of Postgres. "The login page crept back in" is also on your don't-repeat list. You haven't explicitly changed either decision, so I won't add a login or switch databases unless you tell me to.

My plan, keeping both decisions:
- **Storage:** stay on SQLite. In db.py, turn on WAL mode and a busy timeout so a few people saving at once don't lock the database. Read the database path from an environment variable. This needs no new libraries (Python's built-in sqlite3).
- **Users, without a login:** add an optional "logged by" name to decisions and bugs. That means a schema change and migration in db.py, updated routes in app.py and a new form field in templates/index.html. A cookie remembers the name. It records who added an entry; it doesn't check who anyone is.
- **tests/:** add tests for the new field and for saves happening at the same time.

What I need to check with you first:
1. How will teammates use it: one shared copy, or each running it on their own machine? If each runs their own, very little needs to change.
2. Are you changing "no login for v1"? If so, I'll update CONTEXT.md first and then build the login with Flask-Login.
3. Will a shared copy be reachable from outside a trusted network? Without a login, it shouldn't be.
