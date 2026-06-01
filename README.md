# ContextCraft

**BLG106 İnternet Programcılığı — Dönem Projesi**  
**Geliştirici:** Efe Recep KARABUDAK  
**Repo:** https://github.com/eferecep/ContextCraft

ContextCraft, yazılımcıların kendi projelerini web arayüzüne yükleyip **LlamaIndex** ile indeksledikten sonra kısa bir isteği (ör. *"login ekranı yap"*) **detaylandırılmış prompt** ve **yalnızca gerekli dosya listesine** çeviren bir Flask web platformudur.

> Bu uygulama bir sohbet aracı değildir. Kullanıcı burada AI ile konuşmaz; sistem prompt üretir ve hangi dosyaların yeterli olduğunu söyler. Asıl kodlama Claude / ChatGPT gibi dış araçlarda yapılır.

## Özellikler

- Kullanıcı kaydı, giriş ve çıkış (Flask-Login, hash'lenmiş şifre)
- Proje oluşturma ve çoklu dosya yükleme (py, html, css, js, zip vb.)
- LlamaIndex ile hibrit indeksleme (vektör + BM25)
- OpenRouter üzerinden DeepSeek V3.1 ile prompt optimizasyonu
- Prompt geçmişi (`PromptLog` modeli)
- Bootstrap 5 responsive arayüz
- 404 / 500 özel hata sayfaları
- Proje listesinde sayfalama (sayfa başı 10 kayıt)
- Docker + PostgreSQL ile production dağıtım
- **Bonus:** Kullanıcı profili sayfası ve avatar yükleme (bio düzenleme, navbar'da avatar)

## Teknolojiler

| Katman | Araç |
|--------|------|
| Backend | Flask 3.x, SQLAlchemy 2.x, Flask-Migrate, Flask-WTF |
| Auth | Flask-Login, Werkzeug (pbkdf2:sha256) |
| İndeksleme | LlamaIndex 0.11, hibrit retrieve |
| AI | OpenRouter API (embedding + DeepSeek V3.1) |
| Arayüz | Jinja2, Bootstrap 5 |
| Test | pytest (28 test) |
| Deploy | Docker, Gunicorn, PostgreSQL 16 |

## Hızlı başlangıç (yerel)

```bash
git clone https://github.com/eferecep/ContextCraft.git
cd ContextCraft
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # API anahtarlarını doldur
export FLASK_APP=run.py           # veya: flask --app run run
flask db upgrade
python run.py
```

Tarayıcı: http://127.0.0.1:5000

### `.env` (minimum)

```env
SECRET_KEY=uzun-ve-guclu-bir-anahtar
OPENROUTER_API_KEY=sk-or-v1-...
LLAMAINDEX_API_KEY=sk-or-v1-...   # boş bırakılırsa OPENROUTER kullanılır
```

> `.env` dosyası `.gitignore` içindedir; repoya **asla** eklenmez.

## Kullanım akışı

1. Kayıt ol / giriş yap
2. *(Opsiyonel)* **Profil** sayfasından bio ve avatar yükle
3. Yeni proje oluştur, kaynak dosyalarını yükle
4. **İndeksle** butonuna bas (LlamaIndex)
5. Kısa prompt yaz → **Prompt Oluştur**
6. Detaylandırılmış metni kopyala, gerekli dosyaları Claude/ChatGPT'ye taşı

## Test

```bash
pytest -v
```

## Docker (production)

```bash
cp .env.example .env              # SECRET_KEY + OPENROUTER_API_KEY
docker compose up --build
```

Uygulama: http://localhost:5000

| Servis | Açıklama |
|--------|----------|
| `web` | Gunicorn + Flask (`DEBUG=False`) |
| `db` | PostgreSQL 16 (`postgres_data` volume) |
| `uploads` / `storage` | Kalıcı Docker volume'ları |

Durdurmak: `docker compose down`  
Veritabanını da silmek: `docker compose down -v`

## Proje yapısı

```
ContextCraft/
├── app/
│   ├── auth/          # Kayıt, giriş, çıkış, profil, avatar
│   ├── core/          # Proje CRUD, indeksleme, prompt
│   ├── main/          # Anasayfa
│   ├── models/        # User, Project, PromptLog
│   ├── services/      # LlamaIndex, OpenRouter, prompt_optimizer
│   └── templates/     # Jinja2 şablonları
├── docs/
│   ├── ai-gunlugu.md  # AI geliştirme günlüğü (7 oturum)
│   └── rapor.md       # Proje raporu
├── migrations/        # Flask-Migrate
├── tests/             # pytest birim testleri
├── Dockerfile
└── docker-compose.yml
```

## Teslim dokümanları (BLG106)

| Doküman | Konum |
|---------|--------|
| AI günlüğü | [docs/ai-gunlugu.md](docs/ai-gunlugu.md) |
| Proje raporu | [docs/rapor.md](docs/rapor.md) |
| Demo video | [Google Drive](https://drive.google.com/file/d/1gArjevcNEXC0b_p7PW-XWr4B9UseszSF/view?usp=sharing) |

### Demo video

**Demo (3–5 dk):** [Google Drive](https://drive.google.com/file/d/1gArjevcNEXC0b_p7PW-XWr4B9UseszSF/view?usp=sharing)

Önerilen akış: kayıt → profil/avatar → proje yükle → indeksle → prompt oluştur → sonuç ekranı.

## Bonus özellikler (BLG106 §2.3)

| Özellik | Durum | Puan |
|---------|--------|------|
| Kullanıcı profili + avatar yükleme | ✅ | +4 |
| E-posta ile şifre sıfırlama | — | +5 |
| REST API (`/api/v1/...`) | — | +5 |
| Tam metin arama | ✅ | +3 |
| İki dilli arayüz (Flask-Babel) | ✅ | +3 |

Profil bonusu: `/auth/profile` — bio düzenleme, png/jpg/gif/webp avatar (max 2 MB), navbar'da görüntüleme.

İki dilli arayüz: navbar'da **Türkçe | English** linkleri; `Flask-Babel` ile tr/en çeviri dosyaları. Çevirileri yenilemek için: `python scripts/build_translations.py`

Tam metin arama: `/core/projects` sayfasında proje adında `LIKE` araması (`?q=...`); pagination ve boş sonuç mesajı desteklenir.

## Akademik dürüstlük

Bu proje BLG106 dönem projesi kapsamında geliştirilmiştir. Geliştirme sürecinde **Cursor IDE** (AI ajan destekli) kullanılmıştır. Tüm kararlar, promptlar ve düzeltmeler [docs/ai-gunlugu.md](docs/ai-gunlugu.md) dosyasında belgelenmiştir.
