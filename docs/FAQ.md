# FAQ — SVARE

**Structural Value Resolution Engine**

**Exact Scientific Calculator and Bounded Deterministic Math Oracle**

---

## A. Purpose and Positioning

### A1. What is SVARE?

SVARE is a structure-first mathematical expression resolver.

For supported expressions, it produces:

- an exact rational value;
- an exact symbolic form;
- a clearly marked decimal approximation of that symbolic form;
- an explicit non-resolved state when a value should not be forced;
- deterministic structure, semantic, and display receipts.

SVARE is available as a Python command-line application and a standalone HTML application.

---

### A2. Why is SVARE described as both a calculator and a math oracle?

For people, SVARE functions as an exact scientific calculator for supported expressions.

For software, SVARE functions as a bounded deterministic math oracle because it returns structured outcomes rather than only a displayed number.

A caller can distinguish exact rational results, exact symbolic results, approximations, singularities, domain refusals, incomplete input, unsupported input, resource limits, and implementation failures.

The word **oracle** is used in this bounded engineering sense. SVARE is not a universal source of mathematical truth.

---

### A3. What is the central structure-first principle?

SVARE separates three questions:

```text
What structure was submitted?
What exact value or explicit state did it resolve to?
How was that result displayed?
```

A concise conceptual rule is:

```text
value_visible iff structure_uniquely_resolves
```

In the reference implementation, a value is displayed only when the supported expression resolves to an exact rational or exact symbolic result within the published rules and resource limits.

---

### A4. What does “correctness without computation dependency” mean?

It does not mean that the software performs no computation.

The reference engines perform:

- parsing;
- normalization;
- exact integer and rational operations;
- symbolic rule application;
- high-precision decimal approximation;
- display formatting;
- receipt generation.

The narrower claim is that exact semantic identity is not created by binary floating-point approximation or display formatting. The semantic result is established before decimal presentation.

---

### A5. Does SVARE remove arithmetic?

No.

Arithmetic remains part of the input language and implementation.

SVARE adds a structure, semantic, state, and receipt model around supported arithmetic and scientific expressions.

---

### A6. Does SVARE replace conventional calculators or mathematics libraries?

No.

SVARE is useful where exact rational handling, bounded symbolic resolution, explicit states, and reproducible receipts are valuable.

General-purpose calculators, numerical libraries, computer algebra systems, theorem provers, and domain-specific tools remain appropriate for their own scopes.

---

### A7. Is SVARE a computer algebra system?

No.

SVARE supports a bounded set of exact symbolic rules. It does not attempt complete algebraic simplification, equation solving, calculus, matrices, tensors, units, or general theorem proving.

---

### A8. What does SVARE claim?

SVARE claims that, within its published grammar, rules, policies, and resource limits:

- finite decimal and rational arithmetic can be resolved exactly;
- supported symbolic forms can retain exact semantic identity;
- symbolic decimal displays can be marked clearly as approximations;
- non-resolved conditions can be represented explicitly;
- the same supported input under the same version and policy produces reproducible outcomes and receipts;
- Python and HTML can be tested against a shared conformance corpus.

---

### A9. What does SVARE not claim?

SVARE does not claim to be:

- a universal mathematical oracle;
- a complete computer algebra system;
- a theorem prover;
- a formally verified platform;
- certified interval arithmetic;
- a complex-number engine;
- a calculus system;
- a units or dimensional-analysis engine;
- certified for financial, medical, engineering, legal, or safety-critical decisions.

---

## B. Resolution Model

### B1. What are the resolution layers?

SVARE uses four visible stages:

```text
surface expression
        ↓
canonical structure
        ↓
exact semantic value or explicit state
        ↓
decimal or status display
```

---

### B2. What is the surface expression?

The surface expression is the text submitted by the user.

Example:

```text
sin(pi/6) + sqrt(2)
```

---

### B3. What is the canonical structure?

The canonical structure is the versioned structural encoding produced after parsing.

It preserves the submitted operation structure for deterministic inspection and receipt generation.

---

### B4. What is the semantic layer?

The semantic layer contains one of the following:

- an exact rational value;
- an exact symbolic form;
- an explicit resolution state.

The semantic layer is independent of the selected decimal display precision.

---

### B5. What is the display layer?

The display layer presents the semantic result as:

- an exact terminating decimal;
- exact repeating-rational notation;
- a symbolic decimal approximation marked with `≈`;
- an explicit status message.

The display layer does not replace the exact semantic identity.

---

### B6. How are finite decimals handled?

Finite decimal literals are converted directly into exact rational values.

Example:

```text
1.0000000000000001 - 1
```

resolves to:

```text
Resolved value          : 0.0000000000000001
Exact mathematical form : 1/10000000000000000
State                   : RESOLVED_EXACT_RATIONAL
```

The result is not derived from binary floating-point subtraction.

---

### B7. How are repeating rationals displayed?

Example:

```text
1/3
```

displays:

```text
0.3…
```

The ellipsis represents an exact repeating rational expansion. It is not a symbolic approximation.

The display kind is:

```text
EXACT_RATIONAL_REPEATING
```

---

### B8. How are irrational and transcendental values handled?

Supported values such as `sqrt(2)`, `pi`, and `ln(2)` remain exact symbolic forms.

A decimal representation may also be shown, but it is marked with `≈`.

Example:

```text
sqrt(2)
```

may be represented as:

```text
Exact mathematical form : sqrt(2)
Resolved value          : ≈ 1.41421356237309504880168872421
```

---

### B9. Does an approximation become part of exact identity?

No.

The exact symbolic form defines semantic identity.

Display precision and the visible decimal representation participate in the display receipt, not the structure or semantic certificate.

---

### B10. What is bounded recognition?

SVARE applies a published set of exact identities rather than unrestricted symbolic algebra.

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

This difference reflects the bounded rule set. It does not imply a different mathematical truth.

---

### B11. Can symbolic cancellation be exact?

Yes, when the canonical symbolic terms are recognized as identical.

Examples:

```text
pi - pi
ln(2) - ln(2)
pi + e - pi - e
```

Each resolves exactly to `0` without using a numerical near-zero threshold.

---

## C. Supported Input

### C1. Which numeric literals are supported?

Examples:

```text
12
-7
0.125
1.0000000000000001
6.02e23
```

Numeric literals use ASCII digits `0-9`.

Non-ASCII numeral characters are rejected consistently by the Python and HTML engines.

---

### C2. Are identifiers case-sensitive?

No.

Function and constant identifiers are case-insensitive.

Examples:

```text
sin(pi/6)
SIN(PI/6)
Pi
PI
```

---

### C3. How is `E` interpreted?

A standalone `e` or `E` is the mathematical constant.

Inside a numeric literal, `e` or `E` is the scientific-notation exponent marker.

Examples:

```text
E   -> mathematical constant e
2E2 -> 200
```

---

### C4. Which operators are supported?

```text
+   addition
-   subtraction and unary negation
*   multiplication
/   division
%   floor-division remainder
^   exponentiation
**  exponentiation
```

Parentheses are supported.

Implicit multiplication is not supported.

```text
2 * pi   supported
2pi      unsupported
```

---

### C5. What is the exponentiation policy?

Exponentiation is right-associative.

Unary minus has lower precedence than exponentiation.

Examples:

```text
2^3^2   -> 512
-2^2    -> -4
(-2)^2  -> 4
2^-2    -> 1/4
```

---

### C6. How does remainder work?

Remainder follows floor-division semantics and the divisor sign.

```text
-3 % 2   -> 1
3 % -2   -> -1
-3 % -2  -> -1
```

---

### C7. Which constants are supported?

```text
pi
e
tau
```

---

### C8. Which functions are supported?

Arithmetic and integer functions:

```text
sqrt abs sign floor ceil trunc round min max gcd lcm
```

Trigonometric functions:

```text
sin cos tan asin acos atan
```

Logarithmic and exponential functions:

```text
ln log10 log exp
```

Angle helpers:

```text
deg rad
```

---

### C9. What does `log` mean?

```text
log(x)
```

means the natural logarithm.

```text
log(value, base)
```

uses the supplied base.

Examples:

```text
log(81,3) -> 4
log(8,2)  -> 3
```

---

### C10. What do `deg` and `rad` mean?

`deg(x)` interprets `x` as degrees and converts it exactly to radians:

```text
deg(x) = x * pi / 180
sin(deg(30)) -> 1/2
```

`rad(x)` means that the supplied value is already in radians:

```text
rad(x) = x
sin(rad(pi/6)) -> 1/2
```

---

### C11. What happens when a function receives the wrong number of arguments?

Invalid function arity returns:

```text
CONFLICT
```

Examples include:

```text
atan(1,2)
min()
```

---

## D. Resolution States and Display Kinds

### D1. Which resolution states exist in v10.0.6?

| State | Meaning |
|---|---|
| `RESOLVED_EXACT_RATIONAL` | The semantic result is an exact rational value. |
| `RESOLVED_EXACT_SYMBOLIC` | The semantic result is retained in exact symbolic form. |
| `SINGULAR` | The expression reaches a recognized singular point. |
| `FORBIDDEN` | The expression violates the supported real-number domain or an operation rule. |
| `INDETERMINATE` | The structure has no unique value, such as `0/0` or `0^0`. |
| `INCOMPLETE` | The submitted expression is unfinished. |
| `CONFLICT` | The syntax, token structure, argument structure, or function arity is invalid. |
| `ABSTAIN` | A name or function is outside the bounded registry. |
| `LIMIT_EXCEEDED` | A published deterministic resource boundary was reached. |
| `INTERNAL_ERROR` | An unexpected implementation failure occurred. |

---

### D2. What is `SINGULAR`?

`SINGULAR` identifies a recognized singular point.

Example:

```text
tan(pi/2)
```

returns:

```text
SINGULAR
```

with no numeric value.

---

### D3. What is `FORBIDDEN`?

`FORBIDDEN` identifies an operation outside the supported real-number domain or an invalid operation rule.

Examples:

```text
sqrt(-1)
1/0
0^(-1/2)
```

No numeric value is exposed.

---

### D4. What is `INDETERMINATE`?

`INDETERMINATE` identifies a structure with no unique value.

Examples:

```text
0/0
0^0
```

---

### D5. What is `INCOMPLETE`?

`INCOMPLETE` identifies unfinished input.

Example:

```text
(1 + 2
```

---

### D6. What is `CONFLICT`?

`CONFLICT` identifies invalid syntax, token structure, argument structure, unsupported characters, or invalid function arity.

It is distinct from an implementation failure.

---

### D7. What is `ABSTAIN`?

`ABSTAIN` means that a submitted name or function is outside the bounded registry.

Example:

```text
unknown_function(2)
```

---

### D8. What is `LIMIT_EXCEEDED`?

`LIMIT_EXCEEDED` means that a published resource boundary was reached.

Example:

```text
2^2^2^2^2^2
```

returns:

```text
State      : LIMIT_EXCEEDED
Error code : MAX_EXACT_RESULT_DIGITS
```

The resolver refuses the prohibited result instead of attempting to construct it.

---

### D9. What is `INTERNAL_ERROR`?

`INTERNAL_ERROR` identifies an unexpected implementation failure.

It is not reported as `CONFLICT`.

---

### D10. Which display kinds exist?

| Display kind | Meaning |
|---|---|
| `EXACT_RATIONAL_TERMINATING` | Exact integer or terminating rational decimal. |
| `EXACT_RATIONAL_REPEATING` | Exact rational shown with repeating ellipsis notation. |
| `APPROXIMATE_SYMBOLIC` | Decimal approximation of an exact symbolic form, displayed with `≈`. |
| `UNDEFINED` | Singular or forbidden result. |
| `INDETERMINATE` | No unique value. |
| `INCOMPLETE` | Incomplete submission. |
| `NOT_EVALUATED` | Resolver abstained. |
| `LIMIT_EXCEEDED` | Resource policy refused resolution. |
| `INTERNAL_ERROR` | Unexpected implementation failure. |
| `UNRESOLVED` | Other unresolved submission. |

---

## E. Determinism and Receipts

### E1. Is SVARE deterministic?

Yes, within the same application, canonicalization, semantic-rule, certificate-schema, and resource-policy versions.

The same supported input and display precision produce reproducible:

- state;
- exact semantic result;
- canonical structure;
- structure certificate;
- semantic certificate;
- display receipt.

---

### E2. Does evaluation order never matter?

The submitted operator structure, precedence, and associativity matter.

SVARE does not claim that differently structured expressions always produce the same result.

The deterministic claim is that the same supported structure under the same published policies produces the same outcome.

---

### E3. What is the structure certificate?

The structure certificate is a SHA-256 receipt for the versioned canonical submitted structure.

It identifies how the expression was structurally represented.

---

### E4. What is the semantic certificate?

The semantic certificate is a SHA-256 receipt for the versioned canonical semantic result and state.

Recognized equivalent expressions may share a semantic certificate while retaining different structure certificates.

Example:

```text
sin(pi/6)
sin(deg(30))
1/2
```

All resolve to the exact semantic value `1/2`.

---

### E5. What is the display receipt?

The display receipt identifies the visible representation using:

- application version;
- semantic certificate;
- selected precision;
- display kind;
- displayed value;
- displayed mathematical form and label.

Changing display precision can change the display receipt without changing the structure or semantic certificate.

---

### E6. Are the receipts digital signatures or mathematical proofs?

No.

The SHA-256 receipts are deterministic fingerprints of versioned resolution artifacts.

They are not:

- digital signatures;
- proofs of authorship;
- formal proofs of mathematical correctness;
- protection against a compromised implementation;
- substitutes for independent validation.

---

### E7. Do mathematically equivalent expressions always share the same semantic certificate?

Only when the equivalence is recognized by the bounded semantic rules.

SVARE does not claim complete equivalence recognition.

---

### E8. Are receipts stable across all future versions?

Not necessarily.

SVARE reports separate version identifiers for canonicalization, semantic rules, certificate schema, and resource policy.

A policy change may intentionally change a receipt.

---

## F. Precision, Limits, and Safety

### F1. What precision range is supported?

The resolver precision range is 6 through 120 significant digits.

Requested Python precision values outside this range are clamped.

```text
--precision 5   -> effective precision 6
--precision 500 -> effective precision 120
```

The HTML interface provides presets of:

```text
12, 18, 30, 48, and 72 significant digits
```

---

### F2. Does precision affect exact identity?

No.

Precision affects the decimal display and display receipt.

It does not change the canonical structure or semantic certificate.

---

### F3. Are symbolic decimal approximations certified intervals?

No.

The symbolic decimal layer does not provide formal lower-and-upper enclosures.

The `≈` marker identifies a deterministic decimal approximation of an exact symbolic form.

---

### F4. What resource limits apply?

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

---

### F5. Why are resource limits explicit?

They make refusal deterministic and prevent the resolver from silently attempting prohibited constructions.

Limit results include stable error codes such as:

```text
MAX_EXACT_RESULT_DIGITS
MAX_NESTING_DEPTH
MAX_TOKEN_COUNT
```

---

### F6. Is SVARE safe for direct public network exposure?

The grammar does not use Python `eval`, JavaScript `eval`, or arbitrary source-code execution.

However, a public high-volume service should still add:

- process isolation;
- request throttling;
- memory limits;
- execution deadlines;
- monitoring.

The reference applications are not a complete operational security layer.

---

### F7. Is SVARE certified for financial or safety-critical use?

No.

Independent validation, operational controls, domain review, and applicable regulatory assurance are required before using any software in high-stakes systems.

---

## G. Python and HTML Applications

### G1. Where are the current files?

```text
demo_extension_v10_0_6/SVARE_v10_0_6.py
demo_extension_v10_0_6/SVARE_v10_0_6.html
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
demo_extension_v10_0_6/SVARE_v10_0_6_validation.json
```

---

### G2. How do I run the Python self-test?

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --self-test
```

The v10.0.6 self-test contains:

```text
59 shared conformance vectors
4 release invariants
63 total checks
```

---

### G3. How do I resolve an expression?

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "1.0000000000000001 - 1"
```

---

### G4. How do I request JSON output?

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
```

---

### G5. How do I choose display precision?

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --precision 60 "sqrt(2) + ln(2)"
```

---

### G6. How do I list supported functions?

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --list-functions
```

---

### G7. How do I use interactive mode?

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py
```

---

### G8. What are the Python requirements?

Python 3.9 or later is required.

The Python engine uses only the Python standard library.

---

### G9. How do I run the HTML application?

Open:

```text
demo_extension_v10_0_6/SVARE_v10_0_6.html
```

The application runs locally without a server or network connection.

---

### G10. Does the HTML application use a third-party component?

Yes.

The HTML file embeds Decimal.js for browser-side high-precision decimal approximation.

Decimal.js remains subject to its own MIT license and attribution. SVARE itself is governed by the repository license.

---

### G11. Why is Decimal.js used?

Standard JavaScript `Number` arithmetic does not provide the required high-precision symbolic decimal displays.

Decimal.js supports deterministic browser-side approximations while SVARE retains exact rational and symbolic identity in its own resolution model.

---

### G12. Can Decimal.js be removed?

It can be replaced by a dedicated SVARE high-precision browser kernel, but deleting it without a replacement would reduce decimal precision and break current Python–HTML parity.

The published v10.0.6 file retains the validated embedded component.

---

### G13. What are the command exit codes?

| Exit code | Meaning |
|---|---|
| `0` | Expression resolved, or an informational command completed successfully. |
| `1` | Self-test failed. |
| `2` | The expression returned a non-`RESOLVED_*` state. |

---

## H. Validation and Reproducibility

### H1. What is the shared conformance corpus?

The file:

```text
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
```

contains 59 shared vectors covering exact arithmetic, symbolic identities, explicit states, operator semantics, resource limits, repeating rationals, zero-base powers, and ASCII numeral policy.

---

### H2. What is the vector payload hash?

```text
76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69
```

Both engines embed the same vector payload and verify this hash during self-test.

---

### H3. What does the validation report record?

The v10.0.6 validation report records:

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

---

### H4. Are the self-tests formal verification?

No.

They are regression, conformance, and cross-runtime parity checks.

They do not constitute exhaustive formal proof.

---

### H5. How are frozen files verified?

Published SHA-256 file fingerprints are listed in:

```text
VERIFY/FREEZE_DEMO_SHA256.txt
```

Verification instructions are provided in:

```text
VERIFY/VERIFY.txt
```

---

## I. Scope and Use

### I1. What can SVARE currently do well?

SVARE is designed for:

- exact finite-decimal and rational resolution;
- bounded exact symbolic scientific resolution;
- explicit handling of invalid or unresolved input;
- reproducible JSON receipts;
- deterministic regression fixtures;
- Python–HTML parity experiments;
- bounded mathematical tool-use prototypes.

---

### I2. What remains outside the current scope?

Current v10.0.6 does not provide:

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

### I3. Is the Python engine an installable library?

Not yet.

It is currently a reference command-line engine that can emit structured JSON.

Installable packaging, a stable function API, schemas, receipt verification helpers, and agent-framework adapters are possible future directions.

---

### I4. Can AI systems call SVARE?

An AI system can invoke the Python command-line engine and consume its JSON output.

The current distribution does not yet provide a packaged OpenAI, Anthropic, or MCP adapter.

---

### I5. Is absence of a number a failure?

Not necessarily.

Explicit states such as `SINGULAR`, `FORBIDDEN`, `INDETERMINATE`, `INCOMPLETE`, `ABSTAIN`, and `LIMIT_EXCEEDED` preserve meaningful distinctions instead of forcing a numeric answer.

---

## J. License and Attribution

### J1. How is the reference implementation licensed?

The Python and HTML reference implementation is governed by the **SVARE Open Use License** in the repository `LICENSE` file.

It permits commercial and non-commercial use, study, reproduction, distribution, modification, implementation, extension, and deployment, subject to the stated conditions.

---

### J2. How are architecture and documentation licensed?

Unless otherwise stated, SVARE architecture descriptions and documentation are licensed under:

```text
Creative Commons Attribution-NonCommercial 4.0 International
CC BY-NC 4.0
```

---

### J3. Is SVARE an MIT-licensed project?

No.

Decimal.js, embedded in the standalone HTML file, remains subject to its own MIT license and attribution.

That third-party license applies to Decimal.js and does not make the SVARE reference implementation an MIT-licensed project.

---

### J4. Is attribution required?

Attribution to SVARE is encouraged but not required for use of the reference implementation under the stated Open Use terms.

Architecture and documentation under CC BY-NC 4.0 require appropriate attribution.

Applicable third-party notices and attributions must be retained.

---

## K. Structural Context

### K1. Is SVARE part of a broader structure-first research direction?

Yes.

SVARE examines whether exact mathematical identity, explicit states, and reproducible receipts can be organized through visible structural resolution.

This context is conceptual. Runtime behaviour is defined by the v10.0.6 reference files and published policies.

---

### K2. What is the concise SVARE invariant?

Within the same published versions and policies:

```text
same supported input structure
-> same canonical structure
-> same resolution state
-> same exact semantic result
-> same version-scoped receipts
```

Display precision additionally determines the display receipt.

---

### K3. What is the simplest summary of SVARE?

SVARE is an exact scientific calculator for supported expressions and a bounded deterministic math oracle with explicit states and reproducible receipts.
