# Agent Guidelines: Trigger Scout

This workspace detects buying triggers for a fixed ICP firm roster. It is a
hard fork of a job-search framework, rebuilt around roster-centric signal
detection: the roster names the firms, source modules fetch candidate signals,
and the trigger rubric decides what each signal is worth.

## Thin-Pointer Design (Single Source of Truth)

To prevent duplication and configuration drift across agent frameworks
(Claude Code, Codex, Cursor, Gemini CLI, etc.), this workspace uses a unified
thin-pointer design:

1. **Trigger rubric:** `.claude/skills/trigger-scout/01-trigger-rubric.md` is
   the single source of truth for what counts as a trigger: tracks, trigger
   types, scoring dimensions, vetoes, verdict bands, email rules, and the
   output contract. Edit it when the qualification bar moves.
2. **Canonical workflow specifications:** the step-by-step instructions live in
   `.claude/skills/trigger-scout/SKILL.md` and `.claude/commands/triggers.md`.
   Do not duplicate these rules. Treat them as the single source of truth.
3. **Trigger source modules:** signal-fetching CLIs live under
   `.agents/skills/` in the portable Agent Skills format, one `SKILL.md` per
   source, each declaring `kind: trigger-source` in its frontmatter. The scout
   discovers them by globbing; see
   `.claude/skills/trigger-scout/02-source-contract.md` before adding one.
4. **Roster:** the firm list is `roster.csv` (gitignored, never committed) or
   the absolute path in `TRIGGER_ROSTER`. Only `roster.example.csv` ships.

## Rules that matter here

- Research only. No outreach, no emails, no register writes without explicit
  approval. Staged rows go to `trigger_staging_YYYY-MM-DD.csv`; appending them
  to the register is a separate, explicitly approved step.
- Never fabricate signals. A signal with no working evidence URL is dropped.
- Email rules are absolute: `verified` means published first-party;
  `inferred_format` needs an observed company address format; otherwise leave
  the email empty with confidence `unknown`. Never invent a format.
- Dedupe keys come from `python3 tools/trigger_key.py`, never from ad-hoc
  slugifying.
