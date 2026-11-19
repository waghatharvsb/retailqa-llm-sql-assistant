import re
from decimal import Decimal

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|replace|"
    r"rename|call|outfile|dumpfile|load_file|sleep|benchmark)\b",
    re.I,
)


def clean_sql(raw):
    s = raw.strip()
    m = re.search(r"```(?:sql)?\s*(.*?)```", s, re.S | re.I)
    if m:
        s = m.group(1)
    s = re.sub(r"^\s*SQLQuery:\s*", "", s, flags=re.I)
    return s.strip()


def is_safe_select(sql):
    s = sql.strip().rstrip(";").strip()
    if not s or ";" in s or "--" in s or "/*" in s:
        return False
    if not re.match(r"(?is)^(select|with)\b", s):
        return False
    return not FORBIDDEN.search(s)


def _fmt(v):
    if isinstance(v, Decimal):
        v = float(v)
        return str(int(v)) if v == int(v) else f"{v:.2f}"
    return str(v)


def format_result(cols, rows):
    if not rows:
        return "No rows returned."
    lines = [" | ".join(cols)] + [" | ".join(_fmt(v) for v in r) for r in rows]
    return "\n".join(lines)