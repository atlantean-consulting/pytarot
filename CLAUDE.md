# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Tarot divination tool that uses `/dev/urandom` (via `os.urandom`) as an entropy source. The 78 tarot cards are encoded as Braille Unicode characters (U+2800–U+284D), where card index N maps to codepoint U+2800+N.

## Architecture

- **`tarot.py`** — Core library. Card data, rejection-sampled random drawing (`draw(n)`, `draw_one()`), and display formatting. All other modules import this.
- **`divine.py`** — Interactive REPL. Raw terminal input (termios/tty), draw-on-keypress, spread accumulation.
- **`draw.py`** — CLI. `python draw.py [N]` draws N cards (default 1).
- **`cross_reference.md`** — Full 78-card mapping table (index, Braille codepoint, card name, Playing Cards codepoint).

## Running

```bash
python draw.py 10        # draw 10 unique cards
python draw.py 10 --repeats  # allow duplicates
python divine.py         # interactive mode (any key = draw, q = quit)
```

## Key Design Decisions

- **Rejection sampling** in `tarot.draw()`: bytes >= 234 (78*3) are discarded to eliminate modulo bias, since 256 is not divisible by 78.
- **No repeats by default** — `draw.py` draws without replacement (like a real deck). Pass `--repeats` to allow duplicates. The library function `tarot.draw(n, replace=True)` defaults to replacement for backward compatibility.
- **No external dependencies** — stdlib only.
- Card ordering: Major Arcana (0–21), Wands (22–35), Cups (36–49), Swords (50–63), Pentacles (64–77). This matches the Unicode Playing Cards block mapping (Clubs=Wands, Hearts=Cups, Spades=Swords, Diamonds=Pentacles).
