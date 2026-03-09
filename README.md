# AI / 주식 뉴스 자동 수집 및 요약 프로젝트

초보자도 실행할 수 있도록 만든 **RSS 기반 뉴스 봇**입니다.

아래 흐름을 자동으로 실행합니다.

1. RSS 뉴스 수집 (TechCrunch, CNBC, Reuters, Yahoo Finance)
2. 투자 관련 키워드/이벤트 기준 필터링
3. OpenAI API 기반 요약 생성
4. Markdown 파일 저장

- 네트워크/프록시 이슈로 특정 RSS가 실패하면 해당 소스는 자동으로 건너뛰고 나머지 소스로 계속 진행합니다.

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

`.bashrc` 또는 `.zshrc`에 추가해두면 매번 입력하지 않아도 됩니다.

### 프록시 환경에서 설치가 403으로 실패할 때

- 내부 PyPI 미러가 있다면 아래처럼 설치하세요.

```bash
python3 -m pip install -r requirements.txt --index-url https://<internal-pypi>/simple --trusted-host <internal-pypi-host>
```

- 또는 네트워크 팀에 `pypi.org`, `files.pythonhosted.org` 접근 허용을 요청하세요.

---

## 실행 방법

기본 실행(실제 RSS 호출):

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

실행하면 아래 형식의 파일이 생성됩니다.

- `output/news_YYYY_MM_DD.md`

예)

- `output/news_2026_03_09.md`

---

## 출력 형식

```markdown
## 기사 제목
출처: 링크

### 3줄 요약
- 무슨 일이 있었는지
- 왜 중요한지
- 투자자 관점에서 볼 포인트

### 투자 포인트
- ...

### 추가 항목
- 관련 기업: ...
- 시장 영향도: 낮음/중간/높음

### 인스타 후킹
- ...
- ...
- ...
```

---

## 네트워크 제한 환경에서 검증하는 방법

Codex cloud처럼 RSS 실호출이 차단된 환경에서도 검증할 수 있도록 `tests/fixtures/sample_tech.xml`을 사용한 테스트를 추가했습니다.

- `test_collect_from_local_sample_rss_file`: 샘플 XML 파싱 검증
- `test_pipeline_with_sample_rss_runs_without_network`: 수집→필터→요약(목킹)→마크다운 전체 흐름 검증

실행:

```bash
python3 -m unittest discover -s tests -v
```

---

## GitHub Actions 운영 분리

- `ci-offline.yml`: PR/Push 시 실행되는 기본 CI. 샘플 RSS 기반 테스트 포함(네트워크 제한 환경에서도 재현 가능)
- `live-rss-run.yml`: 스케줄/수동 실행으로 실제 RSS 수집 + OpenAI 요약 실행

실운영 워크플로우(`live-rss-run.yml`)를 사용하려면 저장소 Secret에 아래를 등록하세요.

- `OPENAI_API_KEY`

워크플로우 실행 후 생성된 markdown은 `daily-news-markdown` 아티팩트로 업로드됩니다.

