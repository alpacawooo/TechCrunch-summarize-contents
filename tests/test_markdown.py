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
            why_important="핵심 이유",
            related_companies=["NVIDIA", "Microsoft"],
            beneficiary_sectors=["반도체", "데이터센터"],
            risk_sectors=["소비재"],
            time_horizon="장기 트렌드",
            insta_hooks=["h1", "h2", "h3"],
        )
        md = render_markdown([item])
        self.assertIn("### 3줄 요약", md)
        self.assertIn("### 왜 중요한가", md)
        self.assertIn("### 투자 포인트", md)
        self.assertIn("### 인스타 후킹", md)
        self.assertIn("- 관련 기업: NVIDIA, Microsoft", md)
        self.assertIn("- 수혜 가능 업종: 반도체, 데이터센터", md)


if __name__ == "__main__":
    unittest.main()
