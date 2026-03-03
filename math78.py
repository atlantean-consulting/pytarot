#!/usr/bin/env python3
"""Interactive mod-78 arithmetic shell for tarot cards.

Launch with no arguments to get a >>> prompt.
Enter cards, then operations to perform on them.
"""

import sys
import tarot

# --- Card notation parsing and formatting ---

_ROMAN = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]


def _to_roman(n):
    if n == 0:
        return "0"
    parts = []
    for val, sym in _ROMAN:
        while n >= val:
            parts.append(sym)
            n -= val
    return "".join(parts)


def _from_roman(s):
    s = s.upper()
    if s == "0":
        return 0
    roman_vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for ch in reversed(s):
        val = roman_vals.get(ch)
        if val is None:
            return None
        if val < prev:
            total -= val
        else:
            total += val
        prev = val
    return total


_SUIT_LETTERS = {"W": "Wands", "C": "Cups", "S": "Swords", "$": "Pentacles"}
_SUIT_TO_LETTER = {v: k for k, v in _SUIT_LETTERS.items()}
_RANK_LETTERS = {
    "1": "Ace", "2": "2", "3": "3", "4": "4", "5": "5",
    "6": "6", "7": "7", "8": "8", "9": "9", "10": "10",
    "A": "Ace",
    "P": "Page", "N": "Knight", "Q": "Queen", "K": "King",
}
_RANK_TO_LETTER = {}
for letter, name in _RANK_LETTERS.items():
    _RANK_TO_LETTER[name] = letter
# Page is our display name for Jack
_RANK_TO_LETTER["Jack"] = "P"


def _card_index_by_name():
    """Build a lookup from card name to index."""
    return {tarot.card_name(i): i for i in range(tarot.NUM_CARDS)}


_NAME_TO_INDEX = _card_index_by_name()


def parse_card(token):
    """Parse a card notation token into an index (0–77).

    Accepts:
      - Integer index: "0", "42", "77"
      - Roman numeral for Major Arcana: "0", "I", "XVIII"
      - Minor Arcana notation: "1W", "10S", "P$", "NC"
      - Braille glyph: "⠉"
    """
    token = token.strip()
    if not token:
        return None

    # Braille glyph
    if len(token) == 1 and 0x2800 <= ord(token) <= 0x284D:
        return ord(token) - tarot.BRAILLE_BASE

    # Minor arcana: rank + suit letter
    for suit_ch in _SUIT_LETTERS:
        if token.upper().endswith(suit_ch):
            rank_part = token[:-1].upper()
            if rank_part in _RANK_LETTERS:
                rank_name = _RANK_LETTERS[rank_part]
                suit_name = _SUIT_LETTERS[suit_ch]
                # Map Page -> Jack for lookup
                if rank_name == "Page":
                    rank_name = "Jack"
                full_name = f"{rank_name} of {suit_name}"
                if full_name in _NAME_TO_INDEX:
                    return _NAME_TO_INDEX[full_name]

    # Try as plain integer index
    try:
        n = int(token)
        if 0 <= n < tarot.NUM_CARDS:
            return n
    except ValueError:
        pass

    # Try as Roman numeral (Major Arcana)
    val = _from_roman(token)
    if val is not None and 0 <= val <= 21:
        return val

    return None


def format_notation(index):
    """Format a card index as card notation."""
    if index < 0 or index >= tarot.NUM_CARDS:
        return str(index)

    name = tarot.card_name(index)

    # Major Arcana
    if index <= 21:
        return _to_roman(index)

    # Minor Arcana
    parts = name.split(" of ")
    if len(parts) == 2:
        rank_name, suit_name = parts
        rank_ch = _RANK_TO_LETTER.get(rank_name, rank_name)
        suit_ch = _SUIT_TO_LETTER.get(suit_name, suit_name)
        return f"{rank_ch}{suit_ch}"

    return name


def format_result(index):
    """Format a result card with braille, notation, and name."""
    return f"{tarot.braille(index)} {format_notation(index)} ({tarot.card_name(index)})"


# --- Operations ---

def op_add(indices):
    """Sum all indices, mod 78."""
    return [sum(indices) % tarot.NUM_CARDS]


def op_subt(indices):
    """Subtract subsequent indices from the first, mod 78."""
    if not indices:
        return []
    result = indices[0]
    for i in indices[1:]:
        result -= i
    return [result % tarot.NUM_CARDS]


def op_mult(indices):
    """Multiply all indices, mod 78."""
    result = 1
    for i in indices:
        result *= i
    return [result % tarot.NUM_CARDS]


def op_root(indices):
    """Digital root in base 78. Repeatedly sum base-78 digits until single digit."""
    results = []
    for n in indices:
        if n == 0:
            results.append(0)
            continue
        while n >= tarot.NUM_CARDS:
            digit_sum = 0
            while n > 0:
                digit_sum += n % tarot.NUM_CARDS
                n //= tarot.NUM_CARDS
            n = digit_sum
        results.append(n)
    return results


def op_pvd(indices):
    """Place value decomposition: treat the number as base-78 and return its digits."""
    results = []
    for n in indices:
        if n == 0:
            results.append(0)
            continue
        digits = []
        val = abs(n)
        while val > 0:
            digits.append(val % tarot.NUM_CARDS)
            val //= tarot.NUM_CARDS
        digits.reverse()
        results.extend(digits)
    return results


def op_factor(indices):
    """Factor pairs for each value. Prints them; returns the original indices."""
    for n in indices:
        val = abs(n) if n != 0 else 0
        if val == 0:
            print(f"  0: no factors")
            continue
        pairs = []
        i = 1
        while i * i <= val:
            if val % i == 0:
                pairs.append((i, val // i))
            i += 1
        pair_strs = []
        for a, b in pairs:
            a_label = format_notation(a % tarot.NUM_CARDS) if a < tarot.NUM_CARDS else str(a)
            b_label = format_notation(b % tarot.NUM_CARDS) if b < tarot.NUM_CARDS else str(b)
            pair_strs.append(f"{a} x {b} = [{a_label} x {b_label}]")
        print(f"  {n}: " + ", ".join(pair_strs))
    return indices


def op_digits(indices):
    """Interpret the list of indices as digits of a base-78 number, return that number."""
    n = 0
    for i in indices:
        n = n * tarot.NUM_CARDS + i
    return [n]


def op_div(indices):
    """Divide first index by subsequent indices (integer division), mod 78."""
    if not indices:
        return []
    result = indices[0]
    for i in indices[1:]:
        if i == 0:
            print("  division by zero (The Fool divides nothing)")
            return []
        result //= i
    return [result % tarot.NUM_CARDS]


def op_exp(indices):
    """Exponentiate left-to-right, mod 78."""
    if not indices:
        return []
    result = indices[0]
    for i in indices[1:]:
        result = pow(result, i, tarot.NUM_CARDS)
    return [result % tarot.NUM_CARDS]


def op_log(indices):
    """Floor of log base second of first. With one value, log base 78."""
    import math
    if not indices:
        return []
    if len(indices) == 1:
        n, base = indices[0], tarot.NUM_CARDS
    else:
        n, base = indices[0], indices[1]
    if n <= 0 or base <= 1:
        print(f"  log undefined for n={n}, base={base}")
        return []
    result = int(math.log(n) / math.log(base))
    return [result % tarot.NUM_CARDS]


def op_pairs_add(indices):
    """Pairwise addition of consecutive cards, mod 78."""
    return [(indices[i] + indices[i + 1]) % tarot.NUM_CARDS for i in range(len(indices) - 1)]


def op_pairs_subt(indices):
    """Pairwise subtraction of consecutive cards, mod 78."""
    return [(indices[i] - indices[i + 1]) % tarot.NUM_CARDS for i in range(len(indices) - 1)]


def op_pairs_mult(indices):
    """Pairwise multiplication of consecutive cards, mod 78."""
    return [(indices[i] * indices[i + 1]) % tarot.NUM_CARDS for i in range(len(indices) - 1)]


OPERATIONS = {
    "add": op_add,
    "subt": op_subt,
    "mult": op_mult,
    "div": op_div,
    "exp": op_exp,
    "log": op_log,
    "root": op_root,
    "pvd": op_pvd,
    "factor": op_factor,
    "digits": op_digits,
    "pairs+": op_pairs_add,
    "pairs-": op_pairs_subt,
    "pairs*": op_pairs_mult,
}


def parse_cards(line):
    """Parse a line of comma-separated card tokens into indices."""
    tokens = [t.strip() for t in line.split(",")]
    indices = []
    for token in tokens:
        if not token:
            continue
        idx = parse_card(token)
        if idx is None:
            print(f"  unknown card: {token}")
            return None
        indices.append(idx)
    return indices


def run_operations(indices, ops_line):
    """Parse and execute a chain of operations."""
    ops = ops_line.strip().split()
    values = list(indices)

    for op_name in ops:
        fn = OPERATIONS.get(op_name)
        if fn is None:
            print(f"  unknown operation: {op_name}")
            return None
        values = fn(values)
        if values is None:
            return None

    return values


def print_cards(indices):
    """Print a list of card indices with notation."""
    for i in indices:
        if 0 <= i < tarot.NUM_CARDS:
            print(f"  {format_result(i)}")
        else:
            # Large number from digits operation — show raw value
            print(f"  = {i}")


def load_scratch(name):
    """Load braille glyphs from a scratch file (l_div or l_dr)."""
    try:
        with open(name) as f:
            content = f.read().strip()
    except FileNotFoundError:
        print(f"  {name} not found (run divine.py or draw.py first)")
        return None
    if not content:
        print(f"  {name} is empty")
        return None
    return parse_cards(content)


def resolve_input(spec):
    """Resolve an input specifier to a list of card indices.

    Accepts: 'ldiv', 'ldraw', or comma-separated card notation/indices.
    """
    if spec.lower() == "ldiv":
        return load_scratch("l_div")
    if spec.lower() == "ldraw":
        return load_scratch("l_dr")
    return parse_cards(spec)


def print_help():
    print("  Card entry: comma-separated cards")
    print("    Notation: 0-XXI (Major), 1W-K$ (Minor), indices, or braille")
    print("    Suits: W=Wands, C=Cups, S=Swords, $=Pentacles")
    print("    Courts: A=Ace, P=Page, N=Knight, Q=Queen, K=King")
    print("  Sources: ldiv (last divination), ldraw (last draw)")
    print("  Then enter operations to chain:")
    print("    add subt mult div  — reduce all to one value (mod 78)")
    print("    exp             — exponentiation, left-to-right (mod 78)")
    print("    log             — floor(log_base(n)); 1 arg = base 78")
    print("    root            — digital root (base 78)")
    print("    pvd             — place value decomposition (base 78)")
    print("    factor          — show factor pairs")
    print("    digits          — interpret cards as base-78 digits")
    print("    pairs+ pairs- pairs*  — pairwise ops on consecutive cards")
    print()


def repl():
    """Interactive REPL mode."""
    print("mod-78 tarot arithmetic")
    print("enter cards, then operations (type 'help' for commands)")
    print()

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            break
        if line.lower() == "help":
            print_help()
            continue
        if line.lower() == "n":
            continue

        # Step 1: parse cards
        indices = resolve_input(line)
        if indices is None:
            continue

        echo = ", ".join(format_notation(i) for i in indices)
        print(f"  [{echo}] = indices {indices}")

        # Step 2: get operations
        while True:
            try:
                ops_line = input("  op> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not ops_line:
                break
            if ops_line.lower() in ("quit", "exit", "q"):
                return
            if ops_line.lower() == "n":
                break

            result = run_operations(indices, ops_line)
            if result is not None:
                print_cards(result)
                indices = result


def main():
    import sys

    if len(sys.argv) < 2:
        repl()
        return

    # CLI mode: math78.py <cards> [operations]
    indices = resolve_input(sys.argv[1])
    if indices is None:
        sys.exit(1)

    echo = ", ".join(format_notation(i) for i in indices)
    print(f"  [{echo}] = indices {indices}")

    if len(sys.argv) >= 3:
        # Operations are space-separated in argv[2]
        result = run_operations(indices, sys.argv[2].replace(",", " "))
        if result is not None:
            print_cards(result)


if __name__ == "__main__":
    main()
