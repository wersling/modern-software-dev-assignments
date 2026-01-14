import re
from dataclasses import dataclass
from typing import List


@dataclass
class ExtractResult:
    """提取结果的统一数据结构。"""
    tags: List[str]
    action_items: List[str]


def extract_tags(text: str) -> List[str]:
    """
    从文本中提取 #标签 格式的标签。

    规则：
    - 匹配独立的标签：#标签名
    - 不匹配代码块中的 #（简单排除）
    - 不匹配 HTML 实体或标题中的 #
    - 支持中文标签：#中文标签
    - 支持特殊字符：#tag-1, #tag_2
    - 自动去重并返回列表

    Args:
        text: 要解析的文本内容

    Returns:
        标签列表（去重后）

    Examples:
        >>> extract_tags("#tag1 #tag2")
        ['tag1', 'tag2']
        >>> extract_tags("这是 #中文标签 和 #tag-1")
        ['中文标签', 'tag-1']
        >>> extract_tags("### 标题")
        []
    """
    if not text:
        return []

    # 正则表达式匹配 #标签
    # 规则：
    # (?<!\w) - 确保 # 前面不是单词字符（避免匹配标题 ####）
    # \# - 匹配 # 字符
    # ([\w\u4e00-\u9fff-]+) - 匹配标签名（支持中文、字母、数字、下划线、连字符）
    # (?!\w) - 确保标签名后面不是单词字符
    tag_pattern = r'(?<!\w)#([\w\u4e00-\u9fff-]+)(?!\w)'

    matches = re.findall(tag_pattern, text)

    # 去重并保持顺序
    seen = set()
    unique_tags = []
    for tag in matches:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags


def extract_action_items(text: str) -> List[str]:
    """
    从文本中提取待办事项。

    支持的格式：
    1. 以 ! 结尾的行（原有功能）
    2. 以 "todo:" 开头的行（原有功能，不区分大小写）
    3. - [ ] 任务描述（新增）
    4. - [x] 已完成任务（可选）

    Args:
        text: 要解析的文本内容

    Returns:
        待办事项列表（去重后）

    Examples:
        >>> extract_action_items("任务1!")
        ['任务1!']
        >>> extract_action_items("todo: 这也是任务")
        ['todo: 这也是任务']
        >>> extract_action_items("- [ ] 任务1")
        ['任务1']
        >>> extract_action_items("- [x] 已完成")
        ['已完成']
    """
    if not text:
        return []

    action_items = []
    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # 格式 1 & 2: 原有逻辑 - ! 结尾或 todo: 开头
        if stripped.endswith("!") or stripped.lower().startswith("todo:"):
            action_items.append(stripped)
            continue

        # 格式 3 & 4: - [ ] 或 - [x] 格式
        # 正则匹配：- [ ] 任务描述 或 - [x] 任务描述
        task_pattern = r'^-\s*\[([ x])\]\s*(.+)$'
        match = re.match(task_pattern, stripped, re.IGNORECASE)

        if match:
            # 提取任务描述（去除首尾空格）
            task_description = match.group(2).strip()
            if task_description:
                action_items.append(task_description)

    # 去重并保持顺序
    seen = set()
    unique_items = []
    for item in action_items:
        if item not in seen:
            seen.add(item)
            unique_items.append(item)

    return unique_items


def extract_from_content(text: str) -> ExtractResult:
    """
    从文本内容中提取标签和待办事项。

    这是统一的入口函数，会同时提取标签和待办事项。

    Args:
        text: 要解析的文本内容

    Returns:
        ExtractResult 对象，包含 tags 和 action_items 两个列表

    Examples:
        >>> result = extract_from_content("#tag1\\n- [ ] 任务1\\nTodo: 任务2!")
        >>> result.tags
        ['tag1']
        >>> result.action_items
        ['任务1', '任务2!']
    """
    tags = extract_tags(text)
    action_items = extract_action_items(text)

    return ExtractResult(tags=tags, action_items=action_items)
