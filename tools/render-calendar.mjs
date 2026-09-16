#!/usr/bin/env node
/* Pre-render the calendar markup with the same module the browser runs.

   build-event-pages.py calls this with the event records on stdin and gets
   back, as JSON, the HTML the browser would produce at this moment in
   Niwot: the homepage cards, the events page's upcoming list, the current
   month's grid and its detail rail, and the expected list. One renderer,
   so the pre-rendered page and the hydrated page cannot disagree.

       node tools/render-calendar.mjs < events.json

   Set NIWOT_NOW to an ISO instant to render as of another time (tests). */
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { readdirSync } from 'node:fs';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const core = readdirSync(path.join(root, 'assets/js')).find((f) => /^calendar-core\.[0-9a-f]{10}\.js$/.test(f));
if (!core) { console.error('calendar-core.<hash>.js not found'); process.exit(1); }
const C = await import(pathToFileURL(path.join(root, 'assets/js', core)).href);

const events = JSON.parse(readFileSync(0, 'utf8'));
const instant = process.env.NIWOT_NOW ? new Date(process.env.NIWOT_NOW) : new Date();
const now = C.zonedParts(instant);
const today = C.parseIso(now.date);

const upcoming = C.buildUpcoming(events, now);
const shown = C.monthDefault(events, today.y, today.m, now);
const grid = C.renderCells(C.buildCells(events, today.y, today.m, shown ? shown.day : null));
let detail;
if (shown) {
  detail = C.renderDetail(shown.instances.map((i) => C.detailFor(i, now)), { interactive: false });
} else {
  const next = upcoming[0] || null;
  detail = C.renderMonthEmpty(today.y, today.m, now, next, C.instancesInMonth(events, today.y, today.m).length > 0);
}
process.stdout.write(JSON.stringify({
  now,
  monthLabel: C.MONTHS[today.m - 1] + ' ' + today.y,
  homeCards: C.renderUpcoming(upcoming.slice(0, 3), 'link', now),
  upcomingList: C.renderUpcoming(upcoming, 'select', now),
  grid,
  detail,
  expected: C.renderExpected(C.buildExpected(events)),
  expectedCount: C.buildExpected(events).length,
  upcomingIds: upcoming.map((i) => i.id).filter((v, i, a) => a.indexOf(v) === i),
}));
