FROM python:3.11.11-slim

WORKDIR /payment-backend

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH="/payment-backend:${PYTHONPATH}"

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY app ./app
COPY migration ./migration
COPY alembic.ini ./

EXPOSE 8001
# 8001 = payment-backend 트래픽 (FastAPI). 같은 포트에 /api/v1/* (외부) 와 /api/internal/* (서비스간) 가 prefix 로 공존.
# /api/internal/* 는 X-Internal-Token 헤더로 검증되며 네트워크상 cluster 내부에서만 도달 가능해야 한다.

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
