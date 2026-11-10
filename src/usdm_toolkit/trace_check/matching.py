"""Label matching between USDM names/labels and SDTM values.

USDM carries no SDTM short codes (ARMCD, ETCD, ...) and sponsors rarely use
identical spelling, so artifacts are linked by *labels*: normalised exact
match first, then a conservative fuzzy match. Approximate matches are
reported back so a human can confirm them.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher

DEFAULT_THRESHOLD = 0.8
_PREFIX_MIN_LEN = 4
_PREFIX_SCORE = 0.85
_SUBSET_SCORE = 0.9
_ROMAN = {"1": "i", "2": "ii", "3": "iii", "4": "iv", "5": "v"}

LabelItem = str | tuple[str, Sequence[str]]


_SHORT_TOKEN_LEN = 2


def normalize(text: object) -> str:
    """Lower-case, turn punctuation/underscores into spaces, collapse spaces.

    A minus sign directly before a number is kept as ``neg`` so that
    ``Day -1`` and ``Day 1`` stay different.
    """
    s = re.sub(r"(?<![0-9a-z])-\s*(\d)", r" neg\1", str(text or "").lower())
    s = re.sub(r"[^0-9a-z]+", " ", s)
    return " ".join(s.split())


def tokens(text: object, *, roman: bool = False) -> frozenset[str]:
    toks = normalize(text).split()
    if roman:
        toks = [_ROMAN.get(t, t) for t in toks]
    return frozenset(toks)


def _numbers(norm: str) -> frozenset[str]:
    return frozenset(re.findall(r"(?:neg)?\d+", norm))


def _differ_only_in_short_tokens(ta: frozenset[str], tb: frozenset[str]) -> bool:
    """``Arm A`` vs ``Arm B``: both sides differ, only in 1-2 letter tokens."""
    only_a, only_b = ta - tb, tb - ta
    return bool(only_a and only_b) and all(
        len(t) <= _SHORT_TOKEN_LEN for t in only_a | only_b)


def similarity(a: object, b: object) -> float:
    """Score in [0, 1]; 1.0 means equal after normalisation."""
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    nums_a, nums_b = _numbers(na), _numbers(nb)
    if nums_a and nums_b and not (nums_a <= nums_b or nums_b <= nums_a):
        return 0.0  # "Week 2" must never pair with "Week 4" (or "Day -1"/"Day 1")
    if _differ_only_in_short_tokens(tokens(na), tokens(nb)):
        return 0.0
    score = SequenceMatcher(None, na, nb).ratio()
    short, long_ = sorted((na, nb), key=len)
    if len(short) >= _PREFIX_MIN_LEN and long_.startswith(short):
        score = max(score, _PREFIX_SCORE)
    ta, tb = tokens(na), tokens(nb)
    if ta and tb and (ta <= tb or tb <= ta):
        score = max(score, _SUBSET_SCORE)
    return score


def text_similarity(a: object, b: object) -> float:
    """Plain character similarity, for long free text (titles, criteria)."""
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return 0.0
    return 1.0 if na == nb else SequenceMatcher(None, na, nb).ratio()


def containment(short: object, long_: object) -> float:
    """Share of ``short``'s words that also occur in ``long_`` (0..1).

    High containment with low similarity means ``short`` is an abbreviation
    of ``long_`` (e.g. TI.IETEST, capped at 200 characters).
    """
    ts, tl = tokens(short), tokens(long_)
    return len(ts & tl) / len(ts) if ts else 0.0


def coded_compatible(a: object, b: object) -> bool:
    """Coded values agree if one token set contains the other.

    ``DOUBLE BLIND`` ~ ``Double Blind Study`` but ``Phase III Trial`` is not
    ``Phase II Trial`` (character similarity would wrongly accept that).
    Arabic numerals are read as Roman (``Phase 2`` ~ ``Phase II``).
    """
    ta, tb = tokens(a, roman=True), tokens(b, roman=True)
    return bool(ta and tb) and (ta <= tb or tb <= ta)


_PHASE_TOKEN = re.compile(r"^(i{1,3}|iv|v|0)([ab]?)$")


def _phase_numerals(text: object) -> frozenset[str]:
    out = set()
    for tok in normalize(text).split():
        tok = _ROMAN.get(tok, tok)
        m = _PHASE_TOKEN.match(tok)
        if m:
            out.add(m.group(1) + m.group(2))
    return frozenset(out)


def phase_compatible(a: object, b: object) -> bool:
    """Trial phases agree only if their phase numerals are identical.

    ``Phase II`` is not ``Phase I/II``; ``Phase 2`` equals ``Phase II Trial``.
    Falls back to :func:`coded_compatible` when no numeral is present.
    """
    pa, pb = _phase_numerals(a), _phase_numerals(b)
    if pa or pb:
        return pa == pb
    return coded_compatible(a, b)


@dataclass(frozen=True)
class Pair:
    left: str
    right: str
    score: float
    exact: bool


@dataclass(frozen=True)
class MatchResult:
    pairs: tuple[Pair, ...]
    left_only: tuple[str, ...]
    right_only: tuple[str, ...]

    def right_for(self, left: str) -> str | None:
        return next((p.right for p in self.pairs if p.left == left), None)

    @property
    def approximate(self) -> tuple[Pair, ...]:
        return tuple(p for p in self.pairs if not p.exact)


def _expand(items: Iterable[LabelItem]) -> list[tuple[str, tuple[str, ...]]]:
    """Normalise inputs to ``(key, aliases)``; repeated keys are kept once.

    Keys are display labels, so a duplicate (two encounters both called
    ``Day 1``) is the same thing on the report and must not show as a gap.
    """
    out: dict[str, tuple[str, ...]] = {}
    for item in items:
        if isinstance(item, tuple):
            key, aliases = item
            out.setdefault(key, tuple(a for a in aliases if a) or (key,))
        else:
            out.setdefault(item, (item,))
    return list(out.items())


def match_labels(left: Iterable[LabelItem], right: Iterable[LabelItem],
                 threshold: float = DEFAULT_THRESHOLD) -> MatchResult:
    """One-to-one greedy matching, best score first, exact matches preferred."""
    lefts, rights = _expand(left), _expand(right)
    candidates = []
    for li, (_, l_alias) in enumerate(lefts):
        for ri, (_, r_alias) in enumerate(rights):
            score = max(similarity(a, b) for a in l_alias for b in r_alias)
            if score >= threshold:
                candidates.append((score, li, ri))
    candidates.sort(key=lambda c: (-c[0], c[1], c[2]))

    used_l: dict[int, tuple[int, float]] = {}
    used_r: set[int] = set()
    for score, li, ri in candidates:
        if li in used_l or ri in used_r:
            continue
        used_l[li] = (ri, score)
        used_r.add(ri)

    pairs = tuple(
        Pair(lefts[li][0], rights[ri][0], score, score == 1.0)
        for li, (ri, score) in sorted(used_l.items())
    )
    return MatchResult(
        pairs=pairs,
        left_only=tuple(k for i, (k, _) in enumerate(lefts) if i not in used_l),
        right_only=tuple(k for i, (k, _) in enumerate(rights) if i not in used_r),
    )
