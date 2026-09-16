# Image and usage-rights inventory

Every photograph on the site, where it is used, and what is on record about
its rights. The footer's "Photography licensed for use on this site" is the
site's own statement; the licence documents themselves are not in this
repository. **Confirming and filing them (a licence, an invoice, or a
written release per photograph) is a launch-checklist item that only the
editor can close.** No image on the site is stock, AI-generated or
historical-archive material; all are contemporary photographs of Niwot.

Responsive sets live in `img/` under a content id, at 400, 560, 700, 1000 and
1400px in AVIF, WebP and JPEG (the aerial set stops at 547px, its source
size). Social-preview originals live in `assets/photos/`.

| Set id | Subject | Used on | Alt text on record | Rights status |
| --- | --- | --- | --- | --- |
| `wGe2SyelMi` | Second Avenue, the 300 block, hanging baskets and patios | Home hero; `second-avenue-patios.jpg` is the social image for home, contact, thanks, privacy, 404 | Yes | Licensed per site statement; document not on file in repo |
| `KhUALOhxqL` | Niwot Tribune false-front building | Home (Explore card), Explore, Community, Our Story; `niwot-tribune-storefront.jpg` social image for Explore, Community, Civic | Yes | Same |
| `q7-qiFttde` | Cottonwood Square patios and the bronze bears | Home, Explore, Eat & Shop; `niwot-tavern-patios.jpg` social image for Eat & Shop | Yes | Same |
| `6yrnq1YwyN` | CB&Q 14649 caboose at Whistle Stop Park | Events, Community, Our Story; `whistle-stop-caboose.jpg` social image for Events and every event page | Yes | Same |
| `BWgZxGn9m1` | Vintage Colorado Niwot gateway sculpture | Home, Explore, Plan a Visit; `niwot-gateway-sculpture.jpg` social image for Plan a Visit and the election page | Yes | Same |
| `WddVYgaVD3` | Sunset over the Front Range from the grassland trail (portrait) | Home, Explore, Plan a Visit | Yes | Same |
| `UC8Go6fryR` | Left Hand valley and foothills | Our Story hero; `valley-haystack-foothills.jpg` social image for Our Story | Yes | Same |
| `kxfgjkLgAm` | Aerial view of Niwot in autumn (547px source) | Our Story | Yes | Same; the aerial is the one image whose photographer is most likely a third party — confirm first |

Icons and the wordmark (`favicon.*`, `icon-192.png`, `apple-touch-icon.png`,
`assets/logo/*`) are the site's own artwork.

## Standards applied

- Every `<img>` carries `width` and `height`, `decoding="async"`, and
  `loading="lazy"` unless it is the first image on the page, which is
  preloaded instead.
- Alt text describes the scene and names the place. Captions carry the
  location and, on Our Story, the historical identification.
- No image is repeated within one page except the caboose, which appears
  once on Our Story's "Still visible today" pair and once as the social
  preview.
- Event pages share the caboose social image because no event-specific
  photography with rights on record exists. It is a photograph of the park,
  not of the event, and the page text never implies otherwise. Replace it
  per event only with an image whose rights are recorded here.

## To add an image

1. Record the source, photographer, date and rights basis in this table.
2. Export the responsive set (AVIF, WebP, JPEG at the five widths).
3. Write alt text that names the place; add a caption where context matters.
