#!/bin/bash
# filepath: /workspaces/jour329w_fall2025/assignments/process_beat_book.sh

set -e

# Configuration
CHUNK_SIZE=100  # Number of stories per chunk
MODEL="claude-3.5-haiku"
INPUT_FILE="enhanced_beat_stories.json"
PROMPT_FILE="prompt-2.txt"
OUTPUT_FILE="revised.md"
TEMP_DIR="temp_processing"

# Create temporary directory
mkdir -p "$TEMP_DIR"

echo "Starting beat book generation process..."

# Check if required files exist
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: $INPUT_FILE not found"
    exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: $PROMPT_FILE not found"
    exit 1
fi

# Split JSON into chunks
echo "Splitting JSON into chunks of $CHUNK_SIZE stories..."
uv run python3 - << EOF
import json
import math

# Load the full JSON
with open('$INPUT_FILE', 'r') as f:
    stories = json.load(f)

total_stories = len(stories)
chunk_size = $CHUNK_SIZE
num_chunks = math.ceil(total_stories / chunk_size)

print(f"Total stories: {total_stories}")
print(f"Number of chunks: {num_chunks}")

# Split into chunks
for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx = min((i + 1) * chunk_size, total_stories)
    chunk = stories[start_idx:end_idx]
    
    with open(f'$TEMP_DIR/chunk_{i:03d}.json', 'w') as f:
        json.dump(chunk, f, indent=2)
    
    print(f"Created chunk {i:03d}: stories {start_idx}-{end_idx-1}")
EOF

# Initialize scratchpad
cat > "$TEMP_DIR/scratchpad.md" << 'EOF'
# Beat Book Generation Progress

## Key Insights Gathered So Far:
- [Initial processing - no insights yet]

## Emerging Patterns:
- [To be identified during processing]

## Important People/Organizations:
- [To be catalogued during processing]

## Geographic Coverage:
- [To be mapped during processing]

## Current Draft Sections Completed:
- [None yet]

## Next Steps:
- Begin processing first chunk of stories
EOF

# Process each chunk
echo "Processing chunks with Claude..."
NUM_CHUNKS=$(ls "$TEMP_DIR"/chunk_*.json | wc -l)

for chunk_file in "$TEMP_DIR"/chunk_*.json; do
    chunk_num=$(basename "$chunk_file" .json | sed 's/chunk_//')
    echo "Processing chunk $chunk_num of $((NUM_CHUNKS-1))..."
    
    # Create iteration-specific prompt
    cat > "$TEMP_DIR/iteration_prompt.txt" << EOF
You are helping create a comprehensive beat book for journalists. This is an iterative process where you'll analyze chunks of stories and build upon previous progress.

ORIGINAL TASK:
$(cat "$PROMPT_FILE")

CURRENT PROGRESS (from previous iterations):
$(cat "$TEMP_DIR/scratchpad.md")

CURRENT CHUNK TO ANALYZE:
This is chunk $chunk_num of $((NUM_CHUNKS-1)) total chunks.

Please:
1. Analyze the stories in this chunk for patterns, key people, institutions, and geographic coverage
2. Update the scratchpad with new insights and patterns you discover
3. Add to or refine any draft sections of the beat book based on this new data
4. If this is the final chunk, create a complete, polished beat book

Respond with:
1. UPDATED_SCRATCHPAD: [Updated scratchpad content]
2. DRAFT_SECTION: [Any new or updated beat book content]

Current chunk data:
EOF

    # Process this chunk
    cat "$TEMP_DIR/iteration_prompt.txt" "$chunk_file" | uv run llm -m "$MODEL" > "$TEMP_DIR/response_$chunk_num.md"
    
    # Extract and update scratchpad
    if grep -q "UPDATED_SCRATCHPAD:" "$TEMP_DIR/response_$chunk_num.md"; then
        sed -n '/UPDATED_SCRATCHPAD:/,/DRAFT_SECTION:/p' "$TEMP_DIR/response_$chunk_num.md" | \
        sed '1d;$d' > "$TEMP_DIR/scratchpad.md"
    fi
    
    # Extract draft section
    if grep -q "DRAFT_SECTION:" "$TEMP_DIR/response_$chunk_num.md"; then
        sed -n '/DRAFT_SECTION:/,$p' "$TEMP_DIR/response_$chunk_num.md" | \
        sed '1d' > "$TEMP_DIR/draft_$chunk_num.md"
    fi
    
    echo "Completed chunk $chunk_num"
    sleep 2  # Rate limiting
done

# Final synthesis
echo "Creating final synthesis..."
cat > "$TEMP_DIR/final_prompt.txt" << EOF
You are creating the final version of a beat book for journalists. You have processed all the story chunks and gathered insights.

ORIGINAL TASK:
$(cat "$PROMPT_FILE")

FINAL SCRATCHPAD WITH ALL INSIGHTS:
$(cat "$TEMP_DIR/scratchpad.md")

DRAFT SECTIONS FROM ALL ITERATIONS:
EOF

# Append all draft sections
for draft_file in "$TEMP_DIR"/draft_*.md; do
    if [[ -f "$draft_file" ]]; then
        echo "--- Section from $(basename "$draft_file") ---" >> "$TEMP_DIR/final_prompt.txt"
        cat "$draft_file" >> "$TEMP_DIR/final_prompt.txt"
        echo "" >> "$TEMP_DIR/final_prompt.txt"
    fi
done

cat >> "$TEMP_DIR/final_prompt.txt" << EOF

Please create a final, comprehensive, well-organized beat book that synthesizes all the insights and information gathered. The beat book should be practical, informative, and valuable for a journalist covering this beat.
EOF

# Generate final beat book
cat "$TEMP_DIR/final_prompt.txt" | uv run llm -m "$MODEL" > "$OUTPUT_FILE"

echo "Beat book generation complete!"
echo "Final output saved to: $OUTPUT_FILE"
echo "Temporary files saved in: $TEMP_DIR"
echo ""
echo "Summary:"
echo "- Processed $NUM_CHUNKS chunks"
echo "- Generated iterative drafts and scratchpad notes"
echo "- Created final synthesized beat book"

# Optional: Clean up temp files (uncomment if desired)
# echo "Cleaning up temporary files..."
# rm -rf "$TEMP_DIR"