"""Generate investor-focused summaries from filtered news using OpenAI API."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List

from news_bot.collector.rss_collector import NewsArticle


@dataclass
class SummarizedNews:
    title: str
    source: str
    link: str
    published: str
    three_line_summary: List[str]
    investor_point: str
    related_companies: List[str]
    market_impact: str
    insta_hooks: List[str]


def _article_payload(article: NewsArticle) -> str:
    return f"제목: {article.title}\n출처: {article.source}\n요약: {article.summary}\n본문: {article.content}".strip()


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def _call_openai(payload: str, model: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise RuntimeError("openai 패키지가 설치되지 않았습니다. `pip install -r requirements.txt`를 실행하세요.") from exc

    client = OpenAI(api_key=api_key)

    system_prompt = (
        "너는 투자자 관점 뉴스 요약가다. 반드시 한국어 JSON만 출력한다. "
        "스키마: {'three_line_summary':[str,str,str],'investor_point':str,'related_companies':[str],"
        "'market_impact':'낮음|중간|높음','insta_hooks':[str,str,str]}"
    )

    user_prompt = (
        "아래 뉴스 정보를 바탕으로 요약해라.\n"
        "요구사항:\n"
        "1) three_line_summary는 정확히 3줄\n"
        "   - 무슨 일이 있었는지\n"
        "   - 왜 중요한지\n"
        "   - 투자자 관점에서 볼 포인트\n"
        "2) related_companies는 최대 5개\n"
        "3) market_impact는 낮음/중간/높음 중 하나\n"
        "4) insta_hooks는 정확히 3개\n\n"
        f"뉴스:\n{payload}"
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content or "{}"
    return _extract_json(content)


def summarize_article(article: NewsArticle, model: str = "gpt-4o-mini") -> SummarizedNews:
    result = _call_openai(_article_payload(article), model=model)

    three_line_summary = result.get("three_line_summary") or []
    if len(three_line_summary) < 3:
        three_line_summary = (three_line_summary + ["정보 부족", "정보 부족", "정보 부족"])[:3]

    insta_hooks = result.get("insta_hooks") or []
    if len(insta_hooks) < 3:
        insta_hooks = (insta_hooks + ["핵심 포인트 요약", "투자자 관점 체크", "시장 반응 해석"])[:3]

    market_impact = result.get("market_impact", "중간")
    if market_impact not in {"낮음", "중간", "높음"}:
        market_impact = "중간"

    return SummarizedNews(
        title=article.title,
        source=article.source,
        link=article.link,
        published=article.published,
        three_line_summary=three_line_summary,
        investor_point=result.get("investor_point", "실적/가이던스와 밸류에이션 변화를 함께 점검하세요."),
        related_companies=result.get("related_companies", []),
        market_impact=market_impact,
        insta_hooks=insta_hooks,
    )


def summarize_news(articles: List[NewsArticle], model: str = "gpt-4o-mini") -> List[SummarizedNews]:
    return [summarize_article(article, model=model) for article in articles]
