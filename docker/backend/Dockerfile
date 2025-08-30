FROM python:3.11-slim

WORKDIR /backend

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
ENV PYTHONPATH="/backend/app:${PYTHONPATH}"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync

# Copy entrypoint script first and set permissions
COPY entrypoint.sh /backend/
RUN chmod +x /backend/entrypoint.sh

# Copy application code
COPY . .

EXPOSE 8000

ENTRYPOINT ["/backend/entrypoint.sh"]