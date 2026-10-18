#!/usr/bin/env python3
"""Builds the Saddle Point Productions site into /public.

Run from the repo root:   python3 tools/build.py
No packages needed. Re-run after editing page copy below or public/data/events.json
so the pre-rendered calendar (what Google sees) matches the data file.
"""
import json, html, datetime, pathlib, urllib.parse, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://saddlepointpro.com"
PHONE_DISPLAY = "(702) 420-1941"
PHONE_TEL = "+17024201941"
EMAIL = "xiao@saddlepointpro.com"
# No street address: the business runs from a home, so the site shows only city and ZIP.
ADDRESS = {"city": "Las Vegas", "region": "NV", "zip": "89123"}
BUILD_DATE = datetime.date.today().isoformat()
FONTS = "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..800&display=swap"
e = html.escape

VENUE_ADDR = {
    "Las Vegas Convention Center": ("3150 Paradise Rd", "89109"),
    "Venetian Expo": ("201 Sands Ave", "89169"),
    "Mandalay Bay Convention Center": ("3950 S Las Vegas Blvd", "89119"),
    "Caesars Palace": ("3570 S Las Vegas Blvd", "89109"),
}

NAV = [
    ("/production-support-labor/", "Production support"),
    ("/led-video-wall-rental/", "LED video walls"),
    ("/event-equipment-rental/", "Equipment rental"),
    ("/las-vegas-trade-show-calendar/", "Trade show calendar"),
    ("/about/", "About"),
]

# ---------------------------------------------------------------- PHOTOS
# Stock photos from Unsplash (free for commercial use under the Unsplash License,
# https://unsplash.com/license). They load from Unsplash's image CDN, which resizes them.
#
# To use YOUR OWN photo instead: put the file in public/assets/img/photos/ (for example
# "led-wall.jpg") and set "src" to "/assets/img/photos/led-wall.jpg". Update "alt" to
# describe your photo, and clear "credit" and "credit_url" (set them to "").
# Then run: python3 tools/build.py
#
# Credits aren't required by the Unsplash License, so they're hidden. The photographer
# names below are kept for your records. Set SHOW_CREDITS = True to show them again.
SHOW_CREDITS = False
PHOTOS = {
    "general-session": {"src": "photo-1773828755374-0ee802d9f44b", "alt": "Speaker presenting to a large audience in a conference auditorium",
                        "credit": "Marwen Larafa", "credit_url": "https://unsplash.com/@marwen_larafa"},
    "festival-stage": {"src": "photo-1727096857692-e9dadf2bc92e", "alt": "Crew and performers on a festival stage under lighting rigs",
                       "credit": "Ambitious Studio* | Rick Barrett", "credit_url": "https://unsplash.com/@weareambitious"},
    "trade-show": {"src": "photo-1761195696518-6384573549ea", "alt": "Visitors walking a busy exhibition hall lined with trade show booths",
                   "credit": "Trans Russia", "credit_url": "https://unsplash.com/@transrussia"},
    "road-cases": {"src": "photo-1573339886430-32442b7ab985", "alt": "Stack of black road cases ready for load-in",
                   "credit": "Ben Tofan", "credit_url": "https://unsplash.com/@bentofan"},
    "led-wall": {"src": "photo-1769798643655-e0f10f62c3fd", "alt": "Audience watching a presentation on a large LED screen at a conference main stage",
                 "credit": "Carlos Gil", "credit_url": "https://unsplash.com/@carlosgil83"},
    "led-closeup": {"src": "photo-1545164415-0fae860defbd", "alt": "Close-up of glowing LED lights",
                    "credit": "Justin Lane", "credit_url": "https://unsplash.com/@jlane56"},
    "outdoor-stage": {"src": "photo-1574504212584-29a03eb6e41e", "alt": "Crowd in front of an outdoor festival stage on a sunny day",
                      "credit": "A J.", "credit_url": "https://unsplash.com/@antoinejulien"},
    "truss-lights": {"src": "photo-1786173071075-c56bf31c17de", "alt": "Stage lights on a metal truss shining through haze",
                     "credit": "Maximilian Bungart", "credit_url": "https://unsplash.com/@hypernature"},
    "led-building": {"src": "photo-1575719028439-65ce8662c1cc", "alt": "People walking past a building with large permanent LED displays",
                     "credit": "Kevin Grieve", "credit_url": "https://unsplash.com/@grievek1610begur"},
    "concert-stage": {"src": "photo-1561229261-911dc57bef91", "alt": "Concert stage with lighting over the crowd",
                      "credit": "sthanley de León", "credit_url": "https://unsplash.com/@stanliess"},
    "vegas-strip": {"src": "photo-1581351721010-8cf859cb14a4", "alt": "The Las Vegas Strip lit up at night",
                    "credit": "Julian Paefgen", "credit_url": "https://unsplash.com/@julianpaefgen"},
}


def photo_url(src, w, h):
    if src.startswith("photo-"):
        return f"https://images.unsplash.com/{src}?auto=format&fit=crop&w={w}&h={h}&q=70"
    return src


def photo(key, ratio=(4, 3), sizes="(max-width: 880px) 100vw, 40vw", eager=False, cls="photo"):
    """A <figure> with a responsive image and a small photo credit."""
    p = PHOTOS[key]
    rw, rh = ratio
    widths = [640, 960, 1400]
    src = p["src"]
    if src.startswith("photo-"):
        srcset = ", ".join(f"{photo_url(src, w, round(w * rh / rw))} {w}w" for w in widths)
        attrs = f'src="{photo_url(src, 960, round(960 * rh / rw))}" srcset="{srcset}" sizes="{sizes}"'
    else:
        attrs = f'src="{e(src)}"'
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    credit = ""
    if SHOW_CREDITS and p.get("credit"):
        credit = f'<figcaption>Photo: <a href="{e(p["credit_url"])}?utm_source=saddlepointpro&amp;utm_medium=referral" rel="noopener">{e(p["credit"])}</a> / <a href="https://unsplash.com/?utm_source=saddlepointpro&amp;utm_medium=referral" rel="noopener">Unsplash</a></figcaption>'
    return (f'<figure class="{cls}"><img {attrs} alt="{e(p["alt"])}" width="{rw * 240}" height="{rh * 240}" {load} decoding="async">'
            f"{credit}</figure>")


def page_head(crumbs_html, h1, lede_html, actions_html="", photo_key=None):
    text = f"""<div>
    <p class="crumbs">{crumbs_html}</p>
    <h1>{e(h1)}</h1>
    <p class="lede">{lede_html}</p>
    {actions_html}
  </div>"""
    media = photo(photo_key, eager=True) if photo_key else ""
    cls = "page-head has-photo" if photo_key else "page-head"
    return f"""<section class="{cls}">
  <div class="wrap">
  {text}
  {media}
  </div>
</section>"""


BUSINESS_LD = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "@id": SITE + "/#business",
    "name": "Saddle Point Productions LLC",
    "url": SITE + "/",
    "logo": SITE + "/assets/img/logo-512.png",
    "image": SITE + "/assets/img/og-default.jpg",
    "telephone": "+1-702-420-1941",
    "email": EMAIL,
    "address": {"@type": "PostalAddress", "addressLocality": ADDRESS["city"],
                "addressRegion": ADDRESS["region"], "postalCode": ADDRESS["zip"], "addressCountry": "US"},
    "areaServed": [{"@type": "City", "name": "Las Vegas"}, {"@type": "AdministrativeArea", "name": "Clark County, Nevada"}],
    "description": "Las Vegas production support partner providing event production labor, LED video wall rental and support, staging, truss and crank lift rental, and permanent LED display installation.",
    "sameAs": [
        "https://www.instagram.com/saddle_point_pro/",
        "https://www.facebook.com/profile.php?id=61580309384973",
    ],
}


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"


def head(title, desc, path, extra=""):
    url = SITE + path
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Saddle Point Productions">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/og-default.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/css/site.css">
<meta name="theme-color" content="#21152e">
{extra}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(current):
    cur = ' aria-current="page"'
    links = "\n".join(
        f'<a href="{href}"{cur if href == current else ""}>{label}</a>' for href, label in NAV)
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Saddle Point Productions home">
      <img src="/assets/img/logo-96.png" alt="" width="44" height="44">
      <span>Saddle Point Productions<small>Las Vegas production support</small></span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav" aria-label="Main">
{links}
<a class="btn small" href="/request-a-quote/">Request a quote</a>
    </nav>
  </div>
</header>
<main id="main">
"""


def footer(extra_scripts=""):
    year = datetime.date.today().year
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="cols">
      <div>
        <h2>Saddle Point Productions LLC</h2>
        <p>Local production support for event companies, AV providers, and exhibit houses working in Las Vegas.</p>
        <address>
          <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br>
          <a href="mailto:{EMAIL}">{EMAIL}</a><br>
          {ADDRESS['city']}, {ADDRESS['region']} {ADDRESS['zip']}
        </address>
      </div>
      <div>
        <h2>Services</h2>
        <ul>
          <li><a href="/production-support-labor/">Production support &amp; labor</a></li>
          <li><a href="/led-video-wall-rental/">LED video wall rental</a></li>
          <li><a href="/led-display-services/">LED mapping &amp; repair</a></li>
          <li><a href="/led-display-sales-installation/">LED display sales &amp; installation</a></li>
          <li><a href="/mobile-stage-rental/">Mobile stage rental</a></li>
          <li><a href="/truss-crank-lift-rental/">Truss &amp; crank lift rental</a></li>
        </ul>
      </div>
      <div>
        <h2>Plan</h2>
        <ul>
          <li><a href="/las-vegas-trade-show-calendar/">Las Vegas trade show calendar</a></li>
          <li><a href="/request-a-quote/">Request a quote</a></li>
          <li><a href="/about/">About us</a></li>
          <li><a href="https://www.instagram.com/saddle_point_pro/" rel="noopener">Instagram</a></li>
          <li><a href="https://www.facebook.com/profile.php?id=61580309384973" rel="noopener">Facebook</a></li>
        </ul>
      </div>
    </div>
    <p class="legal">© {year} Saddle Point Productions LLC. Trade show names belong to their organizers; Saddle Point Productions is not affiliated with the events listed in the calendar.</p>
  </div>
</footer>
<script>
(function(){{var b=document.querySelector('.nav-toggle'),n=document.getElementById('site-nav');if(!b)return;
b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o);}});}})();
</script>
{extra_scripts}
</body>
</html>
"""


def cta_band(heading="Have a show coming up?", text=None):
    text = text or "Send the dates, venue, and what you need. We'll reply with what we can cover and a quote, usually within one business day."
    return f"""<section class="cta-band">
  <div class="wrap">
    <h2>{heading}</h2>
    <p>{text}</p>
    <div class="actions">
      <a class="btn" href="/request-a-quote/">Request a quote</a>
      <a class="btn ghost" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
    </div>
  </div>
</section>
"""


def crumbs_ld(items):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(items)]})


def faq_html(faqs):
    if not faqs:
        return "", ""
    body = "\n".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in faqs)
    schema = ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(
            re.sub(r"<[^>]+>", "", a))}} for q, a in faqs]})
    return f"""<section class="block alt"><div class="wrap"><h2>Questions we get</h2><div class="faq">{body}</div></div></section>""", schema


def write(path, content):
    out = PUB / path.strip("/") / "index.html" if path != "/" else PUB / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    PAGES.append(path)


PAGES = []

# ---------------------------------------------------------------- events
DATA = json.loads((PUB / "data" / "events.json").read_text())
EVENTS = DATA["events"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]


def d(s):
    return datetime.date.fromisoformat(s)


def range_short(ev):
    if not ev["startDate"]:
        return "TBA", "Dates not announced"
    a, b = d(ev["startDate"]), d(ev["endDate"] or ev["startDate"])
    if a == b:
        main = f"{MONTHS[a.month-1]} {a.day}"
    elif a.month == b.month:
        main = f"{MONTHS[a.month-1]} {a.day}–{b.day}"
    else:
        main = f"{MONTHS[a.month-1]} {a.day}–<wbr>{MONTHS[b.month-1]} {b.day}"
    main = main.replace(" ", "&nbsp;")
    return main, str(a.year) if a.year == b.year else f"{a.year}–{b.year}"


def time_state(ev, today):
    if not ev["startDate"]:
        return "tba"
    if ev["endDate"] < today:
        return "past"
    if ev["startDate"] <= today:
        return "now"
    return "upcoming"


def upcoming(today, n):
    dated = [x for x in EVENTS if x["startDate"] and x["endDate"] >= today]
    return sorted(dated, key=lambda x: x["startDate"])[:n]


# ---------------------------------------------------------------- HOME
def board(today):
    items = []
    for ev in upcoming(today, 4):
        main, yr = range_short(ev)
        items.append(f"""<li><div class="d">{main}<small>{yr}</small></div>
<div><div class="n">{e(ev['name'])}</div><div class="v">{e(ev['venue'])}</div></div></li>""")
    return f"""<aside class="board" aria-labelledby="board-h">
  <h2 id="board-h">Next on the show floor <span>Las Vegas</span></h2>
  <ol id="board-list">{''.join(items)}</ol>
  <a class="more" href="/las-vegas-trade-show-calendar/">See the full trade show calendar</a>
</aside>"""


SERVICES = [
    ("/production-support-labor/", "Production support & labor",
     "Stagehands, LED and AV technicians, and load-in and load-out help that works under your production manager, on your schedule."),
    ("/led-video-wall-rental/", "LED video wall rental",
     "LED walls delivered, built, and run for trade show booths, general sessions, and live events, with a technician on site."),
    ("/led-display-services/", "LED content mapping & repair",
     "Pixel maps and content specs for your designers, plus on-site troubleshooting for dead pixels, failed modules, and signal problems."),
    ("/mobile-stage-rental/", "Mobile stage rental",
     "Staging for outdoor and pop-up events, delivered and set by a crew that can also handle your video and lighting."),
    ("/truss-crank-lift-rental/", "Truss & crank lift rental",
     "Truss, hardware, and crank lifts for ground-supported lighting and signage, with crew for assembly if you need it."),
    ("/led-display-sales-installation/", "LED display sales & installation",
     "Permanent LED displays for venues, retail, and corporate spaces, from site survey to installation and service."),
]


def spec_rows():
    return "\n".join(f"""<div class="spec-row"><h3><a href="{h}">{e(t)}</a></h3><p>{e(dsc)}</p><a class="go" href="{h}" aria-label="{e(t)} details">Details</a></div>"""
                     for h, t, dsc in SERVICES)


def build_home(today):
    title = "Las Vegas Production Support & LED Walls | Saddle Point"
    desc = "Local production partner in Las Vegas for event companies and AV providers: production labor, LED video wall rental and support, staging, truss, and crank lift rental."
    page = head(title, desc, "/", ld(BUSINESS_LD)) + header("/") + f"""
<section class="hero">
  <div class="wrap">
    <div>
      <h1>Your local production partner in Las Vegas</h1>
      <p class="lede">Crew, LED video wall support, and staging equipment for production companies, AV providers, and exhibit houses working trade shows, conventions, and live events in Las Vegas.</p>
      <div class="actions">
        <a class="btn" href="/request-a-quote/">Request a quote</a>
        <a class="btn ghost" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
      </div>
    </div>
    {board(today)}
  </div>
</section>

<section class="photo-strip" aria-label="Photos of the kinds of events we support">
  <div class="wrap">
    {photo("general-session", (3, 2), "(max-width: 760px) 100vw, 33vw")}
    {photo("festival-stage", (3, 2), "(max-width: 760px) 100vw, 33vw")}
    {photo("trade-show", (3, 2), "(max-width: 760px) 100vw, 33vw")}
  </div>
</section>

<section class="block">
  <div class="wrap split">
    <div>
      <h2>We work for the production company, not around it</h2>
    </div>
    <div class="prose">
      <p>When your show lands in Las Vegas and you need extra hands or gear, we fill the gap. We take direction from your production manager or technical director and represent your company on site. We don't pitch your client.</p>
      <p>Tell us the call times, positions, and equipment you need. We'll confirm what we can cover before you commit, and we'll tell you early if a request is outside what we can do well.</p>
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <div class="section-head">
      <h2>What we provide</h2>
      <p class="lede">Rental, labor, and permanent installs are separate services, so you can book exactly the piece you're missing.</p>
    </div>
    <div class="spec">
{spec_rows()}
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap split">
    <div>
      <h2>What to send for a fast quote</h2>
      <p>The more of this we have, the quicker we can confirm availability and price.</p>
    </div>
    <ul class="ticks">
      <li>Show name, venue, and hall or room</li>
      <li>Load-in, show, and load-out dates and times</li>
      <li>Positions and headcount, or the equipment list</li>
      <li>For LED: wall size, pixel pitch if specified, indoor or outdoor, and how it's supported (ground-stacked or flown)</li>
      <li>Venue or show labor rules you already know about</li>
      <li>On-site contact and how you want us to bill</li>
    </ul>
  </div>
</section>
""" + cta_band() + footer(BOARD_JS)
    write("/", page)


BOARD_JS = """<script>
(function(){
  var list=document.getElementById('board-list'); if(!list||!window.fetch) return;
  var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var today=new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles'}).format(new Date());
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  fetch('/data/events.json').then(function(r){return r.json();}).then(function(data){
    var ev=data.events.filter(function(x){return x.startDate && x.endDate>=today;})
      .sort(function(a,b){return a.startDate<b.startDate?-1:1;}).slice(0,4);
    if(!ev.length) return;
    list.innerHTML=ev.map(function(x){
      var a=x.startDate.split('-').map(Number), b=x.endDate.split('-').map(Number), t;
      if(x.startDate===x.endDate) t=M[a[1]-1]+' '+a[2];
      else if(a[1]===b[1]) t=M[a[1]-1]+' '+a[2]+'–'+b[2];
      else t=M[a[1]-1]+' '+a[2]+'–<wbr>'+M[b[1]-1]+' '+b[2];
      t=t.replace(/ /g,'&nbsp;');
      var now=x.startDate<=today?' (on now)':'';
      return '<li><div class="d">'+t+'<small>'+a[0]+'</small></div><div><div class="n">'+esc(x.name)+esc(now)+'</div><div class="v">'+esc(x.venue)+'</div></div></li>';
    }).join('');
  }).catch(function(){});
})();
</script>"""


# ---------------------------------------------------------------- SERVICE PAGES
SERVICE_PHOTOS = {
    "/production-support-labor/": "road-cases",
    "/led-video-wall-rental/": "led-wall",
    "/led-display-services/": "led-closeup",
    "/led-display-sales-installation/": "led-building",
    "/mobile-stage-rental/": "outdoor-stage",
    "/truss-crank-lift-rental/": "truss-lights",
}


def service_page(path, title, desc, h1, lede, body, faqs, related, service_type, parent=None):
    trail = [("Home", "/")]
    if parent:
        trail.append(parent)
    trail.append((h1, path))
    crumbs = " / ".join(f'<a href="{p}">{e(n)}</a>' for n, p in trail[:-1]) + f" / <span>{e(h1)}</span>"
    faq_block, faq_ld = faq_html(faqs)
    svc_ld = ld({"@context": "https://schema.org", "@type": "Service", "name": h1, "serviceType": service_type,
                 "provider": {"@id": SITE + "/#business"}, "areaServed": {"@type": "City", "name": "Las Vegas"},
                 "url": SITE + path, "description": desc})
    rel = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for h, t in related)
    page = head(title, desc, path, crumbs_ld(trail) + svc_ld + faq_ld + ld(BUSINESS_LD)) + header(path) + f"""
{page_head(crumbs, h1, lede, f'<div class="actions"><a class="btn" href="/request-a-quote/?service={urllib.parse.quote(service_type)}">Request a quote</a><a class="btn ghost" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></div>', SERVICE_PHOTOS.get(path))}
{body}
{faq_block}
<section class="block"><div class="wrap"><h2>Related services</h2><ul class="related">{rel}</ul></div></section>
""" + cta_band() + footer()
    write(path, page)


def two(h, left, right_html, alt=False):
    return f"""<section class="block{' alt' if alt else ''}"><div class="wrap split"><div><h2>{h}</h2>{left}</div><div class="prose">{right_html}</div></div></section>"""


def ticks(items):
    return '<ul class="ticks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def build_services():
    service_page(
        "/production-support-labor/",
        "Event Production Labor & AV Crew in Las Vegas | Saddle Point",
        "Production labor and technical assistance for event companies and AV providers in Las Vegas: stagehands, LED and AV techs, and load-in and load-out crew.",
        "Production support & labor in Las Vegas",
        "Extra hands and technical help for production companies and AV providers running shows in Las Vegas. We work under your production manager, on your schedule.",
        two("Where we usually help", "<p>Most calls come from out-of-town production teams who need local crew to fill out a show, or local companies with more work than staff for a week.</p>",
            ticks(["Load-in and load-out for trade show booths, general sessions, and breakouts",
                   "LED wall build, operation, and strike",
                   "AV setup assistance: cabling, displays, and gear prep",
                   "Ground-level truss assembly and equipment staging",
                   "Overnight changeovers and room resets",
                   "Equipment pickup, delivery, and warehouse prep"]))
        + two("How a booking works", "<p>We keep it simple so your team can plan around us.</p>",
              "<p>Send the call sheet or a rough schedule: dates, call times, venue, positions, and who our crew reports to. We confirm the people and hours we can cover, then send a written quote with rates, minimums, and overtime terms.</p>"
              "<p>On site, our crew checks in with your lead and follows your plan. If something on the show looks unsafe or outside our scope, we raise it with your lead first.</p>", alt=True)
        + two("Venue and union rules", "",
              "<p>Las Vegas convention venues and many shows have their own rules about who can do which work, including union jurisdiction and exhibitor-appointed contractor (EAC) paperwork. These rules vary by venue, show, and type of work.</p>"
              "<p>Before we confirm a crew, we'll check the venue and show requirements with you. If a task has to go through the house or show labor, we'll tell you so you can plan for it.</p>"),
        [("Do you supply crew for out-of-town production companies?", "Yes. That's most of our work. We act as your local crew and follow your team's direction."),
         ("How far ahead should we book?", "As early as you have dates. Big convention weeks in Las Vegas fill up, so earlier requests give us the best chance of covering every position."),
         ("Can you work overnight or split calls?", "Often, yes. Include the full schedule in your request and we'll confirm what we can cover."),
         ("Do you handle rigging?", "We handle ground-level truss assembly and equipment staging. For flown rigging, we'll confirm what's allowed at the venue and who's qualified to do it before we agree to anything.")],
        [("/led-video-wall-rental/", "LED video wall rental"), ("/truss-crank-lift-rental/", "Truss & crank lift rental"),
         ("/las-vegas-trade-show-calendar/", "Las Vegas trade show calendar")],
        "Event production labor")

    service_page(
        "/led-video-wall-rental/",
        "LED Video Wall Rental in Las Vegas | Delivery, Setup & Operation",
        "LED video wall and LED screen rental in Las Vegas for trade show booths, conventions, and live events, with delivery, setup, on-site operation, and strike.",
        "LED video wall rental in Las Vegas",
        "LED walls for trade show booths, general sessions, and live events, delivered, built, and run by a technician who stays with the wall.",
        two("What's included", "<p>Every rental quote spells out exactly what's included. Typically:</p>",
            ticks(["LED panels and the frames or ground support to mount them",
                   "Video processing and the cabling to reach your source",
                   "Delivery, build, and strike at the venue",
                   "A technician on site to run the wall and handle problems",
                   "Spare modules for fast swaps during the show"]))
        + two("Tell us about the wall", "<p>These details decide which panels and processing we quote.</p>",
              "<ul><li>Finished size, or the space you need to fill</li><li>Pixel pitch, if your designer has specified one, and the typical viewing distance</li>"
              "<li>Indoor or outdoor, and how many hours a day it runs</li><li>Ground-stacked, on truss, or flown</li><li>Your content source and its resolution</li></ul>"
              "<p>We'll confirm the panel model, pitch, and quantity we can supply for your dates. Need a different spec than we stock? We'll say so instead of quoting something that doesn't fit.</p>", alt=True)
        + two("Content that fits the wall", "",
              '<p>Content built to the wall\'s exact pixel dimensions looks sharper and avoids surprises at the show. We can send your designers a pixel map and content specs ahead of time. See <a href="/led-display-services/">LED content mapping and repair</a>.</p>'),
        [("Do you rent LED walls without a technician?", "We recommend a technician on any show. A wall that fails mid-session costs more than the labor. For simple setups, ask us and we'll look at it case by case."),
         ("Can you support another company's LED wall?", 'Yes. We can build, operate, and troubleshoot walls supplied by others. See <a href="/led-display-services/">LED mapping and repair</a>.'),
         ("What pixel pitch should I use?", "It depends mostly on how close the audience will be and how big the wall is. Send us the room layout and viewing distance and we'll recommend options.")],
        [("/led-display-services/", "LED mapping & repair"), ("/led-display-sales-installation/", "Buy a permanent LED display"),
         ("/production-support-labor/", "Production labor"), ("/event-equipment-rental/", "All equipment rental")],
        "LED video wall rental", parent=("Equipment rental", "/event-equipment-rental/"))

    service_page(
        "/led-display-services/",
        "LED Content Mapping, Troubleshooting & Repair | Las Vegas",
        "LED display content mapping, on-site pixel and module troubleshooting, and LED wall repair in Las Vegas for event walls and permanent displays.",
        "LED content mapping, troubleshooting & repair",
        "Technical LED support for production companies and venues, from pixel maps before the show to fixing a failed module during it.",
        two("Content mapping", "<p>Before the show, we help your content team build for the wall you actually have.</p>",
            ticks(["Pixel maps with exact canvas size and panel layout",
                   "Content specs for designers: resolution, frame rate, safe areas",
                   "Processor setup and scaling, so content lands pixel for pixel",
                   "Test patterns and a check of each content source before doors open"]))
        + two("On-site troubleshooting and repair", "<p>When a wall acts up, we diagnose it on the spot.</p>",
              ticks(["Dead or stuck pixels and failed modules",
                     "Receiving card, data, and power faults",
                     "Color and brightness mismatches between panels",
                     "Signal dropouts between the source, processor, and wall"])
              + "<p>We can stand by during your show or come out for a service call on a wall that's already installed. Tell us the panel brand and model, and we'll say upfront whether we can work on it.</p>", alt=True),
        [("Can you work on a brand of LED panel you didn't supply?", "Often, yes. Send the brand, model, and processor and we'll confirm before scheduling."),
         ("Do you offer standby technicians for a show?", "Yes. A tech can stay with the wall for the run of show and handle problems as they come up.")],
        [("/led-video-wall-rental/", "LED video wall rental"), ("/led-display-sales-installation/", "LED display sales & installation"),
         ("/production-support-labor/", "Production labor")],
        "LED display technical services")

    service_page(
        "/led-display-sales-installation/",
        "LED Display Sales & Installation in Las Vegas | Saddle Point",
        "Permanent LED display sales and installation in Las Vegas for venues, retail, houses of worship, and corporate spaces: site survey, specification, install, and service.",
        "LED display sales & installation",
        "Permanent LED displays for businesses and venues in the Las Vegas area, specified for your space and installed by the team that will service them.",
        """<section class="block"><div class="wrap split"><div><h2>How a project runs</h2><p>Every install goes through the same four steps.</p></div><div class="prose"><ol>
<li><strong>Site visit.</strong> We measure the space and check viewing distances, mounting surfaces, power, and where the signal will come from.</li>
<li><strong>Specification and quote.</strong> We recommend a pixel pitch, size, and brightness, then quote the display, mounting, processing, and labor separately so you can compare.</li>
<li><strong>Installation.</strong> We mount, wire, and set up the display, coordinating with your electrician or general contractor where needed.</li>
<li><strong>Handover and service.</strong> We show your team how to run it and agree on how service calls will work after install.</li></ol></div></div></section>"""
        + two("Good fits", "", ticks(["Lobbies, conference rooms, and event spaces", "Retail storefronts and in-store displays",
                                      "Venues, bars, and restaurants", "Houses of worship", "Exterior signage, subject to local permits"]), alt=True),
        [("Do you handle permits?", "For exterior signs and some electrical work, permits are required. We'll tell you what's likely to be needed and work with your contractor on it."),
         ("Can you replace or upgrade an existing display?", "Yes. Send photos and the current model and we'll start with a site visit.")],
        [("/led-display-services/", "LED repair & service"), ("/led-video-wall-rental/", "Rent an LED wall instead")],
        "LED display installation")

    service_page(
        "/mobile-stage-rental/",
        "Mobile Stage Rental in Las Vegas | Delivery & Setup",
        "Mobile stage rental in Las Vegas for outdoor events, festivals, and pop-ups, with delivery, setup, and optional LED, lighting, and production crew.",
        "Mobile stage rental in Las Vegas",
        "Stages for outdoor events, festivals, and pop-ups, delivered and set by a crew that can also bring your LED wall and production labor.",
        two("Tell us about your event", "<p>Stage options depend on the site as much as the show.</p>",
            ticks(["Event date, setup window, and strike time", "Site address and ground surface (asphalt, grass, sand)",
                   "Deck size and height you need, or the act you're staging", "Whether you need a roof, wings, or a backdrop",
                   "Access for a vehicle and trailer to reach the stage spot"]))
        + two("Permits and site rules", "",
              "<p>Outdoor events in Clark County and Las Vegas may need permits, and many sites have their own rules for wind, power, and vehicle access. Check with your venue or permit office early. We'll share the stage specs your permit application needs.</p>", alt=True),
        [("Can you add an LED wall to the stage?", 'Yes. We can quote the stage, an <a href="/led-video-wall-rental/">LED wall</a>, and crew together.'),
         ("What happens if it's windy?", "Outdoor staging has wind limits. We'll go over the limits for the stage you're renting and agree on a plan before the event.")],
        [("/event-equipment-rental/", "All equipment rental"), ("/led-video-wall-rental/", "LED video wall rental"),
         ("/production-support-labor/", "Production labor")],
        "Mobile stage rental", parent=("Equipment rental", "/event-equipment-rental/"))

    service_page(
        "/truss-crank-lift-rental/",
        "Truss & Crank Lift Rental in Las Vegas | Saddle Point",
        "Truss, clamps, base plates, and crank lift rental in Las Vegas for lighting, signage, and LED support at trade shows and events, with optional assembly crew.",
        "Truss & crank lift rental",
        "Truss, hardware, and crank lifts for ground-supported lighting, signage, and small LED walls, with crew to assemble them if you need it.",
        two("What you can rent", "<p>Tell us what the truss needs to hold and we'll quote the parts.</p>",
            ticks(["Truss sections, corners, and base plates", "Clamps, spigots, pins, and safety hardware",
                   "Crank lifts and stands for lighting and banners", "Ground-supported structures for small LED walls"]))
        + two("Load and safety", "",
              "<p>Every truss setup needs to stay within its rated load and span. Send what's going on the structure (fixtures, signage, LED panels, and their weights) and we'll check it before quoting.</p>"
              "<p>We quote ground-supported systems. For anything flown from the venue ceiling, the venue's rigging rules apply. We'll help you coordinate.</p>", alt=True),
        [("Do you deliver and assemble?", "Yes. You can rent the equipment alone or with a crew to assemble and strike it."),
         ("Can I pick up the equipment myself?", "Ask when you request a quote and we'll confirm pickup times.")],
        [("/event-equipment-rental/", "All equipment rental"), ("/production-support-labor/", "Production labor"),
         ("/led-video-wall-rental/", "LED video wall rental")],
        "Truss and crank lift rental", parent=("Equipment rental", "/event-equipment-rental/"))

    # Equipment hub
    path = "/event-equipment-rental/"
    title = "Event Equipment Rental in Las Vegas | LED Walls, Stages, Truss"
    desc = "Event equipment rental in Las Vegas for production companies: LED video walls, mobile stages, truss, and crank lifts, with delivery, setup, and crew."
    rows = "\n".join(f"""<div class="spec-row"><h3><a href="{h}">{e(t)}</a></h3><p>{e(dsc)}</p><a class="go" href="{h}" aria-label="{e(t)} details">Details</a></div>"""
                     for h, t, dsc in [SERVICES[1], SERVICES[3], SERVICES[4]])
    trail = [("Home", "/"), ("Equipment rental", path)]
    page = head(title, desc, path, crumbs_ld(trail)) + header(path) + f"""
{page_head('<a href="/">Home</a> / <span>Equipment rental</span>', "Event equipment rental in Las Vegas",
           "LED walls, staging, and truss for production companies and event teams, available on its own or with the crew to set it up and run it.",
           '<div class="actions"><a class="btn" href="/request-a-quote/">Request a quote</a></div>', "concert-stage")}
<section class="block"><div class="wrap"><div class="spec">{rows}</div></div></section>
<section class="block alt"><div class="wrap split"><div><h2>Availability and specs</h2></div><div class="prose">
<p>Quantities and models change as gear goes out on shows. Instead of a catalog that may be out of date, we confirm current availability and specs for your dates in writing with every quote.</p>
<p>Not sure what you need? Send a floor plan or a description of the event and we'll suggest options.</p></div></div></section>
""" + cta_band() + footer()
    write(path, page)


# ---------------------------------------------------------------- CALENDAR
CAT_ORDER = ["Automotive", "Construction & manufacturing", "Fashion & retail", "Media, AV & live events",
             "Security & cybersecurity", "Technology", "Other industries"]


def gcal_link(ev):
    a = ev["startDate"].replace("-", "")
    b = (d(ev["endDate"]) + datetime.timedelta(days=1)).isoformat().replace("-", "")
    q = {"action": "TEMPLATE", "text": ev["name"], "dates": f"{a}/{b}",
         "details": f"{ev['description']}\nOfficial site: {ev['officialUrl']}", "location": ev["venue"] + ", Las Vegas, NV"}
    return "https://calendar.google.com/calendar/render?" + urllib.parse.urlencode(q)


def status_tag(ev):
    return {"confirmed": '<span class="tag confirmed">Organizer-confirmed</span>',
            "reported": '<span class="tag reported">Confirm with organizer</span>',
            "unannounced": '<span class="tag">Dates not announced</span>'}[ev["status"]]


def ev_html(ev, today):
    main, yr = range_short(ev)
    st = time_state(ev, today)
    time_tag = {"now": '<span class="tag now">Happening now</span>', "past": '<span class="tag past">Ended</span>'}.get(st, "")
    full = "Not announced"
    if ev["startDate"]:
        a, b = d(ev["startDate"]), d(ev["endDate"])
        full = f"{MONTHS_LONG[a.month-1]} {a.day}, {a.year}" + (f" – {MONTHS_LONG[b.month-1]} {b.day}, {b.year}" if b != a else "")
    notes = f"<dt>Notes</dt><dd>{e(ev['notes'])}</dd>" if ev["notes"] else ""
    cal = ""
    if ev["startDate"]:
        cal = f'<a class="btn small ghost" href="{e(gcal_link(ev))}" rel="noopener">Add to Google Calendar</a><button class="btn small ghost ics" type="button" data-id="{ev["id"]}" hidden>Download .ics</button>'
    status_text = DATA["statusKey"][ev["status"]]
    q = urllib.parse.urlencode({"event": ev["name"]})
    return f"""<details class="ev{' is-past' if st == 'past' else ''}" id="{ev['id']}">
<summary><div class="when">{main}<small>{yr}</small></div><div class="what"><strong>{e(ev['name'])}</strong><span>{e(ev['venue'])}</span></div>
<div class="tags">{time_tag}<span class="tag">{e(ev['category'])}</span>{status_tag(ev)}</div></summary>
<div class="ev-body">
<p>{e(ev['description'])}</p>
<dl><dt>Dates</dt><dd>{full}</dd><dt>Venue</dt><dd>{e(ev['venue'])}</dd><dt>Industry</dt><dd>{e(ev['category'])}</dd>
<dt>Date status</dt><dd>{e(status_text)}</dd><dt>Source</dt><dd><a href="{e(ev['sourceUrl'])}" rel="noopener">{e(ev['sourceLabel'])}</a></dd>
<dt>Last checked</dt><dd>{e(ev['lastVerified'])}</dd>{notes}</dl>
<div class="ev-actions"><a class="btn small" href="{e(ev['officialUrl'])}" rel="noopener">Official event website</a>{cal}</div>
<p class="ev-cta">Working this show? <a href="/request-a-quote/?{q}">Ask about local crew or LED support</a>.</p>
</div></details>"""


def calendar_list_html(today):
    dated = sorted([x for x in EVENTS if x["startDate"] and x["endDate"] >= today], key=lambda x: (x["startDate"], x["name"]))
    groups, out = {}, []
    for ev in dated:
        a = d(ev["startDate"])
        groups.setdefault((a.year, a.month), []).append(ev)
    for (y, m), evs in groups.items():
        out.append(f'<section class="month-group"><h3>{MONTHS_LONG[m-1]} {y}</h3>' + "".join(ev_html(x, today) for x in evs) + "</section>")
    tba = [x for x in EVENTS if not x["startDate"]]
    if tba:
        out.append('<section class="month-group"><h3>Dates not announced yet</h3>' + "".join(ev_html(x, today) for x in tba) + "</section>")
    return "\n".join(out)


def events_ld():
    items = []
    for ev in EVENTS:
        if ev["status"] != "confirmed" or not ev["startDate"]:
            continue
        street, z = VENUE_ADDR.get(ev["venueGroup"], ("", ""))
        addr = {"@type": "PostalAddress", "addressLocality": "Las Vegas", "addressRegion": "NV", "addressCountry": "US"}
        if street:
            addr.update({"streetAddress": street, "postalCode": z})
        items.append({"@type": "Event", "name": ev["name"], "startDate": ev["startDate"], "endDate": ev["endDate"],
                      "eventStatus": "https://schema.org/EventScheduled",
                      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                      "location": {"@type": "Place", "name": ev["venue"], "address": addr},
                      "description": ev["description"], "url": ev["officialUrl"]})
    return ld({"@context": "https://schema.org", "@graph": items})


def build_calendar(today):
    path = "/las-vegas-trade-show-calendar/"
    title = "Las Vegas Trade Show Calendar | Upcoming Conventions & Events"
    desc = "Upcoming Las Vegas trade shows and conventions with dates, venues, industries, and official links, checked against organizer sources. Filter by month, industry, and venue."
    count = len([x for x in EVENTS if x["startDate"]])
    trail = [("Home", "/"), ("Las Vegas trade show calendar", path)]
    page = head(title, desc, path, crumbs_ld(trail) + events_ld()) + header(path) + f"""
{page_head('<a href="/">Home</a> / <span>Las Vegas trade show calendar</span>', "Las Vegas Trade Show Calendar",
           "Plan ahead for upcoming Las Vegas trade shows, conventions, and exhibitions. Explore event dates, venues, industries, and official event resources while preparing your production and equipment requirements.",
           photo_key="trade-show")}

<section class="block" style="padding-top:2rem">
  <div class="wrap">
    <form class="cal-tools" id="cal-tools" role="search" aria-label="Filter trade shows" hidden>
      <div class="search"><label for="f-q">Search by show name</label><input id="f-q" type="search" placeholder="e.g. CES, SEMA, NAB" autocomplete="off"></div>
      <div><label for="f-month">Month</label><select id="f-month"><option value="">All months</option></select></div>
      <div><label for="f-cat">Industry</label><select id="f-cat"><option value="">All industries</option></select></div>
      <div><label for="f-venue">Venue</label><select id="f-venue"><option value="">All venues</option></select></div>
    </form>
    <div class="cal-bar" id="cal-bar" hidden>
      <span id="cal-count" aria-live="polite"></span>
      <span><label><input type="checkbox" id="f-past"> Show past events</label> &nbsp; <button type="button" id="f-reset">Clear filters</button></span>
    </div>
    <p class="legend"><span class="tag confirmed">Organizer-confirmed</span> dates checked on the organizer's site. <span class="tag reported">Confirm with organizer</span> dates published by independent listings only. Always confirm with the organizer before booking travel or labor.</p>
    <div id="cal-list">
{calendar_list_html(today)}
    </div>
  </div>
</section>

<section class="block alt"><div class="wrap split">
  <div><h2>How to use this calendar</h2></div>
  <div class="prose">
    <p>This calendar lists major trade shows and conventions in Las Vegas. Each entry shows the dates, venue, industry, and a link to the official event website. Open any show to see where its dates came from and when we last checked them.</p>
    <p>Show dates are only part of the picture for production teams. Exhibitor move-in and move-out usually start before opening day and run past closing, and each show publishes its own schedule in its exhibitor manual. Big weeks also tighten the market for local crew, rental gear, and hotel rooms, so book early when your show overlaps another large event.</p>
    <p>We update the list as organizers announce new dates. Currently listing {count} dated events. Spot an error or a missing show? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </div>
</div></section>

<section class="block"><div class="wrap">
  <div class="faq">
    <h2>Common questions</h2>
    <details><summary>Where are most Las Vegas trade shows held?</summary><p>The largest shows use the Las Vegas Convention Center, the Venetian Expo, Caesars Forum, and Mandalay Bay Convention Center. Some, like CES and AWS re:Invent, spread across several venues at once.</p></details>
    <details><summary>Are these dates official?</summary><p>Shows marked "Organizer-confirmed" were checked against the organizer's own website or documents. Shows marked "Confirm with organizer" come from independent listings. Either way, check the official site before you book.</p></details>
    <details><summary>Can Saddle Point Productions help with my show?</summary><p>If you're producing, exhibiting at, or supplying a show in Las Vegas, we provide local production labor, LED video wall support, and staging equipment. <a href="/request-a-quote/">Tell us about your show</a>.</p></details>
  </div>
</div></section>
""" + cta_band("Planning production support for a Las Vegas trade show?",
               "Need local AV labor, LED display support, or event equipment? Contact Saddle Point Productions to discuss your project.") + footer('<script src="/assets/js/calendar.js" defer></script>')
    write(path, page)


# ---------------------------------------------------------------- ABOUT
def build_about():
    path = "/about/"
    title = "About Saddle Point Productions | Las Vegas Production Partner"
    desc = "Saddle Point Productions LLC is a Las Vegas company providing production labor, LED display support, and event equipment to production companies and AV providers."
    page = head(title, desc, path, crumbs_ld([("Home", "/"), ("About", path)]) + ld(BUSINESS_LD)) + header(path) + f"""
{page_head('<a href="/">Home</a> / <span>About</span>', "About Saddle Point Productions",
           "We're a Las Vegas production support company. Our job is to make the companies we work for look good on show day.",
           photo_key="vegas-strip")}
<section class="block"><div class="wrap split">
  <div><h2>What we do</h2></div>
  <div class="prose">
    <p>Saddle Point Productions LLC provides production labor, LED video wall rental and support, staging, truss, and crank lifts to event production companies, AV providers, exhibit houses, and event teams working in Las Vegas.</p>
    <p>We're intentionally not a full-service agency. We work as a subcontractor and local vendor. You bring the client and the creative, and we bring local hands and gear for the parts you need.</p>
    <!-- TODO: Add a short founder/team paragraph and one or two real project examples (with permission) once ready. -->
  </div>
</div></section>
<section class="block alt"><div class="wrap split">
  <div><h2>How we work</h2></div>
  {ticks(["We confirm what we can cover in writing before you commit.",
          "Our crew reports to your production lead and follows your show plan.",
          "We tell you early when a request is outside our scope or a venue rule applies.",
          "Every quote lists equipment, labor, and terms clearly."])}
</div></section>
""" + cta_band("Let's talk about your next Las Vegas show") + footer()
    write(path, page)


# ---------------------------------------------------------------- QUOTE
def build_quote():
    path = "/request-a-quote/"
    title = "Request a Quote | Saddle Point Productions, Las Vegas"
    desc = "Request a quote for production labor, LED video wall rental, LED support, staging, truss, crank lift rental, or LED display installation in Las Vegas."
    opts = ["Production labor", "LED video wall rental", "LED content mapping or repair", "Mobile stage rental",
            "Truss or crank lift rental", "LED display sales & installation"]
    checks = "".join(f'<label><input type="checkbox" name="services" value="{e(o)}"> {e(o)}</label>' for o in opts)
    page = head(title, desc, path, crumbs_ld([("Home", "/"), ("Request a quote", path)])) + header(path) + f"""
<section class="page-head"><div class="wrap">
  <p class="crumbs"><a href="/">Home</a> / <span>Request a quote</span></p>
  <h1>Request a quote</h1>
  <p class="lede">Tell us about the show and what you need. We usually reply within one business day. In a hurry? Call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
</div></section>
<section class="block"><div class="wrap">
  <!-- To receive submissions without opening the visitor's email app, set data-endpoint to a form service URL (see README). -->
  <form class="form" id="quote-form" data-endpoint="" novalidate>
    <div class="row">
      <div><label for="q-name">Your name</label><input id="q-name" name="name" required autocomplete="name"></div>
      <div><label for="q-company">Company</label><input id="q-company" name="company" autocomplete="organization"></div>
    </div>
    <div class="row">
      <div><label for="q-email">Email</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
      <div><label for="q-phone">Phone</label><input id="q-phone" name="phone" type="tel" autocomplete="tel"></div>
    </div>
    <fieldset><legend>What do you need?</legend><div class="checks">{checks}</div></fieldset>
    <div class="row">
      <div><label for="q-event">Show or event name</label><input id="q-event" name="event"></div>
      <div><label for="q-venue">Venue <span class="hint">and hall, if known</span></label><input id="q-venue" name="venue"></div>
    </div>
    <div class="row">
      <div><label for="q-start">First day on site <span class="hint">load-in</span></label><input id="q-start" name="start" type="date"></div>
      <div><label for="q-end">Last day on site <span class="hint">load-out</span></label><input id="q-end" name="end" type="date"></div>
    </div>
    <div><label for="q-details">Details <span class="hint">call times, positions, LED size and pitch, equipment list</span></label><textarea id="q-details" name="details"></textarea></div>
    <div class="hp" aria-hidden="true"><label for="q-web">Leave this empty</label><input id="q-web" name="website" tabindex="-1" autocomplete="off"></div>
    <div><button class="btn" type="submit">Send request</button></div>
    <div id="form-status" role="status" aria-live="polite"></div>
  </form>
</div></section>
""" + footer('<script src="/assets/js/quote.js" defer></script>')
    write(path, page)


# ---------------------------------------------------------------- 404 / robots / sitemap
def build_misc():
    page = head("Page not found | Saddle Point Productions", "This page doesn't exist.", "/404") + header("") + """
<section class="page-head"><div class="wrap"><h1>This page doesn't exist</h1>
<p class="lede">The page may have moved when we rebuilt the site. Try one of these instead.</p>
<ul class="related"><li><a href="/">Home</a></li><li><a href="/led-video-wall-rental/">LED video wall rental</a></li>
<li><a href="/production-support-labor/">Production support</a></li><li><a href="/las-vegas-trade-show-calendar/">Trade show calendar</a></li>
<li><a href="/request-a-quote/">Request a quote</a></li></ul></div></section>
""" + footer()
    (PUB / "404.html").write_text(page.replace('<meta name="description"', '<meta name="robots" content="noindex">\n<meta name="description"'), encoding="utf-8")
    (PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    urls = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{BUILD_DATE}</lastmod></url>" for p in PAGES)
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')


if __name__ == "__main__":
    today = BUILD_DATE
    build_home(today)
    build_services()
    build_calendar(today)
    build_about()
    build_quote()
    build_misc()
    print("Built", len(PAGES), "pages into", PUB)
