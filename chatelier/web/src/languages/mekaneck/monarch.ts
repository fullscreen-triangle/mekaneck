/**
 * Monaco language definition for `.mck`.
 *
 * Syntax highlighting, completions and live diagnostics, the last driven by
 * the local checker in `./checker.ts` — which is pinned to the binary by the
 * shared fixture suite, so the editor cannot disagree with the compiler about
 * whether a program is well formed.
 */

import { diagnose, type FloorValues } from "./checker";
import { KEYWORDS } from "./lexer";

export const LANGUAGE_ID = "mekaneck";

/** Monarch tokenizer. Deliberately close to `lexer.ts` in what it recognises. */
export const monarchLanguage = {
  defaultToken: "",
  ignoreCase: false,
  keywords: [...KEYWORDS],

  // The clauses that carry the language's two commitments, highlighted
  // distinctly so they read as structure rather than as ordinary keywords.
  structural: ["seek", "excluding", "via", "until", "closure"],

  tokenizer: {
    root: [
      [/#.*$/, "comment"],
      [
        /[a-zA-Z_]\w*/,
        {
          cases: {
            "@structural": "keyword.control",
            "@keywords": "keyword",
            "@default": "identifier",
          },
        },
      ],
      [/"[^"]*"/, "string"],
      [/"[^"]*$/, "string.invalid"],
      [/\d+\.\d+|\d+/, "number"],
      [/[{}()]/, "@brackets"],
      [/[,;:=]/, "delimiter"],
      [/\s+/, "white"],
    ],
  },
} as const;

export const languageConfiguration = {
  comments: { lineComment: "#" },
  brackets: [
    ["{", "}"],
    ["(", ")"],
  ] as [string, string][],
  autoClosingPairs: [
    { open: "{", close: "}" },
    { open: "(", close: ")" },
    { open: '"', close: '"' },
  ],
  surroundingPairs: [
    { open: "{", close: "}" },
    { open: "(", close: ")" },
    { open: '"', close: '"' },
  ],
};

/** A snippet completion, in Monaco's shape but without importing Monaco. */
export interface Completion {
  label: string;
  insertText: string;
  documentation: string;
  /** Monaco's `CompletionItemKind`; 27 = Snippet, 14 = Keyword. */
  kind: number;
}

/**
 * Completions.
 *
 * The `seek` snippet includes `excluding` and a three-catalyst `via` because
 * those are what the checker requires — a snippet that produced a program the
 * compiler rejects would be teaching the wrong shape.
 */
export const completions: Completion[] = [
  {
    label: "substrate",
    kind: 27,
    insertText: [
      "substrate ${1:Name} {",
      "  receivers  : ${2:recordings()};",
      "  observable : ${3:coherence_index()};",
      "  events     : ${4:label_change()};",
      "  floor      : ${5:asymptotic_separation()};",
      "}",
    ].join("\n"),
    documentation:
      "The four obligations. The floor is the one with empirical content: " +
      "asymptotic_separation() can return a non-positive value and so can be " +
      "contradicted by data; sample_minimum() cannot.",
  },
  {
    label: "seek",
    kind: 27,
    insertText: [
      "seek        ${1:target()}",
      "excluding   ${2:all_other()}",
      "via         (${3:a}, ${4:b}, ${5:c})",
      "until       closure",
    ].join("\n"),
    documentation:
      "The single primitive. `excluding` is mandatory — a target is not " +
      "determined by a positive description alone. Termination is by closure: " +
      "the seek stops when no remaining catalyst reaches a new cell.",
  },
  {
    label: "catalyst-triad",
    kind: 27,
    insertText: [
      "catalyst ${1:a} : ${4:f()} independent ${2:b}, ${3:c};",
      "catalyst ${2:b} : ${5:g()} independent ${1:a}, ${3:c};",
      "catalyst ${3:c} : ${6:h()} independent ${1:a}, ${2:b};",
    ].join("\n"),
    documentation:
      "Three mutually independent catalysts. Fewer than three cannot survive " +
      "the loss of a member, so the type checker rejects them.",
  },
  ...KEYWORDS.map((k) => ({
    label: k,
    kind: 14,
    insertText: k,
    documentation: "",
  })),
];

/** A diagnostic in Monaco's marker shape. */
export interface Marker {
  message: string;
  startLineNumber: number;
  startColumn: number;
  endLineNumber: number;
  endColumn: number;
  /** Monaco's `MarkerSeverity`: 8 = Error, 4 = Warning. */
  severity: number;
}

/**
 * Diagnostics as Monaco markers.
 *
 * Runs locally, so it is instant and works before a binary is paired. It is a
 * mirror, not the authority: the binary re-checks on `run`.
 */
export function markers(source: string, floors: FloorValues = {}): Marker[] {
  return diagnose(source, floors).map((d) => {
    const end = endPosition(source, d.span.end);
    return {
      message: d.message,
      startLineNumber: d.line,
      startColumn: d.column,
      endLineNumber: end.line,
      // Monaco's end column is exclusive; a zero-width span still needs to
      // mark at least one character or it renders as nothing.
      endColumn: Math.max(end.column, d.column + 1),
      severity: d.severity === "error" ? 8 : 4,
    };
  });
}

function endPosition(src: string, offset: number): { line: number; column: number } {
  let line = 1;
  let column = 1;
  for (let i = 0; i < src.length && i < offset; i += 1) {
    if (src[i] === "\n") {
      line += 1;
      column = 1;
    } else {
      column += 1;
    }
  }
  return { line, column };
}
