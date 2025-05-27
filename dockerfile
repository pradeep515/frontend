FROM python:3.11-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y curl git unzip && rm -rf /var/lib/apt/lists/*

# Install uv and reflex
RUN pip install --no-cache-dir uv reflex
RUN pip install reflex-chakra
RUN pip install cryptography
RUN pip install --force-reinstall python-jose==3.3.0
RUN pip install --force-reinstall python-dotenv

# Copy only dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync

# Copy the rest of the application
COPY . /app

# Make start.sh executable
RUN chmod +x start.sh

EXPOSE 3000

CMD ["/bin/sh", "./start.sh"]