# Multi-stage build for smaller image
FROM python:3.10-slim as builder

WORKDIR /app

# Install Poetry for dependency management
RUN pip install poetry==1.7.1

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies without creating virtualenv
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --only main

# Runtime stage - smaller final image
FROM python:3.10-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start API
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]