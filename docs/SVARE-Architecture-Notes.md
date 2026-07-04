# SVARE — Architecture Notes

**Structural Value Resolution Engine**

**Exact Scientific Calculator and Bounded Deterministic Math Oracle**

**Release: v10.0.6**

---

## 1. Architectural Purpose

SVARE is a structure-first mathematical expression resolver.

Its architecture separates:

```text
submitted expression
canonical structure
exact semantic result or explicit state
visible display
version-scoped receipts
```

The central design goal is to preserve exact rational or exact symbolic meaning before decimal presentation.

SVARE does not claim that computation disappears.

It provides a disciplined architecture in which:

- supported finite-decimal and rational expressions resolve exactly;
- supported symbolic forms retain exact semantic identity;
- symbolic decimal output is marked as approximate;
- invalid, unsupported, incomplete, singular, indeterminate, and resource-prohibited inputs remain explicit;
- deterministic receipts identify structure, semantic result, and display;
- Python and HTML implementations can be checked against one shared conformance corpus.

---

## 2. Architectural Positioning

SVARE serves two related roles.

For people:

```text
exact scientific calculator
```

For software:

```text
bounded deterministic math oracle
```

The word **oracle** is used in a bounded engineering sense.

SVARE is not:

- a universal mathematical oracle;
- a complete computer algebra system;
- a theorem prover;
- a formally verified platform;
- a complex-number engine;
- a calculus engine;
- a units or dimensional-analysis engine.

---

## 3. Core Architectural Principle

SVARE separates exact meaning from visible representation.

```text
surface expression
        ↓
canonical structure
        ↓
exact semantic value or explicit state
        ↓
decimal or status display
```

A concise conceptual rule is:

```text
value_visible iff structure_uniquely_resolves
```

In the reference implementation, value visibility means that the supported expression resolves to:

- `RESOLVED_EXACT_RATIONAL`; or
- `RESOLVED_EXACT_SYMBOLIC`.

All other outcomes remain explicit states.

---

## 4. Versioned Architecture

SVARE v10.0.6 reports separate identifiers for its principal policies.

```text
application_version         = 10.0.6
canonicalization_version    = 2
semantic_rules_version      = 2
certificate_schema_version  = 2
resource_policy_version     = 2
vector_schema_version       = 2
```

This separation allows future changes to be identified precisely.

A change in canonicalization does not necessarily imply the same kind of change as:

- a semantic-rule update;
- a certificate-schema update;
- a resource-policy update;
- a display-policy update.

Receipts are therefore version-scoped.

---

## 5. High-Level Runtime Architecture

```text
┌──────────────────────────────┐
│ Surface Expression           │
│ User or software input       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Tokenizer and Parser         │
│ Grammar, precedence, arity   │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│ Parsed Expression Tree       │
│ Submitted operation shape    │
└──────────┬─────────────┬─────┘
           │             │
           ↓             ↓
┌──────────────────┐  ┌──────────────────────────┐
│ Structural       │  │ Semantic Resolver        │
│ Canonicalizer    │  │ Rational, symbolic,      │
│                  │  │ or explicit state        │
└────────┬─────────┘  └────────────┬─────────────┘
         ↓                         ↓
┌──────────────────┐  ┌──────────────────────────┐
│ Canonical        │  │ Exact Semantic Result    │
│ Structure        │  │ or Explicit State        │
└────────┬─────────┘  └────────────┬─────────────┘
         │                         ↓
         │              ┌──────────────────────────┐
         │              │ Display Resolver         │
         │              │ Exact, repeating,        │
         │              │ approximate, or status   │
         │              └────────────┬─────────────┘
         │                           ↓
         │              ┌──────────────────────────┐
         │              │ Visible Display          │
         │              └────────────┬─────────────┘
         │                           │
         └──────────────┬────────────┘
                        ↓
             ┌──────────────────────────┐
             │ Receipt Layer            │
             │ Structure, semantic,     │
             │ and display receipts     │
             └──────────────────────────┘
```

The canonical structure and semantic result are deterministic outputs derived from the same parsed expression tree.

The semantic resolver evaluates the parsed tree. It does not evaluate the serialized canonical-structure string.

For explicit states whose visible presentation includes the evaluated or submitted expression, the display resolver also uses the surface expression.


---

## 6. Surface Expression Layer

The surface-expression layer accepts mathematical text.

Examples:

```text
1.0000000000000001 - 1
sin(pi/6)
sqrt(2)^2
log(81,3)
2^3^2
```

The surface layer is not treated as the final semantic identity.

It is parsed under fixed grammar and policy rules.

---

## 7. Tokenization and Parsing

### 7.1 Parser responsibilities

The parser determines:

- valid tokens;
- numeric literals;
- constants;
- function names;
- parentheses;
- operator precedence;
- operator associativity;
- unary operators;
- argument structure;
- incomplete input;
- invalid syntax.

### 7.2 Operator policy

Supported operators:

```text
+   addition
-   subtraction and unary negation
*   multiplication
/   division
%   floor-division remainder
^   exponentiation
**  exponentiation
```

Exponentiation is right-associative.

Unary minus has lower precedence than exponentiation.

Examples:

```text
2^3^2   -> 512
-2^2    -> -4
(-2)^2  -> 4
2^-2    -> 1/4
```

### 7.3 Identifier policy

Function and constant identifiers are case-insensitive.

Examples:

```text
sin(pi/6)
SIN(PI/6)
Pi
PI
```

A standalone `e` or `E` is the mathematical constant.

Inside a numeric literal, `e` or `E` is the scientific-notation exponent marker.

```text
E   -> mathematical constant e
2E2 -> 200
```

### 7.4 Character policy

Numeric literals use ASCII digits:

```text
0-9
```

Unsupported numeral characters return an explicit state rather than being interpreted inconsistently.

### 7.5 No arbitrary source execution

The grammar does not use:

- Python `eval`;
- JavaScript `eval`;
- arbitrary source-code execution.

This narrows the accepted language to the published mathematical grammar.

---

## 8. Parsed Expression Tree

The parser produces a structured expression tree.

The implementation-level parsed node kinds represent:

```text
number
name
unary operation
binary operation
function call
```

The tree preserves:

* operator order;
* parentheses as reflected in the resulting operation tree;
* precedence;
* associativity;
* function argument order.

Encodings such as:

```text
RAT(...)
ADD(...)
SUB(...)
MUL(...)
DIV(...)
POW(...)
CALL_SQRT(...)
CALL_SIN(...)
```

belong to the canonical-structure layer described in Section 9. They are not the parser’s original node-kind names.

SVARE does not claim that arbitrary reordering preserves meaning.

For example:

```text
1 - 2 != 2 - 1
```

The valid determinism claim is:

```text
same supported structure under the same policies
-> same outcome
```

---

## 9. Structural Canonicalization

The canonicalizer converts the parsed tree into a versioned structural encoding.

Its responsibilities include:

- stable node naming;
- stable child ordering where defined;
- exact rational normalization;
- deterministic symbolic representation;
- stable structural material for structure-certificate payload construction;

Canonicalization does not depend on:

- random values;
- current time;
- execution history;
- external network services;
- display precision.

Therefore:

```text
same parsed structure
-> same canonical structure
```

under the same canonicalization version.

---

## 10. Semantic Resolution Layer

The semantic resolver produces one of three outcome classes:

```text
exact rational value
exact symbolic form
explicit resolution state
```

The semantic layer is independent of the selected decimal display precision.

---

## 11. Exact Rational Kernel

### 11.1 Literal conversion

Accepted integers and finite decimals are converted directly into exact rationals.

Examples:

```text
12                  -> 12/1
0.125               -> 1/8
1.0000000000000001  -> 10000000000000001/10000000000000000
```

No binary floating-point conversion is required to establish these values.

### 11.2 Rational operations

For exact rationals:

```text
a/b
c/d
```

SVARE applies exact integer formulas.

```text
addition       -> (ad + bc) / bd
subtraction    -> (ad - bc) / bd
multiplication -> ac / bd
division       -> ad / bc, when c != 0
```

Results are normalized by exact integer arithmetic.

### 11.3 Exact rational example

```text
1.0000000000000001 - 1
```

resolves to:

```text
Resolved value          : 0.0000000000000001
Exact mathematical form : 1/10000000000000000
State                   : RESOLVED_EXACT_RATIONAL
```

---

## 12. Symbolic Resolution Layer

SVARE preserves exact symbolic identity for supported values and expressions.

Examples include:

```text
pi
e
tau
sqrt(2)
ln(2)
1/6 * pi
```

Published exact identities may reduce a symbolic expression to an exact rational or simpler symbolic form.

Examples:

```text
sin(pi/6)   -> 1/2
cos(pi)     -> -1
tan(pi/4)   -> 1
sqrt(81/25) -> 9/5
sqrt(2)^2   -> 2
exp(ln(7))  -> 7
log10(1000) -> 3
log(81,3)   -> 4
```

The symbolic rule set is intentionally bounded.

SVARE does not claim complete symbolic equivalence recognition.

---

## 13. Bounded Recognition

The semantic engine applies published rules rather than unrestricted symbolic algebra.

Example:

```text
sqrt(2)^2
```

resolves exactly to:

```text
2
```

In v10.0.6:

```text
sqrt(2) * sqrt(2)
```

remains symbolic and displays:

```text
≈ 2
```

This reflects the boundary of the implemented rule set.

It does not imply a different mathematical truth.

---

## 14. Exact Symbolic Cancellation

Identical canonical symbolic additive terms may cancel exactly.

Examples:

```text
pi - pi
ln(2) - ln(2)
pi + e - pi - e
```

Each resolves to the exact rational value:

```text
0
```

This cancellation uses exact canonical symbolic identity.

It does not depend on a numerical near-zero threshold.

---

## 15. Resolution States

SVARE v10.0.6 exposes the following states:

| State | Meaning |
|---|---|
| `RESOLVED_EXACT_RATIONAL` | The semantic result is an exact rational value. |
| `RESOLVED_EXACT_SYMBOLIC` | The semantic result is retained in exact symbolic form. |
| `SINGULAR` | The expression reaches a recognized singular point. |
| `FORBIDDEN` | The expression violates the supported real-number domain or an operation rule. |
| `INDETERMINATE` | The structure has no unique value. |
| `INCOMPLETE` | The submitted expression is unfinished. |
| `CONFLICT` | The syntax, token structure, argument structure, or function arity is invalid. |
| `ABSTAIN` | A name or function is outside the bounded registry. |
| `LIMIT_EXCEEDED` | A published deterministic resource boundary was reached. |
| `INTERNAL_ERROR` | An unexpected implementation failure occurred. |

Examples:

```text
tan(pi/2)           -> SINGULAR
sqrt(-1)            -> FORBIDDEN
1/0                 -> FORBIDDEN
0/0                 -> INDETERMINATE
0^0                 -> INDETERMINATE
(1 + 2              -> INCOMPLETE
atan(1,2)           -> CONFLICT
unknown_function(2) -> ABSTAIN
2^2^2^2^2^2         -> LIMIT_EXCEEDED
```

For every non-`RESOLVED_*` state:

```text
no exact numeric result is forced
```

---

## 16. Display Architecture

The display layer converts a semantic result into a visible representation.

For explicit states whose visible presentation includes the evaluated or submitted expression, it also uses the surface expression.

The display layer does not replace the semantic result.

### 16.1 Display kinds

| Display kind | Meaning |
|---|---|
| `EXACT_RATIONAL_TERMINATING` | Exact integer or terminating rational decimal. |
| `EXACT_RATIONAL_REPEATING` | Exact rational shown with repeating ellipsis notation. |
| `APPROXIMATE_SYMBOLIC` | Decimal approximation of an exact symbolic form, marked with `≈`. |
| `UNDEFINED` | Singular or forbidden result. |
| `INDETERMINATE` | No unique value. |
| `INCOMPLETE` | Incomplete submission. |
| `NOT_EVALUATED` | Resolver abstained. |
| `LIMIT_EXCEEDED` | Resource policy refused resolution. |
| `INTERNAL_ERROR` | Unexpected implementation failure. |
| `UNRESOLVED` | Other unresolved submission. |

### 16.2 Exact terminating display

```text
1/8 -> 0.125
```

### 16.3 Exact repeating display

```text
1/3 -> 0.3…
1/6 -> 0.16…
```

The ellipsis identifies an exact repeating rational.

It is not a symbolic approximation.

### 16.4 Symbolic approximation display

```text
sqrt(2) -> ≈ 1.41421356237309504880168872421
```

The `≈` marker is mandatory for symbolic decimal approximations.

---

## 17. Precision Policy

The resolver precision range is:

```text
6 through 120 significant digits
```

Requested Python values outside this range are clamped.

```text
--precision 5   -> effective precision 6
--precision 500 -> effective precision 120
```

The HTML interface provides presets of:

```text
12, 18, 30, 48, and 72 significant digits
```

Precision affects:

- symbolic decimal display;
- display receipt.

Precision does not affect:

- canonical structure;
- exact rational identity;
- exact symbolic identity;
- semantic certificate.

---

## 18. Receipt Architecture

SVARE emits three SHA-256 receipts.

### 18.1 Structure certificate

The structure certificate identifies the versioned canonical submitted structure.

```text
structure_certificate = H(
    certificate-schema version,
    canonicalization version,
    canonical structure
)
```

### 18.2 Semantic certificate

The semantic certificate identifies the versioned canonical semantic result and state.

```text
semantic_certificate = H(
    certificate-schema version,
    semantic-rules version,
    canonical semantic result,
    resolution state
)
```

### 18.3 Display receipt

The display receipt identifies the visible representation.

```text
display_receipt = H(
    application version,
    certificate-schema version,
    semantic certificate,
    precision,
    display kind,
    displayed value,
    displayed label,
    displayed mathematical form
)
```

### 18.4 Receipt consequence

Under identical versions and policies:

```text
same canonical structure
-> same structure certificate

same canonical semantic result and state
-> same semantic certificate

same resolved semantic result and display policy
-> same display receipt

same explicit state
+ same applicable submitted surface
+ same display policy
-> same display receipt
```

Recognized equivalent expressions may share a semantic certificate while retaining different structure certificates.

Example:

```text
sin(pi/6)
sin(deg(30))
1/2
```

All resolve to the exact semantic value:

```text
1/2
```

---

## 19. Receipt Boundary

The receipts are deterministic fingerprints of versioned resolution artifacts.

They are not:

- digital signatures;
- proofs of authorship;
- formal mathematical proofs;
- protection against a compromised implementation;
- substitutes for independent validation.

A hash confirms identity of the hashed payload under the stated schema.

It does not independently prove that the implementation or mathematical rules are correct.

---

## 20. Determinism Model

Within the same application and policy versions:

```text
same submitted input
-> same parsed structure or parser state
-> same canonical structure or canonical unresolved placeholder
-> same resolution state
-> same exact semantic result or explicit state
-> same structure and semantic certificates
```

For resolved exact results, at the same display precision:

```text
same exact semantic result
-> same visible display
-> same display receipt
```

For explicit states whose visible presentation includes the submitted expression:

```text
same explicit state
+ same submitted surface
+ same display precision
-> same status display
-> same display receipt
```

This guarantee is version-scoped.

A change to any of the following may intentionally change an outcome or receipt:

* canonicalization;
* semantic rules;
* certificate schema;
* resource policy;
* application version;
* display policy.

---

## 21. Resource Policy

SVARE applies explicit deterministic boundaries.

| Boundary | Limit |
|---|---:|
| Input characters | 10,000 |
| Tokens | 512 |
| Nesting depth | 128 |
| AST nodes | 512 |
| Operation budget | 4,096 |
| Literal digits | 4,000 |
| Absolute literal exponent | 50,000 |
| Exact result digits | 50,000 |

When a boundary is exceeded, SVARE returns:

```text
LIMIT_EXCEEDED
```

with a stable error code.

Example:

```text
2^2^2^2^2^2
```

returns:

```text
State      : LIMIT_EXCEEDED
Error code : MAX_EXACT_RESULT_DIGITS
```

The resolver refuses the prohibited result instead of attempting an unbounded construction.

---

## 22. Security Boundary

The expression grammar does not invoke arbitrary source-code execution.

However, the reference applications are not a complete operational security platform.

A public service should add:

- process isolation;
- request throttling;
- memory limits;
- execution deadlines;
- monitoring;
- deployment-specific authentication and authorization where required.

The architecture does not claim certification for hostile, high-volume, or safety-critical deployment.

---

## 23. Python Reference Engine

Current Python file:

```text
demo_extension_v10_0_6/SVARE_v10_0_6.py
```

Characteristics:

- Python 3.9 or later;
- Python standard library only;
- command-line expression resolution;
- interactive mode;
- JSON output;
- precision selection;
- function listing;
- self-test execution;
- deterministic exit codes.

Example:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
```

The Python engine is currently a reference command-line application.

It is not yet distributed as an installable library with a stable public function API.

---

## 24. Standalone HTML Application

Current HTML file:

```text
demo_extension_v10_0_6/SVARE_v10_0_6.html
```

Characteristics:

- single-file local application;
- no server required;
- no network connection required;
- embedded conformance vectors;
- browser-side self-test;
- exact rational and symbolic resolution model;
- high-precision symbolic decimal display.

The HTML application embeds Decimal.js for high-precision browser-side decimal approximation.

Decimal.js remains subject to its own MIT license and attribution.

The Decimal.js license applies only to that component.

It does not make SVARE an MIT-licensed project.

---

## 25. Shared Conformance Architecture

The Python and HTML engines use one shared vector corpus.

Current vector file:

```text
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
```

The corpus contains:

```text
59 shared conformance vectors
```

The embedded vector payload SHA-256 is:

```text
76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69
```

Both engines verify the same payload during self-test.

---

## 26. Validation Architecture

Current validation file:

```text
demo_extension_v10_0_6/SVARE_v10_0_6_validation.json
```

The v10.0.6 release validation records:

```text
Python self-test checks        : 63
Python failures                : 0
HTML self-test checks          : 63
HTML failures                  : 0
Shared conformance vectors     : 59
Differential expressions       : 97
Differential mismatches        : 0
Browser page errors            : 0
```

These results provide regression, conformance, and cross-runtime parity evidence.

They do not constitute exhaustive formal verification.

---

## 27. Supported Mathematical Scope

### 27.1 Constants

```text
pi
e
tau
```

### 27.2 Arithmetic and integer functions

```text
sqrt abs sign floor ceil trunc round min max gcd lcm
```

### 27.3 Trigonometric functions

```text
sin cos tan asin acos atan
```

### 27.4 Logarithmic and exponential functions

```text
ln log10 log exp
```

### 27.5 Angle helpers

```text
deg rad
```

### 27.6 Current exclusions

SVARE v10.0.6 does not provide:

- complete algebraic simplification;
- equation solving;
- calculus;
- complex numbers;
- matrices or tensors;
- units or dimensional analysis;
- graph reasoning;
- general variable-binding systems;
- formal proof generation.

---

## 28. Architectural Safety Properties

### 28.1 Exactness before display

Exact rational or exact symbolic identity is established before decimal presentation.

### 28.2 Explicit non-resolution

Singular, forbidden, indeterminate, incomplete, unsupported, conflicting, resource-prohibited, and failed inputs remain distinct.

### 28.3 No forced numeric output

A non-resolved state does not become a fabricated number.

### 28.4 Version-scoped reproducibility

Under the same application and policy versions, the same supported input
produces the same outcome and the same structure and semantic certificates.

At the same display precision, it also produces the same display receipt.

### 28.5 Bounded resource refusal

Resource policy prevents prohibited constructions from being attempted without a deterministic boundary.

### 28.6 Cross-runtime evidence

Python and HTML are tested against the same vector corpus and differential expression set.

---

## 29. Architectural Boundaries

The architecture does not establish:

- universal mathematical completeness;
- complete equivalence recognition;
- formal verification of the source code;
- certified interval bounds;
- correctness outside the supported real-number domain;
- immunity to compromised runtime environments;
- suitability for financial, medical, engineering, legal, or safety-critical deployment without independent validation.

---

## 30. Extension Points

The architecture permits future additions such as:

- installable Python packaging;
- a stable callable API;
- formal JSON schemas;
- receipt-verification helpers;
- agent-framework adapters;
- MCP integration;
- additional exact symbolic rules;
- broader conformance corpora;
- independent implementations;
- formal specification work;
- a dedicated browser-side high-precision kernel.

Any such extension should preserve:

- explicit versioning;
- exact-versus-approximate separation;
- explicit resolution states;
- deterministic resource boundaries;
- receipt transparency;
- conformance testing.

---

## 31. Architectural Invariant

Within fixed versions and policies:

```text
same submitted input
-> same parsed structure or parser state
-> same canonical structure or canonical unresolved placeholder
-> same resolution state
-> same exact semantic result or explicit state
-> same structure and semantic certificates
```

For resolved exact results, the same display precision produces the same visible display and display receipt.

For explicit states whose display contains the submitted expression, reproducibility of the display receipt additionally requires the same submitted surface.

---

## Final Architectural Statement

SVARE is a structure-first mathematical resolver.

Its architecture does not claim that computation disappears.

It separates:

```text
submitted structure
exact semantic result or explicit state
visible decimal or status display
```

For supported expressions, exact rational or exact symbolic meaning is resolved before decimal presentation.

For singular, forbidden, indeterminate, incomplete, unsupported, conflicting, resource-prohibited, or failed expressions, SVARE returns an explicit state instead of forcing a numeric answer.
