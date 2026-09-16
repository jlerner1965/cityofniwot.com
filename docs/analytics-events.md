# Analytics event map

**Status: no analytics runs on the site.** The privacy page says so, and it
is true. Enabling GA4 needs two things only the site owner can supply: a
measurement ID, and approval of the privacy-page change that must go live
with it (which service, what it records, how to opt out). Until then nothing
is loaded and nothing is sent.

What is already in place so that switching it on is one small change:

- Every link worth measuring carries a `data-track` attribute naming the
  event (table below). The directory builder and event builder write them,
  so they survive rebuilds.
- `forms.js` dispatches a `niwot:track` DOM event at the two submission
  milestones. A form *view* is never emitted and must never be counted.
- Preview deployments send `X-Robots-Tag: noindex` and are on a different
  hostname; the loader below refuses to run anywhere but `townofniwot.com`,
  so preview activity cannot land in production data.

| Event name | Where it fires | Parameters |
| --- | --- | --- |
| `directory_search` | `#dir-q` input on `/eat-shop/`, debounced, when the query settles (wire in `directory.js`) | `query_length`, `results` |
| `directory_filter` | category radio or `<select>` change on `/eat-shop/` | `category` |
| `business_website_click` | `data-track="business_website_click"` — listing links to a business's own site | `listing` (row id), `category` |
| `business_listing_click` | `data-track="business_listing_click"` — listing links to the Association directory | same |
| `event_view` | page view of any `/events/<id>/` page (derive from `page_location`) | `event_id` |
| `event_source_click` | `data-track="event_source_click"` — "Organizer's page" on event pages | `event_id` |
| `event_registration_click` | `data-track="event_registration_click"` — registration or ticket links | `event_id` |
| `resident_resource_click` | `data-track="resident_resource_click"` on `/community/` | `href` host |
| `official_civic_source_click` | `data-track="official_civic_source_click"` on `/civic/` and the election page | `href` host |
| `plan_visit_click` | `data-track="plan_visit_click"` — the homepage hero CTA | — |
| `directions_click` | `data-track="directions_click"` on `/plan-a-visit/` | `destination` |
| `listing_submit_start` | `niwot:track` from `forms.js` when a submission is sent | `kind` |
| `listing_submit_success` | `niwot:track` after Formspree answers `ok` for a listing or event | `kind` |
| `correction_submit_success` | `niwot:track` after Formspree answers `ok` for any correction kind | `kind` |
| `newsletter_signup_success` | not applicable: no newsletter exists | — |

Never counted: form views, failed submissions, automated traffic (GA4's
bot filtering plus the hostname guard), preview activity.

Context sent with every event: `page_location`, `page_title` and the
`data-track` parameters above. No user identifiers, no email addresses, no
form contents.

## Loader, once approved

Add to every page head, after the stylesheet, with the real ID:

```html
<script src="/assets/js/analytics.<hash>.js" defer data-id="G-XXXXXXXXXX"></script>
```

`analytics.js` (to be written when approved; ~40 lines): exit unless
`location.hostname === 'townofniwot.com'`; load gtag with
`anonymize_ip` and no advertising features; delegate `click` on
`[data-track]` to `gtag('event', name, params)`; listen for `niwot:track`
and forward it. Then update `/privacy/` and `vercel.json`'s
`Content-Security-Policy` (`script-src` and `connect-src` for
`googletagmanager.com` and `google-analytics.com`) in the same commit.
