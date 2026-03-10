"""Generate investor-focused summaries from filtered news."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from news_bot.collector.rss_collector import NewsArticle
from news_bot.filter.news_filter import INDUSTRY_KEYWORDS, MARKET_EVENT_KEYWORDS

def _call_openai(article: NewsArticle) -> dict:
    raise NotImplementedError("OpenAI summarization is not implemented yet.")

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


def _article_payload(article: NewsArticle) -> str:
    return f"{article.title} {article.summary} {article.content}".lower()


def _extract_hit_keywords(article: NewsArticle, keywords: list[str]) -> list[str]:
    payload = _article_payload(article)
    return [kw for kw in keywords if kw in payload]


def _line_one(article: NewsArticle) -> str:
    return f"무슨 일이 있었는지: {article.title} 관련 이슈가 보도되었습니다."


def _line_two(article: NewsArticle) -> str:
    event_hits = _extract_hit_keywords(article, MARKET_EVENT_KEYWORDS)
    if event_hits:
        return f"시장이 왜 반응할 수 있는지: {', '.join(event_hits[:3])} 이(가) 실적/밸류에이션 기대에 영향을 줄 수 있습니다."
    return "시장이 왜 반응할 수 있는지: 관련 섹터 심리와 밸류에이션에 간접 영향을 줄 수 있는 뉴스입니다."


def _line_three(article: NewsArticle) -> str:
    industry_hits = _extract_hit_keywords(article, INDUSTRY_KEYWORDS)
    if industry_hits:
        return f"투자자가 체크할 포인트: {', '.join(industry_hits[:3])} 노출도가 높은 기업들의 후속 코멘트·가이던스를 확인하세요."
    return "투자자가 체크할 포인트: 이슈의 실적 반영 시점(단기/중장기)과 실현 가능성을 구분하세요."


def _why_important(article: NewsArticle) -> List[str]:
    payload = _article_payload(article)

    ai_impact = "AI 산업 영향: 높음" if any(k in payload for k in ["ai", "openai", "llm", "data center", "gpu"]) else "AI 산업 영향: 간접"
    semi_impact = "반도체 산업 영향: 높음" if any(k in payload for k in ["semiconductor", "chip", "gpu", "fab"]) else "반도체 산업 영향: 제한적"
    bigtech_impact = "빅테크 기업 영향: 높음" if any(k in payload for k in ["microsoft", "google", "amazon", "tesla", "nvidia"]) else "빅테크 기업 영향: 간접"
    macro_impact = "금융시장 영향: 높음" if any(k in payload for k in ["fed", "interest rate", "policy", "guidance", "earnings"]) else "금융시장 영향: 보통"

    return [ai_impact, semi_impact, bigtech_impact, macro_impact]


def _investor_points(article: NewsArticle) -> List[str]:
    payload = _article_payload(article)

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
        f"어떤 기업에 긍정적인지: {positives[0]}",
        f"어떤 기업에 리스크인지: {risks[0]}",
        f"단기 뉴스인지 장기 트렌드인지: {horizon}",
    ]


def _insta_hooks(article: NewsArticle) -> List[str]:
    base = article.title.replace('"', "")
    return [
        f"{base}: 엔비디아만 보면 놓치는 이유",
        "AI 투자자라면 이 뉴스는 꼭 봐야 하는 이유",
        "겉으로는 호재인데 시장이 애매하게 반응한 이유",
    ]


def summarize_article(article: NewsArticle) -> SummarizedNews:
    try:
        result = _call_openai(article)

        return SummarizedNews(
            title=result.get("title", article.title),
            source=result.get("source", article.source),
            link=result.get("link", article.link),
            published=result.get("published", article.published),
            core_summary_lines=result.get(
                "core_summary_lines",
                [_line_one(article), _line_two(article), _line_three(article)],
            ),
            why_important=result.get("why_important", _why_important(article)),
            investor_points=result.get("investor_points", _investor_points(article)),
            insta_hooks=result.get("insta_hooks", _insta_hooks(article)),
        )
    except Exception:
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
def summarize_daily_overview(items: List[SummarizedNews]) -> str:
    if not items:
        return "오늘은 공유할 핵심 뉴스가 없습니다."

    titles = [item.title for item in items[:3]]
    return "오늘의 핵심 뉴스: " + " / ".join(titles)
