"""Turn logged entries into a CONTEXT.md written for an AI coding agent.

This is the heart of Ten Prompts Ago: not a dump of notes, but a short file
that tells the agent what is settled and which mistakes not to repeat.
"""

INTRO = (
    "Read this before writing any code. These are settled. "
    "Follow them unless I explicitly change one."
)

# (entry kind, section heading, extra instruction added to each item)
SECTIONS = (
    ("decision", "Decisions", ""),
    ("bug", "Don't repeat these", " Do not reintroduce this."),
)


def build_context(entries):
    """Return the CONTEXT.md text for these entries, or None if there are none.

    Entries keep the order they are given in (newest first from the database).
    """
    if not entries:
        return None

    lines = ["# Project context", "", INTRO]
    for kind, heading, instruction in SECTIONS:
        items = [entry for entry in entries if entry["kind"] == kind]
        if not items:
            continue
        lines += ["", f"## {heading}"]
        for entry in items:
            lines.append(
                f"- {as_sentence(entry['text'])}{instruction} Why: {as_sentence(entry['reason'])}"
            )
    return "\n".join(lines) + "\n"


def as_sentence(text):
    """Trim the text and make sure it ends like a sentence."""
    text = text.strip()
    if text.rstrip(",;:").strip():
        text = text.rstrip(",;:").rstrip()
    else:
        return text
    last = text[-1]
    if last in "\"')]" and len(text) > 1 and text[-2] in ".!?":
        return text
    if last not in ".!?":
        text += "."
    return text
