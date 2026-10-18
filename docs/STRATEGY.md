# Saddle Point Productions — website strategy notes

Prepared October 18, 2026.

## 1. Audit of the previous site

These findings come from the GitHub repo. The live site blocked automated access, so it couldn't be checked directly.

| Area | Finding | Fixed in rebuild |
|---|---|---|
| Content | Homepage contained template filler: a "Lorem ipsum" test block, four placeholder posts dated 2017, and dead pagination | Removed |
| Positioning | Copy targeted consumers (weddings) rather than production companies | Rewritten for B2B subcontracting |
| Titles / meta | Title was "Saddle Point Overview"; no meta descriptions | Unique title and description on every page |
| Headings | H1 read "We Offer Entertainment Equipment and Services" | One descriptive H1 per page |
| URLs | `generic.html` and `elements.html` (template names) | Descriptive URLs; old URLs 301-redirect |
| Crawling | No robots.txt, sitemap, canonical tags, or structured data | All added |
| Images | Template stock photos and manufacturer product shots; 10 MB video and 3.4 MB image | Removed; only the logo is used (optimized) |
| Accessibility | Viewport blocked pinch-zoom; no skip link | Fixed |
| Trust | Template author credit in footer; out-of-state phone number | Removed; 702 number used |

**Needs your access to check:** Google Search Console (indexing, existing queries, backlinks), analytics, Cloudflare bot and robots settings, and Core Web Vitals once live. The old pages carried little content, so ranking loss risk from the URL change is low, and the redirects cover it anyway.

## 2. Keyword research and page map

**No search volume tool was available.** Volumes below are not verified figures. "Intent" and "Feasibility" are qualitative judgments. Once the site is live, validate them with Google Keyword Planner and, after a few weeks, your own Search Console queries.

| Keyword group | Intent | Commercial value | Feasibility for a new local site | Target page |
|---|---|---|---|---|
| event production labor / AV labor / stagehands Las Vegas | Hire crew | High: matches the core business | Medium. Competing with staffing agencies and union locals | /production-support-labor/ |
| trade show production support Las Vegas | Hire support | High | Medium | /production-support-labor/ |
| LED video wall rental / LED screen rental Las Vegas | Rent | High | Low–medium. Crowded with established AV rental companies | /led-video-wall-rental/ |
| LED display setup, mapping, technical support | Hire tech | Medium | Medium–high. Fewer pages target it specifically | /led-display-services/ |
| LED display repair / LED wall repair Las Vegas | Service call | Medium | Medium–high | /led-display-services/ |
| mobile stage rental Las Vegas | Rent | Medium | Medium | /mobile-stage-rental/ |
| truss rental / crank lift rental Las Vegas | Rent | Medium | Medium–high | /truss-crank-lift-rental/ |
| event equipment rental Las Vegas | Browse | Medium (broad) | Low. Party rental sites dominate | /event-equipment-rental/ (hub) |
| LED display installation / LED sign Las Vegas | Buy | High per project | Medium. Competes with sign companies | /led-display-sales-installation/ |
| Las Vegas trade show calendar / trade shows this month / upcoming conventions / trade shows by industry | Research | Indirect: brings in exhibitors and production teams | Medium. Established calendars exist, so win on accuracy, sourcing, and filters | /las-vegas-trade-show-calendar/ |

**Rules for the map:** each page targets one intent. Rental, labor, and permanent install are kept separate so they don't compete with each other. The equipment hub links down to specific rental pages rather than trying to rank for each one.

## 3. Site architecture

```
/                                   Home: positioning, services, next shows
├─ /production-support-labor/       Labor & technical assistance
├─ /event-equipment-rental/         Rental hub
│   ├─ /led-video-wall-rental/
│   ├─ /mobile-stage-rental/
│   └─ /truss-crank-lift-rental/
├─ /led-display-services/           Content mapping, troubleshooting, repair
├─ /led-display-sales-installation/ Permanent installs (separate journey)
├─ /las-vegas-trade-show-calendar/  Calendar (indexable, filterable)
├─ /about/
└─ /request-a-quote/                Prefills from calendar and service links
```

**Not built yet, on purpose:**

- **Individual trade show pages** (e.g. `/las-vegas-trade-show-calendar/ces/`). Each one is only worth adding with original content, such as move-in timing from the exhibitor manual, venue notes, and production tips. Thin "name + dates" pages risk being treated as low quality. Start with 2–3 shows that matter most to your clients (likely CES, NAB, SEMA, LDI).
- **Guides and resources.** Useful first topics:
  - Choosing LED pixel pitch for a trade show booth
  - What to send a local crew before load-in
  - How Las Vegas venue labor rules affect out-of-town production teams

  Write these once you can add real experience.

## 4. Trade show calendar

The calendar has 19 entries: 18 with dates (November 2026 – April 2028) and 1 marked "dates not announced" (SEMA 2027).

**Organizer-confirmed (13):**
- SEMA 2026
- AAPEX 2026
- LDI 2026
- CES 2027
- World of Concrete 2027
- SHOT Show 2027
- NAB 2027
- CinemaCon 2027
- HD Expo 2027
- JCK 2027
- Black Hat USA 2027
- PACK EXPO Las Vegas 2027
- NAB 2028

**Reported (5):** AWS re:Invent 2026, MJBizCon 2026, MAGIC (February 2027), ISC West 2027, and AAPEX 2027. Their dates are consistent across several independent listings, but no organizer page was found yet. Recheck these first.

**Corrections found during verification:**
- **LDI 2027 moves to New Orleans** (October 15–21, 2027), so it was removed. LDI 2026 is still in Las Vegas.
- **HD Expo 2027** runs May 3–5 (expo hall May 4–5), per the organizer. Many aggregator sites still show May 4–6.
- **InfoComm 2027** is in Orlando, so it isn't listed.

**Structured data:** Google event markup is added only for organizer-confirmed shows.

**Worth adding next (verify each first):** G2E, IMEX America (both October 2026, likely past by launch), Licensing Expo, National Hardware Show, WasteExpo, ASD Market Week, Cosmoprof North America, and the August MAGIC.

## 5. Before launch: please verify or supply

The site avoids claims that haven't been verified. These would strengthen it once confirmed:

1. **Address.** Done: the site shows only "Las Vegas, NV 89123", with no street address. Set your Google Business Profile up as a service-area business and hide the street address there too, so the listings match.
2. **Insurance and licensing.** If you carry general liability or workers' comp, or hold a Nevada / Clark County business license, add a line to About. Production companies often ask for a COI.
3. **Inventory specs.** Panel models, pixel pitches, quantities, stage sizes, and truss types. The site currently says "we confirm specs with every quote."
4. **Photos.** Real photos of your crew, gear, and past setups (with client permission) are the single biggest credibility upgrade available. There are natural places for them on each service page.
5. **Project history.** Even two or three short, permission-cleared examples on About would help.
6. **Response time.** The site says "usually within one business day." Change it if that's not realistic.
7. **Social links.** The footer links Instagram and Facebook. Your personal LinkedIn was removed from the main nav. Consider a company LinkedIn page.

## 6. After launch

- Create or claim the Google Business Profile with the same name, phone, and website as the site.
- Submit the sitemap in Search Console and Bing Webmaster Tools.
- Ask satisfied production clients for a Google review.
- Recheck "reported" calendar entries monthly.
