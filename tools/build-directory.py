#!/usr/bin/env python3
"""Rebuild the Eat & Shop directory from data/directory.json.

    python3 tools/build-directory.py            # write eat-shop/index.html
    python3 tools/build-directory.py --check    # exit 1 if the page is stale

The page carries every listing in the HTML, folded by category, so it works
without JavaScript and a crawler reads all of it. This writes those groups,
the category chips and phone selector with their counts, the "last checked"
sentence, the result count, and the ItemList structured data in <head>,
all from the one data file.

A record is published only while `hidden` is false and `status` is
"active" or "correction-pending". A closed or moved business keeps its
record (with `_notes` saying what happened and when) but leaves the page;
add a redirect in vercel.json if it ever had a page of its own. Keys that
begin with an underscore are editorial and are never written to the page.
"""
import datetime as dt, html, json, os, re, sys
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
SITE = "https://townofniwot.com"
PAGE = "eat-shop/index.html"
PUBLISHED = ("active", "correction-pending")

def esc(s): return html.escape(str(s), quote=True)
def rd(f): return open(f, encoding="utf-8").read()
def human(iso):
    d = dt.date.fromisoformat(iso); return f"{d.strftime('%B')} {d.day}, {d.year}"

data = json.load(open("data/directory.json", encoding="utf-8"))
cats = data["categories"]
by_slug = {c["slug"]: c["label"] for c in cats}
ids = [l["id"] for l in data["listings"]]
assert len(ids) == len(set(ids)), "duplicate listing id"
for l in data["listings"]:
    assert l["category"] in by_slug, f"{l['id']}: unknown category {l['category']}"
    assert l["status"] in ("active", "correction-pending", "closed", "moved"), f"{l['id']}: bad status"
    assert l.get("verifiedAt") and l.get("url") and l.get("linkLabel"), f"{l['id']}: needs verifiedAt, url, linkLabel"
live = [l for l in data["listings"] if not l.get("hidden") and l["status"] in PUBLISHED]

def row(l):
    cat = by_slug[l["category"]]
    attrs = (f'data-cat="{esc(l["category"])}" data-name="{esc(l["name"])}" data-category="{esc(cat)}" '
             f'data-note="{esc(l["description"])}"')
    if l.get("area"): attrs += f' data-area="{esc(l["area"])}"'
    if l.get("address"): attrs += f' data-address="{esc(l["address"])}"'
    left = (f'<h3 class="n-h3" style="font-size:1.375rem;color:var(--n-evergreen)">{esc(l["name"])}</h3>\n'
            f'<div class="n-label" style="margin-top:8px">{esc(cat)}</div>\n')
    if l.get("description"):
        left += f'<p class="n-body" style="margin:10px 0 0;max-width:58ch;font-size:.9375rem">{esc(l["description"])}</p>\n'
    right = ""
    if l.get("address"): right += f'<div class="n-small" style="font-size:.875rem;color:var(--n-ink)">{esc(l["address"])}</div>\n'
    if l.get("area"): right += f'<div class="n-small" style="font-size:.875rem">{esc(l["area"])}</div>\n'
    track = "business_website_click" if l["sourceType"] == "business-site" else "business_listing_click"
    right += (f'<a class="n-link" href="{esc(l["url"])}" rel="noopener" style="justify-self:start" data-track="{track}">'
              f'{esc(l["linkLabel"])} <span aria-hidden="true">&#8599;</span></a>\n')
    if l["status"] == "correction-pending":
        right += '<div class="n-small" style="font-size:.8125rem;color:var(--n-red-ink)">A correction to this listing is being checked</div>\n'
    right += f'<div class="n-small" style="font-size:.8125rem" data-verified="{esc(l["verifiedAt"])}">Checked {esc(human(l["verifiedAt"]))}</div>\n'
    return (f'<li class="n-row" id="{esc(l["id"])}" data-listing {attrs}>\n<div>\n{left}</div>\n'
            f'<div style="display:grid;gap:8px;align-content:start">\n{right}</div>\n</li>\n')

def group(c):
    own = [l for l in live if l["category"] == c["slug"]]
    if not own: return ""
    return (f'<details class="n-group" id="cat-{c["slug"]}" data-group="{c["slug"]}">\n'
            f'<summary><span class="n-h3" data-group-label>{esc(c["label"])}</span><span style="display:flex;align-items:center;gap:12px">'
            f'<span class="n-label n-label--quiet" data-group-count>{len(own)}</span><span class="n-gmark" aria-hidden="true"></span></span></summary>\n'
            f'<ul>\n{"".join(row(l) for l in own)}</ul>\n</details>\n')

def chips():
    out = [f'<label class="n-chip"><input type="radio" name="category" value="all" checked><span class="n-chip-l"><span data-chip-label>All categories</span> <span class="n-chip-n">{len(live)}</span></span></label>\n']
    opts = [f'<option value="all" selected>All categories ({len(live)})</option>\n']
    for c in cats:
        n = sum(1 for l in live if l["category"] == c["slug"])
        if not n: continue
        out.append(f'<label class="n-chip"><input type="radio" name="category" value="{c["slug"]}"><span class="n-chip-l"><span data-chip-label>{esc(c["label"])}</span> <span class="n-chip-n">{n}</span></span></label>\n')
        opts.append(f'<option value="{c["slug"]}">{esc(c["label"])} ({n})</option>\n')
    return "".join(out), "".join(opts)

def itemlist():
    items = []
    for n, l in enumerate(live, 1):
        item = {"@type": l["schemaType"], "@id": f"{SITE}/eat-shop/#{l['id']}", "name": l["name"]}
        if l.get("description"): item["description"] = l["description"]
        item["url"] = l["url"]
        addr = {"@type": "PostalAddress"}
        if l.get("address"): addr["streetAddress"] = l["address"]
        if l.get("postalCode"): addr["postalCode"] = l["postalCode"]
        addr.update({"addressLocality": "Niwot", "addressRegion": "CO", "addressCountry": "US"})
        item["address"] = addr
        items.append({"@type": "ListItem", "position": n, "url": f"{SITE}/eat-shop/#{l['id']}", "item": item})
    return {"@context": "https://schema.org", "@type": "ItemList", "name": "Niwot business directory",
            "numberOfItems": len(live), "itemListElement": items}

def build(t):
    chip_html, opt_html = chips()
    t = re.sub(r'(<legend class="n-label n-label--quiet">Filter by category</legend>\n).*?(</fieldset>)',
               lambda m: m.group(1) + chip_html + m.group(2), t, count=1, flags=re.S)
    t = re.sub(r'(<select id="dir-cat" data-dir-select>\n).*?(</select>)',
               lambda m: m.group(1) + opt_html + m.group(2), t, count=1, flags=re.S)
    t = re.sub(r'(<span aria-live="polite" aria-atomic="true" class="n-label n-label--quiet" data-dir-count>)[^<]*(</span>)',
               lambda m: m.group(1) + f"{len(live)} listings" + m.group(2), t, count=1)
    dates = sorted({l["verifiedAt"] for l in live})
    sentence = (f"Listings were last checked between {human(dates[0])} and {human(dates[-1])}; each row shows its own date."
                if dates[0] != dates[-1] else f"Listings were last checked on {human(dates[0])}.")
    t = re.sub(r'(<span data-dir-verified>)[^<]*(</span>)', lambda m: m.group(1) + esc(sentence) + m.group(2), t, count=1)
    t = re.sub(r'(<div data-dir-list style="[^"]*">\n).*?(</div>\n<div data-dir-empty)',
               lambda m: m.group(1) + "".join(group(c) for c in cats) + m.group(2), t, count=1, flags=re.S)
    ld = '<script type="application/ld+json">' + json.dumps(itemlist(), ensure_ascii=False, separators=(",", ":")) + '</script>'
    t, n = re.subn(r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"ItemList".*?</script>',
                   lambda m: ld, t, count=1, flags=re.S)
    assert n == 1, "ItemList block not found"
    return t

def main():
    before = rd(PAGE)
    after = build(before)
    if "--check" in sys.argv:
        if after != before:
            print(f"{PAGE} is stale: run python3 tools/build-directory.py"); return 1
        print(f"{PAGE} matches data/directory.json ({len(live)} listings published)"); return 0
    if after != before:
        open(PAGE, "w", encoding="utf-8").write(after); print(f"wrote {PAGE}: {len(live)} listings in {sum(1 for c in cats if any(l['category']==c['slug'] for l in live))} categories")
    else:
        print(f"{PAGE} already current ({len(live)} listings)")
    hidden = [l["id"] for l in data["listings"] if l not in live]
    if hidden: print("not published:", ", ".join(hidden))
    return 0

if __name__ == "__main__":
    sys.exit(main())
