# Copilot Session Summary: Local Embedding & Similarity Matching System

## Overview

This session focused on building a local system for generating text embeddings using Ollama's `embeddinggemma` model and finding semantically similar source articles for a "beat book" viewer application.

---

## What We Built

### 1. Embedding Generation Scripts

#### `generate_embeddings.py` (Article-Level)
- Reads `source_stories.json` containing 629 news articles
- Generates embeddings for each story's full `content` field
- Outputs `source_stories_embeddings.json` with embeddings added to each story
- Uses Python's built-in `urllib` (no external dependencies)

#### `generate_embeddings_granular.py` (Sentence-Level)
- Splits each article's content into individual sentences using regex
- Handles abbreviations (Mr., Dr., U.S., Ph.D., etc.) to avoid false splits
- Generates embeddings for each sentence (14,194 total sentences from 629 articles)
- Outputs `source_stories_embeddings_granular.json` with structure:
```json
{
  "article_id": "...",
  "title": "...",
  "sentences": [
    {"text": "...", "embedding": [...], "index": 0}
  ]
}
```

---

### 2. Markdown to Beat Book Converters

#### `md_to_beatbook.py` (Article-Level Matching)
- Converts markdown files to JSON format
- Generates embeddings for each sentence in the markdown
- Finds the most similar source article using cosine similarity
- Outputs JSON with `source` (article_id) and `similarity` score

#### `md_to_beatbook_granular.py` (Sentence-Level Matching with Composite Scoring)
- Matches each sentence against individual source sentences
- Uses **composite scoring**: 70% sentence similarity + 30% article similarity
- Loads both granular and article-level embeddings
- Outputs include:
  - `source` - article ID
  - `source_sentence` - the matching sentence text
  - `similarity` - composite score
  - `sentence_similarity` - sentence-to-sentence score
  - `article_similarity` - sentence-to-article score
- Customizable weights via command-line: `--sentence-weight` and `--article-weight`

**Usage:**
```bash
python3 md_to_beatbook_granular.py beat_book.md
# Output: beat_book_granular.json
```

---

### 3. Viewer Application (`viewer.html`)

A web-based viewer for the beat book JSON files with:

#### Main Menu Header
- Purple gradient header bar with title "📖 Beat Book Viewer"
- **File selector dropdown** that auto-discovers available JSON files
- Loading indicator

#### Source Highlighting
- Sentences with high similarity scores (≥0.65) are highlighted in purple gradient
- **Hover effect**: Background fills with gradient, text turns white, slight scale-up
- Makes it easy to distinguish adjacent links

#### Hover Preview Tooltip
- Shows article title, author, date
- Displays content preview (first 400 characters)

#### Split-View Article Panel
- Clicking a highlighted source opens the full article in a side panel
- Clean article metadata display

#### Similarity Threshold
- Configurable in code: `const SIMILARITY_THRESHOLD = 0.65;`
- Only sources meeting the threshold are linked

---

## How to Run

### Step 1: Generate Embeddings

**Article-level (for composite scoring):**
```bash
python3 generate_embeddings.py
```

**Sentence-level (required for granular matching):**
```bash
python3 generate_embeddings_granular.py
```

### Step 2: Convert Markdown to Beat Book

```bash
python3 md_to_beatbook_granular.py your_file.md
```

### Step 3: View in Browser

```bash
python3 -m http.server 8000
```
Then open: http://localhost:8000/viewer.html

---

## Key Technical Details

### Ollama API
- Endpoint: `http://localhost:11434/api/embed`
- Model: `embeddinggemma:latest`
- Returns embeddings in `result["embeddings"][0]`

### Cosine Similarity
```python
def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (magnitude1 * magnitude2)
```

### Composite Scoring Formula
```
composite = (0.7 × sentence_similarity) + (0.3 × article_similarity)
```

---

## Files Created/Modified

| File | Purpose |
|------|---------|
| `generate_embeddings.py` | Generate article-level embeddings |
| `generate_embeddings_granular.py` | Generate sentence-level embeddings |
| `md_to_beatbook.py` | Convert MD with article matching |
| `md_to_beatbook_granular.py` | Convert MD with sentence matching + composite scoring |
| `viewer.html` | Web viewer with menu, hover effects, and file selector |
| `source_stories_embeddings.json` | Article embeddings (629 articles) |
| `source_stories_embeddings_granular.json` | Sentence embeddings (14,194 sentences) |

---

## Session Statistics

- **Articles processed**: 629
- **Sentences embedded**: 14,194
- **Average composite similarity** (≥0.5 matches): ~0.59
- **Average sentence similarity**: ~0.64
- **Average article similarity**: ~0.47
