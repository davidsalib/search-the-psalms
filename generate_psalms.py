#!/usr/bin/env python3
"""Generate a markdown file for each Psalm and update word files with clickable links."""
import json
import re
import os

BASE_DIR = os.path.dirname(__file__)
PSALMS_JSON_DIR = os.path.join(BASE_DIR, "bible", "ps")
PSALMS_MD_DIR = os.path.join(BASE_DIR, "bible", "psalms")
WORDS_DIR = os.path.join(BASE_DIR, "words")
COMMON_DIR = os.path.join(BASE_DIR, "experimental-common-words")

def extract_verse_text(verse):
    parts = verse.get("verse_parts", [])
    text_parts = []
    for part in parts:
        style = part.get("style", "")
        text = part.get("text", "")
        if style == "LINE_BREAK":
            text_parts.append(" ")
        elif style == "FOOTNOTE":
            continue
        else:
            text_parts.append(text)
    full_text = "".join(text_parts)
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    return full_text

def generate_psalm_files():
    os.makedirs(PSALMS_MD_DIR, exist_ok=True)
    for ch in range(1, 151):
        filepath = os.path.join(PSALMS_JSON_DIR, f"{ch}.JSON")
        with open(filepath, "r") as f:
            data = json.load(f)

        lines = []
        lines.append(f"# Psalm {ch}\n")

        for paragraph in data.get("paragraphs_list", []):
            if paragraph.get("type") == "section_header":
                lines.append(f"\n### {paragraph.get('text', '')}\n")
                continue
            for verse in paragraph.get("verses_list", []):
                num = verse.get("num_str", verse.get("num_int", ""))
                text = extract_verse_text(verse)
                if text:
                    lines.append(f"**{num}** {text}\n")

        output_path = os.path.join(PSALMS_MD_DIR, f"psalm-{ch}.md")
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

    print(f"Generated 150 Psalm files in {PSALMS_MD_DIR}")

def update_word_files(word_dir):
    """Update all .md files in a directory to make Psalm references clickable."""
    # Determine relative path from word_dir to psalms dir
    rel_path = os.path.relpath(PSALMS_MD_DIR, word_dir)

    for filename in os.listdir(word_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(word_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()

        # Replace **Psalm X:Y** with [**Psalm X:Y**](../bible/psalms/psalm-X.md)
        def replace_ref(m):
            chapter = m.group(1)
            verse = m.group(2)
            link = f"{rel_path}/psalm-{chapter}.md"
            return f"[**Psalm {chapter}:{verse}**]({link})"

        updated = re.sub(
            r'\*\*Psalm (\d+):(\d+)\*\*',
            replace_ref,
            content
        )

        if updated != content:
            with open(filepath, "w") as f:
                f.write(updated)

    print(f"Updated links in {word_dir}")

if __name__ == "__main__":
    generate_psalm_files()
    update_word_files(WORDS_DIR)
    update_word_files(COMMON_DIR)
