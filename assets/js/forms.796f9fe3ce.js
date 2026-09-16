/* Submission form.

   The form POSTs to Formspree on its own (and Formspree then redirects to
   /thanks/ via the _next field), so it works with this file absent or
   broken. This only upgrades the experience: it posts the same payload in
   the background with an Accept: application/json header and renders the
   outcome in place, instead of navigating away.

   Outcome text comes from the endpoint, not from here — so a form that
   cannot deliver says exactly why rather than showing a thank-you the
   server never earned. Field errors from the endpoint are written under the
   field they belong to and tied to it with aria-describedby, and a summary
   is announced. */

/* Submission milestones, for whatever analytics the site adopts: nothing
   listens today. A form view is not a milestone and is never emitted. */
function track(name, detail) {
  document.dispatchEvent(new CustomEvent('niwot:track', { detail: Object.assign({ event: name }, detail || {}) }));
}

function outcomeNode(form, selector, text) {
  const template = form.parentElement.querySelector(selector);
  if (!template) return null;
  const node = template.content.firstElementChild.cloneNode(true);
  if (text) {
    const slot = node.querySelector('[data-message]');
    if (slot) slot.textContent = text;
  }
  return node;
}

function show(form, node) {
  if (!node) return;
  form.replaceWith(node);
  /* role="status" announces it; move focus so keyboard users land on it. */
  node.setAttribute('tabindex', '-1');
  node.focus();
}

function setBusy(form, busy) {
  const button = form.querySelector('button[type="submit"]');
  if (!button) return;
  button.disabled = busy;
  button.textContent = busy ? 'Sending…' : button.dataset.label || button.textContent;
}

function clearFieldErrors(form) {
  form.querySelectorAll('[data-field-error]').forEach((node) => node.remove());
  form.querySelectorAll('[aria-invalid="true"]').forEach((field) => {
    field.removeAttribute('aria-invalid');
    field.removeAttribute('aria-describedby');
  });
}

function showFieldErrors(form, errors) {
  let first = null;
  errors.forEach((error) => {
    const field = error.field && form.querySelector('[name="' + error.field + '"]');
    if (!field || !field.id) return;
    const id = field.id + '-error';
    const note = document.createElement('p');
    note.id = id;
    note.setAttribute('data-field-error', '');
    note.className = 'n-small';
    note.style.cssText = 'margin:8px 0 0;max-width:48ch;color:var(--n-gold-lt)';
    note.textContent = error.message;
    field.setAttribute('aria-invalid', 'true');
    field.setAttribute('aria-describedby', id);
    field.insertAdjacentElement('afterend', note);
    if (!first) first = field;
  });
  return first;
}

function summary(form, text) {
  let error = form.querySelector('[data-form-error]');
  if (!error) {
    error = document.createElement('p');
    error.setAttribute('data-form-error', '');
    error.setAttribute('role', 'alert');
    error.className = 'n-small';
    error.style.cssText = 'margin:14px 0 0;max-width:48ch;color:var(--n-gold-lt)';
    form.appendChild(error);
  }
  error.textContent = text;
}

/* A listing is published with the source it was checked against, so for the
   kinds where the source IS the submission — an event, a correction — the
   link is required rather than welcome. Which kinds those are is marked on
   the options themselves, so the form stays the one place that says so.
   Without scripting the field stays optional: the endpoint cannot enforce it
   either way, and a required attribute nobody can satisfy is worse. */
document.querySelectorAll('[data-contact-form]').forEach((form) => {
  const kind = form.querySelector('[name="kind"]');
  const source = form.querySelector('[name="source"]');
  const note = form.querySelector('[data-source-note]');
  if (kind && source) {
    const sync = () => {
      const option = kind.selectedOptions[0];
      const needed = !!(option && option.hasAttribute('data-requires-source'));
      source.required = needed;
      source.setAttribute('aria-required', String(needed));
      if (note) note.textContent = needed ? '(required)' : '(optional)';
    };
    kind.addEventListener('change', sync);
    sync();
  }

  const button = form.querySelector('button[type="submit"]');
  if (button) button.dataset.label = button.textContent;

  form.addEventListener('submit', async (event) => {
    /* Let the browser handle its own validation first. */
    if (!form.reportValidity()) return;

    event.preventDefault();
    clearFieldErrors(form);
    const kindField = form.querySelector('[name="kind"]');
    const kindValue = kindField ? kindField.value : '';
    track('listing_submit_start', { kind: kindValue });
    const old = form.querySelector('[data-form-error]');
    if (old) old.remove();
    setBusy(form, true);

    let payload;
    let ok = false;
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form))),
      });
      payload = await response.json();
      ok = response.ok && payload.ok !== false;
      /* Formspree reports a problem as { error } or { errors: [{ field, message }] }. */
      if (!ok && payload && !payload.message) {
        payload.message = payload.error
          ? 'That could not be sent: ' + payload.error + '. Please try again, or email editor@townofniwot.com.'
          : 'That could not be sent. Please check the highlighted fields and try again.';
      }
    } catch {
      payload = {
        message:
          'That could not be sent — the connection failed. Please try again, or email editor@townofniwot.com.',
      };
    }

    setBusy(form, false);

    if (ok) {
      track(/correction/i.test(kindValue) ? 'correction_submit_success' : 'listing_submit_success', { kind: kindValue });
      show(form, outcomeNode(form, '[data-form-success]'));
      return;
    }

    /* Errors keep the form in place so the reader can correct and retry;
       only an unconfigured endpoint replaces it, since retrying is futile. */
    if (payload && payload.configured === false) {
      show(form, outcomeNode(form, '[data-form-unavailable]', payload.message));
      return;
    }

    summary(form, payload ? payload.message : 'That could not be sent.');
    const first = Array.isArray(payload && payload.errors) ? showFieldErrors(form, payload.errors) : null;
    if (first) first.focus();
  });
});
