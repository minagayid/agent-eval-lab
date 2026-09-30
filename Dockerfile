FROM node:22-bookworm-slim AS web
WORKDIR /web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
COPY . .
COPY --from=web /web/dist /app/web/dist
RUN pip install --no-cache-dir '.[postgres]' && useradd -m runner && chown -R runner:runner /app
USER runner
CMD ["uvicorn", "agent_eval.api:app", "--host", "0.0.0.0", "--port", "8000"]
