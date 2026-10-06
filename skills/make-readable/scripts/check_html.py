#!/usr/bin/env python3
"""Check a make-readable page. Usage: python3 -I check_html.py page.html

Prints OK, or one line per problem and exits 1.
"""
import json
import re
import sys
from html.parser import HTMLParser

VOID = {"meta", "link", "br", "hr", "img", "input", "source", "wbr"}
REQUIRED = ["#rail", "#sel-bar", "#note-pop", "#notes-panel", "#readable-notes", "#drawer", "#draft-editor", "#ref-pop", ".navbar", ".theme-switch", ".content", ".toc"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.problems = [], []
        self.ids, self.classes, self.hrefs, self.sections = [], set(), [], []
        self.external, self.froms, self.unlabelled = [], [], []
        self._section, self._h2_in = None, set()

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

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "section":
            self._section = None
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            opened = self.stack[-1] if self.stack else None
            self.problems.append(f"line {self.getpos()[0]}: </{tag}> does not close {opened}")


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
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(p.sections)} sections")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
