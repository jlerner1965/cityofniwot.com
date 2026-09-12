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
| `/civic/incorporation-election/` | 2026 incorporation election |
| `/plan-a-visit/` | Directions, parking and accessibility |
| `/our-story/` | History of Niwot |
| `/contact/` | Send a listing, event or correction |
| `/privacy/` | Privacy |
| `/events/<event-id>/` | One page per calendar event, generated (15 at present) |
| `/404/` and `404.html` | Not-found page |

## Navigation

Every page carries the same primary navigation, in this order:

| Position | Page | Shown in the bar |
| --- | --- | --- |
| 1 | Explore | yes |
| 2 | Eat & Shop | yes |
| 3 | Events | yes |
| 4 | Community | yes |
| 5 | Plan a Visit | yes |
| 6 | 2026 Election | yes |
| 7 | Our Story | collapsed menu only |
| 8 | Contact | collapsed menu only |

Six is what fits on one line in the masthead without the labels crowding, so
above 1180px the bar shows the first six and the last two are reached from the
footer. At 1180px and below the bar collapses to the menu button, which has the
room the bar does not: it lists all eight, with the last two set a tier back
behind a rule, so every page on the site is one tap from every other page on a
phone. The two rules that carry this are `.n-nav-more` and the
`@media (max-width: 1180px)` block in `assets/css/guide.d3b5b76211.css`; the
same width is repeated in the `<noscript>` block in each page's header, which
opens the list statically where scripting is off.

The page's own entry carries `class="n-on"` and `aria-current="page"`. Adding a
page to the navigation means editing the `<nav class="n-nav">` block in every
HTML file — there is no template — and marking the current entry on its own
page.

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
by the hidden `_gotcha` field. To change the destination mailbox or the
endpoint, edit the form in the Formspree dashboard or update the `action`
attribute on the form.

## Outbound links

The site links out to 91 addresses across 51 hosts — business sites, organizer
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

Worth running monthly, and after any batch of listing edits. It checks that a
page answers, not that it still says what the listing claims — that part is an
editorial check and needs a person.

## Event pages and SEO

Each event on the calendar also has its own page at `/events/<event-id>/`,
with Event structured data pointing at this site, an organizer link, and
links to related events. These pages are generated from the JSON embedded in
`events/index.html`. After editing the calendar data, regenerate them and the
sitemap with:

```sh
python3 tools/build-event-pages.py
```

Every indexable page carries a canonical URL, Open Graph tags, a robots meta
tag allowing large image previews, and JSON-LD structured data (WebSite with
site search, Organization, Place for Niwot, BreadcrumbList, Event, Article on
the history and election pages, TouristDestination on Explore, and an ItemList
of businesses on Eat & Shop). The homepage also carries six visible, matching
FAQ answers for natural-language search intent. `sitemap.xml` lists every
indexable page, and `llms.txt` provides a concise map for AI retrieval systems
that choose to read the emerging format.

Note that `assets/css` and `assets/js` file names carry a content hash but are
served with a one-day cache, so editing a file in place is safe.
