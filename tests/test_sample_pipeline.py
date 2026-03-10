import unittest
from pathlib import Path
from unittest.mock import patch

from news_bot.collector.rss_collector import collect_from_rss_file
from news_bot.filter.news_filter import filter_important_news
from news_bot.output.markdown_writer import render_markdown
from news_bot.summarizer.news_summarizer import summarize_news


class SamplePipelineTests(unittest.TestCase):
    @patch("news_bot.summarizer.news_summarizer._call_openai")
    def test_pipeline_with_sample_rss_runs_without_network(self, mock_call):
        mock_call.return_value = {
            "summary_3_lines": ["line1", "line2", "line3"],
            "why_it_matters": "중요",
            "investment_point": "포인트",
            "related_companies": ["NVIDIA"],
            "theme_type": "장기 트렌드",
            "importance_level": "높음",
            "beneficiary_sectors": ["반도체"],
            "risk_sectors": ["소비재"],
            "insta_hooks": ["h1", "h2", "h3"],
        }

        sample_path = Path("tests/fixtures/sample_tech.xml")
        collected = collect_from_rss_file(sample_path, source_name="Sample", limit_per_source=10)
        filtered = filter_important_news(collected, top_k=5)
        summarized = summarize_news(filtered.selected)
        markdown = render_markdown(summarized)

        self.assertGreaterEqual(len(collected), 3)
        self.assertGreaterEqual(len(filtered.selected), 1)
        self.assertIn("### 3줄 요약", markdown)
        self.assertIn("### 왜 중요한가", markdown)
        self.assertIn("### 인스타 후킹", markdown)


if __name__ == "__main__":
    unittest.main()
