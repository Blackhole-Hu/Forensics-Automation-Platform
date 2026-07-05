"""
电子取证平台 - 配置模块
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "CTF Forensic Platform"
    debug: bool = True

    # 文件存储
    upload_dir: Path = Path(__file__).parent.parent / "uploads"
    results_dir: Path = Path(__file__).parent.parent / "results"
    max_upload_size: int = 500 * 1024 * 1024  # 500MB

    # 工具路径
    tools_dir: str = r"E:\CompetitionTools\tools"

    # 数据库
    database_url: str = "sqlite+aiosqlite:///./forensic.db"

    # AI 配置
    ai_api_key: str = ""
    ai_model: str = "gpt-4o"

    class Config:
        env_prefix = "FORENSIC_"


settings = Settings()

# 确保目录存在
settings.upload_dir.mkdir(exist_ok=True)
settings.results_dir.mkdir(exist_ok=True)
