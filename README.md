# skills

Agent skills by [@ark1tech](https://github.com/ark1tech). Each folder in [`skills/`](skills) holds a `SKILL.md` and the references, scripts and assets it needs.

## Install

```bash
npx skills add ark1tech/skills
```

Or copy a skill folder into your agent's skills directory (for example `~/.claude/skills/`, `~/.codex/skills/` or `~/.cursor/skills/`).

## Skills

### [make-readable](skills/make-readable)

Turns an explanation, briefing or onboarding doc into one offline HTML page that reads like a long-form post:

- a sticky, collapsible contents rail, a section picker, and system, light and dark themes
- wide tables, plus diagrams and charts composed from primitives (flows, lanes, zones, bars, schedules, quadrants, a line and bar chart engine), drawn only where the shape of the information is the point
- highlights, comments and a notes drawer with `@` references, all saved back into the same HTML file

`scripts/check_html.py` checks structure, dead anchors, figure labels, chart data and external resources. [`examples/figures.html`](skills/make-readable/examples/figures.html) shows what the primitives can make.

It sets `disable-model-invocation: true`, so it runs only when you call it by name.

Requirements: `python3` for the check.

## License

MIT
