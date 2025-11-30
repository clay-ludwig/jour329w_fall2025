#!/usr/bin/env python3
"""
Iteratively build a beat book for education reporting by processing stories in random batches.
Uses a two-stage process:
1. Groq GPT-OSS-120B reads stories and updates education_beat_book.md
2. Claude Sonnet 4.5 refines the beat book and outputs education_beat_book_refined.md
"""
import json
import subprocess
import argparse
import time
import random
import os
import re
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


BEAT_BOOK_PROMPT = """You are helping create a comprehensive "beat book" - a narrative guide for a new reporter covering the education beat in Caroline County, Maryland for the Easton Star-Democrat.

<context>
Today is {current_date}.

You are being shown stories in batches of {batch_size} at a time from a total collection of {total_stories} education stories. This is batch {batch_num} of {total_batches}. Your job is to INTEGRATE and EXPAND the beat book based on what you learn from these new stories.

CRITICAL FOCUS: This beat book is ONLY about education in Caroline County, MD. EXCLUDE and IGNORE any information about other Maryland counties (Dorchester, Kent, Queen Anne's, Talbot, etc.) even if they appear in the source stories. Focus exclusively on Caroline County schools, districts, officials, and education issues.

CRITICAL: You are building this beat book progressively. The current beat book below already contains valuable information from {processed_count} previously analyzed stories. Your task is to ADD to and ENRICH this existing content, NOT replace it. Think of yourself as expanding a living document, weaving new threads into an existing tapestry.
</context>

<current_beat_book>
{current_beat_book}
</current_beat_book>

<new_stories>
{stories}
</new_stories>

<instructions>
Your goal is to INTEGRATE the new stories into the existing beat book by:
- Adding new people, institutions, or themes you discover IN CAROLINE COUNTY
- Expanding on themes already present with new examples and context FROM CAROLINE COUNTY
- Adding new story angle suggestions based on patterns you see in CAROLINE COUNTY coverage
- Enriching sections that could benefit from additional depth
- Connecting new information to existing threads in the narrative
- Explain what matters on this beat using examples and lessons from CAROLINE COUNTY stories
- Suggest story ideas and undercovered angles specific to CAROLINE COUNTY
- Flag unfinished stories (ongoing lawsuits, policy debates) with a caveat that they may already be resolved
- Give more weight to recent coverage - the beat book should orient toward the future
- Include specific story references and context when relevant
- Mention contact information for sources only when available in the stories
- SKIP any stories that are primarily about other counties - only extract Caroline County information
</instructions>

<critical_preservation_rules>
1. PRESERVE all existing content from the current beat book unless it's factually contradicted by new stories
2. When new stories overlap with existing themes, EXPAND those sections rather than replacing them
3. INTEGRATE new people and institutions into the existing narrative flow
4. ADD new sections only when the new stories introduce genuinely novel themes
5. MAINTAIN the narrative voice and flow established in the current beat book
6. DO NOT remove story ideas, contact information, or contextual details already present
7. Think ADDITIVE and CUMULATIVE - you are building upon prior work, not starting fresh
</critical_preservation_rules>

<update_guidelines>
If these stories don't add significant new information to the beat book, respond with "NO UPDATE NEEDED" and I'll keep the current version. If updating, you MUST return the COMPLETE beat book with both the preserved existing content AND new integrated material.
</update_guidelines>

<output_format>
Provide your response in one of two formats:
1. If no update needed: "NO UPDATE NEEDED"
2. If updating: The COMPLETE updated beat book as a narrative essay in Markdown format (no preamble, just the beat book content). This must include ALL existing content plus new additions.
</output_format>"""


CLAUDE_REFINE_PROMPT = """You are a senior editor refining a "beat book" - a narrative guide for a new reporter covering the education beat in Caroline County, Maryland for the Easton Star-Democrat. A junior staff writer has been reading source stories and building the beat book; your job is to edit and polish their work.

<meta_context>
Today is {current_date}.

OVERALL PROGRESS: You are {progress_percentage:.1f}% through the project.
- Batch {batch_num} of {total_batches} total batches
- {processed_count} of {total_stories} stories have been analyzed so far
- This means there are {remaining_stories} stories yet to be processed

THE BIG PICTURE:
You are the senior editor in a two-stage editorial process building a comprehensive beat book from {total_stories} local education stories. A junior staff writer reads source stories in batches and progressively builds a draft beat book. Your job is to refine, clarify, and improve their work with an eye toward the final product that will serve readers for years.

STAGE OF PROJECT:
{stage_guidance}

Your refinements should reflect where we are in this journey. Early on, establish the foundation and voice. In the middle, deepen and expand. Near the end, polish and ensure coherence across the entire guide.
</meta_context>

<context>
You will see:
1. Your PREVIOUS edited version (education_beat_book_refined.md)
2. The LATEST draft from the junior writer (education_beat_book.md)

Your role is to create the NEXT edited version by thoughtfully integrating updates while maintaining editorial quality and working toward a cohesive final beat book.
</context>

<previous_refined_version>
{previous_refined}
</previous_refined_version>

<latest_groq_version>
{latest_groq}
</latest_groq_version>

<word_count_guidance>
Current word count: ~{word_count} words
Target: Keep the beat book at or under 7,000 words

**If current word count is OVER 7,000 words:** You MUST be aggressive about cutting content. Remove one-off stories, tangential details, and less important developments.

**If current word count is UNDER 7,000 words:** You have room to add valuable content, but still prioritize quality over quantity.

**Word count management is a critical editorial responsibility.** A concise, focused beat book is far more valuable than an exhaustive one.
</word_count_guidance>

<instructions>
Your goal is to produce a polished, cohesive beat book that will serve a new reporter for years to come. This is NOT about choosing one version over another - it's about synthesizing the best of both while keeping the end goal in mind.

Think long-term and holistically:
- What information will still be valuable 6 months or a year from now?
- What story angles have lasting relevance vs. being too time-specific?
- How can you make the narrative more cohesive and easier to navigate?
- Where can you clarify relationships, timelines, or context?
- How do new additions fit into the overall arc and structure of the guide?

**BE AGGRESSIVE ABOUT CUTTING:**
- Any information about counties other than Caroline County (Dorchester, Kent, Queen Anne's, Talbot, etc.)
- One-off stories that don't represent broader trends or ongoing issues IN CAROLINE COUNTY
- Minor developments at individual schools that don't reflect systemic patterns
- Tangential details about people who aren't key decision-makers
- Story ideas that are too narrow or time-specific to be useful long-term
- Redundant information that's already covered elsewhere in the beat book

**Focus on what matters in Caroline County:**
- Systemic issues affecting Caroline County schools and students
- Key decision-makers in Caroline County who shape policy and direction
- Recurring themes in Caroline County education coverage
- Story angles with relevance and lasting impact for Caroline County

Compare the two versions and:
1. INTEGRATE new people, institutions, themes, or story ideas from the latest version ONLY if they meet the criteria above
2. PRESERVE strong writing, clear explanations, and valuable context from your previous refined version
3. IMPROVE clarity where either version is confusing or redundant
4. STRENGTHEN the narrative flow and connections between themes
5. AGGRESSIVELY REMOVE one-off stories, minor details, and tangential information
6. VERIFY that key details (names, dates, positions) are accurate and consistent
7. CONSIDER the overall structure - does it need reorganizing as it grows?
8. RESPECT the word count target - if over 7,000 words, you must trim significantly
</instructions>

<style_requirements>
ESSENTIAL WRITING STYLE (The senior editor will refine this, but follow these guidelines):
- Write in flowing paragraphs with a narrative throughline - this should read like an article, NOT a reference manual
- AVOID bullet points, lists, and tables except sparingly for very specific elements (like a short checklist at the very end if absolutely necessary)
- Use a direct, plain style - no flowery language, metaphors, or poetic phrases
- Avoid dramatic constructions like "This is a beat where..." or "In a time when..." - just state facts directly
- Don't use rhetorical devices or evocative imagery - write like a wire service reporter
- Keep sentences clear and factual without literary flourishes
- Weave together people, institutions, issues, and story ideas into a cohesive narrative
- Connect the dots between different stories and themes rather than cataloging them separately
- Focus on what's happening now and what might happen next, not just what happened
- Introduce key people, issues, and institutions naturally within the narrative flow
</style_requirements>

<editorial_priorities>
1. **Caroline County focus** - This beat book covers ONLY Caroline County, MD. Remove any information about other counties.
2. **Accuracy over volume** - Get names, titles, and facts right; remove speculation
3. **Clarity over cleverness** - If something is confusing in either version, clarify it
4. **Coherence over completeness** - A well-integrated narrative beats an exhaustive list
5. **Future-focus over history** - Emphasize ongoing issues and story opportunities
6. **Lasting value over timeliness** - What will still matter months from now?
7. **Narrative arc** - The beat book should tell a story about Caroline County education, not just compile facts
8. **Plain, direct style** - Avoid flowery language, metaphors, rhetorical devices, or literary flourishes. Write like a wire service reporter: clear, factual, unadorned.
</editorial_priorities>

<update_guidelines>
If the latest Groq version doesn't add meaningful new information beyond what's in your previous refined version, respond with "NO UPDATE NEEDED" and I'll keep the current refined version.

If updating, you MUST return the COMPLETE refined beat book - a synthesis of both versions that represents your best editorial judgment about what a new reporter needs to know, structured and written to serve them well for the long term.
</update_guidelines>

<output_format>
Provide your response in one of two formats:
1. If no update needed: "NO UPDATE NEEDED"
2. If updating: The COMPLETE refined beat book as a narrative essay in Markdown format (no preamble, just the beat book content)
</output_format>"""


CLAUDE_REVIEW_PROMPT = """You are a senior editor conducting a comprehensive review of an education beat book for the Easton Star-Democrat, covering education in Caroline County, Maryland. This is a RESEARCH AND EDITORIAL CLEANUP checkpoint.

<meta_context>
Today is {current_date}.

CHECKPOINT REVIEW: You are {progress_percentage:.1f}% through the overall project.
- This is batch {batch_num} (a checkpoint every 10 batches)
- {processed_count} of {total_stories} stories have been analyzed
- {remaining_stories} stories remain

This is a pause to step back, verify accuracy, assess importance, and trim excess. You have web search access to fact-check and research.
</meta_context>

<current_beat_book>
{current_refined}
</current_beat_book>

<instructions>
Your task is to review, fact-check, and refine the current beat book with research tools. This is about QUALITY CONTROL and EDITORIAL BALANCE, not adding new content.

PRIMARY GOALS:
1. **Fact-check key information** - Verify current positions, roles, ongoing issues, contact details
2. **Assess importance** - Based on your research, determine what matters most and should get more emphasis
3. **Cut irrelevant content** - Remove tangential information that doesn't serve the beat book's purpose
4. **Balance emphasis** - Ensure the most important stories, people, and issues get appropriate weight
5. **Update outdated information** - Fix anything that has changed since the stories were published

USE WEB SEARCH FOR:
- Verifying current positions/titles of key people mentioned
- Checking if ongoing issues (lawsuits, policy debates, controversies) have been resolved
- Looking up recent developments at key institutions (school boards, districts)
- Finding contact information for important sources
- Determining current relevance of story angles and themes
- Assessing which people/institutions are most important to the beat TODAY

You have a maximum of 10 web searches - use them strategically to improve accuracy and relevance.
</instructions>

<word_count_guidance>
Current word count: ~{word_count} words
Target: Keep the beat book at or under 7,000 words

**This is a critical checkpoint to manage word count.** If the beat book is approaching or exceeding 7,000 words, you MUST aggressively trim content. Be ruthless about cutting one-off stories and minor details.
</word_count_guidance>

<editorial_review_criteria>
**What to EMPHASIZE:**
- Major recurring themes and ongoing issues in CAROLINE COUNTY schools
- Key decision-makers in CAROLINE COUNTY who are still active and relevant (superintendents, board chairs, influential advocates)
- Story angles with lasting value and applicability to CAROLINE COUNTY
- Institutions in CAROLINE COUNTY that appear frequently in coverage and shape local policy
- Systemic challenges facing CAROLINE COUNTY education

**What to AGGRESSIVELY CUT:**
- **Any information about other counties** (Dorchester, Kent, Queen Anne's, Talbot, etc.)
- **One-off stories** that don't illustrate broader trends in Caroline County (e.g., a single school's new sign, a one-time event)
- **Minor school-level developments** that don't reflect systemic issues
- People who have left their positions or are no longer relevant
- Resolved issues that are no longer active
- **Tangential details** about individuals who aren't key decision-makers
- Redundant or repetitive information
- **Story ideas that are too narrow or time-bound** to help a reporter 6+ months from now
- Details that don't help a new reporter understand Caroline County's major players and themes

**Ask yourself:** Would a reporter who starts covering Caroline County 6 months from now care about this detail? Does it represent a pattern in Caroline County or just a single incident?

**What to VERIFY:**
- Job titles and current positions
- Status of ongoing legal/policy matters
- Contact information accuracy
- Recent changes at key institutions
</editorial_review_criteria>

<style_requirements>
- Maintain direct, plain style - no flowery language
- Keep narrative flow but be willing to reorganize for clarity
- Ensure factual accuracy above all else
- Note research findings where relevant (e.g., "As of [date], [person] holds [position]")
</style_requirements>

<output_format>
CRITICAL: Return ONLY the beat book content itself. Do not include:
- Any preamble or introduction about what you're doing
- Thinking aloud or process descriptions
- Explanations of your research or changes
- Phrases like "I'll conduct...", "Let me...", "Based on my research..."
- Summary of findings or methodology

Your response must START IMMEDIATELY with the beat book title/header ("# Education Beat Book") and contain NOTHING else.

The complete reviewed and refined beat book should be:
- Fact-checked and accurate
- Balanced with appropriate emphasis on important elements
- Trimmed of irrelevant or outdated information
- Updated with research findings where applicable
</output_format>"""


INITIAL_BEAT_BOOK = """# Education Beat Book - Easton Star-Democrat
## Caroline County, Maryland

This guide covers the education beat in Caroline County, Maryland, focusing on the schools, institutions, and key players that shape local education coverage."""


INITIAL_REFINED_BEAT_BOOK = """# Education Beat Book - Easton Star-Democrat
## Caroline County, Maryland

This guide covers the education beat in Caroline County, Maryland, focusing on the schools, institutions, and key players that shape local education coverage."""


def search_caroline_county_info():
    """
    Use Claude Sonnet 4.5 with web search to gather current information about
    Caroline County, Maryland - focusing on population and education statistics.
    
    This function is called once per script run to gather contextual information
    that will be appended to the beat book.
    
    Returns:
        String containing formatted statistics, or None if search failed
    """
    prompt = """Search the web for current information about Caroline County, Maryland and compile a reference report with the following statistics:

**Population Statistics:**
- Current population estimate
- Population trends (growing/declining)
- Demographics breakdown if available

**Education Statistics:**
- Number of public schools in the county
- Number of students enrolled in the school system
- Student-to-teacher ratios
- Graduation rates
- Any notable education rankings or achievements
- School district name and organizational structure
- Number of teachers/staff

CRITICAL FORMATTING REQUIREMENTS:
1. Your response will be inserted directly into a markdown document. It must be clean, polished, and ready for publication.
2. Include ONLY the two category headings and bullet-point statistics - nothing else.
3. Start immediately with "**Population Statistics:**" - no preamble, introduction, or commentary.
4. Do NOT include any meta-commentary about your search process, clarifications, or explanations.
5. Each fact must include an inline citation: "Statistic description ([source](URL))"
6. If you encounter ambiguity (e.g., multiple Caroline Counties), silently resolve it by using context clues (Maryland vs other states) and proceed with the correct data.

Your output will be directly appended to a professional document. Make it publication-ready."""

    try:
        print("\n" + "="*80)
        print("🔍 GATHERING CAROLINE COUNTY BACKGROUND INFORMATION")
        print("="*80)
        print("Searching the web for population and education statistics...")
        print("-"*80)
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 5
            }]
        )
        
        # Extract text from response
        result_text = ""
        web_searches = 0
        
        for block in response.content:
            if block.type == "text":
                result_text += block.text
            elif block.type == "server_tool_use":
                web_searches += 1
                if hasattr(block, 'input') and isinstance(block.input, dict):
                    query = block.input.get('query', 'N/A')
                    print(f"  🔎 Web search {web_searches}: {query[:80]}{'...' if len(query) > 80 else ''}")
        
        result_text = result_text.strip()
        
        print(f"\n✅ Web search complete")
        print(f"  • Searches performed: {web_searches}")
        print(f"  • Response length: {len(result_text)} characters")
        print("="*80 + "\n")
        
        return result_text
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to gather Caroline County information: {e}")
        print("="*80 + "\n")
        return None


def strip_quick_stats_section(beat_book_text):
    """
    Remove the Quick Statistics section from beat book text if it exists.
    This allows us to append a fresh version each time.
    
    Args:
        beat_book_text: The beat book text that may contain a Quick Statistics section
        
    Returns:
        Beat book text without the Quick Statistics section
    """
    # Look for the Quick Statistics section marker
    section_marker = "## Quick Statistics: Caroline County, Maryland"
    
    if section_marker in beat_book_text:
        # Find the position of the section marker
        # Look for the preceding separator (---)
        separator = "\n\n---\n\n"
        
        # Try to find the separator before the Quick Statistics section
        parts = beat_book_text.split(separator + section_marker)
        if len(parts) == 2:
            # Return just the first part (everything before the Quick Statistics)
            return parts[0].rstrip()
        
        # Fallback: just remove from the section marker onward
        parts = beat_book_text.split(section_marker)
        if len(parts) == 2:
            return parts[0].rstrip()
    
    return beat_book_text


def append_quick_stats_section(beat_book_text, caroline_county_info):
    """
    Append the Quick Statistics section to the beat book.
    First strips any existing Quick Statistics section to avoid duplicates.
    
    Args:
        beat_book_text: The beat book text
        caroline_county_info: The Caroline County statistics text from web search
        
    Returns:
        Beat book text with Quick Statistics section appended
    """
    if not caroline_county_info:
        return beat_book_text
    
    # First, remove any existing Quick Statistics section
    clean_text = strip_quick_stats_section(beat_book_text)
    
    # Now append the fresh Quick Statistics section
    quick_stats_section = f"\n\n---\n\n## Quick Statistics: Caroline County, Maryland\n\n{caroline_county_info}"
    
    return clean_text + quick_stats_section


def load_state(state_file):
    """Load the current state from file if it exists."""
    if Path(state_file).exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'beat_book': INITIAL_BEAT_BOOK,
        'refined_beat_book': INITIAL_REFINED_BEAT_BOOK,
        'processed_indices': [],
        'batch_num': 0,
        'total_batches': 0,
        'caroline_county_info': None
    }


def refine_with_claude(previous_refined, latest_groq, batch_num, total_batches, processed_count, total_stories):
    """
    Use Claude Sonnet 4.5 to refine the beat book by comparing previous refined version
    with the latest Groq version.
    
    Args:
        previous_refined: Previous refined beat book text
        latest_groq: Latest beat book from Groq
        batch_num: Current batch number
        total_batches: Total number of batches
        processed_count: Number of stories processed so far
        total_stories: Total number of stories in dataset
        
    Returns:
        Refined beat book text, or None if refinement failed
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    progress_percentage = (processed_count / total_stories) * 100
    remaining_stories = total_stories - processed_count
    
    # Calculate approximate word count of current refined beat book
    word_count = len(previous_refined.split())
    
    # Provide stage-specific guidance
    if progress_percentage < 25:
        stage_guidance = "EARLY STAGE: Focus on establishing the foundation, voice, and basic structure of the beat book. Identify the major themes and players that are emerging."
    elif progress_percentage < 50:
        stage_guidance = "BUILDING STAGE: Deepen existing themes, expand on key players and institutions, and begin to see patterns in coverage. Build out story ideas."
    elif progress_percentage < 75:
        stage_guidance = "MATURE STAGE: Refine the narrative arc, strengthen connections between themes, and ensure comprehensive coverage of the beat's major elements."
    else:
        stage_guidance = "FINAL STAGE: Polish for coherence, ensure nothing critical is missing, strengthen the overall narrative, and prepare for the final product. Think about the lasting value."
    
    prompt_text = CLAUDE_REFINE_PROMPT.format(
        current_date=current_date,
        batch_num=batch_num,
        total_batches=total_batches,
        processed_count=processed_count,
        total_stories=total_stories,
        remaining_stories=remaining_stories,
        progress_percentage=progress_percentage,
        stage_guidance=stage_guidance,
        word_count=word_count,
        previous_refined=previous_refined,
        latest_groq=latest_groq
    )
    
    try:
        print("Refining with Claude Sonnet 4.5...")
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt_text
            }]
        )
        
        # Extract text from response
        result_text = ""
        for block in response.content:
            if block.type == "text":
                result_text += block.text
        
        result_text = result_text.strip()
        
        if result_text == "NO UPDATE NEEDED" or result_text.startswith("NO UPDATE NEEDED"):
            print("Claude determined no refinement needed.")
            return previous_refined
        
        return result_text
        
    except Exception as e:
        print(f"ERROR: Unexpected error during Claude refinement: {e}")
        return None


def review_with_claude(current_refined, batch_num, total_batches, processed_count, total_stories):
    """
    Use Claude Sonnet 4.5 with web search to comprehensively review the beat book.
    This is done every 10 batches to fact-check, assess importance, and trim excess.
    
    Args:
        current_refined: Current refined beat book text
        batch_num: Current batch number
        total_batches: Total number of batches
        processed_count: Number of stories processed so far
        total_stories: Total number of stories in dataset
        
    Returns:
        Reviewed beat book text, or None if review failed
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    progress_percentage = (processed_count / total_stories) * 100
    remaining_stories = total_stories - processed_count
    
    # Calculate approximate word count of current refined beat book
    word_count = len(current_refined.split())
    
    prompt_text = CLAUDE_REVIEW_PROMPT.format(
        current_date=current_date,
        batch_num=batch_num,
        total_batches=total_batches,
        processed_count=processed_count,
        total_stories=total_stories,
        remaining_stories=remaining_stories,
        progress_percentage=progress_percentage,
        word_count=word_count,
        current_refined=current_refined
    )
    
    try:
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE REVIEW CHECKPOINT")
        print("="*80)
        print(f"📊 Progress: {progress_percentage:.1f}% ({processed_count}/{total_stories} stories)")
        print(f"📦 Batch: {batch_num}/{total_batches}")
        print(f"📝 Current beat book size: {len(current_refined)} characters, ~{len(current_refined.split())} words")
        print(f"🔧 Initiating Claude Sonnet 4.5 review with web search capability...")
        print("-"*80)
        
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        print("⏳ Sending request to Claude...")
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=16000,
            temperature=0.7,
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 10
            }],
            messages=[{
                "role": "user",
                "content": prompt_text
            }]
        )
        
        print(f"✅ Response received from Claude")
        print(f"📊 Response stats: {response.usage.input_tokens} input tokens, {response.usage.output_tokens} output tokens")
        
        # Track tool usage
        web_searches = 0
        print("\n🔍 Processing response blocks:")
        
        # Extract text from response and log tool use
        result_text = ""
        for i, block in enumerate(response.content):
            if block.type == "text":
                result_text += block.text
                print(f"  📄 Block {i+1}: Text content ({len(block.text)} chars)")
            elif block.type == "tool_use":
                web_searches += 1
                tool_name = block.name
                print(f"  🔎 Block {i+1}: Tool use - {tool_name}")
                if hasattr(block, 'input') and isinstance(block.input, dict):
                    query = block.input.get('query', 'N/A')
                    print(f"      Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        result_text = result_text.strip()
        
        print(f"\n📈 Review complete:")
        print(f"  • Web searches performed: {web_searches}")
        print(f"  • Reviewed beat book size: {len(result_text)} characters, ~{len(result_text.split())} words")
        size_change = len(result_text) - len(current_refined)
        change_pct = (size_change / len(current_refined) * 100) if current_refined else 0
        print(f"  • Size change: {size_change:+d} chars ({change_pct:+.1f}%)")
        print("="*80 + "\n")
        
        return result_text
        
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error during Claude review: {e}")
        print("="*80 + "\n")
        return None


def save_state(state_file, state):
    """Save the current state to file."""
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f"State saved to {state_file}")


def save_beat_book(beat_book_file, beat_book_text, caroline_county_info=None):
    """Save the current beat book to a separate file.
    
    Args:
        beat_book_file: Path to the beat book file
        beat_book_text: The beat book content
        caroline_county_info: Optional Caroline County statistics to append
    """
    # If Caroline County info is provided and this is a refined beat book, append it
    if caroline_county_info and 'refined' in beat_book_file:
        beat_book_text = append_quick_stats_section(beat_book_text, caroline_county_info)
    
    with open(beat_book_file, 'w', encoding='utf-8') as f:
        f.write(beat_book_text)
    print(f"Beat book saved to {beat_book_file}")


def parse_token_limit_error(error_text):
    """
    Parse a 413 token limit error to extract limit and requested tokens.
    
    Returns:
        tuple: (limit, requested) or (None, None) if not a token limit error
    """
    # Look for pattern like: "Limit 8000, Requested 8740"
    match = re.search(r'Limit\s+(\d+),\s*Requested\s+(\d+)', error_text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def trim_beat_book_for_token_limit(beat_book_text, target_reduction_ratio):
    """
    Intelligently trim the beat book to reduce token count.
    
    Strategy:
    - Keep the opening paragraph/header intact
    - Trim from the middle sections proportionally
    - Keep the most recent additions (at the end) relatively intact
    
    Args:
        beat_book_text: The full beat book text
        target_reduction_ratio: Float between 0 and 1, representing how much to keep
        
    Returns:
        Trimmed beat book text
    """
    lines = beat_book_text.split('\n')
    
    if len(lines) <= 10:
        # Too short to trim safely, just return as-is
        return beat_book_text
    
    # Keep first 5 lines (header) intact
    header = '\n'.join(lines[:5])
    
    # Keep last 20% of lines (recent additions) relatively intact
    keep_from_end = max(5, int(len(lines) * 0.2))
    footer = '\n'.join(lines[-keep_from_end:])
    
    # Trim the middle section
    middle_lines = lines[5:-keep_from_end]
    if middle_lines:
        keep_count = int(len(middle_lines) * target_reduction_ratio)
        # Keep every Nth line to preserve structure
        if keep_count > 0:
            step = len(middle_lines) / keep_count
            trimmed_middle = [middle_lines[int(i * step)] for i in range(keep_count)]
        else:
            trimmed_middle = []
        middle = '\n'.join(trimmed_middle)
    else:
        middle = ""
    
    # Add a note about trimming
    trim_note = "\n\n[Note: Beat book content has been temporarily trimmed to fit token limits. Full context will be restored in next iteration.]\n\n"
    
    return f"{header}\n\n{middle}{trim_note}{footer}"


def update_beat_book(current_beat_book, stories_batch, batch_num, total_batches, total_stories, batch_size, processed_count):
    """
    Send current beat book and new stories to Groq model for update.
    
    Args:
        current_beat_book: Current beat book text
        stories_batch: List of story dicts to analyze
        batch_num: Current batch number
        total_batches: Total number of batches
        total_stories: Total number of stories in dataset
        batch_size: Number of stories per batch
        processed_count: Number of stories already processed
        
    Returns:
        Updated beat book text, or None if update failed
    """
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Format stories for the prompt
    stories_text = "\n\n---\n\n".join([
        f"STORY {i+1}:\nTitle: {story['title']}\nDate: {story['date']}\nContent: {story['content']}"
        for i, story in enumerate(stories_batch)
    ])
    
    # Try with full beat book first, then trim if needed
    beat_book_to_use = current_beat_book
    max_retries = 3
    
    for attempt in range(max_retries):
        prompt = BEAT_BOOK_PROMPT.format(
            current_date=current_date,
            batch_num=batch_num,
            total_batches=total_batches,
            total_stories=total_stories,
            batch_size=len(stories_batch),  # Use actual batch size in case last batch is smaller
            processed_count=processed_count,
            current_beat_book=beat_book_to_use,
            stories=stories_text
        )
        
        try:
            if attempt > 0:
                print(f"Retry attempt {attempt + 1}/{max_retries} with trimmed beat book...")
            else:
                print(f"Sending batch {batch_num}/{total_batches} to Groq model...")
                
            result = subprocess.run(
                ['uv', 'run', 'llm', '-m', 'groq/openai/gpt-oss-120b', '-o', 'max_tokens', '2048', prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=120  # 2 minute timeout
            )
            
            response = result.stdout.strip()
            
            # Check if model said no update needed
            if response == "NO UPDATE NEEDED" or response.startswith("NO UPDATE NEEDED"):
                print("Model determined no update needed for this batch.")
                return current_beat_book
            
            return response
            
        except subprocess.CalledProcessError as e:
            # Check if this is a 413 token limit error
            if "Error code: 413" in e.stderr or "rate_limit_exceeded" in e.stderr:
                limit, requested = parse_token_limit_error(e.stderr)
                
                if limit and requested:
                    print(f"Token limit exceeded: Limit={limit}, Requested={requested}")
                    
                    # Calculate how much we need to reduce
                    # We want to be comfortably under the limit, so target 85% of limit
                    target_tokens = int(limit * 0.85)
                    reduction_ratio = target_tokens / requested
                    
                    print(f"Trimming beat book by ~{int((1 - reduction_ratio) * 100)}% to fit within token limit...")
                    
                    # Trim the beat book for next attempt
                    beat_book_to_use = trim_beat_book_for_token_limit(current_beat_book, reduction_ratio)
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Brief pause before retry
                        continue
                    else:
                        print("ERROR: Still exceeding token limit after maximum retries.")
                        print("Consider reducing --batch-size or manually trimming the beat book.")
                        return None
                else:
                    print(f"ERROR: Token limit error but couldn't parse details: {e.stderr}")
                    return None
            else:
                # Some other error
                print(f"ERROR: Command failed with exit code {e.returncode}")
                print(f"stderr: {e.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("ERROR: Request timed out after 120 seconds")
            return None
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            return None
    
    # Should never reach here, but just in case
    return None


def build_beat_book(input_file, state_file, beat_book_file, refined_beat_book_file, batch_size=20, delay=2):
    """
    Main function to iteratively build the beat book using Groq and refine with Claude.
    
    Args:
        input_file: Path to source_stories.json
        state_file: Path to save state between runs
        beat_book_file: Path to save the Groq beat book
        refined_beat_book_file: Path to save the Claude refined beat book
        batch_size: Number of stories per batch
        delay: Seconds to wait between API calls
    """
    # Load stories
    print(f"Loading stories from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_stories = json.load(f)
    
    print(f"Loaded {len(all_stories)} stories")
    
    # Load previous state if exists
    state = load_state(state_file)
    
    # Gather Caroline County information once per run if not already cached
    if state.get('caroline_county_info') is None:
        print("\nGathering background information about Caroline County...")
        caroline_info = search_caroline_county_info()
        if caroline_info:
            state['caroline_county_info'] = caroline_info
            # Save state immediately after gathering this info
            save_state(state_file, state)
        else:
            print("⚠ Warning: Failed to gather Caroline County information. Continuing without it.")
    else:
        print("\n✓ Using cached Caroline County information from previous run")
    
    # Create list of indices we haven't processed yet
    total_indices = list(range(len(all_stories)))
    unprocessed_indices = [i for i in total_indices if i not in state['processed_indices']]
    
    if not unprocessed_indices:
        print("\n✓ All stories have been processed!")
        
        # Save final versions with Quick Statistics appended
        save_beat_book(beat_book_file, state['beat_book'])
        save_beat_book(refined_beat_book_file, state['refined_beat_book'], state.get('caroline_county_info'))
        save_state(state_file, state)
        
        print(f"Final beat book saved to {beat_book_file}")
        print(f"Final refined beat book saved to {refined_beat_book_file}")
        if state.get('caroline_county_info'):
            print("✓ Quick Statistics section included in refined beat book")
        return
    
    # Calculate total batches
    total_batches = (len(all_stories) + batch_size - 1) // batch_size
    state['total_batches'] = total_batches
    
    print(f"\nProgress: {len(state['processed_indices'])}/{len(all_stories)} stories processed")
    print(f"Remaining: {len(unprocessed_indices)} stories in {(len(unprocessed_indices) + batch_size - 1) // batch_size} batches")
    
    # Shuffle unprocessed indices for random selection
    random.shuffle(unprocessed_indices)
    
    # Process in batches
    for i in range(0, len(unprocessed_indices), batch_size):
        batch_indices = unprocessed_indices[i:i + batch_size]
        state['batch_num'] += 1
        current_batch_num = state['batch_num']
        
        print(f"\n{'='*60}")
        print(f"Processing batch {current_batch_num}/{total_batches}")
        print(f"Stories in this batch: {len(batch_indices)}")
        print(f"{'='*60}")
        
        # Get stories for this batch
        stories_batch = [all_stories[idx] for idx in batch_indices]
        
        # Update beat book with retry logic
        max_retries = 3
        retry_count = 0
        updated_beat_book = None
        
        while retry_count < max_retries and updated_beat_book is None:
            if retry_count > 0:
                wait_time = delay * (2 ** retry_count)  # Exponential backoff
                print(f"Retry {retry_count}/{max_retries} - waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            
            updated_beat_book = update_beat_book(
                state['beat_book'],
                stories_batch,
                current_batch_num,
                total_batches,
                len(all_stories),
                batch_size,
                len(state['processed_indices'])
            )
            retry_count += 1
        
        if updated_beat_book is None:
            print(f"\n✗ Failed to process batch {current_batch_num} after {max_retries} retries")
            print(f"Saving state and exiting. You can resume by running the script again.")
            save_state(state_file, state)
            save_beat_book(beat_book_file, state['beat_book'])
            save_beat_book(refined_beat_book_file, state['refined_beat_book'])
            return
        
        # Update Groq beat book in state
        state['beat_book'] = updated_beat_book
        state['processed_indices'].extend(batch_indices)
        
        # Save Groq beat book
        save_beat_book(beat_book_file, state['beat_book'])
        
        # Now refine with Claude
        print(f"\n{'='*60}")
        print(f"Stage 2: Claude refinement")
        print(f"{'='*60}")
        
        refined_retry_count = 0
        refined_beat_book = None
        
        while refined_retry_count < max_retries and refined_beat_book is None:
            if refined_retry_count > 0:
                wait_time = delay * (2 ** refined_retry_count)
                print(f"Retry {refined_retry_count}/{max_retries} - waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            
            refined_beat_book = refine_with_claude(
                state['refined_beat_book'],
                state['beat_book'],
                current_batch_num,
                total_batches,
                len(state['processed_indices']),
                len(all_stories)
            )
            refined_retry_count += 1
        
        if refined_beat_book is None:
            print(f"\n⚠ Failed to refine with Claude after {max_retries} retries")
            print(f"Keeping previous refined version and continuing...")
        else:
            # Update refined beat book in state
            state['refined_beat_book'] = refined_beat_book
            save_beat_book(refined_beat_book_file, state['refined_beat_book'], state.get('caroline_county_info'))
        
        # Check if this is a checkpoint batch (every 10 batches)
        is_checkpoint = (current_batch_num % 10 == 0)
        
        if is_checkpoint:
            print(f"\n{'='*60}")
            print(f"🔍 CHECKPOINT REVIEW - Batch {current_batch_num}")
            print(f"{'='*60}")
            
            review_retry_count = 0
            reviewed_beat_book = None
            
            while review_retry_count < max_retries and reviewed_beat_book is None:
                if review_retry_count > 0:
                    wait_time = delay * (2 ** review_retry_count)
                    print(f"Retry {review_retry_count}/{max_retries} - waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                
                reviewed_beat_book = review_with_claude(
                    state['refined_beat_book'],
                    current_batch_num,
                    total_batches,
                    len(state['processed_indices']),
                    len(all_stories)
                )
                review_retry_count += 1
            
            if reviewed_beat_book is None:
                print(f"\n⚠ Failed checkpoint review after {max_retries} retries")
                print(f"Keeping current refined version and continuing...")
            else:
                # Update refined beat book with reviewed version
                state['refined_beat_book'] = reviewed_beat_book
                save_beat_book(refined_beat_book_file, state['refined_beat_book'], state.get('caroline_county_info'))
                print(f"✓ Checkpoint review complete - beat book fact-checked and balanced")
        
        # Save state after each successful batch
        save_state(state_file, state)
        
        print(f"✓ Batch {current_batch_num} complete. Progress: {len(state['processed_indices'])}/{len(all_stories)} stories")
        
        # Wait between batches to avoid rate limits (except on last batch)
        if i + batch_size < len(unprocessed_indices):
            print(f"Waiting {delay}s before next batch...")
            time.sleep(delay)
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETE! All {len(all_stories)} stories processed!")
    print(f"{'='*60}")
    
    # Save final versions with Quick Statistics appended
    save_beat_book(beat_book_file, state['beat_book'])
    save_beat_book(refined_beat_book_file, state['refined_beat_book'], state.get('caroline_county_info'))
    save_state(state_file, state)
    
    print(f"Groq beat book saved to: {beat_book_file}")
    print(f"Claude refined beat book saved to: {refined_beat_book_file}")
    if state.get('caroline_county_info'):
        print("✓ Quick Statistics section included in refined beat book")
    print(f"Total batches processed: {state['batch_num']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Build an education beat book by iteratively analyzing stories with Groq GPT-OSS-120B'
    )
    parser.add_argument(
        '--input',
        default='source_stories.json',
        help='Input JSON file with stories (default: source_stories.json)'
    )
    parser.add_argument(
        '--state',
        default='beat_book_state.json',
        help='State file to track progress (default: beat_book_state.json)'
    )
    parser.add_argument(
        '--output',
        default='education_beat_book.md',
        help='Output file for Groq beat book (default: education_beat_book.md)'
    )
    parser.add_argument(
        '--refined-output',
        default='education_beat_book_refined.md',
        help='Output file for Claude refined beat book (default: education_beat_book_refined.md)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=20,
        help='Number of stories per batch (default: 20)'
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=2,
        help='Seconds to wait between batches (default: 2)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset state and start from beginning'
    )
    
    args = parser.parse_args()
    
    # Reset state if requested
    if args.reset and Path(args.state).exists():
        Path(args.state).unlink()
        print(f"Removed existing state file: {args.state}")
    
    build_beat_book(
        args.input,
        args.state,
        args.output,
        args.refined_output,
        batch_size=args.batch_size,
        delay=args.delay
    )
