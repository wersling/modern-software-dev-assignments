from backend.app.services.extract import Priority, extract_action_items, extract_priority


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


def test_extract_priority_high():
    assert extract_priority("[HIGH] Do this") == Priority.HIGH
    assert extract_priority("[urgent] Fix bug") == Priority.HIGH
    assert extract_priority("[important] Meeting") == Priority.HIGH
    assert extract_priority("[!] Critical") == Priority.HIGH


def test_extract_priority_medium():
    assert extract_priority("[MEDIUM] Normal task") == Priority.MEDIUM
    assert extract_priority("[normal] Regular work") == Priority.MEDIUM


def test_extract_priority_low():
    assert extract_priority("[LOW] Backlog item") == Priority.LOW
    assert extract_priority("[later] Future task") == Priority.LOW
    assert extract_priority("[someday] Maybe") == Priority.LOW


def test_extract_priority_none():
    assert extract_priority("Just a task") is None
    assert extract_priority("Regular text") is None
