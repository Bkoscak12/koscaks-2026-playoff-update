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

