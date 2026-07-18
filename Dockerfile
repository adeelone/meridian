FROM node:20-bookworm-slim AS frontend
WORKDIR /app/packages/frontend
COPY packages/frontend/package*.json ./
RUN npm ci
COPY packages/frontend ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MERIDIAN_HOME=/data \
    MERIDIAN_CORS_ORIGINS=

WORKDIR /app
COPY pyproject.toml README.md ./
COPY packages ./packages
COPY --from=frontend /app/packages/frontend/dist ./packages/frontend/dist
RUN python -m pip install --no-cache-dir .

EXPOSE 8000
VOLUME ["/data"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "packages/backend", "--host", "0.0.0.0", "--port", "8000"]
