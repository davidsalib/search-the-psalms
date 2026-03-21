#!/usr/bin/env python3
"""
Generate summary.md files:
1. Per-book summary.md with top 5 words
2. Global summary.md with top words across all books and top 5 per book
"""

import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS_DIR = os.path.join(PROJECT_ROOT, "books")

# Canonical book order
BOOK_ORDER = [
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "joshua", "judges", "ruth", "1-samuel", "2-samuel",
    "1-kings", "2-kings", "1-chronicles", "2-chronicles",
    "ezra", "nehemiah", "esther", "job", "psalms", "proverbs",
    "ecclesiastes", "song-of-solomon", "isaiah", "jeremiah", "lamentations",
    "ezekiel", "daniel", "hosea", "joel", "amos",
    "obadiah", "jonah", "micah", "nahum", "habakkuk",
    "zephaniah", "haggai", "zechariah", "malachi",
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1-corinthians", "2-corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1-thessalonians", "2-thessalonians",
    "1-timothy", "2-timothy", "titus", "philemon",
    "hebrews", "james", "1-peter", "2-peter",
    "1-john", "2-john", "3-john", "jude", "revelation",
]

DISPLAY_NAMES = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
    "judges": "Judges", "ruth": "Ruth", "1-samuel": "1 Samuel",
    "2-samuel": "2 Samuel", "1-kings": "1 Kings", "2-kings": "2 Kings",
    "1-chronicles": "1 Chronicles", "2-chronicles": "2 Chronicles",
    "ezra": "Ezra", "nehemiah": "Nehemiah", "esther": "Esther",
    "job": "Job", "psalms": "Psalms", "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "song-of-solomon": "Song of Solomon",
    "isaiah": "Isaiah", "jeremiah": "Jeremiah", "lamentations": "Lamentations",
    "ezekiel": "Ezekiel", "daniel": "Daniel", "hosea": "Hosea",
    "joel": "Joel", "amos": "Amos", "obadiah": "Obadiah",
    "jonah": "Jonah", "micah": "Micah", "nahum": "Nahum",
    "habakkuk": "Habakkuk", "zephaniah": "Zephaniah", "haggai": "Haggai",
    "zechariah": "Zechariah", "malachi": "Malachi", "matthew": "Matthew",
    "mark": "Mark", "luke": "Luke", "john": "John", "acts": "Acts",
    "romans": "Romans", "1-corinthians": "1 Corinthians",
    "2-corinthians": "2 Corinthians", "galatians": "Galatians",
    "ephesians": "Ephesians", "philippians": "Philippians",
    "colossians": "Colossians", "1-thessalonians": "1 Thessalonians",
    "2-thessalonians": "2 Thessalonians", "1-timothy": "1 Timothy",
    "2-timothy": "2 Timothy", "titus": "Titus", "philemon": "Philemon",
    "hebrews": "Hebrews", "james": "James", "1-peter": "1 Peter",
    "2-peter": "2 Peter", "1-john": "1 John", "2-john": "2 John",
    "3-john": "3 John", "jude": "Jude", "revelation": "Revelation",
}


def parse_summary_md(filepath):
    """Parse a book's SUMMARY.md and return list of (word, occurrences, verses, slug)."""
    words = []
    with open(filepath, "r") as f:
        for line in f:
            # Match table rows like: | 1 | God | 231 | 199 | [god.md](god.md) |
            m = re.match(
                r"\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*\[(.+?)\.md\]",
                line,
            )
            if m:
                word = m.group(1).strip()
                occurrences = int(m.group(2))
                verses = int(m.group(3))
                slug = m.group(4).strip()
                words.append((word, occurrences, verses, slug))
    return words


def generate_book_summary(book_slug, words):
    """Generate summary.md for a single book with top 5 words."""
    display_name = DISPLAY_NAMES.get(book_slug, book_slug.replace("-", " ").title())
    top5 = words[:5]

    lines = [
        f"# {display_name} — Summary",
        "",
        "## Top 5 Words",
        "",
        "| # | Word | Occurrences | Verses | File |",
        "|---|------|-------------|--------|------|",
    ]
    for i, (word, occ, ver, slug) in enumerate(top5, 1):
        lines.append(f"| {i} | {word} | {occ} | {ver} | [{slug}.md]({slug}.md) |")

    lines.append("")
    lines.append(f"See [SUMMARY.md](SUMMARY.md) for the complete top {len(words)} words.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Source: NKJV (New King James Version)**")
    lines.append("")

    return "\n".join(lines)


def generate_global_summary(all_books_data):
    """Generate global summary.md with top words across all books and top 5 per book."""
    # Aggregate word counts across all books
    global_counts = {}  # word_lower -> total occurrences
    global_verses = {}  # word_lower -> total verses
    global_display = {}  # word_lower -> display name

    for book_slug, words in all_books_data:
        for word, occ, ver, slug in words:
            key = word.lower()
            global_counts[key] = global_counts.get(key, 0) + occ
            global_verses[key] = global_verses.get(key, 0) + ver
            if key not in global_display:
                global_display[key] = word

    # Sort by total occurrences
    sorted_words = sorted(global_counts.items(), key=lambda x: x[1], reverse=True)
    top_50 = sorted_words[:50]

    lines = [
        "# Bible Word Summary — All 66 Books (NKJV)",
        "",
        "## Top 50 Words Across All Books",
        "",
        "| # | Word | Total Occurrences | Total Verses |",
        "|---|------|-------------------|--------------|",
    ]
    for i, (word_key, total_occ) in enumerate(top_50, 1):
        display = global_display[word_key]
        total_ver = global_verses[word_key]
        lines.append(f"| {i} | {display} | {total_occ} | {total_ver} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Top 5 Words by Book")
    lines.append("")
    lines.append(
        "| # | Book | #1 | #2 | #3 | #4 | #5 |"
    )
    lines.append(
        "|---|------|----|----|----|----|----|"
    )

    for i, (book_slug, words) in enumerate(all_books_data, 1):
        display_name = DISPLAY_NAMES.get(book_slug, book_slug.replace("-", " ").title())
        top5 = words[:5]
        cols = []
        for word, occ, ver, slug in top5:
            cols.append(f"{word} ({occ})")
        # Pad if fewer than 5
        while len(cols) < 5:
            cols.append("—")
        book_link = f"[{display_name}](books/{book_slug}/summary.md)"
        lines.append(
            f"| {i} | {book_link} | {' | '.join(cols)} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("**Source: NKJV (New King James Version)**")
    lines.append("")

    return "\n".join(lines)


def main():
    all_books_data = []  # [(book_slug, [(word, occ, ver, slug), ...]), ...]

    for book_slug in BOOK_ORDER:
        book_dir = os.path.join(BOOKS_DIR, book_slug)
        summary_path = os.path.join(book_dir, "SUMMARY.md")

        if not os.path.exists(summary_path):
            print(f"  SKIP: {book_slug} (no SUMMARY.md)")
            continue

        words = parse_summary_md(summary_path)
        if not words:
            print(f"  SKIP: {book_slug} (no words parsed)")
            continue

        all_books_data.append((book_slug, words))

        # Generate per-book summary.md
        content = generate_book_summary(book_slug, words)
        out_path = os.path.join(book_dir, "summary.md")
        with open(out_path, "w") as f:
            f.write(content)
        print(f"  {book_slug}/summary.md — top 5: {', '.join(w[0] for w in words[:5])}")

    # Generate global summary.md
    global_content = generate_global_summary(all_books_data)
    global_path = os.path.join(PROJECT_ROOT, "summary.md")
    with open(global_path, "w") as f:
        f.write(global_content)
    print(f"\nGlobal summary.md written with {len(all_books_data)} books")


if __name__ == "__main__":
    main()
