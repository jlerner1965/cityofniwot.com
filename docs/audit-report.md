# TownofNiwot.com — audit and optimization report

Branch `claude/townofniwot-audit-optimize-0ougka` on `jlerner1965/cityofniwot.com`.
Audit and implementation completed September 16, 2026. Every measurement
below was taken in this branch against a local server that applies the same
headers and redirects as `vercel.json`, in headless Chromium.

## 1. Repository, branch and deployment

| Item | Finding |
| --- | --- |
| Repository | `jlerner1965/cityofniwot.com` (origin). Confirmed as the production source: on September 16, 2026 every page served by `https://townofniwot.com` was byte-identical (MD5) to the file in `main`, and the production `ETag` matched the homepage's hash. The older repositories named in the brief were not used. |
| Branch | `claude/townofniwot-audit-optimize-0ougka`, created from `main` at `23a35c3`; no uncommitted work existed. |
| Hosting | Vercel (`server: Vercel` on every response). Apex `townofniwot.com` is canonical; `www.` and `http://` both answer `308` to the apex. HSTS is set. |
| Vercel project | `arp-roject/cityofniwot-com`. Vercel's Git integration deploys this repository: the push of this branch produced a Preview deployment automatically (GitHub deployment 6484742590, status success), at <https://cityofniwot-bkc1rp76e-arp-roject.vercel.app>, behind Vercel Authentication (sign in to the team to view; it sends `x-robots-tag: noindex`). Production deploys from `main` (last production deployment: `23a35c3`, September 15, 2026). |
| Build | None. Static HTML, CSS and JavaScript committed as served; Python tools under `tools/` regenerate the derived pages; four GitHub Actions run checks and the event refresh. |
| Environment variables | None used. |
| Analytics | None (verified in every page head; the privacy page says so). |
| Search Console | No HTML verification tag in any page; if the property is verified it is by DNS. **Owner action:** confirm. |
| Form endpoint | Formspree `xqpkjoob`, JSON and classic POST; delivery confirmed by a controlled submission (section 26). |
| Newsletter | None exists; no signup on any page. |
| Sitemap, robots | `sitemap.xml` regenerated (30 URLs). `robots.txt` allows all and points at the sitemap. |
| Redirects | Three, in `vercel.json` (section 8). |

## 2. Route inventory before

`/`, `/explore/`, `/eat-shop/`, `/events/`, `/community/`, `/civic/incorporation-election/`, `/plan-a-visit/`, `/our-story/`, `/contact/` (noindex), `/privacy/`, `/thanks/` (noindex), `/404/`, and 15 generated event pages under `/events/<id>/`.

## 3. Route inventory after

The same, plus `/civic/` (new hub), `/contact/` now indexable, and 19 event pages: two retired with redirects (`trivia-night-2026-09-15`, `tree-carving-fundraiser-2026-09-15`) and six added (`trivia-night-2026`, `ncaa-open-house-2026-10-04`, `first-friday-art-walk-2026-12-04`, `holiday-magic-market-fayre-2026-12-12`, `lets-wine-about-winter-2027`). No working route was deleted.

## 4. Page-purpose map

| Route | One purpose | One next action |
| --- | --- | --- |
| `/` | Say what Niwot is and route the five needs | Plan a Visit / Find local businesses |
| `/explore/` | Four places in walking order | Plan a visit |
| `/eat-shop/` | Find a business by category or search | Open the business's own page |
| `/events/` | What is on, verified | Organizer's page / View details |
| `/events/<id>/` | One event, fully described | Organizer's page (or register) |
| `/plan-a-visit/` | Get here, park, walk, transit, access | Directions links |
| `/community/` | Which group or body does what | The body's own page |
| `/civic/` | Who governs Niwot; the election; official bodies | The ballot guide / the Commission |
| `/civic/incorporation-election/` | Neutral ballot summary | Official ballot text |
| `/our-story/` | Sourced history | Sources; report a correction |
| `/contact/` | Send a listing or correction | Submit |
| `/privacy/` | What is collected and by whom | Email the editor |

## 5. Implemented change log

**Events (freshness).** The homepage and calendar were pre-rendered weekly, so for up to six days a finished event sat on the homepage as "upcoming" for crawlers and anyone without JavaScript (on audit day the homepage HTML still listed September 15). Records moved to `data/events.json`; `tools/build-event-pages.py` now embeds them in both pages and pre-renders the cards, the month grid, the detail rail and the expected list through `tools/render-calendar.mjs`, which imports the browser's own `calendar-core.js`, so static and hydrated output cannot differ. The refresh job runs daily with Node available. Event structured data now maps `cancelled`/`postponed` to the correct `eventStatus` (it was always `EventScheduled`), and records support `endDate`, `registrationUrl`, `accessibility`, `statusNote`, `nextReview` and stripped `_notes`.

**Event verification** (September 16, against organizer pages): Trivia Night is the Business Association's weekly Tuesday listing (record now recurs over the dates read: September 15, 22, 29); the Holiday Parade gained its 11 am–1 pm hours; the Holiday Magic Market Fayre gained 10 am–4 pm at Niwot Hall and a separate December 12 record; First Friday Art Walk (December 4), the Cultural Arts Association's October 4 open house and Let's Wine About Winter (February 20, 2027) were added; the "Tree Carving Fundraiser" was retired from the calendar because it is an ongoing appeal, not a dated event, and the tree carvings got a sourced entry under Explore. The Great Pumpkin Party stays "expected" (2026 date still unpublished).

**Directory (maintainability).** The 63 listings were extracted to `data/directory.json` with `status`, `hidden`, `sourceType`, `verifiedAt`, `nextReview`, `postalCode` and `_notes`; `tools/build-directory.py` regenerates the page (chips, selector, counts, groups, "last checked" sentence and the ItemList) and `--check` runs in CI. The rebuild reproduced the existing page and ItemList exactly before any data changed. On phones the opening photo takes a short frame and the four quick-category tiles give way to the selector, which brought the search box from 1,100 px down the page to under 800 px.

**Navigation and civic hub.** Bar is now Explore · Eat & Shop · Events · Plan a Visit · Community · Our Story · Civic Information, with "Submit a listing" as a small outlined action; Our Story and Contact were previously reachable on desktop only from the footer. The identifier "Independent community guide" sits under the wordmark while the bar is shown. Measured: one row and a 76 px header at 1181, 1240, 1300, 1301, 1366, 1440, 1600 and 1920 px. New `/civic/` page: civic status, the election band (time-aware), eight official bodies, and how the section is kept. The footer's Civic column links it on every page.

**History.** A sourced "Before 1875" timeline entry on the Arapaho and Cheyenne territory (Fort Laramie Treaty of 1851, Historical Society) and Niwot (Left Hand), c. 1820s–1864, from the Colorado Encyclopedia entry by Margaret Coel; the railroad entry names the Colorado Central line and 1873. No quotations, no folklore. Editorial standards paragraph names the new source and the register.

**Performance and privacy.** Both typefaces self-hosted from `assets/fonts/` (six woff2 files, SIL OFL) with `font-display: swap` and preloads; Google Fonts requests are gone from every page and from the privacy policy. `Content-Security-Policy` added (self, inline styles, Formspree for connect and form-action, no objects, frame-ancestors self) and verified against every page with no console violations. Non-production hosts receive `X-Robots-Tag: noindex, nofollow` via a `missing host` rule in `vercel.json`. Lighthouse Best Practices went from 96 to 100 on every page.

**Contact form.** Kinds now match the brief (new listing, business/event/organization/resource/accessibility/general corrections, event submission, public art, image rights, other); source link required for events and every correction kind; optional "page this is about" field; consent and no-guarantee wording on the form and the thank-you page; `forms.js` emits `listing_submit_start` and `*_submit_success` DOM events for future analytics (never a form view). `/contact/` is indexable with a canonical and breadcrumb schema.

**Accessibility.** Reduced-motion now overrides every transition (the refresh rules had out-ranked the base rule); `main` is a real focus target for the skip link; the election page uses palette variables instead of six pre-refresh hex colours.

**Editorial systems.** `data/source-registry.json` (30 claim records with source, type, last-checked and next-review), `tools/check-review-dates.py` (worklist of overdue events, listings and claims; runs in the weekly issue), seven new dated-content checks covering every page that mentions the election as ahead plus the trivia record's horizon, and `docs/`: election transition, image inventory, analytics map, maintenance schedule, launch checklist.

## 6. Preserved content

Every page, section, photograph, external link and canonical URL that existed on September 16 is still present, apart from the two retired event pages, which redirect. Preserved specifically: the hero line "A small place worth knowing", the quick actions, the FAQ block and its FAQPage schema, the four Explore places, the walking sequence, drive-time estimates (still labelled estimates), the accessibility statement's careful scope, all four community groups and both public bodies, all resident-resource rows, the full election page including its change log and verification note, the timeline and the 12 logged editorial changes, the privacy page's change history, the 404 and thanks pages, the Association-directory links, the 1180 px collapse, the square-edged evergreen/cream design system and the railway devices.

## 7. Removed or consolidated content

- `/events/tree-carving-fundraiser-2026-09-15/`: not an event; consolidated into `/explore/#tree-carvings` (redirected).
- `/events/trivia-night-2026-09-15/`: replaced by the recurring `/events/trivia-night-2026/` (redirected).
- The Google Fonts stylesheet link and the two preconnects: replaced by self-hosted fonts.
- The homepage notice band, FAQ and every civic mention were kept; they are scheduled for revision by the transition plan, not removed.

## 8. Redirect map (`vercel.json`, all 308)

| From | To |
| --- | --- |
| `/events/tree-carving-fundraiser-trivia-night-2026-09-15/` | `/events/trivia-night-2026/` (was `/events/?date=2026-09-15#cal-h`) |
| `/events/trivia-night-2026-09-15/` | `/events/trivia-night-2026/` |
| `/events/tree-carving-fundraiser-2026-09-15/` | `/explore/#tree-carvings` |

All three verified locally; `www.`→apex and `http`→`https` remain Vercel-level.

## 9. Broken-link report

Internal: every `href` and every image reference on every page resolves (0 missing). Outbound (`tools/check-links.py`, after changes): 92 OK, 2 blocked to robots (`niwotlaw.com`, `sliferfrontrange.com`, HTTP 403), 3 "broken" from the sandbox only: `niwotmarket.com` pages reset the connection to this environment but the site is live (fetched through a second route: family-owned grocery at 7980 Niwot Road with Deli, Sachi Sushi and The Nook pages), and `thegardengatecafe.com` answers 403 to automated clients. None removed. **Owner action:** none required; the monthly job will keep reporting the bot-blocked hosts as BLOCKED.

## 10. Event inventory and verification

See the table at the end (section A). Every dated record was read on its organizer's page on September 9–16, 2026; venues and times not on the listing are left off and the description says so.

## 11. Directory inventory and verification

See section B. 63 listings, 10 categories, all checked September 8–10, 2026 against the business's own site or its Association listing; `nextReview` 2026-12-15. Closed or moved businesses: none known.

## 12. Community-organization source list

| Organization | Type | Source | Checked |
| --- | --- | --- | --- |
| Niwot Business Association | business membership | <https://niwot.com/> | 2026-09-09 |
| Niwot Cultural Arts Association | arts nonprofit (2009) | <https://niwotarts.org/> | 2026-09-16 |
| Niwot Historical Society | historical nonprofit | <https://niwothistoricalsociety.org/> | 2026-09-16 |
| Niwot Community Association | resident nonprofit (1990) | <https://niwot.org/> | 2026-09-09 |
| Niwot Election Commission | court-appointed public body | <https://niwotelection.org/> | 2026-09-16 |
| Niwot Local Improvement District | county district | <https://bouldercounty.gov/government/boards-and-commissions/niwot-local-improvement-district/> | 2026-09-09 |

## 13. Resident-resource source list

Boulder County Planning, Road Maintenance, Building Division, Sheriff, Parks & Open Space trail closures and regulations, Elections, Commissioners (all `bouldercounty.gov`); Mountain View Fire Rescue (`mvfpd.org`); Left Hand Water District (`lefthandwater.gov`); Niwot Sanitation District (`niwotsd.colorado.gov`); St. Vrain Valley Schools (`svvsd.org`); RTD Route BOLT. All answered 200 (Left Hand Water 202) on September 16, 2026. Gaps the brief lists and the site does not yet cover with a direct link: postal services, property records and taxes, animal services, public health, general utilities (electric/gas). These are noted as follow-ups rather than added unverified.

## 14. Historical-claim source register

In `data/source-registry.json` (entries for `/our-story/`): the 1873 railroad and 1875 plat (Historical Society), the 1851 treaty and Haystack campground (Historical Society), Niwot (Left Hand) (Colorado Encyclopedia, Coel), the 1907 caboose (Cultural Arts Association), the Tribune building (confidence medium: period attribution without a build date), the 2020 population (Census). Each carries `lastChecked` and `nextReview`.

## 15. Civic-information source register

Same file, entries for `/`, `/civic/`, `/civic/incorporation-election/` and `/community/`: election date, ballot content, comment deadline, electorate, the two authorities' roles, the Commission's appointment. The Election Commission's site on September 16 still gives November 3, 2026, the September 18 noon comment deadline and meeting, and no results language.

## 16. Image and usage-rights inventory

`docs/image-inventory.md`. Eight photograph sets, all contemporary Niwot scenes with alt text and dimensions; rights are asserted by the site's footer but the licence documents are not in the repository (**owner action**).

## 17. Form field and delivery map

| Field | Name | Required | Delivered to |
| --- | --- | --- | --- |
| What is this? | `kind` | yes (select) | Formspree → editor mailbox |
| Name of the business, event or page | `subject` | yes | same |
| Page this is about | `page` | no | same |
| Details | `detail` | yes | same |
| Link to your own page or the source | `source` | required for events and all correction kinds (with JS); optional without | same |
| Your email | `email` | no | same (reply-to) |
| honeypot | `_gotcha` | hidden | Formspree spam filter |
| `_subject`, `_next` | hidden | — | subject line; no-JS redirect to `/thanks/` |

Success is shown only after Formspree answers `ok`; errors keep the form in place with field-level messages tied by `aria-describedby`. `/thanks/` is noindex.

## 18. Newsletter test results

Not applicable: no newsletter or notice list exists, no signup form exists, and the privacy page states this. Nothing to remove.

## 19. Analytics event map

`docs/analytics-events.md`. No analytics runs; `data-track` hooks and form DOM events are in place; enabling needs a GA4 ID and privacy approval (**owner action**).

## 20. Metadata inventory

Section C. Every page has a unique title and description, one H1, a self-referencing canonical (except the noindexed thanks and 404 pages), Open Graph tags and a social image.

## 21. Schema inventory

Home: WebSite (with SearchAction), Organization, Place, WebPage, FAQPage (matching visible answers). Eat & Shop: ItemList of 63 typed LocalBusiness items, BreadcrumbList. Events: ItemList of the 13 upcoming events, BreadcrumbList. Event pages: Event (with eventStatus, location, organizer, offers for free events, eventSchedule for series) and BreadcrumbList. Explore: TouristDestination, BreadcrumbList. Our Story and election: Article, Organization, Place, BreadcrumbList. Civic hub: WebPage, BreadcrumbList. Others: BreadcrumbList. No GovernmentOrganization anywhere. All blocks parse as JSON.

## 22. Accessibility report

axe-core (WCAG 2.0/2.1/2.2 A and AA plus best-practice rules): 0 violations on all 16 audited pages at 1366 px and at 375 px, before and after. Manual: skip link visible on focus and lands on `main`; tab order follows the visual order; focus rings 2 px caboose red on light grounds and light gold on dark grounds (measured); menu button toggles `aria-expanded` and its name, closes on Escape and returns focus; the `<noscript>` fallback shows the full list; landmarks header/nav/main/footer on every page; one H1 per page; reduced motion removes every transition and smooth scrolling; no information carried by colour alone (calendar days also carry a square marker and an accessible name).

## 23. Mobile QA report

Widths 320, 375, 390, 768, 1024, 1366, 1440 on all 16 pages: no horizontal overflow anywhere (document `scrollWidth` equals `clientWidth`). 200 % zoom equivalent (683 px and 640 px viewports): no overflow on home, directory, events, civic, history. Header: 68 px collapsed, one row of links at every width above the 1180 px collapse. Directory on a phone: search box at 795 px from the top (was 1,021 px in this branch's first pass and about 1,100 px in production). Real-device Safari and Android Chrome were not available in this environment (**owner action:** a pass on a phone before merge; the layouts are the same CSS the audit measured).

## 24. Lighthouse results (headless Chromium, local server)

| Page | Before (mobile P/A/BP/SEO) | After (mobile) | Before (desktop) | After (desktop) |
| --- | --- | --- | --- | --- |
| Home | 98/100/96/100 | 98/100/100/100 | 100/100/96/100 | 100/100/100/100 |
| Eat & Shop | 97/100/96/100 | 97/100/100/100 | 100/100/96/100 | 100/100/100/100 |
| Events | 98/100/96/100 | 98/100/100/100 | 100/100/96/100 | 100/100/100/100 |
| Our Story | 97/100/96/100 | 99/100/100/100 | 100/100/96/100 | 100/100/100/100 |
| Community | 99/100/96/100 | 99/100/100/100 | 100/100/96/100 | 100/100/100/100 |
| Plan a Visit | 99/100/96/100 | 99/100/100/100 | 100/100/96/100 | 100/100/100/100 |

CLS 0 everywhere (0.004 on Our Story desktop), TBT 0 ms. Mobile LCP 2.0–2.6 s under Lighthouse's simulated slow 4G is the photograph; it is already AVIF, sized and preloaded. All four targets (90/95/95/95) met on every page.

## 25. Production-build results

No build step. `tools/rehash-assets.py --check`: all 9 hashed assets match. `tools/build-directory.py --check`: page matches data. `tools/build-event-pages.py`: 19 pages, 13 upcoming, sitemap 30 URLs. `tools/check-dated-content.py`: nothing expired. `tools/check-review-dates.py`: 0 overdue, 108 records tracked.

## 26. Controlled form-delivery evidence

September 16, 2026, 15:30 UTC: one JSON POST to `https://formspree.io/f/xqpkjoob` with `kind` "Something else", subject "Controlled test submission — site audit, September 16, 2026", no email address. Response `HTTP 200 {"next":"/thanks","ok":true}`. **Owner action:** confirm the email arrived (subject "TownofNiwot.com submission").

## 27. Screenshots

Representative captures are in `docs/screenshots/`: the directory on a phone before and after, the civic hub at phone and desktop widths, the events page on a phone, and the open menu at 390 px. Full-page before-and-after captures at 375 px and 1366 px were taken for every page during the audit.

## 28. Production-launch checklist

`docs/launch-checklist.md`.

## 29. Editorial maintenance schedule

`docs/maintenance-schedule.md`.

## 30. Remaining risks and required approvals

1. **Preview to review.** The branch's Vercel preview is at <https://cityofniwot-bkc1rp76e-arp-roject.vercel.app> (noindexed by header). Owner to review it before merging; production is untouched.
2. **Photograph licences** are asserted, not filed. Owner to file them per the inventory.
3. **Analytics** off until a GA4 ID and privacy wording are approved.
4. **Real-device testing** (iPhone Safari, Android Chrome) not possible here.
5. **Election transition** is planned and watched by the weekly check; it still needs a person on November 4 and again at certification.
6. **Trivia record horizon** ends September 29; the dated-content check will raise it.
7. **Resident-resource gaps** (postal, property tax, animal services, public health, utilities) are unfilled rather than guessed; each needs the authoritative page identified.
8. **Search Console** verification and sitemap submission unconfirmed.
9. Two directory hosts block automated checks; their listings rely on the quarterly manual review.

---

## A. Event inventory (data/events.json)

| id | Name | Date(s) | Time (MT) | Venue | Organizer | Status | Verified | Source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rock-rails-2026` | Rock & Rails concert series | 2026-06-04 weekly to 2026-08-27 | 17:00–21:00 | Whistle Stop Park, Old Town | Niwot Cultural Arts Association | confirmed | 2026-09-09 | <https://niwotarts.org/rock-rails/> |
| `rise-benefit-concert-2026` | Rise Benefit Concert at Whistle Stop Park | 2026-09-03 | 17:00–21:00 | Whistle Stop Park, Old Town | Niwot Business Association | confirmed | 2026-09-09 | <https://niwot.com/upcoming-events/> |
| `dancing-under-the-stars-2026` | Dancing Under the Stars | 2026-06-12 weekly to 2026-09-18 | 19:00–21:30 | Cottonwood Square | Niwot Business Association | confirmed | 2026-09-09 | <https://niwot.com/events/dancing-under-the-stars-2026/> |
| `second-friday-art-walk-2026-09-11` | Second Friday Art Walk | 2026-09-11 | 17:00–21:00 | Old Town and Cottonwood Square | Niwot Business Association | confirmed | 2026-09-09 | <https://niwot.com/upcoming-events/> |
| `why-not-niwot-awards-night-2026` | Why Not Niwot? Awards Night | 2026-09-11 | 18:00–21:00 | Niwot Hall | Niwot Cultural Arts Association | confirmed | 2026-09-09 | <https://niwotarts.org/why-not-niwot/> |
| `osmosis-opening-diane-pike-2026-09-11` | Opening: Peaks, Pines and a Raven | 2026-09-11 | 17:00–21:00 | Osmosis Gallery | Osmosis Gallery | confirmed | 2026-09-09 | <https://niwot.com/events/opening-peaks-pines-and-a-raven-feat-diane-pike/> |
| `house-blend-band-2026-09-12` | House Blend Band | 2026-09-12 | not published | Niwot — venue on the organizer’s listing | Niwot Business Association | confirmed | 2026-09-14 | <https://niwot.com/upcoming-events/> |
| `trivia-night-2026` | Trivia Night | 2026-09-15 weekly to 2026-09-29 | 18:30–20:30 | The Wheel House | Niwot Business Association | confirmed | 2026-09-16 | <https://niwot.com/events/trivia-night/> |
| `road-of-remembrance-2026-09-16` | The Road of Remembrance | 2026-09-16 | 19:00–20:30 | Niwot Hall | Niwot Business Association | confirmed | 2026-09-14 | <https://niwot.com/upcoming-events/> |
| `basin-design-open-house-2026-09-19` | Basin Design Open House | 2026-09-19 | 17:00–20:00 | Basin Design | Niwot Business Association | confirmed | 2026-09-14 | <https://niwot.com/upcoming-events/> |
| `blessing-of-the-animals-2026-10-04` | Blessing of the Animals | 2026-10-04 | 16:00–17:00 | Niwot United Methodist Church | Niwot Business Association | confirmed | 2026-09-14 | <https://niwot.com/upcoming-events/> |
| `ncaa-open-house-2026-10-04` | Niwot Cultural Arts Association Open House | 2026-10-04 | 14:00–17:00 | 9700 Niwot Road | Niwot Cultural Arts Association | confirmed | 2026-09-16 | <https://niwotarts.org/> |
| `niwot-wellness-lecture-2026-10-07` | Niwot Wellness Lecture Series | 2026-10-07 | 18:00–20:00 | Niwot Hall | Niwot Business Association | confirmed | 2026-09-14 | <https://niwot.com/upcoming-events/> |
| `enchanted-evening-2026` | Enchanted Evening | 2026-11-27 | 18:00–21:00 | Old Town and Cottonwood Square | Niwot Business Association | confirmed | 2026-09-09 | <https://niwot.com/events/enchanted-evening/> |
| `holiday-parade-2026` | Niwot Holiday Parade | 2026-11-28 | 11:00–13:00 | Second Avenue, Murray Street to Niwot Road | Niwot Business Association | confirmed | 2026-09-16 | <https://niwot.com/upcoming-events/holidays-and-parades/> |
| `first-friday-art-walk-2026-12-04` | First Friday Art Walk | 2026-12-04 | 17:00–21:00 | Old Town and Cottonwood Square | Niwot Business Association | confirmed | 2026-09-16 | <https://niwot.com/upcoming-events/> |
| `holiday-magic-market-fayre-2026-12-05` | Holiday Magic Market Fayre | 2026-12-05 | 10:00–16:00 | Niwot Hall and businesses around town | Niwot Business Association | confirmed | 2026-09-16 | <https://niwot.com/upcoming-events/> |
| `holiday-magic-market-fayre-2026-12-12` | Holiday Magic Market Fayre | 2026-12-12 | 10:00–16:00 | Niwot Hall and businesses around town | Niwot Business Association | confirmed | 2026-09-16 | <https://niwot.com/events/holiday-magic-market-fayre/> |
| `lets-wine-about-winter-2027` | Let’s Wine About Winter | 2027-02-20 | 13:00–17:00 | Old Town and Cottonwood Square | Niwot Business Association | confirmed | 2026-09-16 | <https://niwot.com/events/lets-wine-about-winter-2026-743/> |
| `great-pumpkin-party-2026` | Niwot’s Great Pumpkin Party | Late October — the organizer says details are still to come | not published | Second Avenue, Old Town | Niwot Business Association | tentative | 2026-09-09 | <https://niwot.com/events/niwots-great-pumpkin-party/> |
| `rock-rails-2027` | Rock & Rails concert series, 2027 season | Thursday evenings, June to August 2027 — dates published by the organizer each spring | not published | Whistle Stop Park, Old Town | Niwot Cultural Arts Association | tentative | 2026-09-09 | <https://niwotarts.org/rock-rails/> |

## B. Directory inventory (data/directory.json)

| Category | Listings |
| --- | --- |
| Restaurants & Bars | 13 |
| Coffee, Bakery & Sweets | 4 |
| Grocery & Provisions | 2 |
| Shops & Gifts | 9 |
| Arts & Makers | 2 |
| Health & Wellness | 16 |
| Beauty & Personal Care | 4 |
| Everyday Services | 2 |
| Professional Services | 10 |
| Stay the Night | 1 |

Source basis: 39 listings link to the business's own site; 24 to its Niwot Business Association listing (7 of those to the Association's directory root because the business's own site was down at the last check). Verified dates: 2026-09-08 (33), 2026-09-09 (28), 2026-09-10 (2). All 63 are `status: active`, none hidden; `nextReview` is 2026-12-15 for every record.

| id | Name | Category | Address | Link | Checked |
| --- | --- | --- | --- | --- | --- |
| `niwot-tavern` | Niwot Tavern | restaurants-bars | 7960 Niwot Road | <https://www.niwottavern.com/> | 2026-09-08 |
| `raza-fresa` | Raza Fresa Mexican Kitchen | restaurants-bars | 7960 Niwot Road, Suite 11D | <https://razafresa.com/> | 2026-09-08 |
| `cimminis` | Cimmini’s Italian Restaurant | restaurants-bars | 300 Second Avenue | <https://cimminisniwot.com/> | 2026-09-09 |
| `fortezza-ristorante` | Fortezza Ristorante | restaurants-bars | 7916 Niwot Road | <https://fortezzaristorante.com/> | 2026-09-09 |
| `taverna-laudisio` | Taverna Laudisio | restaurants-bars | 121 Second Avenue | <https://tavernalaudisio.com/> | 2026-09-09 |
| `sachi-sushi` | Sachi Sushi | restaurants-bars | 7980 Niwot Road | <https://niwotmarket.com/sachi-sushi-1> | 2026-09-09 |
| `fans-chinese-cuisine` | Fan’s Chinese Cuisine | restaurants-bars | 7960 Niwot Road, Unit C9 | <https://niwot.com/> | 2026-09-08 |
| `abos-pizza` | Abo’s Pizza Niwot | restaurants-bars | 7960 Niwot Road, Suite B5 | <https://abospizza.com/locations/niwot/> | 2026-09-08 |
| `garden-gate-cafe` | The Garden Gate Cafe | restaurants-bars | 7960 Niwot Road, Unit B4 | <https://www.thegardengatecafe.com/> | 2026-09-08 |
| `fritz-family-brewers` | Fritz Family Brewers | restaurants-bars | 6778 N 79th Street | <https://www.fritzfamilybrewers.com/> | 2026-09-08 |
| `the-wheel-house` | The Wheel House | restaurants-bars | 101 Second Avenue, Suite B | <https://www.niwotwheelhouse.com/> | 2026-09-09 |
| `niwot-market-deli` | Niwot Market Deli | restaurants-bars | 7980 Niwot Road | <https://niwotmarket.com/deli> | 2026-09-08 |
| `subway` | Subway | restaurants-bars | 7960 Niwot Road, Unit B10 | <https://restaurants.subway.com/united-states/co/niwot/7960-niwot-rd> | 2026-09-08 |
| `old-oak-coffeehouse` | The Old Oak Coffeehouse | coffee-bakery | 136 Second Avenue | <https://www.theoldoakcoffeehouse.com/> | 2026-09-08 |
| `winot-coffee-company` | WiNot Coffee Company | coffee-bakery | 7960 Niwot Road, Unit D13 | <https://niwot.com/listing/winot-coffee-company/> | 2026-09-09 |
| `emory-janes-coffee-co` | Emory Jane’s Coffee Co. | coffee-bakery | — | <https://www.emoryjanescoffeeco.com/> | 2026-09-09 |
| `love-ice-cream` | Love Ice Cream | coffee-bakery | 240 Second Avenue | <https://www.loveicecream.co/> | 2026-09-09 |
| `niwot-market` | Niwot Market | grocery-provisions | 7980 Niwot Road | <https://niwotmarket.com/> | 2026-09-08 |
| `niwot-liquor` | Niwot Liquor Store | grocery-provisions | 361 Second Avenue | <https://niwot.com/listing/niwot-liquor/> | 2026-09-09 |
| `little-bird` | Little Bird | shops-gifts | 112 Second Avenue | <https://niwot.com/listing/little-bird/> | 2026-09-09 |
| `wise-buys-antiques` | Wise Buys Antiques | shops-gifts | 190 Second Avenue | <https://niwot.com/listing/wise-buys-antiques/> | 2026-09-08 |
| `niwot-jewelry-gifts` | Niwot Jewelry & Gifts | shops-gifts | 300 Second Avenue, Suite 102 | <https://niwot.com/listing/niwot-jewelry-gifts/> | 2026-09-09 |
| `inkberry-books` | Inkberry Books | shops-gifts | 7960 Niwot Road, Suite B3 | <https://niwot.com/listing/inkberry-books/> | 2026-09-09 |
| `fly-away-home` | Fly Away Home | shops-gifts | 7960 Niwot Road | <https://www.flyawayhomedecor.com/> | 2026-09-08 |
| `the-nook` | The Nook | shops-gifts | 7980 Niwot Road | <https://niwotmarket.com/the-nook> | 2026-09-08 |
| `belle-terre-floral` | Belle Terre Floral | shops-gifts | 7960 Niwot Road | <https://niwot.com/listing/belle-terre-floral/> | 2026-09-08 |
| `niwot-wheel-works` | Niwot Wheel Works | shops-gifts | 7960 Niwot Road, Unit C10 | <https://www.niwotwheelworks.com/> | 2026-09-09 |
| `murray-street-flowers` | Murray Street Flowers | shops-gifts | 100 Murray Street | <https://www.murraystreetflowers.com/> | 2026-09-09 |
| `osmosis-gallery` | Osmosis Gallery | arts-makers | 290 Second Avenue | <https://www.osmosisartgallery.com/> | 2026-09-09 |
| `pebble-art-jewelry` | Pebble Art Jewelry | arts-makers | 7980 Niwot Road | <https://niwot.com/listing/pebble-art-jewelry/> | 2026-09-08 |
| `left-hand-animal-hospital` | Left Hand Animal Hospital | health-wellness | 304 Franklin Street | <https://lefthandanimalhospital.com/> | 2026-09-08 |
| `niwot-natural-medicine` | Niwot Natural Medicine | health-wellness | 165 Second Avenue | <https://niwot.com/listing/niwot-natural-medicine-2/> | 2026-09-08 |
| `ohm-physical-therapy` | OHM Physical Therapy | health-wellness | 7960 Niwot Road | <https://niwot.com/listing/ohm/> | 2026-09-08 |
| `dignity-counseling` | Dignity Counseling and Wellness | health-wellness | 210 Franklin Street | <https://niwot.com/listing/dignity-counseling-and-wellness/> | 2026-09-08 |
| `western-wellness-chiropractic` | Western Wellness Chiropractic | health-wellness | 198 Second Avenue | <https://niwot.com/> | 2026-09-08 |
| `chill-cryotherapy` | Chill Cryotherapy & Recovery | health-wellness | 198 Second Avenue, Unit D | <https://chill303.com/> | 2026-09-08 |
| `butterfield-wellness` | Butterfield Wellness Center | health-wellness | 8940 Morton Road | <https://niwot.com/> | 2026-09-10 |
| `hidden-yoga-studio` | The Hidden Yoga Studio | health-wellness | 361 Second Avenue, Unit 201 | <https://niwot.com/> | 2026-09-10 |
| `una-vida` | Una Vida Meditation & Movement | health-wellness | — | <https://www.unavidaniwot.com/> | 2026-09-08 |
| `inner-space-healing` | Inner Space Healing | health-wellness | — | <https://niwot.com/> | 2026-09-08 |
| `hannas-herb-shop` | Hanna’s Herb Shop | health-wellness | 7960 Niwot Road, Suite D15 | <https://www.hannasherbshop.com/> | 2026-09-09 |
| `alchemy-lounge` | The Alchemy Lounge | health-wellness | — | <https://niwot.com/> | 2026-09-08 |
| `ola-chiropractic` | Ola Chiropractic and Wellness | health-wellness | 263 Second Avenue, Suite 106B | <https://www.olachiropracticwellness.com/> | 2026-09-09 |
| `niwot-dental` | Niwot Dental | health-wellness | 6800 N 79th Street, Suite 203 | <https://www.niwotdental.com/> | 2026-09-09 |
| `niles-family-dentistry` | Niles Family Dentistry | health-wellness | 364 Second Avenue | <https://www.nilesfamilydentistry.com/> | 2026-09-09 |
| `healing-collective` | The Healing Collective | health-wellness | 6800 N 79th Street, Suite 202 | <https://niwot.com/listing/healing-collective-the/> | 2026-09-09 |
| `blessings-day-spa` | Blessings Day Spa & Skincare Boutique | beauty-personal-care | 240 Second Avenue | <https://www.niwotblessings.com/> | 2026-09-08 |
| `classic-looks` | Classic Looks | beauty-personal-care | 6964 N 79th Street, Unit 6 | <https://www.classiclooks.net/> | 2026-09-08 |
| `niwot-beauty-bar` | Niwot Beauty Bar | beauty-personal-care | 6897 Paiute Avenue | <https://niwot.com/> | 2026-09-08 |
| `2nd-nature-hair-lounge` | 2nd Nature Hair Lounge | beauty-personal-care | 300 Second Avenue, Suite 101 | <https://2ndnaturehairniwot.com/> | 2026-09-09 |
| `johns-dry-cleaners` | John’s Dry Cleaners | everyday-services | 6964 N 79th Street, Unit 5 | <https://www.johnsdrycleaners.com/locations/> | 2026-09-08 |
| `sew-fresh-studio` | Sew Fresh Studio | everyday-services | 7960 Niwot Road, Suite B1 | <https://sewfreshstudio.com/> | 2026-09-09 |
| `warren-moore-rutherford` | Warren Moore Rutherford, LLP | professional-services | 6964 N 79th Street, Suite 3 | <https://www.niwotlaw.com/> | 2026-09-09 |
| `slifer-smith-frampton-niwot` | Slifer Smith & Frampton Real Estate, Niwot | professional-services | 136 Second Avenue, Suite C | <https://www.sliferfrontrange.com/> | 2026-09-09 |
| `osmosis-architecture` | Osmosis Architecture | professional-services | 290 Second Avenue | <https://www.osmosisarchitecture.com/> | 2026-09-08 |
| `left-hand-valley-courier` | Left Hand Valley Courier | professional-services | — | <https://www.lhvc.com/> | 2026-09-09 |
| `he-business-tax-consultants` | H&E Business and Tax Consultants LLC | professional-services | — | <https://niwot.com/listing/he-business-and-tax-consultants-llc> | 2026-09-09 |
| `noblestar-technologies` | Noblestar Technologies LLC | professional-services | — | <https://niwot.com/listing/noblestar-techologies-llc/> | 2026-09-08 |
| `dmr-group` | DMR Group, LLC | professional-services | — | <https://niwot.com/listing/dmr-group-llc/> | 2026-09-08 |
| `niwot-partners` | Niwot Partners LLC | professional-services | — | <https://niwot.com/listing/niwot-partners-llc/> | 2026-09-09 |
| `itrade-colorado` | iTrade Colorado | professional-services | — | <https://niwot.com/listing/itrade-colorado/> | 2026-09-08 |
| `niwot-group-at-compass` | The Niwot Group at Compass | professional-services | — | <https://theniwotgroup.com/> | 2026-09-09 |
| `niwot-inn` | Niwot Inn & Spa | stay-the-night | 342 Second Avenue | <https://niwotinn.com/> | 2026-09-08 |

## C. Metadata inventory

| Route | Title | Description length | Robots | Canonical | Schema types |
| --- | --- | --- | --- | --- | --- |
| `/` | Niwot, Colorado Community Guide | TownofNiwot.com | 156 | index | self | WebSite, Organization, Place, WebPage, FAQPage |
| `/404/` | Page not found — TownofNiwot.com | 138 | noindex, follow | — | — |
| `/civic/incorporation-election/` | 2026 Niwot Incorporation Election | TownofNiwot.com | 159 | index | self | BreadcrumbList, Article, Organization, Place |
| `/civic/` | Civic Information for Niwot, Colorado | TownofNiwot.com | 149 | index | self | BreadcrumbList, WebPage |
| `/community/` | Niwot Community Organizations & Resident Resources | 148 | index | self | BreadcrumbList |
| `/contact/` | Send a Listing, Event or Correction | TownofNiwot.com | 138 | index | self | BreadcrumbList |
| `/eat-shop/` | Niwot Restaurants, Shops & Local Services | TownofNiwot.com | 151 | index | self | ItemList, BreadcrumbList |
| `/events/` | Niwot, Colorado Events Calendar: Concerts, Art Walks & More | 146 | index | self | ItemList, BreadcrumbList |
| `/explore/` | Things to Do in Niwot, Colorado | TownofNiwot.com | 153 | index | self | BreadcrumbList, TouristDestination |
| `/our-story/` | History of Niwot, Colorado | TownofNiwot.com | 151 | index | self | BreadcrumbList, Article, Organization, Place |
| `/plan-a-visit/` | Visit Niwot, Colorado: Directions, Parking & Accessibility | 131 | index | self | BreadcrumbList |
| `/privacy/` | Privacy | TownofNiwot.com | 130 | index | self | BreadcrumbList |
| `/thanks/` | Thank you — TownofNiwot.com | 95 | noindex, follow | — | — |
| `/events/basin-design-open-house-2026-09-19/` | Basin Design Open House — Sep 19, 2026 | Niwot Events | 153 | index | self | Event, BreadcrumbList |
| `/events/blessing-of-the-animals-2026-10-04/` | Blessing of the Animals — Oct 4, 2026 | Niwot Events | 153 | index | self | Event, BreadcrumbList |
| `/events/dancing-under-the-stars-2026/` | Dancing Under the Stars 2026 | Niwot Events | 149 | index | self | Event, BreadcrumbList |
| `/events/enchanted-evening-2026/` | Enchanted Evening — Nov 27, 2026 | Niwot Events | 153 | index | self | Event, BreadcrumbList |
| `/events/first-friday-art-walk-2026-12-04/` | First Friday Art Walk — Dec 4, 2026 | Niwot Events | 152 | index | self | Event, BreadcrumbList |
| `/events/holiday-magic-market-fayre-2026-12-05/` | Holiday Magic Market Fayre — Dec 5, 2026 | Niwot Events | 155 | index | self | Event, BreadcrumbList |
| `/events/holiday-magic-market-fayre-2026-12-12/` | Holiday Magic Market Fayre — Dec 12, 2026 | Niwot Events | 152 | index | self | Event, BreadcrumbList |
| `/events/holiday-parade-2026/` | Niwot Holiday Parade — Nov 28, 2026 | Niwot Events | 151 | index | self | Event, BreadcrumbList |
| `/events/house-blend-band-2026-09-12/` | House Blend Band — Sep 12, 2026 | Niwot Events | 145 | index | self | Event, BreadcrumbList |
| `/events/lets-wine-about-winter-2027/` | Let’s Wine About Winter — Feb 20, 2027 | Niwot Events | 154 | index | self | Event, BreadcrumbList |
| `/events/ncaa-open-house-2026-10-04/` | Niwot Cultural Arts Association Open House | Niwot, CO Events | 154 | index | self | Event, BreadcrumbList |
| `/events/niwot-wellness-lecture-2026-10-07/` | Niwot Wellness Lecture Series — Oct 7, 2026 | Niwot Events | 153 | index | self | Event, BreadcrumbList |
| `/events/osmosis-opening-diane-pike-2026-09-11/` | Opening: Peaks, Pines and a Raven — Sep 11, 2026 | Niwot Events | 154 | index | self | Event, BreadcrumbList |
| `/events/rise-benefit-concert-2026/` | Rise Benefit Concert at Whistle Stop Park | Niwot, CO Events | 157 | index | self | Event, BreadcrumbList |
| `/events/road-of-remembrance-2026-09-16/` | The Road of Remembrance — Sep 16, 2026 | Niwot Events | 148 | index | self | Event, BreadcrumbList |
| `/events/rock-rails-2026/` | Rock & Rails concert series 2026 | Niwot Events | 155 | index | self | Event, BreadcrumbList |
| `/events/second-friday-art-walk-2026-09-11/` | Second Friday Art Walk — Sep 11, 2026 | Niwot Events | 152 | index | self | Event, BreadcrumbList |
| `/events/trivia-night-2026/` | Trivia Night 2026 | Niwot Events | 148 | index | self | Event, BreadcrumbList |
| `/events/why-not-niwot-awards-night-2026/` | Why Not Niwot? Awards Night — Sep 11, 2026 | Niwot Events | 150 | index | self | Event, BreadcrumbList |
