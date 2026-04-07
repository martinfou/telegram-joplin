#!/bin/bash
# Link Checker Script
# Checks for broken markdown links in project-management files.
# By default validates the entire project-management/ tree.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default paths - run from project root
# Default: entire project-management/ tree (not just backlog)
SCAN_DIR="${1:-project-management}"
BASE_DIR="${2:-.}"

echo "Checking markdown links in $SCAN_DIR..."
echo "----------------------------------------"

# Use temp file for error count (subshells in pipes lose variable updates)
ERROR_FILE=$(mktemp)
trap "rm -f $ERROR_FILE" EXIT
echo 0 > "$ERROR_FILE"

# Function to check if a file exists
check_link() {
    local link="$1"
    local source_file="$2"
    local source_dir=$(dirname "$source_file")
    
    # Remove markdown link syntax and strip URL fragment for file check
    link=$(echo "$link" | sed 's/.*(\(.*\))/\1/')
    link="${link%%#*}"  # Strip #fragment for file existence check
    
    # Handle relative paths
    if [[ "$link" == /* ]]; then
        # Absolute path
        target="$BASE_DIR$link"
    else
        # Relative path
        target="$source_dir/$link"
    fi
    
    # Check if file exists
    if [ -f "$target" ]; then
        return 0
    else
        return 1
    fi
}

# Find all markdown files
FILES=$(find "$SCAN_DIR" -name "*.md" 2>/dev/null || true)

if [ -z "$FILES" ]; then
    echo -e "${YELLOW}⚠ No markdown files found in $SCAN_DIR${NC}"
    exit 0
fi

# Check each file
while IFS= read -r file; do
    [ -z "$file" ] && continue
    
    echo "Checking: $file"
    
    # Extract markdown links
    LINKS=$(grep -o "\[.*\]([^)]*)" "$file" 2>/dev/null || true)
    
    [ -z "$LINKS" ] && continue
    
    # Check each link
    while IFS= read -r link; do
        [ -z "$link" ] && continue
        
        # Skip external links (http/https)
        echo "$link" | grep -q "http" && continue
        
        # Skip known template placeholder paths (see scripts/README.md)
        link_target=$(echo "$link" | sed 's/.*(\(.*\))/\1/' | sed 's/#.*//')
        echo "$link_target" | grep -qE '\*|path/to/|-story-name\.md|-feature-name\.md|-user-authentication\.md|-defect-description\.md|-description\.md$' && continue
        # Joplin resource URLs, local file URLs, and obvious placeholders
        echo "$link_target" | grep -qE '^(:/|file://)' && continue
        echo "$link_target" | grep -qE 'resource_id|\{resource' && continue
        echo "$link_target" | grep -qE '^(image_url|link)$' && continue
        [[ "$link_target" == *".cursorrules" ]] && continue
        # Skip backlog-relative paths in templates (correct when template is copied to backlog/)
        if [[ "$file" == *"/templates/"* ]] && echo "$link_target" | grep -qE '^(user-stories|defects|technical-debt|retrospective-improvements)/'; then
            continue
        fi
        # Skip product-backlog links in templates (path is correct when template is copied to backlog/user-stories/, backlog/defects/, or backlog/technical-debt/)
        if [[ "$file" == *"/templates/"* ]] && echo "$link_target" | grep -q 'product-backlog\.md'; then
            continue
        fi
        
        # Check if link target exists
        if check_link "$link" "$file"; then
            echo -e "  ${GREEN}✓ $link${NC}"
        else
            echo -e "  ${RED}✗ Broken link: $link (in $file)${NC}"
            count=$(cat "$ERROR_FILE")
            echo $((count + 1)) > "$ERROR_FILE"
        fi
    done <<< "$LINKS"
done <<< "$FILES"

ERRORS=$(cat "$ERROR_FILE")

# Summary
echo "----------------------------------------"
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✓ Link check passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ERRORS broken link(s)${NC}"
    exit 1
fi
