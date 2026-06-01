"""Profil ve avatar testleri."""

from io import BytesIO

from app.extensions import db
from app.models import User
from app.utils.avatar_helpers import get_avatar_absolute_path


def test_profile_requires_login(client):
    """Profil sayfası giriş gerektirmeli."""
    response = client.get("/auth/profile", follow_redirects=True)
    assert response.status_code == 200
    assert b"Giri" in response.data or b"login" in response.data.lower()


def test_profile_page_loads(auth_client):
    """Giriş yapmış kullanıcı profil sayfasını görebilmeli."""
    response = auth_client.get("/auth/profile")
    assert response.status_code == 200
    assert b"Profilim" in response.data
    assert b"Hakk" in response.data


def test_update_bio(auth_client, app, user):
    """Bio güncelleme veritabanına yansımalı."""
    response = auth_client.post(
        "/auth/profile",
        data={
            "bio": "Token optimizasyonu meraklısı",
            "submit": "Profili Kaydet",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"ncellendi" in response.data.lower()

    with app.app_context():
        test_user = db.session.get(User, user)
        assert test_user.bio == "Token optimizasyonu meraklısı"


def test_upload_avatar(auth_client, app, user):
    """Geçerli avatar yüklemesi avatar_path alanını set etmeli."""
    response = auth_client.post(
        "/auth/profile/avatar",
        data={
            "avatar": (BytesIO(b"fake-png-content"), "avatar.png"),
            "submit": "Avatar Yükle",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"y" in response.data.lower()

    with app.app_context():
        test_user = db.session.get(User, user)
        assert test_user.avatar_path is not None
        assert test_user.has_avatar
        assert get_avatar_absolute_path(test_user.avatar_path) is not None

    avatar_response = auth_client.get(f"/auth/avatars/{user}")
    assert avatar_response.status_code == 200


def test_reject_invalid_avatar(auth_client, app, user):
    """Geçersiz dosya türü reddedilmeli."""
    response = auth_client.post(
        "/auth/profile/avatar",
        data={
            "avatar": (BytesIO(b"print('hi')"), "script.py"),
            "submit": "Avatar Yükle",
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        test_user = db.session.get(User, user)
        assert test_user.avatar_path is None


def test_delete_avatar(auth_client, app, user):
    """Avatar kaldırılınca avatar_path null olmalı."""
    auth_client.post(
        "/auth/profile/avatar",
        data={
            "avatar": (BytesIO(b"fake-png"), "me.png"),
            "submit": "Avatar Yükle",
        },
        content_type="multipart/form-data",
    )

    with app.app_context():
        test_user = db.session.get(User, user)
        assert test_user.avatar_path is not None

    response = auth_client.post(
        "/auth/profile/avatar/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        test_user = db.session.get(User, user)
        assert test_user.avatar_path is None
        assert not test_user.has_avatar
