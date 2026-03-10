"""Write summarized news into markdown format."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from news_bot.summarizer.news_summarizer import SummarizedNews


def render_markdown(summaries: Iterable[SummarizedNews]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["# AI / 주식 뉴스 자동 요약", "", f"- 생성 시각: {now}", ""]

    for item in summaries:
        lines.append(f"## {item.title}")
        lines.append(f"출처: {item.link}")
        lines.append("")

        lines.append("### 3줄 요약")
        lines.append(f"- {item.summary_3_lines[0]}")
        lines.append(f"- {item.summary_3_lines[1]}")
        lines.append(f"- {item.summary_3_lines[2]}")
        lines.append("")

        lines.append("### 왜 중요한가")
        lines.append(f"- {item.why_it_matters}")
        lines.append("")

        lines.append("### 투자 포인트")
        companies = ", ".join(item.related_companies) if item.related_companies else "정보 없음"
        beneficiary = ", ".join(item.beneficiary_sectors) if item.beneficiary_sectors else "정보 없음"
        risks = ", ".join(item.risk_sectors) if item.risk_sectors else "정보 없음"
        lines.append(f"- 투자 포인트: {item.investment_point}")
        lines.append(f"- 관련 기업: {companies}")
        lines.append(f"- 수혜 가능 업종: {beneficiary}")
        lines.append(f"- 리스크 가능 업종: {risks}")
        lines.append(f"- 성격: {item.theme_type}")
        lines.append(f"- 중요도: {item.importance_level}")
        lines.append("")

        lines.append("### 인스타 후킹")
        for hook in item.insta_hooks[:3]:
            lines.append(f"- {hook}")
        lines.append("\n---\n")

    return "\n".join(lines).strip() + "\n"


def write_markdown_file(content: str, output_dir: str = "output") -> Path:
    today = datetime.now().strftime("%Y_%m_%d")
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / f"news_{today}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path
