#!/usr/bin/env python3
"""Canonical dedupe keys for trigger-scout signals.

The key is a pure function of (company, signal, url): two runs that slugify
differently would store the same signal twice and defeat dedup. Long signals
are length-capped with a hash of the full slug appended, so a truncated
signal is stable across runs and two different long signals never collide.

Usage:
    python3 tools/trigger_key.py --company "<company>" --signal "<signal>" --url "<url>"
    python3 tools/trigger_key.py --audit   # verify stored keys against the current scheme
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "trigger_scraper" / "seen_triggers.json"
MAX_SLUG = 60


def slug(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > MAX_SLUG:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]
        text = f"{text[:MAX_SLUG - 9]}-{digest}"
    return text or "untitled"


def key(company: str, signal: str, url: str) -> str:
    return f"{slug(company)}--{slug(signal)}--{hashlib.sha256((url or '').encode('utf-8')).hexdigest()[:10]}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--company", default="")
    ap.add_argument("--signal", default="")
    ap.add_argument("--url", default="")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()

    if args.audit:
        if not STATE.exists():
            print("no state file yet - nothing to audit")
            return 0
        data = json.loads(STATE.read_text(encoding="utf-8"))
        bad = 0
        for k, entry in data.get("seen", {}).items():
            want = key(entry.get("company", ""), entry.get("signal", ""), entry.get("url", ""))
            if k != want:
                print(f"  MISMATCH {k}\n           -> {want}")
                bad += 1
        print(f"audit: {len(data.get('seen', {}))} entries, {bad} mismatched")
        return 1 if bad else 0

    print(key(args.company, args.signal, args.url))
    return 0


if __name__ == "__main__":
    sys.exit(main())
