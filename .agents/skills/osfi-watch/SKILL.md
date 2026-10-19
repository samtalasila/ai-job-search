---
name: osfi-watch
version: 1.0.0
description: >
  Regulatory trigger source: lists and keyword-searches OSFI announcements
  (guidelines, advisories, speeches, statements). Feeds e23_workstream signals
  for the E-23 Readiness track: AI safety-code developments, model-risk
  guidance, and anything moving the May 1, 2027 deadline calculus.
kind: trigger-source
context: fork
enabled: true  # set to false to keep installed but have /triggers skip it
allowed-tools: Bash(bun run .agents/skills/osfi-watch/cli/src/cli.ts *)
---

# OSFI Watch Skill

Searches the public OSFI news feed for regulatory developments relevant to AI
model-risk supervision and E-23 readiness. No authentication, no API key, zero
runtime dependencies (runs with just `bun`).

OSFI items are regulator-level signals: they apply to the sector, not one
firm. The trigger scout maps them to the E-23 track and pairs them with
firm-level roster checks.

## Commands

### List recent announcements

```bash
bun run .agents/skills/osfi-watch/cli/src/cli.ts list [--page <n>] [--limit <n>] [--format json|table]
```

### Search announcements

```bash
bun run .agents/skills/osfi-watch/cli/src/cli.ts search --query "<keywords>" [--since <YYYY-MM-DD>] [--limit <n>] [--format json]
```

Keyword matching is case-insensitive OR: an item matches when any term appears
in its title. `--since` filters client-side on the item date.

```bash
# AI and model-risk items since the start of the month
bun run .agents/skills/osfi-watch/cli/src/cli.ts search --query "artificial intelligence, AI, model risk, E-23" --since 2026-10-01 --format table

# Latest five announcements of any kind
bun run .agents/skills/osfi-watch/cli/src/cli.ts list --limit 5 --format table
```

### Fetch announcement detail

```bash
bun run .agents/skills/osfi-watch/cli/src/cli.ts detail <url> [--format json|plain]
```

Returns the title and an evidence snippet from the announcement page.

## Output

`list` and `search` emit `{ "results": [...] }` with objects shaped:

```json
{ "company": null, "signal": "<title>", "url": "https://www.osfi-bsif.gc.ca/...", "date": "YYYY-MM-DD | null", "type": "News release | Advisory | ...", "source": "osfi-watch" }
```

All errors go to stderr as `{ "error": "...", "code": "..." }`, exit code 1.

## Notes

- Source: `https://www.osfi-bsif.gc.ca/en/news` (OSFI news feed, Drupal,
  server-rendered). Keep volume low: bounded pages, small limits.
- Parsing anchors (re-pin these if the markup changes): each item is
  `<article class="news feed ...">`; title and URL come from the heading link
  inside it; the date comes from a `datetime="YYYY-MM-DD..."` attribute.
- The feed page shows a handful of items per page; `--page` passes through to
  the site's `?page=N` pagination.
- Dates are the announcement's publication date, never inferred.
