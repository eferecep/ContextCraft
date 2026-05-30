#!/bin/sh
set -e

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "degistir-bunu-guclu-bir-anahtar-ile" ]; then
    echo "UYARI: Production için güçlü bir SECRET_KEY tanımlayın."
fi

echo "Veritabanı migration çalıştırılıyor..."
attempt=0
max_attempts=30
until flask db upgrade; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge "$max_attempts" ]; then
        echo "Migration başarısız: veritabanına bağlanılamadı."
        exit 1
    fi
    echo "DB henüz hazır değil, tekrar deneniyor ($attempt/$max_attempts)..."
    sleep 2
done

workers="${GUNICORN_WORKERS:-2}"
echo "Gunicorn başlatılıyor (workers=$workers)..."
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers "$workers" \
    --timeout 120 \
    run:app
