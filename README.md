# AI / 주식 뉴스 자동 수집 및 요약 프로젝트

AI / 반도체 / 빅테크 / 매크로 관련 RSS 뉴스를 수집해,
투자 콘텐츠용 요약 markdown을 생성하고 Slack 브리핑까지 자동 전송하는 프로젝트입니다.

기본 파이프라인:

1. RSS 뉴스 수집 (TechCrunch, CNBC, Reuters, Yahoo Finance)
2. 투자 관련 키워드/이벤트 기준 필터링
3. 기사별 요약 생성 (OpenAI API 우선, 실패 시 규칙 기반 fallback)
4. Markdown 파일 저장
5. Slack 브리핑 전송(Webhook 설정 시)

---

## 프로젝트 구조

```text
news_bot/
  collector/
    rss_collector.py
  filter/
    news_filter.py
  summarizer/
    news_summarizer.py
  output/
    markdown_writer.py
  notification/
    slack_notifier.py
  main.py
tests/
  fixtures/
    sample_tech.xml
  test_collector.py
  test_filter.py
  test_markdown.py
  test_sample_pipeline.py
  test_slack_notifier.py
  test_summarizer.py
.github/
  workflows/
    ci-offline.yml
    live-rss-run.yml
    news_bot.yml
requirements.txt
README.md
```

---

## 설치 및 환경변수

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
export OPENAI_API_KEY="your_api_key_here"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
```

---

## 실행

```bash
python3 -m news_bot.main
```

Slack 전송 없이 실행:

```bash
python3 -m news_bot.main --skip-slack
```

---

## 요약 필드(강화)

기사별로 아래 필드를 생성합니다.

- `title`
- `source`
- `summary_3_lines`
- `why_it_matters`
- `investment_point`
- `related_companies`
- `theme_type` (`단기 이슈` / `장기 트렌드`)
- `importance_level` (`낮음` / `중간` / `높음`)

---

## Slack 브리핑 형식

Slack에는 markdown 원문 전체가 아니라, **상위 중요 기사(top 3~5)** 브리핑만 전송합니다.
중요도(`importance_level`) + 핵심 기업(OpenAI/NVIDIA/Microsoft/Google/Amazon/TSMC/AMD/ASML/Meta) + 키워드(실적/가이던스/규제/투자/공급망 등) 기준으로 우선순위를 정렬합니다.

예시:

```text
[AI / 반도체 뉴스 브리핑]
생성일: 2026-03-10
총 기사 수: 5

1) 기사 제목
- 핵심 요약: ...
- 왜 중요한가: ...
- 투자 포인트: ...
- 관련 기업: ...
- 성격: 장기 트렌드
- 중요도: 높음

[오늘의 한줄 총평]
- 오늘은 AI 인프라 투자와 반도체 공급망 이슈가 동시에 부각되며 대형 기술주 중심의 장기 성장 서사가 강화됐다.
```

- 메시지가 길면 자동 truncate 처리합니다.
- Slack Block payload를 사용해 가독성을 높이고, `text` fallback도 함께 보냅니다.

---

## 오늘의 한줄 총평 생성 방식

전체 기사 요약 결과를 바탕으로 아래 신호를 조합해 한 줄 총평을 생성합니다.

- 중요도 높은 기사 개수
- 장기 트렌드 기사 비중
- 핵심 기업 노출 여부(NVIDIA/TSMC 등)

---

## Slack Webhook / GitHub Secrets

1. Slack 앱에서 Incoming Webhook 발급
2. GitHub 저장소 `Settings → Secrets and variables → Actions`
3. 아래 secret 등록
   - `OPENAI_API_KEY`
   - `SLACK_WEBHOOK_URL`

`news_bot.yml`에서 다음과 같이 주입합니다.

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 예외 처리 정책

- OpenAI 키 미설정/호출 실패: 규칙 기반 요약 fallback으로 계속 진행
- Slack Webhook 미설정: Slack 단계만 skip
- Slack 전송 실패: 경고 로그 출력 후 워크플로우 계속 진행

---

## 테스트

```bash
python3 -m unittest discover -s tests -v
```

오프라인 환경에서도 `tests/fixtures/sample_tech.xml` 기반으로 주요 파이프라인을 검증합니다.
