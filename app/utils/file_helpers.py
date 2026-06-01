import shutil
from pathlib import Path
from typing import Optional, Set

from flask import current_app
from flask_babel import lazy_gettext as _l
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


def _get_allowed_extensions() -> Set[str]:
    return set(current_app.config.get("ALLOWED_EXTENSIONS", set()))


def _get_allowed_extensionless() -> Set[str]:
    return set(current_app.config.get("ALLOWED_EXTENSIONLESS", set()))


def allowed_file(filename: str) -> bool:
    """Dosya uzantısının veya adının yükleme listesinde olup olmadığını kontrol eder."""
    if not filename:
        return False

    safe_name = secure_filename(filename)
    if not safe_name:
        return False

    lower_name = safe_name.lower()
    if lower_name in _get_allowed_extensionless():
        return True

    if "." not in safe_name:
        return False

    extension = safe_name.rsplit(".", 1)[1].lower()
    return extension in _get_allowed_extensions()


def get_project_upload_dir(user_id: int, project_id: int) -> Path:
    """Proje dosyalarının kaydedileceği klasör yolunu döndürür."""
    upload_root = Path(current_app.config["UPLOAD_FOLDER"])
    return upload_root / str(user_id) / str(project_id)


def ensure_upload_dir(path: Path) -> Path:
    """Klasör yoksa oluşturur."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_relative_path(relative_path: str) -> Optional[Path]:
    """
    Path traversal saldırılarını engelleyerek güvenli göreli yol üretir.
    Örnek: app/routes.py  →  Path('app/routes.py')
    Reddedilen: ../../etc/passwd
    """
    if not relative_path:
        return None

    relative_path = relative_path.replace("\\", "/").strip("/")
    if ".." in relative_path.split("/"):
        return None

    parts = []
    for part in relative_path.split("/"):
        safe_part = secure_filename(part)
        if not safe_part:
            return None
        parts.append(safe_part)

    if not parts:
        return None

    return Path(*parts)


def save_uploaded_file(
    file_storage: FileStorage,
    user_id: int,
    project_id: int,
    relative_path: Optional[str] = None,
) -> str:
    """
    Tek dosyayı proje klasörüne kaydeder.
    Dönen değer: proje kök dizininin mutlak yolu (source_path olarak saklanır).
    """
    original_name = file_storage.filename or ""
    if not allowed_file(original_name):
        raise ValueError(_l("İzin verilmeyen dosya türü: %(filename)s") % {"filename": original_name})

    project_dir = ensure_upload_dir(get_project_upload_dir(user_id, project_id))

    if relative_path:
        safe_path = safe_relative_path(relative_path)
        if safe_path is None:
            raise ValueError(_l("Geçersiz dosya yolu: %(path)s") % {"path": relative_path})
        target = project_dir / safe_path
        ensure_upload_dir(target.parent)
    else:
        safe_name = secure_filename(original_name)
        target = project_dir / safe_name

    file_storage.save(str(target))
    return str(project_dir)


def delete_project_files(source_path: str) -> None:
    """Proje klasörünü ve içindeki tüm dosyaları siler."""
    path = Path(source_path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


def list_project_files(source_path: str) -> list:
    """Proje klasöründeki dosyaların göreli yollarını listeler."""
    if not source_path:
        return []

    root = Path(source_path)
    if not root.is_dir():
        return []

    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append(str(path.relative_to(root)))
    return files
