#!/bin/bash
# Start script for Telegram-Joplin Bot
# This script activates the virtual environment and starts the bot
# without modifying any configuration files

set -e

echo "🚀 Starting Telegram-Joplin Bot..."

# Check if virtual environment exists (support venv or .venv)
VENV_DIR=""
if [ -d "venv" ]; then
    VENV_DIR="venv"
elif [ -d ".venv" ]; then
    VENV_DIR=".venv"
else
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please configure your environment variables."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if bot is already running
if pgrep -f "python main.py" > /dev/null; then
    echo "⚠️  Bot appears to be already running. Kill existing process? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "🛑 Killing existing bot processes..."
        pkill -f "python main.py"
        sleep 2
    else
        echo "✅ Keeping existing bot running."
        deactivate
        exit 0
    fi
fi

# Test setup before starting
echo "🧪 Running setup test..."
if python tests/test_setup.py > /dev/null 2>&1; then
    echo "✅ Setup test passed"
else
    echo "❌ Setup test failed. Please check your configuration."
    deactivate
    exit 1
fi

# Start the bot
echo "🤖 Starting bot..."
python main.py

# Deactivate when done
deactivate