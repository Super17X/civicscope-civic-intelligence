# CivicScope 2.0 — ZIP-first civic intelligence

**Status:** GitHub/Vercel deployable source, source-grounded research and incremental jurisdiction coverage. CivicScope is an independent, nonpartisan tool; it is not an election authority, legal advice, or a city planning department.

## Available features

- ZIP lookup from Zippopotam.us (approximate city/state **only**; not an address, voting precinct, zoning parcel, or jurisdiction guarantee).
- Optional address-level Census geographic verification using **explicit consent** and a POST to the CivicScope server. The service forwards the address to the U.S. Census Geocoder; raw addresses are not persisted by the app. Census boundary data is **not** an official ballot or property-specific zoning finding.
- Live Federal Register public proposed/final rules, pagination, configurable topic filtering, source and freshness indicators.
- Optional Open States state legislative bills (`OPENSTATES_API_KEY`) and Congress.gov bill search (`CONGRESS_API_KEY`). Missing keys show unavailable coverage rather than invented records.
- NYC **citywide** Zoning Application Portal records from NYC Open Data (initial local adapter; ZIP/parcel mapping not verified), optional NYC Council Legistar API token (`NYC_LEGISTAR_TOKEN`). Other cities get a truthful unsupported-coverage state instead of pretending NYC data is local.
- National election calendar and limited explicitly sourced 2026 New York election events. Exact races, candidates, early voting and polling places must be verified with official local election offices.
- Regulatory history search by RIN, matched proposal/final documents, official full-text paragraph differences between **two specific Federal Register documents** (not an eCFR legal amendment redline).
- Saved documents and topics in browser-local storage, in-session alerts, JSON export, iCalendar (.ics) export for events/deadlines.
- Research assistant using source-grounded Federal Register documents. Extractive fallback requires no model key; optional AI summaries with `OPENAI_API_KEY` use server-side official source snippets and citations.
- Optional email alert infrastructure with PostgreSQL, Resend, opt-in confirmation, unsubscribe links, per-document delivery deduplication and Vercel daily cron. **Not active without server-side secrets, database migration and provider setup.** The cron currently monitors nationwide Federal Register updates only.

## Setup

Deploy the repository root to Vercel with the **Other** framework. `index.html` is the SPA, `app.js` and `v2.js` are the dependency-free client, and `/api` hosts Node 22-compatible serverless functions.

```bash
npm install
npm run check
npm test
# Browser integration (local simulated government responses)
python test/browser_v2.py
```

### Optional server-side environment variables (never publish secrets)

| Variable | Enables |
| --- | --- |
| `OPENSTATES_API_KEY` | State legislation |
| `CONGRESS_API_KEY` | Congress.gov bill samples |
| `NYC_LEGISTAR_TOKEN` | NYC Council's Legistar API |
| `OPENAI_API_KEY` | Model-generated optional source-grounded research answers |
| `OPENAI_MODEL` | Configured model name, default `gpt-4.1-mini` |
| `DATABASE_URL` | PostgreSQL/Neon subscriber storage |
| `RESEND_API_KEY` | Confirmations and optional policy emails |
| `ALERTS_FROM_EMAIL` | Verified Resend sender, e.g. `alerts@yourdomain` |
| `PUBLIC_SITE_URL` | HTTPS production origin for links, e.g. `https://civicscope-github.vercel.app` |
| `CRON_SECRET` | Protected daily cron and subscriber unsubscribe HMAC |

Apply `db/schema.sql` to an authorized PostgreSQL database before activating email. The cron runs daily at 13:00 UTC if configured. It never runs in the browser. Alerts use nationwide documents and are not locally verified.

**Secrets must stay on the server.** Never add keys to `app.js`, `v2.js`, `.env.example` values, GitHub commits, or user-visible results. Configure Vercel encrypted environment variables. Verify sender domain and provider quotas before enabling mail.

## Data sources

- [ZIP — Zippopotam.us](https://api.zippopotam.us/)
- [Federal Register](https://www.federalregister.gov/developers/documentation/api/v1)
- [Census Geocoder](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html)
- [FEC election dates](https://www.fec.gov/introduction-campaign-finance/election-results-and-voting-information/)
- [New York Board of Elections](https://elections.ny.gov/election-information)
- [NYC ZAP projects](https://data.cityofnewyork.us/d/hgx4-8ukb)
- [NYC Council API](https://council.nyc.gov/legislation/api/)
- [Open States](https://docs.openstates.org/api-v3/)
- [Congress.gov](https://api.congress.gov/)

## Important limitations

- U.S. national elections are not a full local election calendar. Official address-specific candidates, ballots, registration cutoffs and polling places require election authority integrations.
- Local coverage starts with NYC citywide zoning applications. Expansion to 50 states, municipalities, local hearings, GIS parcels, school boards and geospatial querying needs additional source adapters, historical storage, licensing assessment and QA.
- Federal Register rules are not the same as currently consolidated law. Use [eCFR](https://www.ecfr.gov/) and official state/local codes for applicable provisions.
- RIN matching and plain-text paragraph difference **do not establish which legal requirements changed**. Legal review and codified text comparison are needed.
- The research assistant grounds answers in recent federal documents; it does not independently verify local legal applicability.
- Local storage does not sync devices. Email subscriptions require external paid/free-tier services, provider policies, sender authentication and production abuse controls. Do not publish a working email subscription form until these have been reviewed.
- API integrations depend on provider uptime, schema, quotas, authentication and permitted reuse. The current tests use mocked upstream responses and do not certify live government API availability.

## Quality and security

```bash
npm run check
npm test
python test/browser_v2.py
```

Input validation, upstream HTTPS host allowlists, URL safety, content escaping, timeouts, strict caching for private lookups, security headers and optional secret isolation are implemented. Still required before large-scale public launch: distributed API abuse/rate limiting, email deliverability tests, monitoring, source audits, database backups, automated vulnerability scanning, WCAG 2.2 manual testing, and actual public endpoint checks.

The SQL source models subscriber consent and deliveries; no personal address is kept by CivicScope. Users should be informed that addresses are sent to the Census government service for lookup when they explicitly agree.
