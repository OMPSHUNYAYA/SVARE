import hashlib
import re
import sys

KERNEL = "SVARE"
VERSION = "8.1"
MAX_REVEAL_DEPTH = 24
DEFAULT_REVEAL_DEPTH = 6
MAX_VISIBLE_DIGITS = 18


def seal(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def strip_zeros(text):
    out = text.lstrip("0")
    return out if out else "0"


def visible_digit_count(value):
    v = value.strip()
    if v in {"undefined", "indeterminate", "not_visible"}:
        return 0
    if v.startswith("-"):
        v = v[1:]
    if "." in v:
        left, right = v.split(".", 1)
        digits = left + right
    else:
        digits = v
    digits = digits.lstrip("0")
    return len(digits)


def format_visible_output(value):
    v = value.strip()
    if v in {"undefined", "indeterminate", "not_visible"}:
        return v
    negative = v.startswith("-")
    body = v[1:] if negative else v
    if "." in body:
        left, right = body.split(".", 1)
        scale = len(right)
        raw_digits = left + right
    else:
        scale = 0
        raw_digits = body
    digits = raw_digits.lstrip("0")
    if digits == "":
        return "0"
    if len(digits) <= MAX_VISIBLE_DIGITS:
        return value
    exponent = len(digits) - 1 - scale
    mantissa_rest = digits[1:MAX_VISIBLE_DIGITS]
    mantissa = digits[0]
    if mantissa_rest:
        mantissa = mantissa + "." + mantissa_rest
    out = mantissa + "e" + str(exponent)
    if negative:
        out = "-" + out
    return out


def is_bounded_display(value):
    return visible_digit_count(value) > MAX_VISIBLE_DIGITS


def clean_number_token(text):
    t = text.strip().replace(" ", "")
    changed = True
    while changed:
        changed = False
        if len(t) >= 2 and t[0] == "(" and t[-1] == ")":
            level = 0
            ok = True
            for idx, ch in enumerate(t):
                if ch == "(":
                    level += 1
                elif ch == ")":
                    level -= 1
                    if level == 0 and idx != len(t) - 1:
                        ok = False
                        break
            if ok:
                t = t[1:-1]
                changed = True
        if t.startswith("+(") and t.endswith(")"):
            t = "+" + t[2:-1]
            changed = True
        if t.startswith("-(") and t.endswith(")"):
            t = "-" + t[2:-1]
            changed = True
    return t


def parse_number(text):
    t = clean_number_token(text)
    sign = 1
    while t.startswith("+") or t.startswith("-"):
        if t[0] == "-":
            sign = -sign
        t = t[1:]
    if t.startswith("(") and t.endswith(")"):
        return parse_number(("-" if sign < 0 else "") + t[1:-1])
    if t.startswith("."):
        t = "0" + t
    if t.endswith("."):
        t = t + "0"
    if "." in t:
        left, right = t.split(".", 1)
    else:
        left, right = t, ""
    if left == "":
        left = "0"
    if not left.isdigit() or (right != "" and not right.isdigit()):
        return None
    digits = strip_zeros(left + right)
    scale = len(right)
    if digits == "0":
        sign = 1
        scale = 0
    return {"sign": sign, "digits": digits, "scale": scale}


def normalize_scaled(sign, digits, scale):
    digits = strip_zeros(digits)
    while scale > 0 and digits.endswith("0"):
        digits = digits[:-1]
        scale -= 1
    if digits == "" or digits == "0":
        return "0", 1, "0", 0
    if scale > 0:
        if len(digits) <= scale:
            digits = "0" * (scale - len(digits) + 1) + digits
        left = strip_zeros(digits[:-scale])
        right = digits[-scale:]
        visible = left + "." + right
    else:
        visible = digits
    if sign < 0:
        visible = "-" + visible
    return visible, sign, strip_zeros(digits), scale


def compare_abs(a, b):
    a = strip_zeros(a)
    b = strip_zeros(b)
    if len(a) < len(b):
        return -1
    if len(a) > len(b):
        return 1
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def add_abs(a, b):
    ia = len(a) - 1
    ib = len(b) - 1
    carry = 0
    out = []
    while ia >= 0 or ib >= 0 or carry:
        da = ord(a[ia]) - 48 if ia >= 0 else 0
        db = ord(b[ib]) - 48 if ib >= 0 else 0
        s = da + db + carry
        out.append(chr(48 + (s % 10)))
        carry = s // 10
        ia -= 1
        ib -= 1
    return strip_zeros("".join(reversed(out)))


def sub_abs(a, b):
    ia = len(a) - 1
    ib = len(b) - 1
    borrow = 0
    out = []
    while ia >= 0:
        da = ord(a[ia]) - 48 - borrow
        db = ord(b[ib]) - 48 if ib >= 0 else 0
        if da < db:
            da += 10
            borrow = 1
        else:
            borrow = 0
        out.append(chr(48 + da - db))
        ia -= 1
        ib -= 1
    return strip_zeros("".join(reversed(out)))


def align_values(a, b):
    scale = max(a["scale"], b["scale"])
    ad = a["digits"] + "0" * (scale - a["scale"])
    bd = b["digits"] + "0" * (scale - b["scale"])
    return ad, bd, scale


def add_scaled(a, b):
    ad, bd, scale = align_values(a, b)
    if a["sign"] == b["sign"]:
        return a["sign"], add_abs(ad, bd), scale
    rel = compare_abs(ad, bd)
    if rel == 0:
        return 1, "0", 0
    if rel > 0:
        return a["sign"], sub_abs(ad, bd), scale
    return b["sign"], sub_abs(bd, ad), scale


def multiply_abs(a, b):
    if a == "0" or b == "0":
        return "0"
    res = [0] * (len(a) + len(b))
    for ia in range(len(a) - 1, -1, -1):
        for ib in range(len(b) - 1, -1, -1):
            res[ia + ib + 1] += (ord(a[ia]) - 48) * (ord(b[ib]) - 48)
    for idx in range(len(res) - 1, 0, -1):
        carry = res[idx] // 10
        res[idx] %= 10
        res[idx - 1] += carry
    return strip_zeros("".join(str(x) for x in res))


def mul_digit(a, d):
    if d == 0 or a == "0":
        return "0"
    carry = 0
    out = []
    for idx in range(len(a) - 1, -1, -1):
        v = (ord(a[idx]) - 48) * d + carry
        out.append(chr(48 + (v % 10)))
        carry = v // 10
    while carry:
        out.append(chr(48 + (carry % 10)))
        carry //= 10
    return strip_zeros("".join(reversed(out)))


def divmod_abs(n, d):
    n = strip_zeros(n)
    d = strip_zeros(d)
    if d == "0":
        return None, None
    q = []
    rem = "0"
    for ch in n:
        rem = strip_zeros(rem + ch)
        digit = 0
        for cand in range(9, -1, -1):
            prod = mul_digit(d, cand)
            if compare_abs(prod, rem) <= 0:
                digit = cand
                rem = sub_abs(rem, prod)
                break
        q.append(chr(48 + digit))
    return strip_zeros("".join(q)), strip_zeros(rem)


def divide_scaled(a, b, reveal_depth):
    if b["digits"] == "0":
        if a["digits"] == "0":
            return "INDETERMINATE_ZERO", "indeterminate", "ZERO/ZERO", 0, False, "ratio cannot resolve through a Zero denominator"
        return "FORBIDDEN", "undefined", "DENOM_ZERO", 0, False, "ratio cannot resolve through a Zero denominator"
    if a["digits"] == "0":
        return "RESOLVED", "0", "ZERO", reveal_depth, False, "ratio resolves by structural digit revelation"
    sign = 1 if a["sign"] == b["sign"] else -1
    numerator = a["digits"] + "0" * b["scale"]
    denominator = b["digits"] + "0" * a["scale"]
    whole, rem = divmod_abs(numerator, denominator)
    digits = []
    depth_used = 0
    residual_continues = False
    for _ in range(reveal_depth):
        if rem == "0":
            break
        rem = strip_zeros(rem + "0")
        q, rem = divmod_abs(rem, denominator)
        digits.append(q[-1])
        depth_used += 1
    while rem != "0" and digits and set(digits) == {"0"} and depth_used < MAX_REVEAL_DEPTH:
        rem = strip_zeros(rem + "0")
        q, rem = divmod_abs(rem, denominator)
        digits.append(q[-1])
        depth_used += 1
    if rem != "0":
        residual_continues = True
    frac = "".join(digits)
    if frac:
        raw = whole + frac
        visible, _, _, scale = normalize_scaled(sign, raw, len(frac))
        depth_value = scale
    else:
        visible, _, _, scale = normalize_scaled(sign, whole, 0)
        depth_value = scale
    return "RESOLVED", visible, "+" if sign > 0 else "-", depth_value, residual_continues, "ratio resolves by structural digit revelation"


def split_expression(text):
    raw = text.strip()
    reveal_depth = DEFAULT_REVEAL_DEPTH
    tokens = raw.split()
    kept = []
    idx = 0
    while idx < len(tokens):
        if tokens[idx].lower() == "depth" and idx + 1 < len(tokens) and tokens[idx + 1].isdigit():
            reveal_depth = min(int(tokens[idx + 1]), MAX_REVEAL_DEPTH)
            idx += 2
        elif tokens[idx].lower() == "show":
            idx += 1
        else:
            kept.append(tokens[idx])
            idx += 1
    s = "".join(kept).replace(" ", "")
    pattern = r"^(.+?)([+\-*/])(.+)$"
    best = None
    level = 0
    for i, ch in enumerate(s):
        if ch == "(":
            level += 1
        elif ch == ")":
            level -= 1
        elif ch in "+-*/" and level == 0 and i > 0:
            prev = s[i - 1]
            if prev in "+-*/(":
                continue
            best = (s[:i], ch, s[i + 1:])
            break
    if best is None:
        for i, ch in enumerate(s):
            if ch in "*/" and i > 0:
                best = (s[:i], ch, s[i + 1:])
                break
    if best is None:
        m = re.match(pattern, s)
        if not m:
            return None
        best = (m.group(1), m.group(2), m.group(3))
    left = parse_number(best[0])
    right = parse_number(best[2])
    if left is None or right is None:
        return None
    relation = {"+": "MERGE", "-": "REMOVE", "*": "EXPAND", "/": "RATIO"}[best[1]]
    return {"surface": raw, "left": left, "right": right, "op": best[1], "relation": relation, "reveal_depth": reveal_depth}


def make_result(relation, state, visible, direction, depth_value, note, expr, residual):
    text = relation + "|" + expr["surface"] + "|" + state + "|" + visible + "|" + str(expr.get("reveal_depth", ""))
    steps = {
        "MERGE": ["SVARE receives two direction-aware structures.", "Depth layers are aligned so both structures speak the same unit layer.", "Matching directions merge.", "Opposite directions cancel by structural digit packets.", "The remaining structure reveals the visible value."],
        "REMOVE": ["SVARE receives a source structure and a removal structure.", "Removal reverses the direction of the removed structure.", "Depth layers are aligned before resolution.", "Structures merge or cancel by structural digit packets.", "The remaining directional structure reveals the visible value."],
        "EXPAND": ["SVARE receives packet-ready structures.", "Unsafe raw mark expansion is avoided.", "SVARE preserves structural identity through compressed packets.", "The compressed structure resolves through structural digit packets.", "The visible value is revealed through the resolved packet structure."],
        "RATIO": ["SVARE receives a numerator structure and a denominator structure.", "Decimal surfaces are aligned into equivalent depth structures.", "Whole value is revealed through structural digit packets.", "Residual structure is carried into deeper layers.", "Each permitted depth layer reveals one visible digit."]
    }[relation]
    visibility_note = ""
    if relation == "RATIO" and residual and state == "RESOLVED":
        visibility_note = "This output reflects bounded structural depth. The underlying residual structure continues beyond visible digits. Use 'depth N' to reveal deeper structure."
    return {"relation": relation, "state": state, "visible": visible, "direction": direction, "depth_value": depth_value, "note": note, "certificate": seal(text), "steps": steps, "visibility_note": visibility_note}


def result_for(expr):
    left = expr["left"]
    right = expr["right"]
    relation = expr["relation"]
    if relation == "MERGE":
        sign, digits, scale = add_scaled(left, right)
        visible, sign, digits, scale = normalize_scaled(sign, digits, scale)
        note = "packet structures merge through structural digit resolution"
        residual = False
    elif relation == "REMOVE":
        r = dict(right)
        r["sign"] = -r["sign"]
        sign, digits, scale = add_scaled(left, r)
        visible, sign, digits, scale = normalize_scaled(sign, digits, scale)
        note = "packet structures remove through structural digit resolution"
        residual = False
    elif relation == "EXPAND":
        sign = 1 if left["sign"] == right["sign"] else -1
        digits = multiply_abs(left["digits"], right["digits"])
        scale = left["scale"] + right["scale"]
        visible, sign, digits, scale = normalize_scaled(sign, digits, scale)
        note = "packet structures expand through structural digit resolution"
        residual = False
    else:
        state, visible, direction, scale, residual, note = divide_scaled(left, right, expr["reveal_depth"])
        return make_result(relation, state, visible, direction, scale, note, expr, residual)
    state = "RESOLVED"
    direction = "ZERO" if visible == "0" else "-" if visible.startswith("-") else "+"
    return make_result(relation, state, visible, direction, scale, note, expr, residual)


def print_result(expr, result):
    display_value = format_visible_output(result["visible"])
    bounded = is_bounded_display(result["visible"])

    print()
    print("Surface expression       :", expr["surface"])

    if result["relation"] == "RATIO":
        print("Reveal depth             :", expr["reveal_depth"])

    print("SVARE relation           :", result["relation"])
    print("Resolution state         :", result["state"])
    print("Visible value            :", display_value)
    print("Direction                :", result["direction"])
    print("Visible depth            :", result["depth_value"])
    print("Resolution note          :", result["note"])
    print("Certificate              :", result["certificate"])

    print()
    print("Resolution Walkthrough")
    print("-" * 72)

    for idx, step in enumerate(result["steps"], start=1):
        print(str(idx) + ". " + step)

    if result.get("visibility_note") or bounded:
        print()
        print("STRUCTURAL VISIBILITY NOTE")
        print("-" * 72)

        if result.get("visibility_note"):
            print("This output reflects bounded structural depth.")
            print("The underlying residual structure continues beyond visible digits.")
            print("Use:")
            print("  expression depth N")
            print("Example:")
            base_surface = expr["surface"].split(" depth ", 1)[0]
            print("  " + base_surface + " depth 12")

        if bounded:
            print("This output is bounded for demo visibility.")
            print("Full structural resolution is preserved internally.")
            print("Visible digit limit      :", MAX_VISIBLE_DIGITS)

    print()
    print("FINAL VISIBLE VALUE")
    print("=" * 72)
    print(" ", display_value)
    print("=" * 72)


def run_expression(text):
    expr = split_expression(text)
    if expr is None:
        return None, None
    return expr, result_for(expr)


def demo():
    examples = [
        "5 + 2",
        "-7 - 9",
        "-7 * -8",
        "-7 - -8",
        "-7 + 8",
        "1.2 + 2.35",
        "0.25 * 4",
        "1.0000000000000001-1.0000000000000000",
        "-00000.0009-9999",
        "(+0.72) - (0.72)",
        "2 / 3 depth 8",
        "9 / 0",
        "0 / 0",
        "88888888 * 88888888"
    ]
    print("DEMO MODE")
    print("=" * 72)
    print("Selected release examples. More cases can be entered in interactive mode.")
    print()
    for item in examples:
        expr, result = run_expression(item)
        if expr is not None:
            print_result(expr, result)


def interactive():
    print()
    print("INTERACTIVE MODE")
    print("=" * 72)
    print("Enter ordinary expressions:")
    print("  5 + 2")
    print("  1.2 + 2.35")
    print("  -7 - 9")
    print("  (-7) * (-8)")
    print("  -.99*(+0.72)")
    print("  1.0000000000000001-1.0000000000000000")
    print("  -00000.0009-9999")
    print("  (+0.72) - (0.72)")
    print("  0.000009/0.2222 depth 12")
    print("Type exit to stop.")
    print()
    while True:
        try:
            text = input("SVARE> ")
        except EOFError:
            break
        if text.strip().lower() in {"exit", "quit"}:
            break
        expr, result = run_expression(text)
        if expr is None:
            print()
            print("Please use ordinary input such as:")
            print("  5 + 2")
            print("  1.2 * 2")
            print("  -7 - 9")
            print("  (-7) * (-8)")
            print("  1.0000000000000001-1.0000000000000000")
            print("  -00000.0009-9999")
            print("  (+0.72) - (0.72)")
            print("  2/3 depth 8")
            print()
            continue
        print_result(expr, result)


def main():
    print("SVARE v" + VERSION)
    print("Structural Value Resolution Engine")
    print("=" * 72)
    print("Invisible Structural Engine")
    print("Principle: value_visible iff structure_uniquely_resolves")
    print("Language: structure -> resolution -> visibility")
    print("User input: ordinary expressions")
    print("Core resolution: structural packets, depth, direction, residual visibility, and bounded public display")
    print("Decimal rule: decimal surfaces become structural depth")
    print("Direction rule: negative and explicit positive surfaces become structural direction")
    print("Anchor: values are revealed when structure resolves")
    print("Demo safety: oversized raw/depth/deep-decimal expansions are structurally packet-resolved; residual ratios disclose bounded visible depth; oversized visible values use bounded scientific visibility before final value")
    print()
    if len(sys.argv) > 1:
        expr, result = run_expression(" ".join(sys.argv[1:]))
        if expr is None:
            print("Could not parse structural expression.")
            return
        print_result(expr, result)
        return
    demo()
    interactive()


if __name__ == "__main__":
    main()
