FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync

# Copy entrypoint script first and set permissions
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy application code
COPY . .

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]