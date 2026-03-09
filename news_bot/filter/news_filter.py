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
    dropped_count: int


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_any_keyword(text: str, keywords: Iterable[str]) -> bool:
    normalized = _normalize_text(text)
    return any(keyword in normalized for keyword in keywords)


def has_industry_signal(article: NewsArticle) -> bool:
    payload = f"{article.title} {article.summary}"
    return _contains_any_keyword(payload, INDUSTRY_KEYWORDS)


def has_market_event_signal(article: NewsArticle) -> bool:
    payload = f"{article.title} {article.summary}"
    return _contains_any_keyword(payload, MARKET_EVENT_KEYWORDS)


def article_priority_score(article: NewsArticle) -> int:
    payload = _normalize_text(f"{article.title} {article.summary}")
    industry_hits = sum(1 for kw in INDUSTRY_KEYWORDS if kw in payload)
    event_hits = sum(1 for kw in MARKET_EVENT_KEYWORDS if kw in payload)

    # 이벤트 가중치를 조금 더 높여 투자 관련성 우선순위 강화
    return industry_hits + (event_hits * 2)


def deduplicate_articles(articles: Iterable[NewsArticle]) -> List[NewsArticle]:
    unique_map: dict[str, NewsArticle] = {}

    for article in articles:
        stable_key_raw = f"{article.title.lower().strip()}|{article.link.lower().strip()}"
        stable_key = sha1(stable_key_raw.encode("utf-8")).hexdigest()
        if stable_key not in unique_map:
            unique_map[stable_key] = article

    return list(unique_map.values())


def filter_important_news(articles: Iterable[NewsArticle], top_k: int = 15) -> FilterResult:
    deduped = deduplicate_articles(articles)

    selected = [
        article
        for article in deduped
        if has_industry_signal(article) or has_market_event_signal(article)
    ]

    selected.sort(key=article_priority_score, reverse=True)
    selected = selected[:top_k]

    return FilterResult(selected=selected, dropped_count=max(0, len(deduped) - len(selected)))
