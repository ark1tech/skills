#!/usr/bin/env python3
"""Check a make-readable page. Usage: python3 -I check_html.py page.html

Prints OK, or one line per problem and exits 1.
"""
import json
import re
import sys
from html import unescape
from html.parser import HTMLParser

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "wbr"}
REQUIRED = ["#rail", "#sel-bar", "#note-pop", "#notes-panel", "#readable-notes", "#readable-glossary", "#gloss-pop", "#term-dialog", "#drawer", "#draft-editor", "#ref-pop", ".navbar", ".theme-switch", ".gloss-toggle", ".content", ".toc"]
# Text inside these is markup, identifiers or someone else's verbatim words, not prose the page needs to define.
NOT_PROSE = {"script", "style", "code", "pre", "kbd", "blockquote", "q"}
# Two or more capitals in one all-caps run (SLA, B2B, HANA), with an optional plural "s".
ACRONYM = re.compile(r"\b(?=[A-Z0-9]*[A-Z][A-Z0-9]*[A-Z])[A-Z0-9]+(?=s?\b)")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.problems = [], []
        self.ids, self.classes, self.hrefs, self.sections = [], set(), [], []
        self.external, self.froms, self.unlabelled = [], [], []
        self._section, self._h2_in = None, set()
        self.text, self._content_at, self._skip = [], None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        self.classes.update((a.get("class") or "").split())
        if tag == "a" and (a.get("href") or "").startswith("#") and len(a["href"]) > 1:
            self.hrefs.append((a["href"][1:], self.getpos()[0]))
        if tag == "section" and a.get("id"):
            self.sections.append(a["id"])
            self._section = a["id"]
        if tag == "h2" and self._section:
            self._h2_in.add(self._section)
        src = a.get("src") or (a.get("href") if tag == "link" else None)
        if src and re.match(r"https?:", src):
            self.external.append((tag, src))
        if a.get("data-from"):
            self.froms.append((a["data-from"], self.getpos()[0]))
        if tag == "figure" and "fig" in (a.get("class") or "").split() and not a.get("aria-label"):
            self.unlabelled.append(self.getpos()[0])
        if tag == "mark" and "hl" in (a.get("class") or ""):
            self.problems.append(f"line {self.getpos()[0]}: saved highlight <mark> in source; highlights belong in #readable-notes")
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))
            if self._content_at is None and "content" in (a.get("class") or "").split():
                self._content_at = len(self.stack)
            elif self._content_at is not None and tag in NOT_PROSE:
                self._skip += 1

    def handle_data(self, data):
        if self._content_at is not None and not self._skip:
            self.text.append(data)

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "section":
            self._section = None
        if self._content_at is not None and tag in NOT_PROSE and self._skip:
            self._skip -= 1
        if self._content_at is not None and self.stack and len(self.stack) == self._content_at and self.stack[-1][0] == tag:
            self._content_at = None
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            opened = self.stack[-1] if self.stack else None
            self.problems.append(f"line {self.getpos()[0]}: </{tag}> does not close {opened}")


def check_glossary(html, text):
    """The glossary must exist, cover every acronym in the content, and define only terms the page uses."""
    body = re.search(r'<div class="content">(.*)</main>', html, re.S)
    used = unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)\b.*?</\1>", " ", body.group(1) if body else "", flags=re.S)))  # code included
    m = re.search(r'<script type="application/json" id="readable-glossary">(.*?)</script>', html, re.S)
    if not m:
        return []  # the REQUIRED check already reports the missing block
    try:
        terms = json.loads(m.group(1))
    except ValueError as e:
        return [f"#readable-glossary is not valid JSON: {e}"]
    if not isinstance(terms, list) or not terms:
        return ["#readable-glossary is empty; every readable defines its acronyms and jargon"]
    problems, seen, covered = [], set(), set()
    for i, t in enumerate(terms, 1):
        if not isinstance(t, dict) or not str(t.get("term", "")).strip() or not str(t.get("def", "")).strip():
            problems.append(f"glossary entry {i} needs a non-empty term and def")
            continue
        term, full = t["term"].strip(), str(t.get("full") or "")
        if term.lower() in seen:
            problems.append(f"glossary defines {term!r} twice")
        seen.add(term.lower())
        covered.update(w.lstrip("0123456789") for w in re.findall(r"[A-Za-z0-9]+", f"{term} {full}"))
        if "{{" not in term and not any(re.search(r"(?<![A-Za-z])" + re.escape(w), used, re.I) for w in (term, full) if w):
            problems.append(f"glossary term {term!r} never appears on the page; remove it or use it")
    words = {w.lower() for w in re.findall(r"[A-Za-z]+", text) if not w.isupper()}
    # "6TB" and "S/4HANA" check as TB and HANA; an all-caps word the page also writes in lower case ("SWARM", "ALL") is styling, not an acronym.
    missing = sorted({a for a in (t.lstrip("0123456789") for t in ACRONYM.findall(text)) if a not in covered and a.lower() not in words})
    if missing:
        problems.append("acronyms missing from the glossary: " + ", ".join(missing))
    return problems


def main(path):
    html = open(path, encoding="utf-8").read()
    p = Page()
    p.feed(html)
    problems = list(p.problems)
    problems += [f"unclosed <{t}> from line {line}" for t, line in p.stack]
    for sel in REQUIRED:
        name = sel[1:]
        if (sel[0] == "#" and name not in p.ids) or (sel[0] == "." and name not in p.classes):
            problems.append(f"missing {sel}; copy the chrome from template.html unchanged")
    dupes = {i for i in p.ids if p.ids.count(i) > 1}
    if dupes:
        problems.append(f"duplicate ids: {', '.join(sorted(dupes))}")
    for s in p.sections:
        if s not in p._h2_in:
            problems.append(f"section #{s} has no h2, so it won't appear in the contents rail")
    if not p.sections:
        problems.append("no <section id> elements; the contents rail will be empty")
    for target, line in p.hrefs:
        if target not in p.ids:
            problems.append(f"line {line}: link to #{target} has no matching id")
    for spec, line in p.froms:
        for token in spec.split():
            source = token.lstrip("!~").split("|")[0]
            if source not in p.ids:
                problems.append(f"line {line}: data-from points at #{source}, which doesn't exist")
    for line in p.unlabelled:
        problems.append(f"line {line}: figure has no aria-label; give it a one-sentence summary")
    for i, raw in enumerate(re.findall(r'<script type="application/json" class="chart-data">(.*?)</script>', html, re.S), 1):
        try:
            chart = json.loads(raw)
        except ValueError as e:
            problems.append(f"chart {i}: invalid JSON: {e}")
            continue
        if chart.get("type") not in ("line", "bar"):
            problems.append(f"chart {i}: type must be line or bar")
        xs, series = chart.get("x") or [], chart.get("series") or []
        if not xs or not series:
            problems.append(f"chart {i}: needs x labels and at least one series")
        for sr in series:
            if len(sr.get("values") or []) != len(xs):
                problems.append(f"chart {i}: series {sr.get('name')!r} has {len(sr.get('values') or [])} values for {len(xs)} x labels")
    for cap in re.findall(r"<figcaption>(.*?)</figcaption>", html, re.S):
        if len(re.findall(r"\w\s=\s\w", cap)) >= 2:
            problems.append(f"figcaption reads like a key ({cap[:50]}…); use a .fig-legend instead")
    for tag, src in p.external:
        problems.append(f"external {tag}: {src}; the page must work offline as one file")
    left = sorted(set(re.findall(r"\{\{[^}]*\}\}", html)))
    if left:
        problems.append("unfilled placeholders: " + ", ".join(left[:8]) + (" …" if len(left) > 8 else ""))
    m = re.search(r'<script type="application/json" id="readable-notes">(.*?)</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            if not isinstance(data.get("notes"), list):
                problems.append("#readable-notes has no notes list")
        except ValueError as e:
            problems.append(f"#readable-notes is not valid JSON: {e}")
    problems += check_glossary(html, re.sub(r"\{\{[^}]*\}\}", " ", " ".join(p.text)))
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(p.sections)} sections")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
