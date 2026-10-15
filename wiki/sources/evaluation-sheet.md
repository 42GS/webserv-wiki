---
title: webserv 평가표 (42 EvalHub 정리본)
type: source
sources: [raw/evaluation-sheet.md]
superseded_by: sources/evaluation-sheet-en
updated: 2026-10-15
---

# webserv 평가표

원본: `raw/evaluation-sheet.md` — <https://www.42evalhub.com/common/webserv> 의 평가 항목을 한국어로 정리한 2차 자료 (raw/evaluation-sheet.md:3-5).

> [!warning] 영어 원문으로 대체됨 (2026-10-15)
> 같은 URL의 영어 원문 [[sources/evaluation-sheet-en]]과 대조했더니 여러 항목이 다르다. 이 정리본은 평가표 **구버전**을 옮긴 것으로 보인다 (근거: README 0점 항목이 없음, 1회 1 I/O 규칙이 원문에서는 EAGAIN까지 반복 허용으로 바뀜).
> 평가 기준은 영어 원문을 따른다. 차이 목록은 [[analysis/subject-vs-evaluation]] 4절에 있다.
> 이 페이지는 이력 확인용으로 남긴다.

## 평가 순서

| 단계 | 내용 | 위키 페이지 |
|---|---|---|
| 0. Guidelines | Git 저장소 내용만, 크래시 시 즉시 0점, 설정 파일 외 수정은 학생과 합의해야 함, 누수 검사 필수 (raw/evaluation-sheet.md:15-25) | [[concepts/resilience]] |
| 0. Attachments | `tester`, `ubuntu_tester`, `cgi_tester`, `ubuntu_cgi_tester` (raw/evaluation-sheet.md:32-33) | [[concepts/testing]] |
| 1.1 코드 질의 | I/O 멀티플렉싱 설명, `select()` 한 개만 쓰는지 질문, read/write 동시 감시, 1회 1 I/O, errno 금지 (raw/evaluation-sheet.md:39-57) | [[concepts/io-multiplexing]] |
| 1.2 Configuration | 여러 포트·호스트네임, 에러 페이지, body 제한, 라우트별 디렉토리·index·메서드 (raw/evaluation-sheet.md:59-77) | [[concepts/configuration-file]] |
| 1.3 Basic checks | GET/POST/DELETE, UNKNOWN 메서드, 업로드 후 다운로드 (raw/evaluation-sheet.md:79-86) | [[concepts/http-features]] |
| 1.4 CGI | 작업 디렉토리, GET/POST, 무한 루프·에러 스크립트 (raw/evaluation-sheet.md:88-97) | [[concepts/cgi]] |
| 1.5 Browser | 헤더 확인, 정적 사이트, 잘못된 URL, 디렉토리 리스팅, 리다이렉트 (raw/evaluation-sheet.md:99-107) | [[concepts/http-features]] |
| 1.6 Port issues | 같은 포트 중복 설정, 공통 포트 서버 동시 실행 (raw/evaluation-sheet.md:109-114) | [[concepts/configuration-file]] |
| 1.7 Siege | `siege -b` availability ≥ 99.5%, 누수·hang 없음, 무한 실행 (raw/evaluation-sheet.md:116-122) | [[concepts/testing]], [[concepts/resilience]] |
| 2. Bonus | 쿠키·세션, 복수 CGI (raw/evaluation-sheet.md:126-137) | [[concepts/bonus]] |

## 즉시 0점·평가 종료 조건

- 디펜스 중 segfault·예기치 않은 종료 (raw/evaluation-sheet.md:23)
- `select()`(또는 동등 함수)가 메인 루프에 없거나 read/write를 동시에 검사하지 않음 (raw/evaluation-sheet.md:48-49)
- `read`/`recv`/`write`/`send` 후 `errno` 검사 (raw/evaluation-sheet.md:54)
- 1.1 항목 중 하나라도 불명확·부정확 → 평가 중단 (raw/evaluation-sheet.md:41, raw/evaluation-sheet.md:57)

## subject에 없는 추가 기준

- 클라이언트당 `select()` 1회에 read 1번 또는 write 1번 (raw/evaluation-sheet.md:50)
- 반환값 `-1`과 `0` 모두 검사 (raw/evaluation-sheet.md:53)
- I/O 에러 시 클라이언트 제거 (raw/evaluation-sheet.md:51)
- 호스트네임별 서버 설정 (raw/evaluation-sheet.md:65-68)
- `siege -b` availability ≥ 99.5% (raw/evaluation-sheet.md:119)
- 메모리 누수 검사 (raw/evaluation-sheet.md:25, raw/evaluation-sheet.md:120)

자세한 대조는 [[analysis/subject-vs-evaluation]].
