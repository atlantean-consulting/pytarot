# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Tarot divination tool that uses `/dev/urandom` (via `os.urandom`) as an entropy source. The 78 tarot cards are encoded as Braille Unicode characters (U+2800–U+284D), where card index N maps to codepoint U+2800+N. No external dependencies — stdlib only.

## Architecture

- **`tarot.py`** — Core library. Card data, rejection-sampled random drawing (`draw(n, replace)`, `draw_one()`), and display formatting. All other modules import this.
- **`divine.py`** — Interactive REPL. Raw terminal input (termios/tty), draw-on-keypress, spread accumulation. Writes result to `l_div` on exit.
- **`draw.py`** — CLI. `python draw.py [N] [--repeats]` draws N unique cards (default 1). Writes result to `l_dr` on exit.
- **`math78.py`** — Mod-78 arithmetic shell. Interactive REPL or CLI mode. Can read from scratch files (`ldiv`/`ldraw`), card notation, or raw indices.
- **`cross_reference.md`** — Full 78-card mapping table (index, Braille codepoint, card name, Playing Cards codepoint).

## Running

```bash
python draw.py 10                          # draw 10 unique cards
python draw.py 10 --repeats                # allow duplicates
python divine.py                           # interactive (any key = draw, q = quit)
python divine.py --no-repeats              # interactive, no duplicate cards
python math78.py                           # arithmetic REPL
python math78.py ldraw "add root"          # operate on last draw
python math78.py "AW,NC,K$" "add,root"    # operate on specific cards
```

## Card Notation (math78.py)

- Major Arcana: Roman numerals `0`, `I`, `II` ... `XXI`
- Minor Arcana: rank + suit letter, e.g. `1W`, `10S`, `QC`, `K$`
- Suits: `W`=Wands, `C`=Cups, `S`=Swords, `$`=Pentacles
- Courts: `A`=Ace, `P`=Page, `N`=Knight, `Q`=Queen, `K`=King
- Also accepts raw indices (0–77) and Braille glyphs

## Scratch Files

`draw.py` and `divine.py` write their results (comma-separated Braille glyphs) to `l_dr` and `l_div` respectively, overwritten each run. `math78.py` reads these via `ldraw`/`ldiv` input specifiers.

## Key Design Decisions

- **Rejection sampling** in `tarot.draw()`: bytes >= 234 (78*3) are discarded to eliminate modulo bias, since 256 is not divisible by 78.
- **Repeat defaults differ by tool**: `draw.py` defaults to no repeats (`--repeats` to allow); `divine.py` defaults to repeats (`--no-repeats` to suppress). The library function `tarot.draw(n, replace=True)` defaults to replacement.
- **REPL chaining**: In the `math78.py` REPL, each operation's result replaces the working set. Subsequent operations act on the previous result, not the original input. This means `add` then `root` applies root to the single sum, not to the original cards. Operations like `root` are no-ops on values already < 78.
- Card ordering: Major Arcana (0–21), Wands (22–35), Cups (36–49), Swords (50–63), Pentacles (64–77). Maps to Unicode Playing Cards block (Clubs=Wands, Hearts=Cups, Spades=Swords, Diamonds=Pentacles).
