#!/bin/bash
# Intelligent Joplin Librarian — Setup Script
# Uses uv for dependencies (see README). Creates .venv and sets up .env from template.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()     { echo -e "${RED}[ERR]${NC} $1"; }

echo "🤖 Intelligent Joplin Librarian — Setup"
echo "========================================"

# 1. uv (https://docs.astral.sh/uv/getting-started/installation/)
if ! command -v uv &>/dev/null; then
    err "uv not found. Install it first, e.g.: curl -LsSf https://astral.sh/uv/install.sh | sh"
    err "Or: brew install uv"
    exit 1
fi
info "uv $(uv --version | head -1) found"

# 2. Python check (uv will use a compatible interpreter)
if ! command -v python3 &>/dev/null; then
    err "Python 3 not found. Install Python 3.11+."
    exit 1
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
info "Python $PY_VER found"

if [ -d "venv" ] && [ ! -d ".venv" ]; then
    warn "Legacy venv/ detected — this project uses .venv (uv). Remove venv/ after verifying setup if you no longer need it."
fi

# 3. Install dependencies (runtime + dev for local work)
uv sync --all-groups
info "Dependencies installed (see pyproject.toml + uv.lock)"

# 4. Environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        info "Created .env from .env.example — edit it with your keys"
    else
        warn ".env.example not found — create .env manually"
    fi
else
    info ".env already exists"
fi

echo
echo "=========================================="
echo "  Setup complete!"
echo "=========================================="
echo
echo "Next steps:"
echo "  1. Edit .env with your API keys"
echo "  2. Start Joplin with Web Clipper enabled"
echo "  3. source .venv/bin/activate   # or: uv run python main.py"
echo "  4. python main.py"
echo
