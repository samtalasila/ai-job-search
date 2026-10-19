# Trigger Scout

Buying-trigger detection for a fixed ICP firm roster. Forked from
[MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search)
and rebuilt around a different problem: where the upstream project queries
aggregated job portals for matching postings, this one starts from a roster of
companies and checks each across scattered sources (regulatory announcements,
hiring postings, leadership news, funding coverage).

```
roster.csv  x  trigger sources  x  trigger rubric  ->  ranked triggers  ->  staged rows
```

## Quick start

Prerequisites: Bun 1.x and Python 3.10+.

1. Clone the repo and enter it.
2. Point the scout at a roster: copy `roster.example.csv` to `roster.csv` and
   fill in real firms, or set `TRIGGER_ROSTER` to the absolute path of a
   canonical roster kept elsewhere (e.g. next to your CRM register).
   `roster.csv` is gitignored and never committed.
3. Run `/triggers` in Claude Code, or run a source CLI directly:

```bash
bun run .agents/skills/osfi-watch/cli/src/cli.ts search \
  --query "artificial intelligence, model risk" --since 2026-09-19 --format table
```

4. Review the ranked table. Approved rows are staged to
   `trigger_staging_YYYY-MM-DD.csv` in your register's column order, ready for
   your approval to append. The scout never writes to the register itself.

## What's here

| Path | What it is |
| ---- | ---------- |
| `.claude/skills/trigger-scout/SKILL.md` | The scout workflow: roster x sources x rubric |
| `.claude/skills/trigger-scout/01-trigger-rubric.md` | Scoring rubric: tracks, trigger types, dimensions, vetoes, email rules, output contract |
| `.claude/skills/trigger-scout/02-source-contract.md` | How to add a trigger source module |
| `.agents/skills/osfi-watch/` | First source module: OSFI announcements (regulatory track) |
| `.claude/commands/triggers.md` | The `/triggers` command |
| `tools/trigger_key.py` | Dedupe-key helper for signals |
| `roster.example.csv` | Roster format, example rows |
| `TRIGGER_SCOUT.md` | Full documentation |

## The rubric is the product

Source modules come and go. The durable asset is `01-trigger-rubric.md`: the
tracks, the trigger types, the five weighted scoring dimensions, the vetoes,
the verdict bands, and the email rules. Edit it when your qualification bar
moves; every scan inherits the change.

## Adding a source

Follow `02-source-contract.md`: add a directory under `.agents/skills/` with a
`SKILL.md` whose frontmatter sets `kind: trigger-source`, plus a Bun CLI (or
documented WebSearch queries). The scout discovers it automatically; the
`enabled` toggle lets a module sit out scans without being deleted.

## Data note

This fork is public. The real firm roster (`roster.csv`), seen-signal state,
and staged rows are all gitignored and never committed. Only the example
roster and the framework ship.

## License

MIT, as upstream. See `LICENSE`.
