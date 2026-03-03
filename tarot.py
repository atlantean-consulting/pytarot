"""Tarot divination library using /dev/urandom entropy and Braille Unicode encoding.

The 78 tarot cards are mapped to Braille patterns U+2800–U+284D.
Card index N maps to codepoint U+2800+N, where the raised dots
correspond to the set bits of N.

Canonical order: Major Arcana (0–21), Wands (22–35),
Cups (36–49), Swords (50–63), Pentacles (64–77).
"""

import os

NUM_CARDS = 78
BRAILLE_BASE = 0x2800
# Rejection threshold: largest multiple of 78 that fits in a byte
# 78 * 3 = 234, so we discard bytes >= 234 to avoid modulo bias
REJECTION_THRESHOLD = (256 // NUM_CARDS) * NUM_CARDS  # 234

MAJOR_ARCANA = [
    "The Fool", "The Magician", "The High Priestess", "The Empress",
    "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
    "Strength", "The Hermit", "Wheel of Fortune", "Justice",
    "The Hanged Man", "Death", "Temperance", "The Devil",
    "The Tower", "The Star", "The Moon", "The Sun",
    "Judgement", "The World",
]

SUITS = ["Wands", "Cups", "Swords", "Pentacles"]
RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
         "Jack", "Knight", "Queen", "King"]

# Playing Cards Unicode block base offsets per suit
_SUIT_BASES = {
    "Wands":     0x1F0D0,  # Clubs
    "Cups":      0x1F0B0,  # Hearts
    "Swords":    0x1F0A0,  # Spades
    "Pentacles": 0x1F0C0,  # Diamonds
}
_RANK_OFFSETS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0xA, 0xB, 0xC, 0xD, 0xE]

# Build the canonical card table: list of (name, playing_card_codepoint)
CARDS = []
# Major Arcana: U+1F0E0 (The Fool) through U+1F0F5 (The World)
for i, name in enumerate(MAJOR_ARCANA):
    CARDS.append((name, 0x1F0E0 + i))
# Minor Arcana in suit order
for suit in SUITS:
    base = _SUIT_BASES[suit]
    for j, rank in enumerate(RANKS):
        CARDS.append((f"{rank} of {suit}", base + _RANK_OFFSETS[j]))

assert len(CARDS) == NUM_CARDS


def card_name(index):
    """Return the name of card at the given index (0–77)."""
    return CARDS[index][0]


def playing_card(index):
    """Return the Unicode Playing Card character for the given index."""
    return chr(CARDS[index][1])


def braille(index):
    """Return the Braille pattern character for the given index."""
    return chr(BRAILLE_BASE + index)


def format_card(index):
    """Return a display string: braille glyph + card name."""
    return f"{braille(index)} {card_name(index)}"


def draw(n=1, replace=True):
    """Draw n cards using rejection-sampled bytes from os.urandom.

    Returns a list of n card indices (0–77).
    If replace=False, each card can only appear once (max n=78).
    """
    if not replace and n > NUM_CARDS:
        raise ValueError(f"Cannot draw {n} unique cards from a {NUM_CARDS}-card deck")
    seen = set()
    results = []
    while len(results) < n:
        raw = os.urandom(n - len(results) + 16)
        for byte in raw:
            if byte < REJECTION_THRESHOLD:
                index = byte % NUM_CARDS
                if replace or index not in seen:
                    seen.add(index)
                    results.append(index)
                    if len(results) == n:
                        break
    return results


def draw_one():
    """Draw a single card. Returns its index (0–77)."""
    return draw(1)[0]
