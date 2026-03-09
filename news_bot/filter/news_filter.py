"""Filtering logic for selecting investment-relevant AI/market news."""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha1
from typing import Iterable, List

from news_bot.collector.rss_collector import NewsArticle


INDUSTRY_KEYWORDS = [
    "ai",
    "openai",
    "anthropic",
    "nvidia",
    "microsoft",
    "google",
    "amazon",
    "tesla",
    "semiconductor",
    "gpu",
    "llm",
    "data center",
    "ai chip",
    "earnings",
    "guidance",
    "fed",
    "interest rate",
]

MARKET_EVENT_KEYWORDS = [
    "earnings",
    "guidance",
    "forecast",
    "investment",
    "invest",
    "acquisition",
    "merger",
    "m&a",
    "regulation",
    "regulatory",
    "rate",
    "fed",
    "policy",
    "ai launch",
    "chip supply",
    "production",
    "fab",
]


@dataclass
class FilterResult:
    selected: List[NewsArticle]
    duplicate_dropped_count: int
    irrelevant_dropped_count: int
    topk_dropped_count: int

    @property
    def dropped_count(self) -> int:
        return self.duplicate_dropped_count + self.irrelevant_dropped_count + self.topk_dropped_count


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_any_keyword(text: str, keywords: Iterable[str]) -> bool:
    normalized = _normalize_text(text)
    return any(keyword in normalized for keyword in keywords)


def _article_text_payload(article: NewsArticle) -> str:
    return f"{article.title} {article.summary} {article.content}".strip()


def has_industry_signal(article: NewsArticle) -> bool:
    return _contains_any_keyword(_article_text_payload(article), INDUSTRY_KEYWORDS)


def has_market_event_signal(article: NewsArticle) -> bool:
    return _contains_any_keyword(_article_text_payload(article), MARKET_EVENT_KEYWORDS)


def article_priority_score(article: NewsArticle) -> int:
    payload = _normalize_text(_article_text_payload(article))
    industry_hits = sum(1 for kw in INDUSTRY_KEYWORDS if kw in payload)
    event_hits = sum(1 for kw in MARKET_EVENT_KEYWORDS if kw in payload)
    return industry_hits + (event_hits * 2)


def deduplicate_articles(articles: Iterable[NewsArticle]) -> tuple[List[NewsArticle], int]:
    articles_list = list(articles)
    unique_map: dict[str, NewsArticle] = {}

    for article in articles_list:
        stable_key_raw = f"{article.title.lower().strip()}|{article.link.lower().strip()}"
        stable_key = sha1(stable_key_raw.encode("utf-8")).hexdigest()
        if stable_key not in unique_map:
            unique_map[stable_key] = article

    unique_articles = list(unique_map.values())
    duplicate_dropped_count = max(0, len(articles_list) - len(unique_articles))
    return unique_articles, duplicate_dropped_count


def filter_important_news(articles: Iterable[NewsArticle], top_k: int = 15) -> FilterResult:
    deduped, duplicate_dropped_count = deduplicate_articles(articles)

    relevant = [
        article
        for article in deduped
        if has_industry_signal(article) or has_market_event_signal(article)
    ]
    irrelevant_dropped_count = max(0, len(deduped) - len(relevant))

    relevant.sort(key=article_priority_score, reverse=True)
    selected = relevant[:top_k]
    topk_dropped_count = max(0, len(relevant) - len(selected))

    return FilterResult(
        selected=selected,
        duplicate_dropped_count=duplicate_dropped_count,
        irrelevant_dropped_count=irrelevant_dropped_count,
        topk_dropped_count=topk_dropped_count,
    )
