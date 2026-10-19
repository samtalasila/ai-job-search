# Trigger Source Contract

How to add a new trigger source module. The trigger scout discovers modules by
reading every `.agents/skills/*/SKILL.md` and using the ones whose frontmatter
sets `kind: trigger-source`.

## Frontmatter

```yaml
---
name: my-source
version: 1.0.0
description: >
  One-paragraph description: what signals it finds, for which track.
kind: trigger-source
context: fork
enabled: true  # set to false to keep installed but sit out scans
allowed-tools: Bash(bun run .agents/skills/my-source/cli/src/cli.ts *)
---
```

`kind: trigger-source` is what makes the scout pick the module up. `enabled`
lets a fork keep a module installed but skip it without deleting the directory.

## CLI interface (preferred)

When the source has a fetchable endpoint or page, ship a zero-dependency Bun
CLI at `.agents/skills/<name>/cli/src/cli.ts` with a `package.json` (no
runtime dependencies). Support these commands:

```bash
# Recent items, newest first
bun run .agents/skills/<name>/cli/src/cli.ts list [--page <n>] [--limit <n>] [--format json|table]

# Keyword-filtered items, optionally bounded by date
bun run .agents/skills/<name>/cli/src/cli.ts search --query "<keywords>" [--since <YYYY-MM-DD>] [--limit <n>] [--format json]

# Full detail for one item (evidence snippet)
bun run .agents/skills/<name>/cli/src/cli.ts detail <url|id> [--format json|plain]
```

JSON output is a `results` array of objects with at least:

```json
{ "company": "...", "signal": "one-line summary", "url": "...", "date": "YYYY-MM-DD | null", "source": "<name>" }
```

`company` may be null for regulator-level items (a guideline applies to the
whole sector); the scout maps those to the E-23 track directly. Errors go to
stderr as `{ "error": "...", "code": "..." }` with exit code 1.

## WebSearch-based modules

When the source has no stable endpoint, skip the CLI and document query
strings in the SKILL.md instead. The scout runs them via WebSearch and tags
results as websearch-sourced, which the rubric weighs as lower evidence
quality than CLI output. Test-run at least one query before registering.

## House rules

- **ToS and volume.** Document the source's access rules in the SKILL.md.
  Scraping against a site's terms gets a prominent personal-use-only warning.
  Keep volume low: bounded pages, small limits, no crawling.
- **Parsing anchors.** HTML parsers rot when markup changes. Document the
  anchors the parser depends on (element, class, attribute) in the SKILL.md so
  the next person can re-pin them.
- **Rate limits are never evidence of breakage.** A 429 means back off and
  report the module as inconclusive for the run, not broken.
- **Dates are never invented.** `null` when the source gives none; the rubric
  scores unconfirmed dates down.
