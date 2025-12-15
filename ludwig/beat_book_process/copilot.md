# Copilot Session Summary - December 14, 2025

## Overview

This session focused on refining the `markdown_creator/build_beat_book.py` script, which generates an education beat book for Caroline County, Maryland using a two-stage AI pipeline:

1. **Groq GPT-OSS-120B** - Takes factual notes from batches of source stories
2. **Claude Sonnet 4.5** - Refines notes into a cohesive, synthesized beat book

---

## Changes Made

### 1. Model Configuration

- **Changed Claude model from Haiku to Sonnet 4.5** (`claude-sonnet-4-5-20250929`) for all refinement tasks
- Sonnet is used for both regular batch refinement and checkpoint reviews (every 10 batches)
- Groq model remains `groq/openai/gpt-oss-120b` for initial note-taking

### 2. Prompt Simplification & Roles

Established clear separation of concerns:
- **Groq (GPT-OSS-120B)**: Acts as a "reporter" taking detailed factual notes
- **Claude (Sonnet 4.5)**: Acts as an "editor" synthesizing notes into a cohesive beat book

### 3. Geographic Clarification

Added explicit clarification in all prompts that this covers **Caroline County, MARYLAND** (on the Eastern Shore), NOT the similarly-named Caroline County in Virginia.

### 4. Batch Splitting for Token Limits

Implemented automatic batch splitting when Groq's token limit is exceeded:
- Batches that exceed the token limit are split in half recursively
- Each sub-batch saves to its own file with a suffix (e.g., `notes_a.md`, `notes_ba.md`)
- Sub-batches are processed independently, then combined for Claude refinement

### 5. Multiple Reporters Roleplay

When batches split into multiple sub-batches, Claude receives a roleplay scenario:
- Single batch: "A reporter has been taking notes..."
- Multiple sub-batches: "3 reporters have each taken notes from different source stories..."
- Notes are wrapped in XML tags: `<reporter_1_notes>`, `<reporter_2_notes>`, etc.

### 6. Per-Batch Output Directories

Changed output structure to organize notes by batch:
```
output/
├── batch_1/
│   ├── notes.md         (if no split)
│   ├── notes_a.md       (first split)
│   └── notes_b.md       (second split)
├── batch_2/
│   └── notes.md
├── beat_book.md
└── beat_book_state.json
```

### 7. Daily Rate Limit Handling

Distinguished between two types of Groq errors:
- **Per-request token limit** (`TOKEN_LIMIT_EXCEEDED`): Splits batch and retries
- **Daily rate limit** (`DAILY_LIMIT_EXCEEDED`): Saves state and aborts cleanly with message to run again tomorrow

### 8. Removed "NO UPDATE NEEDED" Logic

Previously, both Groq and Claude could return "NO UPDATE NEEDED" to skip processing. This was removed:
- Groq now always produces notes (even if just "No Caroline County education content")
- Claude now always integrates notes into the beat book
- This ensures all content is processed and nothing is silently skipped

### 9. Groq Prompt: More Detailed Notes

Updated Groq's note-taking prompt to capture more detail:
- Budget figures, enrollment numbers, dates
- Programs, initiatives, and policies
- Quotes from officials or stakeholders
- Explicit instruction to be thorough

### 10. Claude Prompt: Synthesis Over Cataloging

Completely rewrote Claude's refinement instructions to prevent story-by-story cataloging:

**Key instructions:**
1. **Synthesize, don't catalog** - Merge information about the same person/school/issue into one place
2. **Focus on the big picture** - Major issues, key players, patterns - avoid one-off events
3. **Organize by topic, not by source** - Structure around subjects (budget, schools, personnel)
4. **No citations** - No article mentions, no "according to" attributions

### 11. Preamble Stripping

Added code to strip any "thinking out loud" dialogue from Claude's responses before saving:
- Looks for the first markdown heading (`#`)
- Strips everything before it
- Ensures clean output without Claude's reasoning process

### 12. Word Count Target

Changed from aggressive cutting ("Under 7,000 words, cut aggressively") to more permissive ("5,000-10,000 words") to preserve detail.

---

## File Structure

```
ludwig/stardem_final/
├── markdown_creator/
│   ├── build_beat_book.py      # Main script (heavily modified)
│   ├── source_stories.json     # Input data
│   └── output/
│       ├── batch_N/
│       │   └── notes*.md       # Groq notes per batch
│       ├── beat_book.md        # Final refined beat book
│       └── beat_book_state.json # Progress state
└── copilot.md                  # This file
```

---

## Usage

```bash
cd ludwig/stardem_final/markdown_creator
python build_beat_book.py --batch-size 10
```

Options:
- `--batch-size N` - Number of stories per batch (default: 20)
- `--reset` - Start over from the beginning
- `--delay N` - Seconds between batches (default: 2)

The script saves state after each batch, so it can be interrupted and resumed.

---

## Models Used

| Stage | Model | Purpose |
|-------|-------|---------|
| Note-taking | `groq/openai/gpt-oss-120b` | Extract facts from source stories |
| Refinement | `claude-sonnet-4-5-20250929` | Synthesize notes into beat book |
| Checkpoint review | `claude-sonnet-4-5-20250929` | Web search to fact-check (every 10 batches) |

---

## Known Limitations

1. **Groq daily token limits** - Free tier has daily limits; script will abort cleanly when hit
2. **Large stories** - Single stories exceeding Groq's context window will be skipped
3. **Claude preamble** - Despite explicit instructions, Claude sometimes adds thinking/commentary that must be stripped

---

## Next Steps

Potential improvements for future sessions:
- Add retry logic with exponential backoff for transient API errors
- Consider caching Groq notes to avoid re-processing on Claude failures
- Add option to skip checkpoint reviews for faster iteration
- Consider parallel processing of independent batches
