# telegram-joplin Project Rules

## Stack
- Python (joplin + Google Tasks MCP server)
- Hermione / Hermes agent integration

## Commit conventions
Before committing, query Joplin MCP for "Commit Message Conventions" and follow the format.

## Code patterns
- Python 3.10+ type hints
- FastMCP for MCP server
- httpx for async HTTP
- Use `uv` for package management

## Git
- Feature branches from `main`
- Atomic commits
