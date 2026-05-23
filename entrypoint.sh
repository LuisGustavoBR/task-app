#!/bin/sh
set -e

echo "[entrypoint] Aplicando migrations..."
alembic upgrade head
echo "[entrypoint] Migrations concluídas. Iniciando servidor..."

exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --proxy-headers \
    --forwarded-allow-ips "*"
