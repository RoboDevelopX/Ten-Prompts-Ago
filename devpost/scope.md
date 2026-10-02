---
doc: scope
status: approved
---

# Ten Prompts Ago

A tiny web app that keeps a log of the decisions you've made and the bugs you've already fixed while building with an AI coding agent, and turns it into a `CONTEXT.md` your agent actually remembers.

## The Unique Kernel
The export is written *for the agent*, not as a dump of notes. One click turns the log into a short `CONTEXT.md` grouped into **Decisions** (what's settled) and **Don't repeat these** (bugs already fixed), so pasting it at the start of a session stops the agent from rebuilding the login page you ruled out or bringing back a bug you killed ten prompts ago.

## Who It's For
Someone building a project with Claude Code, Cursor, Codex, or a similar agent across many prompts and sessions. Today they re-explain the same decisions by hand ("we said no login for v1") and lose half an hour each time the agent forgets. The first user is the learner themself.

## The Core Loop
While building: make a decision or fix a bug → add it to Ten Prompts Ago in a few seconds. At the start of the next agent session: click export → paste `CONTEXT.md` into the agent. They come back because every new session (or every time the agent drifts) needs the same context again.

## Inspiration & Identity
A focused developer utility: quick to add an entry, nothing to configure, no accounts. Feels like a scratchpad, not a project-management tool.

## Why This Matters to the Learner
"I realized the problem wasn't that the AI was bad. It simply had no memory of what I had decided. I wanted a small tool that keeps that memory for me." They also want a working project for their resume that they can keep improving.

## What "Working" Looks Like
Open the app, add a decision ("use SQLite, not Postgres") and a fixed bug, see both in the running list, click export, and get a formatted `CONTEXT.md` with the two groups. The "oh, that's cool" beat: that file pasted into a coding agent, which then respects the decision instead of re-arguing it.

## The POC Boundary
- Add an entry: a short text, marked as either a decision or a fixed bug.
- See the running list of entries.
- One-click export of a formatted `CONTEXT.md` (download and copy), grouped into "Decisions" and "Don't repeat these."
- Entries saved locally so they survive a restart.
- Single user, single project, runs locally.

## Later
- Versioned context files.
- Importing decisions straight from a chat history.
- A small CLI to log a decision without leaving the terminal.

## Explicitly Cut
- **Accounts / login:** single local user, so there's nothing to log into (and "no login for v1" is the app's own example).
- **Tags:** two fixed groups are enough to prove the export works.
- **Search:** the list stays short enough to scan in a proof of concept.
