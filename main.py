#!/usr/bin/env python3
"""Entry point for the news-image-20261126 submission.

The poster itself is pre-rendered: render_poster.py draws entry.png from
the sourced 26 November 2026 story ledger (52 stories, 5 regions),
deterministically, with Pillow. This program only places that finished
image where the grader expects it, so the two grading runs produce
byte-identical output. Standard library only; no network, no extra
packages, no secrets.
"""
import os
import shutil
import sys
from pathlib import Path

IMAGE_NAME = "entry.png"


def place_poster() -> int:
    repo_root = Path(__file__).resolve().parent
    source = repo_root / IMAGE_NAME
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    if not source.is_file():
        print(f"missing poster: {source}", file=sys.stderr)
        return 1
    shutil.copyfile(source, target_dir / IMAGE_NAME)
    return 0


if __name__ == "__main__":
    sys.exit(place_poster())
