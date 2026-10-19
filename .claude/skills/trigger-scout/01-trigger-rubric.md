# Trigger Scoring Rubric

The single source of truth for what counts as a buying trigger. Every source
module feeds raw signals; this rubric decides whether a signal becomes a
qualified lead, a watchlist item, or nothing.

## Track A: Workflow Evidence diagnostic

**ICP.** Regulated Canadian operators with a live AI workflow or vendor
rollout: lenders, MIC managers, credit unions, alternative lenders.
50 to 500 employees; flag firms outside the band, do not auto-drop the
adjacent ones. The sharpest sub-segment is a newly appointed COO or operations
leader at a 50 to 200 person lender inside their first 90 days.

**Offer.** Fixed 10-day diagnostic, CAD 15 to 18k, ending in a
stop/fix/buy/build/scale decision on the workflow in question.

**What a qualified trigger looks like.** A named firm where something changed
that makes the diagnostic's decision urgent or newly possible: a new operations
leader who will want their own read on inherited AI work, a vendor pilot
hitting a checkpoint, a funding event that changes what the firm can spend, a
hiring signal paired with evidence of workflow strain.

## Track B: E-23 Readiness diagnostic

**ICP.** Mid-market federally regulated financial institutions preparing for
OSFI's E-23 deadline of May 1, 2027: banks, trust and loan companies, insurers
under OSFI supervision.

**Offer.** Fixed 10-day diagnostic, CAD 15 to 18k, producing model evidence
readiness for the deadline.

**What a qualified trigger looks like.** Regulatory movement that raises the
cost of waiting (OSFI AI safety-code or guideline developments, E-23 workstream
news), or firm-level evidence of preparation activity (model-risk, AI
governance, or compliance hiring; public statements about AI oversight).

## Trigger types

Use exactly these values; they match the register schema.

| trigger_type    | Counts when | Watchlist when | Drop when |
|-----------------|-------------|----------------|-----------|
| new_coo         | Named COO/ops leader appointed at an ICP firm, inside 90 days | Appointment announced but firm fit unconfirmed | Interim title, or outside ICP |
| new_leadership  | Relevant leadership appointment (CRO, CTO, head of ops/risk) **plus** a second operating signal | Appointment alone, no second signal | Role unrelated to operations, risk, or technology |
| vendor_pilot    | Named vendor pilot, rollout, or checkpoint at an ICP firm | Vendor named but pilot stage unclear | Press release with no firm commitment |
| hiring_posting  | Posting for model validation, AI/ML, compliance, or ops leadership **plus** corroborating strain signal | Posting alone | Role is generic backfill with no AI/ops content |
| funding_event   | Funding round, acquisition, or recapitalization at an ICP firm | Rumored, not closed | Firm outside ICP |
| e23_workstream  | OSFI/Fed regulatory development on AI, model risk, or E-23; firm-level E-24/E-23 prep disclosure | Commentary with no regulatory movement | Non-Canadian or non-financial regulation |
| icp_pipeline    | Firm matches ICP on verified facts and deserves investigation even without a dated trigger | Always the band for firms, not events | Firm provably outside ICP |

## Scoring dimensions (0 to 100 each)

1. **ICP fit (30%).** Firm is regulated, Canadian, in the size band, on the
   roster. Adjacent firms score lower, never zero on this dimension alone.
2. **Signal strength (25%).** How directly the signal implies the buying
   condition: a live workflow decision scores high; ambient news scores low.
3. **Timing (20%).** Trigger recency and deadline proximity. For E-23, months
   remaining to May 1, 2027. For new_coo, days since appointment.
4. **Evidence quality (15%).** Maps to `data_quality`: verified first-party
   evidence scores highest; approx, stale, unconfirmed progressively lower.
5. **Actionability (10%).** Can we name the buyer and write one crisp outreach
   question that separates ongoing staffing needs from a bounded project?

Overall score is the weighted sum, rounded to an integer.

## Vetoes

Any one of these caps the verdict, regardless of score:

- Firm provably outside the ICP with no adjacency: drop.
- No working evidence URL: drop.
- Trigger date older than 120 days with nothing new: drop as stale.
- Already present in the register (by company + signal): skip silently.
- A hiring posting with no second signal: cap at watchlist. A posting proves
  hiring intent, not a broken workflow or willingness to outsource.

## Verdict bands

- **qualified** (75+): stage the row.
- **watchlist** (50 to 74): track, do not stage yet.
- **lead_to_investigate** (25 to 49): firm or theme worth a look, no dated trigger.
- **dropped** (below 25, or any veto): record in seen state, do not present.

## Email rules

- `verified`: the address is published first-party by the person or the firm
  (team page, press release, official filing). Certainty `high`, unless the
  source is old or the domain may have changed (then `medium`).
- `inferred_format`: no published address, but the firm's email format is
  established from at least one observed address at that same firm. Construct
  the address in that format. Certainty `medium` (`low` when the only evidence
  is a third-party directory or conflicting signals).
- `unknown`: no format can be established from public evidence. Leave the email
  empty, confidence `unknown`, certainty blank.
- Never invent a format. An inference needs an observed example at that firm.
- Stop-guessing rule: after two bounces on constructed addresses at a firm,
  stop guessing there. Leave empty.

## Research-only rules

- No outreach, no emails, no LinkedIn contact, no sends. Drafts come to the
  user first.
- Confirmed facts stay separate from inferred opportunity in every summary.
- Never claim the diagnostic replaces a hire or fixes a named problem without
  evidence.

## Output contract (leads.csv column order)

Staged rows use exactly this column order. `id` is left empty and assigned
from the register's current max at append time; `date_added` is the staging
date.

`id, date_added, trigger_type, trigger_date, data_quality, person_name,
person_title, person_verified, person_email, email_confidence, email_certainty,
company, company_size, offer_track, status, outreach_status, goal,
trigger_summary, evidence, confirmed_vs_inferred, outreach_question, notes`

- `offer_track`: Decision Sprint | E-23 Evidence Work | funder-reporting offer
  | Hands-on Workshop | Sprint for a new COO
- `status` is qualification only: qualified | watchlist | lead_to_investigate.
  Outreach moves through `outreach_status`, never through `status`.
- `goal`: Workflow Evidence | E-23 Readiness (both, semicolon-separated, when
  dual-track).
- `trigger_summary`: what the trigger revealed and why it mattered, one to two
  sentences.
- `outreach_question`: one question distinguishing ongoing staffing needs from
  a bounded improvement project.
