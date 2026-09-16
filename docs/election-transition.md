# Election transition plan: November 3, 2026

The incorporation election is the one piece of the site that is guaranteed
to go stale on a known date. This is the sequence for the days after it.
The weekly dated-content check (`tools/check-dated-content.py`) opens a
GitHub issue listing every phrase below that is still on the site once its
date has passed, so nothing here depends on memory.

Neutrality rules do not change after the vote: no projected outcomes, no
results from anything but the Boulder County Clerk and Recorder or the Niwot
Election Commission, and preliminary results labelled as such until the
county certifies them.

## Step 1 — Election night and the day after (November 3–4)

Nothing is published on election night unless the County Clerk has posted
unofficial results. When it has:

1. `civic/incorporation-election/index.html`
   - Remove the "Before you vote" task band (`#tasks`) and the comment-deadline
     panel if it is still there.
   - Add a status band in its place, on the sky ground, headed
     **"Unofficial results"**, dated, quoting the Clerk's posted counts for
     Question 1 only if they are on the Clerk's page, with a link to that page.
     Say plainly that the count is unofficial until certified.
   - Change the H1 label from "Civic information" to "Civic information · 2026
     election record"; keep the H1 text.
   - Rewrite "What happens next" (`#after`) in the tense that now applies.
   - Add a change-log entry under `#changes`.
   - Add `"dateModified"` to the Article JSON-LD.
2. `civic/index.html` — change the band label from "Current election" to
   "Recent election", rewrite the two paragraphs in past tense, and point the
   second button at the Clerk's results page.
3. `index.html` — the notice band: change to "Election held November 3, 2026 —
   unofficial results" with the link, or drop the band and rely on the FAQ.
   Update the sixth FAQ answer **and** the matching FAQPage JSON-LD in `<head>`.
4. `our-story/index.html` — the "Today" timeline entry and the "Niwot today"
   band: replace "in November 2026 voters … decide" with what they decided.
5. `community/index.html` — the Election Commission card: past tense.
6. `llms.txt` — describe the page as the record of the election.
7. Run `python3 tools/check-dated-content.py` until it is silent, then
   `python3 tools/build-event-pages.py` for the sitemap dates.

## Step 2 — Certification (by Colorado law, canvass and certification follow
within weeks; use the Clerk's published date)

1. Replace "Unofficial results" with **"Certified results"**, dated, citing the
   Clerk's certification document.
2. If incorporation failed: say the process has ended, that Niwot remains
   unincorporated, and that the Commission's role is complete.
3. If incorporation passed: say the District Court's order of incorporation
   is the next step and link the Commission's or court's notice; do not
   describe the new town's government until it exists.
4. Add the archive label to the election page: a line under the H1 reading
   "Archived civic record — the election was held November 3, 2026" and
   `"archivedAt"` in the Article JSON-LD.
5. Navigation: the "Civic Information" entry keeps its place; the election
   page stays reachable from `/civic/` and the footer. Keep its URL — it
   has inbound links and historical value.
6. Sitemap: nothing to remove.

## Step 3 — Within a month of certification

- Re-read every page for stale tense with `grep -rn "will\|scheduled for\|before you vote" --include=*.html`.
- Move the election entries in `data/source-registry.json` to
  `"status": "retired"` and add new entries for the results and the
  certification document.
- Update the homepage `WebSite` description in JSON-LD, which mentions
  "neutral 2026 incorporation election information".

## What is never done

- Publishing results from a campaign site, a newspaper or a social post.
- Automating publication from a third-party results feed.
- Deleting the election page or redirecting it elsewhere.
