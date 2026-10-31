# CivicScope 2.0 release notes

**What changed:** Census opt-in address geography, NYC ZAP citywide municipal adapter and optional Council adapter, election source calendar, federal rule pagination and research, RIN history and document text comparison, source-grounded assistant, local/calendar/timeline/research screens, watchlist JSON and iCalendar exports, email-alert infrastructure with verification and daily cron, and expanded tests.

**Source boundaries:** Not nationwide local zoning or ballot lookup. NYC ZAP returns citywide records; the UI explicitly says they are not selected-ZIP records. Election detail coverage is intentionally conservative. The research assistant uses sampled nationwide sources. Optional integrations are disabled until keys or database credentials are configured.

**Validation:** `npm run check`, `npm test` (26 tests), and `test/browser_v2.py` (mocked API browser journey and desktop/mobile) pass locally. Live public endpoint and upstream external services must be separately verified after deployment.

**Safe rollout:** Preserve the existing GitHub commit as a rollback point; push all source changes to a feature branch and deploy a preview for inspection before promoting to production, if GitHub's current environment supports branch/preview access. The repository is Git-linked to Vercel, so main publishes automatically.