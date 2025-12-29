from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)

# 环境变量：控制使用哪种提取方式，默认使用规则方式
USE_LLM_EXTRACTION = True


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


# Pydantic 模型用于结构化输出
class ActionItemsResponse(BaseModel):
    """LLM 返回的行动项列表"""
    action_items: List[str]


def extract_action_items_llm(text: str, model: str = "llama3.1:8b") -> List[str]:
    """
    使用 LLM 从文本中提取行动项
    
    Args:
        text: 输入文本
        model: Ollama 模型名称，默认为 llama3.1:8b
        
    Returns:
        提取的行动项列表（去重后）
    """
    if not text.strip():
        return []
    
    # 构建 prompt
    system_prompt = """You are an AI assistant that extracts action items from text.
Your task is to identify and extract all actionable tasks, to-dos, or action items from the provided text.

An action item is typically:
- A task that needs to be done (e.g., "Set up database", "Write tests")
- Often starts with imperative verbs (e.g., Add, Create, Implement, Fix, Update, Write, Check, Verify)
- May be formatted as bullet points, numbered lists, or checkbox items
- May be prefixed with keywords like "TODO:", "Action:", "Next:"

Extract only the core action item text, removing:
- Bullet points (-, *, •)
- Numbering (1., 2., etc.)
- Checkbox markers ([ ], [x], [todo])
- Keyword prefixes (TODO:, Action:, etc.)

Return the action items as a JSON array of strings. If no action items are found, return an empty array."""

    user_prompt = f"""Extract action items from the following text:

{text}

Return the action items as a JSON array."""

    try:
        # 使用结构化输出调用 Ollama
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format=ActionItemsResponse.model_json_schema(),  # 使用 Pydantic 模型的 JSON schema
        )
        
        # 解析响应
        message_content = response.message.content
        result = json.loads(message_content)
        
        # 提取 action_items 列表
        items = result.get("action_items", [])
        
        # 去重并保持顺序
        seen: set[str] = set()
        unique: List[str] = []
        for item in items:
            if not item or not isinstance(item, str):
                continue
            item_stripped = item.strip()
            if not item_stripped:
                continue
            lowered = item_stripped.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            unique.append(item_stripped)
        
        return unique
        
    except Exception as e:
        # 如果 LLM 调用失败，记录错误并返回空列表
        print(f"LLM extraction failed: {e}")
        return []


def get_extract_function():
    """
    根据环境变量返回对应的提取函数
    
    Returns:
        extract_action_items 或 extract_action_items_llm
    """
    if USE_LLM_EXTRACTION:
        return extract_action_items_llm
    return extract_action_items
