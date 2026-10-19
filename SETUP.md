# Setup

## 1. Prerequisites

- Bun 1.x (`bun --version`)
- Python 3.10+ (`python3 --version`)

## 2. Clone

```bash
git clone <your-fork-url>
cd ai-job-search
```

## 3. Roster

Copy `roster.example.csv` to `roster.csv` and fill in the firms you watch
(columns: `company,website,size_band,regulator,tracks,notes`), or set
`TRIGGER_ROSTER` to the absolute path of a canonical roster kept elsewhere.
`roster.csv` is gitignored; it never ships.

## 4. Source CLIs

The shipped source module has zero runtime dependencies and runs with plain
`bun`. No install step needed, but you can verify it:

```bash
bun run .agents/skills/osfi-watch/cli/src/cli.ts list --limit 3 --format table
```

## 5. Run a scan

In Claude Code, run `/triggers`. See `TRIGGER_SCOUT.md` for the full
documentation: the rubric, the source contract, and the register handoff.
