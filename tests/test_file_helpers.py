"""Dosya yardımcı fonksiyon testleri."""

from app.utils.file_helpers import allowed_file, safe_relative_path


def test_allowed_file_accepts_python(app):
    """İzin verilen uzantılar kabul edilmeli."""
    with app.app_context():
        assert allowed_file("main.py") is True
        assert allowed_file("index.html") is True


def test_allowed_file_rejects_unknown(app):
    """İzin verilmeyen uzantılar reddedilmeli."""
    with app.app_context():
        assert allowed_file("virus.exe") is False
        assert allowed_file("") is False


def test_safe_relative_path_valid(app):
    """Geçerli göreli yol kabul edilmeli."""
    with app.app_context():
        result = safe_relative_path("app/routes.py")
        assert result is not None
        assert str(result).replace("\\", "/") == "app/routes.py"


def test_safe_relative_path_rejects_traversal(app):
    """Path traversal denemeleri reddedilmeli."""
    with app.app_context():
        assert safe_relative_path("../../etc/passwd") is None
        assert safe_relative_path("app/../../secret") is None
