"""RSS collector for market-relevant news sources."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from typing import Any, Iterable, List

REQUEST_TIMEOUT = 12
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; news-bot/1.0)"}


@dataclass
class NewsArticle:
    title: str
    link: str
    source: str
    published: str
    summary: str
    content: str = ""


DEFAULT_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "Reuters": "https://feeds.reuters.com/reuters/businessNews",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
}


def _format_published(entry: dict[str, Any]) -> str:
    published_parsed = entry.get("published_parsed")
    if not published_parsed:
        return "unknown"

    dt = datetime(*published_parsed[:6])
    return dt.isoformat()


def _clean_text(text: str) -> str:
    try:
        from bs4 import BeautifulSoup
    except ModuleNotFoundError:
        # Fallback when dependency is missing in restricted test/runtime env.
        return unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip())

    without_tags = BeautifulSoup(text or "", "html.parser").get_text(" ", strip=True)
    return unescape(re.sub(r"\s+", " ", without_tags)).strip()


def fetch_article_text(url: str, timeout: int = REQUEST_TIMEOUT) -> str:
    """Fetch and parse article body text from URL.

    This is best-effort: failures return an empty string.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ModuleNotFoundError:
        return ""

    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    article_tag = soup.find("article")
    paragraphs = article_tag.find_all("p") if article_tag else soup.find_all("p")
    text = "\n".join(p.get_text(" ", strip=True) for p in paragraphs if p.get_text(" ", strip=True))
    return text[:5000]


def _entry_to_article(entry: dict[str, Any], source: str, fetch_full_text: bool = False) -> NewsArticle:
    title = _clean_text(entry.get("title", "(no title)"))
    link = entry.get("link", "").strip()
    summary = _clean_text(entry.get("summary", ""))
    published = _format_published(entry)

    content = ""
    if fetch_full_text and link:
        content = fetch_article_text(link)

    return NewsArticle(
        title=title,
        link=link,
        source=source,
        published=published,
        summary=summary,
        content=content,
    )


def collect_from_feed(
    feed_url: str,
    source_name: str,
    limit_per_source: int = 20,
    fetch_full_text: bool = False,
) -> List[NewsArticle]:
    try:
        import feedparser
        import requests
    except ModuleNotFoundError:
        return []

    try:
        response = requests.get(feed_url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
    except requests.RequestException:
        return []

    if getattr(parsed, "bozo", False) and not getattr(parsed, "entries", []):
        return []

    articles: List[NewsArticle] = []
    for entry in parsed.entries[:limit_per_source]:
        article = _entry_to_article(entry, source=source_name, fetch_full_text=fetch_full_text)
        if article.title and article.link:
            articles.append(article)
    return articles


def collect_all(
    feeds: dict[str, str] | None = None,
    limit_per_source: int = 20,
    fetch_full_text: bool = False,
) -> List[NewsArticle]:
    feed_map = feeds or DEFAULT_FEEDS
    all_articles: List[NewsArticle] = []

    for source_name, feed_url in feed_map.items():
        all_articles.extend(
            collect_from_feed(
                feed_url,
                source_name=source_name,
                limit_per_source=limit_per_source,
                fetch_full_text=fetch_full_text,
            )
        )

    return all_articles


def iter_sources(feeds: dict[str, str] | None = None) -> Iterable[tuple[str, str]]:
    for source_name, feed_url in (feeds or DEFAULT_FEEDS).items():
        yield source_name, feed_url
