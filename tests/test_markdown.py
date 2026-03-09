import unittest

from news_bot.output.markdown_writer import render_markdown
from news_bot.summarizer.news_summarizer import SummarizedNews


class MarkdownTests(unittest.TestCase):
    def test_render_contains_required_sections(self):
        item = SummarizedNews(
            title="Test title",
            source="TechCrunch",
            link="https://example.com",
            published="2026-01-01",
            three_line_summary=["a", "b", "c"],
            investor_point="point",
            related_companies=["NVIDIA", "Microsoft"],
            market_impact="높음",
            insta_hooks=["h1", "h2", "h3"],
        )
        md = render_markdown([item])
        self.assertIn("### 3줄 요약", md)
        self.assertIn("### 투자 포인트", md)
        self.assertIn("### 추가 항목", md)
        self.assertIn("### 인스타 후킹", md)
        self.assertIn("시장 영향도: 높음", md)


if __name__ == "__main__":
    unittest.main()
