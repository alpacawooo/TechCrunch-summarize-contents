import os
import unittest
from unittest.mock import patch

from news_bot.notification.slack_notifier import _build_briefing_text, select_top_briefings, send_news_briefing_to_slack
from news_bot.summarizer.news_summarizer import SummarizedNews


def _item(title: str, importance: str, companies: list[str]) -> SummarizedNews:
    return SummarizedNews(
        title=title,
        source="Reuters",
        link="https://example.com",
        published="2026",
        summary_3_lines=["a", "b", "c"],
        why_it_matters="중요 이유",
        investment_point="투자 포인트",
        related_companies=companies,
        theme_type="장기 트렌드",
        importance_level=importance,
        beneficiary_sectors=["반도체"],
        risk_sectors=["소비재"],
        insta_hooks=["h1", "h2", "h3"],
    )


class SlackNotifierTests(unittest.TestCase):
    def test_select_top_briefings_prioritizes_importance_and_companies(self):
        low = _item("generic", "낮음", [])
        high = _item("NVIDIA earnings", "높음", ["NVIDIA"])
        medium = _item("macro", "중간", [])

        top = select_top_briefings([low, medium, high], max_items=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0].title, "NVIDIA earnings")

    def test_build_briefing_text_contains_required_sections(self):
        text = _build_briefing_text([_item("title1", "높음", ["NVIDIA"])], max_items=3)
        self.assertIn("[AI / 반도체 뉴스 브리핑]", text)
        self.assertIn("총 기사 수: 1", text)
        self.assertIn("[오늘의 한줄 총평]", text)

    def test_send_slack_skips_without_webhook(self):
        with patch.dict(os.environ, {}, clear=True):
            sent = send_news_briefing_to_slack([_item("t", "중간", [])], max_items=3)
            self.assertFalse(sent)


if __name__ == "__main__":
    unittest.main()
