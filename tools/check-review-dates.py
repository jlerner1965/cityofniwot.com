#!/usr/bin/env python3
"""List the time-sensitive records whose review date has passed.

Every event, directory listing and source-register entry carries the date it
was last checked and, where it matters, the date it is next due. This reads
data/events.json, data/directory.json and data/source-registry.json and
prints what is overdue, oldest first, so a review session has a worklist.

    python3 tools/check-review-dates.py             # overdue only
    python3 tools/check-review-dates.py --all       # everything, with due dates
    python3 tools/check-review-dates.py --days 14   # due within two weeks too

Exit status is 1 when something is overdue. Review intervals, when a record
carries no nextReview of its own, are:

    events              14 days after verifiedAt, and never past the event
    directory listings  90 days after verifiedAt
    source register     as each entry says (nextReview is required there)
"""
import argparse, datetime as dt, json, os, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = dt.datetime.now(ZoneInfo("America/Denver")).date()
EVENT_DAYS, LISTING_DAYS = 14, 90

def load(name):
    try:
        return json.load(open(os.path.join(ROOT, "data", name), encoding="utf-8"))
    except FileNotFoundError:
        return None

def d(s): return dt.date.fromisoformat(s)

def collect():
    rows = []
    events = load("events.json") or []
    for e in events:
        if e.get("status") == "tentative" or not e.get("startDate"):
            due = e.get("nextReview") or (d(e["verifiedAt"]) + dt.timedelta(days=EVENT_DAYS)).isoformat()
        else:
            last = e.get("recurrence", {}).get("until") or e.get("endDate") or e["startDate"]
            if d(last) < TODAY: continue            # past: nothing left to verify
            due = e.get("nextReview") or min(d(e["verifiedAt"]) + dt.timedelta(days=EVENT_DAYS), d(last)).isoformat()
        rows.append(("event", e["id"], e["verifiedAt"], due, e.get("sourceUrl", "")))
    dirdata = load("directory.json") or {"listings": []}
    for l in dirdata["listings"]:
        if l.get("hidden") or l.get("status") in ("closed", "moved"): continue
        due = l.get("nextReview") or (d(l["verifiedAt"]) + dt.timedelta(days=LISTING_DAYS)).isoformat()
        rows.append(("listing", l["id"], l["verifiedAt"], due, l.get("url", "")))
    for r in load("source-registry.json") or []:
        if r.get("status") == "retired": continue
        rows.append(("source", f"{r['page']} — {r['claim'][:60]}", r["lastChecked"], r["nextReview"], r.get("sourceUrl", "")))
    return sorted(rows, key=lambda r: r[3])

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true"); ap.add_argument("--days", type=int, default=0)
    a = ap.parse_args()
    horizon = TODAY + dt.timedelta(days=a.days)
    rows = collect()
    shown = rows if a.all else [r for r in rows if d(r[3]) <= horizon]
    overdue = [r for r in rows if d(r[3]) < TODAY]
    if not shown:
        print(f"Nothing is due for review as of {TODAY} ({len(rows)} records tracked)."); return 0
    print(f"{len(overdue)} overdue, {len(shown)} shown, {len(rows)} tracked, as of {TODAY}\n")
    for kind, ident, checked, due, url in shown:
        flag = "OVERDUE" if d(due) < TODAY else "due"
        print(f"{flag:8} {due}  {kind:8} {ident}\n         checked {checked}  {url}")
    return 1 if overdue else 0

if __name__ == "__main__":
    sys.exit(main())
