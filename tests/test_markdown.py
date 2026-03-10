import unittest

from news_bot.summarizer.news_summarizer import SummarizedNews
from news_bot.output.markdown_writer import render_markdown


class MarkdownTests(unittest.TestCase):
    def test_render_contains_required_sections(self):
        item = SummarizedNews(
            title="Test title",
            source="TechCrunch",
            link="https://example.com",
            published="2026-01-01",
            core_summary_lines=["a", "b", "c"],
            why_important=["x"],
            investor_points=["y"],
            insta_hooks=["h1", "h2", "h3"],
        )
        md = render_markdown([item])
        self.assertIn("### 핵심 요약", md)
        self.assertIn("### 왜 중요한 뉴스인가", md)
        self.assertIn("### 투자자 관점 포인트", md)
        self.assertIn("### 인스타 후킹 문장 3개", md)


if __name__ == "__main__":
    unittest.main()
