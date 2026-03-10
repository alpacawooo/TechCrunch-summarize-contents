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
    summary_3_lines: List[str]
    why_it_matters: str
    investment_point: str
    related_companies: List[str]
    theme_type: str
    importance_level: str
    beneficiary_sectors: List[str]
    risk_sectors: List[str]
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
        "openai": "OpenAI",
        "nvidia": "NVIDIA",
        "microsoft": "Microsoft",
        "google": "Google",
        "alphabet": "Google",
        "amazon": "Amazon",
        "tsmc": "TSMC",
        "amd": "AMD",
        "asml": "ASML",
        "meta": "Meta",
        "apple": "Apple",
        "intel": "Intel",
        "anthropic": "Anthropic",
    }
    lowered = text.lower()
    found: List[str] = []
    for key, name in company_map.items():
        if key in lowered and name not in found:
            found.append(name)
    return found[:6]


def _rule_based_summary(article: NewsArticle) -> SummarizedNews:
    text = f"{article.title} {article.summary} {article.content}".strip()
    lowered = text.lower()
    companies = _detect_companies(text)

    has_key_player = bool({"OpenAI", "NVIDIA", "Microsoft", "Google", "Amazon", "TSMC", "AMD", "ASML", "Meta"}.intersection(companies))
    has_market_event = any(k in lowered for k in ["earnings", "guidance", "regulation", "investment", "supply", "실적", "가이던스", "규제", "투자", "공급"])

    if "fed" in lowered or "interest rate" in lowered or "금리" in text:
        theme_type = "단기 이슈"
        beneficiary = ["은행", "보험", "채권"]
        risks = ["고밸류 성장주"]
    elif any(k in lowered for k in ["semiconductor", "chip", "반도체", "ai infra", "data center", "공급망"]):
        theme_type = "장기 트렌드"
        beneficiary = ["반도체", "데이터센터", "AI 인프라"]
        risks = ["공급망 병목 노출 업종"]
    else:
        theme_type = "단기 이슈"
        beneficiary = ["AI 인프라", "클라우드"]
        risks = ["마진 압박 기업"]

    if has_key_player and has_market_event:
        importance = "높음"
    elif has_key_player or has_market_event:
        importance = "중간"
    else:
        importance = "낮음"

    first = article.summary or article.title
    return SummarizedNews(
        title=article.title,
        source=article.source,
        link=article.link,
        published=article.published,
        summary_3_lines=[
            first[:160] if first else "핵심 이벤트가 보도되었습니다.",
            "수요/정책/실적 기대치 변화가 관련 종목의 멀티플 재평가로 이어질 수 있습니다.",
            "다음 분기 가이던스와 밸류체인 수혜 기업 실적 신호를 함께 점검하세요.",
        ],
        why_it_matters=(
            "이 뉴스는 AI·반도체·빅테크·매크로 흐름과 연결돼 있습니다. "
            "단기 뉴스로 끝날지, 실적 추정치 상향으로 이어질지 판단에 중요합니다."
        ),
        investment_point="실적/가이던스 발표 일정과 CAPEX, 공급망 지표를 함께 보며 포지션을 조정할 필요가 있습니다.",
        related_companies=companies,
        theme_type=theme_type,
        importance_level=importance,
        beneficiary_sectors=beneficiary,
        risk_sectors=risks,
        insta_hooks=[
            "엔비디아만 보면 놓치는 이유",
            "이 뉴스가 AI 투자자에게 중요한 이유",
            "겉으론 호재인데 시장은 왜 다르게 볼까",
        ],
    )


def summarize_daily_overview(summaries: List[SummarizedNews]) -> str:
    if not summaries:
        return "오늘은 유의미한 AI/반도체 뉴스가 제한적이었습니다."

    high = sum(1 for s in summaries if s.importance_level == "높음")
    long_term = sum(1 for s in summaries if s.theme_type == "장기 트렌드")
    company_hits = {c for s in summaries for c in s.related_companies}

    if high >= 2 and long_term >= 1:
        return "오늘은 AI 인프라 투자와 반도체 공급망 이슈가 동시에 부각되며 대형 기술주 중심의 장기 성장 서사가 강화됐습니다."
    if "NVIDIA" in company_hits or "TSMC" in company_hits:
        return "오늘 흐름은 반도체 밸류체인 핵심 기업 중심으로 수요 기대와 실적 가시성이 재평가되는 국면입니다."
    return "오늘은 개별 이벤트가 혼재했지만, AI·빅테크 관련 실적 기대와 정책 변수 점검이 핵심 포인트였습니다."


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
        "스키마: {'summary_3_lines':[str,str,str],'why_it_matters':str,'investment_point':str,'related_companies':[str],"
        "'theme_type':'단기 이슈|장기 트렌드','importance_level':'낮음|중간|높음',"
        "'beneficiary_sectors':[str],'risk_sectors':[str],'insta_hooks':[str,str,str]}"
    )

    user_prompt = (
        "아래 뉴스 정보를 바탕으로 요약해라. 본문이 없어도 제목/요약/링크 기반으로 작성한다.\n"
        "요구사항:\n"
        "1) summary_3_lines는 정확히 3줄(무슨 일이 있었는지/왜 시장이 반응할 수 있는지/투자자가 체크할 포인트)\n"
        "2) why_it_matters는 2~3문장\n"
        "3) investment_point는 1~2문장\n"
        "4) theme_type은 '단기 이슈' 또는 '장기 트렌드'\n"
        "5) importance_level은 '낮음/중간/높음' 중 하나\n"
        "6) related_companies는 최대 6개\n"
        "7) insta_hooks는 정확히 3개\n\n"
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
    fallback = _rule_based_summary(article)
    try:
        result = _call_openai(_article_payload(article), model=model)
    except Exception:
        return fallback

    summary_3_lines = result.get("summary_3_lines") or fallback.summary_3_lines
    if len(summary_3_lines) < 3:
        summary_3_lines = fallback.summary_3_lines

    insta_hooks = result.get("insta_hooks") or fallback.insta_hooks
    if len(insta_hooks) < 3:
        insta_hooks = fallback.insta_hooks

    theme_type = result.get("theme_type", fallback.theme_type)
    if theme_type not in {"단기 이슈", "장기 트렌드"}:
        theme_type = fallback.theme_type

    importance_level = result.get("importance_level", fallback.importance_level)
    if importance_level not in {"낮음", "중간", "높음"}:
        importance_level = fallback.importance_level

    return SummarizedNews(
        title=article.title,
        source=article.source,
        link=article.link,
        published=article.published,
        summary_3_lines=summary_3_lines[:3],
        why_it_matters=result.get("why_it_matters", fallback.why_it_matters),
        investment_point=result.get("investment_point", fallback.investment_point),
        related_companies=(result.get("related_companies") or fallback.related_companies)[:6],
        theme_type=theme_type,
        importance_level=importance_level,
        beneficiary_sectors=result.get("beneficiary_sectors") or fallback.beneficiary_sectors,
        risk_sectors=result.get("risk_sectors") or fallback.risk_sectors,
        insta_hooks=insta_hooks[:3],
    )


def summarize_article(article: NewsArticle, model: str = DEFAULT_MODEL) -> SummarizedNews:
    return _from_openai_or_fallback(article, model=model)


def summarize_news(articles: List[NewsArticle], model: str = DEFAULT_MODEL) -> List[SummarizedNews]:
    return [summarize_article(article, model=model) for article in articles]
