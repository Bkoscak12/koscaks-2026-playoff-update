const NHL_SCORE_URL = "https://api-web.nhle.com/v1/score/now";
const NHL_BRACKET_URL = "https://api-web.nhle.com/v1/playoff-series/carousel/20252026";
const ESPN_NHL_NEWS_URL = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/news?limit=100";
const NEWSAPI_URL = "https://newsapi.org/v2/everything";

const jsonHeaders = {
  "Content-Type": "application/json",
  "Cache-Control": "no-store",
  "Access-Control-Allow-Origin": "*"
};

exports.handler = async function handler(event) {
  try {
    const apiPath = getApiPath(event.path);
    const query = event.queryStringParameters || {};

    if (apiPath === "/score/now") {
      return proxyJson(NHL_SCORE_URL, "NHL scores");
    }

    if (apiPath === "/bracket") {
      return proxyJson(NHL_BRACKET_URL, "NHL bracket");
    }

    if (apiPath === "/stories") {
      return proxyStories();
    }

    if (apiPath === "/stories/canadiens") {
      return proxyStories('"Montreal Canadiens" OR Canadiens OR Montréal OR Montreal OR MTL');
    }

    if (apiPath === "/stories/search") {
      const searchQuery = (query.q || "").trim();

      if (!searchQuery) {
        return response(400, { error: "Search query is required" });
      }

      return proxyStorySearch(searchQuery);
    }

    return response(404, { error: "API route not found" });
  } catch (error) {
    return response(500, { error: error.message || "Unexpected API error" });
  }
};

function getApiPath(path) {
  return path
    .replace(/^\/api/, "")
    .replace(/^\/\.netlify\/functions\/api/, "")
    .replace(/^\/?/, "/");
}

async function proxyStorySearch(searchQuery) {
  const newsApiKey = process.env.NEWSAPI_KEY;

  if (newsApiKey) {
    const params = new URLSearchParams({
      q: `(NHL OR hockey OR "Stanley Cup") AND (${searchQuery})`,
      language: "en",
      sortBy: "publishedAt",
      pageSize: "20",
      apiKey: newsApiKey
    });

    return proxyJson(`${NEWSAPI_URL}?${params.toString()}`, "NewsAPI story search");
  }

  return proxyJson(ESPN_NHL_NEWS_URL, "ESPN NHL story search");
}

async function proxyStories(teamQuery) {
  const newsApiKey = process.env.NEWSAPI_KEY;

  if (newsApiKey) {
    const params = new URLSearchParams({
      q: teamQuery || 'NHL OR hockey OR "Stanley Cup"',
      language: "en",
      sortBy: "publishedAt",
      pageSize: "36",
      apiKey: newsApiKey
    });

    return proxyJson(`${NEWSAPI_URL}?${params.toString()}`, "NewsAPI stories");
  }

  return proxyJson(ESPN_NHL_NEWS_URL, "ESPN NHL stories");
}

async function proxyJson(url, label) {
  const upstream = await fetch(url, {
    headers: {
      Accept: "application/json",
      "User-Agent": "PuckDropUltimate/1.0"
    }
  });

  const body = await upstream.text();

  if (!upstream.ok) {
    return response(upstream.status, {
      error: `${label} API error`,
      status: upstream.status,
      body
    });
  }

  return {
    statusCode: 200,
    headers: jsonHeaders,
    body
  };
}

function response(statusCode, body) {
  return {
    statusCode,
    headers: jsonHeaders,
    body: JSON.stringify(body)
  };
}

