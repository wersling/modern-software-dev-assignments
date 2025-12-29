from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..schemas import (
    ExtractRequest, 
    ExtractResponse, 
    ExtractedItem,
    ActionItemResponse,
    MarkDoneRequest
)
from ..database import Database
from ..dependencies import get_db, get_extract_function
from ..exceptions import ActionItemNotFoundError, ExtractionError
from loguru import logger


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(
    request: ExtractRequest,
    db: Database = Depends(get_db),
    extract_func = Depends(get_extract_function)
) -> ExtractResponse:
    """
    从文本中提取行动项
    
    Args:
        request: 提取请求（包含文本和是否保存为笔记）
        db: 数据库实例（依赖注入）
        extract_func: 提取函数（依赖注入）
        
    Returns:
        ExtractResponse: 提取结果
        
    Raises:
        ExtractionError: 提取失败时抛出
    """
    note_id: Optional[int] = None
    
    # 如果需要保存笔记
    if request.save_note:
        note_id = db.insert_note(request.text)
        logger.info(f"Saved note with id {note_id}")
    
    # 提取行动项
    try:
        items = extract_func(request.text)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise ExtractionError(str(e))
    
    # 保存行动项到数据库
    if items:
        ids = db.insert_action_items(items, note_id=note_id)
        extracted_items = [
            ExtractedItem(id=item_id, text=text) 
            for item_id, text in zip(ids, items)
        ]
    else:
        extracted_items = []
    
    logger.info(f"Extracted {len(extracted_items)} action items")
    return ExtractResponse(note_id=note_id, items=extracted_items)


@router.get("", response_model=list[ActionItemResponse])
def list_all(
    note_id: Optional[int] = Query(None, description="筛选特定笔记的行动项"),
    db: Database = Depends(get_db)
) -> list[ActionItemResponse]:
    """
    获取行动项列表
    
    Args:
        note_id: 可选，只返回指定笔记的行动项
        db: 数据库实例（依赖注入）
        
    Returns:
        list[ActionItemResponse]: 行动项列表
    """
    results = db.list_action_items(note_id=note_id)
    return [ActionItemResponse(**item) for item in results]


@router.post("/{action_item_id}/done", response_model=ActionItemResponse)
def mark_done(
    action_item_id: int,
    request: MarkDoneRequest,
    db: Database = Depends(get_db)
) -> ActionItemResponse:
    """
    标记行动项的完成状态
    
    Args:
        action_item_id: 行动项 ID
        request: 标记请求（包含完成状态）
        db: 数据库实例（依赖注入）
        
    Returns:
        ActionItemResponse: 更新后的行动项信息
        
    Raises:
        ActionItemNotFoundError: 行动项不存在时抛出
    """
    success = db.update_action_item_status(action_item_id, request.done)
    if not success:
        raise ActionItemNotFoundError(action_item_id)
    
    # 获取更新后的行动项
    result = db.get_action_item(action_item_id)
    if not result:
        raise ActionItemNotFoundError(action_item_id)
    
    return ActionItemResponse(**result)


