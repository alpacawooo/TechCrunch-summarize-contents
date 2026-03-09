# AI / 주식 뉴스 자동 수집 및 요약 프로젝트

초보자도 실행할 수 있도록 만든 **RSS 기반 뉴스 봇**입니다.

아래 흐름을 자동으로 실행합니다.

1. RSS 뉴스 수집 (TechCrunch, CNBC, Reuters, Yahoo Finance)
2. 투자 관련 키워드/이벤트 기준 필터링
3. 투자자 관점 요약 생성
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

> 참고: 현재 코드의 핵심 로직은 `feedparser`를 중심으로 동작하며, `requests`, `beautifulsoup4`는 추후 본문 크롤링 확장 시 사용할 수 있도록 요구사항에 포함해두었습니다.

---

## 실행 방법

기본 실행:

```bash
python3 -m news_bot.main
```

옵션 예시:

```bash
python3 -m news_bot.main --limit-per-source 30 --top-k 20 --output-dir output
```

실행하면 아래 형식의 파일이 생성됩니다.

- `output/news_YYYY_MM_DD.md`

예)

- `output/news_2026_03_09.md`

---

## 필터링 기준

### 1) 산업 키워드

- AI, OpenAI, Anthropic, NVIDIA, Microsoft, Google, Amazon, Tesla
- Semiconductor, GPU, LLM, Data center, AI chip
- earnings, guidance, Fed, interest rate

### 2) 시장 영향 이벤트

- 실적 발표, 가이던스 변경
- 대규모 투자, 인수합병(M&A)
- 규제 변화, 금리 정책
- AI 기술 발표, 반도체 공급 변화

### 3) 중복 제거

- 제목 + 링크를 기반으로 해시를 생성해 중복 뉴스 제거

---

## 출력 형식

각 뉴스는 아래 구조로 저장됩니다.

- 기사 제목
- 출처
- 핵심 요약 (3줄)
  1. 무슨 일이 있었는지
  2. 시장이 왜 반응할 수 있는지
  3. 투자자가 체크할 포인트
- 왜 중요한 뉴스인가
  - AI 산업 영향
  - 반도체 산업 영향
  - 빅테크 기업 영향
  - 금융시장 영향
- 투자자 관점 포인트
- 인스타 후킹 문장 3개

---

## 향후 확장 아이디어

현재 구조는 다음 기능을 쉽게 추가할 수 있도록 모듈화되어 있습니다.

- OpenAI API 요약
- Notion 저장
- Telegram 알림
- 인스타 콘텐츠 자동 생성 강화

확장 위치 예시:

- `summarizer/news_summarizer.py`: LLM 요약 추가
- `output/`: Notion/Telegram writer 추가
- `main.py`: 실행 파이프라인에 후처리 단계 연결

---

## 빠른 실행 체크리스트

1. `python3 --version`으로 3.10 이상 확인
2. 가상환경 생성/활성화
3. `pip install -r requirements.txt`
4. `python3 -m news_bot.main`
5. `output/news_YYYY_MM_DD.md` 파일 확인
