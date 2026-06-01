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

## Teknolojiler

| Katman | Araç |
|--------|------|
| Backend | Flask 3.x, SQLAlchemy 2.x, Flask-Migrate, Flask-WTF |
| Auth | Flask-Login, Werkzeug (pbkdf2:sha256) |
| İndeksleme | LlamaIndex 0.11, hibrit retrieve |
| AI | OpenRouter API (embedding + DeepSeek V3.1) |
| Arayüz | Jinja2, Bootstrap 5 |
| Test | pytest (22 test) |
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
2. Yeni proje oluştur, kaynak dosyalarını yükle
3. **İndeksle** butonuna bas (LlamaIndex)
4. Kısa prompt yaz → **Prompt Oluştur**
5. Detaylandırılmış metni kopyala, gerekli dosyaları Claude/ChatGPT'ye taşı

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
│   ├── auth/          # Kayıt, giriş, çıkış
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
| Demo video | *(link eklenecek)* |

### Demo video

Kayıt tamamlandığında link buraya eklenecek:

```
Demo: [YouTube veya Google Drive linki]
```

Önerilen akış (3–5 dk): kayıt → proje yükle → indeksle → prompt oluştur → sonuç ekranı.

## Akademik dürüstlük

Bu proje BLG106 dönem projesi kapsamında geliştirilmiştir. Geliştirme sürecinde **Cursor IDE** (AI ajan destekli) kullanılmıştır. Tüm kararlar, promptlar ve düzeltmeler [docs/ai-gunlugu.md](docs/ai-gunlugu.md) dosyasında belgelenmiştir.
