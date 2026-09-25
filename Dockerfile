FROM node:20-slim AS frontend-build
WORKDIR /frontend
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY dca-scraper-frontend/package*.json dca-scraper-frontend/pnpm-workspace.yaml ./
RUN pnpm install
COPY dca-scraper-frontend/ ./
RUN pnpm run build

FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-spa libgl1 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN rm -rf api-dca-ocr/public
COPY --from=frontend-build /frontend/dist ./api-dca-ocr/public

CMD gunicorn --chdir api-dca-ocr app:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 300