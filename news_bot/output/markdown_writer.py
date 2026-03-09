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
        lines.append(f"- {item.three_line_summary[0]}")
        lines.append(f"- {item.three_line_summary[1]}")
        lines.append(f"- {item.three_line_summary[2]}")
        lines.append("")

        lines.append("### 투자 포인트")
        lines.append(f"- {item.investor_point}")
        lines.append("")

        lines.append("### 추가 항목")
        companies = ", ".join(item.related_companies) if item.related_companies else "정보 없음"
        lines.append(f"- 관련 기업: {companies}")
        lines.append(f"- 시장 영향도: {item.market_impact}")
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
