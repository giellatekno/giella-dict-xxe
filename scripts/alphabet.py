"""Sorting in the alphabetical order of the dictionary's language, for the
scripts in this folder.

The alphabet is picked by the language of the dictionary (xml:lang of its
files, see dictionary.py). Case is ignored. Spaces, hyphens and other
characters that are not letters only count when two words are otherwise
equal. Accented letters not in the alphabet (é, ï, ...) sort as their
base letter; other letters not in the alphabet sort after it.

To add a language, add its alphabet to ALPHABETS. Letters that sort as
one are written together ("æä").
"""

import unicodedata

from dictionary import LANG

# fmt: off
ALPHABETS = {
    "sme": [
        "a", "á", "b", "c", "č", "d", "đ", "e", "f", "g", "h",
        "i", "j", "k", "l", "m", "n", "ŋ", "o", "p", "r", "s",
        "š", "t", "ŧ", "u", "v", "z", "ž", "æä", "øö", "å",
    ],
    "sma": list("abcdefghi") + ["ï"] + list("jklmnopqrstuvwxyz") + ["æä", "øö", "å"],
}

# a language without an alphabet of its own
DEFAULT = list("abcdefghijklmnopqrstuvwxyz") + ["æä", "øö", "å"]

ALPHABET = ALPHABETS.get(LANG, DEFAULT)
RANK = {c: n for n, letters in enumerate(ALPHABET) for c in letters}


def _rank(c):
    if c in RANK:
        return RANK[c]
    # other accented letters (é, ï, ...) sort as their base letter
    base = unicodedata.normalize("NFD", c)[0]
    return RANK.get(base, len(ALPHABET) + ord(c))


def sort_key(word):
    word = unicodedata.normalize("NFC", word.lower())
    letters = [c for c in word if c.isalpha()]
    return ([_rank(c) for c in letters], word)
