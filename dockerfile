# FROM python:3.11-slim

# WORKDIR /app
# COPY pyproject.toml .
# COPY rxconfig.py .
# RUN pip install uv && uv sync
# COPY frontend ./frontend
# COPY start.sh .
# RUN chmod +x start.sh
# EXPOSE 3000
# CMD ["./start.sh"]
FROM python:3.11-slim

# Install build dependencies and Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock .
COPY rxconfig.py .
RUN pip install uv && uv sync --frozen
COPY frontend ./frontend
COPY start.sh .
RUN chmod +x start.sh
# Verify reflex installation
RUN /app/.venv/bin/reflex --version
EXPOSE 3000
CMD ["./start.sh"]