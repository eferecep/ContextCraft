# ContextCraft — production imajı (Python 3.9: proje bağımlılıkları ile uyumlu)
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh \
    && mkdir -p uploads storage

ENV FLASK_APP=run.py \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]
