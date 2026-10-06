---
name: make-readable
description: Builds a single self-contained HTML reading page (the "readable") for an explanation, briefing or onboarding doc. It has a sticky collapsible contents rail, light/dark/system themes, a searchable glossary in the navbar, wide tables, and highlights and comments that save back into the same file. Process-, system- and data-heavy parts are drawn as diagrams and charts; the rest stays text. Use when the user asks for something to be explained as an HTML page, asks for a readable, or names make-readable. Covers design, interaction and features only, not what the content says.
disable-model-invocation: true
---

# make-readable

Turns an explanation into one `.html` file that reads like a long-form blog post. This skill decides how the page looks and behaves. What the page says comes from the conversation.

## Output rules

- **One file, fully offline:** inline CSS and JS, system fonts, inline SVG icons. No CDNs, web fonts, images from URLs, or iframes.
- **A local file, not an Artifact,** unless the user asks to publish.
- **Location:** `~/Downloads/<kebab-case-name>.html` unless the user names another place.
- **Open it when done:** `open <file>`.

## Workflow

```
- [ ] 1. cp ~/.claude/skills/make-readable/template.html <output path>
- [ ] 2. Fill <title>, the navbar {{SHORT_NAME}} and the post header
- [ ] 3. Replace the sample section with real sections built from the components below.
         Run each section through the figure gate. Where it passes, compose a figure from the primitives in figures.md.
- [ ] 4. Fill #readable-glossary and run the glossary gate (below) on the finished text
- [ ] 5. python3 -I ~/.claude/skills/make-readable/scripts/check_html.py <file>  (fix until OK)
- [ ] 6. Optional: screenshot once at desktop (dark) and 390px phone width
- [ ] 7. open <file>, then reply with the path and a 2–4 line summary
```

Copy the template with `cp`; don't retype it. Edit only inside `<div class="content">`, plus `<title>`, `{{SHORT_NAME}}` and the `#readable-glossary` block. Leave the `<style>`, rail, navbar, floating UI, notes panel and scripts untouched unless the user asks for a design change.

**Updating a readable that already exists:** edit sections in place. Never regenerate the file from the template, and never touch `<script type="application/json" id="readable-notes">`. That block holds the user's saved highlights, comments, notes and glossary-term notes. Renaming a glossary term orphans the notes kept on it, so keep `term` stable. Highlights and passage references re-anchor to the edited text on their own. Rerun the glossary gate after every edit. If the file predates the glossary, copy the Glossary chip, `#gloss-pop`, `#term-dialog`, `#readable-glossary`, the `--scrim` tokens, the glossary CSS and the glossary script from the template into it.

## Page anatomy

```
rail (fixed left, 288px, collapsible)   | navbar (sticky): ☰ SHORT_NAME / current section · Notes · Comments · Glossary · Save · theme icons
                                        | content column 720px
  Contents                              |   header.post: eyebrow · h1 · lede · meta
  01 Section one  ← active highlight    |   callout "The short version"
  02 Section two                        |   ol.toc (inline contents, only shows under 1080px)
  …                                     |   section#id > h2 + p.sub + body
                                        |   .table-wrap breaks out to 1120px
                                        |   hr + footer (provenance)
```

The rail, the inline contents and the `h2` numbers are generated from `main section[id] > h2` at load. Never hand-write numbers or rail items. Give a section a shorter rail label with `data-short="…"`.

## Components: which to use when

| Content shape | Component | Markup |
|---|---|---|
| The 3–6 points a skimmer must leave with | Summary callout, once, right after the header | `<div class="callout"><div class="eyebrow">The short version</div><ul>…</ul></div>` |
| A question the page answers | Section with a one-line dek | `<section id="x"><h2>Title</h2><p class="sub">dek</p>…</section>` |
| Sub-topic inside a section | `h3` | `<h3>…</h3>` |
| Facts with a label each | Bullets with bold lead-ins | `<li><strong>Label:</strong> detail</li>` (nest one level at most) |
| 3+ items × 2+ attributes, comparisons, people, pricing | Wide table | `<div class="table-wrap"><table>…</table></div>` |
| Rows that fall into groups | Group row | `<tr class="group"><td colspan="N">Group</td></tr>` |
| Status of an item | Pill | `<span class="pill good|warn|bad">…</span>`, or plain `.pill` for neutral |
| Numbers that should line up | Tabular figures | `<td class="num">` or `class="tab"` |
| A short process or flow (≤6 steps) | Step chips | `<ul class="steps"><li>A</li><li>B</li></ul>` |
| Dated events in order | Timeline | `<ol class="timeline"><li><time>date · source</time>text</li></ol>`; `li.next` marks open or upcoming items |
| Exact words someone said or wrote | Blockquote | `<blockquote><p>"…"</p><cite>who, where, date</cite></blockquote>` |
| The agent's inference or recommendation, not a sourced fact | Derived callout | `<div class="callout"><div class="label-derived">Agent synthesis</div>…</div>` |
| Caveat, conflict, name clash, easy mistake | Warning callout | `<div class="callout warn"><div class="eyebrow">Watch out</div>…</div>` |
| File paths, identifiers, commands | Inline code | `<code>…</code>` |

Layout rules:
- Sections are direct children of `.content`. Tables sit directly in a section, never inside a callout or list; the breakout maths assumes the column is the parent.
- Tables get `min-width: 640px` and scroll inside their own box on phones. Keep cell text short and put long prose in paragraphs.
- Number of sections: as many as the topic needs. Each should answer one question, and the rail should read like a table of contents.
- Keep paragraphs to about 4 sentences. Prefer a list or table when content has structure.
- Every external link is a real `<a href>`. Anchor links must point at an existing `id`.

## Glossary

Every readable has a glossary. It is not part of the content: the terms live in the `#readable-glossary` JSON block, and the reader opens them from the **Glossary** chip in the navbar, searches, and opens a term to read its whole definition, keep notes on it, or search the web for it.

```html
<script type="application/json" id="readable-glossary">[
  {"term": "SLA", "full": "Service level agreement", "def": "The uptime and response times the vendor promises in the contract, and the credit owed when it misses them."},
  {"term": "Landed cost", "def": "What a unit costs once it reaches the shelf: purchase price plus freight, duties and handling."}
]</script>
```

- `term` is written exactly as the page writes it. `full` is the spelled-out form, for acronyms and initialisms only. `def` is plain text.
- The script sorts the terms, so write them in any order.

**Glossary gate.** Run it once the text is final, and again after every edit.

1. Reread the page as a smart reader from outside the team, and list every term they might stop on:
   - acronyms and initialisms, including ones that feel universal in the field (ERP, SKU, SLA)
   - jargon, trade terms and terms of art
   - product, vendor, system, team and internal-project names the page doesn't explain
   - metrics and formulas (CAC, p95 latency)
   - labels the page or its sources coin and then use as if they were known
   - ordinary words used in a narrow sense ("pilot", "lane", "landed cost")
2. Give each one an entry. Leave out everyday words used in their everyday meaning.
3. Each definition:
   - says what the term means *on this page*, in one or two sentences
   - explains without the term itself or other undefined jargon
   - puts an acronym's expansion in `full`, not in `def`
   - says how the page uses the term when that differs from the textbook meaning
4. Remove entries for terms the page no longer uses.

`check_html.py` enforces the mechanical half. The block must be valid and non-empty, every all-caps acronym in the content must have an entry, and every entry's term must appear on the page. It skips quoted text (someone else's words) and all-caps styling of a word the page also writes in lower case ("SWARM"). It can't detect jargon; step 1 covers that, and it covers acronyms inside quotes too.

## Figures: draw only what needs drawing

A figure has to earn its place: it should show something the text can't show as well. Ask whether the reader would sketch it themselves to follow along. If not, keep it as text.

**Draw** when the shape of the information is the point:
- order and dependency (branches, parallel steps, loops, approvals, handoffs, or more than about 5 steps)
- a system of 3+ parts with things moving between them
- containment or layers
- a change between two states
- magnitudes, ranges or parts of a whole for several items
- durations and phases
- position on two criteria
- values over time
- overlap or attrition

**Keep it as text** (a list, step chips or a table) for:
- 3 or fewer linear steps
- one or two numbers
- lists of facts, people or opinions
- attribute comparisons (a table)
- estimated or incomplete data: never invent or interpolate points to fill a figure.

**Build from primitives, not from examples.** The template ships composable primitives:
- **Layout:** flow grid with spans, lanes, zones, free canvas, before/after panels.
- **Marks:** nodes with status, icons and values; magnitude and range bars; stack; stats; schedule with milestones; quadrant.
- **Connectors:** highlighted, dashed, labelled, routed.
- **Annotation:** labels, notes, legends.
- **Charts:** a line and bar engine with hover lookups.
- **Ink SVG classes:** for any shape the others can't make.

Pick the relationship first, choose the primitives that encode it, and compose. Several primitives can share one figure. The gallery shows range, not a menu: don't force content into the nearest example.

Rules:
- About one figure per section that passes the gate. Most pages need only 1–4.
- The text around a figure still states the takeaway in one sentence. The figure supports the text; it never replaces the key sentence.
- Every figure gets `aria-label="one-sentence summary"`, plus a `.fig-label` saying what it shows. Mark illustrative data as "sample".
- Explain symbols with a legend UI (`.fig-legend`: real swatches plus short labels), never with prose such as "amber = needs attention".
- Animate (`class="fig animate"`) only when direction or progression is the point. Never animate for decoration. Animations already turn off for reduced-motion readers.
- Use the primitives' classes and the theme tokens only: no raw colours and no chart libraries. Reach for ink SVG only when no primitive fits, then look at it once.

Encoding table, every primitive's markup, connector syntax, charts, ink SVG, motion and the quality bar: [figures.md](figures.md). Compositions to learn from: [examples/figures.html](examples/figures.html).

## Design system (in template.html; change only on request)

- **Palette:** neutral greys after the ChatGPT settings screen. Light is the default, dark comes from the system setting or the toggle. All colours are tokens on `:root` (`--bg --rail --card --card-2 --line --line-soft --fg --text --muted --faint --accent --good --warn --bad --hl --hl-note --shadow`, plus `--fig-bg --node --edge` and chart series `--s1`–`--s4` for figures), redefined for dark under `prefers-color-scheme` and `[data-theme="dark"]`. Never use raw colours in components.
- **Type:** system UI sans and system mono. Body 17px/1.75. Lede 21px. h1 `clamp(36px, 5vw, 52px)`, weight 600, −0.03em tracking. h2 30px. h3 20.5px. UI and meta text 13–15px. Mono uppercase labels 12–13px with 0.06em tracking.
- **Spacing:** sections 112px apart (88px on phones). h3 has 56px above it, paragraphs 20px, list items 10px. Callouts and tables have 40px above them.
- **Widths:** column 720px, wide figures 1120px, rail 288px. Side gutter is 28px, or 16px under 600px. Under 1080px the rail hides and the inline contents list shows. Under 500px the navbar breadcrumb hides to make room for the chips.
- **Shape:** callouts have a 20px radius, tables 18px, popovers 14px; pills and segmented controls are fully rounded. Borders are 1px `--line`. Only the floating popovers and panel cast shadows.

## Built-in features (don't break them; mention them in the reply)

- **Theme switch:** three icon buttons (system, light, dark) in the navbar, no text labels, remembered in `localStorage` as `readable-theme` and applied before paint.
- **Contents rail:** sticky and collapsible (the panel icon in the rail, or in the navbar when collapsed). Its state is remembered as `readable-rail`. The scrollbar is thin and only shows on hover. The current section is highlighted in the rail and named in the navbar.
- **Section picker:** the section name in the navbar breadcrumb is a button. It opens a scrollable list of every section with the current one centred and bold. Pick with the mouse or ↑/↓/Enter (Esc closes) to jump there instantly. The navbar and rail are not text-selectable, because selecting there autoscrolled the page.
- **Highlights and comments:**
  - Select text and a floating bar offers Highlight, Comment, Notes or Copy. Click a highlight to edit its comment or remove it.
  - **Copy** puts one line on the clipboard for pasting into an AI agent ahead of a question: the exact selection, the element it sits in, its section, and the file's absolute path with the section anchor, e.g. `["Solution one-liner." in <li> in section 04 "What AWS is asking for" (at /Users/…/brief.html#asks)]`. The agent finds the spot by searching the file for the quote.
  - The **Comments** panel (navbar) lists every highlight and comment by section; clicking one jumps to it.
  - The panel's **Copy** button copies every highlight the same way, in page order, each followed by `Comment: …` when it has one, so the whole review can go to an agent at once.
  - Each note is stored as its exact quote plus 32 characters on either side, so it re-anchors after edits. Notes it can't place show as "Text not found".
- **Saving:** notes autosave to `localStorage` under `readable-notes:<path>`.
  - **Save** writes them into the `#readable-notes` JSON block of the same file. Chrome and Edge use the save dialog (pick the same file once per session). Other browsers download a copy.
  - Saving strips the `<mark>` elements and UI state, so the saved source stays clean.
- **Notes drawer:** a resizable bottom drawer, opened from **Notes** in the navbar, for the reader's own notes. One toolbar row holds the formatting buttons (left), the resize handle (centre), and the save status and close button (right), with no title text.
  - **Formatting:** bold, italic, headings, lists, quotes and links. Markdown shortcuts work at the start of a line: `- `, `1. `, `# `, `> `. Enter on an empty quote, heading or bold/italic line drops back to plain text, so formatting never sticks.
  - **References:** typing `@` opens a popover pinned beside the caret (never over the typing line). It searches highlights, comments, sections and any passage, and an icon switch (section · highlight · comment) narrows it to one type. Arrow keys and hover pick a row and scroll only the list, never the page.
    - Highlights, sections and passages go in as chips. Clicking a chip jumps to that spot and flashes it.
    - Comments go in as a quote block: the passage, a chip back to its section, and the comment.
  - **Notes** on the selection bar (next to Highlight and Comment) highlights the passage and quotes it into the notes with a link back.
  - **Storage:** paste is plain text only. The notes live as HTML in `data.draft` in the same JSON block, so they autosave and goes into the file with Save.
- **Glossary:** the Glossary chip (left of Save) shows how many terms the page defines and opens a search box over them.
  - Typing filters by term, spelled-out form and definition, with term matches first. ↑/↓ preview each term's whole definition in the list.
  - A click or Enter opens the term in a centred dialog: the definition, a **Your notes** box, and a button that searches "what is <term>" on the reader's chosen engine (Google, Bing, DuckDuckGo, Brave, Kagi or Perplexity; Google by default, remembered as `readable-search`). Esc, the close button or a click on the backdrop closes it and returns to the search.
  - Term notes autosave and go into the file with Save, like comments (`data.terms` in `#readable-notes`, keyed by the term). Terms with notes show a small amber marker in the list.
  - The terms themselves are the page's `#readable-glossary` block, so Save never changes them.
- **Chart lookups:** hover, tap or arrow-key through any chart to see the exact values at each point, in a card next to a guide line (line charts) or a lit column (bar charts).
- **Accessibility:** visible focus rings, Escape closes popovers and the panel, and `prefers-reduced-motion` turns off the slides. Contents links and Notes jumps move to the target instantly (no smooth scroll); keep it that way.

## Verification

- `scripts/check_html.py` checks tag balance, required chrome, sections without an `h2`, duplicate ids, dead anchor links, external resources, leftover `{{placeholders}}`, stray saved `<mark>`s, whether the notes JSON is valid, figure edges that point at missing ids, figures with no `aria-label`, chart JSON (type, labels, value counts), and the glossary: valid and non-empty, every acronym in the content defined, and no entry the page doesn't use.
- After adding figures, look once at the gallery-style render: chip labels hidden behind nodes, or lines running under nodes, mean the layout needs moving (see figures.md).
- For a visual check, take at most one look. If Playwright is installed, render at 1440×900 in dark mode and at 390×844, and confirm `document.documentElement.scrollWidth === innerWidth` at phone width. Headless Chrome's `--window-size` can't go below about 500px, so use device emulation for phones.
