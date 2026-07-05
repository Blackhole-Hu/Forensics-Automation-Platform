"""
电子取证平台 - 配置模块
"""
from pydantic_settings import BaseSettings
from pathlib import Path

# 基于代码位置的绝对路径
_BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "CTF Forensic Platform"
    debug: bool = True

    # 文件存储
    upload_dir: Path = _BASE_DIR / "uploads"
    results_dir: Path = _BASE_DIR / "results"
    max_upload_size: int = 500 * 1024 * 1024  # 500MB

    # 工具路径
    tools_dir: str = r"E:\CompetitionTools\tools"

    # 数据库（绝对路径，避免工作目录变化导致找不到）
    database_url: str = f"sqlite+aiosqlite:///{_BASE_DIR / 'forensic.db'}"

    # AI 配置
    ai_api_key: str = ""
    ai_model: str = "gpt-4o"

    class Config:
        env_prefix = "FORENSIC_"


settings = Settings()

# 确保目录存在
settings.upload_dir.mkdir(exist_ok=True)
settings.results_dir.mkdir(exist_ok=True)
