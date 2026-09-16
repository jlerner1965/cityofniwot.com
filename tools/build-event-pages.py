#!/usr/bin/env python3
"""Rebuild everything on the site that is derived from the event records.

Source of truth is data/events.json. Run from anywhere after editing it:

    python3 tools/build-event-pages.py

It writes the records into the homepage and the calendar page (the
<script id="niwot-events"> block each carries), pre-renders the upcoming
cards, the current month's grid and detail rail, the expected list, one page
per dated event under /events/<id>/, the calendar's ItemList and index of
event pages, and sitemap.xml. Tentative records without a date get no page.
The header and footer are copied from 404/index.html so they always match
the rest of the site.

Keys beginning with an underscore (`_notes`) are editorial and are stripped
before anything is published.

Pre-rendering goes through tools/render-calendar.mjs, which imports the same
calendar-core.js the browser runs, so the static page and the hydrated page
cannot disagree. Node is required for that step; without it the cards are
rendered by the Python fallback below and the month grid is left as it was.
"""
import re, json, html, glob, os, subprocess, sys, datetime as dt
from zoneinfo import ZoneInfo
# Derived, not hardcoded: this has to run on a build machine too.
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
SITE="https://townofniwot.com"; TZ=ZoneInfo("America/Denver"); TODAY=dt.datetime.now(TZ).date()
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
CHECK="--check" in sys.argv      # read-only: verify(), then exit
def wr(f,s):
    """Write f, and say whether that changed anything."""
    if CHECK: return False       # --check never touches the working tree
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
def public(rec):
    """The record as published: editorial keys (leading underscore) removed."""
    return {k:v for k,v in rec.items() if not k.startswith("_")}
events=[public(e) for e in json.load(open("data/events.json",encoding="utf-8"))]
ids=[e["id"] for e in events]
assert len(ids)==len(set(ids)),"duplicate event id in data/events.json"
for e in events:
    assert e.get("status") in ("confirmed","cancelled","postponed","tentative"),e["id"]
    if e["status"]!="tentative": assert e.get("startDate"),e["id"]+" needs a startDate"
    assert e.get("sourceUrl") and e.get("verifiedAt") and e.get("organizer",{}).get("name"),e["id"]+" needs sourceUrl, verifiedAt, organizer"

# ---------- 1b. --check: is the committed output still true to the data? ----------
# check-assets.yml already refuses a directory page that has drifted from
# data/directory.json. The event pages had no such guard: edit a record,
# forget the builder, and the pages merge saying the old thing. The daily job
# then corrects them by pushing to main, which is a fix arriving after the
# wrong page has been served, not a check.
#
# What cannot be compared is the part that moves on its own. The upcoming
# cards, the month grid, each page's deep link into the calendar and the
# sitemap's dates are all rendered as of today, so a byte comparison would
# fail every morning and teach everyone to ignore it. What does not move is
# the shape: which records have pages, and whether each page still says what
# its record says. That is what drifts when someone forgets the builder, and
# that is what this checks.
def verify():
    bad=[]
    def note(where,msg): bad.append((where,msg))
    dated_ids={e["id"] for e in events if e.get("startDate")}
    on_disk={os.path.basename(os.path.dirname(f))
             for f in glob.glob("events/*/index.html")}
    for eid in sorted(dated_ids-on_disk):
        note("data/events.json",f"{eid} has no page at events/{eid}/ — run the builder")
    redirects={r.get("source") for r in json.load(open("vercel.json")).get("redirects",[])}
    for eid in sorted(on_disk-dated_ids):
        note(f"events/{eid}/index.html","page has no record; the builder would remove it"
             +("" if f"/events/{eid}/" in redirects else " and vercel.json has no redirect for it"))

    sitemap=rd("sitemap.xml") if os.path.exists("sitemap.xml") else ""
    index_page=rd("events/index.html")
    for eid in sorted(dated_ids & on_disk):
        e=byid[eid]; f=f"events/{eid}/index.html"; page=rd(f)
        ev=None
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',page,re.S):
            try: obj=json.loads(raw)
            except ValueError: continue
            for n in (obj.get("@graph",[obj]) if isinstance(obj,dict) else obj):
                if isinstance(n,dict) and n.get("@type")=="Event": ev=n
        if ev is None:
            note(f,"no Event structured data"); continue
        # The record is the source; the page is a copy of it. Every field
        # here is one a person edits in events.json and would expect to see
        # on the page the same day.
        want_status="https://schema.org/Event"+{"confirmed":"Scheduled","cancelled":"Cancelled",
                                                "postponed":"Postponed"}.get(e["status"],"Scheduled")
        for label,got,expected in (
            ("name",ev.get("name"),e["name"]),
            ("startDate",(ev.get("startDate") or "")[:10],e["startDate"]),
            ("eventStatus",ev.get("eventStatus"),want_status),
            ("location",(ev.get("location") or {}).get("name"),e["location"]["name"]),
            ("organizer",(ev.get("organizer") or {}).get("name"),e["organizer"]["name"]),
        ):
            if got!=expected:
                note(f,f"{label} is {got!r}; data/events.json says {expected!r}")
        if f'<link rel="canonical" href="{page_url(e)}">' not in page:
            note(f,f"canonical is not {page_url(e)}")
        if f"<loc>{page_url(e)}</loc>" not in sitemap:
            note("sitemap.xml",f"does not list {page_url(e)}")
        if f'<a href="/events/{eid}/">' not in index_page:
            note("events/index.html",f"the Event pages index does not link /events/{eid}/")

    published=json.dumps(events,ensure_ascii=False,separators=(",",":"))
    for path in ("index.html","events/index.html"):
        m=re.search(r'<script type="application/json" id="niwot-events"[^>]*>(.*?)</script>',
                    rd(path),re.S)
        if not m: note(path,"no niwot-events block")
        elif m.group(1)!=published:
            note(path,"the embedded records differ from data/events.json — run the builder")

    if bad:
        print(f"{len(bad)} thing(s) no longer match data/events.json:\n")
        for where,msg in bad: print(f"  {where}\n      {msg}")
        print("\nRun: python3 tools/build-event-pages.py")
        return 1
    print(f"{len(dated_ids)} event pages, the calendar index, the embedded records "
          f"and the sitemap all match data/events.json")
    return 0

EMBED_TZ=ZoneInfo("America/Denver")
EMBED='<script type="application/json" id="niwot-events" data-built="%s">%s</script>'%(
    dt.datetime.now(EMBED_TZ).strftime("%Y-%m-%d %H:%M"),json.dumps(events,ensure_ascii=False,separators=(",",":")))
rebuilt=set()
for path in ("index.html","events/index.html"):
    t=rd(path)
    t2,n=re.subn(r'<script type="application/json" id="niwot-events"[^>]*>.*?</script>',lambda m:EMBED,t,count=1,flags=re.S)
    assert n==1,path+": no niwot-events block"
    # Only the records matter: a rebuild that changes nothing but the
    # data-built stamp would commit noise every day.
    if re.sub(r' data-built="[^"]*"','',t2)!=re.sub(r' data-built="[^"]*"','',t):
        wr(path,t2); rebuilt.add(path)
if not CHECK: print("event records:",len(events),"embedded"+(" (changed)" if rebuilt else ""))
def postal(e):
    """The record's address as schema.org wants it. A venue with no street
    address gets the locality alone — which is true — rather than nothing."""
    a={"@type":"PostalAddress"}
    street=(e.get("location") or {}).get("address")
    if street: a["streetAddress"]=street
    a.update({"addressLocality":"Niwot","addressRegion":"CO","addressCountry":"US"})
    return a
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
if CHECK: sys.exit(verify())

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
header=re.search(r'(<body>.*?)<main id="main"[^>]*>',p404,re.S).group(1)
footer=re.search(r'</main>(.*?)</body>',p404,re.S).group(1)
footer=footer.replace('<span>Reviewed September 2026</span>','<span>Reviewed September 2026</span>')
head_common=re.search(r'(<link rel="icon".*?<script src="/assets/js/guide[^>]*></script>)',p404,re.S).group(1)
EV_IMG=SITE+"/assets/photos/whistle-stop-caboose.jpg"
EV_ALT="The red CB&Q caboose at Whistle Stop Park in Niwot, home of the summer concert series"

dated=[e for e in events if e.get("startDate")]
upcoming=sorted([e for e in dated if d(last_date(e))>=TODAY],key=lambda e:e["startDate"])

def status_row(e):
    """What we can honestly say we know. A record that names the organizer's
    listing but no start time was located, not confirmed — and a page that
    claims both is the thing this row exists to prevent."""
    if e["status"]=="cancelled": return "Cancelled by the organizer"
    if e["status"]=="postponed": return "Postponed \u2014 new date not yet published"
    if e["status"]!="confirmed": return "Expected, not yet confirmed"
    if not e.get("startTime"): return "Source listing located \u2014 details incomplete"
    return "Confirmed with the organizer"

def event_page(e):
    name=e["name"]; loc=e["location"]["name"]; org=e["organizer"]; tl=time_label(e); dl_=date_label(e)
    is_conf=e["status"]=="confirmed"
    title=f"{name} — {short_date(e['startDate'])} | Niwot Events"
    if e.get("recurrence"): title=f"{name} {d(e['startDate']).year} | Niwot Events"
    if len(title)>65: title=f"{name} | Niwot, CO Events"
    if e["status"]=="cancelled": title="Cancelled: "+title
    desc=trim(f"{name} in Niwot, Colorado: {dl_}{', '+tl if tl else ''}, at {loc}. {e['description']}")
    free=bool(e.get("cost")) and e["cost"].lower().startswith("free")
    addr=postal(e)
    ev={"@context":"https://schema.org","@type":"Event","@id":page_url(e)+"#event","name":name,
        "description":e["description"],"url":page_url(e),"image":[EV_IMG],
        "startDate":iso(e["startDate"],e["startTime"]) if e.get("startTime") else e["startDate"],
        "eventStatus":{"confirmed":"https://schema.org/EventScheduled","cancelled":"https://schema.org/EventCancelled",
                       "postponed":"https://schema.org/EventPostponed"}.get(e["status"],"https://schema.org/EventScheduled"),
        "eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode",
        "location":{"@type":"Place","name":loc,"address":addr},
        "organizer":{"@type":"Organization","name":org["name"],"url":org["url"]},
        "keywords":[e.get("tag","Event"),"Niwot","Boulder County"],
        "sameAs":e["sourceUrl"]}
    if e.get("cost"): ev["isAccessibleForFree"]=free
    if e.get("registrationUrl"): ev["url"]=page_url(e); ev.setdefault("offers",{"@type":"Offer","url":e["registrationUrl"]})
    if e.get("accessibility"): ev["accessibilitySummary"]=e["accessibility"]
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
    if e.get("accessibility"): rows.append(("Access",e["accessibility"]))
    rows.append(("Status",status_row(e)))
    rows.append(("Checked",long_date(e["verifiedAt"])))
    dl="".join(f'<div style="padding:12px 0;border-top:1px solid var(--n-rule);display:grid;grid-template-columns:minmax(96px,.28fr) minmax(0,1fr);gap:8px 20px"><dt class="n-label n-label--quiet" style="font-size:12px">{esc(k)}</dt><dd class="n-body" style="margin:0;font-size:.9375rem">{esc(v)}</dd></div>' for k,v in rows)
    others=[o for o in upcoming if o["id"]!=e["id"]][:5]
    more="".join(f'<li style="padding:12px 0;border-top:1px solid var(--n-rule)"><a class="n-shift" href="/events/{o["id"]}/" style="color:var(--n-evergreen);font-size:1.0625rem;text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px">{esc(o["name"])}</a><div class="n-small" style="margin-top:4px;font-size:.875rem">{esc(date_label(o))}{(" &#183; "+esc(time_label(o))) if time_label(o) else ""} &#183; {esc(o["location"]["name"])}</div></li>' for o in others)
    past_note=""
    if e["status"] in ("cancelled","postponed"):
        past_note='<div class="n-callout n-callout--paper" style="margin-top:20px"><div class="n-label">'+("Cancelled" if e["status"]=="cancelled" else "Postponed")+'</div><p class="n-body" style="margin:8px 0 0;max-width:56ch">'+esc(e.get("statusNote") or ("The organizer has cancelled this event." if e["status"]=="cancelled" else "The organizer has postponed this event and has not yet published a new date."))+' Check the organizer&#8217;s page for the latest.</p></div>'
    elif d(last_date(e))<TODAY:
        past_note='<div class="n-callout n-callout--paper" style="margin-top:20px"><div class="n-label">Past event</div><p class="n-body" style="margin:8px 0 0;max-width:56ch">This event has already taken place. It stays on the site as a record of what happened, and for the organizer&#8217;s next date.</p></div>'
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
{header}<main id="main" tabindex="-1">
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
<a class="n-btn" href="{esc(e["sourceUrl"])}" rel="noopener" data-track="event_source_click">Organizer&#8217;s page <span aria-hidden="true">&#8599;</span></a>
{('<a class="n-btn" href="'+esc(e["registrationUrl"])+'" rel="noopener" data-track="event_registration_click">Register or buy tickets <span aria-hidden="true">&#8599;</span></a>') if e.get("registrationUrl") else ''}
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

# ---------- 5b. the pre-rendered "coming up" cards ----------
# The browser rebuilds these from the same JSON on load, so anyone with
# scripting sees a current list whatever the file says. Crawlers and everyone
# else read the file — and that copy goes stale by itself as events pass,
# which is how a finished event stays sitting on the homepage. Rendering it
# here, from the same records, is what archives it. The markup below is the
# markup renderUpcoming() emits in calendar-core.js; when one moves, the other
# has to move with it, or the page will flicker as it hydrates.
NOW_AT=dt.datetime.now(TZ)
NOW={"date":NOW_AT.date().isoformat(),"time":NOW_AT.strftime("%H:%M")}
DATED_STATUSES=("confirmed","cancelled","postponed")
STATUS_LABEL={"confirmed":"Confirmed","cancelled":"Cancelled",
              "postponed":"Postponed","tentative":"Expected — date not confirmed"}

def jesc(v):
    """escapeHtml() from calendar-core.js, character for character."""
    return (str("" if v is None else v).replace("&","&amp;").replace("<","&lt;")
            .replace(">","&gt;").replace('"',"&quot;"))

def instances(evs):
    """Every dated occurrence, soonest first — expandEvents() in Python."""
    out=[]
    for e in evs:
        if not e.get("startDate") or e.get("status") not in DATED_STATUSES: continue
        if e.get("recurrence"):
            r=e["recurrence"]; x=until=d(e["startDate"]); until=d(r["until"]); dates=[]
            while x<=until:
                # calendar-core counts Sunday as 0, as Date#getDay() does;
                # Python counts Monday as 0.
                if (x.weekday()+1)%7==r["weekday"]: dates.append(x.isoformat())
                x+=dt.timedelta(days=1)
        else:
            dates=[e["startDate"]]
        for date in dates:
            out.append({"id":e["id"],"date":date,
                        "endDate":date if e.get("recurrence") else (e.get("endDate") or date),
                        "startTime":e.get("startTime"),"endTime":e.get("endTime"),"event":e})
    out.sort(key=lambda i:(i["date"],i["startTime"] or "00:00",i["event"]["name"]))
    return out

def is_past(i):
    end_date=i["endDate"] or i["date"]; end_time=i["endTime"] or "24:00"
    if end_date!=NOW["date"]: return end_date<NOW["date"]
    return end_time<=NOW["time"]

def day_label(iso):
    # dayLabel() in calendar-core.js abbreviates the weekday ("Fri, September
    # 11"). The browser re-renders these cards from the same records on load,
    # so spelling it out here would make the card change under the reader
    # between the served HTML and the hydrated page.
    x=d(iso); base=f"{WD[x.weekday()][:3]}, {x.strftime('%B')} {x.day}"
    return base if x.year==d(NOW["date"]).year else f"{base}, {x.year}"

def inst_time(i):
    if not i["startTime"]: return ""
    s=fmt_time(i["startTime"])
    if not i["endTime"]: return s
    en=fmt_time(i["endTime"])
    return (s[:-3]+"–"+en) if s[-2:]==en[-2:] else (s+"–"+en)

def card(i,mode):
    e=i["event"]; t=inst_time(i)
    when=day_label(i["date"])
    if i["endDate"] and i["endDate"]!=i["date"]: when+=" to "+day_label(i["endDate"])
    if mode=="select":
        action=('<button type="button" class="n-jump" data-jump="'+i["date"]
                +'" data-jump-event="'+jesc(i["id"])+'"'
                ' style="margin-top:auto;align-self:start;background:none;border:0;'
                'border-bottom:1px solid currentColor;color:var(--n-sky-ink);font:inherit;'
                'font-size:.9375rem;font-weight:500;cursor:pointer">'
                'View details <span aria-hidden="true">&#8594;</span></button>')
    else:
        action=('<a class="n-link" href="'+jesc(f'/events/?date={i["date"]}&event={i["id"]}#cal-h')
                +'" style="margin-top:auto;align-self:start">'
                'View details <span aria-hidden="true">&#8594;</span></a>')
    return ('<article data-event-id="'+jesc(i["id"])+'" data-event-date="'+i["date"]
            +'" data-event-status="'+jesc(e["status"])+'" class="n-up">'
            '<div class="n-label">'+jesc(when)+((' &#183; '+jesc(t)) if t else '')+'</div>'
            '<h3 class="n-h3" style="font-size:1.375rem;color:var(--n-evergreen)">'
            '<a href="/events/'+e["id"]+'/" style="color:inherit;text-decoration:none">'
            +jesc(e["name"])+'</a></h3>'
            +(('<div class="n-label">'+jesc(STATUS_LABEL.get(e["status"],e["status"]))+'</div>')
              if e["status"]!="confirmed" else "")
            +'<div class="n-body" style="font-size:.9375rem">'+jesc(e["location"]["name"])+'</div>'
            '<div class="n-small" style="font-size:.875rem">'+jesc(e["organizer"]["name"])
            +((' &#183; '+jesc(e["cost"])) if e.get("cost") else "")+'</div>'
            +action+'</article>')

def empty_note(mode):
    where=('The expected seasonal events are listed below' if mode=="select"
           else 'The expected seasonal events are listed on the '
                '<a href="/events/#expected">events calendar</a>')
    return ('<p class="n-body" data-upcoming-empty style="margin:0;max-width:56ch">'
            'Nothing is confirmed on the calendar right now. '+where+', and the '
            'organizers’ own pages carry anything announced since this page '
            'was checked.</p>')

def replace_inner(t,attr):
    """The content of the one <div> carrying `attr`, found by balancing."""
    m=re.search(r'<div[^>]*'+re.escape(attr)+r'[^>]*>',t)
    if not m: return None,None,None
    start=m.end(); depth=1
    for tok in re.finditer(r'<(/?)div\b',t[start:]):
        depth+=-1 if tok.group(1) else 1
        if depth==0: return t[:start],t[start:start+tok.start()],t[start+tok.start():]
    return None,None,None

live=[i for i in instances(events) if not is_past(i)]
def node_render():
    """The browser's own rendering of every calendar surface, or None."""
    try:
        r=subprocess.run(["node","tools/render-calendar.mjs"],cwd=ROOT,input=json.dumps(events),
                         capture_output=True,text=True,timeout=60)
    except (OSError,subprocess.SubprocessError) as ex:
        print("! node render unavailable:",ex); return None
    if r.returncode!=0:
        print("! node render failed:",r.stderr.strip()[:400]); return None
    return json.loads(r.stdout)
rendered=node_render()
def swap_inner(path,attr,body):
    t=rd(path); head,_,tail=replace_inner(t,attr)
    if head is None: print(f"! {path}: no {attr} container"); return
    if wr(path,head+body+tail): rebuilt.add(path)
if rendered:
    swap_inner("index.html",'data-upcoming="link"',rendered["homeCards"])
    swap_inner("events/index.html",'data-upcoming="select"',rendered["upcomingList"])
    swap_inner("events/index.html",'data-cal-grid',rendered["grid"])
    swap_inner("events/index.html",'data-cal-detail',rendered["detail"])
    t=rd("events/index.html")
    t=re.sub(r'(<span class="n-label n-label--quiet" data-cal-label aria-live="polite">)[^<]*(</span>)',
             lambda m:m.group(1)+esc(rendered["monthLabel"])+m.group(2),t,count=1)
    t=re.sub(r'(<ul class="n-expected" data-expected>).*?(</ul>)',lambda m:m.group(1)+rendered["expected"]+m.group(2),t,count=1,flags=re.S)
    t=re.sub(r'(<h2 class="n-h3" id="exp-h"[^>]*>Annual events still waiting on a date</h2>)',lambda m:m.group(1),t)
    t=re.sub(r'(id="exp-h".*?<span class="n-label n-label--quiet">)\d+(</span>)',lambda m:m.group(1)+str(rendered["expectedCount"])+m.group(2),t,count=1,flags=re.S)
    if wr("events/index.html",t): rebuilt.add("events/index.html")
    print(f"pre-rendered via node as of {rendered['now']['date']} {rendered['now']['time']} Niwot time: "
          f"{len(rendered['upcomingIds'])} upcoming, month {rendered['monthLabel']}")
else:
    for path,mode,limit in (("index.html","link",3),("events/index.html","select",None)):
        shown=live[:limit] if limit else live
        swap_inner(path,'data-upcoming="%s"'%mode,"".join(card(i,mode) for i in shown) or empty_note(mode))
        print(f"{path}: {len(shown)} cards (python fallback)")

# ---------- 5c. the calendar page's canonical event-page index ----------
# This server-rendered list is the non-scripted path to every canonical event
# page. Rebuild it with the feed so renamed or split records cannot leave a
# dead link behind after the stale page itself is removed.
event_links="".join(
    f'<li><a href="/events/{e["id"]}/">{esc(e["name"])}</a> '
    f'<span class="n-small">({esc(short_date(e["startDate"]))})</span></li>'
    for e in sorted(dated,key=lambda e:e["startDate"]))
page_index=(
    '<section class="n-bg-white n-pad-sm" aria-labelledby="pages-h" '
    'style="border-top:1px solid var(--n-rule)"><div class="n-wrap">'
    '<h2 class="n-label n-label--quiet" id="pages-h" style="margin:0 0 12px">Event pages</h2>'
    '<ul class="n-body" style="columns:2;column-gap:32px;margin:0;padding-left:1.2em;'
    'font-size:.9375rem;max-width:72ch">'+event_links+'</ul></div></section>')
t=rd("events/index.html")
t,n=re.subn(r'<section class="n-bg-white n-pad-sm" aria-labelledby="pages-h".*?</section>',
            page_index,t,count=1,flags=re.S)
if n and wr("events/index.html",t): rebuilt.add("events/index.html")
print(f"events/index.html: {len(dated)} canonical event links")

# ---------- 5d. the calendar page's structured data ----------
# It used to carry an Event object per listing. Google puts the event
# experience on single-event pages, and fourteen Events on one URL competes
# with the fourteen pages that each describe one properly. An ItemList says
# what this page actually is: an index pointing at them.
# In the order the page shows them — by next occurrence, not by the date a
# series first ran — so the list and the cards cannot disagree.
listed=[]
for i in live:
    if i["event"] not in listed: listed.append(i["event"])
itemlist={"@context":"https://schema.org","@type":"ItemList",
          "name":"Upcoming events in Niwot, Colorado",
          "itemListOrder":"https://schema.org/ItemListOrderAscending",
          "numberOfItems":len(listed),
          "itemListElement":[{"@type":"ListItem","position":n,"url":page_url(e),"name":e["name"]}
                             for n,e in enumerate(listed,1)]}
t=rd("events/index.html")
blocks=list(re.finditer(r'<script type="application/ld\+json">(.*?)</script>',t,re.S))
def is_the_list(raw):
    """The block this page's index lives in — an ItemList once this has run
    before, an Event graph the first time. Matching both keeps the rebuild
    idempotent; matching only Events made the second run a no-op."""
    try: obj=json.loads(raw)
    except ValueError: return False
    if not isinstance(obj,dict): return False
    if obj.get("@type")=="ItemList": return True
    return any(isinstance(x,dict) and x.get("@type")=="Event"
               for x in obj.get("@graph",[]))
first=next((b for b in blocks if is_the_list(b.group(1))), None)
if first:
    t=t[:first.start()]+ld(itemlist)+t[first.end():]
    if wr("events/index.html",t): rebuilt.add("events/index.html")
    print(f"events/index.html: Event graph -> ItemList of {len(listed)}")

# ---------- 5e. pages for events that no longer exist ----------
# Splitting or renaming a record leaves its old page behind, live and
# indexable, describing an event this site no longer lists.
keep={e["id"] for e in dated}
for f in sorted(glob.glob("events/*/index.html")):
    eid=os.path.basename(os.path.dirname(f))
    if eid in keep: continue
    os.remove(f); os.rmdir(os.path.dirname(f))
    has_redirect=any(r.get("source")==f"/events/{eid}/" for r in json.load(open("vercel.json")).get("redirects",[]))
    print("removed stale page:",eid,"" if has_redirect else "(no redirect in vercel.json — add one)")

# ---------- 6. sitemap ----------
# lastmod was a literal date repeated on every line, so each run stamped the
# whole site with the day the line was written and overwrote anything newer.
# Git is the record of when a page actually changed; a page this run just
# rewrote is dated today, because it changed just now.
TODAYS=TODAY.isoformat()
def git(*a):
    try:
        return subprocess.run(["git",*a],cwd=ROOT,capture_output=True,
                              text=True,timeout=10).stdout.strip()
    except Exception:
        return ""
# A build machine clones one commit deep, so git there cannot say when a page
# last changed — every file would look like it changed on the deploy. Where
# the date cannot be recomputed, the one already in the sitemap is kept.
SHALLOW = git("rev-parse","--is-shallow-repository")=="true"
PREV = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>",
                       open("sitemap.xml",encoding="utf-8").read())) \
       if os.path.exists("sitemap.xml") else {}
def changed_on(url,path,rewritten=False):
    if rewritten or git("status","--porcelain","--",path): return TODAYS
    if not SHALLOW:
        stamp=git("log","-1","--format=%cI","--",path)
        if stamp:
            try:
                return dt.datetime.fromisoformat(stamp).astimezone(TZ).date().isoformat()
            except ValueError:
                pass
    return PREV.get(SITE+url, TODAYS)
pages=[(u,changed_on(u,f,f in rebuilt)) for u,f in [
    ("/","index.html"),("/explore/","explore/index.html"),
    ("/eat-shop/","eat-shop/index.html"),("/events/","events/index.html"),
    ("/community/","community/index.html"),
    ("/civic/","civic/index.html"),
    ("/civic/incorporation-election/","civic/incorporation-election/index.html"),
    ("/plan-a-visit/","plan-a-visit/index.html"),
    ("/our-story/","our-story/index.html"),("/contact/","contact/index.html"),
    ("/privacy/","privacy/index.html")]]
pages+=[(f"/events/{e['id']}/",
         changed_on(f"/events/{e['id']}/",f"events/{e['id']}/index.html",
                    e["id"] in touched))
        for e in sorted(dated,key=lambda e:e["startDate"])]
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{m}</lastmod>\n  </url>\n" for p,m in pages)+"</urlset>\n"
wr("sitemap.xml",sm)

print("sitemap:",len(pages),"urls")
