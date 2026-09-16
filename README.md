# TownofNiwot.com

Static site for the Niwot, Colorado community guide. This repository holds the
built site exactly as it should be served: plain HTML, CSS, JavaScript and
images, with no build step.

Built from the page mockups at
`https://townofniwot-page-mockups.jlerner1965.chatgpt.site`.

## Pages

| Path | Page |
| --- | --- |
| `/` | Home |
| `/explore/` | Things to do |
| `/eat-shop/` | Restaurants, shops and local services directory |
| `/events/` | Events calendar |
| `/community/` | Community organizations and resident resources |
| `/civic/` | Civic information hub: Niwot's civic status and the election pages |
| `/civic/incorporation-election/` | 2026 incorporation election |
| `/plan-a-visit/` | Directions, parking and accessibility |
| `/our-story/` | History of Niwot |
| `/contact/` | Send a listing, event or correction |
| `/privacy/` | Privacy |
| `/events/<event-id>/` | One page per calendar event, generated from `data/events.json` |
| `/404/` and `404.html` | Not-found page |

## Navigation

Every page carries the same primary navigation, in this order:

| Position | Page | Shown in the bar |
| --- | --- | --- |
| 1 | Explore | yes |
| 2 | Eat & Shop | yes |
| 3 | Events | yes |
| 4 | Plan a Visit | yes |
| 5 | Community | yes |
| 6 | Our Story | yes |
| 7 | Civic Information (`/civic/`) | yes |
| action | Submit a listing (`/contact/`) | yes, as a small outlined button |

Above 1180px the bar shows all of it; between 1180px and 1300px the
"Independent community guide" identifier beside the wordmark is hidden to
make the room (it is repeated in the footer). At 1180px and below the bar
collapses to the menu button, which lists the seven pages with the action
last, set a tier back behind a rule. The rules that carry this are
`.n-nav-cta` and the `@media (max-width: 1180px)` block in
`assets/css/guide.<hash>.css`; the same width is repeated in the `<noscript>`
block in each page's header, which opens the list statically where scripting
is off.

The page's own entry carries `class="n-on"` and `aria-current="page"`. Adding a
page to the navigation means editing the `<nav class="n-nav">` block in every
HTML file — there is no template — and marking the current entry on its own
page. `tools/build-event-pages.py` copies the header from `404/index.html`
into every event page, so that file is the one to get right first.

The 1180px collapse width belongs to the navigation alone. The touch-padding
media queries in the same stylesheet are still at 1080px; they are a different
measurement and do not move with it.

## Layout

- `assets/css/` and `assets/js/` hold the shared stylesheet and scripts. File
  names carry a content hash, so renaming one means updating the pages that
  reference it.
- `img/` holds responsive image sets in AVIF, WebP and JPEG at several widths.
- `assets/photos/` holds the full-size JPEGs used for social sharing previews (`og:image`).
- `vercel.json` enforces trailing-slash URLs, sets cache headers for images and assets, and adds basic security headers.
- `favicon.ico`, `favicon.svg` and `apple-touch-icon.png` are the site icons.
- `robots.txt`, `sitemap.xml` and `llms.txt` are ready for the production domain.
- `assets/fonts/` holds the two typefaces (Instrument Serif and Instrument
  Sans, SIL Open Font License), served from here rather than from Google.
- `vercel.json` also sends a Content-Security-Policy and, on any host other
  than `townofniwot.com`, `X-Robots-Tag: noindex, nofollow`, so preview
  deployments are never indexed.
- `docs/` holds the editorial documents: the election transition plan, the
  image-rights inventory, the analytics event map, the maintenance schedule
  and the launch checklist.

## Serving locally

Any static file server works. For example:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/`. Pages live in folders with an
`index.html`, so links like `/events/` resolve on any host that serves
directory indexes (GitHub Pages, Netlify, Vercel, Cloudflare Pages, nginx).

## Contact form

The form on `/contact/` posts to Formspree (`https://formspree.io/f/xqpkjoob`),
which emails each submission to the editor. With JavaScript, the outcome is
shown in place; without it, Formspree redirects to `/thanks/`. Spam is filtered
by the hidden `_gotcha` field. The form collects the kind of submission, the
page it is about, the details, a source link (required for events and every
correction kind) and an optional email; it says that nothing is published
without review. Nothing on the site is a newsletter signup, and the privacy
page says so. Delivery was last confirmed with a controlled submission on
September 16, 2026. To change the destination mailbox or the
endpoint, edit the form in the Formspree dashboard or update the `action`
attribute on the form.

## Logo

`assets/logo/` holds the wordmark: NIWOT set on the rail device, with COLORADO
beneath.

| File | Use |
| --- | --- |
| `niwot-logo.svg` | Primary. Dark type, transparent ground — soft white or paper |
| `niwot-logo-reversed.svg` | Evergreen and other dark grounds. The rail turns gold, the same swap the homepage hero makes |
| `niwot-logo-1024.png` | Raster, transparent, 1024px wide |
| `niwot-logo-reversed-1024.png` | Raster on evergreen, 1024px wide |

The type is **converted to outlines**, not set as `<text>`: the files carry no
`font-family` and need no font installed, so the mark cannot land on a
substitute serif in someone else's document or print shop. That also means the
wording cannot be edited by retyping it — a change means regenerating from
Instrument Serif and Instrument Sans.

Do not place it below **155px wide**. COLORADO is the smallest thing in the
lockup and its capitals are 10.4 units in a 320.4-unit artboard, which works
out at 5px tall at 155px wide — about the floor for readable uppercase on
screen. In print, where 4px of cap height still holds, it goes to about 125px.
Below that use the favicon tile.

The lockup does not say "independent community guide". It did, and the line
was dropped because it was unreadable at any size the mark is actually used —
2px of cap height at 96px wide. On the site that costs nothing, since the
masthead and the footer disclaimer both say it. Somewhere the mark travels
alone, "NIWOT COLORADO" reads closer to a municipal seal than this site is,
which is worth a thought before putting it on anything civic.

The site header does not use these files. It sets the same wordmark as live
text, which scales, stays selectable and reads to a screen reader — better than
an image for that job. These are for everywhere the site is not: social
profiles, print, partner listings.

## Outbound links

The site links out to about a hundred addresses across some fifty hosts — business sites, organizer
pages, Boulder County services. A directory is only as good as its links and
they rot quietly, so check them:

```sh
python3 tools/check-links.py
python3 tools/check-links.py --json report.json
```

It reads every `href` in the HTML, so nothing has to be listed twice, and
reports each one as OK, REDIRECT, BLOCKED or BROKEN. A host that refuses HEAD
is retried with GET, and 403 or 429 is reported as BLOCKED rather than broken —
several small business hosts turn away anything that looks automated, and that
is not the same as a dead link. Exit status is 1 if anything is BROKEN, so it
can gate a deploy.

A host that answers is believed at once. A connection that dies before any
answer — a reset, a timeout, a DNS or TLS failure — is tried twice more, a few
seconds apart, because that failure can belong to the network the check is
running on rather than to the site: four listings once reported BROKEN from an
audit sandbox were all live, and three of them answered on the second attempt.
`--tries 1` turns the retries off for a quick local pass.

Worth running monthly, and after any batch of listing edits. It checks that a
page answers, not that it still says what the listing claims — that part is an
editorial check and needs a person.

## Content with an expiry date

Some sentences are only true until a date: an election described as upcoming,
a promise to re-check something after a review. Nothing edits them when that
date passes, and on a civic page a stale tense is worse than a stale link — it
tells a resident a vote is still coming when it has already happened.

```sh
python3 tools/check-dated-content.py
```

A weekly job runs it and opens an issue when something has expired, updating
that one issue rather than filing a new one each week. It is silent while
everything is current.

Each check is a date, a file and a phrase that should be gone by then, listed
at the top of the script. A check goes quiet on its own once the wording
changes — there is no list to remember to tick off. The exception is the
ballot-language note on the election page, which is silenced by a note
containing the words `Ballot language re-checked on <date>`; the check says so
when it fires.

To add a claim that expires, append an entry to `CHECKS`.

## Data files

The site's time-sensitive content lives in `data/`, not in the pages:

| File | What | Rebuild with |
| --- | --- | --- |
| `data/events.json` | Every event record (see the field list below) | `python3 tools/build-event-pages.py` |
| `data/directory.json` | Every business listing, with `status`, `hidden`, `sourceType`, `verifiedAt`, `nextReview` | `python3 tools/build-directory.py` |
| `data/source-registry.json` | The claim-by-claim register of sources behind time-sensitive and historical statements, each with `lastChecked` and `nextReview` | — (read by `tools/check-review-dates.py`) |

Keys beginning with an underscore (`_notes`) are editorial and are stripped
before anything is published. `python3 tools/check-review-dates.py --days 14`
lists what is due for a re-check; the weekly job includes it in its issue.

Event record fields: `id`, `name`, `status` (`confirmed`, `cancelled`,
`postponed`, `tentative`), `startDate`, `startTime`, `endDate`, `endTime`,
`timezone` (always `America/Denver`), `recurrence` (`weekday` with Sunday = 0,
and `until`: only dates actually read on the organizer's page), `location`
(`name`, `address`), `organizer` (`name`, `url`), `sourceUrl`, `verifiedAt`,
`cost`, `registrationUrl`, `accessibility`, `statusNote` (shown for cancelled
or postponed), `tag`, `description`, `expected` (tentative records),
`nextReview`, `_notes`.

## Event pages and SEO

Each event on the calendar also has its own page at `/events/<event-id>/`,
with Event structured data pointing at this site, an organizer link, and
links to related events. `tools/build-event-pages.py` reads
`data/events.json`, embeds it in the homepage and the calendar page, and
pre-renders the upcoming cards, the current month's grid and detail rail and
the expected list through `tools/render-calendar.mjs`, which imports the
same `calendar-core.js` the browser runs, so the static page and the
hydrated page cannot disagree. It also writes the event pages, the
calendar's ItemList and index of event pages, and the sitemap. A daily job
runs it. Node is required for the pre-render; without it the cards fall back
to a Python rendering and the month grid is left alone.

```sh
python3 tools/build-event-pages.py
python3 tools/build-event-pages.py --check   # CI: the pages must match the data
```

A record that is renamed or retired loses its page on the next build; add a
redirect for the old address in `vercel.json` (the build says so).

`--check` compares the committed pages against `data/events.json` and exits 1
if they have parted: a record with no page, a page with no record, or a page
whose name, date, status, venue, organizer, canonical, sitemap entry or index
link no longer matches its record. It deliberately ignores everything that
moves on its own — the upcoming cards, the month grid, each page's deep link
into the calendar, the sitemap's dates — because those are rendered as of
today and a check that fails every morning is a check nobody reads.

The directory page is rebuilt the same way from `data/directory.json`:

```sh
python3 tools/build-directory.py            # write
python3 tools/build-directory.py --check    # CI: the page must match the data
```

Every indexable page carries a canonical URL, Open Graph tags, a robots meta
tag allowing large image previews, and JSON-LD structured data (WebSite with
site search, Organization, Place for Niwot, BreadcrumbList, Event, Article on
the history and election pages, TouristDestination on Explore, and an ItemList
of businesses on Eat & Shop). The homepage also carries six visible, matching
FAQ answers for natural-language search intent. `sitemap.xml` lists every
indexable page, and `llms.txt` provides a concise map for AI retrieval systems
that choose to read the emerging format.

## Asset hashes

`assets/css` and `assets/js` filenames carry a content hash, and `vercel.json`
serves them with a one-day cache plus a week of stale-while-revalidate. That
is only safe while the hash is true.

Editing one in place is **not** safe. The name stops matching, the server has
the new bytes, and every browser that has been here recently keeps the old
ones for a day or more. If the HTML changed in the same commit and depends on
the new CSS, those visitors get a broken page — and it looks perfect in a
fresh browser, so it is easy to miss.

After editing anything under `assets/`:

```sh
python3 tools/rehash-assets.py
```

It renames each file to its real hash and rewrites every reference, in the
pages and in the scripts. The scripts import each other, so one rename makes
its importers stale in turn; the tool repeats until everything settles.
`--check` reports without changing anything, and a job runs it on every push.
