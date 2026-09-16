# Editorial maintenance schedule

The site has no CMS. Its data lives in three JSON files and its checks in
`tools/`; GitHub Actions runs the automatic ones and opens issues. This is
what a person does, and when.

| Cadence | What | How |
| --- | --- | --- |
| Daily (automatic) | Pre-render the calendar and homepage cards as of today; refresh the sitemap | `.github/workflows/refresh-events.yml` runs `tools/build-event-pages.py` at 06:00 Mountain and commits if anything moved |
| Every push (automatic) | Asset hashes match their bytes; the directory page matches its data | `.github/workflows/check-assets.yml` |
| Weekly, Tuesday (automatic) | Dated wording that has expired; records past their review date | `.github/workflows/check-dated-content.yml` runs `tools/check-dated-content.py` and `tools/check-review-dates.py` and opens or updates one issue |
| Monthly, 1st (automatic) | Outbound links | `.github/workflows/check-links.yml` |
| Weekly (editor, ~20 min) | Re-read the Business Association calendar and the Cultural Arts Association site; update `data/events.json` (`verifiedAt`, times, venues, new records, cancellations as `status`); run the builder | `python3 tools/check-review-dates.py --days 14` gives the worklist |
| Weekly (editor) | Answer submissions from the form; publish what the source supports; log corrections on Our Story | Formspree inbox |
| Monthly (editor) | Act on the link report: BROKEN rows are fixed or the listing's link moved to the Association directory with `_notes` saying why | Actions → "Check outbound links" |
| Quarterly (editor, ~2 hours) | Every directory listing re-checked against its source; closed businesses set `status: closed`, `hidden: true`, with a redirect if a page existed; `nextReview` advanced 90 days | `data/directory.json`, then `python3 tools/build-directory.py` |
| Quarterly (editor) | Resident-resource and organization links still handle the task they are listed for; transit and parking paragraphs re-read | `data/source-registry.json` `nextReview` dates |
| Yearly (editor) | History claims and population figure; image-rights table; privacy page against actual behaviour | `docs/image-inventory.md`, `/privacy/` |
| On a date (editor) | The election transition | `docs/election-transition.md`, driven by the dated-content issue |

## Rules that keep the data honest

- A record is never guessed. A time or venue that is not on the organizer's
  page is left off and the description says so.
- `verifiedAt` means "I read the source on this date", nothing looser.
- Editorial notes go in `_notes`; they are stripped before publication.
- A listing that closes keeps its record, hidden, so the history survives
  and the id is never reused.
- After editing anything under `assets/`, run `python3 tools/rehash-assets.py`.
