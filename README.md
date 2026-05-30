# ContextCraft

Büyük yazılım projelerini Claude veya ChatGPT gibi yapay zekalara doğrudan yüklemek hem token limitlerini hızla doldurur hem de modelin kafasını karıştırır. ContextCraft, projelerinizi indeksleyip kısa isteğinizi **detaylandırılmış prompt** ve **yalnızca gerekli dosya listesine** çeviren bir Flask web platformudur.

## Teknolojiler

- Flask 3.x, SQLAlchemy, Flask-Login, Flask-WTF
- LlamaIndex 0.11 (hibrit retrieve)
- OpenRouter API (embedding + DeepSeek V3.1)
- Bootstrap 5

## Yerel geliştirme

```bash
cd ContextCraft
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # API anahtarlarını doldur
flask db upgrade
python run.py
```

Tarayıcı: http://127.0.0.1:5000

## Test

```bash
pytest -v
```

## Docker ile çalıştırma (Production)

Hoca PDF Prompt 11: `Dockerfile` + `docker-compose.yml` + PostgreSQL.

1. `.env` dosyasını oluşturun (`.env.example` şablonu):

```bash
cp .env.example .env
```

En az şunları doldurun:

```env
SECRET_KEY=uzun-ve-guclu-bir-anahtar
OPENROUTER_API_KEY=sk-or-...
LLAMAINDEX_API_KEY=sk-or-...
```

2. Konteynerleri başlatın:

```bash
docker compose up --build
```

3. Uygulama: http://localhost:5000

- **web:** Gunicorn + Flask (`FLASK_ENV=production`, `DEBUG=False`)
- **db:** PostgreSQL 16 (volume: `postgres_data`)
- **uploads / storage:** Kalıcı Docker volume'ları

Durdurmak:

```bash
docker compose down
```

Veritabanı verisini de silmek için:

```bash
docker compose down -v
```

### Ortam değişkenleri (Docker)

| Değişken | Açıklama |
|---|---|
| `SECRET_KEY` | Flask oturum gizli anahtarı (zorunlu, production) |
| `OPENROUTER_API_KEY` | OpenRouter API anahtarı |
| `LLAMAINDEX_API_KEY` | Embedding API (boşsa OPENROUTER kullanılır) |
| `DATABASE_URL` | docker-compose içinde PostgreSQL olarak ayarlı |
| `GUNICORN_WORKERS` | Opsiyonel, varsayılan `2` |

> API anahtarları `.env` dosyasında kalır; `.gitignore` ve `.dockerignore` ile repoya gitmez.
