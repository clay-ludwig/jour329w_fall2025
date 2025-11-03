#!/usr/bin/env python3
"""
Star-Democrat Topic Classification Script
Option 1: Let the LLM Decide

This script reads Star-Democrat stories from a JSON file and uses an LLM
to classify each story into a single topic category. The LLM determines
the topics based on story content, creating consistent topic names.
"""

import json
import subprocess
import sys
from pathlib import Path


def classify_story_with_llm(story, model="groq/meta-llama/llama-4-scout-17b-16e-instruct"):
    """
    Use the LLM to classify a single story into a topic.
    
    Args:
        story: Dictionary containing story data with 'title' and 'content'
        model: The LLM model to use for classification
    
    Returns:
        str: The topic assigned by the LLM
    """
    prompt = f"""Analyze this news story and assign it to a single BROAD topic category.

IMPORTANT: Choose a general, broad topic category, NOT specific subjects. For example:
- Use "Sports" not "Baseball" or "Lacrosse"
- Use "History" not "Harriet Tubman" or "Civil War"
- Use "Education" not specific school names
- Use "Local Government" not specific official names
- Use "Crime" not specific crime types
- Use "Business" not specific business names

Choose a 1-2 word broad topic that represents the general category this story belongs to.
Be consistent - reuse the same topic names across similar stories. Think about what section of a newspaper this would appear in.

Title: {story['title']}
Content: {story['content']}

Return only the broad topic category name as a single string."""

    try:
        # Call the llm command using subprocess
        result = subprocess.run(
            ["uv", "run", "llm", "-m", model],
            input=prompt,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Get the topic from the output and clean it
        topic = result.stdout.strip()
        return topic
    
    except subprocess.CalledProcessError as e:
        print(f"Error calling LLM: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return "Unknown"
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return "Unknown"


def get_next_version_number():
    """
    Find the next available version number for output files.
    
    Returns:
        int: The next version number to use
    """
    current_dir = Path(".")
    existing_files = list(current_dir.glob("stardem_topics_classified_v*.json"))
    
    if not existing_files:
        return 1
    
    # Extract version numbers from existing files
    version_numbers = []
    for file in existing_files:
        try:
            # Extract number from filename like "stardem_topics_classified_v3.json"
            version_str = file.stem.split("_v")[-1]
            version_numbers.append(int(version_str))
        except (ValueError, IndexError):
            continue
    
    return max(version_numbers) + 1 if version_numbers else 1


def main():
    """Main function to process all stories and classify them."""
    
    # Define file paths
    input_file = Path("stardem_sample.json")
    
    # Get the next version number
    version = get_next_version_number()
    output_file = Path(f"stardem_topics_classified_v{version}.json")
    
    print(f"Output will be saved to: {output_file}\n")
    
    # Check if input file exists
    if not input_file.exists():
        print(f"Error: {input_file} not found!", file=sys.stderr)
        print("Please make sure stardem_sample.json is in the current directory.")
        sys.exit(1)
    
    # Load the stories
    print(f"Loading stories from {input_file}...")
    with open(input_file, 'r') as f:
        stories = json.load(f)
    
    print(f"Found {len(stories)} stories to classify\n")
    
    # Process each story
    classified_stories = []
    for i, story in enumerate(stories, 1):
        print(f"Processing story {i}/{len(stories)}: {story['title'][:60]}...")
        
        # Classify the story
        topic = classify_story_with_llm(story)
        
        # Add the topic to the story
        story_with_topic = story.copy()
        story_with_topic['topic'] = topic
        classified_stories.append(story_with_topic)
        
        print(f"  → Topic: {topic}\n")
    
    # Save the classified stories
    print(f"Saving classified stories to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(classified_stories, f, indent=2)
    
    print(f"\nDone! Classified {len(classified_stories)} stories.")
    print(f"Results saved to {output_file}")
    
    # Print topic summary
    print("\n" + "="*60)
    print("TOPIC SUMMARY")
    print("="*60)
    topic_counts = {}
    for story in classified_stories:
        topic = story['topic']
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{topic}: {count} stories")


if __name__ == "__main__":
    main()
