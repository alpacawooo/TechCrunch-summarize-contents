# AI / 주식 뉴스 자동 수집 및 요약 프로젝트

AI / 반도체 / 빅테크 / 매크로 관련 RSS 뉴스를 수집해,
투자 콘텐츠용 요약 markdown을 자동 생성하는 프로젝트입니다.

기본 파이프라인:

1. RSS 뉴스 수집 (TechCrunch, CNBC, Reuters, Yahoo Finance)
2. 투자 관련 키워드/이벤트 기준 필터링
3. 기사별 요약 생성 (OpenAI API 우선, 실패 시 규칙 기반 fallback)
4. Markdown 파일 저장

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
  main.py
tests/
  fixtures/
    sample_tech.xml
  test_collector.py
  test_filter.py
  test_markdown.py
  test_sample_pipeline.py
  test_summarizer.py
.github/
  workflows/
    ci-offline.yml
    live-rss-run.yml
requirements.txt
README.md
```

---

## 설치 방법 (Python 3.10+)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### OpenAI API 키 설정

```bash
export OPENAI_API_KEY="your_api_key_here"
```

`.bashrc` 또는 `.zshrc`에 추가하면 매번 재입력하지 않아도 됩니다.

### GitHub Actions Secret 이름

실운영 워크플로우에서 아래 이름으로 등록합니다.

- `OPENAI_API_KEY`

---

## 실행 방법

기본 실행:

```bash
python3 -m news_bot.main
```

본문 크롤링까지 포함(선택):

```bash
python3 -m news_bot.main --fetch-full-text
```

옵션 예시:

```bash
python3 -m news_bot.main --limit-per-source 30 --top-k 20 --output-dir output --fetch-full-text --model gpt-4o-mini
```

출력 파일 예시:

- `output/news_YYYY_MM_DD.md`

---

## 출력 형식

```markdown
## 기사 제목
출처: 기사 링크

### 3줄 요약
- 무슨 일이 있었는지
- 왜 시장이 반응할 수 있는지
- 투자자가 체크할 포인트

### 왜 중요한가
- 이 뉴스가 중요한 이유를 2~3문장으로 설명

### 투자 포인트
- 관련 기업: Microsoft, NVIDIA
- 수혜 가능 업종: 데이터센터, 반도체
- 리스크 가능 업종: ...
- 성격: 장기 트렌드

### 인스타 후킹
- 엔비디아만 보면 놓치는 이유
- 이 뉴스가 AI 투자자에게 중요한 이유
- 겉으론 호재인데 시장은 왜 다르게 볼까
```

---

## API 키가 없거나 API 실패 시 동작

프로그램은 중단되지 않고, 기사 제목/요약/링크 기반의 규칙 요약으로 자동 대체됩니다.

- OpenAI 정상 호출 시: 구조화된 고품질 요약 사용
- `OPENAI_API_KEY` 미설정 시: fallback 요약 사용
- OpenAI 응답 에러/타임아웃 시: fallback 요약 사용

즉, 운영 환경에서 API 문제가 있어도 markdown 생성은 계속됩니다.

---

## 네트워크 제한 환경에서 검증하는 방법

실제 RSS 호출이 어려운 환경(Codex cloud 등)에서도 검증할 수 있도록
`tests/fixtures/sample_tech.xml` 기반 테스트를 제공합니다.

```bash
python3 -m unittest discover -s tests -v
```

---

## GitHub Actions 운영 분리

- `ci-offline.yml`: PR/Push용 테스트 워크플로우(샘플 RSS 기반)
- `live-rss-run.yml`: 스케줄/수동 실운영 워크플로우(실제 RSS + OpenAI)

