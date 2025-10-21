# Quick Start Guide

Get up and running with the Beat Book Agent in 5 minutes!

## Step 1: Install Dependencies

```bash
cd /workspaces/jour329w_fall2025/ludwig/cns_collections/agent_experiment
pip install -r requirements.txt
```

## Step 2: Set Your API Key

### Option A: Using .env file (Recommended)

Create a `.env` file in the `agent_experiment` directory:

```bash
cp .env.example .env
```

Then edit `.env` and replace `your-api-key-here` with your actual API key:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

### Option B: Environment Variable

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

💡 **Tip:** Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent:
```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Test Your Setup

```bash
python3 test_setup.py
```

This will verify:
- ✓ Python version
- ✓ Dependencies installed
- ✓ API key set
- ✓ Data files present
- ✓ Database functions working

## Step 4: Run the Agent

### Option A: Simple Launcher (Recommended for First Time)

```bash
./run.sh
```

Choose option 1 (CLI) or 2 (Web) when prompted.

### Option B: Direct CLI Execution

```bash
python3 beat_book_agent.py
```

Watch the real-time console output as the agent:
- Makes tool calls to explore data
- Gathers relevant stories
- Synthesizes information
- Generates the beat book

### Option C: Web Interface

```bash
python3 web_monitor.py
```

Open your browser to: **http://localhost:5000**

Click "Start Generation" and watch the agent work in real-time!

## Step 5: View Results

Your beat book will be saved as:
```
beat_book_v1.md  (first run)
beat_book_v2.md  (second run)
beat_book_v3.md  (third run)
...etc.
```

And the tool usage log as:
```
tool_log_v1.json
tool_log_v2.json
tool_log_v3.json
...etc.
```

The version numbers auto-increment, so you can easily compare iterations!

## Example Output

After running successfully, you should see:

```
================================================================================
✅ Beat book generated successfully!
📄 Output saved to: beat_book_v4.md
📝 Version: v4
🔧 Tool calls made: 15
================================================================================
```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
→ Go back to Step 2

### "ModuleNotFoundError: No module named 'anthropic'"
→ Go back to Step 1

### Agent making too many tool calls
→ Normal! The agent explores thoroughly before writing

### Output seems incomplete
→ Try increasing `max_tokens` in the script (default: 8000)

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Try the tool demo: `python3 test_setup.py --demo`
- Customize the system prompt in `prompt.txt`
- Adjust tool limits and parameters in `beat_book_agent.py`

## Demo the Tools

See what the agent has access to:

```bash
python3 test_setup.py --demo
```

This demonstrates:
- Getting database statistics
- Searching by keyword
- Filtering by topic
- Finding high-value stories

---

**Need Help?** Check the [README.md](README.md) for comprehensive documentation.
