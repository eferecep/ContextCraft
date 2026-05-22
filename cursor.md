# ContextCraft — Cursor Proje Rehberi

## Proje Özeti

**ContextCraft**, yazılımcıların projelerini yükleyip LlamaIndex ile bağlamı optimize ederek token israfını önleyen bir Flask web platformudur.

- **Ders:** İnternet Programcılığı (Meslek Yüksek Okulu)
- **Framework:** Flask 3.x
- **Python:** 3.9 (sistem Python — Mac uyumluluğu için)
- **Veritabanı:** SQLite (geliştirme)

---

## Şu An Hangi Aşamadayız?

**Aşama 4 / 8 — Auth tamamlandı, core henüz boş**

| Bölüm | Durum |
|---|---|
| Proje iskeleti (factory + blueprint) | ✅ Tamamlandı |
| User & Project modelleri | ✅ Tamamlandı |
| Veritabanı migration | ✅ Tamamlandı |
| Kayıt / Giriş / Çıkış (auth) | ✅ Tamamlandı |
| Anasayfa (main) | ✅ Minimal tamamlandı |
| Proje yükleme (core) | ⏳ Henüz başlanmadı |
| LlamaIndex entegrasyonu | ⏳ Henüz başlanmadı |
| Dashboard & proje yönetimi | ⏳ Henüz başlanmadı |

---

## İlerleme Adımları

### ✅ Tamamlanan

1. **Proje iskeleti**
   - Application Factory (`create_app`)
   - Blueprint'ler: `main`, `auth`, `core`
   - `extensions.py` (db, migrate, login_manager, csrf)
   - `.env` / `.gitignore` / `requirements.txt`

2. **Veritabanı modelleri**
   - `User` — username (32), email, password_hash, `set_password` / `check_password`
   - `Project` — name, description, source_path, status, owner ilişkisi
   - SQLAlchemy 2.x stili (`Mapped`, `mapped_column`)
   - Python 3.9 uyumu (`Optional[str]`, `str | None` kullanılmaz)

3. **Migration**
   - `flask db init` + `migrate` + `upgrade`
   - `users` ve `projects` tabloları oluşturuldu

4. **Kimlik doğrulama (auth)**
   - `RegisterForm` / `LoginForm` (Flask-WTF + CSRF)
   - `/auth/register`, `/auth/login`, `/auth/logout`
   - E-posta ile giriş (kullanıcı adıyla giriş yok)
   - "Beni hatırla" (`remember_me`)
   - Türkçe flash mesajları
   - `user_loader` yapılandırması

5. **Anasayfa**
   - `base.html` şablonu
   - `/` minimal index sayfası

### ⏳ Sıradaki Adımlar

6. **Core blueprint — Proje yükleme**
   - Proje oluşturma formu
   - Dosya/klasör yükleme (`werkzeug` secure_filename)
   - `uploads/` dizini yönetimi
   - `@login_required` korumalı rotalar

7. **LlamaIndex entegrasyonu**
   - Yüklenen projeyi indeksleme
   - `Project.status` güncelleme (`pending` → `indexed` / `failed`)
   - Token optimizasyonu / bağlam çıkarma servisi

8. **Dashboard & proje yönetimi**
   - Kullanıcının projelerini listeleme
   - Proje detay sayfası
   - Proje silme / yeniden indeksleme

9. **UI iyileştirmeleri**
   - Bootstrap veya Tailwind entegrasyonu
   - Responsive tasarım

10. **Test & deployment**
    - Birim testleri
    - Production config
    - Sunum / teslim dokümantasyonu

---

## Klasör Yapısı

```
ContextCraft/
├── app/
│   ├── __init__.py          # create_app() + user_loader
│   ├── extensions.py        # db, migrate, login_manager, csrf
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── forms.py         # RegisterForm, LoginForm
│   │   └── routes.py        # register, login, logout
│   ├── core/
│   │   └── __init__.py      # (boş — sırada)
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py        # index
│   ├── models/
│   │   ├── user.py
│   │   └── project.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   └── main/
│   └── static/
├── migrations/
├── config.py
├── run.py
├── requirements.txt
├── .env                     # gitignore'da — repoya gitmez
└── .env.example
```

---

## Kodlama Kuralları (Cursor için)

### Python sürümü
- Hedef: **Python 3.9** (Mac sistem Python)
- `str | None` **kullanma** → `Optional[str]` kullan
- `from typing import Optional, List` tercih et

### SQLAlchemy
- **2.x stili** zorunlu: `Mapped`, `mapped_column`
- Eski `db.Column` stili kullanma
- İlişkiler: `relationship(back_populates=...)`

### Flask mimarisi
- Application Factory pattern korunmalı
- Her blueprint kendi `routes.py` / `forms.py` dosyasına sahip olmalı
- Extension'lar `extensions.py` içinde tanımlanmalı
- Blueprint tanımından **sonra** routes import edilmeli

### Güvenlik
- Şifreler **asla** düz metin saklanmaz → `user.set_password()`
- CSRF koruması tüm formlarda aktif (`FlaskForm` + `hidden_tag()`)
- `.env` dosyası repoya **eklenmez**
- Dosya yüklemelerinde `secure_filename` kullan

### Kullanıcı deneyimi
- Flash mesajları **Türkçe**
- Giriş yalnızca **e-posta + şifre** ile
- Giriş yapmış kullanıcı `/login` ve `/register`'a gelirse anasayfaya yönlendirilmeli

### İş akışı
- Büyük değişikliklerde önce **plan göster**, onay al, sonra kod yaz
- Gereksiz dosya/değişiklik ekleme — minimal diff

---

## Bağımlılıklar

```
flask>=3.0,<4.0
flask-sqlalchemy>=3.1,<4.0
flask-migrate>=4.0,<5.0
flask-login>=0.6,<1.0
flask-wtf>=1.2,<2.0
email-validator>=2.0,<3.0
python-dotenv>=1.0,<2.0
llama-index>=0.10,<1.0
werkzeug>=3.0,<4.0
```

---

## Çalıştırma

```bash
cd ContextCraft
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

Tarayıcı: `http://127.0.0.1:5000`

### Migration komutları

```bash
export FLASK_APP=run.py
flask db migrate -m "açıklama"
flask db upgrade
```

---

## Mevcut Rotalar

| URL | Blueprint | Açıklama |
|---|---|---|
| `/` | main | Anasayfa |
| `/auth/register` | auth | Kayıt ol |
| `/auth/login` | auth | Giriş yap |
| `/auth/logout` | auth | Çıkış yap |

---

## Sonraki Cursor Oturumu İçin Öneri

> "Core blueprint'e proje yükleme akışını ekle. Plan modunda ilerle."
