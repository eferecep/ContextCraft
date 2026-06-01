"""Pytest fixture'ları — in-memory SQLite test ortamı."""

import pytest

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app(tmp_path):
    """Test uygulaması; geçici upload/storage klasörleri kullanır."""
    upload_dir = tmp_path / "uploads"
    storage_dir = tmp_path / "storage"
    upload_dir.mkdir()
    storage_dir.mkdir()

    application = create_app("testing")
    application.config.update(
        {
            "UPLOAD_FOLDER": str(upload_dir),
            "AVATAR_FOLDER": str(upload_dir / "avatars"),
            "STORAGE_FOLDER": str(storage_dir),
            "OPENROUTER_API_KEY": "test-openrouter-key",
            "LLAMAINDEX_API_KEY": "test-llama-key",
        }
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test istemcisi."""
    return app.test_client()


@pytest.fixture
def user(app):
    """Kayıtlı test kullanıcısı oluşturur."""
    with app.app_context():
        test_user = User(username="testuser", email="test@example.com")
        test_user.set_password("password123")
        db.session.add(test_user)
        db.session.commit()
        user_id = test_user.id
    return user_id


@pytest.fixture
def auth_client(client, app, user):
    """Giriş yapmış test istemcisi."""
    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "password123",
            "remember_me": False,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    return client


def create_user(app, username, email, password="password123"):
    """İkinci kullanıcı gibi ek test kullanıcıları için yardımcı."""
    with app.app_context():
        test_user = User(username=username, email=email)
        test_user.set_password(password)
        db.session.add(test_user)
        db.session.commit()
        return test_user.id
