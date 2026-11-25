# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""Use ABLT from the terminal.

ablt "Abantu basoma ebitabo."            show the pieces
ablt --cuts "Abantu basoma ebitabo."     show where the grammar cuts fall
ablt --ids "Abantu basoma ebitabo."      show the piece numbers
ablt < story.txt                         read lines from a file
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .segmenter import show_cuts
from .tokenizer import ABLT


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ablt",
        description="ABLT: a grammar-first tokenizer for Luganda, by Mathew Sekanjako (Psalms23Wave LLC).",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="text to tokenize; if left out, lines are read from standard input",
    )
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--cuts", action="store_true", help="show the text with | at each grammar cut")
    output.add_argument("--ids", action="store_true", help="show piece numbers instead of pieces")
    credit = f"ablt {__version__}. Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC. Apache-2.0."
    parser.add_argument("--version", action="version", version=credit)
    options = parser.parse_args(arguments)

    lines = [" ".join(options.text)] if options.text else (line.rstrip("\n") for line in sys.stdin)
    tokenizer = None if options.cuts else ABLT()
    for line in lines:
        if options.cuts:
            print(show_cuts(line))
        elif options.ids:
            print(" ".join(str(index) for index in tokenizer.encode(line)))
        else:
            print(" ".join(tokenizer.tokenize(line)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
