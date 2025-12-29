"""
FastAPI 依赖注入
提供可复用的依赖项，用于配置、数据库和服务的注入
"""
from __future__ import annotations

from functools import lru_cache
from typing import Callable

from .config import Settings
from .database import Database


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用配置单例
    使用 lru_cache 确保配置只加载一次
    
    Returns:
        Settings: 应用配置对象
    """
    return Settings()


@lru_cache()
def get_db() -> Database:
    """
    获取数据库实例单例
    使用 lru_cache 确保数据库只初始化一次
    
    Returns:
        Database: 数据库操作对象
    """
    settings = get_settings()
    return Database(settings.database_full_path)


def get_extract_function() -> Callable[[str], list[str]]:
    """
    根据配置返回对应的提取函数
    
    Returns:
        Callable: 提取函数（基于规则或 LLM）
    """
    from .services.extract import extract_action_items_llm, extract_action_items
    
    settings = get_settings()
    if settings.use_llm_extraction:
        # 返回一个闭包，包含模型配置
        def llm_extract(text: str) -> list[str]:
            return extract_action_items_llm(text, model=settings.ollama_model)
        return llm_extract
    return extract_action_items


