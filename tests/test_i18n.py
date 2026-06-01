"""Flask-Babel i18n testleri."""


def test_default_locale_is_turkish(client):
    """Varsayılan arayüz dili Türkçe olmalı."""
    response = client.get("/")
    assert response.status_code == 200
    assert b'lang="tr"' in response.data
    assert b"Giri" in response.data


def test_set_language_en(client):
    """İngilizce seçildiğinde arayüz metinleri çevrilmeli."""
    response = client.get("/set-language/en?next=/", follow_redirects=True)
    assert response.status_code == 200
    assert b'lang="en"' in response.data
    assert b"Log In" in response.data
    assert b"Sign Up" in response.data


def test_set_language_tr_from_en(client):
    """İngilizceden Türkçe'ye geri dönülebilmeli."""
    client.get("/set-language/en?next=/")
    response = client.get("/set-language/tr?next=/", follow_redirects=True)
    assert response.status_code == 200
    assert b'lang="tr"' in response.data
    assert b"Giri" in response.data


def test_invalid_language_is_ignored(client):
    """Desteklenmeyen dil kodu oturumu değiştirmemeli."""
    client.get("/set-language/en?next=/")
    client.get("/set-language/fr?next=/")
    response = client.get("/")
    assert b"Log In" in response.data


def test_language_persists_across_requests(client):
    """Seçilen dil sonraki isteklerde korunmalı."""
    client.get("/set-language/en?next=/")
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Log In" in response.data
    assert b"Email" in response.data


def test_next_param_redirect(client):
    """next parametresi ile güvenli yönlendirme yapılmalı."""
    response = client.get("/set-language/en?next=/auth/login", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/auth/login")


def test_unsafe_next_redirect_is_rejected(client):
    """Harici next URL'leri reddedilmeli."""
    response = client.get("/set-language/en?next=//evil.example/", follow_redirects=False)
    assert response.status_code == 302
    assert "evil" not in (response.location or "")


def test_navbar_language_links(client):
    """Navbar'da her iki dil linki görünmeli."""
    response = client.get("/")
    html = response.get_data(as_text=True)
    assert "/set-language/tr" in html
    assert "/set-language/en" in html
    assert "Türkçe" in html
    assert "English" in html


def test_accept_language_fallback(client):
    """Oturum yokken Accept-Language başlığı dikkate alınmalı."""
    response = client.get("/", headers={"Accept-Language": "en"})
    assert response.status_code == 200
    assert b"Log In" in response.data
