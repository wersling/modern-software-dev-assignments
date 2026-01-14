from backend.app.services.extract import (
    Priority,
    extract_action_items,
    extract_action_items_enhanced,
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


def test_extract_action_items_enhanced_todo_marker():
    text = "- TODO: Write tests #testing"
    items = extract_action_items_enhanced(text)
    assert len(items) == 1
    assert items[0].description == "Write tests"
    assert items[0].tags == ["testing"]


def test_extract_action_items_enhanced_question():
    text = "- Should we implement this feature?"
    items = extract_action_items_enhanced(text)
    assert len(items) == 1
    assert "implement this feature" in items[0].description


def test_extract_action_items_enhanced_imperative():
    text = "- Fix the bug #urgent"
    items = extract_action_items_enhanced(text)
    assert len(items) == 1
    assert "Fix the bug" in items[0].description


def test_extract_action_items_enhanced_full_metadata():
    text = "- [HIGH] TODO: Deploy to production @john #deploy due:2025-02-01"
    items = extract_action_items_enhanced(text)
    assert len(items) == 1
    assert items[0].priority == Priority.HIGH
    assert items[0].assignee == "john"
    assert items[0].tags == ["deploy"]
    assert items[0].due_date == "2025-02-01"
    assert "Deploy to production" in items[0].description


def test_extract_action_items_enhanced_multiple():
    text = """
    - TODO: Write tests
    - Can you review the PR?
    - [urgent] Fix the bug @alice
    - Remember to update docs #documentation
    """.strip()
    items = extract_action_items_enhanced(text)
    assert len(items) == 4
    assert any("Write tests" in item.description for item in items)
    assert any("review the PR" in item.description for item in items)
    assert any("Fix the bug" in item.description for item in items)
    assert any("update docs" in item.description for item in items)
