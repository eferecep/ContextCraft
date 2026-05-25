import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-fallback-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'contextcraft.db'}"
    )
    WTF_CSRF_ENABLED = True

    # Dosya yükleme (Faz 4)
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    ALLOWED_EXTENSIONS = {
        "py", "html", "htm", "css", "js", "json", "txt", "md",
        "yaml", "yml", "toml", "ini", "cfg", "xml", "zip",
    }
    ALLOWED_EXTENSIONLESS = {"dockerfile", "makefile", "readme", "license"}

    # OpenRouter / DeepSeek AI
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-chat")
    OPENROUTER_SITE_URL = os.environ.get("OPENROUTER_SITE_URL", "http://localhost:5000")
    OPENROUTER_APP_NAME = os.environ.get("OPENROUTER_APP_NAME", "ContextCraft")


class DevelopmentConfig(Config):
    DEBUG = True
    # Büyük projeler için varsayılan boyut limiti yok.
    # İstenirse .env ile MAX_CONTENT_LENGTH=524288000 (500 MB) gibi ayarlanabilir.
    _max_upload = os.environ.get("MAX_CONTENT_LENGTH")
    MAX_CONTENT_LENGTH = int(_max_upload) if _max_upload else None


class ProductionConfig(Config):
    DEBUG = False
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
