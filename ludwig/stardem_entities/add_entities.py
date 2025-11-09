import json
import subprocess
import time
import argparse
import sys
from pathlib import Path
import glob
import re

def extract_entities(story_title, story_content, model):
    """Use LLM to extract named entities (people, places, organizations) from story."""
    
    # Truncate content if it's too long (keep first 2000 characters which is ~400-500 words)
    # This helps avoid timeouts while keeping the most important content
    max_content_length = 2000
    if len(story_content) > max_content_length:
        story_content = story_content[:max_content_length] + "..."
    
    prompt = f"""
Extract named entities from this news story and return them in JSON format.

Extract the following entities:
- people: Array of people mentioned in the story. ALWAYS format as "First (Middle) Last, Title" where the title is DESCRIPTIVE and SPECIFIC enough for someone who hasn't read the article to understand. Include organizational/geographic context in titles when relevant. Examples: "John A. Smith, Mayor of Easton", "Mary Johnson, Talbot County Police Chief", "Dr. Sarah Williams, Superintendent of Caroline County Public Schools", "Tom Brown, Easton resident". Never use vague titles like just "Mayor" or "Town Manager" - always specify which town/organization.

- places: Array of geographic locations mentioned. ALWAYS include both city/town AND state when applicable (e.g., "Easton, Maryland" not just "Easton"). For counties, use format "Talbot County, Maryland". List from most specific to most general. Use full official names consistently.

- organizations: Array of organizations, institutions, companies, or agencies mentioned. Use full official names consistently (e.g., "Talbot County Public Schools" not "TCPS" or "the school system"). Include geographic context when helpful (e.g., "Easton Police Department" not just "Police Department").

IMPORTANT RULES:
- Only include people, places, and organizations that are subjects OF the news story
- Do NOT include news organizations producing the content (e.g., "Star-Democrat", "APGMedia", reporters, photographers)
- Do NOT include the story's author/byline
- Focus on who/what the story is ABOUT, not who wrote or published it
- Maintain consistent formatting within each category
- Every person MUST have a descriptive, specific title/role that includes organizational/geographic context
- Every place should include state when applicable (especially for Maryland locations)

Example output:
{{
  "people": ["John A. Smith, Mayor of Easton", "Mary Johnson, Talbot County Police Chief", "Dr. Sarah Williams, Superintendent of Queen Anne's County Public Schools", "Tom Brown, Centreville resident"],
  "places": ["Easton, Maryland", "Talbot County, Maryland", "Washington D.C.", "Baltimore, Maryland"],
  "organizations": ["Talbot County Public Schools", "Maryland Department of Health", "Easton Police Department", "Queen Anne's County Commissioners"]
}}

Story Title: {story_title}
Story Content: {story_content}

Return only valid JSON with the three arrays. If a category has no entities, use an empty array []:
"""
    
    try:
        result = subprocess.run([
            'llm', '-m', model, prompt
        ], capture_output=True, text=True, timeout=60)  # Increased timeout to 60 seconds
        
        if result.returncode == 0:
            # Parse and validate the JSON response
            response_text = result.stdout.strip()
            # Remove any markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('\n', 1)[0]
            
            metadata = json.loads(response_text)
            return metadata
        else:
            # Return more detailed error information
            stderr_msg = result.stderr[:200] if result.stderr else "No error message"
            return {"error": "LLM failed", "stderr": stderr_msg, "returncode": result.returncode}
    except subprocess.TimeoutExpired:
        return {"error": "LLM request timed out after 60 seconds"}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {str(e)}", "response": result.stdout[:200] if 'result' in locals() else "No response"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(description='Add entity metadata (people, places, organizations) to Star-Democrat stories using LLM')
    parser.add_argument('--model', required=True, help='LLM model to use (e.g., groq/openai/gpt-oss-120b)')
    parser.add_argument('--input', default='stardem_sample.json', help='Input JSON file with stories')
    parser.add_argument('--version', type=int, help='Version number for output file (if not provided, will auto-increment)')
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Determine version number
    if args.version is None:
        # Find existing version files and auto-increment
        existing_files = glob.glob('stories_with_entities_v*.json')
        if existing_files:
            # Extract version numbers from filenames
            version_numbers = []
            for filename in existing_files:
                match = re.search(r'_v(\d+)\.json$', filename)
                if match:
                    version_numbers.append(int(match.group(1)))
            version = max(version_numbers) + 1 if version_numbers else 1
        else:
            version = 1
        print(f"Auto-detected version number: {version}")
    else:
        version = args.version
        print(f"Using specified version number: {version}")
    
    # Load Star-Democrat stories
    try:
        with open(args.input) as f:
            all_stories = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input}'")
        print("Make sure the input file exists in the current directory!")
        return
    
    # Filter out unwanted story types
    stories = []
    filtered_out = []
    
    for story in all_stories:
        title = story.get('title', '')
        content = story.get('content', '')
        
        # Skip stories based on title patterns
        if 'TODAY IN HISTORY' in title.upper():
            filtered_out.append(f"{title} (TODAY IN HISTORY)")
            continue
        if 'RELIGION CALENDAR' in title.upper():
            filtered_out.append(f"{title} (RELIGION CALENDAR)")
            continue
        if 'MID-SHORE CALENDAR' in title.upper():
            filtered_out.append(f"{title} (MID-SHORE CALENDAR)")
            continue
        
        # Skip stories based on section
        if 'Section: Calendar' in content or 'Section: Columns' in content or 'Section: Letters' in content:
            filtered_out.append(f"{title} (Calendar/Columns/Letters section)")
            continue
        
        stories.append(story)
    
    print(f"\nLoaded {len(all_stories)} stories from {args.input}")
    print(f"Filtered out {len(filtered_out)} stories (calendars, columns, history, letters)")
    print(f"Processing {len(stories)} stories\n")
    
    if filtered_out and len(filtered_out) <= 10:
        print("Filtered stories:")
        for item in filtered_out:
            print(f"  - {item}")
        print()

    # Process each story
    enhanced_stories = []
    errors = []
    for i, story in enumerate(stories):
        print(f"Processing {i+1}/{len(stories)}: {story.get('title', 'Untitled')[:60]}...")
        
        # Extract entities from the story
        # Use 'summary' field if available, otherwise use 'content'
        story_content = story.get('summary', story.get('content', ''))
        
        if not story_content:
            print(f"  ⚠️  Warning: No content found for story")
            entities = {"error": "No content available"}
        else:
            entities = extract_entities(story.get('title', ''), story_content, args.model)
        
        # Add entity fields to the story
        enhanced_story = story.copy()
        
        # If entity extraction was successful, add each field
        if 'error' not in entities:
            enhanced_story['people'] = entities.get('people', [])
            enhanced_story['places'] = entities.get('places', [])
            enhanced_story['organizations'] = entities.get('organizations', [])
            print(f"  ✓ Found {len(enhanced_story['people'])} people, {len(enhanced_story['places'])} places, {len(enhanced_story['organizations'])} orgs")
        else:
            # If there was an error, add empty arrays and error information
            enhanced_story['people'] = []
            enhanced_story['places'] = []
            enhanced_story['organizations'] = []
            enhanced_story['entity_extraction_error'] = entities.get('error', 'Unknown error')
            errors.append(f"Story {i+1}: {entities.get('error', 'Unknown error')[:100]}")
            print(f"  ✗ Error: {entities.get('error', 'Unknown error')[:80]}")
            # Print stderr if available for debugging
            if 'stderr' in entities:
                print(f"     stderr: {entities['stderr'][:200]}")
            if 'returncode' in entities:
                print(f"     return code: {entities['returncode']}")
            
        enhanced_stories.append(enhanced_story)
        
        # Be respectful to the API
        time.sleep(1)

    # Save the enhanced stories with entities
    output_filename = f'stories_with_entities_v{version}.json'
    with open(output_filename, 'w') as f:
        json.dump(enhanced_stories, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Processed {len(enhanced_stories)} stories with entity extraction")
    print(f"Output saved to: {output_filename}")
    
    # Print error summary if there were any
    if errors:
        print(f"\n⚠️  {len(errors)} stories had errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    # Count successful extractions
    successful = sum(1 for s in enhanced_stories if 'entity_extraction_error' not in s)
    print(f"\n✓ Successfully extracted entities from {successful}/{len(enhanced_stories)} stories")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()