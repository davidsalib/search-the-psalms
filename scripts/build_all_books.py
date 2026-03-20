#!/usr/bin/env python3
"""
Fetch all 66 books of the Bible (NKJV) from Backblaze and generate
most-common-words folders with SUMMARY.md and individual word .md files,
matching the format of the existing most-common-words/ folder for Psalms.
"""

import json
import os
import re
import ssl
import sys
import time
import urllib.request
from collections import Counter, defaultdict

# Bypass SSL verification (macOS Python missing certs)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

BASE_URL = "https://f005.backblazeb2.com/file/catena/bible_versions/en/NKJV"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOP_N = 50

# Common English stop words to exclude
STOP_WORDS = {
    "the", "and", "of", "to", "in", "a", "that", "is", "for", "it",
    "with", "was", "his", "he", "i", "be", "as", "not", "but", "you",
    "they", "are", "on", "have", "had", "him", "her", "she", "them",
    "this", "all", "from", "will", "shall", "my", "me", "or", "which",
    "their", "were", "who", "so", "an", "has", "your", "we", "do",
    "been", "if", "no", "one", "our", "when", "then", "did", "said",
    "up", "out", "by", "there", "what", "its", "at", "into", "may",
    "would", "also", "more", "upon", "am", "us", "how", "about",
    "than", "those", "these", "come", "came", "went", "let", "say",
    "make", "made", "before", "after", "over", "down", "now", "own",
    "away", "off", "every", "each", "other", "any", "such", "some",
    "ye", "thee", "thy", "thou", "o", "nor", "yet", "whom", "whose",
    "where", "because", "therefore", "through", "only", "even", "most",
    "among", "against", "like", "very", "take", "took", "set", "put",
    "too", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "first", "second", "under", "again", "still",
    "just", "while", "being", "here", "between", "both", "does",
    "done", "got", "get", "give", "gave", "go", "gone", "going",
    "might", "much", "must", "could", "should", "since", "until",
    "way", "well", "per", "itself", "himself", "herself", "themselves",
    "myself", "yourself", "ourselves", "yourselves",
    "cannot", "can", "many", "things", "thing", "those",
    "above", "according", "became", "become", "called",
    "day", "days", "man", "men", "people", "sons", "son",
    "hand", "great", "shall", "will", "says",
}

# All 66 books: (key, en_name, ch_count)
BOOKS = [
    # Old Testament
    ("gn", "Genesis", 50), ("ex", "Exodus", 40), ("lv", "Leviticus", 27),
    ("nm", "Numbers", 36), ("dt", "Deuteronomy", 34), ("jo", "Joshua", 24),
    ("jgs", "Judges", 21), ("ru", "Ruth", 4), ("1sm", "1 Samuel", 31),
    ("2sm", "2 Samuel", 24), ("1kgs", "1 Kings", 22), ("2kgs", "2 Kings", 25),
    ("1chr", "1 Chronicles", 29), ("2chr", "2 Chronicles", 36),
    ("ezr", "Ezra", 10), ("neh", "Nehemiah", 13), ("est", "Esther", 10),
    ("jb", "Job", 42), ("ps", "Psalms", 150), ("prv", "Proverbs", 31),
    ("eccl", "Ecclesiastes", 12), ("sg", "Song of Solomon", 8),
    ("is", "Isaiah", 66), ("jer", "Jeremiah", 52), ("lam", "Lamentations", 5),
    ("ez", "Ezekiel", 48), ("dn", "Daniel", 12), ("hos", "Hosea", 14),
    ("jl", "Joel", 3), ("am", "Amos", 9), ("ob", "Obadiah", 1),
    ("jon", "Jonah", 4), ("mi", "Micah", 7), ("na", "Nahum", 3),
    ("hb", "Habakkuk", 3), ("zep", "Zephaniah", 3), ("hg", "Haggai", 2),
    ("zec", "Zechariah", 14), ("mal", "Malachi", 4),
    # New Testament
    ("mt", "Matthew", 28), ("mk", "Mark", 16), ("lk", "Luke", 24),
    ("jn", "John", 21), ("acts", "Acts", 28), ("rom", "Romans", 16),
    ("1cor", "1 Corinthians", 16), ("2cor", "2 Corinthians", 13),
    ("gal", "Galatians", 6), ("eph", "Ephesians", 6),
    ("phil", "Philippians", 4), ("col", "Colossians", 4),
    ("1thes", "1 Thessalonians", 5), ("2thes", "2 Thessalonians", 3),
    ("1tm", "1 Timothy", 6), ("2tm", "2 Timothy", 4),
    ("ti", "Titus", 3), ("phlm", "Philemon", 1),
    ("heb", "Hebrews", 13), ("jas", "James", 5),
    ("1pt", "1 Peter", 5), ("2pt", "2 Peter", 3),
    ("1jn", "1 John", 5), ("2jn", "2 John", 1),
    ("3jn", "3 John", 1), ("jude", "Jude", 1),
    ("rv", "Revelation", 22),
]


def fetch_chapter(book_key, chapter_num, retries=3):
    """Fetch a chapter JSON from Backblaze."""
    url = f"{BASE_URL}/{book_key}/{chapter_num}.json"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
            else:
                print(f"  WARN: Failed to fetch {url}: {e}", file=sys.stderr)
                return None


def extract_verses(chapter_data, book_name, chapter_num):
    """Extract list of (reference, text) from chapter JSON."""
    verses = []
    if not chapter_data or "paragraphs_list" not in chapter_data:
        return verses
    for para in chapter_data["paragraphs_list"]:
        if para.get("type") != "section_paragraph":
            continue
        for verse in para.get("verses_list", []):
            num = verse.get("num_int", 0)
            text_parts = []
            for part in verse.get("verse_parts", []):
                if part.get("style") != "FOOTNOTE":
                    text_parts.append(part.get("text", ""))
            text = "".join(text_parts).strip()
            if text:
                ref = f"{book_name} {chapter_num}:{num}"
                verses.append((ref, text))
    return verses


def count_words(all_verses):
    """Count word occurrences and track which verses contain each word."""
    word_count = Counter()
    word_verses = defaultdict(list)  # word -> [(ref, text)]

    for ref, text in all_verses:
        # Find all words
        words_in_verse = set()
        for match in re.finditer(r"\b[a-zA-Z]+\b", text):
            word = match.group().lower()
            if len(word) >= 3 and word not in STOP_WORDS:
                # Normalize to base form for counting
                words_in_verse.add(word)
                word_count[word] += 1

        for word in words_in_verse:
            word_verses[word].append((ref, text))

    return word_count, word_verses


def slugify(word):
    return word.lower().replace(" ", "-")


def make_book_folder_name(en_name):
    """Convert book name to folder-friendly slug."""
    return en_name.lower().replace(" ", "-")


def bold_word_in_text(text, word):
    """Bold all occurrences of the word in the text (case-insensitive)."""
    pattern = re.compile(rf"(\b{re.escape(word)}\w*\b)", re.IGNORECASE)
    return pattern.sub(r"**\1**", text)


def generate_book_files(book_key, en_name, all_verses, output_dir):
    """Generate most-common-words folder for a single book."""
    word_count, word_verses = count_words(all_verses)

    # Get top N words
    top_words = word_count.most_common(TOP_N)
    if not top_words:
        return

    folder = os.path.join(output_dir, make_book_folder_name(en_name))
    os.makedirs(folder, exist_ok=True)

    # Build word list with display names (capitalized)
    word_list = []  # (slug, display_name, count, verse_count)
    for word, count in top_words:
        slug = slugify(word)
        display = word.capitalize()
        verse_count = len(word_verses[word])
        word_list.append((slug, display, count, verse_count, word))

    # Generate individual word files with prev/next links
    for i, (slug, display, count, verse_count, raw_word) in enumerate(word_list):
        nav_parts = []
        if i > 0:
            prev_slug, prev_display = word_list[i - 1][0], word_list[i - 1][1]
            nav_parts.append(f"[← {prev_display}]({prev_slug}.md)")
        if i < len(word_list) - 1:
            next_slug, next_display = word_list[i + 1][0], word_list[i + 1][1]
            nav_parts.append(f"[{next_display} →]({next_slug}.md)")
        nav_line = " | ".join(nav_parts)

        lines = [f"# {display}", ""]
        if nav_line:
            lines.append(nav_line)
            lines.append("")

        lines.append(f"**Total occurrences in {en_name}: {count}**")
        lines.append("")
        lines.append(f"**Verses containing this word: {verse_count}**")
        lines.append("")
        lines.append(f"*Regex used: `\\b{raw_word}\\w*\\b`*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Add verse references
        book_folder = make_book_folder_name(en_name)
        for ref, text in word_verses[raw_word]:
            bolded = bold_word_in_text(text, raw_word)
            # Parse chapter from ref for linking
            parts = ref.split(" ")
            # Handle multi-word book names like "1 Samuel 3:5"
            ch_verse = parts[-1]  # "3:5"
            ch_num = ch_verse.split(":")[0]
            lines.append(
                f"[**{ref}**](../bible/{book_folder}/{book_folder}-{ch_num}.md) — {bolded}"
            )
            lines.append("")

        filepath = os.path.join(folder, f"{slug}.md")
        with open(filepath, "w") as f:
            f.write("\n".join(lines))

    # Generate SUMMARY.md
    summary_lines = [
        f"# Top {len(word_list)} Common Words in {en_name} (NKJV)",
        "",
        "| # | Word | Occurrences | Verses | File |",
        "|---|------|-------------|--------|------|",
    ]
    for idx, (slug, display, count, verse_count, _) in enumerate(word_list, 1):
        summary_lines.append(
            f"| {idx} | {display} | {count} | {verse_count} | [{slug}.md]({slug}.md) |"
        )
    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("")
    summary_lines.append("**Source: NKJV (New King James Version)**")
    summary_lines.append("")

    with open(os.path.join(folder, "SUMMARY.md"), "w") as f:
        f.write("\n".join(summary_lines))

    return len(word_list)


def main():
    output_dir = os.path.join(PROJECT_ROOT, "books")
    os.makedirs(output_dir, exist_ok=True)

    # Master index
    master_index = [
        "# Search the Scriptures — Most Common Words by Book (NKJV)",
        "",
        "| # | Book | Top Word | File |",
        "|---|------|----------|------|",
    ]

    total_books = len(BOOKS)
    for book_idx, (book_key, en_name, ch_count) in enumerate(BOOKS):
        print(f"[{book_idx+1}/{total_books}] {en_name} ({ch_count} chapters)...")

        all_verses = []
        for ch in range(1, ch_count + 1):
            data = fetch_chapter(book_key, ch)
            if data:
                verses = extract_verses(data, en_name, ch)
                all_verses.extend(verses)
            # Small delay to be polite to the server
            if ch % 10 == 0:
                time.sleep(0.2)

        print(f"  Fetched {len(all_verses)} verses")

        if all_verses:
            n_words = generate_book_files(book_key, en_name, all_verses, output_dir)
            book_folder = make_book_folder_name(en_name)

            # Find top word for index
            word_count, _ = count_words(all_verses)
            top_word = word_count.most_common(1)[0][0].capitalize() if word_count else "—"

            master_index.append(
                f"| {book_idx+1} | {en_name} | {top_word} | [{book_folder}/SUMMARY.md](books/{book_folder}/SUMMARY.md) |"
            )
            print(f"  Generated {n_words} word files in books/{book_folder}/")

    master_index.append("")
    master_index.append("---")
    master_index.append("")
    master_index.append("**Source: NKJV (New King James Version)**")
    master_index.append("")

    with open(os.path.join(PROJECT_ROOT, "BOOKS_INDEX.md"), "w") as f:
        f.write("\n".join(master_index))

    print("\nDone! Master index written to BOOKS_INDEX.md")


if __name__ == "__main__":
    main()
