import shutil
import zipfile
from pathlib import Path
from typing import List, Set

from flask import current_app

SKIP_DIRS: Set[str] = {
    "venv",
    ".venv",
    "__pycache__",
    "node_modules",
    ".git",
    ".idea",
    ".vscode",
    "dist",
    "build",
    ".pytest_cache",
    "htmlcov",
    ".mypy_cache",
    "_extracted",
}

SKIP_EXTENSIONS: Set[str] = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".svg",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".pdf",
    ".sqlite",
    ".db",
    ".lock",
}


def get_storage_dir(user_id: int, project_id: int) -> Path:
    """LlamaIndex persist klasörü: storage/{user_id}/{project_id}/"""
    storage_root = Path(current_app.config["STORAGE_FOLDER"])
    return storage_root / str(user_id) / str(project_id)


def delete_storage_dir(user_id: int, project_id: int) -> None:
    """Proje indeks dosyalarını siler."""
    path = get_storage_dir(user_id, project_id)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def _should_skip_dir(name: str) -> bool:
    return name.lower() in SKIP_DIRS or name.startswith(".")


def _should_skip_file(path: Path) -> bool:
    if path.suffix.lower() in SKIP_EXTENSIONS:
        return True
    if path.name.startswith("."):
        return True
    return False


def _get_text_extensions() -> Set[str]:
    allowed = set(current_app.config.get("ALLOWED_EXTENSIONS", set()))
    return {f".{ext.lower()}" for ext in allowed if ext.lower() != "zip"}


def extract_zip_archives(source_root: Path) -> None:
    """
    Proje klasöründeki .zip dosyalarını _extracted/{zip_adı}/ altına açar.
    Orijinal zip dosyaları yerinde kalır.
    """
    extracted_root = source_root / "_extracted"
    if extracted_root.exists():
        shutil.rmtree(extracted_root)
    extracted_root.mkdir(parents=True, exist_ok=True)

    for zip_path in sorted(source_root.rglob("*.zip")):
        if "_extracted" in zip_path.parts:
            continue
        if not zip_path.is_file():
            continue

        target_dir = extracted_root / zip_path.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_path, "r") as archive:
                archive.extractall(target_dir)
        except (zipfile.BadZipFile, OSError):
            shutil.rmtree(target_dir, ignore_errors=True)


def collect_indexable_files(source_path: str) -> List[Path]:
    """
    İndekslenecek dosyaların proje köküne göre göreli yollarını döndürür.
    Gürültü klasörleri ve ikili dosyalar atlanır.
    """
    root = Path(source_path)
    if not root.is_dir():
        return []

    text_extensions = _get_text_extensions()
    results: List[Path] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        rel = path.relative_to(root)
        if any(_should_skip_dir(part) for part in rel.parts[:-1]):
            continue
        if _should_skip_file(path):
            continue
        if path.suffix.lower() not in text_extensions:
            continue

        results.append(rel)

    return results


def read_project_file(source_root: Path, relative_path: Path) -> str:
    """Proje dosyasını UTF-8 ile okur; hata durumunda latin-1 dener."""
    file_path = source_root / relative_path
    for encoding in ("utf-8", "latin-1"):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(encoding="utf-8", errors="replace")


def ensure_storage_parent(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
