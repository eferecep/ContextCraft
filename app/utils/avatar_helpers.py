import shutil
from pathlib import Path
from typing import Optional, Set

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.utils.file_helpers import ensure_upload_dir


def _get_avatar_extensions() -> Set[str]:
    return set(current_app.config.get("AVATAR_EXTENSIONS", set()))


def get_avatar_dir(user_id: int) -> Path:
    """Kullanıcı avatar klasörünün mutlak yolunu döndürür."""
    avatar_root = Path(current_app.config["AVATAR_FOLDER"])
    return avatar_root / str(user_id)


def allowed_avatar(filename: str) -> bool:
    """Avatar dosyası uzantısının izinli olup olmadığını kontrol eder."""
    if not filename or "." not in filename:
        return False

    safe_name = secure_filename(filename)
    if not safe_name or "." not in safe_name:
        return False

    extension = safe_name.rsplit(".", 1)[1].lower()
    return extension in _get_avatar_extensions()


def _avatar_extension(filename: str) -> str:
    """Güvenli avatar dosya uzantısını döndürür."""
    safe_name = secure_filename(filename)
    return safe_name.rsplit(".", 1)[1].lower()


def delete_avatar_files(user_id: int) -> None:
    """Kullanıcının avatar klasörünü ve içeriğini siler."""
    avatar_dir = get_avatar_dir(user_id)
    if avatar_dir.exists() and avatar_dir.is_dir():
        shutil.rmtree(avatar_dir)


def save_avatar(file_storage: FileStorage, user_id: int) -> str:
    """
    Avatar dosyasını kaydeder.
    Dönen değer: UPLOAD_FOLDER'a göre göreli yol (ör. avatars/1/avatar.png).
    """
    original_name = file_storage.filename or ""
    if not allowed_avatar(original_name):
        raise ValueError(
            "Geçersiz avatar formatı. İzin verilen: png, jpg, jpeg, gif, webp."
        )

    max_bytes = current_app.config.get("AVATAR_MAX_BYTES", 2 * 1024 * 1024)
    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > max_bytes:
        raise ValueError("Avatar dosyası en fazla 2 MB olabilir.")

    extension = _avatar_extension(original_name)
    delete_avatar_files(user_id)

    avatar_dir = ensure_upload_dir(get_avatar_dir(user_id))
    target = avatar_dir / f"avatar.{extension}"
    file_storage.save(str(target))

    upload_root = Path(current_app.config["UPLOAD_FOLDER"])
    return str(target.relative_to(upload_root))


def get_avatar_absolute_path(avatar_path: Optional[str]) -> Optional[Path]:
    """DB'deki avatar_path için güvenli mutlak dosya yolunu döndürür."""
    if not avatar_path:
        return None

    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    absolute_path = (upload_root / avatar_path).resolve()

    try:
        absolute_path.relative_to(upload_root)
    except ValueError:
        return None

    if absolute_path.is_file():
        return absolute_path
    return None
