/* Election page: the five fiscal-issue summaries fold on a phone.

   Each summary is a <details> written open, so without a script — and on a
   wide screen — the page shows everything. On a narrow screen the five
   long cells become one very long column, so they start closed there and
   each opens on its title. A reader who widens the window mid-visit keeps
   whatever state they set. */
const NARROW = '(max-width: 640px)';
const folds = Array.from(document.querySelectorAll('[data-fiscal-fold]'));

if (folds.length && window.matchMedia(NARROW).matches) {
  folds.forEach((fold) => { fold.open = false; });
}
