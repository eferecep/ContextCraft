"""Proje yönetimi ve pagination testleri."""

from io import BytesIO

from app.extensions import db
from app.models import Project

from tests.conftest import create_user


def test_project_list_requires_login(client):
    """Giriş yapmadan proje listesine erişilememeli."""
    response = client.get("/core/projects", follow_redirects=True)
    assert response.status_code == 200
    assert b"Giri" in response.data or b"login" in response.data.lower()


def test_create_project(auth_client, app):
    """Giriş yapmış kullanıcı proje oluşturabilmeli."""
    response = auth_client.post(
        "/core/projects/new",
        data={
            "name": "Test Projesi",
            "description": "Açıklama",
            "files": (BytesIO(b"print('hello')"), "main.py"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Projelerim" in response.data

    with app.app_context():
        project = Project.query.filter_by(name="Test Projesi").first()
        assert project is not None
        assert project.status == "pending"
        assert project.source_path is not None


def test_project_detail_404_for_other_user(auth_client, app):
    """Başka kullanıcının projesine erişim 404 dönmeli."""
    with app.app_context():
        other_id = create_user(app, "other", "other@example.com")
        project = Project(name="Gizli", owner_id=other_id, status="pending")
        db.session.add(project)
        db.session.commit()
        project_id = project.id

    response = auth_client.get(f"/core/projects/{project_id}")
    assert response.status_code == 404
    assert b"404" in response.data or b"bulunamad" in response.data.lower()


def test_search_projects_by_name(auth_client, app, user):
    """Proje adında LIKE araması eşleşen kayıtları döndürmeli."""
    with app.app_context():
        db.session.add_all(
            [
                Project(name="Login App", owner_id=user, status="pending"),
                Project(name="Blog Sitesi", owner_id=user, status="pending"),
            ]
        )
        db.session.commit()

    response = auth_client.get("/core/projects?q=Login")
    assert response.status_code == 200
    assert b"Login App" in response.data
    assert b"Blog Sitesi" not in response.data


def test_search_projects_no_match(auth_client, app, user):
    """Eşleşmeyen aramada boş sonuç mesajı gösterilmeli."""
    with app.app_context():
        db.session.add(Project(name="Demo", owner_id=user, status="pending"))
        db.session.commit()

    response = auth_client.get("/core/projects?q=xyz-yok")
    assert response.status_code == 200
    assert b"bulunamad" in response.data.lower() or b"not found" in response.data.lower()
    assert b"Demo" not in response.data


def test_project_pagination(auth_client, app, user):
    """Proje listesi sayfa başına 10 kayıt göstermeli."""
    with app.app_context():
        for index in range(12):
            db.session.add(
                Project(
                    name=f"Proje {index}",
                    owner_id=user,
                    status="pending",
                )
            )
        db.session.commit()

    page1 = auth_client.get("/core/projects")
    assert page1.status_code == 200
    assert b"Toplam 12 proje" in page1.data
    assert b"Sonraki" in page1.data

    page2 = auth_client.get("/core/projects?page=2")
    assert page2.status_code == 200
    assert b"Sayfa 2 / 2" in page2.data


def test_not_found_page(client):
    """Var olmayan URL özel 404 sayfası döndürmeli."""
    response = client.get("/var-olmayan-sayfa")
    assert response.status_code == 404
    assert b"404" in response.data
