# Trigger Scout (bolt-on)

Buying-trigger detection for an ICP firm roster, built on this repo's
skill/CLI/command pattern. Where `/scrape` queries aggregated job portals for
matching postings, `/triggers` starts from a fixed roster of firms and checks
each one across scattered sources: regulatory announcements, hiring postings,
leadership news, funding coverage.

```
roster.csv  x  trigger sources  x  trigger rubric  ->  ranked triggers  ->  staged rows
```

## Quick start

1. Point the scout at a roster: copy `roster.example.csv` to `roster.csv`
   and fill in real firms, or set `TRIGGER_ROSTER` to the absolute path of a
   canonical roster kept elsewhere (e.g. next to the CRM register).
   `roster.csv` is gitignored; it never ships.
2. Run `/triggers`.
3. Review the ranked table, approve rows, and append the staged CSV to your
   register.

## File map

| Path | What it is |
| ---- | ---------- |
| `.claude/skills/trigger-scout/SKILL.md` | The scout: roster x sources x rubric workflow |
| `.claude/skills/trigger-scout/01-trigger-rubric.md` | Scoring rubric: tracks, trigger types, dimensions, vetoes, email rules, output contract |
| `.claude/skills/trigger-scout/02-source-contract.md` | How to add a trigger source module |
| `.agents/skills/osfi-watch/` | First source module: OSFI announcements (regulatory track) |
| `.claude/commands/triggers.md` | The `/triggers` command |
| `tools/trigger_key.py` | Dedupe-key helper for signals |
| `roster.example.csv` | Roster format, example rows |
| `trigger_scraper/seen_triggers.json` | Seen-signal state (gitignored, created on first run) |
| `trigger_staging_YYYY-MM-DD.csv` | Staged rows awaiting approval (gitignored) |

## The rubric is the product

Source modules come and go; the durable asset is
`01-trigger-rubric.md`: the two tracks (Workflow Evidence, E-23 Readiness),
the seven trigger types, the five scoring dimensions with weights, the vetoes,
the verdict bands, and the email rules. Edit it when your qualification
bar moves; every scan inherits the change.

## Register handoff

Staged rows use the exact `leads.csv` column order, with `id` left empty. IDs
are assigned from the register's current max at append time, which stays a
separate, explicitly approved step. The scout never writes to the register
itself.

## Adding a source

Follow `02-source-contract.md`: add a directory under `.agents/skills/` with a
`SKILL.md` whose frontmatter sets `kind: trigger-source`, plus a Bun CLI (or
documented WebSearch queries). The scout discovers it automatically; the
`enabled` toggle lets a module sit out scans without being deleted.

## Data note

This fork is public. The real firm roster (`roster.csv`), seen-signal state,
and staged rows are all gitignored and never committed. Only the example
roster and the framework ship.
