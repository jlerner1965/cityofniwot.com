# Production launch checklist

Merge `claude/townofniwot-audit-optimize-0ougka` only when every box is
ticked. Items marked **owner** need the site owner; the rest are verified in
the preview.

## Verified in this branch

- [x] Repository `jlerner1965/cityofniwot.com` is the one production serves (every page byte-identical to `townofniwot.com` on September 16, 2026)
- [x] Past events do not appear as upcoming (daily rebuild; pre-render through the browser's own module)
- [x] Current events re-read against organizer pages on September 16, 2026
- [x] Civic information current, neutral and dated; transition plan written and watched by the dated-content check
- [x] Business listings carry source, date, status and review fields in `data/directory.json`
- [x] Broken internal links: none. Outbound: 84 OK, 3 blocked-to-robots, 4 unreachable from the audit sandbox but confirmed live (Niwot Market)
- [x] Submission form delivers (controlled test, Formspree answered `ok`, September 16, 2026)
- [x] No newsletter exists; nothing to remove
- [x] Privacy page matches behaviour (Formspree, Vercel; no fonts from Google; no analytics)
- [x] Keyboard: menu opens, closes on Escape, focus returns to the button; skip link present
- [x] Schema validated (JSON parses; types per page listed in the audit report)
- [x] Canonicals self-referencing; sitemap regenerated with the two new pages
- [x] Preview hosts send `X-Robots-Tag: noindex, nofollow` (vercel.json `missing host` rule)
- [x] Content-Security-Policy added and tested against every page in headless Chromium

## Owner

- [x] Vercel project `arp-roject/cityofniwot-com` deploys this repository; the branch preview is at https://cityofniwot-bkc1rp76e-arp-roject.vercel.app (behind Vercel Authentication; noindexed by header)
- [ ] Review the preview at phone and desktop widths, in particular the navigation bar between 1181px and 1440px and the new `/civic/` page
- [ ] File the photograph licences per `docs/image-inventory.md`
- [ ] Decide on analytics: supply a GA4 measurement ID and approve the privacy wording, or leave analytics off
- [ ] Confirm the Formspree test email arrived in the editor mailbox (subject "TownofNiwot.com submission", September 16, 2026)
- [ ] Add a Search Console verification if none exists (DNS or HTML tag), then submit `sitemap.xml`
- [ ] Merge; then run Actions → "Refresh event pages" once so the sitemap dates are from `main`

## After launch

- [ ] Check `https://townofniwot.com/events/trivia-night-2026-09-15/` redirects (308) to `/events/trivia-night-2026/`
- [ ] Check response headers on production include `Content-Security-Policy` and do **not** include `X-Robots-Tag`
- [ ] Watch the first daily refresh commit the next morning
