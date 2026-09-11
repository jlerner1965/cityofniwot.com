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
| `/404/` and `404.html` | Not-found page |

## Layout

- `assets/css/` and `assets/js/` hold the shared stylesheet and scripts. File
  names carry a content hash, so renaming one means updating the pages that
  reference it.
- `img/` holds responsive image sets in AVIF, WebP and JPEG at several widths.
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

The forms on `/contact/` POST to `/api/contact`. That endpoint is a small
server function that is not part of this static repository. Without it the
form submits but gets a 404, so the endpoint needs to be provided by the host
(a serverless function or a form service) before launch. The progressive
enhancement in `assets/js/forms.*.js` shows the endpoint's response in place.
