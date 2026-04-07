---
template_version: 1.1.0
last_updated: 2026-01-24
compatible_with: [defect-fix, sprint-planning, product-backlog]
requires: [docker, docker-compose]
---

# User Story: US-018 - Docker Compose Setup for Telegram-Joplin Bot and Joplin Server

**Status**: ⭕ To Do
**Priority**: 🟢 Low
**Story Points**: 8 (Fibonacci: 1, 2, 3, 5, 8, 13)
**Created**: 2026-01-24
**Updated**: 2026-03-01
**Assigned Sprint**: Backlog

## Description

Create a comprehensive Docker Compose setup that containerizes the Telegram-Joplin bot application and the Joplin headless server. This will simplify deployment, ensure consistent environments across machines, and make it easier for users to run the entire system without manual installation of dependencies.

## User Story

As a user who wants to deploy the Telegram-Joplin bot, I want a single Docker Compose file that sets up both the bot and Joplin server, so that I can have the entire system running with a single command without worrying about Python dependencies or Joplin server configuration.

## Acceptance Criteria

- [x] Dockerfile created for Telegram-Joplin bot Python application (Python 3.11-slim + Node.js for Joplin CLI)
- [x] Dockerfile includes all required dependencies
- [x] Dockerfile uses Python 3.10+ base image with security best practices
- [ ] docker-compose.yml created with both services (bot and Joplin server) — **bot only**, no Joplin server
- [ ] Python bot service runs with volume mount for live code updates — uses `./data` bind mount, not named volumes
- [ ] Joplin server service configured with official or custom Docker image — **not implemented**
- [ ] Data persistence implemented with named volumes for Joplin data — **not implemented**
- [x] Environment variables configured for bot (TELEGRAM_BOT_TOKEN, etc.)
- [ ] Environment variables configured for Joplin server (APP_BASE_URL, etc.) — **not implemented**
- [ ] Networking configured between containers — **not implemented** (single container)
- [ ] Port mappings defined (Joplin: 22300, Bot: internal) — **not implemented**
- [x] .env.example created with all required variables
- [ ] Docker setup documented in README with quick start instructions — **partial**
- [ ] Docker setup tested with fresh deployment
- [ ] Health checks implemented for both services — **not implemented**
- [x] Docker ignore file created to exclude unnecessary files

## Business Value

This feature improves user experience and reduces deployment friction by:
- Enabling single-command deployment of the entire system
- Eliminating dependency management headaches
- Ensuring consistent environment across all deployments
- Making the application easier to test and share
- Reducing setup time from hours to minutes
- Supporting both development and production environments
- Making backup and migration of Joplin data simple

## Technical Requirements

### Dockerfile for Python Bot

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run the bot
CMD ["python", "main.py"]
```

### docker-compose.yml Structure

```yaml
version: '3.8'

services:
  telegram-joplin-bot:
    build: .
    container_name: telegram-joplin-bot
    depends_on:
      joplin-server:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./config:/app/config
      - ./logs:/app/logs
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - JOPLIN_WEB_CLIPPER_TOKEN=${JOPLIN_WEB_CLIPPER_TOKEN}
      - JOPLIN_WEB_CLIPPER_PORT=41184
      - JOPLIN_SERVER_URL=http://joplin-server:22300
      - LLM_PROVIDER=${LLM_PROVIDER}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    networks:
      - joplin-network

  joplin-server:
    image: joplin/server:latest
    container_name: joplin-server
    ports:
      - "22300:22300"
    volumes:
      - joplin-data:/home/joplin/.config/joplin
      - joplin-db:/home/joplin/.local/share/joplin
    environment:
      - APP_BASE_URL=http://joplin-server:22300
      - DB_CLIENT=pg
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DATABASE=${POSTGRES_DATABASE}
    restart: unless-stopped
    networks:
      - joplin-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:22300/api/ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: joplin-postgres
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DATABASE=${POSTGRES_DATABASE}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - joplin-network

volumes:
  joplin-data:
  joplin-db:
  postgres-data:

networks:
  joplin-network:
    driver: bridge
```

### Implementation Tasks

1. **Create Dockerfile**
   - Use Python 3.10-slim as base image
   - Install system dependencies (git, curl, etc.)
   - Copy and install Python requirements
   - Set working directory to /app
   - Configure entrypoint for bot startup

2. **Create docker-compose.yml**
   - Define three services: bot, Joplin server, PostgreSQL database
   - Configure volumes for data persistence
   - Set up environment variables
   - Configure networking between containers
   - Add health checks for service readiness

3. **Create .env.example**
   - Document all required environment variables
   - Provide example values for each variable
   - Include comments explaining each variable
   - Note which are required vs optional

4. **Update Configuration**
   - Update config.py to read environment variables
   - Support both file-based and environment variable config
   - Add validation for required environment variables

5. **Documentation**
   - Update README with Docker quick start
   - Document environment variable setup
   - Provide troubleshooting guide
   - Include examples for different deployment scenarios

## Reference Documents

- Docker configuration: `docker/Dockerfile`
- Docker Compose: `docker-compose.yml`
- Environment variables: `.env.example`
- Documentation: `docs/DOCKER-SETUP.md`

## Technical References

- Official Python Docker images: https://hub.docker.com/_/python
- Joplin Server Docker image: https://hub.docker.com/r/joplin/server
- PostgreSQL Docker image: https://hub.docker.com/_/postgres
- Docker Compose documentation: https://docs.docker.com/compose/

## Dependencies

- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- US-014 (Daily Priority Report) - for logging and monitoring
- US-015 (Weekly Review Report) - for background task scheduling

## Estimated Effort

- Dockerfile creation: 2 hours
- docker-compose.yml configuration: 2 hours
- Environment variable setup: 1 hour
- Documentation and testing: 2 hours
- **Total**: ~8 story points

## Notes

- This feature supports both development and production environments
- PostgreSQL is included for scalability, but SQLite could be alternative
- Health checks ensure services are ready before starting the bot
- Volume mounts allow hot-reloading of code during development
- Environment-based configuration ensures security (no hardcoded tokens)
- Docker setup follows best practices for Python and Joplin deployments
- Compatible with Docker Desktop and server-based Docker installations

## Considerations

### Development vs Production

**Development**:
- Hot reload enabled via volume mounts
- Debug logging enabled
- Use SQLite for simplicity

**Production**:
- Immutable image with code baked in
- Minimal logging
- PostgreSQL for reliability
- Proper secret management

### Security

- Use environment variables for all secrets
- Never commit .env files to git
- Use health checks to detect failed services
- Configure container restart policies
- Use non-root user in container (future enhancement)

### Scalability

- PostgreSQL database ensures horizontal scalability
- Docker Compose can be evolved to Kubernetes manifests
- Current setup suitable for small to medium deployments
- No load balancing needed for single bot instance

## Implementation Status (as of 2026-03-01)

### What's Done (~30%)
- `Dockerfile` exists (Python 3.11-slim base, Node.js for Joplin CLI)
- `docker-compose.yml` exists but defines **bot service only**
- `.env.example` exists with all bot environment variables
- `.dockerignore` exists

### What's Missing (~70%)
- Joplin server container (`joplin/server:latest`)
- PostgreSQL container for Joplin data
- Named volumes for Joplin data persistence
- Container networking (`joplin-network`)
- Health checks for all services
- Port mappings for Joplin server
- Full documentation with quick start
- Fresh deployment testing

## History

- 2026-01-24 - Created feature request
- 2026-03-01 - Status updated to ⏳ In Progress (~30%) based on code review

