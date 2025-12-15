#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
#     "openai",
#     "python-dotenv",
#     "openai-agents",
# ]
# ///
"""
Iteratively build a beat book for education reporting by processing stories in random batches.
Uses a two-stage process:
1. Local Ollama gemma3:4b reads stories and takes notes
2. OpenAI GPT-5.2 refines the beat book and outputs education_beat_book_refined.md

This is a local variant of build_beat_book_groq.py that uses Ollama instead of Groq,
allowing faster iteration without cloud API rate limits or timeouts.
"""
import json
import argparse
import random
import os
import sys
import traceback
import requests
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from agents import apply_diff

# Load environment variables
load_dotenv()

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = "gemma3:4b"


BEAT_BOOK_PROMPT = """You are a reporter taking notes for a "beat book" - a reporting guide for covering education in Caroline County, Maryland (on the Eastern Shore) for the Easton Star-Democrat.

<context>
Today is {current_date}.
</context>

<stories>
{stories}
</stories>

<instructions>
Read these stories and take detailed factual notes. Document everything explicitly stated in the articles, especially about Caroline County education.
Be thorough. Capture specific details. Stick to facts - do not infer, speculate, or editorialize. If something isn't clearly stated in the stories, don't include it.
Copy sentences down from the articles. If you copy exact sentences, please change the wording to make your notes unique.
</instructions>

<output_format>
Return your notes in Markdown format. Start immediately with the notes - no preamble, no introduction, no commentary.
</output_format>"""


REFINE_PROMPT = """You are an editor creating a "beat book" - a concise reporting guide for a new reporter covering education in Caroline County, MARYLAND (on the Eastern Shore, NOT Virginia) for the Easton Star-Democrat.

<context>
Today is {current_date}. Progress: {progress_percentage:.1f}% complete (batch {batch_num} of {total_batches}, {processed_count} of {total_stories} stories processed).

{reporter_context}
</context>

<current_beat_book_file>
beat_book.md
</current_beat_book_file>

<file_content path="beat_book.md">
{previous_refined}
</file_content>

{reporter_notes_section}

<word_count>
Current: ~{word_count} words. Target: 5,000 words. Please trim when appropriate to match the target.
</word_count>

<instructions>
Update the beat book in `beat_book.md` to incorporate the new information. Your priorities:

1. **Synthesize, don't catalog** - This is NOT a collection of story summaries. Combine information from multiple sources into unified sections about topics, people, and institutions. If multiple notes mention the same person, school, or issue, merge that information into one place.
2. **Focus on the big picture** - What are the major ongoing issues? Who are the key players? What should a reporter know to cover this beat effectively? Avoid one-off events unless they reveal larger patterns.
3. **Organize by topic, not by source** - Structure the beat book around subjects (budget, schools, personnel, programs) rather than individual stories or batches.
4. **Caroline County, Maryland only** - cut information about other counties or states.
5. **No citations** - Do NOT mention specific articles, reporters, publication dates, or "according to" attributions. Present information as established fact.
6. **Narrative style** - flowing paragraphs, not bullet points (except for contact lists).
</instructions>

<writing_style>
Write prose that is direct, clear, and substantive. Prioritize:

- **Short paragraphs**: Keep paragraphs to 2-4 sentences max. One idea per paragraph. White space helps readers. This is journalism, not academia.
- **Natural flow over formality**: Write like you're explaining something to a smart colleague, not drafting a legal document. Vary sentence length. Let ideas breathe.
- **Precision without stiffness**: Use concrete details and specific names, but avoid the mechanical cadence of typical institutional writing. "The board approved a $2.3 million budget" beats "The board gave their approval to a budget in the amount of $2.3 million."
- **Honest about scope**: If something is unclear or limited, say so briefly and move on. Don't pad with qualifiers or hedge excessively.
- **No filler**: Cut "it should be noted that," "it is important to mention," "as previously stated," and similar throat-clearing. Start with the information.
- **Active voice, strong verbs**: "The superintendent restructured the curriculum" not "The curriculum was restructured by the superintendent."

**CRITICAL - Do NOT editorialize or make meta-commentary:**
- NEVER write phrases like "at the intersection of," "serves as a reminder that," "underscores the importance of," "highlights the challenges," "reflects broader trends," "speaks to the"
- NEVER tell the reader what something "means" or "suggests" or "illustrates" - just state what happened
- NEVER frame things as "notable," "significant," "important," or "worth noting" - if it's in the beat book, it's already deemed relevant
- NEVER use "amid" or "amidst" to create false drama
- NEVER write sentences that could start with "This shows that..." or "This demonstrates..." - just give the facts
- You are a reporter, not a commentator. State what happened. Let readers draw conclusions.

**Avoid these AI-generated phrases entirely:**
- "at the intersection of X and Y"
- "serves as a testament to"
- "underscores/highlights/illustrates the"
- "speaks to the broader"
- "reflects the challenges/realities of"
- "a reminder that"
- "in an era of"
- "navigating the complexities of"
- "a microcosm of"
- "emblematic of"
- "a window into"
- "it's not just X — it's Y"

The goal is prose that a reader trusts because it respects their time and intelligence.
</writing_style>

<output_format>
Use the `apply_patch` tool to update `beat_book.md`. Do NOT return the full text in the response.
</output_format>"""


REVIEW_PROMPT = """You are an editor conducting a checkpoint review of an education beat book for the Easton Star-Democrat, covering Caroline County, MARYLAND (on the Eastern Shore, NOT Virginia).

<context>
Today is {current_date}. Progress: {progress_percentage:.1f}% complete (batch {batch_num}, {processed_count} of {total_stories} stories). This checkpoint happens every 10 batches.

You have web search access to fact-check information.
</context>

<current_beat_book_file>
beat_book.md
</current_beat_book_file>

<file_content path="beat_book.md">
{current_refined}
</file_content>

<word_count>
Current: ~{word_count} words. Target: 5,000-10,000 words.
</word_count>

<instructions>
Review and improve the beat book in `beat_book.md`. Use web search (up to 10 searches) to:
- Verify current job titles and positions
- Check if ongoing issues have been resolved
- Confirm key facts

Remove only:
- Information confirmed to be outdated or incorrect
- Information about other counties (not Caroline County, Maryland)
- Clear duplicates

Preserve all substantive information - names, numbers, dates, and specific details.
</instructions>

<writing_style>
Maintain prose that is direct, clear, and substantive:

- **Short paragraphs**: 2-4 sentences max. One idea per paragraph. White space helps readers.
- **Natural flow over formality**: Write like you're explaining something to a smart colleague. Vary sentence length.
- **Precision without stiffness**: Concrete details, specific names, but avoid mechanical institutional cadence.
- **No filler**: Cut throat-clearing phrases. Start with the information.
- **Active voice, strong verbs**: Direct constructions over passive.

**CRITICAL - Remove AI-generated editorializing:**
If you see phrases like these, DELETE them or rewrite to just state facts:
- "at the intersection of," "serves as a reminder," "underscores the importance," "highlights the challenges," "reflects broader trends," "speaks to," "emblematic of," "a microcosm of," "navigating the complexities"
- Anything telling the reader what something "means" or "suggests"
- Framing things as "notable," "significant," or "important"

You are a reporter, not a commentator. State what happened. Let readers draw their own conclusions.
</writing_style>

<output_format>
Use the `apply_patch` tool to update `beat_book.md`. Do NOT return the full text in the response.
</output_format>"""


INITIAL_BEAT_BOOK = """# Education Beat Book - Easton Star-Democrat
## Caroline County, Maryland

This guide covers the education beat in Caroline County, Maryland, focusing on the schools, institutions, and key players that shape local education coverage."""


INITIAL_REFINED_BEAT_BOOK = """# Education Beat Book - Easton Star-Democrat
## Caroline County, Maryland

This guide covers the education beat in Caroline County, Maryland, focusing on the schools, institutions, and key players that shape local education coverage."""


def call_ollama(prompt, model=OLLAMA_MODEL, max_tokens=2048):
    """
    Call the local Ollama API with the given prompt.
    
    Args:
        prompt: The prompt text to send
        model: The Ollama model to use (default: gemma3:4b)
        max_tokens: Maximum tokens to generate
        
    Returns:
        The response text from Ollama, or None if failed
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to Ollama at {OLLAMA_BASE_URL}")
        print("Make sure Ollama is running with: ollama serve")
        return None
    except Exception as e:
        print(f"ERROR: Ollama API call failed: {e}")
        return None


def search_caroline_county_info():
    """
    Use OpenAI GPT-5.2 with web search to gather current information about
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
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.responses.create(
            model="gpt-5.2-2025-12-11",
            instructions="You are a research assistant gathering factual statistics. Use web search to find current, accurate information.",
            input=prompt,
            max_output_tokens=4096,
            tools=[{
                "type": "web_search"
            }],
            store=False
        )
        
        # Extract text from response using the Responses API structure
        result_text = ""
        web_searches = 0
        
        for output_item in response.output:
            if output_item.type == "message":
                for content_block in output_item.content:
                    if content_block.type == "output_text":
                        result_text += content_block.text
            elif output_item.type == "web_search_call":
                web_searches += 1
                if hasattr(output_item, 'action') and hasattr(output_item.action, 'query'):
                    query = output_item.action.query
                    print(f"  🔎 Web search {web_searches}: {query[:80]}{'...' if len(query) > 80 else ''}")
        
        result_text = result_text.strip()
        
        print(f"\n✅ Web search complete")
        print(f"  • Searches performed: {web_searches}")
        print(f"  • Response length: {len(result_text)} characters")
        print(f"  • Input tokens: {response.usage.input_tokens}")
        print(f"  • Output tokens: {response.usage.output_tokens}")
        print("="*80 + "\n")
        
        return result_text
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to gather Caroline County information: {e}")
        traceback.print_exc()
        print("="*80 + "\n")
        return None


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


def refine_with_openai(previous_refined, latest_notes, batch_num, total_batches, processed_count, total_stories, caroline_county_info=None, reporter_context=None, reporter_notes_section=None):
    """
    Use OpenAI GPT-5.2 to refine the beat book by comparing previous refined version
    with the latest notes from local model.
    
    Args:
        previous_refined: Previous refined beat book text
        latest_notes: Latest notes from local Ollama model
        batch_num: Current batch number
        total_batches: Total number of batches
        processed_count: Number of stories processed so far
        total_stories: Total number of stories in dataset
        caroline_county_info: Optional background stats about Caroline County for context
        reporter_context: Context about reporter(s) for the prompt
        reporter_notes_section: Pre-formatted XML section with reporter notes
        
    Returns:
        Refined beat book text, or None if refinement failed
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    progress_percentage = (processed_count / total_stories) * 100
    
    # Calculate approximate word count of current refined beat book
    word_count = len(previous_refined.split())
    
    # Default reporter context if not provided
    if reporter_context is None:
        reporter_context = "A reporter has been taking notes from source stories. Your job is to edit these notes into a cohesive, well-written beat book."
    
    # Build reporter notes section if not provided
    if reporter_notes_section is None:
        notes_with_context = latest_notes
        if caroline_county_info:
            notes_with_context = latest_notes + "\n\n---\n\n## Background: Caroline County Statistics\n\n" + caroline_county_info
        reporter_notes_section = f"<reporter_notes>\n{notes_with_context}\n</reporter_notes>"
    elif caroline_county_info:
        # Append Caroline County context to the notes section
        reporter_notes_section = reporter_notes_section + f"\n\n<background_context>\n## Caroline County Statistics\n\n{caroline_county_info}\n</background_context>"
    
    # Reuse the same prompt template
    prompt_text = REFINE_PROMPT.format(
        current_date=current_date,
        batch_num=batch_num,
        total_batches=total_batches,
        processed_count=processed_count,
        total_stories=total_stories,
        progress_percentage=progress_percentage,
        word_count=word_count,
        previous_refined=previous_refined,
        reporter_context=reporter_context,
        reporter_notes_section=reporter_notes_section
    )
    
    try:
        print("Refining with OpenAI GPT-5.2...")
        print(f"  • Prompt size: {len(prompt_text)} characters")
        print(f"  • Previous beat book: {len(previous_refined)} characters")
        print("  • Sending request to OpenAI API...")
        sys.stdout.flush()  # Force output to display immediately
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.responses.create(
            model="gpt-5.2-2025-12-11",
            instructions="You are a reporter writing a reference guide. State facts. Do NOT editorialize. Never write 'at the intersection of,' 'underscores the importance,' 'serves as a reminder,' 'highlights the challenges,' 'reflects broader trends,' or similar meta-commentary. Never tell readers what something 'means' or 'suggests.' Just state what happened and let readers judge. Short paragraphs, active voice, no filler.",
            input=prompt_text,
            max_output_tokens=24000,
            temperature=0.7,
            reasoning={"effort": "none"},
            tools=[{"type": "apply_patch"}],
            store=False
        )
        
        print(f"  • Response received!")
        print(f"  • Status: {response.status}")
        print(f"  • Input tokens: {response.usage.input_tokens}")
        print(f"  • Output tokens: {response.usage.output_tokens}")
        
        current_content = previous_refined
        patch_applied = False
        
        # Process response items
        for output_item in response.output:
            if output_item.type == "apply_patch_call":
                op = output_item.operation
                print(f"  • Received patch operation: {op.type} for {op.path}")
                
                if op.path == "beat_book.md":
                    try:
                        if op.type == "update_file":
                            current_content = apply_diff(current_content, op.diff)
                            patch_applied = True
                            print(f"  • ✅ Successfully applied patch to {op.path}")
                        elif op.type == "create_file":
                            current_content = apply_diff("", op.diff, create=True)
                            patch_applied = True
                            print(f"  • ✅ Successfully created {op.path}")
                    except Exception as e:
                        print(f"  • ❌ Failed to apply patch: {e}")
            
            elif output_item.type == "message":
                # Log any message content (could be explanation)
                msg_text = ""
                for content_block in output_item.content:
                    if content_block.type == "output_text":
                        msg_text += content_block.text
                if msg_text.strip():
                    print(f"  • Model message: {msg_text[:100]}...")

        if not patch_applied:
            print("  • ⚠️ No patches applied. Checking for full text fallback...")
            # Fallback: check if model returned full text despite instructions
            result_text = ""
            for output_item in response.output:
                if output_item.type == "message":
                    for content_block in output_item.content:
                        if content_block.type == "output_text":
                            result_text += content_block.text
            
            result_text = result_text.strip()
            if result_text and result_text.startswith("#"):
                print("  • Found full text in response, using that.")
                return result_text
            else:
                print("  • No valid update found.")
                return previous_refined # Return original if no update
        
        return current_content
        
    except Exception as e:
        error_str = str(e).lower()
        if "rate_limit" in error_str or "rate limit" in error_str:
            print(f"ERROR: OpenAI rate limit exceeded: {e}")
        elif "connection" in error_str:
            print(f"ERROR: Could not connect to OpenAI API: {e}")
        else:
            print(f"ERROR: Unexpected error during OpenAI refinement: {type(e).__name__}: {e}")
            traceback.print_exc()
        return None


def review_with_openai(current_refined, batch_num, total_batches, processed_count, total_stories):
    """
    Use OpenAI GPT-5.2 with web search to comprehensively review the beat book.
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
    
    # Calculate approximate word count of current refined beat book
    word_count = len(current_refined.split())
    
    # Reuse the same prompt template
    prompt_text = REVIEW_PROMPT.format(
        current_date=current_date,
        batch_num=batch_num,
        processed_count=processed_count,
        total_stories=total_stories,
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
        print(f"🔧 Initiating OpenAI GPT-5.2 review with web search capability...")
        print("-"*80)
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        print("⏳ Sending request to OpenAI...")
        response = client.responses.create(
            model="gpt-5.2-2025-12-11",
            instructions="You are a fact-checker. Verify facts with web search. Remove AI-generated editorializing: phrases like 'at the intersection of,' 'underscores,' 'highlights,' 'serves as a reminder,' 'reflects broader trends.' State facts only. No meta-commentary about what things 'mean' or 'suggest.'",
            input=prompt_text,
            max_output_tokens=24000,
            temperature=0.7,
            reasoning={"effort": "none"},
            tools=[{
                "type": "web_search"
            }, {
                "type": "apply_patch"
            }],
            store=False
        )
        
        print(f"✅ Response received from OpenAI")
        print(f"📊 Response stats: {response.usage.input_tokens} input tokens, {response.usage.output_tokens} output tokens")
        
        # Track tool usage
        web_searches = 0
        print("\n🔍 Processing response blocks:")
        
        current_content = current_refined
        patch_applied = False
        
        for i, output_item in enumerate(response.output):
            if output_item.type == "message":
                msg_text = ""
                for content_block in output_item.content:
                    if content_block.type == "output_text":
                        msg_text += content_block.text
                if msg_text.strip():
                    print(f"  📄 Block {i+1}: Text content ({len(msg_text)} chars)")
            
            elif output_item.type == "web_search_call":
                web_searches += 1
                if hasattr(output_item, 'action') and hasattr(output_item.action, 'query'):
                    query = output_item.action.query
                    print(f"  🔎 Block {i+1}: Web search - {query[:100]}{'...' if len(query) > 100 else ''}")
            
            elif output_item.type == "apply_patch_call":
                op = output_item.operation
                print(f"  • Received patch operation: {op.type} for {op.path}")
                
                if op.path == "beat_book.md":
                    try:
                        if op.type == "update_file":
                            current_content = apply_diff(current_content, op.diff)
                            patch_applied = True
                            print(f"  • ✅ Successfully applied patch to {op.path}")
                        elif op.type == "create_file":
                            current_content = apply_diff("", op.diff, create=True)
                            patch_applied = True
                            print(f"  • ✅ Successfully created {op.path}")
                    except Exception as e:
                        print(f"  • ❌ Failed to apply patch: {e}")

        if not patch_applied:
            print("  • ⚠️ No patches applied. Checking for full text fallback...")
            # Fallback: check if model returned full text despite instructions
            result_text = ""
            for output_item in response.output:
                if output_item.type == "message":
                    for content_block in output_item.content:
                        if content_block.type == "output_text":
                            result_text += content_block.text
            
            result_text = result_text.strip()
            if result_text and result_text.startswith("#"):
                print("  • Found full text in response, using that.")
                return result_text
            else:
                print("  • No valid update found.")
                return current_refined # Return original if no update
        
        print(f"\n📈 Review complete:")
        print(f"  • Web searches performed: {web_searches}")
        print(f"  • Reviewed beat book size: {len(current_content)} characters, ~{len(current_content.split())} words")
        size_change = len(current_content) - len(current_refined)
        change_pct = (size_change / len(current_refined) * 100) if current_refined else 0
        print(f"  • Size change: {size_change:+d} chars ({change_pct:+.1f}%)")
        print("="*80 + "\n")
        
        return current_content
        
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error during OpenAI review: {e}")
        traceback.print_exc()
        print("="*80 + "\n")
        return None


def save_state(state_file, state):
    """Save the current state to file."""
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print(f"State saved to {state_file}")


def save_beat_book(beat_book_file, beat_book_text):
    """Save the current beat book to a separate file.
    
    Args:
        beat_book_file: Path to the beat book file
        beat_book_text: The beat book content
    """
    with open(beat_book_file, 'w', encoding='utf-8') as f:
        f.write(beat_book_text)
    print(f"Beat book saved to {beat_book_file}")


def update_beat_book_local(stories_batch, batch_num, total_batches, total_stories, batch_size):
    """
    Send stories to local Ollama model for note-taking.
    
    Unlike the Groq version, this doesn't need timeout handling or rate limit checks
    since Ollama runs locally. The only thing we check for is token limits by
    splitting batches if responses seem truncated.
    
    Args:
        stories_batch: List of story dicts to analyze
        batch_num: Current batch number
        total_batches: Total number of batches
        total_stories: Total number of stories in dataset
        batch_size: Number of stories per batch
        
    Returns:
        Notes from this batch, or None if failed
    """
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Format stories for the prompt - date is optional
    stories_text = "\n\n---\n\n".join([
        f"STORY {i+1}:\nTitle: {story['title']}\n" + 
        (f"Date: {story['date']}\n" if 'date' in story else "") +
        f"Content: {story['content']}"
        for i, story in enumerate(stories_batch)
    ])
    
    prompt = BEAT_BOOK_PROMPT.format(
        current_date=current_date,
        batch_num=batch_num,
        total_batches=total_batches,
        total_stories=total_stories,
        batch_size=len(stories_batch),
        stories=stories_text
    )
    
    print(f"Sending {len(stories_batch)} stories to Ollama ({OLLAMA_MODEL})...")
    print(f"  • Prompt size: {len(prompt)} characters")
    
    response = call_ollama(prompt, max_tokens=2048)
    
    if response is None:
        print(f"ERROR: Failed to get response from Ollama")
        return None
    
    print(f"  • Response length: {len(response)} characters")
    
    # Check for empty or minimal response
    if not response or len(response.strip()) < 50:
        print("Model returned minimal content for this batch.")
        return response if response else "No Caroline County education content in this batch."
    
    return response


def build_beat_book(input_file, state_file, batch_notes_prefix, beat_book_file, batch_size=20, delay=0):
    """
    Main function to iteratively build the beat book using local Ollama and refine with OpenAI.
    
    Args:
        input_file: Path to source_stories.json
        state_file: Path to save state between runs
        batch_notes_prefix: Prefix for batch notes files (e.g., 'output/batch_notes' -> 'output/batch_notes_1.md')
        beat_book_file: Path to save the OpenAI refined beat book
        batch_size: Number of stories per batch
        delay: Seconds to wait between batches (minimal for local, mainly for OpenAI)
    """
    # Create output directory if needed
    for filepath in [state_file, beat_book_file, batch_notes_prefix]:
        output_dir = Path(filepath).parent
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created output directory: {output_dir}")
    
    # Load stories
    print(f"Loading stories from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_stories = json.load(f)
    
    print(f"Loaded {len(all_stories)} stories")
    
    # Test Ollama connection
    print(f"\n🔗 Testing Ollama connection at {OLLAMA_BASE_URL}...")
    test_response = call_ollama("Say 'OK' if you can hear me.", max_tokens=10)
    if test_response is None:
        print("❌ Could not connect to Ollama. Please ensure it's running.")
        print("   Start Ollama with: ollama serve")
        print(f"   Then pull the model with: ollama pull {OLLAMA_MODEL}")
        return
    print(f"✅ Ollama is responding: {test_response[:50]}...")
    
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
        
        # Save final beat book
        save_beat_book(beat_book_file, state['refined_beat_book'])
        save_state(state_file, state)
        
        print(f"Final beat book saved to {beat_book_file}")
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
        
        # Process batch - local Ollama doesn't need the complex splitting logic
        # since we have more control over context limits
        batch_notes = update_beat_book_local(
            stories_batch,
            current_batch_num,
            total_batches,
            len(all_stories),
            len(stories_batch)
        )
        
        if batch_notes is None:
            print(f"ERROR: Failed to process batch {current_batch_num}")
            # Try splitting the batch if it might be too large
            if len(stories_batch) > 5:
                print("Attempting to split batch into smaller chunks...")
                all_batch_notes = []
                mid = len(stories_batch) // 2
                for sub_batch, suffix in [(stories_batch[:mid], "a"), (stories_batch[mid:], "b")]:
                    sub_notes = update_beat_book_local(
                        sub_batch,
                        current_batch_num,
                        total_batches,
                        len(all_stories),
                        len(sub_batch)
                    )
                    if sub_notes:
                        all_batch_notes.append(sub_notes)
                        # Save sub-batch notes
                        batch_dir = f"{batch_notes_prefix}/batch_{current_batch_num}"
                        Path(batch_dir).mkdir(parents=True, exist_ok=True)
                        batch_notes_file = f"{batch_dir}/notes_{suffix}.md"
                        save_beat_book(batch_notes_file, sub_notes)
                
                if all_batch_notes:
                    batch_notes = "\n\n---\n\n".join(all_batch_notes)
                else:
                    print("ERROR: Could not process batch even after splitting. Skipping.")
                    state['processed_indices'].extend(batch_indices)
                    save_state(state_file, state)
                    continue
            else:
                state['processed_indices'].extend(batch_indices)
                save_state(state_file, state)
                continue
        else:
            # Save batch notes
            batch_dir = f"{batch_notes_prefix}/batch_{current_batch_num}"
            Path(batch_dir).mkdir(parents=True, exist_ok=True)
            batch_notes_file = f"{batch_dir}/notes.md"
            save_beat_book(batch_notes_file, batch_notes)
        
        # Mark batch as processed
        state['processed_indices'].extend(batch_indices)
        
        # Check if there's no useful content
        if batch_notes and "no caroline county education content" in batch_notes.lower():
            print("No new Caroline County information in this batch - skipping OpenAI refinement")
            save_state(state_file, state)
            print(f"✓ Batch {current_batch_num} complete. Progress: {len(state['processed_indices'])}/{len(all_stories)} stories")
            continue
        
        # Format notes for OpenAI
        reporter_context = "A reporter has been taking notes from source stories. Your job is to edit these notes into a cohesive, well-written beat book."
        reporter_notes_section = f"<reporter_notes>\n{batch_notes}\n</reporter_notes>"
        
        state['beat_book'] = batch_notes
        state['reporter_context'] = reporter_context
        state['reporter_notes_section'] = reporter_notes_section
        
        # Now refine with OpenAI
        print(f"\n{'='*60}")
        print(f"Stage 2: OpenAI GPT-5.2 refinement")
        print(f"{'='*60}")
        
        max_retries = 3
        refined_retry_count = 0
        refined_beat_book = None
        
        while refined_retry_count < max_retries and refined_beat_book is None:
            if refined_retry_count > 0:
                wait_time = 2 * (2 ** refined_retry_count)
                print(f"Retry {refined_retry_count}/{max_retries} - waiting {wait_time}s before retry...")
                import time
                time.sleep(wait_time)
            
            refined_beat_book = refine_with_openai(
                state['refined_beat_book'],
                batch_notes,
                current_batch_num,
                total_batches,
                len(state['processed_indices']),
                len(all_stories),
                state.get('caroline_county_info'),
                reporter_context,
                reporter_notes_section
            )
            refined_retry_count += 1
        
        if refined_beat_book is None:
            print(f"\n⚠ Failed to refine with OpenAI after {max_retries} retries")
            print(f"Keeping previous refined version and continuing...")
        else:
            # Update refined beat book in state
            state['refined_beat_book'] = refined_beat_book
            save_beat_book(beat_book_file, state['refined_beat_book'])
        
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
                    wait_time = 2 * (2 ** review_retry_count)
                    print(f"Retry {review_retry_count}/{max_retries} - waiting {wait_time}s before retry...")
                    import time
                    time.sleep(wait_time)
                
                reviewed_beat_book = review_with_openai(
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
                save_beat_book(beat_book_file, state['refined_beat_book'])
                print(f"✓ Checkpoint review complete - beat book fact-checked and balanced")
        
        # Save state after each successful batch
        save_state(state_file, state)
        
        print(f"✓ Batch {current_batch_num} complete. Progress: {len(state['processed_indices'])}/{len(all_stories)} stories")
        
        # Minimal delay between batches (only for OpenAI rate limiting)
        if delay > 0 and i + batch_size < len(unprocessed_indices):
            print(f"Waiting {delay}s before next batch...")
            import time
            time.sleep(delay)
    
    print(f"\n{'='*60}")
    print(f"✓ COMPLETE! All {len(all_stories)} stories processed!")
    print(f"{'='*60}")
    
    # Save final beat book
    save_beat_book(beat_book_file, state['refined_beat_book'])
    save_state(state_file, state)
    
    print(f"Beat book saved to: {beat_book_file}")
    if state.get('caroline_county_info'):
        print("✓ Caroline County stats were used as context for OpenAI refinement")
    print(f"Total batches processed: {state['batch_num']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Build an education beat book by iteratively analyzing stories with local Ollama (gemma3:4b) and refining with OpenAI GPT-5.2'
    )
    parser.add_argument(
        '--input',
        default='source_stories.json',
        help='Input JSON file with stories (default: source_stories.json)'
    )
    parser.add_argument(
        '--state',
        default='output_local/beat_book_state.json',
        help='State file to track progress (default: output_local/beat_book_state.json)'
    )
    parser.add_argument(
        '--output',
        default='output_local',
        help='Output directory for batch notes (default: output_local -> output_local/batch_1/notes.md, etc.)'
    )
    parser.add_argument(
        '--refined-output',
        default='output_local/beat_book.md',
        help='Output file for OpenAI refined beat book (default: output_local/beat_book.md)'
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
        default=1,
        help='Seconds to wait between batches (default: 1, mainly for OpenAI rate limiting)'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset state and start from beginning'
    )
    parser.add_argument(
        '--ollama-url',
        default='http://localhost:11434',
        help='Ollama API base URL (default: http://localhost:11434)'
    )
    parser.add_argument(
        '--model',
        default='gemma3:4b',
        help='Ollama model to use (default: gemma3:4b)'
    )
    
    args = parser.parse_args()
    
    # Update Ollama configuration from args
    OLLAMA_BASE_URL = args.ollama_url
    OLLAMA_MODEL = args.model
    
    # Reset state if requested
    if args.reset and Path(args.state).exists():
        Path(args.state).unlink()
        print(f"Removed existing state file: {args.state}")
    
    build_beat_book(
        args.input,
        args.state,
        args.output,  # batch_notes_prefix
        args.refined_output,  # beat_book_file
        batch_size=args.batch_size,
        delay=args.delay
    )
