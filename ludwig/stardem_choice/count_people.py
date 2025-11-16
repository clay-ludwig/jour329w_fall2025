#!/usr/bin/env python3
"""
Count people mentions in Education_With_Entities.json
Excludes titles (only counts names before the comma)
Outputs results in descending order to a text file
"""

import json
from collections import Counter
from pathlib import Path


def extract_name(person_string):
    """
    Extract the name from a 'Name, Title' format string.
    Returns only the name part (before the comma).
    """
    if ',' in person_string:
        return person_string.split(',')[0].strip()
    return person_string.strip()


def count_people_mentions(json_file):
    """
    Count how many times each person appears in the JSON data.
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        Counter object with person names and their counts
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    person_counter = Counter()
    
    for article in data:
        # Get the people list from each article
        people = article.get('people', [])
        
        # Extract names (without titles) and count them
        for person_entry in people:
            name = extract_name(person_entry)
            if name:  # Only count non-empty names
                person_counter[name] += 1
    
    return person_counter


def write_results(counter, output_file):
    """
    Write the person counts to a text file in descending order.
    
    Args:
        counter: Counter object with person counts
        output_file: Path to the output text file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Person Mention Counts (Descending Order)\n")
        f.write("=" * 50 + "\n\n")
        
        # Sort by count (descending), then by name (alphabetically)
        for name, count in counter.most_common():
            f.write(f"{name}: {count}\n")
        
        f.write("\n" + "=" * 50 + "\n")
        f.write(f"Total unique people: {len(counter)}\n")
        f.write(f"Total mentions: {sum(counter.values())}\n")


def main():
    # Define file paths
    script_dir = Path(__file__).parent
    json_file = script_dir / "Education_With_Entities.json"
    output_file = script_dir / "people_counts.txt"
    
    # Count people mentions
    print(f"Reading {json_file}...")
    person_counts = count_people_mentions(json_file)
    
    # Write results
    print(f"Writing results to {output_file}...")
    write_results(person_counts, output_file)
    
    # Print summary to console
    print(f"\nAnalysis complete!")
    print(f"Total unique people: {len(person_counts)}")
    print(f"Total mentions: {sum(person_counts.values())}")
    print(f"\nTop 10 most mentioned people:")
    for name, count in person_counts.most_common(10):
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
