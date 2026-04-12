FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

RUN apt-get update && apt-get install -y gettext curl && rm -rf /var/lib/apt/lists/*

RUN groupadd -r bloguser && useradd -r -g bloguser bloguser

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

COPY backend/ backend/
COPY scripts/ scripts/

RUN mkdir -p backend/logs backend/static backend/media

RUN chmod +x scripts/entrypoint.sh

RUN chown -R bloguser:bloguser /app

USER bloguser

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "settings.asgi:application"]