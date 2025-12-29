"""
Pydantic 模型定义
定义所有 API 请求和响应的数据结构，提供类型安全和自动验证
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ==================== Note Schemas ====================

class NoteCreate(BaseModel):
    """创建笔记的请求模型"""
    content: str = Field(..., min_length=1, description="笔记内容，不能为空")


class NoteResponse(BaseModel):
    """笔记响应模型"""
    id: int = Field(..., description="笔记 ID")
    content: str = Field(..., description="笔记内容")
    created_at: str = Field(..., description="创建时间")

    class Config:
        from_attributes = True  # 支持从 ORM 对象转换


class NoteListResponse(BaseModel):
    """笔记列表响应模型"""
    notes: list[NoteResponse] = Field(default_factory=list, description="笔记列表")


# ==================== Action Item Schemas ====================

class ActionItemCreate(BaseModel):
    """创建行动项的请求模型"""
    text: str = Field(..., min_length=1, description="行动项文本，不能为空")
    note_id: Optional[int] = Field(None, description="关联的笔记 ID")


class ActionItemResponse(BaseModel):
    """行动项响应模型"""
    id: int = Field(..., description="行动项 ID")
    note_id: Optional[int] = Field(None, description="关联的笔记 ID")
    text: str = Field(..., description="行动项文本")
    done: bool = Field(False, description="是否完成")
    created_at: str = Field(..., description="创建时间")

    class Config:
        from_attributes = True


class ActionItemUpdate(BaseModel):
    """更新行动项的请求模型"""
    text: Optional[str] = Field(None, min_length=1, description="行动项文本")
    done: Optional[bool] = Field(None, description="是否完成")


class MarkDoneRequest(BaseModel):
    """标记行动项完成状态的请求模型"""
    done: bool = Field(True, description="是否完成")


# ==================== Extract Schemas ====================

class ExtractRequest(BaseModel):
    """提取行动项的请求模型"""
    text: str = Field(..., min_length=1, description="要提取行动项的文本")
    save_note: bool = Field(False, description="是否保存为笔记")


class ExtractedItem(BaseModel):
    """提取出的单个行动项"""
    id: int = Field(..., description="行动项 ID")
    text: str = Field(..., description="行动项文本")


class ExtractResponse(BaseModel):
    """提取行动项的响应模型"""
    note_id: Optional[int] = Field(None, description="如果保存了笔记，返回笔记 ID")
    items: list[ExtractedItem] = Field(default_factory=list, description="提取出的行动项列表")


