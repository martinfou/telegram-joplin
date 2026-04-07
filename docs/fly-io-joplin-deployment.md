# How Joplin is Deployed on Fly.io

Joplin doesn't run as a separate service — it runs **inside the same container** as the bot. This document explains the full architecture and deployment flow.

---

## Architecture Overview

| Component | How it works |
|-----------|-------------|
| **Joplin** | Installed as a Node.js CLI (`npm install -g joplin`) inside the Docker image |
| **Joplin server** | Started in the background by `entrypoint.sh` on port 41184 |
| **Bot** | Talks to Joplin via `http://localhost:41184` (same container) |
| **Data persistence** | Fly volume mounted at `/app/data` holds Joplin's profile + bot databases |
| **Deployment** | `fly deploy` (or auto-deploy via GitHub Actions on push to main) |
| **Cost** | Near-zero — machine sleeps when idle, wakes on Telegram webhook |

---

## 1. Docker Image: Everything in One Container

The `Dockerfile` builds a single image containing both the Python bot and the Joplin CLI:

- **Base**: `python:3.11-slim`
- **Node.js 18** is installed (required by Joplin CLI)
- **Joplin CLI** is installed globally via `npm install -g joplin`
- **Python dependencies** are installed with **uv** from `pyproject.toml` + `uv.lock` (`uv sync --frozen --no-dev` in the image)
- **Bot code** is copied in

The result is one image with: Python 3.11 + Node.js 18 + Joplin CLI + bot code.

---

## 2. Container Startup (`entrypoint.sh`)

When the container starts, `entrypoint.sh` orchestrates everything in order:

1. **Create data directories** — ensures `/app/data/joplin` and `/app/data/bot` exist (the volume mount overrides what the Dockerfile created)
2. **Configure Joplin API** — sets the API port to 41184 and pins the auth token from the `JOPLIN_WEB_CLIPPER_TOKEN` environment variable
3. **Start Joplin server** — runs `joplin server start &` in the background
4. **Wait for readiness** — polls `localhost:41184/ping` for up to 30 seconds
5. **Validate token alignment** — checks that the Joplin profile token matches the env variable (warns on mismatch)
6. **Launch the bot** — `exec python main.py` replaces the shell process with the bot

---

## 3. Fly.io Configuration (`fly.toml`)

Key settings in `fly.toml`:

### App and Region

- App name: `telegram-joplin`
- Region: `lax` (Los Angeles)

### Persistent Volume

```toml
[[mounts]]
  source = 'telegram_joplin_data'
  destination = '/app/data'
```

A Fly volume is mounted at `/app/data`. This is where Joplin's SQLite database, note attachments, and the bot's state databases all live. **Data survives redeploys and restarts.**

### Environment Variables

```toml
[env]
  PORT = '8080'
  FLY_APP_NAME = 'telegram-joplin'
  JOPLIN_WEB_CLIPPER_BASE_URL = 'http://localhost:41184'
```

The bot talks to Joplin via localhost — no network hops, no separate service.

### HTTP Service (Webhook Receiver)

```toml
[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 0
  max_machines_running = 1
```

- The bot listens on port 8080 for Telegram webhooks
- **Auto-sleep**: the machine stops when idle and wakes on the next incoming webhook (~10 seconds cold start)
- At most 1 machine runs at a time

### VM Size

```toml
[[vm]]
  size = 'shared-cpu-1x'
  memory = '1gb'
```

Smallest shared CPU tier (1 vCPU, 1 GB RAM) — sufficient for the Joplin CLI server and the Python bot.

---

## 4. Secrets

Sensitive values are stored as Fly secrets (injected as environment variables at runtime, never baked into the image):

```bash
fly secrets set TELEGRAM_BOT_TOKEN=xxx
fly secrets set JOPLIN_WEB_CLIPPER_TOKEN=xxx
fly secrets set DEEPSEEK_API_KEY=xxx
fly secrets set ALLOWED_TELEGRAM_USER_IDS=xxx
fly secrets set GOOGLE_CLIENT_ID=xxx
fly secrets set GOOGLE_CLIENT_SECRET=xxx
# ... any other secrets from .env.example
```

---

## 5. Deployment Pipeline (GitHub Actions)

Deployment is automated via `.github/workflows/ci.yml`:

1. Push to `main`
2. CI runs linting (`ruff`) and tests (`pytest`) on Python 3.11 and 3.12
3. If tests pass, the deploy job runs:
   - Installs `flyctl`
   - Verifies `FLY_API_TOKEN` secret exists
   - Runs `flyctl deploy --remote-only` (builds Docker image on Fly's remote builder and deploys)
4. Fly creates a new machine from the image, attaches the existing volume, and starts the container

For **manual deploys** from your local machine:

```bash
fly deploy
```

---

## 6. Initial Setup (One-Time)

These steps were performed once to create the Fly app:

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Log in
fly auth login

# 3. Create the app (uses existing fly.toml or generates one)
fly launch

# 4. Create the persistent volume (1 GB in the same region)
fly volumes create telegram_joplin_data --region lax --size 1

# 5. Set all secrets
fly secrets set \
  TELEGRAM_BOT_TOKEN=... \
  JOPLIN_WEB_CLIPPER_TOKEN=... \
  DEEPSEEK_API_KEY=... \
  ALLOWED_TELEGRAM_USER_IDS=...

# 6. Deploy
fly deploy
```

After this, every push to `main` auto-deploys via GitHub Actions.

---

## 7. Scheduled Scaling (Optional)

A GitHub Actions workflow (`.github/workflows/fly-schedule-scale.yml`) can keep the machine running during the day and scale to zero at night:

| Time window | Machines | Cost |
|-------------|----------|------|
| 6am–10pm (Eastern) | 1 running | ~$3–4/month |
| 10pm–6am (Eastern) | 0 (scaled to zero) | No compute cost |
| First request at night | Machine auto-starts, handles it, stops again | Pay only for that run |

See [fly-scheduled-scaling.md](fly-scheduled-scaling.md) for setup details.

---

## 8. Viewing Logs

Logs are written to stdout (JSON in production) and captured by Fly.io. To view them:

```bash
# Stream logs in real time (recommended for debugging)
fly logs -f

# Show last 100 lines
fly logs

# Specify app if you have multiple
fly logs -a telegram-joplin -f
```

**Log format**: In production (when `FLY_APP_NAME` is set), logs are JSON with `event`, `level`, `timestamp`, etc. Example:
```json
{"event": "Dream command received", "level": "info", "timestamp": "2026-03-05T18:26:05.123Z"}
```

**More verbose logs**: Set `DEBUG=true` in Fly secrets to enable DEBUG level:
```bash
fly secrets set DEBUG=true
fly deploy
```

---

## 9. Useful Commands

| Task | Command |
|------|---------|
| Deploy | `fly deploy` |
| **View logs (stream)** | `fly logs -f` |
| SSH into container | `fly ssh console` |
| Check app status | `fly status` |
| View logs (last 100) | `fly logs` |
| List volumes | `fly volumes list` |
| Set a secret | `fly secrets set KEY=value` |
| List secrets | `fly secrets list` |
| Restart app | `fly apps restart` |
| Export Joplin notes | `fly ssh console -C "joplin --profile /app/data/joplin export --format md /tmp/backup"` |
| Full Joplin backup | `fly ssh console -C "tar -czf - -C /app/data joplin" > backup.tar.gz` |

See [joplin-backup.md](joplin-backup.md) for detailed backup procedures.
