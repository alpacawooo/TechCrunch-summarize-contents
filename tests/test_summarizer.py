import unittest
from unittest.mock import patch

from news_bot.collector.rss_collector import NewsArticle
from news_bot.summarizer.news_summarizer import summarize_article, summarize_daily_overview


class SummarizerTests(unittest.TestCase):
    @patch("news_bot.summarizer.news_summarizer._call_openai")
    def test_summarize_article_maps_fields(self, mock_call):
        mock_call.return_value = {
            "summary_3_lines": ["one", "two", "three"],
            "why_it_matters": "중요한 이유",
            "investment_point": "포인트",
            "related_companies": ["NVIDIA"],
            "theme_type": "장기 트렌드",
            "importance_level": "높음",
            "beneficiary_sectors": ["반도체"],
            "risk_sectors": ["소비재"],
            "insta_hooks": ["h1", "h2", "h3"],
        }
        article = NewsArticle("t", "https://x", "Reuters", "2026", "s", "c")
        summary = summarize_article(article)
        self.assertEqual(summary.theme_type, "장기 트렌드")
        self.assertEqual(summary.importance_level, "높음")
        self.assertEqual(len(summary.summary_3_lines), 3)
        self.assertEqual(summary.related_companies, ["NVIDIA"])

    @patch("news_bot.summarizer.news_summarizer._call_openai", side_effect=RuntimeError("boom"))
    def test_summarize_article_fallback_when_openai_fails(self, _mock_call):
        article = NewsArticle("OpenAI and Microsoft expand AI infra", "https://x", "Reuters", "2026", "data center buildout", "")
        summary = summarize_article(article)
        self.assertEqual(len(summary.summary_3_lines), 3)
        self.assertIn(summary.importance_level, {"중간", "높음", "낮음"})
        self.assertIn("Microsoft", summary.related_companies)

    def test_daily_overview_returns_string(self):
        article = NewsArticle("NVIDIA earnings rise", "https://x", "Reuters", "2026", "earnings guidance", "")
        with patch("news_bot.summarizer.news_summarizer._call_openai", side_effect=RuntimeError("boom")):
            summary = summarize_article(article)
        overview = summarize_daily_overview([summary])
        self.assertTrue(isinstance(overview, str) and len(overview) > 0)


if __name__ == "__main__":
    unittest.main()
