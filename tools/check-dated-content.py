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
        # The one dated claim the site makes about itself, on 31 pages, and
        # until now the only one nothing watched. It does not become false
        # in October — it was reviewed in September and always will have
        # been — it becomes misleading: a guide that says "Reviewed
        # September 2026" in the spring is telling a reader its listings
        # were checked recently when they were not. A quarter is the
        # horizon the maintenance schedule already works to.
        "after": "2026-12-31",
        "file": "index.html",
        "phrase": "Reviewed September 2026",
        "what": "The footer stamp on 31 pages still reads \"Reviewed September 2026\", "
                "which is now more than a quarter old.",
        "do": "Work the quarterly pass in docs/maintenance-schedule.md — the "
              "directory listings against their sources, the resident-resource "
              "and organization links, the transit and parking paragraphs — "
              "then set the stamp to the month you did it, in the footer of "
              "every HTML file. It is one line: <span>Reviewed <month> "
              "<year></span>. The election page and the privacy page carry "
              "their own dates instead and are not part of this.",
    },
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
        "what": "\"2026 Election\" still leads the footer's Civic column.",
        "do": "The label stays accurate — the page is about the 2026 election — "
              "but a finished vote does not need to be the first thing under "
              "Civic. Consider putting /civic/ first and relabelling this one "
              "\"2026 Election result\", in the footer of every HTML file. (The "
              "primary nav carries the /civic/ hub, not this page, so the bar "
              "itself needs no change.)",
    },
    {
        "after": "2026-11-03",
        "file": "civic/index.html",
        "phrase": "voters inside a proposed boundary decide whether that should change",
        "what": "The civic hub still describes the incorporation vote as ahead.",
        "do": "Rewrite the lead and the \"Current election\" band in past tense with "
              "the official status (preliminary, then certified), relabel the band "
              "\"Recent election\", and keep the link to the election page.",
    },
    {
        "after": "2026-11-03",
        "file": "our-story/index.html",
        "phrase": "in November 2026 voters inside a proposed boundary decide",
        "what": "Our Story's \"Today\" entry still says the November 2026 vote is to come.",
        "do": "Say what voters decided, citing the certified result, in both the "
              "timeline entry and the \"Niwot today\" band below it.",
    },
    {
        "after": "2026-11-03",
        "file": "community/index.html",
        "phrase": "to administer the November 2026 incorporation election",
        "what": "The Niwot Election Commission card still describes its job in the present tense.",
        "do": "Say the Commission administered the November 3, 2026 election, and "
              "note whether it still exists once the court's order is entered.",
    },
    {
        "after": "2026-11-03",
        "file": "llms.txt",
        "phrase": "neutral voter information with links to official election authorities",
        "what": "llms.txt still describes the election page as voter information.",
        "do": "Describe it as the record of the 2026 election and its result.",
    },
    {
        "after": "2026-11-03",
        "file": "civic/incorporation-election/index.html",
        "phrase": "Before you vote",
        "what": "The election page still opens with voting tasks.",
        "do": "Follow docs/election-transition.md: remove the voting tasks, add "
              "the dated status band, label results preliminary until certified, "
              "and add the archive label once certified.",
    },
    {
        "after": "2026-09-18",
        "file": "civic/incorporation-election/index.html",
        "phrase": "Open until noon, Friday, September 18, 2026",
        "what": "The comment-deadline panel is past.",
        "do": "Replace it with what the Commission published after its September 18 "
              "meeting, or remove it.",
    },
    {
        "after": "2026-09-29",
        "file": "data/events.json",
        "phrase": "\"until\": \"2026-09-29\"",
        "what": "The weekly Trivia Night record has run out of read dates.",
        "do": "Re-read https://niwot.com/events/trivia-night/ and extend `until` to "
              "the last Tuesday shown, or retire the record if the listing is gone. "
              "Then run tools/build-event-pages.py.",
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
    missing = []
    for c in CHECKS:
        after = dt.date.fromisoformat(c["after"])
        if TODAY <= after:
            continue
        path = os.path.join(ROOT, c["file"])
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            # A check is a claim about a file. If the file has moved, the
            # check is not satisfied — it is unenforceable, and silence here
            # would retire it without anyone deciding to.
            missing.append(c)
            continue
        if c["phrase"] not in text:
            continue
        if c.get("unless") and c["unless"] in text:
            continue
        expired.append((c, after))

    if missing:
        print("These checks name a file that is no longer there, so nothing "
              "is watching what they describe:\n")
        for c in missing:
            print(f"- `{c['file']}` — {c['what']}")
            print("  Point the check at the file that carries this wording now, "
                  "or drop the check if the wording is gone.\n")

    if not expired:
        if missing:
            return 1
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
