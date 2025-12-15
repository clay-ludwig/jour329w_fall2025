# Beat Book Viewer Project Summary

## Overview

Built a markdown viewer web application with source attribution features. The system converts markdown files into a custom JSON format ("beat book format") where each sentence can be linked to source articles, then displays this content with interactive features.

## Files Created

### 1. `viewer.html`
A responsive HTML/CSS/JS markdown viewer with the following features:

- **Inter Google Font** for clean, minimal typography
- **Markdown rendering** using the marked.js library
- **Beat book JSON format support** - reads JSON files where each line/sentence is a separate entry
- **Source attribution highlighting** - sentences with source IDs are displayed with a purple/blue gradient and dotted underline
- **Hover preview tooltips** - hovering over sourced content shows a preview card with:
  - Article title
  - Author and date
  - Content preview (first ~400 characters)
  - Smooth fade-in animation
  - Smart positioning to stay within viewport
- **Split-screen article viewer** - clicking a sourced sentence opens a side panel showing the full source article with:
  - Animated 50/50 split layout
  - Title, author, date, and full content
  - Close button to return to full-width view
- **Fully responsive** - adapts to mobile with full-screen article panel
- **Container width optimization** - content max-width is set to not shift when the article panel opens

### 2. `md_to_beatbook.py`
A Python script that converts markdown files to beat book JSON format:

- **Sentence splitting** using regex to break paragraphs into individual sentences
- **Preserves markdown structure** - keeps headings, list items, code blocks, and empty lines intact
- **Source ID assignment** - randomly assigns article IDs from `source_stories.json` to ~10% of sentences
- **Handles edge cases** - common abbreviations (Mr., Mrs., Dr., etc.), code blocks, etc.

**Usage:**
```bash
python3 md_to_beatbook.py beat_book.md
python3 md_to_beatbook.py beat_book.md -o custom_output.json
```

## Beat Book JSON Format

```json
[
  {
    "content": "# Heading",
    "source": ""
  },
  {
    "content": "This is a sentence with a source.",
    "source": "search-hits__hit--8987"
  },
  {
    "content": "This sentence has no source.",
    "source": ""
  }
]
```

Each entry contains:
- `content`: The text content (a line or sentence from the markdown)
- `source`: An article ID string that correlates to entries in `source_stories.json`, or empty string if no source

## Data Flow

1. **Markdown file** (`beat_book.md`) is converted using `md_to_beatbook.py`
2. **Beat book JSON** (`beat_book.json`) is generated with sentences and source IDs
3. **Viewer** loads both `beat_book.json` and `source_stories.json`
4. **Sourced content** is highlighted and made interactive
5. **User interaction** via hover (preview) or click (full article panel)

## Running Locally

Start a local HTTP server in the `stardem_different` directory:

```bash
cd ludwig/stardem_different
python3 -m http.server 8000
```

Then open `viewer.html` in the browser via the forwarded port.

## Configuration

In `viewer.html`, you can change these variables at the top of the script:
- `beatbookFile` - path to the beat book JSON file (default: `'beat_book.json'`)
- `storiesFile` - path to the source stories JSON file (default: `'source_stories.json'`)
