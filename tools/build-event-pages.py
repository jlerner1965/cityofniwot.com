#!/usr/bin/env python3
"""Regenerate the per-event pages under /events/<id>/ and sitemap.xml.

Source of truth is the JSON in <script id="niwot-events"> on events/index.html
(addresses come from that page's Event JSON-LD). Run from anywhere after
updating the events page:

    python3 tools/build-event-pages.py

Pages for events that have a start date are written; tentative events without
a date are skipped. Existing pages are overwritten. The header and footer are
copied from 404/index.html so they always match the rest of the site.
"""
import re, json, html, glob, os, subprocess, datetime as dt
from zoneinfo import ZoneInfo
ROOT="/home/user/cityofniwot.com"; os.chdir(ROOT)
SITE="https://townofniwot.com"; TZ=ZoneInfo("America/Denver"); TODAY=dt.date.today()
ROBOTS='<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">'
ORG={"@type":"Organization","@id":SITE+"/#org","name":"TownofNiwot.com","url":SITE+"/",
     "description":"An independent community guide to Niwot, Colorado. Not a municipal government website.",
     "logo":{"@type":"ImageObject","url":SITE+"/apple-touch-icon.png","width":180,"height":180}}
PLACE={"@type":"Place","@id":SITE+"/#niwot","name":"Niwot, Colorado",
       "description":"An unincorporated community in Boulder County, Colorado, between Boulder and Longmont, with a historic Old Town on Second Avenue and Cottonwood Square.",
       "address":{"@type":"PostalAddress","addressLocality":"Niwot","addressRegion":"CO","postalCode":"80503","addressCountry":"US"},
       "geo":{"@type":"GeoCoordinates","latitude":40.1039,"longitude":-105.1708},
       "containedInPlace":{"@type":"AdministrativeArea","name":"Boulder County, Colorado"},
       "sameAs":["https://en.wikipedia.org/wiki/Niwot,_Colorado"]}
def rd(f): return open(f,encoding="utf-8").read()
def wr(f,s):
    """Write f, and say whether that changed anything."""
    os.makedirs(os.path.dirname(f) or ".",exist_ok=True)
    try: same = open(f,encoding="utf-8").read()==s
    except FileNotFoundError: same=False
    if not same: open(f,"w",encoding="utf-8").write(s)
    return not same
def esc(s): return html.escape(str(s),quote=True)
def ld(obj): return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False,separators=(",",":"))+'</script>'
def trim(s,n=155):
    if len(s)<=n: return s
    return s[:n].rsplit(" ",1)[0].rstrip(",;:—- ")+"…"
def set_meta(h,name,content,prop=False):
    attr='property' if prop else 'name'
    pat=re.compile(r'<meta %s="%s" content="[^"]*">'%(attr,re.escape(name)))
    return pat.sub('<meta %s="%s" content="%s">'%(attr,name,esc(content)),h)
def add_robots(h):
    if 'name="robots"' in h: return h
    return h.replace('<link rel="canonical"', ROBOTS+'\n<link rel="canonical"',1)
def add_ld(h,obj):
    return h.replace('</head>', ld(obj)+'\n</head>',1)

# ---------- 1. events data ----------
ev_html=rd("events/index.html")
events=json.loads(re.search(r'id="niwot-events"[^>]*>(.*?)</script>',ev_html,re.S).group(1))
blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',ev_html,re.S)
ldev=json.loads(blocks[0]); ld_list=ldev["@graph"] if isinstance(ldev,dict) and "@graph" in ldev else ldev
addr_by_name={e["name"]:e.get("location",{}).get("address") for e in ld_list if isinstance(e,dict) and e.get("@type")=="Event"}
byid={e["id"]:e for e in events}
name_to_id={}
for e in events: name_to_id.setdefault(e["name"],e["id"])

def iso(date,time):
    y,m,d=map(int,date.split("-")); hh,mm=map(int,time.split(":"))
    return dt.datetime(y,m,d,hh,mm,tzinfo=TZ).isoformat()
def fmt_time(t):
    hh,mm=map(int,t.split(":")); ap="am" if hh<12 else "pm"; h12=hh%12 or 12
    return f"{h12}:{mm:02d} {ap}" if mm else f"{h12} {ap}"
def time_label(e):
    if not e.get("startTime"): return ""
    s=fmt_time(e["startTime"]); 
    if e.get("endTime"):
        en=fmt_time(e["endTime"]); 
        if s[-2:]==en[-2:]: s=s[:-3]
        return f"{s}–{en}"
    return s
WD=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
def d(s): return dt.date.fromisoformat(s)
def long_date(s): x=d(s); return f"{WD[x.weekday()]}, {x.strftime('%B')} {x.day}, {x.year}"
def short_date(s): x=d(s); return f"{x.strftime('%b')} {x.day}, {x.year}"
def date_label(e):
    r=e.get("recurrence")
    if r:
        a,b=d(e["startDate"]),d(r["until"]); wd=WD[r["weekday"]-1] if r["weekday"]>=1 else WD[6]
        return f"{wd}s, {a.strftime('%B')} {a.day} – {b.strftime('%B')} {b.day}, {b.year}"
    return long_date(e["startDate"])
def last_date(e):
    r=e.get("recurrence"); return r["until"] if r else e["startDate"]
def page_url(e): return f"{SITE}/events/{e['id']}/"
def deep_link(e):
    r=e.get("recurrence"); date=e["startDate"]
    if r:  # next occurrence on/after today, else first
        x=d(e["startDate"]); 
        while x<TODAY and x<=d(r["until"]): x+=dt.timedelta(days=7)
        if x>d(r["until"]): x=d(e["startDate"])
        date=x.isoformat()
    return f"/events/?date={date}&event={e['id']}#cal-h"

# header/footer template from 404 page
p404=rd("404/index.html")
header=re.search(r'(<body>.*?)<main id="main">',p404,re.S).group(1)
footer=re.search(r'</main>(.*?)</body>',p404,re.S).group(1)
footer=footer.replace('<span>Reviewed September 2026</span>','<span>Reviewed September 2026</span>')
head_common=re.search(r'(<link rel="icon".*?<script src="/assets/js/guide[^>]*></script>)',p404,re.S).group(1)
EV_IMG=SITE+"/assets/photos/whistle-stop-caboose.jpg"
EV_ALT="The red CB&Q caboose at Whistle Stop Park in Niwot, home of the summer concert series"

dated=[e for e in events if e.get("startDate")]
upcoming=sorted([e for e in dated if d(last_date(e))>=TODAY],key=lambda e:e["startDate"])

def event_page(e):
    name=e["name"]; loc=e["location"]["name"]; org=e["organizer"]; tl=time_label(e); dl_=date_label(e)
    is_conf=e["status"]=="confirmed"
    title=f"{name} — {short_date(e['startDate'])} | Niwot Events"
    if e.get("recurrence"): title=f"{name} {d(e['startDate']).year} | Niwot Events"
    if len(title)>65: title=f"{name} | Niwot, CO Events"
    desc=trim(f"{name} in Niwot, Colorado: {dl_}{', '+tl if tl else ''}, at {loc}. {e['description']}")
    free=bool(e.get("cost")) and e["cost"].lower().startswith("free")
    addr=addr_by_name.get(name) or {"@type":"PostalAddress","addressLocality":"Niwot","addressRegion":"CO","addressCountry":"US"}
    ev={"@context":"https://schema.org","@type":"Event","@id":page_url(e)+"#event","name":name,
        "description":e["description"],"url":page_url(e),"image":[EV_IMG],
        "startDate":iso(e["startDate"],e["startTime"]) if e.get("startTime") else e["startDate"],
        "eventStatus":"https://schema.org/EventScheduled" if is_conf else "https://schema.org/EventScheduled",
        "eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode",
        "location":{"@type":"Place","name":loc,"address":addr},
        "organizer":{"@type":"Organization","name":org["name"],"url":org["url"]},
        "isAccessibleForFree":free,"keywords":[e.get("tag","Event"),"Niwot","Boulder County"],
        "sameAs":e["sourceUrl"]}
    if e.get("endTime"): ev["endDate"]=iso(last_date(e),e["endTime"])
    elif e.get("recurrence"): ev["endDate"]=last_date(e)
    if e.get("recurrence"):
        r=e["recurrence"]; DAY=["https://schema.org/Monday","https://schema.org/Tuesday","https://schema.org/Wednesday","https://schema.org/Thursday","https://schema.org/Friday","https://schema.org/Saturday","https://schema.org/Sunday"]
        ev["eventSchedule"]={"@type":"Schedule","repeatFrequency":"P1W","byDay":DAY[r["weekday"]-1],"startDate":e["startDate"],"endDate":r["until"],"startTime":e.get("startTime"),"endTime":e.get("endTime"),"scheduleTimezone":"America/Denver"}
    if free: ev["offers"]={"@type":"Offer","price":"0","priceCurrency":"USD","availability":"https://schema.org/InStock","url":page_url(e),"validFrom":e["verifiedAt"]}
    crumbs={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
        {"@type":"ListItem","position":2,"name":"Events","item":SITE+"/events/"},
        {"@type":"ListItem","position":3,"name":name,"item":page_url(e)}]}
    rows=[("Date",dl_)]
    if tl: rows.append(("Time",tl+", Mountain Time"))
    rows+= [("Location",loc+", Niwot, Colorado"),("Organizer",org["name"])]
    if e.get("cost"): rows.append(("Cost",e["cost"]))
    rows.append(("Status","Confirmed with the organizer" if is_conf else "Expected, not yet confirmed"))
    rows.append(("Checked",long_date(e["verifiedAt"])))
    dl="".join(f'<div style="padding:12px 0;border-top:1px solid var(--n-rule);display:grid;grid-template-columns:minmax(96px,.28fr) minmax(0,1fr);gap:8px 20px"><dt class="n-label n-label--quiet" style="font-size:12px">{esc(k)}</dt><dd class="n-body" style="margin:0;font-size:.9375rem">{esc(v)}</dd></div>' for k,v in rows)
    others=[o for o in upcoming if o["id"]!=e["id"]][:5]
    more="".join(f'<li style="padding:12px 0;border-top:1px solid var(--n-rule)"><a class="n-shift" href="/events/{o["id"]}/" style="color:var(--n-evergreen);font-size:1.0625rem;text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px">{esc(o["name"])}</a><div class="n-small" style="margin-top:4px;font-size:.875rem">{esc(date_label(o))}{(" &#183; "+esc(time_label(o))) if time_label(o) else ""} &#183; {esc(o["location"]["name"])}</div></li>' for o in others)
    past_note="" if d(last_date(e))>=TODAY else '<div class="n-callout n-callout--paper" style="margin-top:20px"><p class="n-body" style="margin:0;max-width:56ch">This event has already taken place. It stays on the site as a record of what happened, and for the organizer&#8217;s next date.</p></div>'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{ROBOTS}
<link rel="canonical" href="{page_url(e)}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="TownofNiwot.com">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{page_url(e)}">
<meta property="og:image" content="{EV_IMG}">
<meta property="og:image:width" content="1500">
<meta property="og:image:height" content="983">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:alt" content="{esc(EV_ALT)}">
<meta name="twitter:card" content="summary_large_image">

{head_common}
{ld(ev)}
{ld(crumbs)}
</head>
{header}<main id="main">
<section class="n-bg-white" aria-labelledby="title-h">
<div class="n-wrap" style="padding-top:clamp(8px,1vw,16px);padding-bottom:clamp(36px,5vw,72px)">
<nav class="n-crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/events/">Events</a></li><li aria-current="page">{esc(name)}</li></ol></nav>
<div class="n-g2-wide" style="align-items:start;margin-top:clamp(24px,3vw,44px)">
<div>
<div class="n-label">{esc(e.get("tag","Event"))} &#183; Niwot, Colorado</div>
<h1 class="n-display" id="title-h" style="margin-top:14px;font-size:clamp(2rem,1.5rem + 2.2vw,3.5rem);line-height:1.02;max-width:16ch;color:var(--n-evergreen)">{esc(name)}</h1>
<p class="n-lead" style="margin:clamp(16px,2vw,24px) 0 0;max-width:46ch">{esc(dl_)}{(" &#183; "+esc(tl)) if tl else ""}<br>{esc(loc)}</p>
<p class="n-body" style="margin:clamp(16px,2vw,24px) 0 0;max-width:58ch">{esc(e["description"])}</p>
{past_note}
<div class="n-btns" style="margin-top:clamp(24px,3vw,36px)">
<a class="n-btn" href="{esc(e["sourceUrl"])}" rel="noopener">Organizer&#8217;s page <span aria-hidden="true">&#8599;</span></a>
<a class="n-btn n-btn--ghost" href="{esc(deep_link(e))}">See it on the calendar</a>
</div>
</div>
<div>
<div class="n-shead"><span class="n-h3" style="font-size:clamp(1.125rem,1rem + .5vw,1.375rem)">Event details</span></div>
<dl style="margin:8px 0 0">{dl}</dl>
<p class="n-small" style="margin:16px 0 0;font-size:.8125rem;max-width:48ch">Details are checked against the organizer&#8217;s own page. If something here is wrong, <a href="/contact/">send a correction</a>.</p>
</div>
</div>
</div>
</section>
<section class="n-bg-paper n-pad-sm" aria-labelledby="more-h" style="border-top:1px solid var(--n-rule)">
<div class="n-wrap">
<div class="n-shead n-shead-row" style="border-bottom-color:var(--n-evergreen)"><h2 class="n-h2" id="more-h" style="font-size:clamp(1.375rem,1.1rem + 1vw,2rem);color:var(--n-evergreen)">More Niwot events</h2><a class="n-link" href="/events/">Full calendar <span aria-hidden="true">&#8594;</span></a></div>
<ul style="list-style:none;margin:8px 0 0;padding:0;max-width:60ch">{more}</ul>
</div>
</section>
</main>{footer}</body>
</html>
'''

gen=[]; touched=set()
for e in dated:
    if wr(f"events/{e['id']}/index.html",event_page(e)): touched.add(e["id"])
    gen.append(e["id"])
print("event pages:",len(gen),f"({len(touched)} changed)")

# ---------- 6. sitemap ----------
# lastmod was a literal date repeated on every line, so each run stamped the
# whole site with the day the line was written and overwrote anything newer.
# Git is the record of when a page actually changed; a page this run just
# rewrote is dated today, because it changed just now.
TODAYS=TODAY.isoformat()
def changed_on(path,rewritten=False):
    if rewritten: return TODAYS
    try:
        d=subprocess.run(["git","log","-1","--format=%cs","--",path],cwd=ROOT,
                         capture_output=True,text=True,timeout=10).stdout.strip()
        if d: return d
    except Exception: pass
    return TODAYS
pages=[(u,changed_on(f)) for u,f in [
    ("/","index.html"),("/explore/","explore/index.html"),
    ("/eat-shop/","eat-shop/index.html"),("/events/","events/index.html"),
    ("/community/","community/index.html"),
    ("/civic/incorporation-election/","civic/incorporation-election/index.html"),
    ("/plan-a-visit/","plan-a-visit/index.html"),
    ("/our-story/","our-story/index.html"),("/privacy/","privacy/index.html")]]
pages+=[(f"/events/{e['id']}/",
         changed_on(f"events/{e['id']}/index.html",e["id"] in touched))
        for e in sorted(dated,key=lambda e:e["startDate"])]
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{m}</lastmod>\n  </url>\n" for p,m in pages)+"</urlset>\n"
wr("sitemap.xml",sm)

print("sitemap:",len(pages),"urls")
