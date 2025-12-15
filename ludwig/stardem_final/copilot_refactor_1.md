# Copilot Refactor Session 1: Migrating from Anthropic to OpenAI

**Date:** December 14, 2025  
**File Modified:** `ludwig/stardem_final/markdown_creator/build_beat_book.py`

## Summary

Refactored the beat book builder script to replace Anthropic/Claude models with OpenAI's new GPT-5.2 model using the Responses API, while keeping Groq for initial note-taking.

## Original Architecture

The script used a two-stage process:
1. **Stage 1 (Groq):** GPT-OSS-120B via `llm` CLI tool reads stories and takes notes
2. **Stage 2 (Claude):** Claude Sonnet 4.5 refines notes into a polished beat book

Three functions used Anthropic's API:
- `search_caroline_county_info()` - Web search for background statistics
- `refine_with_claude()` - Beat book refinement after each batch
- `review_with_claude()` - Checkpoint reviews every 10 batches (with web search)

## New Architecture

- **Stage 1 (Groq):** Unchanged - still uses `groq/openai/gpt-oss-120b`
- **Stage 2 (OpenAI):** Now uses GPT-5.2 via the new Responses API

## Key Changes

### 1. Import Changes
```python
# Before
import anthropic
from anthropic import Anthropic

# After
from openai import OpenAI
```

### 2. API Migration

The OpenAI Responses API has a different structure than Anthropic's Messages API:

| Anthropic | OpenAI Responses API |
|-----------|---------------------|
| `client.messages.create()` | `client.responses.create()` |
| `messages=[{"role": "user", "content": ...}]` | `input=...` |
| System message in `messages` array | `instructions=...` parameter |
| `max_tokens` | `max_output_tokens` |
| `tools=[{"type": "web_search_20250305", ...}]` | `tools=[{"type": "web_search"}]` |
| `response.content[].text` | `response.output[].content[].text` (where type == "output_text") |

### 3. Function Renames
- `refine_with_claude()` → `refine_with_openai()`
- `review_with_claude()` → `review_with_openai()`

### 4. Response Parsing

```python
# Before (Anthropic)
for block in response.content:
    if block.type == "text":
        result_text += block.text

# After (OpenAI Responses API)
for output_item in response.output:
    if output_item.type == "message":
        for content_block in output_item.content:
            if content_block.type == "output_text":
                result_text += content_block.text
```

### 5. Web Search Tool Output

```python
# Before (Anthropic)
elif block.type == "server_tool_use":
    if hasattr(block, 'input') and isinstance(block.input, dict):
        query = block.input.get('query', 'N/A')

# After (OpenAI)
elif output_item.type == "web_search_call":
    if hasattr(output_item, 'action') and hasattr(output_item.action, 'query'):
        query = output_item.action.query
```

## Model Used

- **Model ID:** `gpt-5.2-2025-12-11`
- **API Endpoint:** `https://api.openai.com/v1/responses`

## Environment Variables

The script now uses `OPENAI_API_KEY` instead of `ANTHROPIC_API_KEY` for the refinement stage. Both should be defined in the `.env` file if using both Groq (which may have its own key) and OpenAI.

## Files Unchanged

- Groq integration via `llm` CLI tool remains unchanged
- Prompt templates (`BEAT_BOOK_PROMPT`, `REFINE_PROMPT`, `REVIEW_PROMPT`) work with both APIs
- State management and batch processing logic unchanged

## OpenAI Responses API Reference

Key features of the new API used in this refactor:
- `input`: Text input to the model (replaces `messages` array for simple cases)
- `instructions`: System/developer message 
- `tools`: Array of tools including `{"type": "web_search"}` for built-in web search
- `store`: Set to `false` to not store responses for privacy
- `max_output_tokens`: Upper bound on generated tokens

Response structure:
- `response.output[]`: Array of output items
- `response.output[].type`: Can be "message", "web_search_call", etc.
- `response.output[].content[]`: For messages, array of content blocks
- `response.output[].content[].type`: "output_text" for text content
- `response.usage.input_tokens` / `response.usage.output_tokens`: Token counts
