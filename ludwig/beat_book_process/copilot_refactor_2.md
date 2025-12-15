# Build Beat Book Refactor - December 14, 2025

## Summary

Refactored `build_beat_book.py` to use OpenAI's `apply_patch` tool for more efficient document updates, and revised writing style guidance to produce more natural, journalistic prose.

## Changes Made

### 1. Switched to `apply_patch` Tool

**Problem**: The script was asking OpenAI to return the entire beat book text on every refinement pass. For a 5,000-10,000 word document, this was inefficient and expensive.

**Solution**: Implemented OpenAI's `apply_patch` tool from the Agents API. The model now returns structured diffs instead of full text, and we apply them locally using `agents.apply_diff`.

**Files changed**:
- Added `from agents import apply_diff` import
- Updated `REFINE_PROMPT` and `REVIEW_PROMPT` to instruct model to use `apply_patch` tool
- Modified `refine_with_openai()` to:
  - Add `tools=[{"type": "apply_patch"}]` to API call
  - Parse `apply_patch_call` responses
  - Apply patches using `apply_diff()`
  - Fall back to full text if model doesn't use patches
- Modified `review_with_openai()` with same pattern (also keeps `web_search` tool)

**Dependencies added**:
- `openai-agents>=0.6.3` (added to pyproject.toml)

### 2. Revised Writing Style Guidance

**Problem**: The "NYT/WSJ style" instruction was producing stiff, formal prose.

**Solution**: Rewrote style guidance to emphasize natural, direct writing.

**New style priorities**:
- **Short paragraphs**: 2-4 sentences max, one idea per paragraph, white space helps readers
- **Natural flow over formality**: "Write like you're explaining something to a smart colleague, not drafting a legal document"
- **Precision without stiffness**: Concrete details without mechanical cadence
- **No filler**: Cut throat-clearing phrases ("it should be noted that," "it is important to mention")
- **Active voice, strong verbs**
- **Avoid**: Buzzwords, jargon, clichés, empty intensifiers

**Updated system instructions** in API calls to reinforce this style.

## Technical Details

### apply_patch Response Handling

```python
for output_item in response.output:
    if output_item.type == "apply_patch_call":
        op = output_item.operation
        if op.path == "beat_book.md":
            if op.type == "update_file":
                current_content = apply_diff(current_content, op.diff)
            elif op.type == "create_file":
                current_content = apply_diff("", op.diff, create=True)
```

### Fallback Behavior

If the model returns full text instead of patches (which can happen), the script detects this and uses the text directly:

```python
if not patch_applied:
    # Check for full text starting with markdown heading
    if result_text and result_text.startswith("#"):
        return result_text
```

## Running the Script

No changes to CLI usage:

```bash
python build_beat_book.py --input source_stories.json --batch-size 10
```

Or with uv:

```bash
uv run python build_beat_book.py --input source_stories.json --batch-size 10
```
