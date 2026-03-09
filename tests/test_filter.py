import unittest

from news_bot.collector.rss_collector import NewsArticle
from news_bot.filter.news_filter import deduplicate_articles, filter_important_news


class FilterTests(unittest.TestCase):
    def test_filter_counts_and_selection(self):
        articles = [
            NewsArticle("NVIDIA beats earnings", "https://a", "Reuters", "2026", "AI chip earnings", ""),
            NewsArticle("NVIDIA beats earnings", "https://a", "Reuters", "2026", "duplicate", ""),
            NewsArticle("Fed interest rate outlook", "https://b", "CNBC", "2026", "fed policy", ""),
            NewsArticle("Sports", "https://c", "CNBC", "2026", "football", ""),
        ]

        result = filter_important_news(articles, top_k=1)
        self.assertEqual(len(result.selected), 1)
        self.assertEqual(result.duplicate_dropped_count, 1)
        self.assertEqual(result.irrelevant_dropped_count, 1)
        self.assertEqual(result.topk_dropped_count, 1)
        self.assertEqual(result.dropped_count, 3)

    def test_deduplicate_accepts_iterable_generator(self):
        articles = (
            article
            for article in [
                NewsArticle("A", "https://a", "S", "2026", "", ""),
                NewsArticle("A", "https://a", "S", "2026", "", ""),
                NewsArticle("B", "https://b", "S", "2026", "", ""),
            ]
        )
        unique, dropped = deduplicate_articles(articles)
        self.assertEqual(len(unique), 2)
        self.assertEqual(dropped, 1)


if __name__ == "__main__":
    unittest.main()
