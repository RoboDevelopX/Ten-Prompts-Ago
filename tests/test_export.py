from context_export import INTRO, build_context


def entry(kind, text, reason):
    return {"kind": kind, "text": text, "reason": reason}


def test_no_entries_means_nothing_to_export():
    assert build_context([]) is None


def test_full_file_layout():
    context = build_context([
        entry("bug", "Login page crept back in", "No login for v1"),
        entry("decision", "No login for v1", "Single local user"),
        entry("decision", "Use SQLite, not Postgres", "One user, no server to run"),
    ])
    assert context == (
        "# Project context\n"
        "\n"
        f"{INTRO}\n"
        "\n"
        "## Decisions\n"
        "- No login for v1. Why: Single local user.\n"
        "- Use SQLite, not Postgres. Why: One user, no server to run.\n"
        "\n"
        "## Don't repeat these\n"
        "- Login page crept back in. Do not reintroduce this. Why: No login for v1.\n"
    )


def test_decisions_come_before_fixed_bugs_whatever_the_input_order():
    context = build_context([
        entry("bug", "B", "rb"),
        entry("decision", "D", "rd"),
    ])
    assert context.index("## Decisions") < context.index("## Don't repeat these")


def test_items_keep_the_given_newest_first_order():
    context = build_context([
        entry("decision", "Newest", "r"),
        entry("decision", "Older", "r"),
        entry("decision", "Oldest", "r"),
    ])
    assert context.index("Newest") < context.index("Older") < context.index("Oldest")


def test_existing_end_punctuation_is_kept():
    context = build_context([entry("decision", "Ship it!", "Why not?")])
    assert "- Ship it! Why: Why not?\n" in context


def test_empty_sections_are_left_out():
    only_decisions = build_context([entry("decision", "D", "r")])
    assert "## Decisions" in only_decisions
    assert "Don't repeat these" not in only_decisions

    only_bugs = build_context([entry("bug", "B", "r")])
    assert "## Don't repeat these" in only_bugs
    assert "## Decisions" not in only_bugs


def test_intro_tells_the_agent_how_to_use_the_file():
    context = build_context([entry("decision", "D", "r")])
    assert context.startswith("# Project context\n\nRead this before writing any code.")


def test_punctuation_inside_quotes_or_brackets_is_respected():
    context = build_context([entry("decision", 'Say "no login."', "(see the scope.)")])
    assert '- Say "no login." Why: (see the scope.)\n' in context


def test_trailing_colon_or_comma_becomes_a_period():
    context = build_context([entry("decision", "Stack:", "Simple,")])
    assert "- Stack. Why: Simple.\n" in context
