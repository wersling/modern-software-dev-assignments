"""
应用配置管理
统一管理所有配置项，支持环境变量和 .env 文件
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings:
    """应用配置类"""
    
    def __init__(self):
        # 数据库配置
        self.database_path: str = os.getenv("DATABASE_PATH", "data/app.db")
        
        # LLM 提取配置
        self.use_llm_extraction: bool = os.getenv("USE_LLM_EXTRACTION", "true").lower() == "true"
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        
        # 应用配置
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def database_full_path(self) -> Path:
        """返回数据库的完整路径"""
        base_dir = Path(__file__).resolve().parents[1]
        return base_dir / self.database_path

