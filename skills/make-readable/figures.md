# Visual primitives

Figures are built by composing small primitives, not by picking from a list of figure types. Decide what relationship the reader needs to see, choose the primitives that encode it, and arrange them to fit the content. [examples/figures.html](examples/figures.html) shows one composition per primitive. Treat them as proof of what's possible, not as templates to copy.

Everything here is already in `template.html` (CSS and JS). It follows the theme tokens, so it works in light and dark mode with no extra code.

## 1. Choose the encoding

Start from the relationship, not the topic.

| The reader needs to see… | Encode it as | Primitives |
|---|---|---|
| Order and dependency: steps, stages, handoffs, parallel work, merges | Position along a reading direction, plus lines | flow grid · nodes · connectors (`!` for the critical path); more than 4–5 steps wrap into a second row that runs back (a snake); a ladder climbs as a staircase |
| Who does what, in order | One row per actor | lanes + flow grid |
| A cycle, a hub, a network with no main direction | Free placement | free canvas · smooth connectors |
| Containment, layers, system boundaries | Nesting | zones (stacked, or `.row` for layers) · lanes |
| A change from one state to another | Side by side | `fig-pair` panels, each with its own flow |
| How big a few things are, or their ranges | Length | bars (`--from` turns a bar into a range) |
| Parts of a whole | Length within one bar | stack + swatch legend |
| A handful of headline numbers | Big type | stats |
| Durations, phases, deadlines | Position on a time axis | schedule (bars, ghost bars, milestones) |
| Two criteria at once | Position on two axes | quadrant |
| Many values over time or across categories | A chart | chart engine (line or bar) |
| Overlap, funnels, radial layouts, simple maps, anything else | Drawn shapes | ink SVG |

Compose freely. A schedule can sit above a row of stats. A flow can use lanes and zones together. A free canvas can carry labelled connectors. Several primitives can share one figure, separated by `.fig-label` headings.

## 2. Canvas and annotation

```html
<figure class="fig [bare] [animate]" aria-label="One-sentence summary of what the figure shows.">
  <div class="fig-label">What this shows · unit or scope</div>   <!-- mono label; repeat it to title sub-parts -->
  …primitives…
  <div class="fig-legend">…</div>                                <!-- whenever symbols need explaining -->
  <figcaption>Optional single sentence of context.</figcaption>
</figure>
```
- **`.fig`** breaks out to the 1120px figure width and scrolls sideways inside itself on phones.
- **`.fig.bare`** removes the frame. Use it to hold `.fig-pair` panels.
- **Figure attributes:** `data-curve="smooth"`, `data-arrows="off"` and `data-route="v"` apply to every flow inside. Each can also go on a single `.flow`.
- **Annotation:**
  - `.fig-note` (mono, two lines with `<b>` on top) is for a note under a panel.
  - `.fig-pair > .panel` gives two framed panels side by side that stack under about 880px.
- **Legend items:** each is `<span>` + a swatch + a 1–3 word label. Swatches:
  - `st` status icons
  - `lg-line` (`.hot`, `.dash`)
  - `lg-node` (`.hot`, `.ghost`, `.out`)
  - `lg-zone`
  - `lg-sw` (`style="--c:var(--s2)"`)
- Never explain symbols in prose.

## 3. Layout

**Flow grid.** Places items in columns and rows.
```html
<div class="flow" style="--cols:4">
  <div class="node" id="a" style="--c:1;--r:1">…</div>
  <div class="node" id="b" style="--c:2;--r:1;--rs:2">…</div>   <!-- --cs / --rs span columns / rows -->
</div>
```
- Columns are `max-content`, spread across the width with an 80px minimum gap.
- Override inline when needed: `style="grid-template-columns:1fr; row-gap:44px; column-gap:48px"`.

**Lanes.** A band for each actor or phase, spanning columns, sitting under nodes and lines.
```html
<div class="lane" style="--c:1;--cs:5;--r:2"></div>
<div class="lane-name" style="--c:1;--r:2">Agents</div>          <!-- reserve column 1 for lane names -->
```

**Zones.** A dashed boundary for a system, team or owner. It can be a grid item or nested.
```html
<div class="zone" style="--c:2;--r:1"><span class="zone-label">SAP S/4HANA</span> …nodes stacked… </div>
<div class="zone row" style="--r:2"><span class="zone-label">Agents</span> …nodes in a row… </div>
```

**Free canvas.** Absolute placement by percentage, for loops, hubs and radial arrangements.
```html
<div class="flow free" style="--h:360px; --minw:640px">
  <div class="node" id="x" style="--x:50;--y:12">…</div>        <!-- --x/--y = the node's centre, in % of the canvas -->
</div>
```

## 4. Marks

**Node:**
```html
<div class="node [hot|out|ghost|dim]" id="n1">
  <span class="node-tag">Small header</span>
  <div class="nr"><i class="st accent"></i>Label<b>value</b></div>   <!-- a row: status or icon · label · right-aligned value -->
  <small>sub-line detail</small>
</div>
```
- **Status (`i.st`):** plain (done), `accent`, `warn`, `good`, `bad`, `idle` (ring), `run` (spinner).
- **Icons (`i.gi.gi-NAME`):** `doc db users person bell filter agent clock cart factory truck money gear check mail cloud chart bolt`.
- **Variants:** `hot` is the one that matters; `out` is a result; `ghost` is planned or optional; `dim` is de-emphasised.
- Labels are 1–4 words and render as uppercase mono; detail goes in `<small>`.

**Bars.** Magnitudes or ranges on a shared scale.
```html
<div class="bars" style="--max:70">
  <div class="brow"><span>Spoilage</span><i style="--from:10;--v:40"></i><b>10–40%</b></div>
  <div class="brow dim"><span>Baseline</span><i style="--v:12;--c:var(--s3)"></i><b>12%</b></div>
</div>
```

**Stack.** Parts of a whole. Each segment's `--v` is its share; pair it with an `lg-sw` legend.
```html
<div class="stack"><i style="--v:15;--c:var(--s1)" title="DC · 15 days"></i><i style="--v:30;--c:var(--s2)" title="Store · 30 days"></i></div>
```

**Stats.** Only when a few numbers are the point.
```html
<div class="stats"><div class="stat hot"><b>−40%</b><span>stockouts</span><small>source</small></div> …</div>
```

**Schedule.** Bars and milestones on an `--n`-unit axis.
```html
<div class="gantt" style="--n:20">
  <div class="g-axis"><span style="--at:0">W0</span><span style="--at:4">W4</span>…</div>
  <div class="g-row"><span>Pilot</span><div class="g-track">
    <i style="--s:5;--e:17">label</i>                <!-- .ghost = not committed; --c to recolour -->
    <i class="ms" style="--s:17">Production</i>      <!-- milestone diamond with a label -->
  </div></div>
</div>
```

**Quadrant.** Position on two axes.
```html
<div class="quad" style="--h:340px">
  <span class="q-axis x">Effort →</span><span class="q-axis y">Impact →</span>
  <span class="q-zone tl">Quick wins</span> … tr · bl · br
  <i class="q-dot" style="--x:24;--y:80">Invoice matching</i>   <!-- .left puts the label on the left; .dim; --c -->
</div>
```

Page components work inside figures too: `.pill` for status, `<code>`.

## 5. Connectors

Declare connectors on the target: `data-from="a b"`. Each token can be:
- `id`: a line from `#id` to this element
- `!id`: the highlighted path
- `~id`: dashed, for planned, optional or async steps (`!~id` combines both)
- `id|label`: a chip label at the line's midpoint (`_` becomes a space)

Routing is automatic. Boxes side by side get horizontal elbows; stacked boxes get vertical ones. Lines between the same columns share a trunk, which makes fan-in and fan-out read cleanly.

Options, on the figure or the flow:
- `data-curve="smooth"`: S-curves.
- `data-arrows="off"`: dots instead of arrowheads.
- `data-route="v"`: always route vertically between rows, for layers and top-down trees.

Lines are drawn behind nodes, so arrange nodes so no line has to pass through another box. A hidden chip label means it did; move a node or switch to `data-route="v"`.

## 6. Data charts

```html
<figure class="fig fig-chart [animate]" aria-label="…">
  <div class="fig-label">What is measured · unit</div>
  <script type="application/json" class="chart-data">{
    "type": "line",                      // "line" for trends, "bar" for amounts per period or category
    "x": ["W1", "W2", "W3"],
    "y": { "min": 0, "max": 30, "ticks": 3, "prefix": "$", "suffix": "%" },  // optional; the default is a clean 0-based scale
    "series": [{ "name": "Baseline", "values": [22, 23, null] }],            // null = gap; up to 4 series (--s1..--s4)
    "marker": { "x": "W2", "label": "Pilot starts" },                        // optional dotted event line
    "height": 280, "legend": true
  }</script>
</figure>
```
- **Lookups:** hover, tap or arrow keys show the exact values: a guide line and dots for line charts, a lit column for bars.
- **Data:** chart only real numbers. Never chart estimates as if they were measurements. Label targets as targets.

## 7. Ink SVG (escape hatch)

When no primitive fits (overlaps, funnels, radial diagrams, simple maps, a custom illustration), draw inline SVG with the ink classes. They pick up the theme tokens, so never set colours directly.

```html
<svg class="ink" viewBox="0 0 1000 300" aria-hidden="true">
  <circle class="area" cx="420" cy="150" r="120" style="--c:var(--s1)"/>   <!-- tinted fill + outline in --c -->
  <rect class="shape" x="…" y="…" width="…" height="…" rx="10"/>            <!-- a box like a node -->
  <path class="stroke [hot] [dash]" d="…"/>                                  <!-- a line -->
  <circle class="dot [hot]" cx="…" cy="…" r="3"/>
  <text class="label" x="…" y="…">Mono label</text>                       <!-- also .title, .value -->
</svg>
```
- **Scale:** a viewBox about 1000 units wide keeps 1 unit close to 1px on desktop, so text renders at its intended size. Narrower viewBoxes enlarge the text.
- **Text:** keep it short, and use few labels; the figure's `aria-label` carries the meaning.
- **Ownership:** you own the coordinates, so look at the result once and fix overlaps.

## 8. Motion

- **Opt in per figure** with `class="fig animate"`. Each primitive moves its own way:
  - Connectors: dashes flow along them.
  - `.node.hot`: pulses.
  - Chart lines: draw in.
  - Chart bars, magnitude bars, stacks and schedule bars: grow.
  - Stats, quadrant dots and milestones: fade in.
- **Stagger** with `style="--i:1"`, `--i:2`, … on items.
- **Use it only when direction or progression is the point.** Everything turns off for readers who prefer reduced motion.

## 9. Quality bar

- **Gate:** draw only when the shape of the information carries meaning; otherwise keep text. About one figure per section that passes the gate.
- **Takeaway:** the sentence before or after the figure states it.
- **Labelling:** every figure has an `aria-label` summary and a `.fig-label`. Symbols get a legend; illustrative data is marked "sample".
- **Size:** at most about 12 boxes per diagram; split bigger ones or zoom out. Keep one reading direction and labels of 1–4 words.
- **Look once after building:** hidden chips, lines under boxes, clipped labels or a figure that scrolls on desktop all mean the layout needs to change.
