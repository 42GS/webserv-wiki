---
title: webserv 평가표 영어 원문 (42 EvalHub)
type: source
sources: [raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# webserv 평가표 영어 원문

원본: `raw/evaluation-sheet-en.md`. 42 EvalHub 페이지가 불러오는 `/data/common/webserv.html`의 텍스트를 옮겼다. 원본 HTML은 `raw/evaluation-sheet-en.source.html`에 있다 (raw/evaluation-sheet-en.md:3-5).
위키에서 **평가 기준의 1차 근거**로 쓴다. 한국어 정리본 [[sources/evaluation-sheet]]과 다르면 이 문서를 따른다.

> [!note] 출처 신뢰도
> 42 EvalHub는 42 intra가 아닌 제3자 사이트다. 페이지에 버전·날짜가 없다 (raw/evaluation-sheet-en.md:6). intra의 현재 평가표와 같은지는 **미확인** — 확인 방법: 평가 슬롯의 intra 평가표와 대조.
> 다만 subject v24.0에만 있는 내용(README 요구사항, raw/subject.md:194-207)을 반영하고 있어 정리본보다 최신으로 보인다.

## 평가 순서

| 단계 | 내용 | 위키 페이지 |
|---|---|---|
| Guidelines | Git 저장소 내용만, 크래시 시 0점, 설정 파일 외 수정 금지, 누수 검사 (raw/evaluation-sheet-en.md:18-25) | [[concepts/resilience]] |
| Attachments | `subject.pdf`, `tester`, `cgi_tester` (raw/evaluation-sheet-en.md:29-31) | [[concepts/testing]] |
| README.md Compliance Check | 필수 요소 하나라도 없으면 0점 (raw/evaluation-sheet-en.md:35-44) | [[concepts/build-and-submission]] |
| Check the code | 이벤트 메커니즘 설명, 단일 `poll()`, readiness 후 I/O, errno 금지, 디스크 I/O가 루프를 막지 않음 (raw/evaluation-sheet-en.md:46-61) | [[concepts/io-multiplexing]] |
| Configuration | 여러 interface·port, 에러 페이지, body 제한, 라우트, index, 메서드 (raw/evaluation-sheet-en.md:63-73) | [[concepts/configuration-file]] |
| Basic checks | GET/POST/DELETE, UNKNOWN, status code, 업로드 후 다운로드 (raw/evaluation-sheet-en.md:75-82) | [[concepts/http-features]] |
| Check CGI | 작업 디렉토리, GET/POST, 에러·무한 루프 스크립트 (raw/evaluation-sheet-en.md:84-93) | [[concepts/cgi]] |
| Check with a browser | 헤더, 정적 사이트, 잘못된 URL, 리스팅, 리다이렉트 (raw/evaluation-sheet-en.md:95-103) | [[concepts/http-features]] |
| Port issues | 같은 interface:port 중복은 virtual host 미구현 시 에러, 프로그램 여러 개 동시 실행 (raw/evaluation-sheet-en.md:105-109) | [[concepts/configuration-file]] |
| Siege | `-b`로 availability > 99.5%, 누수·hang 없음, `-c`/`-d`/`-r`로 부하 합의 (raw/evaluation-sheet-en.md:111-118) | [[concepts/testing]] |
| Bonus | 쿠키·세션, 복수 CGI (raw/evaluation-sheet-en.md:120-130) | [[concepts/bonus]] |

## 0점·평가 종료 조건

- 빈 저장소, 동작하지 않는 프로그램, Norm 에러, 치팅(-42) (raw/evaluation-sheet-en.md:23)
- 디펜스 중 segfault 등 예기치 않은 종료 (raw/evaluation-sheet-en.md:24)
- README 필수 요소 누락 (raw/evaluation-sheet-en.md:44)
- `poll()`이 메인 루프에 없거나 read/write를 동시에 검사하지 않음 (raw/evaluation-sheet-en.md:53)
- read/recv/write/send 후 errno 검사 (raw/evaluation-sheet-en.md:57)
- 코드 질의 단계 항목이 하나라도 불명확·부정확 → 평가 중단 (raw/evaluation-sheet-en.md:61)

## 한국어 정리본과의 차이

[[analysis/subject-vs-evaluation]] 4절에 표로 정리했다.
