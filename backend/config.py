import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


_BASE_DIR = Path(__file__).parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "景区导览AI数字人"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8088

    # Database
    DATABASE_URL: str = "mysql+aiomysql://root:Hh261819.@localhost:3306/aihumanproject"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # File paths
    BASE_DIR: Path = _BASE_DIR
    DATA_DIR: Path = _BASE_DIR / "data"
    KNOWLEDGE_DIR: Path = DATA_DIR / "knowledge"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    AUDIO_DIR: Path = DATA_DIR / "audio"

    # LLM - 通义千问 Qwen (DashScope)
    LLM_API_KEY: str = os.getenv("DASHSCOPE_API_KEY")
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen3.6-plus"

    # ASR (Whisper)
    ASR_MODEL: str = "base"
    ASR_DEVICE: str = "cpu"

    # TTS
    TTS_VOICE: str = "zh-CN-XiaoxiaoNeural"

    # Amap (高德地图)
    AMAP_KEY: str = "ef1f20cf0b87fbd95fb9c4868aa3433f"

    # JWT Auth
    JWT_SECRET_KEY: str = "景区导览AI数字人-默认JWT签名密钥-2026"
    JWT_EXPIRATION: int = 1800  # 单位：秒 (30分钟)

    # Vector store
    EMBEDDING_MODEL: str = "BAAI/bge-base-zh-v1.5"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 20

    class Config:
        env_file = str(_BASE_DIR / ".env")
        env_file_encoding = "utf-8"

    def model_post_init(self, __context):
        if not self.LLM_API_KEY:
            self.LLM_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")


settings = Settings()
