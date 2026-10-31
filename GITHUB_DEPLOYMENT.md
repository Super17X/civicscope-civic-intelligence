# Publishing CivicScope to its own GitHub repository

Repository name: `civicscope-civic-intelligence`
Owner: `Super17X`

1. Visit https://github.com/new?name=civicscope-civic-intelligence&description=ZIP-based%20civic%20policy%20and%20election%20intelligence
2. Set owner `Super17X`, choose public or private, and **do not initialize** with a README/license or .gitignore. Create the repository.
3. Commit the files in this package to `main` using either the GitHub file uploader or Git CLI. Locally:

   ```bash
   cd civicscope
   git init -b main
   git add .
   git commit -m 'Initial CivicScope application with tests and CI'
   git remote add origin https://github.com/Super17X/civicscope-civic-intelligence.git
   git push -u origin main
   ```

4. In Vercel, import this GitHub repository as a new project, or attach the repo to the existing CivicScope project under Git settings. The site uses static `index.html`, `styles.css`, `app.js` and serverless `api/data.js`. No build command is required.
5. Add optional `CONGRESS_API_KEY` and `OPENSTATES_API_KEY` to Vercel project Environment Variables, **never** to GitHub source code. Redeploy after adding environment variables.
6. Check the production URL and `/api/data?action=health`, then submit a ZIP and verify the Federal Register source is reachable.

GitHub Actions runs syntax and unit tests on pushes and PRs. Deployments only become automatic after linking Vercel to the new GitHub repo.
