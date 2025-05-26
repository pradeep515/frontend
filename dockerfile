FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv sync
COPY frontend ./frontend
COPY start.sh .
RUN chmod +x start.sh
EXPOSE 3000
CMD ["./start.sh"]