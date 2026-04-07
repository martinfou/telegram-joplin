# Developer Guide

This guide helps contributors run, debug, and extend the bot safely.

## Local Development Flow

```mermaid
flowchart TD
    A[Clone repo] --> B[Install uv]
    B --> C[uv sync --all-groups]
    C --> D[Copy .env.example to .env]
    D --> E[Set keys and tokens]
    E --> F[Run python main.py]
    F --> G[Test in Telegram]
```

## Where to Make Changes

- Commands and user interactions: `src/handlers/`
- Service logic: `src/*_service.py`, `src/*_orchestrator.py`
- External integrations: `src/joplin_client.py`, `src/google_tasks_client.py`
- Settings and env vars: `src/settings.py`, `.env.example`
- Health/webhooks: `src/webhook_server.py`

## Runtime Files

- Local default paths:
  - `data/bot/bot_logs.db`
  - `data/bot/conversation_state.db`
- Configure with:
  - `LOGS_DB_PATH`
  - `STATE_DB_PATH`

## Pre-Commit Hook

Run lint and mypy automatically before each commit:

```bash
cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

## Contribution Flow

```mermaid
flowchart LR
    I[Implement change] --> T[Run ruff + pytest via uv run]
    T --> D[Update docs]
    D --> C[Commit]
    C --> P[Push branch]
    P --> R[Open PR]
```
