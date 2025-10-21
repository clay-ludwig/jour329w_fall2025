#!/bin/bash
# Quick launcher for Beat Book Agent

echo "=========================================="
echo "Beat Book Agent Launcher"
echo "=========================================="
echo ""

# Load .env file if it exists
if [ -f .env ]; then
    echo "✓ Loading .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not found"
    echo ""
    echo "Please set your Anthropic API key:"
    echo ""
    echo "Option 1 - Create a .env file:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your API key"
    echo ""
    echo "Option 2 - Export as environment variable:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    exit 1
fi

echo "✓ API key found"
echo ""

# Check for dependencies
if ! python3 -c "import anthropic" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

echo "Choose an option:"
echo "  1) Command Line Interface (CLI with debug logging)"
echo "  2) Web Interface (visual monitor at http://localhost:5000)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "Starting CLI agent..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 beat_book_agent.py
        ;;
    2)
        echo ""
        echo "Starting web monitor..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Open your browser to: http://localhost:5000"
        echo "Press Ctrl+C to stop"
        echo ""
        python3 web_monitor.py
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
