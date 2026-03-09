"""Generate investor-focused summaries from filtered news."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from news_bot.collector.rss_collector import NewsArticle
from news_bot.filter.news_filter import INDUSTRY_KEYWORDS, MARKET_EVENT_KEYWORDS


@dataclass
class SummarizedNews:
    title: str
    source: str
    link: str
    published: str
    core_summary_lines: List[str]
    why_important: List[str]
    investor_points: List[str]
    insta_hooks: List[str]


def _extract_hit_keywords(article: NewsArticle, keywords: list[str]) -> list[str]:
    payload = f"{article.title} {article.summary}".lower()
    return [kw for kw in keywords if kw in payload]


def _line_one(article: NewsArticle) -> str:
    return f"무슨 일이 있었나: {article.title} 관련 이슈가 보도되었습니다."


def _line_two(article: NewsArticle) -> str:
    event_hits = _extract_hit_keywords(article, MARKET_EVENT_KEYWORDS)
    if event_hits:
        return f"시장 반응 포인트: {', '.join(event_hits[:3])} 이(가) 실적/밸류에이션 기대에 영향을 줄 수 있습니다."
    return "시장 반응 포인트: 관련 섹터 심리에 영향을 줄 수 있는 뉴스입니다."


def _line_three(article: NewsArticle) -> str:
    industry_hits = _extract_hit_keywords(article, INDUSTRY_KEYWORDS)
    if industry_hits:
        return f"투자자 체크 포인트: {', '.join(industry_hits[:3])} 노출도가 높은 기업들의 후속 코멘트·가이던스를 확인하세요."
    return "투자자 체크 포인트: 해당 이슈가 단기 재료인지 장기 구조 변화인지 구분이 필요합니다."


def _why_important(article: NewsArticle) -> List[str]:
    payload = f"{article.title} {article.summary}".lower()

    ai_impact = "AI 산업 영향: 높음" if any(k in payload for k in ["ai", "openai", "llm", "data center", "gpu"]) else "AI 산업 영향: 간접"
    semi_impact = "반도체 산업 영향: 높음" if any(k in payload for k in ["semiconductor", "chip", "gpu", "fab"]) else "반도체 산업 영향: 제한적"
    bigtech_impact = "빅테크 기업 영향: 높음" if any(k in payload for k in ["microsoft", "google", "amazon", "tesla", "nvidia"]) else "빅테크 기업 영향: 간접"
    macro_impact = "금융시장 영향: 높음" if any(k in payload for k in ["fed", "interest rate", "policy", "guidance", "earnings"]) else "금융시장 영향: 보통"

    return [ai_impact, semi_impact, bigtech_impact, macro_impact]


def _investor_points(article: NewsArticle) -> List[str]:
    payload = f"{article.title} {article.summary}".lower()

    positives = []
    risks = []

    if any(k in payload for k in ["nvidia", "gpu", "data center", "ai chip"]):
        positives.append("AI 인프라 수혜주(예: GPU/서버 밸류체인)에는 긍정적으로 작용할 수 있음")
    if any(k in payload for k in ["regulation", "interest rate", "fed"]):
        risks.append("정책/금리 변수로 밸류에이션 변동성이 확대될 수 있음")
    if any(k in payload for k in ["guidance", "earnings", "forecast"]):
        positives.append("실적/가이던스 재평가로 실적 민감주 중심의 차별화 가능")

    if not positives:
        positives.append("직접 수혜 기업 식별을 위해 공급망·고객사 연결고리 확인 필요")
    if not risks:
        risks.append("헤드라인 대비 실제 실적 기여 시점이 지연될 가능성 점검 필요")

    horizon = "단기 뉴스 + 중기 추적 필요"
    if any(k in payload for k in ["fab", "data center", "policy", "acquisition", "merger"]):
        horizon = "중장기 트렌드로 발전 가능성 높음"

    return [
        f"긍정 가능성: {positives[0]}",
        f"리스크 요인: {risks[0]}",
        f"뉴스 성격: {horizon}",
    ]


def _insta_hooks(article: NewsArticle) -> List[str]:
    base = article.title.replace('"', "")
    return [
        f"'{base}' 뉴스, 진짜 수혜주는 따로 있습니다",
        "AI 투자자라면 오늘 이 한 가지 포인트는 꼭 확인하세요",
        "겉보기 호재인데 주가가 엇갈리는 이유를 3줄로 정리했습니다",
    ]


def summarize_article(article: NewsArticle) -> SummarizedNews:
    return SummarizedNews(
        title=article.title,
        source=article.source,
        link=article.link,
        published=article.published,
        core_summary_lines=[_line_one(article), _line_two(article), _line_three(article)],
        why_important=_why_important(article),
        investor_points=_investor_points(article),
        insta_hooks=_insta_hooks(article),
    )


def summarize_news(articles: List[NewsArticle]) -> List[SummarizedNews]:
    return [summarize_article(article) for article in articles]
