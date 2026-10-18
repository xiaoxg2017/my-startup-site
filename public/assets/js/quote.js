/* Request-a-quote form.
   If the form's data-endpoint is set (e.g. a Formspree or Web3Forms URL), submissions are posted there.
   If it's empty, the visitor's email app opens with the request filled in. */
(function () {
  var form = document.getElementById('quote-form');
  if (!form) return;
  var status = document.getElementById('form-status');
  var TO = 'xiao@saddlepointpro.com';

  // Prefill from links like /request-a-quote/?event=CES%202027 or ?service=LED%20video%20wall%20rental
  var p = new URLSearchParams(location.search);
  if (p.get('event')) form.event.value = p.get('event');
  var MAP = {
    'Event production labor': 'Production labor',
    'LED video wall rental': 'LED video wall rental',
    'LED display technical services': 'LED content mapping or repair',
    'LED display installation': 'LED display sales & installation',
    'Mobile stage rental': 'Mobile stage rental',
    'Truss and crank lift rental': 'Truss or crank lift rental'
  };
  var want = MAP[p.get('service')];
  if (want) {
    Array.prototype.forEach.call(form.querySelectorAll('input[name="services"]'), function (c) {
      if (c.value === want) c.checked = true;
    });
  }

  function show(msg, err) {
    status.innerHTML = '<div class="form-status' + (err ? ' err' : '') + '">' + msg + '</div>';
  }

  function collect() {
    var services = Array.prototype.filter.call(form.querySelectorAll('input[name="services"]'), function (c) { return c.checked; })
      .map(function (c) { return c.value; });
    return {
      name: form.name.value.trim(), company: form.company.value.trim(), email: form.email.value.trim(),
      phone: form.phone.value.trim(), services: services.join(', '), event: form.event.value.trim(),
      venue: form.venue.value.trim(), start: form.start.value, end: form.end.value, details: form.details.value.trim()
    };
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (form.website.value) return; // spam trap
    var d = collect();
    if (!d.name || !d.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email)) {
      show('Add your name and a valid email address so we can reply.', true);
      (d.name ? form.email : form.name).focus();
      return;
    }
    var endpoint = form.getAttribute('data-endpoint');
    if (endpoint) {
      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true; btn.textContent = 'Sending…';
      fetch(endpoint, { method: 'POST', headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          show('Request sent. We\'ll reply to ' + d.email + ', usually within one business day.');
        })
        .catch(function () {
          show('The request didn\'t go through. Email <a href="mailto:' + TO + '">' + TO + '</a> or call <a href="tel:+17024201941">(702) 420-1941</a> instead.', true);
        })
        .then(function () { btn.disabled = false; btn.textContent = 'Send request'; });
      return;
    }
    var body = [
      'Name: ' + d.name, 'Company: ' + d.company, 'Email: ' + d.email, 'Phone: ' + d.phone,
      'Services: ' + d.services, 'Show/event: ' + d.event, 'Venue: ' + d.venue,
      'On site: ' + d.start + ' to ' + d.end, '', d.details
    ].join('\n');
    var subject = 'Quote request' + (d.event ? ': ' + d.event : '') + (d.company ? ' (' + d.company + ')' : '');
    location.href = 'mailto:' + TO + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    show('Your email app should open with the request filled in. Press send there. If nothing opened, email <a href="mailto:' + TO + '">' + TO + '</a> or call <a href="tel:+17024201941">(702) 420-1941</a>.');
  });
})();
