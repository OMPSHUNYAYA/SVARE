# SVARE

**Structural Value Resolution Engine**

## Exact Scientific Calculator and Bounded Deterministic Math Oracle

**Calculator at the interface. Deterministic, receipt-bearing resolution at the core.**

SVARE resolves supported mathematical expressions into exact rational values, exact symbolic forms, explicit resolution states, and reproducible version-scoped receipts.

![Release](https://img.shields.io/badge/release-v10.0.6-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![HTML](https://img.shields.io/badge/HTML-standalone-orange)
![Domain](https://img.shields.io/badge/domain-real%20numbers-success)
![Receipts](https://img.shields.io/badge/receipts-SHA--256-purple)
![Deterministic](https://img.shields.io/badge/resolution-deterministic-green)
![No Eval](https://img.shields.io/badge/arbitrary%20eval-not%20used-lightgrey)

[![SVARE Verify](https://github.com/OMPSHUNYAYA/SVARE/actions/workflows/svare-verify.yml/badge.svg)](https://github.com/OMPSHUNYAYA/SVARE/actions/workflows/svare-verify.yml)

---

## 🧭 **Visual Overview**

![SVARE Concept Diagram](docs/SVARE_Diagram.png)

The diagram summarizes the bounded SVARE v10.0.6 resolution architecture:

```text
surface expression
        ↓
parsing and canonical structure
        ↓
exact semantic result or explicit state
        ↓
visible display and version-scoped receipts
```

---

## Positioning

SVARE has two complementary roles.

### For people

SVARE is an **exact scientific calculator** with:

- exact finite-decimal and rational arithmetic;
- bounded exact symbolic scientific rules;
- clearly marked symbolic approximations;
- explicit singular, forbidden, indeterminate, incomplete, unsupported, and limited states;
- standalone Python and browser interfaces.

### For software

SVARE is a **bounded deterministic math oracle** for supported expressions.

It returns structured outcomes rather than only a displayed number. A caller can distinguish:

- an exact rational result;
- an exact symbolic result;
- a visible approximation of an exact symbolic form;
- a recognized singularity;
- a real-domain refusal;
- an indeterminate structure;
- an incomplete or conflicting submission;
- an unsupported expression;
- a deterministic resource-limit refusal;
- an unexpected implementation failure.

The word **oracle** is used in this bounded engineering sense. SVARE is not a universal source of mathematical truth, a theorem prover, or a formally verified system.

---

## 🧪 **Current Demonstrations**

### **Current Public Release (v10.0.6)**

- [demo_extension_v10_0_6](demo_extension_v10_0_6/)
- [SVARE_v10_0_6.py](demo_extension_v10_0_6/SVARE_v10_0_6.py)
- [SVARE_v10_0_6.html](demo_extension_v10_0_6/SVARE_v10_0_6.html)
- [SVARE_v10_0_6_vectors.json](demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json)
- [SVARE_v10_0_6_validation.json](demo_extension_v10_0_6/SVARE_v10_0_6_validation.json)


Earlier concept demonstrations and reference versions are preserved under [`archive/`](archive/) for historical continuity.

Videos presenting those earlier versions are historical demonstrations and do not represent the current release.

The current supported release is SVARE v10.0.6 under [`demo_extension_v10_0_6/`](demo_extension_v10_0_6/).

---

## 🔐 **Verification**

- [VERIFY.txt](VERIFY/VERIFY.txt)
- [FREEZE_DEMO_SHA256.txt](VERIFY/FREEZE_DEMO_SHA256.txt)

---

## Overview

SVARE is a reference expression resolver for exact arithmetic and selected scientific functions.

It:

- parses a bounded expression grammar without arbitrary code evaluation;
- converts finite decimal literals directly into exact rational values;
- performs supported rational operations exactly;
- preserves supported irrational and transcendental values in symbolic form;
- recognizes a bounded set of exact scientific identities;
- combines identical symbolic additive terms with exact rational coefficients;
- produces deterministic decimal displays at a selected precision;
- separates structural, semantic, and display receipts;
- returns explicit states for invalid, incomplete, unsupported, limited, or failed resolution;
- applies the same published conformance vectors to Python and HTML.

SVARE is not a full computer algebra system. Its exact symbolic rules are intentionally bounded and exposed through deterministic, versioned behaviour.

---

## Structural Foundation

SVARE preserves the structure-first principle developed in earlier releases:

```text
value_visible iff structure_uniquely_resolves
structure_uniquely_resolves = complete AND consistent
```

The current engine operationalizes that principle through:

```text
surface expression
        ↓
canonical structure
        ↓
exact semantic value or explicit state
        ↓
decimal or status display
```

SVARE does not claim that implementation performs no computation.

The reference engines still perform:

- parsing;
- normalization;
- exact integer and rational operations;
- deterministic rule application;
- symbolic resolution;
- decimal presentation.

The narrower claim is that mathematical identity is not created by floating-point approximation or presentation order. The exact semantic layer is established before the display layer.

---

## Resolution Model

### Structure layer

Represents the submitted expression after parsing and structural canonicalization.

### Semantic layer

Contains an exact rational value, an exact symbolic form, or an explicit resolution state.

### Display layer

Presents the semantic result as:

- an exact terminating decimal;
- exact repeating-decimal notation;
- a symbolic approximation marked with `≈`;
- an explicit status label.

The display layer does not replace the exact semantic identity.

---

## Instant Demonstration

Input:

```text
1.0000000000000001 - 1
```

Result:

```text
Resolved value          : 0.0000000000000001
Exact mathematical form : 1/10000000000000000
State                   : RESOLVED_EXACT_RATIONAL
Display kind            : EXACT_RATIONAL_TERMINATING
```

The decimal literals are converted directly into exact rational structures. The residual is not derived from binary floating-point subtraction.

---

## Demonstrations

### Bounded symbolic scientific resolution

Input:

```text
sin(pi/6) + cos(pi) + sqrt(2) + ln(2)
```

Result at 30 displayed significant digits:

```text
Resolved value          : ≈ 1.60736074293304035821892084567
Exact mathematical form : ln(2) - 1/2 + sqrt(2)
State                   : RESOLVED_EXACT_SYMBOLIC
Display kind            : APPROXIMATE_SYMBOLIC
```

### Exact symbolic cancellation

Inputs:

```text
pi - pi
ln(2) - ln(2)
pi + e - pi - e
```

Each resolves exactly to:

```text
Resolved value          : 0
Exact mathematical form : 0
State                   : RESOLVED_EXACT_RATIONAL
```

No numerical near-zero threshold is used. Cancellation occurs in the semantic layer by combining identical canonical symbolic terms with exact rational coefficients.

### Repeating rational display

Input:

```text
1/3
```

Result:

```text
Resolved value          : 0.3…
Exact mathematical form : 1/3
Display kind            : EXACT_RATIONAL_REPEATING
```

The ellipsis denotes an exact repeating rational expansion. It is not a rounded symbolic approximation.

### Singularity handling

Input:

```text
tan(pi/2)
```

Result:

```text
Resolved value       : undefined
Evaluated expression : tan(pi/2)
State                : SINGULAR
```

### Resource-limit handling

Input:

```text
2^2^2^2^2^2
```

Result:

```text
Resolved value : limit exceeded
State          : LIMIT_EXCEEDED
Error code     : MAX_EXACT_RESULT_DIGITS
```

The resolver refuses the outer power before constructing the prohibited result.

---

## Quick Start

### Python

Run the self-test:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --self-test
```

Expected report:

```json
{
  "all_pass": true,
  "case_count": 63,
  "conformance_vector_sha256": "76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69",
  "external_vectors_checked": true,
  "failure_count": 0,
  "failures": [],
  "version": "10.0.6"
}
```

Resolve an expression:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py "1.0000000000000001 - 1"
```

Select display precision:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --precision 60 "sqrt(2) + ln(2)"
```

Return the complete receipt:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
```

List supported functions:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --list-functions
```

Start interactive mode:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py
```

Python requirements:

- Python 3.9 or later;
- standard library only.

### Standalone HTML

Open:

```text
demo_extension_v10_0_6/SVARE_v10_0_6.html
```

The browser release:

- runs as a standalone local HTML application;
- does not require a server or network connection;
- includes its bounded exact and symbolic resolver;
- provides interface presets of 12, 18, 30, 48, and 72 significant digits;
- applies a resolver precision range of 6 to 120 significant digits;
- exports JSON receipts;
- includes the same 59 conformance vectors used by Python;
- includes a 63-check self-test.

The embedded Decimal.js component is used for browser-side high-precision approximation. Its MIT attribution remains inside the HTML.

---

## Supported Syntax

### Numeric literals

```text
12
-7
0.125
1.0000000000000001
6.02e23
```

Numeric literals use ASCII digits `0-9`. Non-ASCII numeral characters are rejected consistently by both reference engines.

### Case-insensitive identifiers

Function and constant identifiers are case-insensitive.

```text
pi
PI
Pi

sin(pi/6)
SIN(PI/6)
```

A standalone `e` or `E` is the mathematical constant.

```text
E
```

Within a numeric literal, `e` or `E` is the scientific-notation exponent marker.

```text
2E2 -> 200
2e2 -> 200
```

Tokenization distinguishes the standalone constant from the exponent marker inside a numeric literal.

### Operators

```text
+   addition
-   subtraction and unary negation
*   multiplication
/   division
%   floor-division remainder
^   exponentiation
**  exponentiation
```

Parentheses are supported. Implicit multiplication is not supported.

```text
2 * pi    supported
2pi       unsupported
```

### Operator policy

```text
2^3^2    -> 512
-2^2     -> -4
(-2)^2   -> 4
2^-2     -> 1/4
```

Exponentiation is right-associative. Unary minus has lower precedence than exponentiation.

Remainder follows floor-division semantics and the divisor sign:

```text
-3 % 2   -> 1
3 % -2   -> -1
-3 % -2  -> -1
```

### Constants

```text
pi
e
tau
```

### Functions

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

`log(x)` means the natural logarithm.

`log(value, base)` uses the supplied base.

### Angle-helper semantics

`deg(x)` interprets `x` as degrees and converts it exactly to radians:

```text
deg(x) = x * pi / 180
sin(deg(30)) -> 1/2
```

`rad(x)` interprets `x` as an angle already expressed in radians and preserves the supplied value:

```text
rad(x) = x
sin(rad(pi/6)) -> 1/2
sin(rad(30))   -> sin(30 radians)
```

The names are input-unit wrappers. They are not counterparts to Python's `math.degrees()` and `math.radians()` conversion functions.

### Function arity

Functions accept only their published argument counts.

Examples of invalid arity:

```text
atan(1,2)
min()
```

Invalid function arity returns `CONFLICT`.

---

## Precision Policy

Display precision is supported from 6 through 120 significant digits.

Requested values outside this range are clamped:

```text
--precision 5   -> effective precision 6
--precision 500 -> effective precision 120
```

Precision affects the decimal presentation and display receipt. It does not change the canonical structure or exact semantic certificate.

---

## Selected Exact Rules

SVARE includes bounded rules such as:

```text
sin(pi/6)       -> 1/2
cos(pi)         -> -1
tan(pi/4)       -> 1
sin(deg(30))    -> 1/2
sqrt(81/25)     -> 9/5
sqrt(2)^2       -> 2
exp(ln(7))      -> 7
log10(1000)     -> 3
log(81,3)       -> 4
pi - pi         -> 0
2*pi - pi       -> pi
sqrt(2)+sqrt(2) -> 2*sqrt(2)
```

Recognized exact trigonometric identities include supported multiples of `pi/12`.

The symbolic coefficient collector combines identical canonical additive terms. It does not claim general algebraic equivalence across all possible expressions.

---

## Bounded Recognition

SVARE applies a published, bounded identity set rather than general-purpose algebraic simplification.

Mathematically equivalent expressions may therefore receive different resolution classes when an equivalence lies outside the implemented rule set.

Example:

```text
sqrt(2)^2
```

resolves exactly to:

```text
2
```

while:

```text
sqrt(2) * sqrt(2)
```

remains symbolic in v10.0.6 and displays:

```text
≈ 2
```

Other expressions may display an approximation that numerically resembles an exact rational result:

```text
8^(1/3)
ln(4) / ln(2)
min(sqrt(2), 1)
```

The `≈` marker remains mandatory whenever the semantic result is retained symbolically.

A displayed approximation that resembles an integer or rational does not claim that SVARE established that exact identity.

---

## Zero-Base Power Policy

For exact rational exponents:

```text
0^positive -> 0
0^0        -> INDETERMINATE
0^negative -> FORBIDDEN
```

Examples:

```text
0^(1/2)   -> 0
0^(3/2)   -> 0
0^(-1/2)  -> FORBIDDEN
```

---

## Resolution States

| State | Meaning |
|---|---|
| `RESOLVED_EXACT_RATIONAL` | The semantic result is an exact rational value. |
| `RESOLVED_EXACT_SYMBOLIC` | The semantic result is retained in exact symbolic form. |
| `SINGULAR` | The expression reaches a recognized singular point. |
| `FORBIDDEN` | The expression violates the supported real-number domain or an operation rule. |
| `INDETERMINATE` | The structure has no unique value, such as `0/0` or `0^0`. |
| `INCOMPLETE` | The submitted expression is unfinished. |
| `CONFLICT` | The submitted syntax, token structure, argument structure, or function arity is invalid. |
| `ABSTAIN` | A name or function is outside the bounded registry. |
| `LIMIT_EXCEEDED` | A published deterministic resource boundary was reached. |
| `INTERNAL_ERROR` | An unexpected implementation failure occurred. |

`CONFLICT`, `LIMIT_EXCEEDED`, and `INTERNAL_ERROR` are distinct. An implementation failure is not reported as a structural conflict.

---

## Display Kinds

| Display kind | Meaning |
|---|---|
| `EXACT_RATIONAL_TERMINATING` | Exact integer or terminating rational decimal. |
| `EXACT_RATIONAL_REPEATING` | Exact rational shown with repeating ellipsis notation. |
| `APPROXIMATE_SYMBOLIC` | Decimal approximation of an exact symbolic form; displayed with `≈`. |
| `UNDEFINED` | Singular or forbidden real-domain result. |
| `INDETERMINATE` | No unique value. |
| `INCOMPLETE` | Incomplete submission. |
| `NOT_EVALUATED` | Resolver abstained. |
| `LIMIT_EXCEEDED` | Resource policy refused the resolution. |
| `INTERNAL_ERROR` | Unexpected implementation failure. |
| `UNRESOLVED` | Other unresolved submission. |

---

## Exactness and Approximation

### Exact rational layer

Finite decimal literals are converted directly to fractions. Rational operations are exact within the published resource policy.

### Exact symbolic layer

Supported non-rational values remain symbolic, including:

```text
sqrt(2)
ln(2)
1/6 * pi
ln(2) - 1/2 + sqrt(2)
```

### Decimal display layer

- terminating rational decimals are exact;
- repeating rational decimals use exact ellipsis notation;
- symbolic decimals are marked with `≈`;
- display precision does not change structure or semantic certificates;
- display precision and display kind participate in the display receipt.

The symbolic decimal layer is not certified interval arithmetic and does not provide formal lower-and-upper enclosures.

### Very large exact integers

Exact integers are displayed in full while they remain within the configured exact-result limit.

For example, a valid large literal or exact result may produce a correspondingly long decimal display. Scientific-notation presentation for very large exact integers is a possible future display-layer enhancement.

---

## Deterministic Receipts

Every result contains three SHA-256 values.

### Structure certificate

Identifies the versioned canonical submitted structure.

### Semantic certificate

Identifies the versioned canonical semantic result and state.

Recognized equivalent expressions may share a semantic certificate while retaining different structure certificates.

Example:

```text
sin(pi/6)
sin(deg(30))
1/2
```

All resolve to the exact semantic value `1/2`.

### Display receipt

Identifies the visible representation using:

- application version;
- certificate-schema version;
- semantic certificate;
- precision;
- display kind;
- displayed value;
- displayed mathematical form and label.

### Receipt verification boundary

Receipt comparison can confirm deterministic identity under the stated SVARE versions and policies.

Receipt hashes are not:

- digital signatures;
- proofs of authorship;
- formal proofs of mathematical correctness;
- protection against a compromised implementation;
- substitutes for independent validation.

---

## Versioned Policies

The v10.0.6 distribution defines separate identifiers for:

```text
application version        : 10.0.6
canonicalization version   : 2
semantic-rules version     : 2
certificate-schema version : 2
resource-policy version    : 2
vector-schema version      : 2
```

This separation makes the source of future compatibility changes explicit.

---

## Resource Policy

SVARE applies these deterministic boundaries in both engines:

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

Power-size estimation saturates after the configured threshold. A huge exponent is not converted into an enormous diagnostic string.

A limit result includes a stable error code such as:

```text
MAX_EXACT_RESULT_DIGITS
MAX_NESTING_DEPTH
MAX_TOKEN_COUNT
```

A public network service should still add:

- process isolation;
- request throttling;
- memory limits;
- execution deadlines;
- monitoring.

---

## Shared Conformance Corpus

The current distribution includes:

```text
demo_extension_v10_0_6/SVARE_v10_0_6_vectors.json
```

It contains **59 vectors** covering:

- exact arithmetic;
- symbolic identities;
- refusal states;
- operator semantics;
- resource limits;
- exact cancellation;
- repeating decimals;
- zero-base powers;
- zero-valued `gcd` and `lcm` cases;
- ASCII-numeral policy.

Vector payload SHA-256:

```text
76e1fff4dee7fe2361d5d2a869f589e6f413049df3cf394544e371669fb48f69
```

Both Python and HTML embed the same vector payload and verify this hash during their self-tests.

The self-tests contain:

```text
59 shared conformance vectors
4 release invariants
63 total checks per engine
```

The four release invariants verify:

- embedded vector-hash integrity;
- recognized semantic equivalence;
- precision isolation;
- symbolic approximation marking.

The self-tests are regression and parity checks. They are not exhaustive formal verification.

---

## Reproducibility Check

Run the same expression repeatedly:

```bash
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
python demo_extension_v10_0_6/SVARE_v10_0_6.py --json "sin(pi/6)"
```

Under the same release and policy versions, the runs should produce identical:

- state;
- exact semantic value;
- canonical structure;
- structure certificate;
- semantic certificate;
- display receipt at the same precision.

Equivalent expressions may share semantic certificates while retaining different structure certificates.

---

## JSON Receipt

Principal fields include:

```text
engine
version
canonicalization_version
semantic_rules_version
certificate_schema_version
resource_policy_version
conformance_vector_sha256
surface
state
resolution_class
display_kind
display_value
display_mathematical_form
display_form_label
resolved_value
exact_mathematical_form
exact_value
decimal_approximation
precision
precision_unit
note
approximation_note
error_code
internal_error_code
limit
resource_policy
structure_canonical
semantic_canonical
structure_certificate_sha256
semantic_certificate_sha256
display_receipt_sha256
records
function_registry
certificate_policy
operator_policy
```

---

## Security Characteristics

The expression resolvers do not use:

- Python `eval`;
- JavaScript `eval`;
- arbitrary source-code execution.

The grammar admits only implemented operators, constants, functions, and ASCII numeric literals.

The reference implementation remains unsuitable for direct untrusted high-volume network exposure without an operational containment layer.

---

## What SVARE Is

SVARE is:

- an exact scientific calculator for supported expressions;
- an exact rational expression resolver;
- a bounded symbolic scientific resolver;
- a bounded deterministic math oracle;
- a deterministic receipt generator;
- a Python and standalone HTML reference pair;
- a versioned cross-runtime conformance demonstration;
- a structure-first mathematical resolution project.

---

## What SVARE Does Not Claim

SVARE is not:

- a complete computer algebra system;
- a universal mathematical oracle;
- a general theorem prover;
- a formally verified platform;
- certified interval arithmetic;
- a complex-number engine;
- a calculus system;
- a units or dimensional-analysis engine;
- a matrix or tensor package;
- certified for financial, medical, engineering, legal, or safety-critical decisions.

Unsupported identities may remain symbolic or return `ABSTAIN`.

Exact-looking symbolic decimal output is prevented by the mandatory `≈` marker, but the decimal remains an approximation rather than a proof.

---

## Human and Machine Use

### Human-facing use

The Python CLI and standalone HTML application provide:

- direct expression entry;
- visible exact and decimal forms;
- structure inspection;
- state inspection;
- receipt export;
- self-tests.

### Machine-facing use

The current Python engine can emit structured JSON receipts suitable for:

- deterministic regression checks;
- reproducible test fixtures;
- cache-key experiments;
- cross-runtime comparisons;
- bounded tool-use prototypes.

The current release is not yet packaged as an installable agent-framework library.

---

## Planned Agentic Verification Direction

A future minor release is intended to expose SVARE as an auditable mathematical tool for AI and agentic systems.

Planned work includes:

- an installable Python package;
- a stable function API;
- typed resolution results;
- JSON schemas;
- receipt verification;
- explicit exact-only and bounded-symbolic policies;
- deterministic cache-key guidance;
- package installation tests;
- concurrent-call tests;
- generated differential testing;
- receipt-tampering tests;
- OpenAI and Anthropic tool examples;
- an MCP server adapter.

The intended positioning is:

> **Exact calculator for people. Auditable deterministic math oracle for agents.**

These are roadmap items, not current v10.0.6 capabilities.

---

## Exit Codes

| Exit code | Meaning |
|---|---|
| `0` | Expression resolved, or an informational command completed successfully. |
| `1` | Self-test failed. |
| `2` | Expression returned a non-`RESOLVED_*` state. |

Broken output pipes are handled without an avoidable traceback.

---

## Repository Documentation

### User and technical guides

- [Quickstart](docs/Quickstart.md)
- [FAQ](docs/FAQ.md)
- [Proof Sketch](docs/Proof-Sketch.md)
- [SVARE Challenge](docs/SVARE-Challenge.md)
- [SVARE Architecture Notes](docs/SVARE-Architecture-Notes.md)

### Visual references

- [SVARE Concept Diagram](docs/SVARE_Diagram.png)
- [Dependency Elimination Framework](docs/Dependency-Elimination-Framework.png)
- [Shunyaya Structural Stack](docs/Shunyaya-Structural-Stack.png)

Conceptual documents explain the structure-first foundations of SVARE. Runtime behaviour and current commands are defined by the v10.0.6 reference files and this README.

---

## Structural Context

SVARE is part of a broader structure-first research direction:

```text
correctness = resolve(structure)
```

The project asks whether mathematical admissibility and identity can be preserved without treating floating-point approximation or execution-specific presentation as the source of truth.

A concise lineage used across the broader structural work is:

```text
SLANG -> execution
STIME -> time
STINT -> connectivity
STILE -> communication
STRAL -> traversal
SVARE -> mathematical value resolution
```

This context is conceptual. Each project has its own scope, implementation, and validation boundary.

---

## Challenge

Try expressions that expose:

- finite-decimal precision loss in ordinary floating-point workflows;
- exact rational residuals;
- singular points;
- indeterminate structures;
- incomplete syntax;
- unsupported functions;
- resource-limit refusal;
- semantic equivalence across different surface structures.

The purpose is not to claim universal superiority over established mathematics libraries.

The purpose is to test whether SVARE preserves:

```text
same submitted input
-> same parsed structure or parser state
-> same canonical structure or canonical unresolved placeholder
-> same resolution state
-> same exact semantic result or explicit state
-> same structure and semantic certificates
```

For resolved exact results, the same display precision and display policy produce the same visible display and display receipt.

For explicit states whose display includes the submitted expression, reproducibility of the display receipt additionally requires the same submitted surface.

---

## Roadmap

Potential future work includes:

- installable library packaging and a stable function API;
- agentic verification adapters and MCP support;
- higher-precision independent numerical cross-validation with a published corpus;
- property-based testing for rational-kernel invariants;
- deterministic generated differential testing with failure minimization;
- certified interval-enclosed approximations;
- a formal canonicalization and semantic-rule specification;
- reproducible continuous-integration workflows and release badges;
- broader exact symbolic identity coverage;
- optional scientific-notation display for very large exact integers;
- additional language bindings.

Roadmap items are not current capabilities.

---

## 📜 **License**

See: [LICENSE](LICENSE)

**Reference Implementation**

The SVARE reference implementation, including the Python engine and standalone HTML application, is released under the repository’s **SVARE Open Use License**.

You may use, study, reproduce, implement, modify, extend, and deploy the reference implementation, subject to the terms stated in the [LICENSE](LICENSE) file.

SVARE provides a bounded deterministic reference implementation of structural value resolution.

**Architecture and Documentation**

Unless otherwise stated, the SVARE architecture descriptions and documentation are licensed under **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**.

**Third-Party Component**

The standalone HTML application includes Decimal.js. Decimal.js remains subject to its own MIT licence and attribution.

The Decimal.js licence applies only to that third-party component. It does not make the SVARE reference implementation an MIT-licensed project.

---

## Final Statement

SVARE separates three questions:

```text
What structure was submitted?
What exact value or explicit state did it resolve to?
How was that result displayed?
```

For supported expressions, exact rational or exact symbolic meaning is established before decimal presentation.

For invalid, unsupported, indeterminate, or resource-prohibited expressions, the resolver returns an explicit state instead of forcing a numeric answer.

**SVARE is an exact scientific calculator for direct use and a bounded deterministic math oracle for reproducible resolution.**
