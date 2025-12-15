#!/usr/bin/env python3
"""
Extract only title and content fields from source_stories.json and summarize content using local Ollama model.
Now uses llama3.2:13b and logs all errors both to console and an external error_log.txt file.
"""

import json
import subprocess
import argparse
import traceback

ERROR_LOG = []  # Collect all errors globally


SUMMARIZE_PROMPT = """Summarize this article in 2-5 concise sentences, preserving only the main points, key names, dates, and places. Avoid repeating details or extra commentary. It's fine if your sentence structure isn't perfectly readable as long as it communicates the specific information perfectly.

Article:
{content}

Provide only the summary, no preamble or explanation."""


def log_error(msg):
    """Append error message to global log and print to console."""
    print(msg)
    ERROR_LOG.append(msg)


def summarize_content(content):
    """
    Summarize content using Ollama llama3.2 model.
    Returns summarized content, or original content if failure.
    """
    prompt = SUMMARIZE_PROMPT.format(content=content)

    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2', prompt],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        err = (
            f"\n--- ERROR summarizing content ---\n"
            f"Return Code: {e.returncode}\n"
            f"stderr:\n{e.stderr}\n"
        )
        log_error(err)
        return content

    except Exception as e:
        err = (
            f"\n--- UNEXPECTED ERROR summarizing content ---\n"
            f"{traceback.format_exc()}\n"
        )
        log_error(err)
        return content


def extract_fields(input_file, output_file, limit=None):
    """Read JSON file, extract only title & content, summarize content."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

    except Exception as e:
        log_error(f"\n--- ERROR reading input file {input_file} ---\n{traceback.format_exc()}")
        return

    if limit:
        data = data[:limit]
        print(f"Processing first {limit} entries...")

    filtered_data = []

    for i, entry in enumerate(data, 1):
        print(f"Processing entry {i}/{len(data)}: {entry.get('title', 'Untitled')}")

        content = entry.get("content", "")
        summarized_content = summarize_content(content)

        filtered_data.append({
            "title": entry.get("title"),
            "content": summarized_content
        })

    # Output summarized stories
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, separators=(',', ':'), ensure_ascii=False)
        print(f"\nProcessed {len(filtered_data)} entries")
        print(f"Output written to {output_file}")

    except Exception as e:
        log_error(f"\n--- ERROR writing output file {output_file} ---\n{traceback.format_exc()}")

    # Write error log at the end
    if ERROR_LOG:
        try:
            with open("error_log.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(ERROR_LOG))
            print("\nError log written to error_log.txt")
        except Exception:
            print("\nFailed to write error_log.txt")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract and summarize stories using local Ollama model")
    parser.add_argument('--limit', type=int, help="Limit number of entries to process")
    args = parser.parse_args()

    extract_fields(
        input_file='source_stories.json',
        output_file='source_stories_filtered.json',
        limit=args.limit
    )