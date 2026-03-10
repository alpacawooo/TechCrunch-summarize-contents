import unittest
from pathlib import Path
from unittest.mock import patch

from news_bot.collector.rss_collector import _clean_text, collect_from_feed, collect_from_rss_file


class CollectorTests(unittest.TestCase):
    def test_clean_text_removes_html_tags(self):
        cleaned = _clean_text("<p>Hello <b>AI</b> world</p>")
        self.assertIn("Hello", cleaned)
        self.assertIn("AI", cleaned)
        self.assertNotIn("<b>", cleaned)

    def test_collect_returns_empty_when_dependencies_missing(self):
        with patch.dict("sys.modules", {"requests": None}):
            items = collect_from_feed("https://feed", "Test")
            self.assertEqual(items, [])

    def test_collect_from_local_sample_rss_file(self):
        sample_path = Path("tests/fixtures/sample_tech.xml")
        items = collect_from_rss_file(sample_path, source_name="Sample", limit_per_source=2)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].source, "Sample")
        self.assertIn("NVIDIA", items[0].title)
        self.assertTrue(items[0].link.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
