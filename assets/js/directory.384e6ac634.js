/* Eat & Shop directory: search box, single-select category filter, and the
   folded category groups.

   Every listing is in the HTML already — the build renders the full list,
   folded by category — so the page works without JavaScript and a crawler
   sees all of it. Filtering here only hides rows and opens or hides groups;
   it never fetches or rebuilds them.

   The category is a native radio group on a wide screen and a <select> on a
   phone; both drive the same state. The chosen category (and the search
   text) is kept in the URL — /eat-shop/?category=restaurants-bars — so a
   filtered view can be shared, and Back and Forward restore it. The
   canonical URL stays /eat-shop/: a filtered view has no content of its
   own. */

const form = document.querySelector('[data-dir-filters]');
const search = document.getElementById('dir-q');
const rows = Array.from(document.querySelectorAll('[data-listing]'));
const radios = Array.from(document.querySelectorAll('input[name="category"]'));
const select = document.querySelector('[data-dir-select]');
const groups = Array.from(document.querySelectorAll('[data-group]'));
const heading = document.querySelector('[data-dir-heading]');
const resultLabel = document.querySelector('[data-dir-count]');
const emptyState = document.querySelector('[data-dir-empty]');
const list = document.querySelector('[data-dir-list]');
const clearButtons = Array.from(document.querySelectorAll('[data-dir-clear]'));
const activeStrip = document.querySelector('[data-dir-active]');
const activeLabel = document.querySelector('[data-dir-active-label]');

if (rows.length && search && radios.length) {
  const known = new Map(radios.map((r) => [r.value, r.closest('label').querySelector('[data-chip-label]').textContent.trim()]));
  const state = { cat: 'all', q: '' };

  const haystack = (row) =>
    [row.dataset.name, row.dataset.category, row.dataset.note, row.dataset.area, row.dataset.address]
      .join(' ')
      .toLowerCase();

  /* Unknown category values fall back to all categories rather than to an
     empty page. */
  function readUrl() {
    const params = new URLSearchParams(window.location.search);
    const cat = params.get('category');
    return {
      cat: cat && known.has(cat) && cat !== 'all' ? cat : 'all',
      q: (params.get('q') || '').slice(0, 100),
    };
  }

  function writeUrl(push) {
    const params = new URLSearchParams();
    if (state.cat !== 'all') params.set('category', state.cat);
    if (state.q.trim()) params.set('q', state.q.trim());
    const query = params.toString();
    const url = window.location.pathname + (query ? '?' + query : '') + window.location.hash;
    const method = push ? 'pushState' : 'replaceState';
    window.history[method]({ cat: state.cat, q: state.q }, '', url);
  }

  function apply() {
    const query = state.q.trim().toLowerCase();
    const filtering = state.cat !== 'all' || query !== '';
    let shown = 0;

    rows.forEach((row) => {
      const inCategory = state.cat === 'all' || row.dataset.cat === state.cat;
      const matches = !query || haystack(row).indexOf(query) !== -1;
      const visible = inCategory && matches;
      /* `hidden` removes the row from the layout and the accessibility tree. */
      row.hidden = !visible;
      if (visible) shown += 1;
    });

    /* A group with nothing to show leaves the page; a group that a filter
       has narrowed to is opened, so the reader is not left facing a closed
       fold. With no filter the groups keep whatever the reader set, closed
       by default. */
    groups.forEach((group) => {
      const own = rows.filter((row) => row.dataset.cat === group.dataset.group);
      const count = own.filter((row) => !row.hidden).length;
      group.hidden = count === 0;
      if (filtering && count > 0) group.open = true;
      const counter = group.querySelector('[data-group-count]');
      if (counter) counter.textContent = String(count);
    });

    radios.forEach((radio) => {
      radio.checked = radio.value === state.cat;
    });
    if (select) select.value = state.cat;

    if (heading) {
      heading.textContent = state.cat === 'all' ? 'Local businesses' : known.get(state.cat);
    }
    if (resultLabel) {
      resultLabel.textContent =
        shown === 0 ? 'No matching businesses' : shown === 1 ? '1 listing' : shown + ' listings';
    }
    if (list) list.hidden = shown === 0;
    if (emptyState) emptyState.hidden = shown !== 0;

    /* Whenever a filter is in force, say which, with a reset beside it, so
       a reader who arrived on a filtered URL can see why the list is short. */
    const parts = [];
    if (state.cat !== 'all') parts.push(known.get(state.cat));
    if (query) parts.push('“' + state.q.trim() + '”');
    if (activeStrip) activeStrip.hidden = parts.length === 0;
    if (activeLabel) activeLabel.textContent = parts.join(' · ');
  }

  function sync(fromUrl) {
    Object.assign(state, fromUrl);
    search.value = state.q;
    apply();
  }

  function clear() {
    state.cat = 'all';
    state.q = '';
    search.value = '';
    /* Back to the compact page: every group folded again. */
    groups.forEach((group) => { group.open = false; });
    writeUrl(true);
    apply();
  }

  if (form) {
    /* With JavaScript the filters apply as they change; a submit would only
       reload the page. Without JavaScript the form still works as a GET. */
    form.addEventListener('submit', (event) => event.preventDefault());
  }

  search.addEventListener('input', (event) => {
    state.q = event.target.value;
    writeUrl(false);
    apply();
  });

  radios.forEach((radio) => {
    radio.addEventListener('change', () => {
      if (!radio.checked) return;
      state.cat = radio.value;
      writeUrl(true);
      apply();
    });
  });

  if (select) {
    select.addEventListener('change', () => {
      state.cat = known.has(select.value) ? select.value : 'all';
      writeUrl(true);
      apply();
    });
  }

  clearButtons.forEach((button) => {
    button.addEventListener('click', () => {
      clear();
      search.focus();
    });
  });

  window.addEventListener('popstate', () => sync(readUrl()));

  /* Initial state from the URL. An unknown category is normalised away so
     the history entry matches what is shown. */
  sync(readUrl());
  writeUrl(false);
}
