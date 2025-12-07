#!/usr/bin/env python3
"""
Convert a markdown file to beat book JSON format (GRANULAR version with COMPOSITE scoring).
Each sentence gets matched against individual sentences from source stories,
with a composite score that combines sentence-level and article-level similarity.
"""

import json
import sys
import argparse
import re
import math
import urllib.request
import urllib.error
from pathlib import Path


# Weighting for composite score (adjustable)
SENTENCE_WEIGHT = 0.7  # How much weight to give sentence-level similarity
ARTICLE_WEIGHT = 0.3   # How much weight to give article-level similarity


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


def find_best_match_composite(embedding: list, granular_data: list, article_embeddings: dict) -> dict:
    """
    Find the most similar sentence using a composite score that combines
    sentence-level and article-level similarity.
    
    Args:
        embedding: The embedding vector to compare
        granular_data: List of articles with sentence embeddings
        article_embeddings: Dict mapping article_id to full article embedding
        
    Returns:
        Dict with match info including composite score
    """
    best_match = {
        "article_id": None,
        "sentence_text": None,
        "sentence_index": None,
        "sentence_similarity": -1.0,
        "article_similarity": -1.0,
        "composite_similarity": -1.0,
        "article_title": "",
        "article_date": "",
        "article_author": ""
    }
    
    for article in granular_data:
        article_id = article.get("article_id", "")
        
        # Get article-level similarity (if available)
        article_embedding = article_embeddings.get(article_id)
        article_sim = 0.0
        if article_embedding is not None:
            article_sim = cosine_similarity(embedding, article_embedding)
        
        for sentence_data in article.get("sentences", []):
            sent_embedding = sentence_data.get("embedding")
            if sent_embedding is None:
                continue
            
            # Sentence-level similarity
            sentence_sim = cosine_similarity(embedding, sent_embedding)
            
            # Composite score: weighted average of sentence and article similarity
            composite_sim = (SENTENCE_WEIGHT * sentence_sim) + (ARTICLE_WEIGHT * article_sim)
            
            if composite_sim > best_match["composite_similarity"]:
                best_match = {
                    "article_id": article_id,
                    "sentence_text": sentence_data.get("text", ""),
                    "sentence_index": sentence_data.get("index", 0),
                    "sentence_similarity": sentence_sim,
                    "article_similarity": article_sim,
                    "composite_similarity": composite_sim,
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
    Convert a markdown file to beat book JSON format with composite scoring.
    """
    md_path = Path(md_file_path)
    
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_file_path}")
    
    # Read the markdown file
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    script_dir = Path(__file__).parent
    
    # Load granular embeddings (sentence-level)
    granular_file = script_dir / 'source_stories_embeddings_granular.json'
    if granular_file.exists():
        try:
            with open(granular_file, 'r', encoding='utf-8') as f:
                granular_data = json.load(f)
            total_sents = sum(
                1 for article in granular_data 
                for sent in article.get("sentences", []) 
                if sent.get("embedding") is not None
            )
            print(f"✓ Loaded granular embeddings: {len(granular_data)} articles, {total_sents} sentences")
        except Exception as e:
            print(f"Error loading granular embeddings: {e}")
            sys.exit(1)
    else:
        print(f"Error: source_stories_embeddings_granular.json not found")
        print("Please run generate_embeddings_granular.py first.")
        sys.exit(1)
    
    # Load article-level embeddings (non-granular)
    article_file = script_dir / 'source_stories_embeddings.json'
    article_embeddings = {}
    if article_file.exists():
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
            for story in article_data:
                if story.get("embedding") is not None:
                    article_embeddings[story.get("article_id", "")] = story["embedding"]
            print(f"✓ Loaded article-level embeddings: {len(article_embeddings)} articles")
        except Exception as e:
            print(f"Warning: Could not load article embeddings: {e}")
            print("  Proceeding with sentence-level similarity only.")
    else:
        print("⚠ Article-level embeddings not found (source_stories_embeddings.json)")
        print("  Proceeding with sentence-level similarity only.")
    
    print(f"\n📊 Composite scoring weights: {SENTENCE_WEIGHT*100:.0f}% sentence + {ARTICLE_WEIGHT*100:.0f}% article\n")

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
                match = find_best_match_composite(embedding, granular_data, article_embeddings)
                
                beatbook_data.append({
                    "content": content_text,
                    "source": match["article_id"] or "",
                    "source_sentence": match["sentence_text"] or "",
                    "source_sentence_index": match["sentence_index"] if match["sentence_index"] is not None else -1,
                    "source_title": match["article_title"],
                    "similarity": round(match["composite_similarity"], 4),
                    "sentence_similarity": round(match["sentence_similarity"], 4),
                    "article_similarity": round(match["article_similarity"], 4)
                })
            except Exception as e:
                print(f"\nError: {e}")
                beatbook_data.append({
                    "content": content_text,
                    "source": "",
                    "source_sentence": "",
                    "source_sentence_index": -1,
                    "source_title": "",
                    "similarity": 0.0,
                    "sentence_similarity": 0.0,
                    "article_similarity": 0.0
                })
        else:
            beatbook_data.append({
                "content": content_text,
                "source": "",
                "source_sentence": "",
                "source_sentence_index": -1,
                "source_title": "",
                "similarity": 0.0,
                "sentence_similarity": 0.0,
                "article_similarity": 0.0
            })
    
    print()
    
    # Determine output path
    if output_path is None:
        output_path = md_path.with_stem(md_path.stem + '_granular').with_suffix('.json')
    else:
        output_path = Path(output_path)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(beatbook_data, f, indent=2, ensure_ascii=False)
    
    # Stats
    high_quality = [e for e in beatbook_data if e.get("similarity", 0) >= 0.5]
    avg_sim = sum(e["similarity"] for e in high_quality) / len(high_quality) if high_quality else 0
    avg_sent = sum(e["sentence_similarity"] for e in high_quality) / len(high_quality) if high_quality else 0
    avg_art = sum(e["article_similarity"] for e in high_quality) / len(high_quality) if high_quality else 0
    
    print(f"\n✓ Converted {md_path.name} to granular beat book format")
    print(f"✓ Output: {output_path}")
    print(f"✓ Total entries: {len(beatbook_data)}")
    print(f"✓ High-quality matches (composite ≥0.5): {len(high_quality)}")
    print(f"\n📊 Average scores for high-quality matches:")
    print(f"   Composite: {avg_sim:.4f}")
    print(f"   Sentence:  {avg_sent:.4f}")
    print(f"   Article:   {avg_art:.4f}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Convert markdown to beat book JSON with composite sentence+article similarity scoring'
    )
    parser.add_argument('input', help='Input markdown file path')
    parser.add_argument('-o', '--output', help='Output JSON file path', default=None)
    parser.add_argument(
        '--sentence-weight', 
        type=float, 
        default=0.7,
        help='Weight for sentence-level similarity (0-1, default: 0.7)'
    )
    parser.add_argument(
        '--article-weight',
        type=float,
        default=0.3, 
        help='Weight for article-level similarity (0-1, default: 0.3)'
    )
    
    args = parser.parse_args()
    
    # Update weights if provided
    global SENTENCE_WEIGHT, ARTICLE_WEIGHT
    SENTENCE_WEIGHT = args.sentence_weight
    ARTICLE_WEIGHT = args.article_weight
    
    # Normalize weights to sum to 1
    total = SENTENCE_WEIGHT + ARTICLE_WEIGHT
    if total != 1.0:
        SENTENCE_WEIGHT /= total
        ARTICLE_WEIGHT /= total
    
    try:
        markdown_to_beatbook(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
