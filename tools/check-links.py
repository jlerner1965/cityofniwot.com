#!/usr/bin/env python3
"""Check every outbound link on the site and report the ones that are broken.

A directory is only as good as its links, and they rot quietly: a business
closes, a county reorganizes its site, an organizer moves an event page. Run
this from anywhere, on a machine with ordinary internet access:

    python3 tools/check-links.py

    python3 tools/check-links.py --json report.json   # machine-readable too
    python3 tools/check-links.py --timeout 30         # slow hosts
    python3 tools/check-links.py --workers 4          # be gentler

    python3 tools/check-links.py --tries 1          # no retries (quick pass)

Exit status is 1 if anything is BROKEN, so CI can fail on it. Redirects and
sites that merely dislike robots are reported but do not fail the run.

A host that answers is believed at once — an HTTP status is a fact about the
link. A connection that dies before any answer is tried again, twice, a few
seconds apart, because that failure can belong to the network the check is
running on rather than to the site. Without it one reset fails the run, and a
check that cries wolf is one nobody reads.

What it does NOT do: judge whether a page still says what the listing claims
it says. That is an editorial check and belongs to a person.
"""
import argparse
import collections
import glob
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Fetched as a browser: several small business hosts return 403 to anything
# that looks automated, which would otherwise read as a dead link.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Not link rot, and not ours to chase: the font CDN and map deep links are
# generated, and our own pages are covered by the internal link check.
SKIP = ("fonts.googleapis.com", "fonts.gstatic.com", "google.com/maps",
        "townofniwot.com")


def collect():
    """Every external href on the site, mapped to the pages that use it."""
    found = collections.defaultdict(set)
    pages = (glob.glob(os.path.join(ROOT, "*.html"))
             + glob.glob(os.path.join(ROOT, "*", "index.html"))
             + glob.glob(os.path.join(ROOT, "*", "*", "index.html")))
    for path in sorted(pages):
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            url = m.group(1).replace("&amp;", "&")
            if any(s in url for s in SKIP):
                continue
            found[url].add(os.path.relpath(path, ROOT))
    return {u: sorted(v) for u, v in sorted(found.items())}


class Redirects(urllib.request.HTTPRedirectHandler):
    """Follow redirects, but remember where the chain ended up."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None:
            new.final_url = newurl
            new.redirected = getattr(req, "redirected", []) + [(code, newurl)]
        return new


def opener(timeout):
    ctx = ssl.create_default_context()
    return urllib.request.build_opener(Redirects(),
                                       urllib.request.HTTPSHandler(context=ctx))


def attempt(url, timeout):
    """One pass at a URL: HEAD, then GET if HEAD is refused.

    Returns (status, detail, final_url, answered). `answered` is True when a
    server actually replied — an HTTP status is a fact about the link and is
    never retried. False means nothing answered: a reset, a timeout, a DNS
    or TLS failure, which may be about the network this is running on.
    """
    op = opener(timeout)
    last = None
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers=HEADERS, method=method)
        try:
            with op.open(req, timeout=timeout) as resp:
                final = resp.geturl()
                if final.rstrip("/") != url.rstrip("/"):
                    return "REDIRECT", f"{resp.status} → {final}", final, True
                return "OK", str(resp.status), final, True
        except urllib.error.HTTPError as e:
            # 403/405/429 usually means "not to a robot", not "not there".
            if e.code in (403, 405, 429, 999):
                last = ("BLOCKED", f"HTTP {e.code} ({method})", url, True)
                continue
            last = ("BROKEN", f"HTTP {e.code} {e.reason}", url, True)
            if method == "GET":
                return last
        except urllib.error.URLError as e:
            last = ("BROKEN", f"{type(e.reason).__name__}: {e.reason}", url, False)
        except Exception as e:            # socket, ssl, decoding, redirect loops
            last = ("BROKEN", f"{type(e).__name__}: {e}", url, False)
    return last or ("BROKEN", "no response", url, False)


def check(url, timeout, tries=3):
    """Return (status, detail, final_url), retrying only what never answered.

    Exit status gates a deploy, so a run that calls a live site broken is
    worse than no run at all: the next real breakage reads as more noise.
    A host that answers — 404, 500, 403 — has told us about the link and is
    taken at its word. A connection that dies before any answer has told us
    nothing, so it is tried again after a pause. A site that is genuinely
    gone simply fails three times and is still reported BROKEN, with the
    attempt count in the detail so a reader can tell the two apart.
    """
    for n in range(1, tries + 1):
        status, detail, final, answered = attempt(url, timeout)
        if answered:
            return status, detail, final
        if n < tries:
            time.sleep(n * 2)             # 2s, then 4s
    return status, f"{detail} (no answer in {tries} attempts)", final


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=int, default=20, help="seconds per request")
    ap.add_argument("--workers", type=int, default=8, help="parallel requests")
    ap.add_argument("--json", metavar="FILE", help="also write a JSON report")
    ap.add_argument("--tries", type=int, default=3,
                    help="attempts at a host that never answers (default 3)")
    args = ap.parse_args()

    links = collect()
    print(f"Checking {len(links)} external links "
          f"across {len({re.match(r'https?://([^/]+)', u).group(1) for u in links})} hosts…\n")

    results = {}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check, u, args.timeout, args.tries): u for u in links}
        for fut, url in futures.items():
            status, detail, final = fut.result()
            results[url] = {"status": status, "detail": detail,
                            "final_url": final, "pages": links[url]}

    order = {"BROKEN": 0, "REDIRECT": 1, "BLOCKED": 2, "OK": 3}
    counts = collections.Counter(r["status"] for r in results.values())

    for status in ("BROKEN", "REDIRECT", "BLOCKED"):
        rows = [(u, r) for u, r in results.items() if r["status"] == status]
        if not rows:
            continue
        print(f"── {status} ({len(rows)}) " + "─" * 40)
        for url, r in sorted(rows):
            print(f"  {url}\n      {r['detail']}\n      on: {', '.join(r['pages'])}")
        print()

    print("─" * 56)
    print("  ".join(f"{s}: {counts.get(s, 0)}"
                    for s in ("OK", "REDIRECT", "BLOCKED", "BROKEN")))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(dict(sorted(results.items(), key=lambda kv: order[kv[1]["status"]])),
                      fh, indent=1)
        print(f"\nWrote {args.json}")

    return 1 if counts.get("BROKEN") else 0


if __name__ == "__main__":
    sys.exit(main())
