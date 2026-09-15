"""Slack briefing notifier using structured summarized news payload."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List

import requests

from news_bot.summarizer.news_summarizer import SummarizedNews, summarize_daily_overview

PRIORITY_COMPANIES = {"OpenAI", "NVIDIA", "Microsoft", "Google", "Amazon", "TSMC", "AMD", "ASML", "Meta"}
PRIORITY_KEYWORDS = ["ai 인프라", "반도체", "공급망", "실적", "가이던스", "규제", "투자"]
IMPORTANCE_SCORE = {"높음": 3, "중간": 2, "낮음": 1}


def _score_article(item: SummarizedNews) -> int:
    score = IMPORTANCE_SCORE.get(item.importance_level, 1) * 10

    if PRIORITY_COMPANIES.intersection(set(item.related_companies)):
        score += 5

    combined = f"{item.title} {item.why_it_matters} {item.investment_point}".lower()
    score += sum(1 for key in PRIORITY_KEYWORDS if key in combined)

    if item.theme_type == "장기 트렌드":
        score += 2

    return score


def select_top_briefings(summaries: List[SummarizedNews], max_items: int = 5) -> List[SummarizedNews]:
    sorted_items = sorted(summaries, key=_score_article, reverse=True)
    return sorted_items[:max_items]


def _trim(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return f"{value[:limit]}..."


def _build_briefing_text(summaries: List[SummarizedNews], max_items: int = 5) -> str:
    top = select_top_briefings(summaries, max_items=max_items)
    created = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "[AI / 반도체 뉴스 브리핑]",
        f"생성일: {created}",
        f"총 기사 수: {len(summaries)}",
        "",
    ]

    for index, item in enumerate(top, start=1):
        companies = ", ".join(item.related_companies) if item.related_companies else "정보 없음"
        lines.append(f"{index}) {item.title}")
        lines.append(f"- 핵심 요약: {_trim(item.summary_3_lines[0], 140)}")
        lines.append(f"- 왜 중요한가: {_trim(item.why_it_matters, 160)}")
        lines.append(f"- 투자 포인트: {_trim(item.investment_point, 160)}")
        lines.append(f"- 관련 기업: {_trim(companies, 120)}")
        lines.append(f"- 성격: {item.theme_type}")
        lines.append(f"- 중요도: {item.importance_level}")
        lines.append("")

    lines.append("[오늘의 한줄 총평]")
    lines.append(f"- {summarize_daily_overview(top)}")

    text = "\n".join(lines)
    return _trim(text, 3800)


def _build_blocks(summaries: List[SummarizedNews], max_items: int = 5) -> list[dict]:
    top = select_top_briefings(summaries, max_items=max_items)

    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "AI / 반도체 뉴스 브리핑"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*생성일:* {datetime.now().strftime('%Y-%m-%d')}\n*총 기사 수:* {len(summaries)}",
            },
        },
    ]

    for index, item in enumerate(top, start=1):
        companies = ", ".join(item.related_companies) if item.related_companies else "정보 없음"
        section = (
            f"*{index}) {item.title}*\n"
            f"• 핵심 요약: {_trim(item.summary_3_lines[0], 130)}\n"
            f"• 왜 중요한가: {_trim(item.why_it_matters, 150)}\n"
            f"• 투자 포인트: {_trim(item.investment_point, 150)}\n"
            f"• 관련 기업: {_trim(companies, 110)}\n"
            f"• 성격: {item.theme_type} | 중요도: {item.importance_level}"
        )
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": section}})

    blocks.append(
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*[오늘의 한줄 총평]*\n• {summarize_daily_overview(top)}"},
        }
    )
    return blocks[:50]


def send_news_briefing_to_slack(summaries: List[SummarizedNews], max_items: int = 5) -> bool:
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("[알림] SLACK_WEBHOOK_URL이 없어 Slack 전송을 건너뜁니다.")
        return False

    if not summaries:
        print("[알림] Slack으로 전송할 요약 뉴스가 없어 전송을 건너뜁니다.")
        return False

    payload = {
        "text": _build_briefing_text(summaries, max_items=max_items),
        "blocks": _build_blocks(summaries, max_items=max_items),
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code >= 400:
            print(f"[경고] Slack 전송 실패: {response.status_code} {response.text}")
            return False
    except Exception as exc:  # noqa: BLE001
        print(f"[경고] Slack 전송 중 예외 발생(계속 진행): {exc}")
        return False

    print(f"[완료] Slack 브리핑 전송 성공 (기사 {min(max_items, len(summaries))}건 요약)")
    return True
