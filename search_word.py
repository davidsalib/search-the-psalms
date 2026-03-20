#!/usr/bin/env python3
"""Search Psalms for a word/phrase and generate a markdown file."""
import re
import os
import sys

PSALMS_FILE = os.path.join(os.path.dirname(__file__), "bible", "psalms.txt")

def load_verses():
    with open(PSALMS_FILE, "r") as f:
        lines = f.read().strip().split("\n")
    verses = []
    for line in lines:
        ref, text = line.split("|", 1)
        verses.append((ref, text))
    return verses

def search_psalms(word, regex_pattern, verses):
    """Search verses using the regex pattern. Return list of (ref, highlighted_text)."""
    results = []
    for ref, text in verses:
        if re.search(regex_pattern, text, re.IGNORECASE):
            # Bold the matched words
            highlighted = re.sub(
                regex_pattern,
                lambda m: f"**{m.group(0)}**",
                text,
                flags=re.IGNORECASE
            )
            results.append((ref, highlighted))
    return results

def count_occurrences(regex_pattern, verses):
    """Count total occurrences across all verses."""
    total = 0
    for _, text in verses:
        total += len(re.findall(regex_pattern, text, re.IGNORECASE))
    return total

def generate_markdown(word, regex_pattern, output_path):
    verses = load_verses()
    results = search_psalms(word, regex_pattern, verses)
    total_count = count_occurrences(regex_pattern, verses)

    with open(output_path, "w") as f:
        f.write(f"# {word.title()}\n\n")
        f.write(f"**Total occurrences in Psalms: {total_count}**\n\n")
        f.write(f"**Verses containing this word: {len(results)}**\n\n")
        f.write(f"*Regex used: `{regex_pattern}`*\n\n")
        f.write("---\n\n")

        for ref, text in results:
            f.write(f"**{ref}** — {text}\n\n")

    print(f"Generated {output_path}: {len(results)} verses, {total_count} occurrences")

if __name__ == "__main__":
    word = sys.argv[1]
    pattern = sys.argv[2]
    output = sys.argv[3]
    generate_markdown(word, pattern, output)
