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

## Layout

- `assets/css/` and `assets/js/` hold the shared stylesheet and scripts. File
  names carry a content hash, so renaming one means updating the pages that
  reference it.
- `img/` holds responsive image sets in AVIF, WebP and JPEG at several widths.
- `assets/photos/` holds the full-size JPEGs used for social sharing previews (`og:image`).
- `vercel.json` enforces trailing-slash URLs, sets cache headers for images and assets, and adds basic security headers.
- `favicon.ico`, `favicon.svg` and `apple-touch-icon.png` are the site icons.
- `robots.txt` and `sitemap.xml` are ready for the production domain.

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
of businesses on Eat & Shop). `sitemap.xml` lists every indexable page.

Note that `assets/css` and `assets/js` file names carry a content hash but are
served with a one-day cache, so editing a file in place is safe.
