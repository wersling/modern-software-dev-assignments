from __future__ import annotations

from fastapi import APIRouter, Depends

from ..schemas import NoteCreate, NoteResponse, NoteListResponse
from ..database import Database
from ..dependencies import get_db
from ..exceptions import NoteNotFoundError, DatabaseError


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    db: Database = Depends(get_db)
) -> NoteResponse:
    """
    创建新笔记
    
    Args:
        note: 笔记创建请求
        db: 数据库实例（依赖注入）
        
    Returns:
        NoteResponse: 创建的笔记信息
    """
    note_id = db.insert_note(note.content)
    result = db.get_note(note_id)
    if not result:
        raise DatabaseError("create_note", "Failed to retrieve created note")
    return NoteResponse(**result)


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(
    note_id: int,
    db: Database = Depends(get_db)
) -> NoteResponse:
    """
    根据 ID 获取单个笔记
    
    Args:
        note_id: 笔记 ID
        db: 数据库实例（依赖注入）
        
    Returns:
        NoteResponse: 笔记信息
        
    Raises:
        NoteNotFoundError: 笔记不存在时抛出
    """
    result = db.get_note(note_id)
    if result is None:
        raise NoteNotFoundError(note_id)
    return NoteResponse(**result)


@router.get("", response_model=list[NoteResponse])
def list_all_notes(
    db: Database = Depends(get_db)
) -> list[NoteResponse]:
    """
    获取所有笔记列表
    
    Args:
        db: 数据库实例（依赖注入）
        
    Returns:
        list[NoteResponse]: 笔记列表
    """
    results = db.list_notes()
    return [NoteResponse(**note) for note in results]


