# SVARE Challenge — Exactness, Explicit States, and Reproducible Receipts

**Structural Value Resolution Engine**

**Release: v10.0.6**

---

## Purpose

This document presents reproducible cases that exercise the central properties of SVARE:

- exact finite-decimal and rational resolution;
- preservation of supported exact symbolic meaning;
- separation of semantic identity from decimal display;
- explicit non-resolved states;
- deterministic structure, semantic, and display receipts;
- bounded refusal under published resource limits;
- parity between the Python and HTML reference engines.

The challenge is not a speed benchmark.

It does not claim that every conventional calculator or numerical system loses precision. Arbitrary-precision rational systems, symbolic systems, and correctly configured decimal libraries may produce equally exact results.

The comparisons below use ordinary IEEE 754 binary64 behaviour where stated. Their purpose is to show why exact structure and explicit states are useful when binary floating-point approximation is not the intended semantic model.

---

## Current Reference Files

```text
demo_extension_v10_0_6/SVARE_v10_0_6.py
demo_extension_v10_0_6/SVARE_v10_0_6.html
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
demo_extension_v10_0_6/SVARE_v10_0_6_validation.json
```

Run an expression with:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "EXPRESSION"
```

---

## What the Challenge Tests

The challenge asks whether SVARE v10.0.6 preserves these invariants under its published grammar, policies, and resource limits:

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

The challenge also tests whether:

```text
non-resolved conditions
-> explicit states
-> no forced numeric value
```

---

# Challenge Cases

## Case 1 — Exact Decimal Addition

### Expression

```text
0.1 + 0.2
```

### Typical IEEE 754 binary64 example

Python binary floating-point evaluation displays:

```text
0.30000000000000004
```

### SVARE v10.0.6

```text
Resolved value          : 0.3
Exact mathematical form : 3/10
State                   : RESOLVED_EXACT_RATIONAL
Display kind            : EXACT_RATIONAL_TERMINATING
```

### Property tested

Finite decimal literals are converted directly into exact rational values:

```text
0.1 -> 1/10
0.2 -> 1/5
```

Therefore:

```text
1/10 + 1/5 = 3/10
```

The result is not established through binary floating-point addition.

---

## Case 2 — Exact Residual Preservation

### Expression

```text
1.0000000000000001 - 1.0000000000000000
```

### Typical IEEE 754 binary64 example

Python binary floating-point evaluation produces:

```text
0.0
```

because both surface literals map to the same binary64 value.

### SVARE v10.0.6

```text
Resolved value          : 0.0000000000000001
Exact mathematical form : 1/10000000000000000
State                   : RESOLVED_EXACT_RATIONAL
Display kind            : EXACT_RATIONAL_TERMINATING
```

### Property tested

The decimal residual remains exact because the input literals are parsed as rational structures rather than rounded first to binary64.

---

## Case 3 — Small Contribution Beside a Large Magnitude

### Expression

```text
0.0000000000000000001 + 999999999999999999
```

### Typical IEEE 754 binary64 example

Python binary floating-point evaluation displays:

```text
1e+18
```

The smaller contribution is not visible in the binary64 result.

### SVARE v10.0.6

```text
Resolved value          : 999999999999999999.0000000000000000001
Exact mathematical form : 9999999999999999990000000000000000001/10000000000000000000
State                   : RESOLVED_EXACT_RATIONAL
Display kind            : EXACT_RATIONAL_TERMINATING
```

### Property tested

Exact rational resolution preserves both magnitude contributions.

---

## Case 4 — Grouping Sensitivity in Binary Floating Point

### Expressions

```text
(1e16 + -1e16) + 1
```

```text
1e16 + (-1e16 + 1)
```

### Typical IEEE 754 binary64 example

Python binary floating-point evaluation produces:

```text
(1e16 + -1e16) + 1 -> 1.0
1e16 + (-1e16 + 1) -> 0.0
```

### SVARE v10.0.6

Both expressions resolve exactly to:

```text
Resolved value          : 1
Exact mathematical form : 1
State                   : RESOLVED_EXACT_RATIONAL
```

Their structure certificates differ because their submitted structures differ.

Their semantic certificates are identical because both resolve to the same exact semantic value.

### Property tested

SVARE does not claim that grouping is irrelevant.

It preserves the submitted grouping, but exact rational arithmetic avoids the grouping-sensitive rounding seen in binary64 for this case.

---

## Case 5 — Exact Repeating Rational Display

### Expression

```text
2 / 3
```

### SVARE v10.0.6

```text
Resolved value          : 0.6…
Exact mathematical form : 2/3
State                   : RESOLVED_EXACT_RATIONAL
Display kind            : EXACT_RATIONAL_REPEATING
```

### Property tested

The ellipsis denotes an exact repeating rational expansion.

It is not a rounded symbolic approximation.

The exact semantic identity remains:

```text
2/3
```

---

## Case 6 — Exact Symbolic Meaning and Approximate Display

### Expression

```text
sqrt(2)
```

### SVARE at 30 significant digits

```text
Resolved value          : ≈ 1.41421356237309504880168872421
Exact mathematical form : sqrt(2)
State                   : RESOLVED_EXACT_SYMBOLIC
Display kind            : APPROXIMATE_SYMBOLIC
```

### SVARE at 60 significant digits

```text
Resolved value          : ≈ 1.41421356237309504880168872420969807856967187537694807317668
Exact mathematical form : sqrt(2)
State                   : RESOLVED_EXACT_SYMBOLIC
Display kind            : APPROXIMATE_SYMBOLIC
```

### Receipt behaviour

The two runs retain the same:

- canonical structure;
- exact symbolic identity;
- structure certificate;
- semantic certificate.

They produce different display receipts because the selected precision and visible approximation differ.

### Property tested

Display precision changes representation, not exact semantic identity.

---

## Case 7 — Exact Symbolic Cancellation

### Expressions

```text
pi - pi
ln(2) - ln(2)
pi + e - pi - e
```

### SVARE v10.0.6

Each resolves to:

```text
Resolved value          : 0
Exact mathematical form : 0
State                   : RESOLVED_EXACT_RATIONAL
Display kind            : EXACT_RATIONAL_TERMINATING
```

### Property tested

Identical canonical symbolic additive terms are combined with exact rational coefficients.

No numerical near-zero tolerance is used.

---

## Case 8 — Bounded Symbolic Recognition

### Expressions

```text
sqrt(2)^2
```

```text
sqrt(2) * sqrt(2)
```

### SVARE v10.0.6

The first expression resolves exactly:

```text
sqrt(2)^2 -> 2
```

The second remains symbolic and displays:

```text
sqrt(2) * sqrt(2) -> ≈ 2
```

### Property tested

SVARE uses a bounded published rule set.

It does not claim complete symbolic equivalence recognition.

The difference is a boundary of implemented recognition, not a claim that the mathematical values differ.

---

## Case 9 — Surface Structure and Semantic Identity

### Expression

```text
(+0.72) - (0.72)
```

### SVARE v10.0.6

```text
Resolved value          : 0
Exact mathematical form : 0
State                   : RESOLVED_EXACT_RATIONAL
```

Canonical structure:

```text
SUB(UNARY_PLUS(RAT(18/25)),RAT(18/25))
```

Canonical semantic result:

```text
RAT(0/1)
```

### Property tested

The structure layer preserves submitted unary structure.

The semantic layer records the exact resolved value.

Structure identity and semantic identity are intentionally separate.

---

## Case 10 — Recognized Semantic Equivalence

### Expressions

```text
sin(pi/6)
sin(deg(30))
1/2
```

### SVARE v10.0.6

All three resolve to:

```text
Resolved value          : 0.5
Exact mathematical form : 1/2
State                   : RESOLVED_EXACT_RATIONAL
```

Structure certificates:

```text
sin(pi/6)
5d71e579d8b48a75741773255d23845318b45e0776cd827d1ee8075db7ea1af1

sin(deg(30))
3231e54032fbf00a69c9954afd88449d0333d7842bc55cc86f0afdc3e4a62658

1/2
3f1f77fc711f71ff770967e235dd094f05676037e5c9e65467125a6a6b324920
```

Shared semantic certificate:

```text
ebb862b282b5ce44909f76f40e1146f26a9dddec4af97303276015454c580ada
```

### Property tested

Different recognized structures can retain distinct structure identities while converging to one exact semantic identity.

SVARE does not claim that every mathematically equivalent expression will be recognized as equivalent.

---

## Case 11 — Explicit Non-Resolved States

### Expressions and states

```text
tan(pi/2)           -> SINGULAR
1/0                 -> FORBIDDEN
0/0                 -> INDETERMINATE
0^0                 -> INDETERMINATE
(1 + 2              -> INCOMPLETE
atan(1,2)           -> CONFLICT
unknown_function(2) -> ABSTAIN
```

### Property tested

Different conditions do not collapse into one generic error.

The state model distinguishes:

- a recognized singular point;
- a real-domain or operation refusal;
- a non-unique mathematical structure;
- unfinished input;
- invalid syntax or arity;
- an unsupported name or function.

For every non-`RESOLVED_*` state:

```text
no exact numeric result is forced
```

---

## Case 12 — Resource-Bounded Refusal

### Expression

```text
2^2^2^2^2^2
```

### SVARE v10.0.6

```text
Resolved value : limit exceeded
State          : LIMIT_EXCEEDED
Error code     : MAX_EXACT_RESULT_DIGITS
```

### Property tested

The resolver applies a deterministic result-size policy before attempting the prohibited exact construction.

A resource refusal is not reported as:

- a mathematical conflict;
- an indeterminate value;
- an internal implementation failure.

---

## Case 13 — Operator Policy Is Explicit

### Expressions

```text
2^3^2
-2^2
(-2)^2
2^-2
```

### SVARE v10.0.6

```text
2^3^2   -> 512
-2^2    -> -4
(-2)^2  -> 4
2^-2    -> 1/4
```

### Property tested

SVARE does not claim independence from syntax or operator policy.

It publishes that:

- exponentiation is right-associative;
- unary minus has lower precedence than exponentiation.

The same policy is applied by both reference engines.

---

## Case 14 — Surface Normalization Without Precision Loss

### Expression

```text
-00000.0009 - 9999
```

### SVARE v10.0.6

```text
Resolved value          : -9999.0009
Exact mathematical form : -99990009/10000
State                   : RESOLVED_EXACT_RATIONAL
```

Canonical structure:

```text
SUB(UNARY_MINUS(RAT(9/10000)),RAT(9999/1))
```

### Property tested

Surface formatting is normalized into exact rational structure without changing the mathematical value.

Leading zeros are not treated as semantic magnitude.

---

## Case 15 — Character Policy Is Deterministic

SVARE numeric literals use ASCII digits:

```text
0-9
```

A non-ASCII numeral character is not silently interpreted as an ASCII digit.

It returns:

```text
State               : CONFLICT
Error code          : UNSUPPORTED_CHARACTER
Canonical structure : UNRESOLVED
```

under the same policy in Python and HTML.

### Property tested

Cross-runtime agreement includes character admission, parser-state classification, and error coding—not only arithmetic output.

---

# Reproducibility Challenge

Run the same supported expression twice:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
```

At the same precision and under the same release, compare:

```text
state
exact_value
structure_canonical
semantic_canonical
structure_certificate_sha256
semantic_certificate_sha256
display_receipt_sha256
```

Expected result:

```text
all compared fields are identical
```

---

# Precision-Isolation Challenge

Run:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --precision 30 --json "sqrt(2)"
python demo_extension_v10_0_6/SVARE_v10_0_6.py --precision 60 --json "sqrt(2)"
```

Expected:

```text
same structure_canonical
same semantic_canonical
same structure_certificate_sha256
same semantic_certificate_sha256
different visible approximation
different display_receipt_sha256
```

This demonstrates the separation between exact semantic identity and display precision.

---

# Cross-Runtime Challenge

The release contains one shared vector corpus:

```text
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
```

Vector payload SHA-256:

```text
76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69
```

The release validation records:

```text
Shared conformance vectors : 59
Python self-test checks    : 63
Python failures            : 0
HTML self-test checks      : 63
HTML failures              : 0
Differential expressions   : 97
Differential mismatches    : 0
Browser page errors        : 0
```

These results are reproducible conformance and parity evidence.

They are not exhaustive formal verification.

---

# Falsification Criteria

A result would falsify a stated v10.0.6 guarantee if, under the same release files, policies, submitted input, and applicable precision, any of the following occurred:

1. The same submitted input produced a different parsed structure or parser state.
2. The same submitted input produced a different canonical structure or canonical unresolved placeholder.
3. The same successfully parsed structure produced a different resolution state or exact semantic result.
4. The same canonical semantic result and state produced a different semantic certificate.
5. For resolved exact results, the same semantic result, application version, precision, and display policy produced different visible output or display receipts.
6. For an explicit state whose display includes the submitted expression, the same state, submitted surface, application version, precision, and display policy produced different status displays or display receipts.
7. A non-resolved state exposed a fabricated exact numeric result.
8. Python and HTML disagreed on a published conformance vector.
9. An exact rational result differed from the corresponding rational arithmetic result.
10. A published resource boundary produced an uncontrolled implementation failure instead of its documented explicit state.

A failure of a case would identify a defect in the implementation, policy, validation corpus, or stated guarantee.

It would not establish a universal conclusion about every structure-first or exact-arithmetic system.

---

# What the Challenge Does Not Establish

This document does not establish that SVARE is:

- faster than conventional calculators;
- superior to every arbitrary-precision library;
- a complete computer algebra system;
- capable of recognizing every mathematical equivalence;
- a theorem prover;
- formally verified;
- certified interval arithmetic;
- suitable for high-stakes deployment without independent validation.

The challenge demonstrates the behaviour of the published v10.0.6 reference implementation within its stated scope.

---

# Final Statement

SVARE does not replace computation with a claim of computation-free execution.

It separates:

```text
submitted structure
exact semantic result or explicit state
visible decimal or status display
```

Its challenge is practical and reproducible:

- preserve exact finite-decimal and rational meaning;
- retain supported exact symbolic identity;
- mark symbolic approximations visibly;
- distinguish non-resolved conditions;
- refuse prohibited resource use explicitly;
- produce stable version-scoped receipts;
- maintain Python–HTML agreement on the published test corpus.
