# User Documentation

## Getting Started

The Telegram-Joplin bot helps you create organized notes in Joplin from your Telegram messages using AI.

### Prerequisites

- Telegram account
- Joplin note-taking app installed and running
- API keys for AI service (DeepSeek recommended)

## Installation

### Automated Setup (Recommended)

1. **Download the project**
   ```bash
   git clone <repository-url>
   cd telegram-joplin
   ```

2. **Run setup script**
   ```bash
   ./setup.sh
   ```

3. **Configure environment**
   - Edit the created `.env` file
   - Add your API keys and settings

4. **Test installation**
   ```bash
   source .venv/bin/activate
   python test_setup.py
   ```

5. **Start the bot**
   ```bash
   python main.py
   ```

### Manual Setup

1. Install Python 3.11+ and [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Install dependencies: `uv sync --all-groups` (uses `pyproject.toml` and `uv.lock`)
3. Configure `.env` file
4. Run tests and start bot (`uv run pytest …` / `uv run python main.py` as needed)

## Configuration

### Required Settings

Create a `.env` file with:

```env
# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Your Telegram User ID (get from @userinfobot)
ALLOWED_TELEGRAM_USER_IDS=123456789

# AI Provider (choose one)
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_key

# Joplin (get token from Web Clipper settings)
JOPLIN_WEB_CLIPPER_TOKEN=your_joplin_token
```

### Optional Settings

```env
# Debug logging
DEBUG=true

# Custom ports
OLLAMA_BASE_URL=http://localhost:11434
JOPLIN_WEB_CLIPPER_PORT=41184
```

## Usage

### Basic Workflow

1. **Send a message** to your bot describing what you want to note
2. **AI processes** your message and suggests folder and tags
3. **Note created** automatically in Joplin
4. **Confirmation** sent back with folder name

### Example Messages

```
"Meeting notes from client call about new website project"
"Recipe for chocolate chip cookies - use dark chocolate"
"Idea: Add dark mode toggle to the app settings"
"Book recommendation: 'Atomic Habits' by James Clear"
```

### Clarification Process

If your message is unclear, the bot will ask for clarification:

```
Bot: I need more information about what folder this should go in.
What type of content is this? (work/personal/project/etc.)
```

Reply with additional details.

### Folder Organization

The bot automatically chooses from your existing Joplin folders:

- **00-Inbox**: Temporary notes, quick captures
- **01-Projects**: Active projects and tasks
- **02-Areas**: Areas of responsibility
- **03-Resources**: Reference materials
- **04-Archive**: Completed items (avoided)

### Tagging

Notes are automatically tagged based on content. Common tags include:
- AI, project, meeting, recipe, idea, book, etc.

## Troubleshooting

### Bot Not Responding

1. Check if bot is running: `python main.py`
2. Verify Telegram token is correct
3. Check user ID is in allowed list

### Joplin Connection Issues

1. Ensure Joplin is running
2. Enable Web Clipper in Joplin settings
3. Verify API token
4. Check firewall allows port 41184

### AI Not Working

1. Verify API key is set correctly
2. Check internet connection
3. Try different AI provider in config

### Common Errors

- **"Not authorized"**: Your Telegram ID not in allowed list
- **"Joplin not accessible"**: Joplin not running or Web Clipper disabled
- **"Invalid message"**: Message too short or contains invalid characters

## Advanced Features

### Custom Folders

Add your own folders in Joplin - the bot will learn to use them.

### Multiple Users

Add multiple user IDs to `ALLOWED_TELEGRAM_USER_IDS` (comma-separated).

### Different AI Providers

Switch between:
- **DeepSeek**: Recommended, good balance of speed/cost
- **OpenAI**: GPT models, requires API key
- **Ollama**: Local models, no API costs

## Project Sync (Joplin ↔ Google Tasks)

When enabled, project sync maps Joplin project folders to parent tasks in Google Tasks. Tasks you create for a project appear as subtasks under the correct parent. See [Project Sync](project-sync.md) for:

- What project sync does and how to enable it
- Folder naming and configuration
- Commands: `/tasks_toggle_project_sync`, `/tasks_sync_projects`, `/tasks_reset_project_sync`
- [Troubleshooting](project-sync-troubleshooting.md) for common issues

## Workflow Guide

See [GTD + Second Brain Workflow](gtd-second-brain-workflow.md) for a complete guide on using Google Tasks and Joplin together, including:

- When to create a task vs a note
- Full project walkthroughs (with the "Learn to Sing Harmonies" example)
- Decision framework for where things go
- Weekly review process
- Quick reference for common scenarios

## Testing

- **Project sync smoke test** — Run `./scripts/smoke_project_sync.sh` for automated tests. See [scripts/smoke_project_sync.md](../../scripts/smoke_project_sync.md) for manual production verification steps.

## Support

For issues:
1. Check logs in console output
2. Verify configuration
3. Test with `python test_setup.py`
4. Check GitHub issues for known problems

## Security

- Only authorized Telegram users can use the bot
- Messages are processed securely
- API keys stored locally in `.env` file
- No user data sent to external services