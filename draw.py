#!/usr/bin/env python3
"""Draw N tarot cards from /dev/urandom.

Usage: python draw.py [N] [--repeats]
"""

import argparse
import tarot


def main():
    parser = argparse.ArgumentParser(description="Draw tarot cards from /dev/urandom")
    parser.add_argument("n", nargs="?", type=int, default=1, help="number of cards to draw")
    parser.add_argument("--repeats", action="store_true", help="allow the same card to appear more than once")
    args = parser.parse_args()

    indices = tarot.draw(args.n, replace=args.repeats)
    for index in indices:
        print(tarot.format_card(index))

    with open("l_dr", "w") as f:
        f.write(",".join(tarot.braille(i) for i in indices))


if __name__ == "__main__":
    main()
