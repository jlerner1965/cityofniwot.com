#!/usr/bin/env python3
"""Report claims on the site that have passed their expiry date.

Some sentences are only true until a date: an election described as upcoming,
a promise to re-check something after a review. Nothing edits them when that
date passes, and on a civic page a stale tense is worse than a stale link —
it tells a resident a vote is still coming when it has already happened.

    python3 tools/check-dated-content.py

Each check is a date, a file, and a phrase that should be gone by then. Exit
status is 1 if anything has expired, so a scheduled job can raise it. Silent
when everything is current, so it only speaks when there is something to do.

When a claim is fixed, its phrase stops matching and the check goes quiet on
its own — there is no list to remember to update.
"""
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = dt.datetime.now(ZoneInfo("America/Denver")).date()

# Each entry: once `after` has passed, `phrase` should no longer appear in
# `file` (or, with `unless`, that phrase should have appeared alongside it).
CHECKS = [
    {
        "after": "2026-11-03",
        "file": "index.html",
        "phrase": "is scheduled for November 3, 2026",
        "what": "The homepage FAQ still calls the incorporation election upcoming.",
        "do": "Rewrite the answer in past tense with the outcome, and make the "
              "matching FAQPage JSON-LD in <head> say the same thing — the "
              "visible answer and the structured data have to agree.",
    },
    {
        "after": "2026-11-03",
        "file": "index.html",
        "phrase": "Review what is on the ballot, who may vote",
        "what": "The homepage notice band still points at a ballot to be voted.",
        "do": "Change it to the result, or drop the band and let the election "
              "page carry the record.",
    },
    {
        "after": "2026-11-03",
        "file": "index.html",
        "phrase": ">2026 Election<",
        "what": "\"2026 Election\" still holds one of six slots in the nav bar.",
        "do": "The label stays accurate — the page is about the 2026 election — "
              "but a finished vote does not need prime position. Consider "
              "moving it to the collapsed-menu tier beside Our Story and "
              "Contact, which means editing the nav in every HTML file.",
    },
    {
        "after": "2026-09-11",
        "file": "civic/incorporation-election/index.html",
        "phrase": "This page will carry a dated note when it is",
        "unless": "Ballot language re-checked on",
        "what": "The page promised a dated note once the ballot proof was "
                "reviewed on September 11. The date has passed and no note "
                "has been added.",
        "do": "Re-check the reproduced ballot language against the "
              "Commission's own ballot page, then add a note containing the "
              "words \"Ballot language re-checked on <date>\". That phrase is "
              "what silences this check.",
    },
]


def main():
    expired = []
    for c in CHECKS:
        after = dt.date.fromisoformat(c["after"])
        if TODAY <= after:
            continue
        path = os.path.join(ROOT, c["file"])
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            continue
        if c["phrase"] not in text:
            continue
        if c.get("unless") and c["unless"] in text:
            continue
        expired.append((c, after))

    if not expired:
        print(f"Nothing has expired as of {TODAY}.")
        return 0

    print(f"{len(expired)} thing(s) on the site passed their date:\n")
    for c, after in expired:
        days = (TODAY - after).days
        print(f"### {c['what']}")
        print(f"- **Due:** {after} ({days} day{'s' if days != 1 else ''} ago)")
        print(f"- **Where:** `{c['file']}`")
        print(f"- **Still says:** `{c['phrase']}`")
        print(f"- **To fix:** {c['do']}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
