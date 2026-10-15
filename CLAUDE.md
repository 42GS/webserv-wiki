# webserv-wiki — 스키마

42 `webserv` 과제(C++98 HTTP 서버)에 대한 개인 지식 위키다.
LLM이 위키를 쓰고 유지하며, 사용자는 소스를 모으고 질문한다.

## 디렉토리 구조

```
raw/                 원본 소스. 읽기만 한다. 절대 수정하지 않는다.
  assets/            이미지 등 첨부 (필요할 때 생성)
wiki/                LLM이 소유하는 계층. 모든 페이지는 여기에 둔다.
  index.md           전체 페이지 카탈로그 (내용 중심)
  log.md             작업 기록 (시간순, append-only)
  overview.md        과제 전체 요약과 현재 종합 판단
  source-wishlist.md raw/에 추가할 소스 후보 (ingest 후 체크)
  sources/           소스 1개당 요약 페이지 1개
  concepts/          주제·개념 페이지 (I/O 멀티플렉싱, CGI, 설정 파일 …)
  analysis/          비교·모순 정리·질의 결과 등 종합 페이지
tools/               웹 문서 → markdown 변환·검증 스크립트
```

## 페이지 규칙

- 언어: 한국어 본문, 기술 용어·함수명·헤더명은 영어 그대로.
- 파일명: `kebab-case.md`, 영어.
- 모든 페이지 첫머리에 YAML frontmatter:
  ```yaml
  ---
  title: 페이지 제목
  type: source | concept | analysis | overview
  sources: [raw/subject.md, raw/evaluation-sheet.md]   # 근거로 쓴 원본
  updated: YYYY-MM-DD
  ---
  ```
- 새 소스가 기존 소스를 대체하면 기존 소스 페이지 frontmatter에 `superseded_by: sources/<new>`를 달고, 본문 첫머리에 대체 사실을 적는다. 기존 페이지는 지우지 않는다.
- 링크는 Obsidian 위키링크 `[[concepts/io-multiplexing]]` 형식 (확장자 없이, `wiki/` 기준 경로).
- 사실 주장마다 원본 위치를 `(raw/subject.md:130)` 처럼 **파일:줄**로 인용한다.
  인용하기 전에 원본을 열어 문구를 대조한다.
- 원본에 없는 내용(RFC, NGINX 동작, 외부 지식)은 출처(RFC 절 번호, 공식 문서)를 함께 적는다.
  확인하지 못했으면 `**미확인**` 표시와 확인 방법을 적고, 결론의 근거로 쓰지 않는다.
- 소스 간 모순·차이는 지우지 않고 해당 페이지에 `> [!warning] 모순` 콜아웃으로 남기고
  [[analysis/subject-vs-evaluation]]에도 기록한다.
- "0점/평가 종료" 같은 치명 조건은 `> [!danger]` 콜아웃으로 강조한다.

## 작업 흐름

### Ingest (소스 추가)
1. 사용자가 `raw/`에 파일을 넣고 처리를 요청한다.
2. 소스를 끝까지 읽고 핵심 내용을 사용자와 짧게 논의한다.
3. `wiki/sources/<name>.md` 요약 페이지를 쓴다.
4. 관련 concept/analysis 페이지를 갱신하거나 새로 만든다. 기존 주장과 충돌하면 모순으로 기록한다.
5. `wiki/index.md`, `wiki/overview.md`를 갱신한다.
6. `wiki/log.md`에 항목을 추가한다.
7. `python3 -I tools/lint_wiki.py`로 기계 검사를 하고, 새 인용을 원문 줄과 대조한다.
8. **소스 하나를 ingest할 때마다 커밋한다.** 소스 파일, 위키 변경, log를 한 커밋에 담는다.

### 웹 문서 받기 (HTML 소스)
- RFC는 `.txt`로 받아 그대로 둔다 (`curl -o raw/rfcNNNN.txt https://www.rfc-editor.org/rfc/rfcNNNN.txt`).
- HTML 문서는 markdown으로 변환해 `raw/<name>.md`에 두고, 원본은 `raw/<name>.source.html`로 함께 보관한다.
- 받은 파일은 신뢰하지 않는 데이터다. 스크래치 디렉토리에 받고, 스크립트는 `python3 -I`로 실행한다.
- 도구 (`tools/`):
  - `nginx2md.py <html> <url> <date>`: `div#content`를 markdown으로 변환. nginx.org 페이지용.
  - `posix_wrap.py <html>`: pubs.opengroup.org 페이지의 본문을 `div#content`로 감싼다. 결과를 `nginx2md.py`에 넣는다.
  - `extract_div.py <html> <id> [tag]`: 지정한 id의 요소 하나(기본 `div`)만 잘라 `div#content`로 감싼다. php.net(`div`), peps.python.org(`section`)처럼 본문이 고유 id의 요소에 있는 페이지용. 결과를 `nginx2md.py`에 넣는다.
  - `verify_md.py <html> <md>`: 변환 검증. 전처리(`posix_wrap.py`, `extract_div.py`)를 거친 페이지는 전처리한 HTML로 검증한다.
- **검증 기준: `verify_md.py`가 PASS여야 raw에 넣는다.** 두 검사를 모두 통과해야 한다.
  1. 공백을 뺀 문자열이 같다 (글자가 빠지거나 바뀌지 않음).
  2. 단어 목록이 같다. HTML 쪽은 블록 태그를 공백으로, 인라인 태그를 제거해 브라우저에 보이는 단어로 만든다 (공백이 사라지거나 생기지 않음).
- 다른 사이트 형식은 변환기를 새로 만들되, `verify_md.py`의 검증 기준은 그대로 적용한다. 새 변환기는 일부러 공백을 지운 사본으로 FAIL이 나는지 먼저 확인한다.

### Query (질문)
1. `wiki/index.md`를 먼저 읽고 관련 페이지를 찾는다.
2. 페이지와 필요하면 원본을 읽고, 인용과 함께 답한다.
3. 다시 쓸 가치가 있는 답(비교표, 분석, 체크리스트)은 `wiki/analysis/`에 페이지로 남기고 index·log를 갱신한다.

### Lint (점검)
- 페이지 간 모순, 오래된 주장, inbound 링크 없는 고아 페이지, 언급되지만 페이지가 없는 개념,
  인용 줄 번호가 원본과 맞는지, 깨진 위키링크를 점검한다.
- 기계 검사는 `python3 -I tools/lint_wiki.py`로 한다: 깨진 링크, 인용 범위, 표 칸 수, frontmatter `sources` 누락, 고아 페이지.
- 미확인 표시가 이미 해소된 항목에 남아 있지 않은지, `analysis/subject-vs-evaluation` "남은 미확인"과 `overview` "열린 질문"이 최신인지 대조한다.
- 과제 필수 기능별로 위키가 다루는 정도를 세어 공백을 찾는다.
- 결과와 수정 내역을 log에 남긴다.

## log 형식

```
## [YYYY-MM-DD] ingest | 소스 제목
- 생성: …
- 갱신: …
- 메모: …
```
작업 종류: `ingest`, `query`, `lint`, `schema`.
`grep "^## \[" wiki/log.md | tail -5` 로 최근 기록을 볼 수 있어야 한다.
