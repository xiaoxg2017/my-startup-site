/* Las Vegas trade show calendar
   Reads /data/events.json and renders a filterable list.
   The page ships with a pre-rendered list for search engines and no-JS visitors;
   this script replaces it with the live, filterable version. */
(function () {
  var M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  var ML = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var TODAY = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Los_Angeles' }).format(new Date());
  var listEl = document.getElementById('cal-list');
  var tools = document.getElementById('cal-tools');
  var bar = document.getElementById('cal-bar');
  var f = {
    q: document.getElementById('f-q'),
    month: document.getElementById('f-month'),
    cat: document.getElementById('f-cat'),
    venue: document.getElementById('f-venue'),
    past: document.getElementById('f-past')
  };
  var DATA, EVENTS = [];

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function parts(s) { return s.split('-').map(Number); }
  function addDay(s) {
    var p = parts(s), dt = new Date(Date.UTC(p[0], p[1] - 1, p[2] + 1));
    return dt.toISOString().slice(0, 10);
  }
  function shortRange(ev) {
    if (!ev.startDate) return ['TBA', 'Dates not announced'];
    var a = parts(ev.startDate), b = parts(ev.endDate || ev.startDate), main;
    if (ev.startDate === ev.endDate) main = M[a[1] - 1] + ' ' + a[2];
    else if (a[1] === b[1] && a[0] === b[0]) main = M[a[1] - 1] + ' ' + a[2] + '–' + b[2];
    else main = M[a[1] - 1] + ' ' + a[2] + '–<wbr>' + M[b[1] - 1] + ' ' + b[2];
    main = main.replace(/ /g, '&nbsp;');
    return [main, a[0] === b[0] ? String(a[0]) : a[0] + '–' + b[0]];
  }
  function fullRange(ev) {
    if (!ev.startDate) return 'Not announced';
    var a = parts(ev.startDate), b = parts(ev.endDate);
    var s = ML[a[1] - 1] + ' ' + a[2] + ', ' + a[0];
    if (ev.endDate !== ev.startDate) s += ' – ' + ML[b[1] - 1] + ' ' + b[2] + ', ' + b[0];
    return s;
  }
  function state(ev) {
    if (!ev.startDate) return 'tba';
    if (ev.endDate < TODAY) return 'past';
    if (ev.startDate <= TODAY) return 'now';
    return 'upcoming';
  }
  function statusTag(ev) {
    if (ev.status === 'confirmed') return '<span class="tag confirmed">Organizer-confirmed</span>';
    if (ev.status === 'reported') return '<span class="tag reported">Confirm with organizer</span>';
    return '<span class="tag">Dates not announced</span>';
  }
  function gcal(ev) {
    var q = new URLSearchParams({
      action: 'TEMPLATE',
      text: ev.name,
      dates: ev.startDate.replace(/-/g, '') + '/' + addDay(ev.endDate).replace(/-/g, ''),
      details: ev.description + '\nOfficial site: ' + ev.officialUrl,
      location: ev.venue + ', Las Vegas, NV'
    });
    return 'https://calendar.google.com/calendar/render?' + q.toString();
  }

  function eventHTML(ev) {
    var r = shortRange(ev), st = state(ev);
    var timeTag = st === 'now' ? '<span class="tag now">Happening now</span>' : st === 'past' ? '<span class="tag past">Ended</span>' : '';
    var notes = ev.notes ? '<dt>Notes</dt><dd>' + esc(ev.notes) + '</dd>' : '';
    var cal = ev.startDate
      ? '<a class="btn small ghost" href="' + esc(gcal(ev)) + '" rel="noopener">Add to Google Calendar</a>' +
        '<button class="btn small ghost ics" type="button" data-id="' + esc(ev.id) + '">Download .ics</button>'
      : '';
    return '<details class="ev' + (st === 'past' ? ' is-past' : '') + '" id="' + esc(ev.id) + '">' +
      '<summary><div class="when">' + r[0] + '<small>' + r[1] + '</small></div>' +
      '<div class="what"><strong>' + esc(ev.name) + '</strong><span>' + esc(ev.venue) + '</span></div>' +
      '<div class="tags">' + timeTag + '<span class="tag">' + esc(ev.category) + '</span>' + statusTag(ev) + '</div></summary>' +
      '<div class="ev-body"><p>' + esc(ev.description) + '</p>' +
      '<dl><dt>Dates</dt><dd>' + fullRange(ev) + '</dd><dt>Venue</dt><dd>' + esc(ev.venue) + '</dd>' +
      '<dt>Industry</dt><dd>' + esc(ev.category) + '</dd>' +
      '<dt>Date status</dt><dd>' + esc((DATA.statusKey || {})[ev.status] || '') + '</dd>' +
      '<dt>Source</dt><dd><a href="' + esc(ev.sourceUrl) + '" rel="noopener">' + esc(ev.sourceLabel) + '</a></dd>' +
      '<dt>Last checked</dt><dd>' + esc(ev.lastVerified) + '</dd>' + notes + '</dl>' +
      '<div class="ev-actions"><a class="btn small" href="' + esc(ev.officialUrl) + '" rel="noopener">Official event website</a>' + cal + '</div>' +
      '<p class="ev-cta">Working this show? <a href="/request-a-quote/?event=' + encodeURIComponent(ev.name) + '">Ask about local crew or LED support</a>.</p>' +
      '</div></details>';
  }

  function fillSelect(sel, values, labelFn) {
    values.forEach(function (v) {
      var o = document.createElement('option');
      o.value = v; o.textContent = labelFn ? labelFn(v) : v;
      sel.appendChild(o);
    });
  }

  function monthKey(ev) { return ev.startDate ? ev.startDate.slice(0, 7) : 'tba'; }
  function monthLabel(k) {
    if (k === 'tba') return 'Dates not announced';
    var p = k.split('-'); return ML[Number(p[1]) - 1] + ' ' + p[0];
  }

  function render() {
    var q = f.q.value.trim().toLowerCase();
    var showPast = f.past.checked;
    var visible = EVENTS.filter(function (ev) {
      if (!showPast && state(ev) === 'past') return false;
      if (f.month.value && monthKey(ev) !== f.month.value) return false;
      if (f.cat.value && ev.category !== f.cat.value) return false;
      if (f.venue.value && ev.venueGroup !== f.venue.value) return false;
      if (q) {
        var hay = ev.name.toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });

    var total = EVENTS.filter(function (ev) { return showPast || state(ev) !== 'past'; }).length;
    document.getElementById('cal-count').textContent = 'Showing ' + visible.length + ' of ' + total + ' shows';

    if (!visible.length) {
      listEl.innerHTML = '<div class="empty"><p><strong>No shows match these filters.</strong></p>' +
        '<p>Clear a filter or turn on past events. Looking for a show we don\'t list? Email <a href="mailto:xiao@saddlepointpro.com">xiao@saddlepointpro.com</a> and we\'ll look into it.</p></div>';
      syncURL();
      return;
    }

    var groups = {}, order = [];
    visible.forEach(function (ev) {
      var k = monthKey(ev);
      if (!groups[k]) { groups[k] = []; order.push(k); }
      groups[k].push(ev);
    });
    listEl.innerHTML = order.map(function (k) {
      return '<section class="month-group"><h3>' + monthLabel(k) + '</h3>' + groups[k].map(eventHTML).join('') + '</section>';
    }).join('');
    syncURL();
  }

  function syncURL() {
    var p = new URLSearchParams();
    if (f.q.value.trim()) p.set('q', f.q.value.trim());
    if (f.month.value) p.set('month', f.month.value);
    if (f.cat.value) p.set('industry', f.cat.value);
    if (f.venue.value) p.set('venue', f.venue.value);
    if (f.past.checked) p.set('past', '1');
    var qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }

  function readURL() {
    var p = new URLSearchParams(location.search);
    f.q.value = p.get('q') || '';
    ['month', 'cat', 'venue'].forEach(function (k) {
      var v = p.get(k === 'cat' ? 'industry' : k);
      if (v && Array.prototype.some.call(f[k].options, function (o) { return o.value === v; })) f[k].value = v;
    });
    f.past.checked = p.get('past') === '1';
  }

  function downloadICS(ev) {
    var stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+/, '');
    function fold(s) { return s.replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n'); }
    var ics = [
      'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Saddle Point Productions//Trade Show Calendar//EN', 'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',
      'UID:' + ev.id + '@saddlepointpro.com',
      'DTSTAMP:' + stamp,
      'DTSTART;VALUE=DATE:' + ev.startDate.replace(/-/g, ''),
      'DTEND;VALUE=DATE:' + addDay(ev.endDate).replace(/-/g, ''),
      'SUMMARY:' + fold(ev.name),
      'LOCATION:' + fold(ev.venue + ', Las Vegas, NV'),
      'DESCRIPTION:' + fold(ev.description + '\nOfficial site: ' + ev.officialUrl + '\nConfirm dates with the organizer before booking.'),
      'URL:' + ev.officialUrl,
      'END:VEVENT', 'END:VCALENDAR'
    ].join('\r\n');
    var blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = ev.id + '.ics';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function init(data) {
    DATA = data;
    EVENTS = data.events.slice().sort(function (a, b) {
      if (!a.startDate) return 1; if (!b.startDate) return -1;
      return a.startDate < b.startDate ? -1 : a.startDate > b.startDate ? 1 : a.name.localeCompare(b.name);
    });
    var months = [], cats = [], venues = [];
    EVENTS.forEach(function (ev) {
      var k = monthKey(ev);
      if (months.indexOf(k) === -1) months.push(k);
      if (cats.indexOf(ev.category) === -1) cats.push(ev.category);
      if (venues.indexOf(ev.venueGroup) === -1) venues.push(ev.venueGroup);
    });
    fillSelect(f.month, months, monthLabel);
    fillSelect(f.cat, cats.sort());
    fillSelect(f.venue, venues.sort());
    readURL();
    tools.hidden = false; bar.hidden = false;

    tools.addEventListener('submit', function (e) { e.preventDefault(); });
    ['input', 'change'].forEach(function (t) { tools.addEventListener(t, render); });
    f.past.addEventListener('change', render);
    document.getElementById('f-reset').addEventListener('click', function () {
      f.q.value = ''; f.month.value = ''; f.cat.value = ''; f.venue.value = ''; f.past.checked = false; render();
    });
    listEl.addEventListener('click', function (e) {
      var b = e.target.closest('.ics'); if (!b) return;
      var ev = EVENTS.filter(function (x) { return x.id === b.getAttribute('data-id'); })[0];
      if (ev) downloadICS(ev);
    });
    render();
    if (location.hash) { var el = document.getElementById(location.hash.slice(1)); if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); } }
  }

  if (!window.fetch || !listEl) return;
  fetch('/data/events.json', { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(init)
    .catch(function () { /* keep the pre-rendered list */ });
})();
