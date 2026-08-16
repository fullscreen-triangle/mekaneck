"""
Replace the inline figure blocks in each manuscript with an \input of its
caption file, so the captions live in one place and the papers stay in sync.
"""
import io
import os
import re

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")

PAIRS = [
    ("catalyst-algebra", "catalyst-residual-algebra.tex", "figures/catalyst-captions"),
    ("catalyst-micro-kernel", "catalyst-micro-kernel.tex", "figures/kernel-captions"),
    ("mekaneck-primitives", "mekaneck-substrate-primitives.tex", "figures/primitive-captions"),
]

# matches a whole figure* environment
FIG_RE = re.compile(r"\\begin\{figure\*\}.*?\\end\{figure\*\}\s*", re.DOTALL)

for d, main, cap in PAIRS:
    p = os.path.join(DOCS, d, main)
    s = io.open(p, encoding="utf-8").read()

    n_before = len(FIG_RE.findall(s))
    s = FIG_RE.sub("", s)

    inp = "\\input{" + cap + "}\n\n"
    anchor = "\\subsection{Results}\n\\label{sec:results}"
    if anchor in s and inp not in s:
        s = s.replace(anchor, inp + anchor, 1)

    io.open(p, "w", encoding="utf-8").write(s)
    print(f"{d}: removed {n_before} inline figure blocks, inserted \\input{{{cap}}}")
