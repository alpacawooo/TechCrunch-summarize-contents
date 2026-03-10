import unittest
from unittest.mock import patch

from news_bot.collector.rss_collector import NewsArticle
from news_bot.summarizer.news_summarizer import summarize_article


class SummarizerTests(unittest.TestCase):
    @patch("news_bot.summarizer.news_summarizer._call_openai")
    def test_summarize_article_maps_fields(self, mock_call):
        mock_call.return_value = {
            "three_line_summary": ["one", "two", "three"],
            "why_important": "중요한 이유",
            "related_companies": ["NVIDIA"],
            "beneficiary_sectors": ["반도체"],
            "risk_sectors": ["소비재"],
            "time_horizon": "장기 트렌드",
            "insta_hooks": ["h1", "h2", "h3"],
        }
        article = NewsArticle("t", "https://x", "Reuters", "2026", "s", "c")
        summary = summarize_article(article)
        self.assertEqual(summary.time_horizon, "장기 트렌드")
        self.assertEqual(len(summary.three_line_summary), 3)
        self.assertEqual(summary.related_companies, ["NVIDIA"])

    @patch("news_bot.summarizer.news_summarizer._call_openai", side_effect=RuntimeError("boom"))
    def test_summarize_article_fallback_when_openai_fails(self, _mock_call):
        article = NewsArticle("OpenAI and Microsoft expand AI infra", "https://x", "Reuters", "2026", "data center buildout", "")
        summary = summarize_article(article)
        self.assertEqual(len(summary.three_line_summary), 3)
        self.assertEqual(len(summary.insta_hooks), 3)
        self.assertIn("Microsoft", summary.related_companies)


if __name__ == "__main__":
    unittest.main()
