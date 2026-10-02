---
doc: prd
status: approved
---

# Ten Prompts Ago — Product Requirements

A single-page web app where someone building with an AI coding agent logs the decisions they've made and the bugs they've already fixed, then exports a `CONTEXT.md` the agent can read at the start of a session.
Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`.

## The Core Journey
Develops `scope.md > The Core Loop` and `scope.md > What "Working" Looks Like`.

1. The user opens the app. They see one familiar-looking page: the app name, an "add an entry" form, the running list of entries, and an export area.
2. They add an entry: pick whether it's a **Decision** or a **Fixed bug**, write one sentence ("Use SQLite, not Postgres"), write the reason ("one user, no server to run"), and save.
3. The entry appears in the running list straight away, under its group.
4. Later they change their mind or spot a typo: they edit the entry in place, or delete it.
5. At the start of an agent session, they click **Export**. They see the generated `CONTEXT.md` with a **Copy** button and a **Download** button.
6. They paste or drop the file into Claude Code, Cursor, or another agent. Success: the agent treats the logged decisions as settled and avoids the logged bugs.
7. They close the app. Next time they open it, every entry is still there.

## Screens and Layout
One page, top to bottom (learner: "should look like most other apps when I open the app"):
- **Header:** the name "Ten Prompts Ago" and a one-line tagline.
- **Add entry form:** type (Decision / Fixed bug), the sentence, the reason, and a save button.
- **Entry list:** entries shown in two groups, Decisions and Fixed bugs, each row showing the sentence and its reason with edit and delete actions.
- **Export area:** the Export action, the `CONTEXT.md` preview, Copy and Download.

_Assumption (agent): the add form sits above the list and export comes last, so the page reads in the order of the core journey._

## Look and Feel
Learner direction: "similar to the design of Apple's website."
- Clean and spacious: lots of white space, generous padding, content centered in a narrow column.
- Typography: Apple's system font feel (clean sans-serif), large bold headline, quiet gray secondary text.
- Color: mostly white and light gray surfaces, near-black text, one blue accent for primary actions.
- Soft rounded corners and pill-shaped buttons; minimal borders and shadows.
- Avoid: dashboards, busy sidebars, heavy color, the generic "AI app" gradient look.

## Features and Behavior

### Adding an entry
Implements `scope.md > The POC Boundary` (add an entry).
- As someone building with an agent, I want to log a decision or fixed bug with its reason so the agent later knows both what was settled and why.
  - [ ] The form has a type choice (Decision / Fixed bug), a sentence field, and a reason field.
  - [ ] Saving adds the entry to the list immediately, in the right group.
  - [ ] Saving with an empty sentence or empty reason doesn't save; the user sees a short message saying what's missing.
  - [ ] After a save, the form clears so the next entry can be typed.

### Viewing the running list
- [ ] All entries show in two groups, Decisions and Fixed bugs, each with its sentence and reason.
- [ ] Within each group, the newest entry appears first.
- [ ] Each group shows its count (e.g. "Decisions · 3").

### Editing and deleting an entry
- [ ] Each entry has an edit action that lets the user change its type, sentence, and reason, then save or cancel.
- [ ] Saved edits show in the list and in the next export.
- [ ] Each entry has a delete action; the entry disappears from the list and from the next export.
- _Assumption (agent): delete asks for a quick confirmation so a stray click doesn't lose an entry._

### Exporting CONTEXT.md
The kernel. Implements `scope.md > The Unique Kernel`.
- As someone starting a new agent session, I want one click to give me a context file written for the agent so I don't re-explain settled things.
  - [ ] Clicking Export shows the generated `CONTEXT.md` on the page.
  - [ ] **Copy** puts the full text on the clipboard and confirms ("Copied").
  - [ ] **Download** saves a file named `CONTEXT.md`.
  - [ ] The file has a short intro telling the agent how to use it, then a **Decisions** section and a **Don't repeat these** section (fixed bugs).
  - [ ] Each item is one short, imperative line followed by its reason (e.g. "Use SQLite, not Postgres. Why: one user, no server to run.").
  - [ ] A section with no entries is left out of the file.
  - [ ] Edits and deletions are reflected the next time the user exports.
  - [ ] With nothing logged, Export shows "Nothing to export yet. Log a decision or a fixed bug first." and no file is produced.

## States and Boundaries
- **First use / nothing logged:** the list shows a friendly prompt to add a first decision or fixed bug. Export runs a quick check that there's something to export; with nothing logged it falls back to a short message ("Nothing to export yet. Log a decision or a fixed bug first.") instead of producing an empty file.
- **Normal use:** list grouped, export available.
- **Missing input:** a short inline message names the empty field; nothing is saved.
- **Persistence:** entries are kept on this computer and are still there after closing and reopening the app.
- **Who can see what:** one person on their own machine; no accounts or sharing.

## Product Decisions
- Each entry holds a sentence and a reason — the reason helps the agent understand *why* something is settled.
- Entries can be edited and deleted — decisions change, and the export must stay accurate.
- Export offers both Copy and Download — copy for pasting into a chat, download for dropping the file into a repo.
- Apple-website look — clean, spacious, familiar.
- Two fixed groups, no tags or search (from `scope.md > Explicitly Cut`).
- Empty export: of the learner's list (initialize, verify, authenticate, health-check, fallback), the parts that apply to a local single-user app are a check that entries exist and a friendly fallback message. Authentication doesn't apply (no login), so it's left out with the learner's OK ("if not possible or invalid, then just go ahead").

## What We're Building
Add, view, edit, and delete entries (decision or fixed bug, sentence plus reason); entries persist locally; one-click export of a grouped, agent-ready `CONTEXT.md` with Copy and Download; Apple-style single page.

## Deferred From the POC
- **Multiple projects:** one log per app is enough to prove the export.
- **Export history / versioning:** each export is generated fresh from the current list; versioned files are a scope "Later" item.

## Possible Later Enhancements
- Versioned context files.
- Import decisions from a chat history.
- A small CLI to log a decision from the terminal.

## Non-Goals
- **Accounts, login, authentication:** single local user ("no login for v1").
- **Tags and search:** two groups keep the list scannable.
- **Syncing or sharing between people:** not needed to prove the kernel.
- **Sending the file to an agent automatically:** the user pastes or drops it in themselves.

## Open Questions
None blocking `4-spec`.
