#!/usr/bin/env python3
"""Interactive tarot divination REPL.

Press any key to draw a card. Press 'q' to quit and see your spread.
Use --no-repeats to draw without replacement.
"""

import argparse
import sys
import tty
import termios

import tarot


def getch():
    """Read a single character from stdin without echoing."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main():
    parser = argparse.ArgumentParser(description="Interactive tarot divination")
    parser.add_argument("--no-repeats", action="store_true", help="each card can only appear once")
    args = parser.parse_args()

    spread = []
    seen = set()

    print("╔══════════════════════════════════════╗")
    print("║   /dev/urandom tarot divination      ║")
    print("║   Press any key to draw a card       ║")
    print("║   Press 'q' to quit                  ║")
    print("╚══════════════════════════════════════╝")
    print()

    while True:
        ch = getch()
        if ch in ('q', 'Q', '\x03'):  # q or Ctrl-C
            break

        if args.no_repeats and len(seen) >= tarot.NUM_CARDS:
            print("  All 78 cards have been drawn.")
            break

        index = tarot.draw_one()
        if args.no_repeats:
            while index in seen:
                index = tarot.draw_one()
        seen.add(index)
        spread.append(index)
        position = len(spread)
        print(f"  {position}. {tarot.format_card(index)}")

    if spread:
        print()
        print("── your spread ──")
        glyphs = " ".join(tarot.braille(i) for i in spread)
        print(f"  {glyphs}")
        print()
        for pos, index in enumerate(spread, 1):
            print(f"  {pos}. {tarot.format_card(index)}")
    print()


if __name__ == "__main__":
    main()
