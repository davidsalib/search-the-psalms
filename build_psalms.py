#!/usr/bin/env python3
"""Parse NKJV Psalms JSON files into a single text file for searching."""
import json
import os
import re

PSALMS_DIR = os.path.join(os.path.dirname(__file__), "bible", "ps")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "bible", "psalms.txt")

def extract_verse_text(verse):
    """Extract plain text from verse_parts, skipping footnotes and line breaks."""
    parts = verse.get("verse_parts", [])
    text_parts = []
    for part in parts:
        style = part.get("style", "")
        text = part.get("text", "")
        if style == "LINE_BREAK":
            text_parts.append(" ")
        elif style == "FOOTNOTE":
            continue  # skip footnote markers
        else:
            text_parts.append(text)
    # Join and normalize whitespace
    full_text = "".join(text_parts)
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    return full_text

def main():
    lines = []
    for ch in range(1, 151):
        filepath = os.path.join(PSALMS_DIR, f"{ch}.JSON")
        with open(filepath, "r") as f:
            data = json.load(f)

        for paragraph in data.get("paragraphs_list", []):
            if paragraph.get("type") == "section_header":
                continue
            for verse in paragraph.get("verses_list", []):
                num = verse.get("num_str", verse.get("num_int", ""))
                text = extract_verse_text(verse)
                if text:
                    lines.append(f"Psalm {ch}:{num}|{text}")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(lines))

    print(f"Wrote {len(lines)} verses to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
