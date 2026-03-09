import unittest
from unittest.mock import patch

from news_bot.collector.rss_collector import NewsArticle
from news_bot.summarizer.news_summarizer import summarize_article


class SummarizerTests(unittest.TestCase):
    @patch("news_bot.summarizer.news_summarizer._call_openai")
    def test_summarize_article_maps_fields(self, mock_call):
        mock_call.return_value = {
            "three_line_summary": ["one", "two", "three"],
            "investor_point": "check guidance",
            "related_companies": ["NVIDIA"],
            "market_impact": "중간",
            "insta_hooks": ["h1", "h2", "h3"],
        }
        article = NewsArticle("t", "https://x", "Reuters", "2026", "s", "c")
        summary = summarize_article(article)
        self.assertEqual(summary.market_impact, "중간")
        self.assertEqual(len(summary.three_line_summary), 3)
        self.assertEqual(summary.related_companies, ["NVIDIA"])


if __name__ == "__main__":
    unittest.main()
