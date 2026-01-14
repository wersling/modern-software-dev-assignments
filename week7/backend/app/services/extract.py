import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExtractedActionItem:
    description: str
    priority: Optional[Priority] = None
    tags: list[str] = None
    due_date: Optional[str] = None
    assignee: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


def extract_action_items(text: str) -> list[str]:
    """Legacy function for backward compatibility."""
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[str] = []
    for line in lines:
        normalized = line.lower()
        if normalized.startswith("todo:") or normalized.startswith("action:"):
            results.append(line)
        elif line.endswith("!"):
            results.append(line)
    return results


def extract_priority(text: str) -> Optional[Priority]:
    """Extract priority from text."""
    patterns = {
        Priority.HIGH: [r"\[high\]", r"\[urgent\]", r"\[important\]", r"\[!\]"],
        Priority.MEDIUM: [r"\[medium\]", r"\[normal\]"],
        Priority.LOW: [r"\[low\]", r"\[later\]", r"\[someday\]"],
    }

    text_lower = text.lower()
    for priority, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, text_lower):
                return priority
    return None


def extract_tags(text: str) -> list[str]:
    """Extract hashtags from text."""
    pattern = r"#(\w+)"
    matches = re.findall(pattern, text)
    return list(set(matches))  # Remove duplicates
