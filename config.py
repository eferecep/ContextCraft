import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _env(key: str, default: str = "") -> str:
    """Ortam değişkenini okur; baştaki/sondaki boşluk ve tırnakları temizler."""
    value = os.environ.get(key, default)
    return value.strip().strip('"').strip("'")


def _normalize_database_url(url: str) -> str:
    """postgres:// → postgresql:// (SQLAlchemy uyumu)."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SECRET_KEY = _env("SECRET_KEY", "dev-fallback-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'contextcraft.db'}")
    )
    WTF_CSRF_ENABLED = True

    # Dosya yükleme (Faz 4)
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    ALLOWED_EXTENSIONS = {
        "py", "html", "htm", "css", "js", "json", "txt", "md",
        "yaml", "yml", "toml", "ini", "cfg", "xml", "zip",
    }
    ALLOWED_EXTENSIONLESS = {"dockerfile", "makefile", "readme", "license"}

    # LlamaIndex indeksleme (Faz 5) — OpenRouter anahtarı ile aynı olabilir
    OPENROUTER_API_KEY = _env("OPENROUTER_API_KEY")
    LLAMAINDEX_API_KEY = _env("LLAMAINDEX_API_KEY") or OPENROUTER_API_KEY
    LLAMAINDEX_API_BASE = _env(
        "LLAMAINDEX_API_BASE", "https://openrouter.ai/api/v1"
    )
    LLAMAINDEX_EMBEDDING_MODEL = _env(
        "LLAMAINDEX_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    STORAGE_FOLDER = str(BASE_DIR / "storage")

    # OpenRouter / DeepSeek AI (Faz 6 — prompt optimizasyonu)
    OPENROUTER_MODEL = _env("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3.1")
    OPENROUTER_SITE_URL = _env("OPENROUTER_SITE_URL", "http://localhost:5000")
    OPENROUTER_APP_NAME = _env("OPENROUTER_APP_NAME", "ContextCraft")

    # Faz 6 — opsiyonel reranking (varsayılan kapalı)
    RERANK_ENABLED = os.environ.get("RERANK_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )


class DevelopmentConfig(Config):
    DEBUG = True
    # Büyük projeler için varsayılan boyut limiti yok.
    # İstenirse .env ile MAX_CONTENT_LENGTH=524288000 (500 MB) gibi ayarlanabilir.
    _max_upload = os.environ.get("MAX_CONTENT_LENGTH")
    MAX_CONTENT_LENGTH = int(_max_upload) if _max_upload else None


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    _max_upload = os.environ.get("MAX_CONTENT_LENGTH")
    MAX_CONTENT_LENGTH = int(_max_upload) if _max_upload else None


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
