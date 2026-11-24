#!/usr/bin/env python3
"""THE MILLSTREAM - NI24 entry carrier (Final 6, @agusproblem).

The front page (entry.png, 1024x1024) was drawn in this session by
compose.py (Pillow, original flat scenes, dotted world map from real
polygons). This program is the submitted entrypoint: standard library
only, no network. It copies the finished image to the output directory,
so both runs write byte-identical bytes. The output keeps the name
entry.png either way, as the competition requires.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
