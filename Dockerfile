FROM python:3.14-slim

# Keep output readable and avoid writing .pyc files inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Python packaging/runner) for repeatable dependency management.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies first to leverage Docker layer caching.
COPY pyproject.toml uv.lock ./
# Use lockfile if compatible; allow resolution from pyproject for updated deps.
RUN uv sync --no-dev --python /usr/local/bin/python

# Copy the application code last to keep rebuilds fast during development.
COPY . .

EXPOSE 8000

# Default to Gunicorn for production-style execution.
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
