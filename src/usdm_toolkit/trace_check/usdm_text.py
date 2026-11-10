"""Resolve USDM narrative text to plain text.

USDM text attributes are XHTML that may contain:

* ``<usdm:tag name="x"/>`` - a parameter looked up in a
  SyntaxTemplateDictionary (``parameterMaps[].tag -> reference``);
* ``<usdm:ref klass="K" id="I" attribute="a"/>`` - the value of attribute
  ``a`` on the object with id ``I`` anywhere in the study.

Unresolvable tags are rendered as ``[name]`` so a reviewer can see them.
"""

from __future__ import annotations

import html
import re
from typing import Any

_TAG = re.compile(r'<usdm:tag\b([^>]*?)/?>(?:\s*</usdm:tag>)?')
_REF = re.compile(r'<usdm:ref\b([^>]*?)/?>(?:\s*</usdm:ref>)?')
_ATTR = re.compile(r"""(\w+)=(?:"([^"]*)"|'([^']*)')""")
_ANY_TAG = re.compile(r"<[^>]+>")
_MAX_DEPTH = 4


def _attrs(raw: str) -> dict[str, str]:
    return {k: dq or sq for k, dq, sq in _ATTR.findall(raw)}


def strip_markup(text: Any) -> str:
    """Drop all XHTML tags, unescape entities, collapse whitespace."""
    return " ".join(html.unescape(_ANY_TAG.sub(" ", str(text or ""))).split())


def _scalar(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, dict):  # e.g. a Code: show its decode
        return str(value.get("decode") or value.get("text") or "")
    return "" if value is None else str(value)


def _dicts_in(value: Any) -> list[dict]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def _index(node: Any, out: dict[str, dict]) -> None:
    if isinstance(node, dict):
        if isinstance(node.get("id"), str):
            out.setdefault(node["id"], node)
        for v in node.values():
            _index(v, out)
    elif isinstance(node, list):
        for v in node:
            _index(v, out)


class TextResolver:
    """Resolves tags/refs against one USDM document (built once, read-only)."""

    def __init__(self, usdm: dict) -> None:
        self._by_id: dict[str, dict] = {}
        _index(usdm, self._by_id)
        self._dicts: dict[str, dict[str, str]] = {}
        study = usdm.get("study") if isinstance(usdm.get("study"), dict) else {}
        for version in _dicts_in(study.get("versions")):
            for d in _dicts_in(version.get("dictionaries")):
                if not d.get("id"):
                    continue
                self._dicts[str(d["id"])] = {
                    str(pm.get("tag")): str(pm.get("reference") or "")
                    for pm in _dicts_in(d.get("parameterMaps"))}

    def plain(self, text: Any, dictionary_id: str | None = None) -> str:
        return strip_markup(self._resolve(str(text or ""), dictionary_id, 0))

    def _resolve(self, text: str, dictionary_id: str | None, depth: int) -> str:
        if depth >= _MAX_DEPTH or "usdm:" not in text:
            return text
        text = _TAG.sub(lambda m: self._tag(m, dictionary_id, depth), text)
        return _REF.sub(lambda m: self._ref(m, dictionary_id, depth), text)

    def _tag(self, match: re.Match, dictionary_id: str | None, depth: int) -> str:
        name = _attrs(match.group(1)).get("name", "")
        maps = [self._dicts[dictionary_id]] if dictionary_id in self._dicts \
            else list(self._dicts.values())
        for m in maps:
            if name in m:
                return self._resolve(m[name], dictionary_id, depth + 1)
        return f"[{name}]"

    def _ref(self, match: re.Match, dictionary_id: str | None, depth: int) -> str:
        a = _attrs(match.group(1))
        obj = self._by_id.get(a.get("id", ""))
        if obj is None:
            return f"[{a.get('klass', 'ref')}:{a.get('id', '?')}]"
        return self._resolve(_scalar(obj.get(a.get("attribute", ""))),
                             dictionary_id, depth + 1)
