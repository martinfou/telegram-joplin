#!/usr/bin/env bash
# Documentation-Code Consistency Review (FR-036)
# Run before sprint planning or on-demand.
# Output: project-management/reports/doc-code-consistency-latest.md

set -e
cd "$(dirname "$0")/.."
PY="${PYTHON:-}"
if [ -z "$PY" ] && [ -x "$(dirname "$0")/../.venv/bin/python" ]; then
  PY="$(dirname "$0")/../.venv/bin/python"
fi
"${PY:-python3}" scripts/doc_code_review.py "$@"
