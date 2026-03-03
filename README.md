# pytarot

Tarot divination powered by `/dev/urandom`. Cards are encoded as Braille Unicode patterns (U+2800–U+284D) — each card's index maps directly to its codepoint's bitmask. No dependencies beyond Python stdlib.

## Quick Start

```bash
python draw.py 3              # draw 3 unique cards
python divine.py              # interactive: press any key to draw, q to quit
python math78.py              # mod-78 arithmetic shell
```

## Card Notation

```
Major Arcana:  0, I, II, III ... XXI
Minor Arcana:  1W, 2W ... 10W, PW, NW, QW, KW   (Wands)
               1C, 2C ... KC                      (Cups)
               1S, 2S ... KS                      (Swords)
               1$, 2$ ... K$                      (Pentacles)
Courts:        A=Ace, P=Page, N=Knight, Q=Queen, K=King
```

## Arithmetic (math78.py)

Interactive or CLI. Operations chain left-to-right:

```
add subt mult div    sum/subtract/multiply/divide all indices (mod 78)
exp log              exponentiation, floor-log
root                 digital root (base 78)
pvd                  place value decomposition (base 78)
digits               interpret cards as base-78 number
factor               factor pairs
pairs+ pairs- pairs* pairwise ops on consecutive cards
```

```bash
python math78.py ldraw "add root"         # reduce last draw to digital root
python math78.py "XVIII,XIX,XX" "add"     # sum specific cards
```
