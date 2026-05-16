# Koscak's 2026 Playoff Update

Live NHL playoff update page with scores, standings, a headline ticker, Canadiens-focused stories on the Scores page, and broader NHL headlines in the Latest Headlines section.

## Run Locally

```bash
python3 server.py
```

Then open:

```text
http://localhost:8012/index.html
```

## Notes

The app uses a local Python proxy for NHL and hockey news data. A static GitHub Pages link can show the HTML, but it cannot run `server.py`, so live feeds may not work reliably there. For a permanent public live app, deploy this repository to a host that can run the Python server.

## Deploy On Netlify

This repo is ready for Netlify.

1. Create a new Netlify site from the GitHub repository.
2. Use the default build settings. No build command is required.
3. Publish directory: `.`
4. Functions directory: `netlify/functions`

The `netlify.toml` file routes `/api/*` requests to the Netlify Function, so the browser can keep using the same live API paths:

- `/api/score/now`
- `/api/bracket`
- `/api/stories`
- `/api/stories/canadiens`
- `/api/stories/search?q=team`

Optional: add a `NEWSAPI_KEY` environment variable in Netlify if you want NewsAPI-powered story search. Without it, the app uses the ESPN NHL feed.
