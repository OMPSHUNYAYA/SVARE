import hashlib
import sys
from dataclasses import dataclass
from math import gcd

VERSION = "9.9"
MAX_REVEAL_DEPTH = 48
DEFAULT_REVEAL_DEPTH = 18
MAX_PRIMARY_VISIBLE_DIGITS = 80
SCIENTIFIC_SECONDARY_DIGITS = 18


def seal(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@dataclass
class Value:
    state: str
    num: int = 0
    den: int = 1
    note: str = ""


@dataclass
class Node:
    kind: str
    id: str
    surface: str = ""
    op: str = ""
    left: object = None
    right: object = None
    child: object = None


def make_value(n, d=1):
    if d == 0:
        return Value("FORBIDDEN", 0, 0, "ratio cannot resolve through a Zero denominator")
    if n == 0:
        return Value("RESOLVED", 0, 1, "structure resolves to Zero")
    if d < 0:
        n = -n
        d = -d
    g = gcd(abs(n), abs(d))
    return Value("RESOLVED", n // g, d // g, "structure resolves through exact structural packets")


def parse_directives(text):
    depth = DEFAULT_REVEAL_DEPTH
    kept = []
    tokens = text.strip().split()
    idx = 0
    while idx < len(tokens):
        if tokens[idx].lower() == "depth" and idx + 1 < len(tokens) and tokens[idx + 1].isdigit():
            depth = min(int(tokens[idx + 1]), MAX_REVEAL_DEPTH)
            idx += 2
        else:
            kept.append(tokens[idx])
            idx += 1
    return "".join(kept), depth


def tokenize(s):
    out = []
    idx = 0
    while idx < len(s):
        ch = s[idx]
        if ch.isspace():
            idx += 1
        elif ch in "+-*/()":
            out.append((ch, ch))
            idx += 1
        elif ch.isdigit() or ch == ".":
            start = idx
            dots = 0
            while idx < len(s) and (s[idx].isdigit() or s[idx] == "."):
                if s[idx] == ".":
                    dots += 1
                idx += 1
            value = s[start:idx]
            if dots > 1 or value == ".":
                raise ValueError("CONFLICT: invalid number surface")
            out.append(("NUMBER", value))
        else:
            raise ValueError("CONFLICT: unsupported token")
    out.append(("EOF", ""))
    return out


def parse_number_surface(surface):
    text = surface
    if text.startswith("."):
        text = "0" + text
    if text.endswith("."):
        text += "0"
    if "." in text:
        left, right = text.split(".", 1)
    else:
        left, right = text, ""
    if left == "":
        left = "0"
    if not left.isdigit() or (right != "" and not right.isdigit()):
        raise ValueError("CONFLICT: invalid number surface")
    digits = (left + right).lstrip("0") or "0"
    return make_value(int(digits), 10 ** len(right))


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        self.node_id = 0

    def cur(self):
        return self.tokens[self.idx]

    def consume(self, kind=None):
        token = self.cur()
        if kind and token[0] != kind:
            raise ValueError("INCOMPLETE: expected " + kind)
        self.idx += 1
        return token

    def new_id(self):
        self.node_id += 1
        return "N" + str(self.node_id)

    def parse(self):
        node = self.expr()
        if self.cur()[0] != "EOF":
            raise ValueError("CONFLICT: unresolved trailing structure")
        return node

    def expr(self):
        node = self.term()
        while self.cur()[0] in {"+", "-"}:
            op = self.consume()[0]
            right = self.term()
            node = Node("op", self.new_id(), op=op, left=node, right=right)
        return node

    def term(self):
        node = self.factor()
        while self.cur()[0] in {"*", "/"}:
            op = self.consume()[0]
            right = self.factor()
            node = Node("op", self.new_id(), op=op, left=node, right=right)
        return node

    def factor(self):
        if self.cur()[0] == "+":
            self.consume("+")
            return Node("unary", self.new_id(), op="+", child=self.factor())
        if self.cur()[0] == "-":
            self.consume("-")
            return Node("unary", self.new_id(), op="-", child=self.factor())
        if self.cur()[0] == "NUMBER":
            value = self.consume("NUMBER")[1]
            return Node("value", self.new_id(), surface=value)
        if self.cur()[0] == "(":
            self.consume("(")
            node = self.expr()
            if self.cur()[0] != ")":
                raise ValueError("INCOMPLETE: group is not closed")
            self.consume(")")
            return Node("group", self.new_id(), child=node)
        if self.cur()[0] == "EOF":
            raise ValueError("INCOMPLETE: expression ended before structure resolved")
        raise ValueError("CONFLICT: invalid factor structure")


def relation(op):
    return {"+": "MERGE", "-": "REMOVE", "*": "EXPAND", "/": "RATIO"}[op]


def combine(left, right, op):
    if left.state != "RESOLVED":
        return left
    if right.state != "RESOLVED":
        return right
    a, b, c, d = left.num, left.den, right.num, right.den
    if op == "+":
        return make_value(a * d + c * b, b * d)
    if op == "-":
        return make_value(a * d - c * b, b * d)
    if op == "*":
        return make_value(a * c, b * d)
    if op == "/":
        if c == 0:
            if a == 0:
                return Value("INDETERMINATE_ZERO", 0, 0, "Zero divided by Zero does not uniquely resolve")
            return Value("FORBIDDEN", 0, 0, "ratio cannot resolve through a Zero denominator")
        return make_value(a * d, b * c)
    return Value("CONFLICT", 0, 0, "unknown structural relation")


def eval_node(node, records):
    if node.kind == "value":
        value = parse_number_surface(node.surface)
        records.append((node.id, "VALUE", value))
        return value
    if node.kind == "group":
        value = eval_node(node.child, records)
        records.append((node.id, "GROUP", value))
        return value
    if node.kind == "unary":
        child = eval_node(node.child, records)
        value = child
        if child.state == "RESOLVED" and node.op == "-":
            value = make_value(-child.num, child.den)
        records.append((node.id, "DIRECTION", value))
        return value
    left = eval_node(node.left, records)
    right = eval_node(node.right, records)
    value = combine(left, right, node.op)
    records.append((node.id, relation(node.op), value))
    return value


def finite_decimal(num, den):
    sign = -1 if num < 0 else 1
    n = abs(num)
    whole = n // den
    rem = n % den
    if rem == 0:
        return ("-" if sign < 0 and whole != 0 else "") + str(whole), 0, False
    d = den
    twos = 0
    fives = 0
    while d % 2 == 0:
        d //= 2
        twos += 1
    while d % 5 == 0:
        d //= 5
        fives += 1
    if d != 1:
        return None
    scale = max(twos, fives)
    scaled = n * (10 ** scale) // den
    raw = str(scaled)
    if len(raw) <= scale:
        raw = "0" * (scale - len(raw) + 1) + raw
    left = raw[:-scale].lstrip("0") or "0"
    right = raw[-scale:]
    while right.endswith("0"):
        right = right[:-1]
    visible = left + (("." + right) if right else "")
    if sign < 0 and visible != "0":
        visible = "-" + visible
    return visible, len(right), False


def truncate_finite_visible(value, limit):
    if "." not in value:
        return value
    negative = value.startswith("-")
    body = value[1:] if negative else value
    left, right = body.split(".", 1)
    if len(right) <= limit:
        return value
    visible = left + (("." + right[:limit]) if limit > 0 else "")
    return ("-" if negative else "") + visible


def reveal(num, den, depth):
    finite = finite_decimal(num, den)
    if finite:
        full_visible, finite_depth, _ = finite
        displayed = truncate_finite_visible(full_visible, depth)
        return {
            "visible": displayed,
            "displayed_decimal_layers": min(finite_depth, depth),
            "finite_visibility_depth": finite_depth,
            "recurring_visibility_depth": "NA",
            "residual": False,
            "finite_truncated": finite_depth > depth,
            "kind": "finite",
        }
    sign = -1 if num < 0 else 1
    n = abs(num)
    whole = n // den
    rem = n % den
    digits = []
    for _ in range(depth):
        if rem == 0:
            break
        rem *= 10
        digits.append(str(rem // den))
        rem %= den
    visible = str(whole) + (("." + "".join(digits)) if digits else "")
    if sign < 0 and visible != "0":
        visible = "-" + visible
    residual = rem != 0
    return {
        "visible": visible,
        "displayed_decimal_layers": len(digits),
        "finite_visibility_depth": "NA",
        "recurring_visibility_depth": "∞" if residual else len(digits),
        "residual": residual,
        "finite_truncated": False,
        "kind": "recurring" if residual else "finite",
    }


def visible_digit_count(value):
    if value in {"undefined", "indeterminate", "not_visible"}:
        return 0
    v = value[1:] if value.startswith("-") else value
    digits = v.replace(".", "").lstrip("0")
    return len(digits)


def scientific_visible(value):
    if value in {"undefined", "indeterminate", "not_visible"}:
        return value
    negative = value.startswith("-")
    body = value[1:] if negative else value
    if "." in body:
        left, right = body.split(".", 1)
        scale = len(right)
        raw = left + right
    else:
        scale = 0
        raw = body
    digits = raw.lstrip("0")
    if not digits:
        return "0"
    exponent = len(digits) - 1 - scale
    mantissa = digits[0]
    rest = digits[1:SCIENTIFIC_SECONDARY_DIGITS]
    if rest:
        mantissa += "." + rest
    return ("-" if negative else "") + mantissa + "e" + str(exponent)


def format_visible(value):
    if value in {"undefined", "indeterminate", "not_visible"}:
        return value
    if visible_digit_count(value) <= MAX_PRIMARY_VISIBLE_DIGITS:
        return value
    return scientific_visible(value)


def secondary_scientific(value):
    if value in {"undefined", "indeterminate", "not_visible"}:
        return "—"
    if visible_digit_count(value) > SCIENTIFIC_SECONDARY_DIGITS:
        return scientific_visible(value)
    return "—"


def canonical(node):
    if node.kind == "value":
        value = parse_number_surface(node.surface)
        return "VAL(" + str(value.num) + "/" + str(value.den) + ")"
    if node.kind == "group":
        return "GROUP(" + canonical(node.child) + ")"
    if node.kind == "unary":
        return "DIR(" + node.op + "," + canonical(node.child) + ")"
    return relation(node.op) + "(" + canonical(node.left) + "," + canonical(node.right) + ")"


def node_visible(value, depth):
    if value.state == "RESOLVED":
        r = reveal(value.num, value.den, min(depth, 12))
        return r["visible"] + ("..." if r["residual"] else "")
    if value.state == "FORBIDDEN":
        return "undefined"
    if value.state == "INDETERMINATE_ZERO":
        return "indeterminate"
    return "not_visible"



def visibility_depth_label(finite_visibility_depth, recurring_visibility_depth):
    if finite_visibility_depth != "NA":
        return str(finite_visibility_depth) + " (Finite)"
    if recurring_visibility_depth != "NA":
        return str(recurring_visibility_depth) + " (Recurring)"
    return "NA"

def run_expression(text):
    surface = text.strip()
    try:
        expr_text, depth = parse_directives(surface)
        if not expr_text:
            raise ValueError("INCOMPLETE: expression is empty")
        root = Parser(tokenize(expr_text)).parse()
        records = []
        value = eval_node(root, records)
        if value.state == "RESOLVED":
            reveal_info = reveal(value.num, value.den, depth)
            visible = reveal_info["visible"]
            displayed_decimal_layers = reveal_info["displayed_decimal_layers"]
            finite_visibility_depth = reveal_info["finite_visibility_depth"]
            recurring_visibility_depth = reveal_info["recurring_visibility_depth"]
            residual = reveal_info["residual"]
            finite_truncated = reveal_info["finite_truncated"]
            visibility_kind = reveal_info["kind"]
            direction = "ZERO" if value.num == 0 else "-" if value.num < 0 else "+"
            note = "expression tree resolves through complete and consistent structural packets"
        elif value.state == "FORBIDDEN":
            visible, displayed_decimal_layers, finite_visibility_depth, recurring_visibility_depth = "undefined", "NA", "NA", "NA"
            residual, finite_truncated, visibility_kind = False, False, "none"
            direction = "DENOM_ZERO"
            note = value.note
        elif value.state == "INDETERMINATE_ZERO":
            visible, displayed_decimal_layers, finite_visibility_depth, recurring_visibility_depth = "indeterminate", "NA", "NA", "NA"
            residual, finite_truncated, visibility_kind = False, False, "none"
            direction = "ZERO/ZERO"
            note = value.note
        else:
            visible, displayed_decimal_layers, finite_visibility_depth, recurring_visibility_depth = "not_visible", "NA", "NA", "NA"
            residual, finite_truncated, visibility_kind = False, False, "none"
            direction = "NO_VALUE"
            note = value.note or "structure does not resolve"
        can = canonical(root)
        cert = seal("SVARE|" + VERSION + "|" + can + "|" + value.state + "|" + visible + "|" + str(depth))
        return {
            "surface": surface,
            "depth": depth,
            "decimal_visibility_limit": depth,
            "relation": "TREE" if len(records) > 1 else records[-1][1],
            "state": value.state,
            "visible": visible,
            "display": format_visible(visible),
            "scientific": secondary_scientific(visible),
            "direction": direction,
            "visibility_depth_label": visibility_depth_label(finite_visibility_depth, recurring_visibility_depth),
            "finite_visibility_depth": finite_visibility_depth,
            "recurring_visibility_depth": recurring_visibility_depth,
            "displayed_decimal_layers": displayed_decimal_layers,
            "visibility_kind": visibility_kind,
            "note": note,
            "certificate": cert,
            "canonical": can,
            "residual": residual,
            "finite_truncated": finite_truncated,
            "bounded": visible_digit_count(visible) > MAX_PRIMARY_VISIBLE_DIGITS,
            "records": records,
        }
    except Exception as exc:
        msg = str(exc)
        state = "INCOMPLETE" if msg.startswith("INCOMPLETE") else "CONFLICT"
        return {
            "surface": surface,
            "depth": DEFAULT_REVEAL_DEPTH,
            "decimal_visibility_limit": DEFAULT_REVEAL_DEPTH,
            "relation": "TREE",
            "state": state,
            "visible": "not_visible",
            "display": "not_visible",
            "scientific": "—",
            "direction": "NO_VALUE",
            "visibility_depth_label": "NA",
            "finite_visibility_depth": "NA",
            "recurring_visibility_depth": "NA",
            "displayed_decimal_layers": "NA",
            "visibility_kind": "none",
            "note": msg,
            "certificate": seal("SVARE|" + VERSION + "|" + surface + "|" + state),
            "canonical": "UNRESOLVED",
            "residual": False,
            "finite_truncated": False,
            "bounded": False,
            "records": [],
        }


def print_result(result):
    print()
    print("SVARE v" + VERSION)
    print("Structural Value Resolution Engine")
    print()
    print("Decimal Visibility Limit :", str(result["decimal_visibility_limit"]) + " decimal layers")
    print("Finite Visibility Depth  :", result["finite_visibility_depth"])
    print("Recurring Visibility Depth :", result["recurring_visibility_depth"])
    print("Displayed Decimal Layers :", result["displayed_decimal_layers"])
    print("SVARE relation           :", result["relation"])
    print("Resolution state         :", result["state"])
    print("Visible value            :", result["display"])
    if result["scientific"] != "—":
        print("Scientific visibility    :", result["scientific"])
    print("Direction                :", result["direction"])
    print("Certificate              :", result["certificate"])
    print()
    print("Structural Tree Nodes")
    print("-" * 72)
    for node_id, rel, value in result["records"]:
        print(node_id + " | " + rel + " | " + value.state + " | " + node_visible(value, result["depth"]))
    if result["residual"] or result["finite_truncated"] or result["bounded"]:
        print()
        print("STRUCTURAL VISIBILITY NOTE")
        print("-" * 72)
        if result["finite_truncated"]:
            print("The finite resolved value has more decimal layers than the current display limit.")
            print("Only the visible decimal portion is shortened; structural resolution is preserved.")
        if result["residual"]:
            print("This output reflects bounded recurring decimal visibility.")
            print("The recurring decimal structure continues beyond the current display limit.")
        if result["bounded"]:
            print("Primary display is bounded for demo visibility; scientific visibility is shown separately.")
            print("Primary visible digit limit :", MAX_PRIMARY_VISIBLE_DIGITS)
    print()
    print("FINAL VISIBLE VALUE")
    print("=" * 72)
    print(" ", result["display"])
    print("=" * 72)


def demo():
    examples = [
        "1 + 2 + 3",
        "(1 + 2) * 3",
        "1.5 * (2 + 3.25) - 0.75",
        "1.6 + (2 - 3.25) / 0.75",
        "-25.6 - (-2.09 * 3.25) / -0.75 / 0.0000001",
        "((1.0000000000000001 - 1.0000000000000000) * 10) + 5",
        "(2 / 3) + (1 / 6)",
        "2 / (3 - 3)",
        "(1 + 2",
    ]
    print("SVARE v" + VERSION)
    print("=" * 72)
    for item in examples:
        print_result(run_expression(item))


def interactive():
    if not sys.stdin.isatty():
        return
    print("SVARE v" + VERSION)
    print("=" * 72)
    print("Enter expression, or type exit.")
    while True:
        try:
            text = input("> ").strip()
        except EOFError:
            break
        if text.lower() in {"exit", "quit"}:
            break
        if text:
            print_result(run_expression(text))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print_result(run_expression(" ".join(sys.argv[1:])))
    elif not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            print_result(run_expression(piped))
    else:
        demo()
        interactive()
