import json
import subprocess
import time
import argparse
import sys
from pathlib import Path
import glob
import re

def screen_education_relevance(story_title, story_content, classification_score):
    """Use a fast LLM to screen whether a story is truly centered on education topics."""
    
    prompt = f"""
Evaluate whether this news story is CENTERED on education as its primary focus.

CONTEXT: This story was previously classified as "Education" with a confidence score of {classification_score}. However, this score should be taken with a grain of salt - some stories may mention education tangentially but not be primarily about educational institutions, events, policies, or programs.

CRITERIA FOR TRUE EDUCATION STORIES:
A story should be considered CENTERED on education if its primary focus is:
- K-12 schools, colleges, or universities (operations, policies, events, achievements)
- School boards, education administrators, or education policy decisions
- Teachers, students, or educational programs as the main subject
- Educational initiatives, curriculum changes, or academic outcomes
- School facilities, funding, or educational resources
- Student activities where the educational context is central (academic competitions, school programs)

SHOULD BE EXCLUDED:
- Stories where education is only mentioned in passing or as background context
- Youth programs (like 4-H, scouts, sports leagues) that are primarily about youth development, agriculture, or recreation rather than formal education
- Stories primarily about individuals where their education background is just biographical detail
- Community events or library programs that aren't specifically educational in nature
- Stories where the main focus is local government, business, or another topic, even if education is mentioned

Story Title: {story_title}
Classification Score: {classification_score}

INSTRUCTIONS: Respond with ONLY a JSON object in this exact format:
{{
  "is_education_centered": true or false,
  "reasoning": "Brief explanation (1-2 sentences) of why this story is or isn't centered on education"
}}

Respond with valid JSON only, no other text:
"""
    
    try:
        # Use the faster 20b model for screening
        result = subprocess.run([
            'llm', '-m', 'groq/openai/gpt-oss-20b', prompt
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response_text = result.stdout.strip()
            # Remove any markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('\n', 1)[1]
                response_text = response_text.rsplit('\n', 1)[0]
            
            screening_result = json.loads(response_text)
            return screening_result
        else:
            # If screening fails, default to including the story
            return {"is_education_centered": True, "reasoning": "Screening model failed, defaulting to include"}
    except subprocess.TimeoutExpired:
        return {"is_education_centered": True, "reasoning": "Screening timed out, defaulting to include"}
    except json.JSONDecodeError as e:
        return {"is_education_centered": True, "reasoning": "Screening JSON parse failed, defaulting to include"}
    except Exception as e:
        return {"is_education_centered": True, "reasoning": f"Screening error: {str(e)}, defaulting to include"}

def extract_entities(story_title, story_content, model):
    """Use LLM to extract named entities (people, places, organizations) from education news stories."""
    
    prompt = f"""
Extract named entities from this EDUCATION news story and return them in JSON format.

CONTEXT: This story is from the Education beat covering K-12 schools, colleges, school boards, education policy, and education-related news in Maryland's Eastern Shore region. Focus on identifying the key people, institutions, and locations that are central to the educational story being told.

Extract the following entities:

- people: Array of people mentioned in the story. ALWAYS format as "First (Middle) Last, Title/Role" where the title is DESCRIPTIVE and SPECIFIC to education context. For education stories, prioritize:
  * School administrators: Include their specific role AND the school/district (e.g., "Dr. Jane Smith, Superintendent of Talbot County Public Schools", "John Davis, Principal of Easton High School")
  * School board members: Include their district/position (e.g., "Sarah Johnson, Talbot County Board of Education President", "Mike Williams, Queen Anne's County Board of Education District 3 member")
  * Teachers/Staff: Include subject/role and school when mentioned (e.g., "Emily Brown, Math Teacher at North Caroline High School", "Robert Lee, Athletic Director at Kent Island High School")
  * Students: Include school and grade/year when mentioned (e.g., "Amanda Chen, Easton High School senior", "Tyler Robinson, Talbot County student")
  * Parents: Include community context (e.g., "Lisa Martinez, Talbot County parent")
  * Education officials: Include agency/organization (e.g., "Karen Edwards, Maryland State Department of Education spokesperson")
  Never use vague titles - always specify the school, district, or organization.

- places: Array of geographic locations mentioned. Focus on school-relevant locations:
  * Schools: Use full official names (e.g., "Easton High School", "Chapel District Elementary School", "University of Maryland")
  * Cities/Towns: ALWAYS include state (e.g., "Easton, Maryland", "Cambridge, Maryland")
  * Counties: Use format "Talbot County, Maryland"
  * School districts are organizations, not places
  List from most specific to most general.

- organizations: Array of education-related organizations, institutions, and agencies mentioned. For education stories, focus on:
  * School systems/districts: Use full official names (e.g., "Talbot County Public Schools", "Queen Anne's County Public Schools", "Caroline County Public Schools")
  * School boards: (e.g., "Talbot County Board of Education", "Dorchester County Board of Education")
  * Schools as institutions: When referenced as organizations (e.g., "Easton Elementary School", "North Caroline High School")
  * Educational agencies: (e.g., "Maryland State Department of Education", "Maryland State Board of Education")
  * Student organizations: (e.g., "National Honor Society", "Student Government Association")
  * Educational programs: When named (e.g., "Blueprint for Maryland's Future", "Career and Technical Education program")
  * PTAs and parent groups: (e.g., "Easton Elementary PTA")
  * Educational support organizations: (e.g., "Maryland Association of Boards of Education")
  Do NOT abbreviate - use full official names consistently.

IMPORTANT RULES FOR EDUCATION STORIES:
- Only include people, places, and organizations that are subjects OF the news story
- Do NOT include news organizations, reporters, or photographers (e.g., "Star-Democrat", "APGMedia")
- Do NOT include the story's author/byline
- Focus on the educational entities central to the story
- Prioritize school/district names, key education officials, and students/parents directly involved
- Maintain consistent naming: always use full official names for schools and districts
- For people, ensure their education role/connection is clear in their title

Example output for education stories:
{{
  "people": ["Dr. Kelly Griffith, Superintendent of Talbot County Public Schools", "Susan Delean-Botkin, Talbot County Board of Education President", "Emily Jackson, Talbot County Board of Education Vice President", "Sarah Miller, Easton High School Teacher", "Amanda Roberts, North Caroline High School senior"],
  "places": ["Easton, Maryland", "Talbot County, Maryland", "Easton High School", "Chapel District Elementary School", "University of Maryland, College Park"],
  "organizations": ["Talbot County Public Schools", "Talbot County Board of Education", "Maryland State Department of Education", "Easton High School", "Blueprint for Maryland's Future", "Career and Technical Education program"]
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
    parser = argparse.ArgumentParser(description='Add entity metadata (people, places, organizations) to education stories from Star-Democrat using LLM')
    parser.add_argument('--model', required=True, help='LLM model to use (e.g., groq/openai/gpt-oss-120b)')
    parser.add_argument('--input', default='topic_stories.json', help='Input JSON file with stories (default: topic_stories.json)')
    parser.add_argument('--version', type=int, help='Version number for output file (if not provided, will auto-increment)')
    parser.add_argument('--limit', type=int, help='Limit the number of stories to process (useful for testing)')
    
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
    
    # Apply limit if specified
    if args.limit and args.limit < len(stories):
        print(f"Limiting processing to first {args.limit} stories (--limit argument)")
        stories = stories[:args.limit]
    
    print(f"Processing {len(stories)} stories\n")
    
    if filtered_out and len(filtered_out) <= 10:
        print("Filtered stories:")
        for item in filtered_out:
            print(f"  - {item}")
        print()

    # Determine output filename
    output_filename = f'stories_with_entities_v{version}.json'
    
    # Initialize or load existing results
    if Path(output_filename).exists():
        print(f"Found existing output file {output_filename}, loading previous results...")
        with open(output_filename) as f:
            enhanced_stories = json.load(f)
        print(f"Loaded {len(enhanced_stories)} previously processed stories\n")
    else:
        enhanced_stories = []
        print(f"Starting fresh with new output file: {output_filename}\n")

    # Process each story
    errors = []
    screened_out = []
    starting_count = len(enhanced_stories)
    
    for i, story in enumerate(stories):
        # Skip if already processed (in case we're resuming)
        if i < starting_count:
            continue
            
        print(f"Processing {i+1}/{len(stories)}: {story.get('title', 'Untitled')[:60]}...")
        
        # Get story content
        story_content = story.get('summary', story.get('content', ''))
        
        if not story_content:
            print(f"  ⚠️  Warning: No content found for story")
            # Skip stories with no content
            continue
        
        # First, screen the story to see if it's truly education-centered
        classification_score = story.get('llm_classification', {}).get('score', 0.0)
        screening = screen_education_relevance(story.get('title', ''), story_content, classification_score)
        
        if not screening.get('is_education_centered', True):
            print(f"  ⊘ Screened out: {screening.get('reasoning', 'Not education-centered')}")
            screened_out.append({
                'title': story.get('title', 'Untitled'),
                'reasoning': screening.get('reasoning', 'Not education-centered'),
                'original_score': classification_score
            })
            # Skip entity extraction for this story
            continue
        else:
            print(f"  ✓ Passed screening: {screening.get('reasoning', 'Education-centered')}")
        
        # Extract entities from the story
        entities = extract_entities(story.get('title', ''), story_content, args.model)
        
        # Add entity fields to the story
        enhanced_story = story.copy()
        
        # Add screening info
        enhanced_story['education_screening'] = screening
        
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
        
        # Save after each story is processed (incremental save)
        with open(output_filename, 'w') as f:
            json.dump(enhanced_stories, f, indent=2)
        
        # Be respectful to the API
        time.sleep(1)

    # Final summary
    print(f"\n{'='*60}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total stories loaded: {len(all_stories)}")
    print(f"Filtered out (calendars, columns, etc.): {len(filtered_out)}")
    if starting_count > 0:
        print(f"Previously processed: {starting_count}")
        print(f"Newly processed in this run: {len(enhanced_stories) - starting_count}")
    print(f"Screened out (not education-centered): {len(screened_out)}")
    print(f"Total successfully processed with entities: {len(enhanced_stories)}")
    print(f"\nOutput saved to: {output_filename}")
    print(f"(File is saved incrementally after each story)")
    
    # Print screened out stories summary
    if screened_out:
        print(f"\n⊘ {len(screened_out)} stories screened out as not education-centered:")
        for item in screened_out[:15]:  # Show first 15
            print(f"  - {item['title'][:70]}")
            print(f"    Reason: {item['reasoning']}")
            print(f"    Original score: {item['original_score']}")
        if len(screened_out) > 15:
            print(f"  ... and {len(screened_out) - 15} more screened out stories")
    
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