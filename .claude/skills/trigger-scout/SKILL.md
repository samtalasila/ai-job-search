---
name: triggers
description: >
  Finds buying triggers for the ICP firm roster across installed trigger-source
  modules (regulatory, hiring, news). Scores each signal against the trigger
  rubric, dedupes across runs, and stages leads.csv-compatible rows for approval.
  Trigger phrases: find triggers, trigger scan, new triggers, scan for signals,
  buying signals, /triggers
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(bun --version), Bash(bun run .agents/skills/osfi-watch/cli/src/cli.ts *), Bash(python3 tools/trigger_key.py *), WebFetch, WebSearch, Agent, AskUserQuestion
---

# Trigger Scout

Roster-centric buying-trigger detection. Where the job scraper queries
aggregated portals for matching postings, the trigger scout starts from a fixed
roster of ICP firms and checks each one across scattered sources: regulatory
announcements, hiring postings, leadership news, funding coverage.

```
roster.csv  x  trigger sources  x  trigger rubric  ->  ranked triggers  ->  staged rows
```

## Invocation

- "Find new triggers", "trigger scan", "any new signals?", "/triggers"
- `/triggers workflow` or `/triggers e23` to scope to one track
- `/triggers --since 2026-10-01` to bound recency

## Execution Steps

### Step 0: Load State

1. Read `roster.csv` (repo root). If missing, fall back to `roster.example.csv`
   and say so up front: example firms produce example triggers, nothing real.
2. Read `.claude/skills/trigger-scout/01-trigger-rubric.md` once. It is the
   single source of truth for what counts as a trigger.
3. Read `trigger_scraper/seen_triggers.json` (create if missing, start with
   `{"seen": {}}`). Never read the whole file into the conversation on later
   steps; query it with `python3 tools/trigger_key.py --audit` style lookups.

### Step 1: Discover Source Modules

Read every `.agents/skills/*/SKILL.md`. A trigger source module is one whose
frontmatter sets `kind: trigger-source`. Honor the `enabled` toggle (missing
means enabled). For each enabled module, follow its SKILL.md: run its CLI, or
use its documented WebSearch queries when it has no CLI.

Run modules in parallel where possible. If a module's CLI exits non-zero, log
the error and continue; do not abort the scan.

### Step 2: Fetch Evidence

For each candidate signal:

- Fetch the evidence URL (WebFetch; retry with browser headers on 403).
- Extract the trigger date. `null` when the source gives none; never invent one.
- Confirm the company is on the roster. A signal about a firm adjacent to the
  roster (same segment, just outside the size band) is kept but flagged
  `icp_adjacent`; anything further out is dropped.

### Step 3: Score Against the Rubric

Score every surviving signal on the five rubric dimensions
(`01-trigger-rubric.md`): ICP fit, signal strength, timing, evidence quality,
actionability. Apply the vetoes first: any veto caps the verdict at watchlist
or drops the signal outright. Assign the band: qualified, watchlist, or
lead_to_investigate.

### Step 4: Dedupe & Store

1. Derive each entry's key with the helper, never by slugifying in the moment:

```bash
python3 tools/trigger_key.py --company "<company>" --signal "<signal>" --url "<url>"
```

2. Add ALL fetched signals (new and skipped) to
   `trigger_scraper/seen_triggers.json`:

```json
{
  "seen": {
    "<key from tools/trigger_key.py>": {
      "company": "...",
      "signal": "one-line signal summary",
      "trigger_type": "hiring_posting | icp_pipeline | funding_event | vendor_pilot | new_coo | new_leadership | e23_workstream",
      "track": "workflow | e23",
      "url": "...",
      "first_seen": "YYYY-MM-DD",
      "trigger_date": "YYYY-MM-DD | null",
      "data_quality": "verified | approx | stale | unconfirmed",
      "score": 0,
      "verdict": "qualified | watchlist | lead_to_investigate | dropped",
      "status": "new | staged | skipped",
      "source": "<source module, e.g. osfi-watch>",
      "icp_adjacent": false
    }
  }
}
```

3. Only present signals NOT already in the seen list.

### Step 5: Present Results

Ranked table, qualified first, then watchlist. For each: score, company,
trigger type, one-line signal, trigger date, evidence link. Name the scoring
band honestly; a watchlist item is not a qualified lead.

After presenting, ask which rows to stage. If the run found nothing new, say
exactly: "No new qualified triggers today."

### Step 6: Stage Rows (Approval Only)

Write the approved rows to `trigger_staging_YYYY-MM-DD.csv` using the exact
`leads.csv` column order from the rubric's output contract. Leave `id` empty:
IDs are assigned from the register's current max at append time, never here.

Never write to the real register from this skill. Appending staged rows to the
CRM is a separate, explicitly approved step.

---

## Important Rules

1. **Never fabricate signals.** Only present signals from actual module output
   or fetched evidence. A signal with no working evidence URL is dropped.
2. **Research only.** No outreach, no emails, no LinkedIn contact, no sends.
   Drafts go to the user first.
3. **Confirmed facts stay separate from inferred opportunity.** The signal is
   what happened; the buying hypothesis is inference. Never blur them.
4. **Email rules are absolute.** `verified` means published first-party;
   `inferred_format` needs an observed company address format; otherwise leave
   the email empty with confidence `unknown`. Never invent a format. The
   two-bounce stop-guessing rule stands.
5. **The real roster never ships.** `roster.csv` is gitignored. Only
   `roster.example.csv` is committed.
6. **A posting proves hiring intent**, not a broken workflow or willingness to
   outsource. Hiring signals need a second corroborating signal to score above
   watchlist.
