# /triggers - Scan the ICP Roster for Buying Triggers

You run a trigger scan: roster firms crossed with installed trigger sources,
scored against the trigger rubric, deduped, and staged as register-ready rows.

`$ARGUMENTS` may contain:

- Nothing: scan all enabled sources against the full roster, bound to the last
  30 days.
- `workflow` or `e23`: score for one track only.
- `--since <YYYY-MM-DD>`: recency bound for source queries.
- `--limit <N>`: max signals to fetch evidence and score per source (default 20).

Follow the **trigger-scout** skill (`.claude/skills/trigger-scout/SKILL.md`) for
the full workflow. In short:

1. Load `roster.csv` (or `roster.example.csv` with a warning), the rubric
   (`01-trigger-rubric.md`), and `trigger_scraper/seen_triggers.json`.
2. Discover enabled `kind: trigger-source` modules under `.agents/skills/` and
   run each one's documented interface, in parallel where possible.
3. Fetch evidence for each candidate signal; extract the trigger date; confirm
   the roster company.
4. Score against the rubric. Vetoes first, then the five dimensions, then the
   verdict band.
5. Dedupe with `python3 tools/trigger_key.py` and persist everything seen.
6. Present the ranked table. On a quiet run say exactly:
   "No new qualified triggers today."
7. On approval, stage rows to `trigger_staging_YYYY-MM-DD.csv` in exact
   `leads.csv` column order, `id` left empty.

Research only. No outreach, no register writes, no exceptions.
