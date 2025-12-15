#!/usr/bin/env python3
"""
Extract only title and content fields from source_stories.json and summarize content using local Ollama model
"""
import json
import subprocess
import argparse


SUMMARIZE_PROMPT = """Summarize this article into a highly condensed version that retains all key information, conflicts, people, places, organizations, dates, numbers, and important details. Lean toward keeping information rather than cutting it to ensure nothing important is lost, but simultaneously write as concisely as possible. Remove redundant or unnecessary text, but preserve all substantive content.

Article:
{content}

Provide only the summary, no preamble or explanation."""


def summarize_content(content):
    """
    Summarize content using Ollama local model.
    
    Args:
        content: The article content to summarize
        
    Returns:
        Summarized content
    """
    prompt = SUMMARIZE_PROMPT.format(content=content)
    
    try:
        result = subprocess.run(
            ['ollama', 'run', 'gpt-oss:20b', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error summarizing content: {e}")
        print(f"stderr: {e.stderr}")
        return content  # Return original content if summarization fails


def extract_fields(input_file, output_file, limit=None):
    """
    Read JSON file, extract only title and content fields, and summarize content.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        limit: Optional limit on number of entries to process
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Apply limit if specified
    if limit:
        data = data[:limit]
        print(f"Processing first {limit} entries...")
    
    # Extract only the desired fields and summarize
    filtered_data = []
    for i, entry in enumerate(data, 1):
        print(f"Processing entry {i}/{len(data)}: {entry.get('title', 'Untitled')}")
        
        summarized_content = summarize_content(entry.get('content', ''))
        
        filtered_entry = {
            'title': entry.get('title'),
            'content': summarized_content
        }
        filtered_data.append(filtered_entry)
    
    # Write to output file (minified)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, separators=(',', ':'), ensure_ascii=False)
    
    print(f"\nProcessed {len(filtered_data)} entries")
    print(f"Output written to {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and summarize stories from JSON using local Ollama model')
    parser.add_argument('--limit', type=int, help='Limit number of entries to process')
    args = parser.parse_args()
    
    input_file = 'source_stories.json'
    output_file = 'source_stories_filtered.json'
    
    extract_fields(input_file, output_file, limit=args.limit)
