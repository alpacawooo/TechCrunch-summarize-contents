"""Write summarized news into markdown format."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from news_bot.summarizer.news_summarizer import SummarizedNews


def _section(title: str) -> str:
    return f"\n### {title}\n"


def render_markdown(summaries: Iterable[SummarizedNews]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# AI / 주식 뉴스 자동 요약",
        "",
        f"- 생성 시각: {now}",
        "",
    ]

    for item in summaries:
        lines.append(f"## {item.title}")
        lines.append("")
        lines.append(f"- 출처: {item.source}")
        lines.append(f"- 발행일: {item.published}")
        lines.append(f"- 링크: {item.link}")
        lines.append("")

        lines.append(_section("핵심 요약"))
        for i, summary_line in enumerate(item.core_summary_lines, start=1):
            lines.append(f"{i}. {summary_line}")

        lines.append(_section("왜 중요한 뉴스인가"))
        for bullet in item.why_important:
            lines.append(f"- {bullet}")

        lines.append(_section("투자자 관점 포인트"))
        for bullet in item.investor_points:
            lines.append(f"- {bullet}")

        lines.append(_section("인스타 후킹 문장 3개"))
        for hook in item.insta_hooks:
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
