# Ten Prompts Ago

Ever told your AI "no login for v1" and watched it build a login page anyway?

Ten Prompts Ago is a small web app where you log the decisions you make while building with an AI coding agent (for example, "use SQLite, not Postgres") and the bugs you've already fixed. It keeps them in one place so you can hand your agent the context it keeps forgetting.

Built for the Devpost **Build With AI: Basics** hackathon, planned first with the [Devpost Learn Skill Pack](https://github.com/challengepost/learn-ai-basics). The plan lives in [`devpost/`](devpost/): [scope](devpost/scope.md), [PRD](devpost/prd.md), [spec](devpost/spec.md), and the [build checklist](devpost/checklist.md).

## Run it locally

You need Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --debug
```

Open http://127.0.0.1:5000. Entries are saved in `instance/ten_prompts_ago.db`, created on first run.

## Run the tests

```bash
python -m pytest
```

## How it's built

- **Flask** serves one page and handles the form posts (`app.py`).
- **SQLite** stores entries in a single file (`db.py`).
- **Plain HTML and CSS** in `templates/index.html` and `static/style.css`, styled after apple.com.
