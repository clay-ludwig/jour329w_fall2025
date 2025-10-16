import json
import subprocess
import time
import argparse
import sys
from pathlib import Path

def extract_metadata(story_title, story_content, schema_prompt, model):
    """Use LLM to extract structured metadata from story title and summary."""
    prompt = f"""
Extract metadata from this news story in JSON format using only the title and summary provided.

Schema to follow:
{schema_prompt}

Story Title: {story_title}
Story Summary: {story_content}

Return only valid JSON with the metadata. If information is not available, use an empty array:
"""
    
    try:
        result = subprocess.run([
            'llm', '-m', model, prompt
        ], capture_output=True, text=True, timeout=30)
        
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
            return {"error": "LLM failed", "stderr": result.stderr}
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description='Add metadata to CNS beat stories using LLM')
    parser.add_argument('--model', required=True, help='LLM model to use (e.g., gpt-4o-mini, claude-3.5-haiku)')
    parser.add_argument('--input', default='story_summaries_elections.json', help='Input JSON file with stories')
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Load your beat stories
    try:
        with open(args.input) as f:
            stories = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input}'")
        print("Make sure to update the --input parameter to match your topic file!")
        return

    # Define your schema prompt based on your beat - CUSTOMIZE THIS!
    schema_prompt = """
    {
      "people": ["Person Name 1", "Person Name 2"],
      "geographic_focus": "Baltimore City",
      "key_institutions": ["Maryland General Assembly", "Department of Environment"],
      "story_category": "breaking news",
      "follow_up_rating": 7,
      "education_level": ["k-12", "higher-ed"],
      "schools_named": ["School Name 1", "School Name 2"],
      "topic_overlap": {
        "Maryland Government & Politics": 8,
        "Federal Government & Politics": 2,
        "Civil & Criminal Justice": 3,
        "Sports": 1,
        "Elections": 4,
        "Health": 2,
        "Arts & Society": 1,
        "Environment": 1,
        "International Affairs": 1,
        "Transportation & Infrastructure": 1,
        "Economy": 2,
        "Immigration": 1,
        "Baltimore": 5,
        "Chesapeake Bay": 1,
        "Housing": 1,
        "Agriculture": 1,
        "Washington D.C.": 1
      }
    }
    
    Instructions:
    - people: Extract names of key people mentioned (officials, educators, students, etc.)
    - geographic_focus: Identify the primary location (specific county/city name, or "statewide" if it covers all of Maryland, or "multiple regions" if it covers several areas)
    - key_institutions: List schools, school districts, universities, education agencies, or organizations mentioned
    - story_category: Classify as one of: "breaking news", "feature", "analysis", "investigation", "opinion" or "other"
    - follow_up_rating: Rate 1-10 how much this story deserves a follow-up (10 = high potential for good upcoming follow-up story, 1 = complete/resolved story)
    - education_level: Array that can include "pre-k", "k-12", "higher-ed", or "general" (use "general" if it applies broadly to education without a specific level)
    - schools_named: List any specific schools mentioned by name (leave empty array if none mentioned)
    - topic_overlap: For EACH of the topics listed, rate 1-10 how much this education story overlaps with that topic (10 = heavy overlap, 1 = minimal/no overlap). Use these definitions:
      * Maryland Government & Politics: Stories primarily about state and local government actions and impacts
      * Federal Government & Politics: Stories primarily about federal government actions and impacts
      * Civil & Criminal Justice: Stories primarily about crime, law enforcement (but not immigration), courts, hate crimes and civil rights
      * Sports: Stories primarily about professional, college or youth sports
      * Elections: Stories primarily about political contests between candidates, voting and political conventions
      * Health: Stories primarily about health, including disease, research and well-being
      * Arts & Society: Stories primarily about culture, including events, concerts and demographics
      * Environment: Stories primarily about environmental regulation, protection and harms, excluding the Chesapeake Bay
      * International Affairs: Stories primarily about events outside the United States, or diplomatic relations between the U.S. and other countries
      * Transportation & Infrastructure: Stories primarily about vehicles, roads, transit, bridges and other public works
      * Economy: Stories primarily about budgets, taxes, spending, consumer prices
      * Immigration: Stories primarily about immigration policy and impacts, including enforcement
      * Baltimore: Stories primarily about the city of Baltimore, including city government
      * Chesapeake Bay: Stories primarily about the Chesapeake Bay, including preservation, fishing/crabbing and recreation
      * Housing: Stories primarily about housing (not explicitly defined but infer from context)
      * Agriculture: Stories primarily about food production and farming
      * Washington D.C.: Stories primarily about the District of Columbia, including city government
    """

    # Process each story
    enhanced_stories = []
    for i, story in enumerate(stories):
        print(f"Processing {i+1}/{len(stories)}: {story['title']}")
        
        metadata = extract_metadata(story['title'], story['content'], schema_prompt, args.model)
    # Process each story
    enhanced_stories = []
    for i, story in enumerate(stories):
        print(f"Processing {i+1}/{len(stories)}: {story['title']}")
        
        metadata = extract_metadata(story['title'], story['summary'], schema_prompt, args.model)
        
        # Add metadata fields as separate columns instead of nested object
        enhanced_story = story.copy()
        
        # If metadata extraction was successful, add each field separately
        if 'error' not in metadata:
            # Add each metadata field as a top-level column
            for key, value in metadata.items():
                # Convert arrays to JSON strings for storage
                if isinstance(value, list):
                    enhanced_story[f'metadata_{key}'] = json.dumps(value)
                else:
                    enhanced_story[f'metadata_{key}'] = value
        else:
            # If there was an error, add error information
            enhanced_story['metadata_error'] = metadata.get('error', 'Unknown error')
            
        enhanced_stories.append(enhanced_story)
        
        # Be respectful to the API
        time.sleep(1)

    # Save the enhanced collection
    with open('enhanced_beat_stories.json', 'w') as f:
        json.dump(enhanced_stories, f, indent=2)

    print(f"Processed {len(enhanced_stories)} stories with metadata")

if __name__ == "__main__":
    main()