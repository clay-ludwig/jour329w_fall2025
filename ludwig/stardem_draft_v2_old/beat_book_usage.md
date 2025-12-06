# Beat Book Builder - Usage Guide

## Overview
The `build_beat_book.py` script iteratively builds a comprehensive education beat book by processing stories in random batches and updating the guide progressively using Groq GPT-OSS-120B.

## Basic Usage

### Standard Run
```bash
python build_beat_book.py
```

### Custom Batch Size
```bash
python build_beat_book.py --batch-size 15
```

### Custom Delay Between Batches
```bash
python build_beat_book.py --delay 3
```

### Resume After Interruption
The script automatically resumes from where it left off:
```bash
python build_beat_book.py
```

### Start Over From Scratch
```bash
python build_beat_book.py --reset
```

### Custom Input/Output Files
```bash
python build_beat_book.py --input my_stories.json --output my_beat_book.txt --state my_state.json
```

## Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--input` | `source_stories.json` | Input JSON file with stories |
| `--state` | `beat_book_state.json` | State file to track progress |
| `--output` | `education_beat_book.txt` | Output file for beat book |
| `--batch-size` | `20` | Number of stories per batch |
| `--delay` | `2` | Seconds to wait between batches |
| `--reset` | `False` | Reset state and start from beginning |

## Output Files

- **`education_beat_book.txt`** - The final beat book guide
- **`beat_book_state.json`** - Progress tracking (processed stories, current state, batch number)

## Features

- ✅ Processes stories in random batches (no duplicates)
- ✅ Saves state after each batch (fully resume-able)
- ✅ Retry logic with exponential backoff for errors
- ✅ Model can skip updates if stories don't add value
- ✅ Comprehensive error handling
- ✅ Progress tracking throughout

## Examples

Process all stories with default settings:
```bash
python build_beat_book.py
```

Process with smaller batches and longer delays:
```bash
python build_beat_book.py --batch-size 10 --delay 5
```

Start fresh (delete previous progress):
```bash
python build_beat_book.py --reset
```
