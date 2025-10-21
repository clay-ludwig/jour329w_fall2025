# Beat Book Agent with Tool-Based JSON Access

This directory contains an AI agent that generates beat books by exploring story data through tool calls rather than loading everything at once, solving context window limitations.

## Overview

The agent uses Anthropic's Claude with tool calling to:
1. Search and filter through story data intelligently
2. Explore only relevant stories in detail
3. Build understanding incrementally
4. Generate a comprehensive beat book

## Files

- **`beat_book_agent.py`** - Main agent script with CLI interface
- **`web_monitor.py`** - Web-based real-time monitor
- **`templates/index.html`** - Web UI for monitoring
- **`requirements.txt`** - Python dependencies

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your Anthropic API Key

**Option A: Using .env file (Recommended)**

Create a `.env` file in this directory:

```bash
cp .env.example .env
```

Then edit `.env` and add your API key:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

The scripts will automatically load this file.

**Option B: Environment variable**

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or add to your `.bashrc` or `.zshrc`:

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

### Option 1: Command Line (with Debug Logging)

Run the agent with detailed console output:

```bash
python beat_book_agent.py
```

**Features:**
- Real-time console logging
- Shows each tool call with inputs and results
- Displays iteration progress
- Saves output to `beat_book_YYYYMMDD_HHMMSS.md`
- Saves tool usage log to `tool_log_YYYYMMDD_HHMMSS.json`

**Example Output:**
```
[14:23:45] Loading story database from ../enhanced_beat_stories.json...
[14:23:46] ✓ Loaded 346 stories

================================================================================
Starting Beat Book Generation Agent
Model: claude-3-5-sonnet-20241022
================================================================================

[14:23:46] 🤖 Sending initial request to Claude...

────────────────────────────────────────────────────────────────────────────────
[14:23:47] Iteration 1/30
────────────────────────────────────────────────────────────────────────────────

[14:23:48] 🔧 TOOL CALL: get_stats
   Inputs: {}
   → Returned dict with 6 keys

[14:23:49] 🔧 TOOL CALL: filter_by_topic
   Inputs: {
     "topic": "Education",
     "limit": 100
   }
   → Returned 87 results
...
```

### Option 2: Web Interface (Visual Monitor)

Run the web-based monitor for a visual, real-time interface:

```bash
python web_monitor.py
```

Then open your browser to: **http://localhost:5000**

**Features:**
- Real-time visual updates
- Tool call tracking
- Activity log
- Statistics dashboard
- Live beat book preview
- Download generated output

**Screenshot Description:**
The web interface shows:
- Status badge (Idle/Running/Completed/Error)
- Live statistics (tool calls, iterations, stories explored)
- Tool calls panel with inputs/outputs
- Activity log
- Generated beat book preview
- Start generation button

## How It Works

### Tool-Based Data Access

Instead of loading the entire 13,000+ line JSON file, the agent has access to these tools:

1. **`get_stats()`** - Get dataset overview (topics, tags, categories)
2. **`search_by_keyword(keyword, fields, limit)`** - Search by keyword
3. **`filter_by_topic(topic, limit)`** - Get stories for a specific topic
4. **`filter_by_tag(tag, limit)`** - Find stories with a tag
5. **`filter_by_location(location, limit)`** - Filter by geographic focus
6. **`get_story_details(link)`** - Get full story content (when needed)
7. **`filter_by_category(category, limit)`** - Filter by story type
8. **`filter_by_follow_up_rating(min_rating, limit)`** - Find high-potential stories
9. **`get_related_stories(link, limit)`** - Find related coverage

### Agent Workflow

1. **Discovery Phase**: Agent calls `get_stats()` to understand the dataset
2. **Exploration Phase**: Agent uses filters to find relevant stories
3. **Deep Dive Phase**: Agent calls `get_story_details()` for promising stories
4. **Synthesis Phase**: Agent generates the beat book with citations

### Advantages Over Direct JSON Loading

- ✅ **No context window limits** - Only loads what's needed
- ✅ **Intelligent exploration** - Agent decides what to investigate
- ✅ **Faster processing** - Smaller, focused data chunks
- ✅ **Better quality** - Agent can explore more thoroughly
- ✅ **Debuggable** - See exactly what the agent is looking at

## Output

### Beat Book File

Generated as: `beat_book_v{N}.md` where N is an auto-incrementing version number.

The script automatically finds the highest existing version number and creates the next one:
- First run: `beat_book_v1.md`
- Second run: `beat_book_v2.md`
- Third run: `beat_book_v3.md`
- etc.

Contains:
- Introduction to the beat/topic
- Key people, institutions, and issues
- Examples from recent coverage
- Story ideas and undercovered angles
- Sources and locations
- Citations with links

### Tool Usage Log

Generated as: `tool_log_v{N}.json` (matches the beat book version number)

Contains:
- Timestamp of each tool call
- Tool name and inputs
- Result size
- Complete execution trace

Example:
```json
[
  {
    "timestamp": "14:23:48",
    "tool": "get_dataset_overview",
    "inputs": {},
    "result_size": 2847
  },
  {
    "timestamp": "14:23:49",
    "tool": "query_stories",
    "inputs": {
      "topic": "Education",
      "limit": 100
    },
    "result_size": 12453
  }
]
```

**Version Management:**
- Each run creates a new version (v1, v2, v3, etc.)
- Tool logs are paired with their beat book version
- Easy to compare iterations and track improvements

## Configuration

### Changing the Topic

Edit the initial message in `beat_book_agent.py` or `web_monitor.py`:

```python
messages = [
    {
        "role": "user",
        "content": "Please generate a comprehensive beat book for the [TOPIC] topic..."
    }
]
```

### Adjusting Model Settings

Modify the `run()` method parameters:

```python
agent.run(
    model="claude-3-5-sonnet-20241022",  # or "claude-3-opus-20240229"
    max_tokens=8000  # Increase for longer output
)
```

**Note:** The agent includes a 10-minute timeout (`timeout=600.0`) to handle long-running operations with many tool calls. If you need more time, adjust this in the `messages.create()` call.

### Setting Iteration Limits

Change `max_iterations` in the `run()` method:

```python
max_iterations = 30  # Prevent infinite loops
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"

Make sure you've exported your API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### "Story data not found"

Verify the path to `enhanced_beat_stories.json`:
```bash
ls ../enhanced_beat_stories.json
```

### Agent stops early

Check the tool log to see if the agent is getting the data it needs. You may need to adjust tool descriptions or limits.

### "Streaming is required for operations that may take longer than 10 minutes"

The agent already includes a 10-minute timeout. If you're still seeing this:
- The agent may be making too many tool calls - check `max_iterations` (default: 30)
- Consider using a faster model like `claude-3-haiku-20240307` for testing
- Increase the timeout in `beat_book_agent.py`: change `timeout=600.0` to `timeout=900.0` (15 minutes)

### Web monitor not connecting

Make sure port 5000 is available:
```bash
lsof -i :5000
```

Or change the port:
```bash
PORT=8080 python web_monitor.py
```

## Customization

### Adding New Tools

1. Add a method to `StoryDatabase` class:

```python
def custom_filter(self, param):
    """Your custom filter logic"""
    results = []
    # ... filtering logic ...
    return results
```

2. Add tool definition in `run()` method:

```python
{
    "name": "custom_filter",
    "description": "Description of what this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param"]
    }
}
```

3. Add execution in `_execute_tool()`:

```python
elif tool_name == "custom_filter":
    result = self.db.custom_filter(param=tool_input['param'])
```

### Modifying the System Prompt

Edit the prompt loaded from `prompt.txt` or add instructions in the agent initialization:

```python
self.system_prompt += """
Additional instructions for the agent...
"""
```

## Performance Tips

1. **Start with `get_stats()`** - Helps agent understand what's available
2. **Use appropriate limits** - Don't return more data than needed
3. **Filter before details** - Use summary filters first, then get full content
4. **Monitor tool usage** - Check if agent is making redundant calls

## Example Tool Call Sequence

A typical agent workflow:

```
1. get_stats() → Understand dataset
2. filter_by_topic("Education") → Get education stories  
3. filter_by_follow_up_rating(7) → Find high-potential stories
4. get_story_details(link1) → Read full story #1
5. get_story_details(link2) → Read full story #2
6. search_by_keyword("cellphone") → Find related coverage
7. filter_by_location("Baltimore") → Check local angle
8. get_related_stories(link1) → Find coverage patterns
9. [Generate beat book]
```

## Credits

This agent architecture demonstrates:
- Tool-based AI agents (function calling)
- Incremental data exploration
- Real-time monitoring with WebSockets
- Context window optimization
- Transparent AI decision-making

Built with:
- Anthropic Claude (Sonnet 3.5)
- Flask & Flask-SocketIO
- Python 3.8+
