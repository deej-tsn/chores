FROM python:3.12-slim AS base

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies into the system environment (no venv)
RUN uv sync --no-dev --frozen --no-install-project

# Now copy in your application code
COPY . .

EXPOSE 8000

# Use gunicorn with Uvicorn workers for production
CMD ["uv", "run", "gunicorn", "main:app", \
     "--bind", "0.0.0.0:8000", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4"]