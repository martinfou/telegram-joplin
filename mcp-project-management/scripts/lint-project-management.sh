#!/bin/bash
# Project Management Lint Script
# Runs extremely anal checks: validation, links, forbidden terminology, newline at EOF.
# Run from project root.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PM_DIR="$PROJECT_ROOT/project-management"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

echo "=== Project Management Lint ==="
echo ""

# 1. Backlog validation
echo "1. Backlog validation..."
if [ -f "$SCRIPT_DIR/validate-backlog.sh" ]; then
    (cd "$PROJECT_ROOT" && "$SCRIPT_DIR/validate-backlog.sh" project-management/backlog) || ERRORS=$((ERRORS+1))
else
    echo -e "${YELLOW}  ⚠ validate-backlog.sh not found${NC}"
fi
echo ""

# 2. Link check
echo "2. Link check..."
if [ -f "$SCRIPT_DIR/check-links.sh" ]; then
    (cd "$PROJECT_ROOT" && "$SCRIPT_DIR/check-links.sh" project-management .) || ERRORS=$((ERRORS+1))
else
    echo -e "${YELLOW}  ⚠ check-links.sh not found${NC}"
fi
echo ""

# 3. Forbidden terminology (exclude docs that define or describe the rules)
echo "3. Forbidden terminology check..."
EXCLUDE_FILES="acceptance-criteria-for-project-naming-conventions|scripts/README.md|lint-project-management|glossary.md"
# Check grooming, PBI, tech debt, WIP
VIOLATIONS=$(grep -r -E '\b(grooming|PBI|tech debt|WIP)\b' "$PM_DIR" --include="*.md" 2>/dev/null | grep -vE "$EXCLUDE_FILES" || true)
# Check "bug" except in defect-template's allowed "defect (bug)" parenthetical, and
# legacy paths/filenames that still contain the substring (bug-fix-template.md, sprint-*-bug-fixes.md).
BUG_VIOLATIONS=$(grep -r -E '\bbug\b' "$PM_DIR" --include="*.md" 2>/dev/null | grep -vE "$EXCLUDE_FILES" | grep -v "defect-template" | grep -v "defect (bug)" | grep -vE 'bug-fix-template|polish-and-bug-fixes' || true)
VIOLATIONS=$(echo -e "${VIOLATIONS}\n${BUG_VIOLATIONS}" | grep -v '^$')
if [ -n "$VIOLATIONS" ]; then
    echo -e "${RED}  ✗ Forbidden terms found (use: user story, defect, technical debt, backlog refinement):${NC}"
    echo "$VIOLATIONS" | while read -r line; do echo "    $line"; done
    ERRORS=$((ERRORS+1))
else
    echo -e "${GREEN}  ✓ No forbidden terminology${NC}"
fi
echo ""

# 4. Newline at EOF
echo "4. Newline at EOF check..."
NO_NEWLINE=""
while IFS= read -r -d '' f; do
    [ -s "$f" ] || continue
    last=$(tail -c 1 "$f" | xxd -p 2>/dev/null)
    if [ "$last" != "0a" ] && [ -n "$last" ]; then
        NO_NEWLINE="$NO_NEWLINE $f"
    fi
done < <(find "$PM_DIR" -name "*.md" -print0 2>/dev/null)
if [ -n "$NO_NEWLINE" ]; then
    echo -e "${YELLOW}  ⚠ Files missing newline at EOF:${NC}"
    echo "$NO_NEWLINE" | tr ' ' '\n' | grep -v '^$' | while read -r f; do echo "    $f"; done
else
    echo -e "${GREEN}  ✓ All files have newline at EOF${NC}"
fi
echo ""

# Summary
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Lint passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Lint failed with $ERRORS error(s)${NC}"
    exit 1
fi
