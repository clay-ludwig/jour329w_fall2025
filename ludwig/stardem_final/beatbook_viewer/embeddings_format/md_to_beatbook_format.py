#!/usr/bin/env python3
"""
Convert a markdown file to beat book JSON format.
Each sentence gets matched against individual sentences from source stories
using semantic similarity matching.
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
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def find_best_match(embedding: list, embeddings_data: list) -> dict:
    """
    Find the most similar sentence from the source stories.
    
    Args:
        embedding: The embedding vector to compare
        embeddings_data: List of articles with sentence embeddings
        
    Returns:
        Dict with match info including similarity score
    """
    best_match = {
        "article_id": None,
        "sentence_text": None,
        "sentence_index": None,
        "similarity": -1.0,
        "article_title": "",
        "article_date": "",
        "article_author": ""
    }
    
    for article in embeddings_data:
        article_id = article.get("article_id", "")
        
        for sentence_data in article.get("sentences", []):
            sent_embedding = sentence_data.get("embedding")
            if sent_embedding is None:
                continue
            
            similarity = cosine_similarity(embedding, sent_embedding)
            
            if similarity > best_match["similarity"]:
                best_match = {
                    "article_id": article_id,
                    "sentence_text": sentence_data.get("text", ""),
                    "sentence_index": sentence_data.get("index", 0),
                    "similarity": similarity,
                    "article_title": article.get("title", ""),
                    "article_date": article.get("date", ""),
                    "article_author": article.get("author", "")
                }
    
    return best_match


def split_into_sentences(text):
    """Split text into sentences using regex."""
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
    Convert a markdown file to beat book JSON format with sentence-level similarity matching.
    """
    md_path = Path(md_file_path)
    
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")
    
    # Read the markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Use the output/ subdirectory for embeddings
    script_dir = Path(__file__).parent
    output_dir = script_dir / 'output'
    
    # Load sentence embeddings
    embeddings_file = output_dir / 'source_stories_embeddings.json'
    if embeddings_file.exists():
        try:
            with open(embeddings_file, 'r', encoding='utf-8') as f:
                embeddings_data = json.load(f)
            total_sents = sum(
                1 for article in embeddings_data 
                for sent in article.get("sentences", []) 
                if sent.get("embedding") is not None
            )
            print(f"✓ Loaded embeddings: {len(embeddings_data)} articles, {total_sents} sentences")
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            sys.exit(1)
    else:
        print(f"Error: source_stories_embeddings.json not found in output/")
        print("Please run generate_story_embeddings.py first.")
        sys.exit(1)
    
    print()

    # Split markdown into lines
    lines = content.split('\n')
    
    # Collect entries to process
    entries_to_process = []
    in_code_block = False
    
    for line in lines:
        if is_code_block_delimiter(line):
            in_code_block = not in_code_block
            entries_to_process.append({"content": line, "needs_embedding": False})
            continue
        
        if in_code_block:
            entries_to_process.append({"content": line, "needs_embedding": False})
            continue
        
        if not line.strip() or is_markdown_heading(line) or is_markdown_list_item(line):
            entries_to_process.append({"content": line, "needs_embedding": False})
        else:
            sentences = split_into_sentences(line)
            if sentences:
                for sentence in sentences:
                    entries_to_process.append({"content": sentence, "needs_embedding": True})
            else:
                entries_to_process.append({"content": line, "needs_embedding": False})
    
    # Count entries needing embeddings
    entries_needing_embeddings = [e for e in entries_to_process if e["needs_embedding"]]
    total_to_embed = len(entries_needing_embeddings)
    print(f"✓ Found {len(entries_to_process)} total entries, {total_to_embed} need embeddings")
    print("Generating embeddings and finding similar sentences...\n")
    
    # Process each entry
    beatbook_data = []
    processed_count = 0
    
    for entry in entries_to_process:
        content_text = entry["content"]
        
        if entry["needs_embedding"] and content_text.strip():
            processed_count += 1
            
            preview = content_text[:50].replace('\n', ' ')
            sys.stdout.write(f"\r[{processed_count}/{total_to_embed}] {preview}..." + " " * 20)
            sys.stdout.flush()
            
            try:
                embedding = get_embedding(content_text)
                match = find_best_match(embedding, embeddings_data)
                
                beatbook_data.append({
                    "content": content_text,
                    "source": match["article_id"] or "",
                    "source_sentence": match["sentence_text"] or "",
                    "source_sentence_index": match["sentence_index"] if match["sentence_index"] is not None else -1,
                    "source_title": match["article_title"],
                    "similarity": round(match["similarity"], 4)
                })
            except Exception as e:
                print(f"\nError: {e}")
                beatbook_data.append({
                    "content": content_text,
                    "source": "",
                    "source_sentence": "",
                    "source_sentence_index": -1,
                    "source_title": "",
                    "similarity": 0.0
                })
        else:
            beatbook_data.append({
                "content": content_text,
                "source": "",
                "source_sentence": "",
                "source_sentence_index": -1,
                "source_title": "",
                "similarity": 0.0
            })
    
    print()
    
    # Determine output path - default to output/ directory
    if output_path is None:
        script_dir = Path(__file__).parent
        output_dir = script_dir / 'output'
        output_path = output_dir / (md_path.stem + '.json')
    else:
        output_path = Path(output_path)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(beatbook_data, f, indent=2, ensure_ascii=False)
    
    # Stats
    high_quality = [e for e in beatbook_data if e.get("similarity", 0) >= 0.5]
    avg_sim = sum(e["similarity"] for e in high_quality) / len(high_quality) if high_quality else 0
    
    print(f"\n✓ Converted {md_path.name} to beat book format")
    print(f"✓ Output: {output_path}")
    print(f"✓ Total entries: {len(beatbook_data)}")
    print(f"✓ High-quality matches (similarity ≥0.5): {len(high_quality)}")
    print(f"✓ Average similarity for high-quality matches: {avg_sim:.4f}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Convert markdown to beat book JSON with sentence-level similarity scoring'
    )
    parser.add_argument('input', help='Input markdown file path')
    parser.add_argument('-o', '--output', help='Output JSON file path', default=None)
    
    args = parser.parse_args()
    
    try:
        markdown_to_beatbook(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
