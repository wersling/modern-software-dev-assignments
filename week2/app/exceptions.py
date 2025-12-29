"""
自定义异常类
定义业务逻辑相关的异常，提供明确的错误信息和 HTTP 状态码
"""
from __future__ import annotations

from fastapi import HTTPException


class NoteNotFoundError(HTTPException):
    """笔记未找到异常"""
    def __init__(self, note_id: int):
        super().__init__(
            status_code=404,
            detail=f"Note with id {note_id} not found"
        )


class ActionItemNotFoundError(HTTPException):
    """行动项未找到异常"""
    def __init__(self, item_id: int):
        super().__init__(
            status_code=404,
            detail=f"Action item with id {item_id} not found"
        )


class ExtractionError(HTTPException):
    """提取行动项失败异常"""
    def __init__(self, reason: str):
        super().__init__(
            status_code=500,
            detail=f"Failed to extract action items: {reason}"
        )


class DatabaseError(HTTPException):
    """数据库操作失败异常"""
    def __init__(self, operation: str, reason: str):
        super().__init__(
            status_code=500,
            detail=f"Database operation '{operation}' failed: {reason}"
        )


