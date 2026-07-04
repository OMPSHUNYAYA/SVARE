# SVARE — Quickstart

**Structural Value Resolution Engine**

**Exact Scientific Calculator and Bounded Deterministic Math Oracle**

**Current Release: v10.0.6**

---

## 1. What SVARE Does

SVARE is a structure-first mathematical expression resolver.

For supported expressions, it returns:

- an exact rational value;
- an exact symbolic form;
- a clearly marked symbolic decimal approximation;
- an explicit non-resolved state;
- deterministic structure, semantic, and display receipts.

SVARE is available as:

- a Python command-line application;
- a standalone HTML application.

---

## 2. Current Release Files

```text
demo_extension_v10_0_6/SVARE_v10_0_6.py
demo_extension_v10_0_6/SVARE_v10_0_6.html
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
demo_extension_v10_0_6/SVARE_v10_0_6_validation.json
```

---

## 3. Minimum Requirements

### Python application

- Python 3.9 or later
- Python standard library only
- No installation step required
- No network connection required

### HTML application

- A modern web browser
- No server required
- No network connection required

The HTML application embeds Decimal.js for browser-side high-precision decimal approximation.

---

## 4. Run the Python Self-Test

From the repository root:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --self-test
```

The v10.0.6 self-test contains:

```text
59 shared conformance vectors
4 release invariants
63 total checks
```

A successful run reports that all checks passed.

---

## 5. Resolve an Expression

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "1 + 2 + 3"
```

Expected exact result:

```text
6
```

---

## 6. Resolve a Nested Expression

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "2 * (3 + 4 * (5 - 2))"
```

Expected exact result:

```text
30
```

---

## 7. Preserve a Deep Decimal Residual

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "1.0000000000000001 - 1"
```

Expected semantic result:

```text
Resolved value          : 0.0000000000000001
Exact mathematical form : 1/10000000000000000
State                   : RESOLVED_EXACT_RATIONAL
```

The finite decimal literals are resolved as exact rational values rather than binary floating-point approximations.

---

## 8. Resolve an Exact Symbolic Expression

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "sqrt(2)"
```

Expected result form:

```text
Exact mathematical form : sqrt(2)
State                   : RESOLVED_EXACT_SYMBOLIC
```

The decimal display is marked with:

```text
≈
```

because it is an approximation of the retained exact symbolic form.

---

## 9. Request JSON Output

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
```

JSON output includes fields for:

- state;
- exact value;
- canonical structure;
- canonical semantic result;
- structure certificate;
- semantic certificate;
- display receipt;
- display kind;
- effective precision.

---

## 10. Select Display Precision

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --precision 60 "sqrt(2) + ln(2)"
```

The resolver precision range is:

```text
6 through 120 significant digits
```

Requested Python values outside this range are clamped.

```text
--precision 5   -> effective precision 6
--precision 500 -> effective precision 120
```

Display precision affects symbolic decimal presentation and the display receipt.

It does not alter the canonical structure or semantic certificate.

---

## 11. Use Interactive Mode

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py
```

Enter expressions at the prompt.

Exit using the command shown by the application.

---

## 12. List Supported Functions

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --list-functions
```

Supported constants:

```text
pi
e
tau
```

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

## 13. Open the HTML Application

Open this file in a modern browser:

```text
demo_extension_v10_0_6/SVARE_v10_0_6.html
```

The application runs locally as a single file.

It provides:

- expression entry;
- exact rational and symbolic results;
- symbolic decimal approximations;
- explicit states;
- precision presets;
- receipt inspection;
- browser-side self-tests.

The interface provides precision presets of:

```text
12, 18, 30, 48, and 72 significant digits
```

---

## 14. Resolution Layers

SVARE separates:

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

In v10.0.6, a value is visible when the semantic result is:

```text
RESOLVED_EXACT_RATIONAL
```

or:

```text
RESOLVED_EXACT_SYMBOLIC
```

---

## 15. Resolution States

| State | Meaning |
|---|---|
| `RESOLVED_EXACT_RATIONAL` | Exact rational result. |
| `RESOLVED_EXACT_SYMBOLIC` | Exact symbolic result. |
| `SINGULAR` | Recognized singular point. |
| `FORBIDDEN` | Unsupported real-domain operation or invalid operation rule. |
| `INDETERMINATE` | No unique mathematical value. |
| `INCOMPLETE` | Unfinished input. |
| `CONFLICT` | Invalid syntax, token structure, argument structure, or arity. |
| `ABSTAIN` | Name or function outside the bounded registry. |
| `LIMIT_EXCEEDED` | Published resource boundary reached. |
| `INTERNAL_ERROR` | Unexpected implementation failure. |

---

## 16. Representative State Tests

### Singular point

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "tan(pi/2)"
```

Expected state:

```text
SINGULAR
```

### Forbidden operation

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "1/0"
```

Expected state:

```text
FORBIDDEN
```

### Indeterminate structure

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "0/0"
```

Expected state:

```text
INDETERMINATE
```

### Incomplete input

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "(1 + 2"
```

Expected state:

```text
INCOMPLETE
```

### Unsupported function

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "unknown_function(2)"
```

Expected state:

```text
ABSTAIN
```

### Resource refusal

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "2^2^2^2^2^2"
```

Expected result:

```text
State      : LIMIT_EXCEEDED
Error code : MAX_EXACT_RESULT_DIGITS
```

---

## 17. Exact Repeating Rational Display

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "2/3"
```

Expected display:

```text
0.6…
```

Expected exact form:

```text
2/3
```

Expected display kind:

```text
EXACT_RATIONAL_REPEATING
```

The ellipsis denotes an exact repeating rational expansion.

It is not a symbolic approximation.

---

## 18. Operator Policy

Exponentiation is right-associative.

Unary minus has lower precedence than exponentiation.

```text
2^3^2   -> 512
-2^2    -> -4
(-2)^2  -> 4
2^-2    -> 1/4
```

Implicit multiplication is not supported.

```text
2 * pi   supported
2pi      unsupported
```

---

## 19. Receipt Model

SVARE emits three SHA-256 receipts.

### Structure certificate

Identifies the versioned canonical submitted structure.

### Semantic certificate

Identifies the versioned exact semantic result and resolution state.

### Display receipt

Identifies the visible representation under the selected precision and display policy.

Recognized equivalent expressions may have different structure certificates and the same semantic certificate.

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

## 20. Determinism Check

Run the same command twice:

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

Expected:

```text
all compared fields are identical
```

---

## 21. Precision-Isolation Check

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

---

## 22. Validation Record

The published v10.0.6 validation records:

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

Shared vector payload SHA-256:

```text
76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69
```

These are regression, conformance, and cross-runtime parity results.

They are not exhaustive formal verification.

---

## 23. Resource Limits

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

A boundary refusal returns:

```text
LIMIT_EXCEEDED
```

with a stable error code.

---

## 24. Command Exit Codes

| Exit code | Meaning |
|---|---|
| `0` | Expression resolved, or an informational command completed successfully. |
| `1` | Self-test failed. |
| `2` | The expression returned a non-`RESOLVED_*` state. |

---

## 25. Current Scope

SVARE v10.0.6 supports:

- exact integer, finite-decimal, and rational resolution;
- bounded exact symbolic resolution;
- chained and nested expressions;
- grouped expressions;
- unary signs;
- scientific notation;
- explicit resolution states;
- deterministic receipts;
- precision-controlled symbolic display;
- Python–HTML conformance testing.

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

## 26. Safety Boundary

SVARE is not certified for:

- financial decisions;
- medical decisions;
- engineering control;
- legal decisions;
- safety-critical deployment.

Independent validation, operational controls, domain review, and applicable regulatory assurance are required before high-stakes use.

---

## 27. Repository Structure

```text
SVARE/
│   LICENSE
│   README.md
│
├── archive/
│   ├── concept_demo/
│   │   └── SVARE_Deterministic_Structural_Cinema_v8_8.py
│   │
│   ├── demo/
│   │   ├── SVARE_HTML_v8_1.html
│   │   └── svare_v8_1.py
│   │
│   └── demo_extension/
│       ├── SVARE_HTML_v9_9.html
│       └── svare_v9_9.py
│
├── demo_extension_v10_0_6/
│   ├── SVARE_v10_0_6.html
│   ├── SVARE_v10_0_6.py
│   ├── SVARE_v10_0_6_validation.json
│   └── SVARE_v10_0_6_vectors.json
│
├── docs/
│   └── ...
│
└── VERIFY/
    ├── FREEZE_DEMO_SHA256.txt
    └── VERIFY.txt
```

The current public release files are under:

```text
demo_extension_v10_0_6/
```

The `archive/demo_extension/` directory contains the earlier v9.9 reference demonstration.

---

## 28. Verification Files

Verification instructions:

```text
VERIFY/VERIFY.txt
```

Published SHA-256 fingerprints:

```text
VERIFY/FREEZE_DEMO_SHA256.txt
```

Use these files to verify the frozen release artifacts.

---

## 29. License

The Python and HTML reference implementation is governed by the repository’s:

```text
SVARE Open Use License
```

Architecture and documentation are licensed under:

```text
Creative Commons Attribution-NonCommercial 4.0 International
CC BY-NC 4.0
```

The standalone HTML application includes Decimal.js.

Decimal.js remains subject to its own MIT license and attribution.

That third-party license applies only to Decimal.js and does not make SVARE an MIT-licensed project.

---

## Final Summary

SVARE v10.0.6 is an exact scientific calculator for supported expressions and a bounded deterministic math oracle for software.

It separates:

```text
submitted structure
exact semantic result or explicit state
visible decimal or status display
```

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
