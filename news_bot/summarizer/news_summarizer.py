"""Generate investor-focused summaries from filtered news using OpenAI API with graceful fallback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib import import_module
from importlib.util import find_spec
from typing import Any, List

from news_bot.collector.rss_collector import NewsArticle

DEFAULT_MODEL = "gpt-4o-mini"


@dataclass
class SummarizedNews:
    title: str
    source: str
    link: str
    published: str
    three_line_summary: List[str]
    why_important: str
    related_companies: List[str]
    beneficiary_sectors: List[str]
    risk_sectors: List[str]
    time_horizon: str
    insta_hooks: List[str]


def _article_payload(article: NewsArticle) -> str:
    return f"제목: {article.title}\n출처: {article.source}\n요약: {article.summary}\n링크: {article.link}\n본문: {article.content}".strip()


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)


def _detect_companies(text: str) -> List[str]:
    company_map = {
        "nvidia": "NVIDIA",
        "microsoft": "Microsoft",
        "google": "Google",
        "alphabet": "Google",
        "amazon": "Amazon",
        "meta": "Meta",
        "apple": "Apple",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "tesla": "Tesla",
        "amd": "AMD",
        "intel": "Intel",
        "tsmc": "TSMC",
    }
    lowered = text.lower()
    found: List[str] = []
    for key, name in company_map.items():
        if key in lowered and name not in found:
            found.append(name)
    return found[:5]


def _rule_based_summary(article: NewsArticle) -> SummarizedNews:
    text = f"{article.title} {article.summary} {article.content}".strip()
    companies = _detect_companies(text)

    if "fed" in text.lower() or "interest rate" in text.lower() or "금리" in text:
        beneficiary = ["은행", "보험", "채권"]
        risks = ["고밸류 성장주"]
        horizon = "단기 이슈"
    elif "semiconductor" in text.lower() or "chip" in text.lower() or "반도체" in text:
        beneficiary = ["반도체", "데이터센터"]
        risks = ["메모리 다운사이클 노출 업종"]
        horizon = "중장기 트렌드"
    else:
        beneficiary = ["AI 인프라", "클라우드"]
        risks = ["마진 압박 기업"]
        horizon = "중기 이슈"

    first = article.summary or article.title
    return SummarizedNews(
        title=article.title,
        source=article.source,
        link=article.link,
        published=article.published,
        three_line_summary=[
            f"{first[:140]}" if first else "핵심 이벤트가 보도되었습니다.",
            "가이던스/수요/정책 변화 가능성이 반영되며 관련 섹터의 밸류에이션에 영향을 줄 수 있습니다.",
            "실적 발표 일정, 추가 공시, 밸류체인 수혜 기업의 주가 반응을 함께 확인하세요.",
        ],
        why_important=(
            "이 뉴스는 AI·반도체·빅테크·매크로 흐름 중 하나와 직접 연결되어 있습니다. "
            "단기 모멘텀뿐 아니라 중장기 이익 추정치 변화로 이어질 수 있어 투자 판단에 중요합니다."
        ),
        related_companies=companies,
        beneficiary_sectors=beneficiary,
        risk_sectors=risks,
        time_horizon=horizon,
        insta_hooks=[
            "엔비디아만 보면 놓치는 이유",
            "이 뉴스가 AI 투자자에게 중요한 이유",
            "겉으론 호재인데 시장은 왜 다르게 볼까",
        ],
    )


def _call_openai(payload: str, model: str) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    if find_spec("openai") is None:
        raise RuntimeError("openai 패키지가 설치되지 않았습니다. `pip install -r requirements.txt`를 실행하세요.")

    OpenAI = import_module("openai").OpenAI
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "너는 투자자 관점 뉴스 요약가다. 반드시 한국어 JSON만 출력한다. "
        "스키마: {'three_line_summary':[str,str,str],'why_important':str,'related_companies':[str],"
        "'beneficiary_sectors':[str],'risk_sectors':[str],'time_horizon':str,'insta_hooks':[str,str,str]}"
    )

    user_prompt = (
        "아래 뉴스 정보를 바탕으로 요약해라. 기사 본문이 없더라도 제목/요약/링크만으로 추론해 작성한다.\n"
        "요구사항:\n"
        "1) three_line_summary는 정확히 3줄\n"
        "   - 무슨 일이 있었는지\n"
        "   - 왜 시장이 반응할 수 있는지\n"
        "   - 투자자가 체크할 포인트\n"
        "2) why_important는 2~3문장\n"
        "3) related_companies는 최대 5개\n"
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


def _from_openai_or_fallback(article: NewsArticle, model: str) -> SummarizedNews:
    try:
        result = _call_openai(_article_payload(article), model=model)
    except Exception:
        return _rule_based_summary(article)

    three_line_summary = result.get("three_line_summary") or []
    if len(three_line_summary) < 3:
        three_line_summary = _rule_based_summary(article).three_line_summary

    insta_hooks = result.get("insta_hooks") or []
    if len(insta_hooks) < 3:
        insta_hooks = _rule_based_summary(article).insta_hooks

    related_companies = result.get("related_companies") or _detect_companies(_article_payload(article))
    beneficiary_sectors = result.get("beneficiary_sectors") or ["AI 인프라", "클라우드"]
    risk_sectors = result.get("risk_sectors") or ["마진 압박 기업"]

    return SummarizedNews(
        title=article.title,
        source=article.source,
        link=article.link,
        published=article.published,
        three_line_summary=three_line_summary[:3],
        why_important=result.get("why_important", "이 뉴스는 실적과 밸류체인 기대를 재평가하게 만드는 핵심 변수입니다."),
        related_companies=related_companies[:5],
        beneficiary_sectors=beneficiary_sectors,
        risk_sectors=risk_sectors,
        time_horizon=result.get("time_horizon", "중기 이슈"),
        insta_hooks=insta_hooks[:3],
    )


def summarize_article(article: NewsArticle, model: str = DEFAULT_MODEL) -> SummarizedNews:
    return _from_openai_or_fallback(article, model=model)


def summarize_news(articles: List[NewsArticle], model: str = DEFAULT_MODEL) -> List[SummarizedNews]:
    return [summarize_article(article, model=model) for article in articles]
