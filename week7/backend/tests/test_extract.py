from backend.app.services.extract import (
    Priority,
    extract_action_items,
    extract_assignee,
    extract_due_date,
    extract_priority,
    extract_tags,
)


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


def test_extract_tags_single():
    tags = extract_tags("Task #bugfix")
    assert "bugfix" in tags


def test_extract_tags_multiple():
    tags = extract_tags("#feature #bugfix #enhancement")
    assert len(tags) == 3
    assert "feature" in tags
    assert "bugfix" in tags
    assert "enhancement" in tags


def test_extract_tags_duplicates():
    tags = extract_tags("#task #task #work")
    assert len(tags) == 2
    assert "task" in tags
    assert "work" in tags


def test_extract_tags_none():
    tags = extract_tags("Just regular text")
    assert len(tags) == 0


def test_extract_due_date_due_keyword():
    assert extract_due_date("Task due:2025-01-15") == "2025-01-15"


def test_extract_due_date_by_keyword():
    assert extract_due_date("Finish by:2025-02-01") == "2025-02-01"


def test_extract_due_date_deadline_keyword():
    assert extract_due_date("Deadline:2025-03-15") == "2025-03-15"


def test_extract_due_date_none():
    assert extract_due_date("Task without date") is None


def test_extract_assignee_single():
    assert extract_assignee("Task @john") == "john"


def test_extract_assignee_multiple():
    # Returns first match
    result = extract_assignee("@john please review with @jane")
    assert result in ["john", "jane"]


def test_extract_assignee_none():
    assert extract_assignee("Task without assignee") is None
