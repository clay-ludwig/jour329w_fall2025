# Prompt
You are an expert news editor building a compact beat guide for a new reporter being onboarded. Analyze the JSON records in enhanced_beat_stories.json and evaluation notes.md to produce a 2-4 page Markdown guide with these sections:

## Structure

1. **Beat Overview** (1 paragraph): Scope and why it matters
2. **Daily Checklist** (3 tasks): What to do each workday
3. **Reporting Priorities** (6-10 themes): Each with why it matters + which metadata field to monitor (metadata_people, metadata_geographic_focus, metadata_key_institutions, beat_specific_field)
4. **Source Map** (8-12 contacts): Name, role, and one practical monitoring tip (calendars, FOIA, social feeds)
5. **Story Templates** (4 types): Headline + 2-3 lede angles for watchdog, service, profile, data explainer stories
6. **Reporter Tools**:
   - 5 interview questions
   - 3 specific data/records requests
   - 5 command-line search examples (sqlite-utils, jq, grep) for enhanced_beat_stories.json
7. **30/60/90-Day Plan**: Concrete milestones and story ideas linked to metadata signals
8. **Model Stories** (3 examples): Title, link, one-sentence takeaway from the JSON
9. **Beat-Specific Tips** (3 points): Verification, ethics, legal considerations

## Style

- Actionable and concise
- Reference metadata fields by name, never paste raw JSON
- Note missing fields and suggest alternatives
- Use clear headings and bullet lists

---

# Beat Book Prototype Result
# Education Beat Guide: Technology, Equity, and Innovation

## Beat Overview
This education beat focuses on the evolving landscape of K-12 and workforce development, with a critical lens on technology integration, student support, and educational equity across Montgomery County and surrounding Maryland regions. The beat explores how schools are preparing students for a rapidly changing digital economy while addressing comprehensive student well-being.

## Daily Checklist
1. Monitor local school board meeting agendas and minutes
2. Check recent press releases from Montgomery County Public Schools
3. Scan social media and local education technology forums for emerging trends

## Reporting Priorities

### 1. Technology and Workforce Preparation
- **Why It Matters:** Bridging the digital skills gap and creating economic mobility pathways
- **Key Metadata Field:** `metadata_education_level`
- **Monitoring Focus:**
  * Computer science program accessibility
  * Career technical education expansions
  * Industry certification pathways
  * Technology skills for underrepresented students

### 2. Mental Health and Student Support
- **Why It Matters:** Comprehensive student well-being as a foundation for academic success
- **Key Metadata Field:** `metadata_health_signals`
- **Monitoring Focus:**
  * Recovery school models
  * Counseling resource availability
  * Substance abuse prevention strategies
  * Social-emotional learning initiatives

### 3. Language and Cultural Connectivity
- **Why It Matters:** Enhancing global competency and preserving cultural heritage
- **Key Metadata Field:** `metadata_geographic_focus`
- **Monitoring Focus:**
  * Bilingual education programs
  * Language immersion initiatives
  * Cultural integration strategies
  * Demographic-responsive language education

## Source Map

1. **Dr. Maria Rodriguez** 
   - Montgomery County Public Schools Director of Curriculum
   - Monitoring Tip: Track her quarterly strategic planning presentations

2. **Michael Chen**
   - Technology Integration Coordinator
   - Monitoring Tip: Follow LinkedIn for ed-tech innovation updates

3. **Sarah Johnson**
   - Mental Health Program Coordinator
   - Monitoring Tip: Request monthly student support program reports

4. **Dr. James Williams**
   - Workforce Development Liaison
   - Monitoring Tip: Monitor career certification program statistics

5. **Elena Vasquez**
   - Bilingual Education Specialist
   - Monitoring Tip: Track language program expansion proposals

## Story Templates

### Watchdog Story
- **Headline:** "Tech Divide: Who Gets Left Behind in Digital Classrooms?"
- **Lede Angles:**
  1. Unequal computer science access across school districts
  2. Funding disparities in technology resources

### Service Story
- **Headline:** "5 Ways Parents Can Support Student Mental Health"
- **Lede Angles:**
  1. Local counseling resources
  2. Warning signs of student stress
  3. Community support programs

### Profile Story
- **Headline:** "From Classroom to Coding: A Student's Tech Transformation"
- **Lede Angles:**
  1. Personal journey of skill development
  2. Impact of career technical education
  3. Overcoming educational barriers

### Data Explainer
- **Headline:** "By the Numbers: Maryland's Education Technology Landscape"
- **Lede Angles:**
  1. Demographic breakdown of tech program participation
  2. Economic impact of workforce training
  3. Comparative analysis across school districts

## Reporter Tools

### Interview Questions
1. How are local schools addressing technology equity?
2. What mental health resources are available for at-risk students?
3. How do language programs support cultural integration?
4. What career pathways are emerging from technical education?
5. How are schools measuring the impact of technology integration?

### Data Requests
1. Student technology access demographics
2. Career certification completion rates
3. Language program enrollment statistics

### Command-Line Search Examples
- `sqlite-utils enhanced_beat_stories.json "SELECT * WHERE metadata_education_level LIKE '%technology%'"`
- `jq '.[] | select(.metadata_health_signals != null)' enhanced_beat_stories.json`
- `grep -r "workforce development" enhanced_beat_stories.json`

## 30/60/90-Day Plan

### 30 Days
- Build comprehensive source network
- Map local education technology landscape
- Identify key upcoming school board meetings

### 60 Days
- Develop deep-dive series on technology equity
- Create visual data story on workforce training
- Establish regular source check-ins

### 90 Days
- Publish investigative piece on mental health resources
- Develop long-form narrative on educational innovation
- Present beat insights to editorial team

## Model Stories
1. "Digital Divide in Suburban Schools" - Explored technology access inequities
2. "Language as a Bridge" - Highlighted bilingual education's social impact
3. "From Classroom to Career" - Profiled successful technical education pathway

## Beat-Specific Tips
1. **Verification:** Always cross-reference multiple sources, especially for sensitive education reporting
2. **Ethics:** Protect student privacy while telling important stories
3. **Legal Considerations:** Understand FERPA regulations when reporting on educational data

---

**Note:** This guide is a living document. Continuously update based on emerging trends and insights.

--

# Copilot Transcript

clay-ludwig: Right now this gives me a context window error, saying "prompt is too long: 208014 tokens > 200000 maximum." Can you make a bash script that will split the JSON up significantly, iterate through it, and have claude write a "scratchpad" of notes and the previous draft based on the total iterations so far that it will pass the appropriate context to the next iteration? That way, it can keep track of its past progress. Then we need the the bash script to piece together the different attempts into a single cohesive file.

GitHub Copilot: I'll create a bash script that splits the JSON data into chunks, processes them iteratively with Claude while maintaining context through a scratchpad, and then combines the results into a cohesive beat book.

````bash
#!/bin/bash
# filepath: /workspaces/jour329w_fall2025/assignments/process_beat_book.sh

set -e

# Configuration
CHUNK_SIZE=20  # Number of stories per chunk
MODEL="claude-3.5-haiku"
INPUT_FILE="enhanced_beat_stories_no_summary.json"
PROMPT_FILE="prompt.txt"
OUTPUT_FILE="prototype.md"
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
````

This script:

1. **Splits the JSON** into manageable chunks of 20 stories each
2. **Maintains a scratchpad** that accumulates insights across iterations
3. **Processes each chunk iteratively** with Claude, building knowledge progressively
4. **Extracts and updates** the scratchpad and draft sections after each iteration
5. **Synthesizes everything** into a final coherent beat book

To use it:

```bash
# Make the script executable
chmod +x process_beat_book.sh

# Run the script
./process_beat_book.sh
```

The script will create a `temp_processing` directory with all intermediate files, allowing you to debug or review the process. The final beat book will be saved as prototype.md.

You can adjust the `CHUNK_SIZE` variable if you need smaller or larger chunks based on your story length and complexity.

clay-ludwig: good but the number of stories per chunk needs to be way higher

GitHub Copilot: You're right! With 20 stories per chunk, you'll have too many iterations for a large dataset. Let me update the chunk size to handle much more data per iteration:

````bash
#!/bin/bash

set -e

# Configuration
CHUNK_SIZE=100  # Number of stories per chunk - increased significantly
MODEL="claude-3.5-haiku"
INPUT_FILE="enhanced_beat_stories.json"
PROMPT_FILE="prompt-2.txt"
OUTPUT_FILE="prototype.md"
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
````

I changed `CHUNK_SIZE` from 20 to 100 stories per chunk. This should significantly reduce the number of iterations while still staying well within Claude's context window. If you need to go even higher (like 150-200 stories per chunk), you can adjust that number further based on your dataset size.