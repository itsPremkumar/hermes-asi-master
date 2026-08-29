# Dockerfile — HERMES-ASI-MASTER Container Image

FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash hermes \
    && chown -R hermes:hermes /app
USER hermes

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python profiles/hermes-asi-master/scripts/health_check.py || exit 1

# Default command
ENTRYPOINT ["python", "-m", "hermes_asi_master"]
CMD ["orchestrate"]

# Production stage
FROM base AS production
ENV ENVIRONMENT=production
EXPOSE 8080

# Development stage
FROM base AS development
ENV ENVIRONMENT=development
RUN pip install pytest pytest-asyncio pytest-cov ipython
EXPOSE 8080 5678
