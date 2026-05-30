"""Kimlik doğrulama akışı testleri."""

from app.extensions import db
from app.models import User


def test_register_success(client, app):
    """Geçerli bilgilerle kayıt başarılı olmalı."""
    response = client.post(
        "/auth/register",
        data={
            "username": "yeniuser",
            "email": "yeni@example.com",
            "password": "secret12",
            "password2": "secret12",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Giri" in response.data

    with app.app_context():
        user = User.query.filter_by(email="yeni@example.com").first()
        assert user is not None
        assert user.check_password("secret12")


def test_register_duplicate_email(client, app, user):
    """Aynı e-posta ile ikinci kayıt reddedilmeli."""
    response = client.post(
        "/auth/register",
        data={
            "username": "baska",
            "email": "test@example.com",
            "password": "secret12",
            "password2": "secret12",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"zaten kay" in response.data.lower() or b"already" in response.data.lower()


def test_login_success(client, user):
    """Doğru bilgilerle giriş yapılabilmeli."""
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
    assert b"Ho" in response.data


def test_login_wrong_password(client, user):
    """Yanlış şifre ile giriş reddedilmeli."""
    response = client.post(
        "/auth/login",
        data={
            "email": "test@example.com",
            "password": "yanlis-sifre",
            "remember_me": False,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"hatal" in response.data.lower()


def test_logout(auth_client):
    """Çıkış yapıldıktan sonra korumalı sayfa erişilememeli."""
    response = auth_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200

    response = auth_client.get("/core/projects", follow_redirects=True)
    assert b"Giri" in response.data or b"login" in response.data.lower()


def test_user_password_hash(app):
    """Şifre hash'lenmeli; düz metin saklanmamalı."""
    with app.app_context():
        user = User(username="hashuser", email="hash@example.com")
        user.set_password("sifrem123")
        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "sifrem123"
        assert user.check_password("sifrem123")
        assert not user.check_password("yanlis")
