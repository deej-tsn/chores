FROM python:3.13-slim AS base

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy only dependency files first
COPY ./pyproject.toml ./uv.lock ./

# Install dependencies into the system environment (no venv)
RUN uv sync --no-dev --frozen --no-install-project

# Copy application source
COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--proxy-headers", \
     "--forwarded-allow-ips=*", \ 
     "--root-path", "/api"]