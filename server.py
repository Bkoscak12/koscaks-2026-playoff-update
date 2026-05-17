import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NHL_SCORE_URL = "https://api-web.nhle.com/v1/score/now"
NHL_SCORE_DATE_URL = "https://api-web.nhle.com/v1/score/{date}"
NHL_BRACKET_URL = "https://api-web.nhle.com/v1/playoff-series/carousel/20252026"
ESPN_NHL_NEWS_URL = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/news?limit=100"
NEWSAPI_URL = "https://newsapi.org/v2/everything"


class PuckDropHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/score/now":
            self.proxy_json(NHL_SCORE_URL, "NHL scores")
            return

        if path == "/api/score/date":
            date = parse_qs(urlparse(self.path).query).get("date", [""])[0].strip()
            if not date:
                self.send_error(400, "Score date is required")
                return
            self.proxy_json(NHL_SCORE_DATE_URL.format(date=date), f"NHL scores for {date}")
            return

        if path == "/api/bracket":
            self.proxy_json(NHL_BRACKET_URL, "NHL bracket")
            return

        if path == "/api/stories":
            self.proxy_stories()
            return

        if path == "/api/stories/canadiens":
            self.proxy_stories(team_query='("Montreal Canadiens" OR Canadiens OR Montréal OR Montreal OR MTL)')
            return

        if path == "/api/stories/search":
            query = parse_qs(urlparse(self.path).query).get("q", [""])[0].strip()
            self.proxy_story_search(query)
            return

        super().do_GET()

    def proxy_story_search(self, query):
        if not query:
            self.send_error(400, "Search query is required")
            return

        newsapi_key = os.environ.get("NEWSAPI_KEY")
        if newsapi_key:
            params = urlencode(
                {
                    "q": f'(NHL OR hockey OR "Stanley Cup") AND ({query})',
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 20,
                    "apiKey": newsapi_key,
                }
            )
            self.proxy_json(f"{NEWSAPI_URL}?{params}", "NewsAPI story search")
            return

        self.proxy_json(ESPN_NHL_NEWS_URL, "ESPN NHL story search")

    def proxy_stories(self, team_query=None):
        newsapi_key = os.environ.get("NEWSAPI_KEY")
        if newsapi_key:
            params = urlencode(
                {
                    "q": team_query or "NHL OR hockey OR \"Stanley Cup\"",
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": 36,
                    "apiKey": newsapi_key,
                }
            )
            self.proxy_json(f"{NEWSAPI_URL}?{params}", "NewsAPI stories")
            return

        self.proxy_json(ESPN_NHL_NEWS_URL, "ESPN NHL stories")

    def proxy_json(self, url, label):
        try:
            request = Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "PuckDropUltimate/1.0",
                },
            )
            with urlopen(request, timeout=10) as response:
                payload = response.read()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        except HTTPError as error:
            self.send_error(error.code, f"{label} API error: {error.reason}")
        except URLError as error:
            self.send_error(502, f"Could not reach {label} API: {error.reason}")
        except TimeoutError:
            self.send_error(504, f"{label} API request timed out")


if __name__ == "__main__":
    port = int(os.environ.get("PUCKDROP_PORT", "8012"))
    server = ThreadingHTTPServer(("127.0.0.1", port), PuckDropHandler)
    print(f"PuckDrop Ultimate running at http://127.0.0.1:{port}/index.html")
    server.serve_forever()
