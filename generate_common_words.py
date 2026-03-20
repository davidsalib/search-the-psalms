#!/usr/bin/env python3
"""Generate markdown files for the top 50 common words in Psalms."""
import re
import os
import sys

PSALMS_FILE = os.path.join(os.path.dirname(__file__), "bible", "psalms.txt")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "experimental-common-words")

# Top 50 words with their regex patterns (including variants)
WORDS = [
    ("lord", r'\bLord\b|\bLORD\b'),
    ("god", r'\bGod\b|\bGod\'s\b'),
    ("praise", r'\bprais\w*\b'),
    ("earth", r'\bearth\w*\b'),
    ("forever", r'\bforever\w*\b'),
    ("heart", r'\bheart\w*\b'),
    ("mercy", r'\bmerc(y|ies|iful)\b'),
    ("soul", r'\bsoul\w*\b'),
    ("wicked", r'\bwicked\w*\b'),
    ("enemies", r'\benem(y|ies)\b'),
    ("righteousness", r'\brighteousness\b'),
    ("selah", r'\bSelah\b'),
    ("sing", r'\bsing\b|\bsings\b|\bsinging\b|\bsung\b|\bsang\b'),
    ("strength", r'\bstrength\w*\b'),
    ("good", r'\bgood\w*\b'),
    ("salvation", r'\bsalvation\b'),
    ("fear", r'\bfear\w*\b'),
    ("mouth", r'\bmouth\w*\b'),
    ("israel", r'\bIsrael\w*\b'),
    ("word", r'\bword\b|\bwords\b'),
    ("righteous", r'\brighteous\b'),
    ("hear", r'\bhear\b|\bheard\b|\bhears\b|\bhearing\b'),
    ("rejoice", r'\brejoic\w*\b'),
    ("glory", r'\bglor(y|ious|ify|ified)\b'),
    ("works", r'\bwork\b|\bworks\b'),
    ("nations", r'\bnation\w*\b'),
    ("voice", r'\bvoice\w*\b'),
    ("trust", r'\btrust\w*\b'),
    ("iniquity", r'\biniquit(y|ies)\b'),
    ("deliver", r'\bdeliver\w*\b'),
    ("blessed", r'\bblessed\b|\bblessing\w*\b'),
    ("hands", r'\bhand\b|\bhands\b'),
    ("help", r'\bhelp\w*\b'),
    ("bless", r'\bbless\b|\bblesses\b'),
    ("land", r'\bland\b|\blands\b'),
    ("endures", r'\bendur\w*\b'),
    ("trouble", r'\btrouble\w*\b'),
    ("eyes", r'\beye\b|\beyes\b'),
    ("holy", r'\bholy\b|\bholiness\b'),
    ("house", r'\bhouse\w*\b'),
    ("children", r'\bchildren\b|\bchild\b'),
    ("therefore", r'\btherefore\b'),
    ("heavens", r'\bheaven\w*\b'),
    ("king", r'\bking\b|\bkings\b|\bkingdom\w*\b'),
    ("speak", r'\bspeak\w*\b|\bspoke\b|\bspoken\b'),
    ("evil", r'\bevil\w*\b'),
    ("cast", r'\bcast\w*\b'),
    ("peoples", r'\bpeople\w*\b'),
    ("truth", r'\btruth\w*\b'),
    ("brought", r'\bbr(ought|ing|ings)\b'),
]

def load_verses():
    with open(PSALMS_FILE, "r") as f:
        lines = f.read().strip().split("\n")
    verses = []
    for line in lines:
        ref, text = line.split("|", 1)
        verses.append((ref, text))
    return verses

def search_and_generate(word, regex_pattern, verses, output_path):
    results = []
    total_count = 0
    for ref, text in verses:
        matches = re.findall(regex_pattern, text, re.IGNORECASE)
        if matches:
            total_count += len(matches)
            highlighted = re.sub(
                regex_pattern,
                lambda m: f"**{m.group(0)}**",
                text,
                flags=re.IGNORECASE
            )
            results.append((ref, highlighted))

    with open(output_path, "w") as f:
        f.write(f"# {word.title()}\n\n")
        f.write(f"**Total occurrences in Psalms: {total_count}**\n\n")
        f.write(f"**Verses containing this word: {len(results)}**\n\n")
        f.write(f"*Regex used: `{regex_pattern}`*\n\n")
        f.write("---\n\n")
        for ref, text in results:
            f.write(f"**{ref}** — {text}\n\n")

    return word, total_count, len(results)

def main():
    verses = load_verses()
    summary_rows = []

    for word, pattern in WORDS:
        filename = f"{word}.md"
        output_path = os.path.join(OUTPUT_DIR, filename)
        w, count, verse_count = search_and_generate(word, pattern, verses, output_path)
        summary_rows.append((w, count, verse_count, filename))
        print(f"  {w}: {count} occurrences, {verse_count} verses")

    # Sort by occurrences descending
    summary_rows.sort(key=lambda x: x[1], reverse=True)

    # Write summary
    summary_path = os.path.join(OUTPUT_DIR, "SUMMARY.md")
    with open(summary_path, "w") as f:
        f.write("# Top 50 Common Words in Psalms (NKJV)\n\n")
        f.write("| # | Word | Occurrences | Verses | File |\n")
        f.write("|---|------|-------------|--------|------|\n")
        for i, (w, count, vc, fn) in enumerate(summary_rows, 1):
            f.write(f"| {i} | {w.title()} | {count} | {vc} | [{fn}]({fn}) |\n")
        f.write(f"\n---\n\n**Source: NKJV (New King James Version)**\n")

    print(f"\nDone! Summary at {summary_path}")

if __name__ == "__main__":
    main()
