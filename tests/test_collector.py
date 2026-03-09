import unittest
from unittest.mock import patch

from news_bot.collector.rss_collector import _clean_text, collect_from_feed


class CollectorTests(unittest.TestCase):
    def test_clean_text_removes_html_tags(self):
        cleaned = _clean_text("<p>Hello <b>AI</b> world</p>")
        self.assertIn("Hello", cleaned)
        self.assertIn("AI", cleaned)
        self.assertNotIn("<b>", cleaned)

    def test_collect_returns_empty_when_dependencies_missing(self):
        with patch.dict("sys.modules", {"feedparser": None, "requests": None}):
            items = collect_from_feed("https://feed", "Test")
            self.assertEqual(items, [])


if __name__ == "__main__":
    unittest.main()
