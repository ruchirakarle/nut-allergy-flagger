"""Ingredient-text checker for tree nuts and peanuts (keyword rules)."""
import re
from dataclasses import dataclass, field

TREE_NUTS = [
    "almond", "hazelnut", "cashew", "walnut", "pecan", "pistachio",
    "macadamia", "brazil nut", "pine nut", "pine kernel", "chestnut", "filbert",
    "praline", "marzipan", "gianduja", "tree nut", "nut",
]
PEANUTS = ["peanut", "groundnut", "arachis oil"]

# Phrases that talk about nuts but mean "no nuts here".
NEGATIONS = re.compile(r"\b(nut|peanut|tree nut)[- ]free\b|\b(no|without|free from) (tree )?(nuts?|peanuts?)\b")
# A sentence containing one of these is a cross-contact warning, not an ingredient.
MAY_CONTAIN = re.compile(
    r"may contain|might contain|traces? of|processed in|made in a (facility|factory)|"
    r"manufactured (in|on)|shared (facility|equipment)|produced in a"
)


def _compile(words):
    # longest first so "pine nut" wins over "nut"
    alts = "|".join(sorted(map(re.escape, words), key=len, reverse=True))
    return re.compile(r"\b(" + alts + r")(?:s|es)?\b")


TREE_RE = _compile(TREE_NUTS)
PEANUT_RE = _compile(PEANUTS)


@dataclass
class Result:
    status: str  # "contains" | "may_contain" | "clear"
    tree_nuts: list = field(default_factory=list)
    peanuts: list = field(default_factory=list)
    traces: list = field(default_factory=list)
    pine_only: bool = False  # botanically a seed, but flagged for safety


def check(text: str) -> Result:
    text = NEGATIONS.sub(" ", (text or "").lower())
    direct, traces = [], []
    for sentence in re.split(r"[.;\n]+", text):
        bucket = traces if MAY_CONTAIN.search(sentence) else direct
        for rx in (TREE_RE, PEANUT_RE):
            bucket += [m.group(1) for m in rx.finditer(sentence)]

    uniq = lambda xs: sorted(set(xs), key=xs.index)
    direct, traces = uniq(direct), uniq(traces)
    tree = [w for w in direct if w in TREE_NUTS]
    peanut = [w for w in direct if w in PEANUTS]
    status = "contains" if direct else ("may_contain" if traces else "clear")
    return Result(
        status=status,
        tree_nuts=tree,
        peanuts=peanut,
        traces=traces,
        pine_only=bool(tree) and all(w in ("pine nut", "pine kernel") for w in tree),
    )
