#!/usr/bin/env bash
# Smoke test for project sync (US-034 / Sprint 16 T-007)
# Runs automated tests and documents manual production verification.
#
# Usage:
#   ./scripts/smoke_project_sync.sh          # Run automated tests only
#   ./scripts/smoke_project_sync.sh --help   # Show manual steps
#
# See scripts/smoke_project_sync.md for full manual smoke test procedure.

set -e
cd "$(dirname "$0")/.."

# Use .venv or legacy venv if available (run from project root after ./setup.sh)
if [[ -d .venv/bin ]]; then
    # shellcheck disable=SC1091
    . .venv/bin/activate
elif [[ -d venv/bin ]]; then
    # shellcheck disable=SC1091
    . venv/bin/activate
fi

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Project Sync Smoke Test"
    echo ""
    echo "Automated: Run project sync unit and integration tests"
    echo "  ./scripts/smoke_project_sync.sh"
    echo ""
    echo "Manual: See scripts/smoke_project_sync.md for production verification steps"
    exit 0
fi

echo "=== Project Sync Smoke Test (automated) ==="
echo ""
echo "Running project sync tests..."
python -m pytest tests/test_task_service.py tests/test_project_sync_integration.py -v --tb=short

echo ""
echo "✅ Automated tests complete."
echo ""
echo "For production verification, run the manual steps in scripts/smoke_project_sync.md"
