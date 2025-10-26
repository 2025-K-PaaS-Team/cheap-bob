#!/bin/bash
set -e

# 환경 변수 설정
export DB_HOST=${DB_HOST:-postgres}
export DB_PORT=${DB_PORT:-5432}
export DB_USER=${DB_USER:-cheap}
export DB_PASSWORD=${DB_PASSWORD:-bob}
export DB_NAME=${DB_NAME:-cheapbob}

# 데이터베이스 연결 대기
echo "Waiting for database to be ready..."
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

echo "Database is up - executing migrations"

# 현재 디렉토리 확인
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Python 및 uv 환경 확인
echo "Python version:"
python --version
echo "UV version:"
uv --version

# 가상환경 재설치
echo "Installing dependencies..."
cd /backend
uv sync

# alembic 설치 확인
echo "Checking alembic installation..."
uv pip list | grep alembic || echo "alembic not found in pip list"

# 데이터베이스 마이그레이션 실행
echo "Running database migrations..."
uv run python -m alembic upgrade head

# 애플리케이션 시작
echo "Starting application..."
cd /backend && exec uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Docker 실행 실패하면 확인하기 -> chmod +x entrypoint-dev.sh