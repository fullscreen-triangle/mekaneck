"""Verify every \\Cref in the caption files resolves to a label in its paper."""
import io
import os
import re

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")

PAIRS = [
    ("catalyst-algebra", "catalyst-residual-algebra.tex", "figures/catalyst-captions.tex"),
    ("catalyst-micro-kernel", "catalyst-micro-kernel.tex", "figures/kernel-captions.tex"),
    ("mekaneck-primitives", "mekaneck-substrate-primitives.tex", "figures/primitive-captions.tex"),
]

LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
CREF_RE = re.compile(r"\\[Cc]ref\{([^}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics\[[^\]]*\]\{([^}]+)\}")

ok = True
for d, main, cap in PAIRS:
    base = os.path.join(DOCS, d)
    body = io.open(os.path.join(base, main), encoding="utf-8").read()
    caps = io.open(os.path.join(base, cap), encoding="utf-8").read()

    labels = set(LABEL_RE.findall(body)) | set(LABEL_RE.findall(caps))
    refs = set()
    for m in CREF_RE.findall(caps):
        refs.update(x.strip() for x in m.split(","))
    missing = sorted(r for r in refs if r not in labels)

    imgs = GRAPHIC_RE.findall(caps)
    absent = [g for g in imgs
              if not os.path.exists(os.path.join(base, g))]

    print(f"{d}:")
    print(f"  crefs={len(refs)}  missing={missing or 'none'}")
    print(f"  figures={len(imgs)}  absent={absent or 'none'}")
    if missing or absent:
        ok = False

print("\nALL RESOLVE" if ok else "\nPROBLEMS FOUND")
