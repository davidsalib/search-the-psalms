#!/usr/bin/env python3
"""Find the top 50 most common meaningful words in Psalms."""
import re
import os
from collections import Counter

PSALMS_FILE = os.path.join(os.path.dirname(__file__), "bible", "psalms.txt")

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "be", "as", "are", "was",
    "were", "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "shall", "would", "should", "may", "might", "can", "could", "not", "no",
    "nor", "so", "if", "then", "than", "that", "this", "these", "those",
    "who", "whom", "which", "what", "when", "where", "how", "why", "all",
    "each", "every", "both", "few", "more", "most", "other", "some", "such",
    "only", "own", "same", "too", "very", "just", "because", "about", "up",
    "out", "into", "over", "after", "before", "between", "under", "again",
    "there", "here", "once", "also", "any", "many", "much", "now", "even",
    "new", "well", "way", "our", "us", "we", "me", "my", "i", "he", "she",
    "him", "his", "her", "they", "them", "their", "you", "your", "am", "oh",
    "o", "let", "yet", "upon", "unto", "thy", "thee", "them", "ye", "hath",
    "though", "through", "while", "down", "like", "make", "made", "set",
    "put", "come", "came", "go", "went", "gone", "said", "says", "say",
    "one", "two", "nor", "among", "against", "according", "away", "back",
    "been", "does", "done", "get", "give", "given", "got", "had", "indeed",
    "itself", "keep", "kept", "know", "known", "last", "less", "long",
    "look", "looked", "looks", "man", "men", "must", "never", "next",
    "off", "often", "old", "part", "place", "right", "see", "seen",
    "since", "still", "take", "taken", "tell", "thing", "things", "think",
    "time", "turn", "turned", "use", "used", "want", "whose", "without",
    "work", "year", "around", "another", "became", "become", "being",
    "called", "cannot", "day", "days", "end", "ever", "far", "first",
    "found", "full", "great", "hand", "head", "high", "left", "life",
    "little", "name", "nothing", "number", "people", "s", "t", "don",
    "didn", "won", "wouldn", "couldn", "shouldn", "wasn", "weren", "isn",
    "aren", "haven", "hasn", "hadn", "doesn", "ain", "ll", "ve", "re",
    "d", "m", "above", "below", "already", "always", "enough", "within",
    "whether", "else", "however", "rather", "quite", "along", "across",
    "behind", "beside", "besides", "beyond", "during", "except", "near",
    "toward", "towards", "until", "while", "whom", "whose",
    "themselves", "himself", "herself", "myself", "yourself", "ourselves",
    "itself", "when", "where", "which", "while",
}

def main():
    with open(PSALMS_FILE, "r") as f:
        lines = f.read().strip().split("\n")

    counter = Counter()
    for line in lines:
        _, text = line.split("|", 1)
        words = re.findall(r"[a-zA-Z']+", text.lower())
        for word in words:
            word = word.strip("'")
            if word and word not in STOP_WORDS and len(word) > 2:
                counter[word] += 1

    top50 = counter.most_common(50)
    for i, (word, count) in enumerate(top50, 1):
        print(f"{i}. {word} ({count})")

if __name__ == "__main__":
    main()
