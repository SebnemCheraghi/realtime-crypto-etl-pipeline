#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Preparing environment..."

if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker is not installed."
    exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
    echo "❌ Docker Compose is not available."
    exit 1
fi

if [ ! -f .env ]; then
    echo "📄 Creating .env..."
    cp .env.example .env
fi

if grep -q "^AIRFLOW__CORE__FERNET_KEY=$" .env; then
    echo "🔐 Generating Fernet key..."

    FERNET_KEY=$(openssl rand -base64 32 | tr -d '\n')

    sed -i \
      "s|^AIRFLOW__CORE__FERNET_KEY=.*|AIRFLOW__CORE__FERNET_KEY=${FERNET_KEY}|" \
      .env
fi

CURRENT_UID=$(id -u)

if grep -q "^AIRFLOW_UID=" .env; then
    sed -i "s|^AIRFLOW_UID=.*|AIRFLOW_UID=${CURRENT_UID}|" .env
else
    echo "AIRFLOW_UID=${CURRENT_UID}" >> .env
fi

echo "🐳 Starting Docker containers..."

docker compose down --volumes --remove-orphans

docker compose up -d --build

echo ""
echo "🔍 Services:"
docker compose ps

echo ""
echo "===================================="
echo "✅ Platform is running"
echo "===================================="
echo "Airflow: http://localhost:8081"
echo "Grafana: http://localhost:3001"
echo ""