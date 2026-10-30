# CivicScope — ZIP-first civic intelligence

A lightweight, accessible, nonpartisan dashboard that distinguishes **national regulatory information**, **statewide proposed legislation**, and **address-verified local voting jurisdictions**. Built with zero client dependencies and a Vercel Node serverless data adapter. No accounts required.

## Running and publishing

- Deploy this folder as a **Vercel Other** project, without a build command. `index.html` serves the static web app and `api/data.js` serves `/api/data`.
- Set optional server-side environment variables in Vercel project settings: `OPENSTATES_API_KEY` and `CONGRESS_API_KEY`. Do not commit secrets or put them in browser code.
- `npm test` runs unit tests; `npm run check` checks JS syntax. Tests require Node.js >= 20.
- For full development with serverless functions, use `npx vercel dev` once linked to your Vercel project.
- `test/browser_smoke.py` performs browser interactions with **mocked** responses and screenshots; it does not validate real production feed availability. Requires Python Playwright and Chromium.

## Sources and exact coverage

| Feature | Source | Scope | Credential |
| --- | --- | --- | --- |
| ZIP -> city/state | Zippopotam.us | Approximate ZIP geography only | None |
| Latest proposed/final rules | Federal Register JSON API | Nationwide (not ZIP specific) | None |
| Federal general election date | Computed from statutory recurring federal schedule, cross-check with FEC | Nationwide date only | None |
| State bills | Open States / Plural Policy API | Statewide, if configured | OPENSTATES_API_KEY |
| Federal bills | Congress.gov v3 | Nationwide, if configured | CONGRESS_API_KEY |
| Ballots, polling locations, city plans | Official external government resources | User verifies full address/district | Not connected in MVP |

**Important:** A ZIP is not an electoral district, zoning boundary, municipal boundary, or precise point. Do not describe these records as the user's specific ballot or neighborhood's decisions. Data sources can be stale or incomplete. Federal Register feeds show the newest 35 matches per current topic, not every applicable law. Congress.gov results, when enabled, are recent bills filtered by title, not comprehensive semantic search. The Google Civic Information API requires credentials and address information; this release links to official address-based lookups rather than collecting a residence address.

The policy comparison view groups only Federal Register records sharing a Regulation Identifier Number (RIN) and containing both a proposed and final rule in the **currently loaded sample**. It is **not** an automated redline, legal interpretation or guarantee that one rule superseded the other.

Watchlist, ZIP and seen IDs live only in browser `localStorage`. There are no background jobs, accounts, cross-device sync, email or push notifications. Alerts are in-session when a newly fetched item matches a watched topic; avoid calling them real-time notifications.

## Security/operations

- Strict ZIP regex, fixed upstream hosts, limited topic allowlist; server-side API keys only.
- HTML escaping and HTTPS URL checks before rendering externally sourced text.
- Security headers and restrictive content security policy; no user-provided HTML execution.
- 9-second upstream aborts, partial-success source service status, HTTP response caching.
- Production requires additional rate limiting, abuse controls, monitoring, origin source verification, Sentry/telemetry, legal QA, accessibility audit, and tested recoverability.

## Intended development trajectory

1. Data/accuracy: address-to-district lookup after opt-in, city/county adapters for zoning board & school board, actual ballots, official meeting calendars.
2. Watchlists: authenticated database + real scheduled ingestion and opt-in notifications with unsubscribe and audit history.
3. Compare: structured legal effective dates, document revisions, exact-version text diff with citations and human review.
4. Operations: ingestion workers, source adapters with quality scores, data provenance tables, deduplication, automated tests, rate limiting and CI/CD.

## License and disclaimer

Code is provided as an application starter. Check external data-provider terms and attribution requirements. This is not a government site, election authority or legal advice.