"""
Merge all .bib files from the mekaneck project into a single monograph.bib.
Deduplicates entries by citation key; last-seen entry wins on collision.
Run from the monograph/ directory:
    python bibliography/merge_bibs.py
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent.parent  # mekaneck/

BIB_GLOBS = [
    "docs/**/*.bib",
    "mekaneck/docs/**/*.bib",
    "blindhorse/docs/**/*.bib",
    "parable/docs/**/*.bib",
]

EXCLUDE_PATTERNS = [
    "Notes.bib",   # Zotero note files — not real .bib
]


def collect_bib_files(root: pathlib.Path) -> list[pathlib.Path]:
    files = []
    for glob in BIB_GLOBS:
        for f in sorted(root.glob(glob)):
            if any(ex in f.name for ex in EXCLUDE_PATTERNS):
                continue
            files.append(f)
    return files


def parse_entries(text: str) -> list[str]:
    """Split a .bib file into individual entries."""
    entries = []
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0 and start is None:
                # Look back for @Type
                pre = text[max(0, i-40):i]
                if re.search(r'@\w+\s*$', pre):
                    start = text.rfind('@', 0, i)
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                entries.append(text[start:i+1].strip())
                start = None
    return entries


def entry_key(entry: str) -> str | None:
    m = re.match(r'@\w+\s*\{\s*([^,\s]+)', entry)
    return m.group(1) if m else None


def merge(root: pathlib.Path, output: pathlib.Path) -> None:
    files = collect_bib_files(root)
    print(f"Found {len(files)} .bib files")

    seen: dict[str, str] = {}
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  WARNING: could not read {f}: {e}", file=sys.stderr)
            continue
        entries = parse_entries(text)
        for entry in entries:
            key = entry_key(entry)
            if key:
                seen[key] = entry
            else:
                # Preamble / string definitions — keep first occurrence
                pass

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as fh:
        fh.write(f"%% monograph.bib — merged from {len(files)} source files\n")
        fh.write(f"%% {len(seen)} unique entries\n\n")
        for entry in seen.values():
            fh.write(entry)
            fh.write("\n\n")

    print(f"Written {len(seen)} entries to {output}")


if __name__ == "__main__":
    merge(ROOT, ROOT / "monograph" / "bibliography" / "monograph.bib")
