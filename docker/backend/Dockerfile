FROM python:3.11-slim

# Set working directory
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
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync

# Copy application code
COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database to be ready\n\
echo "Waiting for database..."\n\
while ! pg_isready -h $DB_HOST -p ${DB_PORT:-5432} -U $DB_USER; do\n\
    sleep 1\n\
done\n\
\n\
# Run database migrations\n\
echo "Running database migrations..."\n\
uv run alembic upgrade head\n\
\n\
# Start the application\n\
echo "Starting application..."\n\
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]