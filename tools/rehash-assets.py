#!/usr/bin/env python3
"""Make every hashed asset filename match the bytes inside it.

`assets/css/guide.<hash>.css` and the scripts beside it carry a content hash
in the name, and they are served with a one-day cache plus a week of
stale-while-revalidate. That is only safe while the hash is true. Edit such a
file in place and the name stops matching: the server has the new bytes but
every browser that has been here recently keeps the old ones, for a day or
more. If the HTML changed in the same commit and depends on the new CSS —
a rule that hides something, a new element — those visitors get a broken
page, and it cannot be reproduced on a fresh browser.

    python3 tools/rehash-assets.py            # rename and rewrite references
    python3 tools/rehash-assets.py --check    # report only, exit 1 if stale

Run it after editing anything under assets/. The scripts import each other,
so renaming one changes its importers, which changes their hashes in turn;
this repeats until everything settles.
"""
import argparse
import glob
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = re.compile(r"^(?P<base>.+)\.(?P<hash>[0-9a-f]{10})\.(?P<ext>css|js)$")


def assets():
    return sorted(glob.glob(os.path.join(ROOT, "assets", "css", "*.css"))
                  + glob.glob(os.path.join(ROOT, "assets", "js", "*.js")))


def referrers():
    """Everything that can name an asset: the pages, and the scripts."""
    return (sorted(glob.glob(os.path.join(ROOT, "*.html"))
                   + glob.glob(os.path.join(ROOT, "*", "index.html"))
                   + glob.glob(os.path.join(ROOT, "*", "*", "index.html")))
            + assets())


def digest(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:10]


def one_pass(check):
    """Fix every asset whose name is out of date. Returns what it found."""
    found = []
    for path in assets():
        name = os.path.basename(path)
        m = NAME.match(name)
        if not m:
            continue
        actual = digest(path)
        if actual == m.group("hash"):
            continue
        new_name = f"{m.group('base')}.{actual}.{m.group('ext')}"
        found.append((name, new_name))
        if check:
            continue
        os.rename(path, os.path.join(os.path.dirname(path), new_name))
        for ref in referrers():
            with open(ref, encoding="utf-8") as fh:
                text = fh.read()
            if name in text:
                with open(ref, "w", encoding="utf-8") as fh:
                    fh.write(text.replace(name, new_name))
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report stale names without renaming anything")
    args = ap.parse_args()

    if args.check:
        stale = one_pass(check=True)
        for old, new in stale:
            print(f"  stale: {old}\n         its bytes hash to {new.split('.')[-2]}")
        if stale:
            print(f"\n{len(stale)} asset name(s) no longer match their contents.")
            print("Run: python3 tools/rehash-assets.py")
            return 1
        print(f"All {len(assets())} hashed assets match their contents.")
        return 0

    renamed = []
    # Renaming a file edits its importers, which makes their own names stale,
    # so keep going until a pass finds nothing left to do.
    for _ in range(20):
        found = one_pass(check=False)
        if not found:
            break
        renamed += found
    else:
        print("gave up after 20 passes — is there an import cycle?")
        return 1

    if not renamed:
        print(f"Nothing to do: all {len(assets())} hashed assets already match.")
        return 0
    for old, new in renamed:
        print(f"  {old}\n    -> {new}")
    print(f"\nRenamed {len(renamed)}, references rewritten.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
