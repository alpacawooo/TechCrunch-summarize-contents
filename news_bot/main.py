"""Main entrypoint for AI/stock news automation project."""

from __future__ import annotations

import argparse
import sys

from news_bot.collector.rss_collector import collect_all
from news_bot.filter.news_filter import filter_important_news
from news_bot.output.markdown_writer import render_markdown, write_markdown_file
from news_bot.summarizer.news_summarizer import summarize_news


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI/주식 뉴스 자동 수집 및 요약")
    parser.add_argument("--limit-per-source", type=int, default=20, help="소스별 최대 수집 개수")
    parser.add_argument("--top-k", type=int, default=15, help="최종 선별 뉴스 개수")
    parser.add_argument("--output-dir", default="output", help="마크다운 파일 저장 디렉터리")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        collected = collect_all(limit_per_source=args.limit_per_source)
        filtered_result = filter_important_news(collected, top_k=args.top_k)
        summarized = summarize_news(filtered_result.selected)

        md_content = render_markdown(summarized)
        output_path = write_markdown_file(md_content, output_dir=args.output_dir)
    except RuntimeError as exc:
        print(f"[오류] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print("[완료] 뉴스 수집/필터링/요약/저장이 완료되었습니다.")
    print(f"- 수집 개수: {len(collected)}")
    print(f"- 선별 개수: {len(filtered_result.selected)}")
    print(f"- 제외 개수(중복/비관련 포함): {filtered_result.dropped_count}")
    print(f"- 저장 파일: {output_path}")


if __name__ == "__main__":
    main()
