FROM python:3.11-slim

# Install Node.js 18 (for Joplin CLI) and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates make g++ socat \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Joplin CLI globally
RUN npm install -g joplin

# uv — Python dependency install (matches CI / local dev)
COPY --from=ghcr.io/astral-sh/uv:0.11.3 /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN mkdir -p /app/data/bot /app/data/joplin \
    && chmod +x /app/entrypoint.sh

ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV LOGS_DB_PATH=/app/data/bot/bot_logs.db
ENV STATE_DB_PATH=/app/data/bot/conversation_state.db
ENV JOPLIN_PROFILE=/app/data/joplin

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
