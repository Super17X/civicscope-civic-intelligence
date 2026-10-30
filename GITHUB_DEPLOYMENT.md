# CivicScope GitHub + Vercel deployment

Source: https://github.com/Super17X/civicscope-civic-intelligence.

The project has a static frontend (index.html, styles.css, app.js) and a Vercel serverless endpoint (api/data.js). CI runs Node syntax checks and unit tests on pushes and pull requests.

## Vercel
Import or connect the GitHub repo in the Vercel dashboard, use the repository root as the project root, select Other/framework null, and leave build/output commands empty. Configure OPENSTATES_API_KEY and CONGRESS_API_KEY using Vercel encrypted environment variables only if the additional API coverage is desired. The federal data adapter and ZIP lookup do not need these keys.

## Checks
- npm run check
- npm test
- GET /api/data?action=health should respond with an ok:true JSON body
- GET /api/data?action=zip&zip=10001 should resolve an approximate ZIP location
- GET /api/data?action=policies&topic=housing should return source-labeled documents or a clear upstream error

Data coverage limitations: no guaranteed ZIP-to-voting-district match; national election date is not a complete local ballot; nationwide rules should never be presented as locally applicable without jurisdiction verification.
