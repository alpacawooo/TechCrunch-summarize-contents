"""RSS collector for market-relevant news sources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List



@dataclass
class NewsArticle:
    title: str
    link: str
    source: str
    published: str
    summary: str


DEFAULT_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "https://feeds.reuters.com/reuters/businessNews",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
}


def _format_published(entry: dict) -> str:
    published_parsed = entry.get("published_parsed")
    if not published_parsed:
        return "unknown"

    dt = datetime(*published_parsed[:6])
    return dt.isoformat()


def _entry_to_article(entry: dict, source: str) -> NewsArticle:
    title = entry.get("title", "(no title)").strip()
    link = entry.get("link", "").strip()
    summary = entry.get("summary", "").strip()
    published = _format_published(entry)
    return NewsArticle(title=title, link=link, source=source, published=published, summary=summary)


def collect_from_feed(feed_url: str, source_name: str, limit_per_source: int = 20) -> List[NewsArticle]:
    try:
        import feedparser
    except ModuleNotFoundError as exc:
        raise RuntimeError("feedparser가 설치되지 않았습니다. `pip install -r requirements.txt`를 먼저 실행하세요.") from exc

    parsed = feedparser.parse(feed_url)

    if parsed.bozo:
        # bozo==1 means malformed feed or parsing issue; still try entries if present.
        pass

    articles: List[NewsArticle] = []
    for entry in parsed.entries[:limit_per_source]:
        article = _entry_to_article(entry, source=source_name)
        if article.title and article.link:
            articles.append(article)
    return articles


def collect_all(feeds: dict[str, str] | None = None, limit_per_source: int = 20) -> List[NewsArticle]:
    feed_map = feeds or DEFAULT_FEEDS
    all_articles: List[NewsArticle] = []

    for source_name, feed_url in feed_map.items():
        all_articles.extend(collect_from_feed(feed_url, source_name=source_name, limit_per_source=limit_per_source))

    return all_articles


def iter_sources(feeds: dict[str, str] | None = None) -> Iterable[tuple[str, str]]:
    for source_name, feed_url in (feeds or DEFAULT_FEEDS).items():
        yield source_name, feed_url
