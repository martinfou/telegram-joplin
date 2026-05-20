# Project Context — Telegram Joplin Bot

## Stack
- Python 3.12+, uv package manager
- Telegram Bot API (python-telegram-bot)
- Joplin Web Clipper API (REST)
- Google Tasks API (OAuth2)
- DeepSeek API (LLM)
- Deployed on Fly.io (Docker)

## Core Flow
User sends Telegram message → LLM classifies → Task (Google Tasks) or Note (Joplin)
- GTD: tasks with next actions
- PARA: notes organized in Joplin

## Key Files
- main.py — Entry point
- src/ — Application code
- src/handlers/ — Telegram message handlers
- src/google_tasks_client.py — Google OAuth + Tasks sync
- src/joplin_client.py — Joplin Web Clipper client
- src/llm_orchestrator.py — LLM classification logic
