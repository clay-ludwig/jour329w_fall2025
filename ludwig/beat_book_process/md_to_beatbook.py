#!/usr/bin/env python3
"""
Convert a markdown file to beat book JSON format.
Each line becomes a separate entry in the JSON array.
Uses Ollama embeddings to find the most similar source story for each entry.
"""

import json
import sys
import argparse
import re
import math
import urllib.request
import urllib.error
from pathlib import Path


def get_embedding(text: str, model: str = "embeddinggemma:latest") -> list:
    """
    Get an embedding for the given text using Ollama's embedding API.
    
    Args:
        text: The text to embed
        model: The Ollama model to use for embeddings
        
    Returns:
        A list of floats representing the embedding vector
    """
    url = "http://localhost:11434/api/embed"
    data = json.dumps({
        "model": model,
        "input": text
    }).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    return result["embeddings"][0]


def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score between -1 and 1
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def find_most_similar_story(embedding: list, stories_with_embeddings: list) -> tuple:
    """
    Find the most similar story to the given embedding.
    
    Args:
        embedding: The embedding vector to compare
        stories_with_embeddings: List of stories with 'embedding' and 'article_id' fields
        
    Returns:
        Tuple of (article_id, similarity_score)
    """
    best_match = None
    best_similarity = -1.0
    
    for story in stories_with_embeddings:
        story_embedding = story.get("embedding")
        if story_embedding is None:
            continue
        
        similarity = cosine_similarity(embedding, story_embedding)
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = story.get("article_id", "")
    
    return best_match, best_similarity


def split_into_sentences(text):
    """
    Split text into sentences using regex.
    Handles common abbreviations and edge cases.
    """
    # Pattern to split on sentence boundaries
    # Matches periods, question marks, exclamation marks followed by space or end of string
    # Handles common abbreviations like Mr., Mrs., Dr., etc.
    sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+'
    
    sentences = re.split(sentence_pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def is_markdown_heading(line):
    """Check if a line is a markdown heading."""
    return re.match(r'^#{1,6}\s+', line.strip()) is not None


def is_markdown_list_item(line):
    """Check if a line is a markdown list item."""
    return re.match(r'^\s*[-*+]\s+', line.strip()) or re.match(r'^\s*\d+\.\s+', line.strip())


def is_code_block_delimiter(line):
    """Check if a line is a code block delimiter."""
    return line.strip().startswith('```')


def markdown_to_beatbook(md_file_path, output_path=None):
    """
    Convert a markdown file to beat book JSON format.
    
    Args:
        md_file_path: Path to the input markdown file
        output_path: Path to the output JSON file (optional)
    
    Returns:
        Path to the created JSON file
    """
    md_path = Path(md_file_path)
    
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")
    
    # Read the markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Load source stories with embeddings
    script_dir = Path(__file__).parent
    stories_path = script_dir / 'source_stories_embeddings.json'
    stories_with_embeddings = []
    
    if stories_path.exists():
        try:
            with open(stories_path, 'r', encoding='utf-8') as f:
                stories_with_embeddings = json.load(f)
            # Filter to only stories with embeddings
            stories_with_embeddings = [s for s in stories_with_embeddings if s.get('embedding') is not None]
            print(f"✓ Loaded {len(stories_with_embeddings)} stories with embeddings from source_stories_embeddings.json")
        except Exception as e:
            print(f"Error: Could not load source_stories_embeddings.json: {e}")
            sys.exit(1)
    else:
        print(f"Error: source_stories_embeddings.json not found at {stories_path}")
        print("Please run generate_embeddings.py first to create the embeddings file.")
        sys.exit(1)

    # Split into lines
    lines = content.split('\n')
    
    # Create JSON structure
    beatbook_data = []
    in_code_block = False
    
    # First, collect all content entries that need embeddings
    entries_to_process = []
    
    for line in lines:
        # Check for code block delimiters
        if is_code_block_delimiter(line):
            in_code_block = not in_code_block
            entries_to_process.append({
                "content": line,
                "needs_embedding": False
            })
            continue
        
        # If we're in a code block, don't split into sentences
        if in_code_block:
            entries_to_process.append({
                "content": line,
                "needs_embedding": False
            })
            continue
        
        # Empty lines, headings, and list items are kept as-is (no embedding needed)
        if not line.strip() or is_markdown_heading(line) or is_markdown_list_item(line):
            entries_to_process.append({
                "content": line,
                "needs_embedding": False
            })
        else:
            # Regular paragraph text - split into sentences
            sentences = split_into_sentences(line)
            
            if sentences:
                for sentence in sentences:
                    entries_to_process.append({
                        "content": sentence,
                        "needs_embedding": True  # These need embeddings for similarity matching
                    })
            else:
                entries_to_process.append({
                    "content": line,
                    "needs_embedding": False
                })
    
    # Count entries that need embeddings
    entries_needing_embeddings = [e for e in entries_to_process if e["needs_embedding"]]
    total_to_embed = len(entries_needing_embeddings)
    print(f"✓ Found {len(entries_to_process)} total entries, {total_to_embed} need embeddings")
    print("Generating embeddings and finding similar stories...")
    print()
    
    # Process each entry
    processed_count = 0
    for i, entry in enumerate(entries_to_process, 1):
        content_text = entry["content"]
        
        if entry["needs_embedding"] and content_text.strip():
            processed_count += 1
            # Show progress
            preview = content_text[:50].replace('\n', ' ')
            sys.stdout.write(f"\r[{processed_count}/{total_to_embed}] Processing: {preview}..." + " " * 20)
            sys.stdout.flush()
            
            try:
                # Generate embedding for this content
                embedding = get_embedding(content_text)
                
                # Find most similar story
                article_id, similarity = find_most_similar_story(embedding, stories_with_embeddings)
                
                beatbook_data.append({
                    "content": content_text,
                    "source": article_id if article_id else "",
                    "similarity": round(similarity, 4)
                })
            except Exception as e:
                print(f"\nError generating embedding: {e}")
                beatbook_data.append({
                    "content": content_text,
                    "source": "",
                    "similarity": 0.0
                })
        else:
            # No embedding needed for this entry
            beatbook_data.append({
                "content": content_text,
                "source": "",
                "similarity": 0.0
            })
    
    print()  # New line after progress
    
    # Determine output path
    if output_path is None:
        output_path = md_path.with_suffix('.json')
    else:
        output_path = Path(output_path)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(beatbook_data, f, indent=2, ensure_ascii=False)
    
    # Calculate stats
    entries_with_source = [e for e in beatbook_data if e.get("source")]
    avg_similarity = 0.0
    if entries_with_source:
        avg_similarity = sum(e.get("similarity", 0) for e in entries_with_source) / len(entries_with_source)
    
    print(f"\n✓ Converted {md_path.name} to beat book format")
    print(f"✓ Output: {output_path}")
    print(f"✓ Total entries: {len(beatbook_data)}")
    print(f"✓ Entries with source matches: {len(entries_with_source)}")
    print(f"✓ Average similarity score: {avg_similarity:.4f}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Convert markdown file to beat book JSON format with semantic source matching'
    )
    parser.add_argument(
        'input',
        help='Input markdown file path'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: same name as input with .json extension)',
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        markdown_to_beatbook(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
