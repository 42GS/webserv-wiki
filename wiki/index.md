---
title: Index
type: overview
updated: 2026-10-15
---

# Index

- [[overview]] — 과제 전체 요약, 평가 흐름, 현재 종합 판단, 열린 질문
- [[source-wishlist]] — raw/에 추가할 공식 소스 후보, 우선순위, 해소할 미확인 항목

## Sources

| 페이지 | 요약 | 원본 |
|---|---|---|
| [[sources/subject]] | webserv subject v24.0 장별 요약, 0점 조건 | `raw/subject.md` |
| [[sources/evaluation-sheet-en]] | 평가표 영어 원문 (42 EvalHub). 평가 기준의 1차 근거 | `raw/evaluation-sheet-en.md` |
| [[sources/rfc9110]] | RFC 9110 HTTP Semantics — 과제 관련 절 목록과 핵심 규칙 | `raw/rfc9110.txt` |
| [[sources/rfc9112]] | RFC 9112 HTTP/1.1 — 과제 관련 절 목록과 핵심 규칙 | `raw/rfc9112.txt` |
| [[sources/rfc3875]] | RFC 3875 CGI/1.1 (Informational) — 과제 관련 절과 핵심 규칙 | `raw/rfc3875.txt` |
| [[sources/nginx-core-module]] | NGINX core 모듈 — 과제 관련 디렉티브 목록, 변환 검증 방법 | `raw/nginx-core-module.md` |
| [[sources/nginx-request-processing]] | NGINX 요청 처리 — server 선택(포트 → Host), default server, location과 query | `raw/nginx-request-processing.md` |
| [[sources/posix-poll]] | POSIX `poll()` — 이벤트 비트, 준비 상태의 의미, busy waiting | `raw/posix-poll.md` |
| [[sources/posix-signal-h]] | POSIX `<signal.h>` — 시그널 기본 동작 (SIGPIPE·SIGCHLD·SIGINT 등) | `raw/posix-signal-h.md` |
| [[sources/posix-send]] | POSIX `send()` — EPIPE와 SIGPIPE, MSG_NOSIGNAL, 반환값 | `raw/posix-send.md` |
| [[sources/posix-recv]] | POSIX `recv()` — 반환값 0·-1의 의미, 스트림의 메시지 경계 | `raw/posix-recv.md` |
| [[sources/posix-waitpid]] | POSIX `wait()`·`waitpid()` — WNOHANG, 반환값, 종료 상태 매크로, SIGCHLD | `raw/posix-waitpid.md` |
| [[sources/posix-bind]] | POSIX `bind()` — EADDRINUSE·EADDRNOTAVAIL, non-blocking 비동기 할당 | `raw/posix-bind.md` |
| [[sources/siege]] | siege 매뉴얼 — 옵션(-c·-r·-t·-d·-b), Availability의 의미 | `raw/siege.pod` |
| [[sources/siegerc]] | siege 기본 설정 템플릿 — connection=close, protocol, timeout, failures | `raw/siegerc.in` |
| [[sources/posix-exit]] | POSIX `_Exit()` — 프로세스 종료의 결과(좀비, fd 닫힘, 자식 입양) | `raw/posix-exit.md` |
| [[sources/nginx-index-module]] | NGINX index 모듈 — `/`로 끝나는 요청, 파일 목록 순서, 내부 리다이렉트 | `raw/nginx-index-module.md` |
| [[sources/evaluation-sheet]] | 평가표 한국어 정리본 — **구버전, 영어 원문으로 대체됨** | `raw/evaluation-sheet.md` |

## Concepts

| 페이지 | 요약 |
|---|---|
| [[concepts/io-multiplexing]] | 단일 `poll()`·non-blocking·`errno` 금지 등 9개 규칙, EAGAIN 반복 모순, `revents` 처리표, POLLOUT 관리, recv·send 반환값 처리표, 허용 함수 |
| [[concepts/configuration-file]] | 필수 기능 10개와 평가 테스트 대응, root=NGINX alias 방식, location 매칭, server 선택, NGINX 지시자 대응표, Port issues, virtual host |
| [[concepts/cgi]] | 호출 절차 7단계, 메타변수 표, CGI 응답 파싱(4가지 유형·Status), 실패 처리(502·504), 자식 회수(waitpid) |
| [[concepts/http-features]] | 필수 기능, 메서드별 규칙(RFC 9110), 응답 헤더 규칙, HEAD·Date 쟁점 |
| [[concepts/status-codes]] | 과제 상황별 status code 선택표 (정상·리다이렉트·4xx·5xx), RFC 근거 |
| [[concepts/request-parsing]] | 요청줄 → 헤더 → 본문 길이 결정 → chunked 디코딩, 단계별 에러 코드 |
| [[concepts/connection-management]] | keep-alive 판단, 413 이후 처리, pipelining 순서, 타임아웃 4종, lingering close와 `shutdown` 쟁점 |
| [[concepts/security]] | 경로 공격(`..`), 명령 주입, 길이 공격, response splitting, request smuggling |
| [[concepts/resilience]] | 크래시·hang·누수 금지 요구, 시그널 처리표 (SIGPIPE 무시, SIGINT 정리 후 종료) |
| [[concepts/testing]] | tester·siege·curl 등 도구, siege 옵션·기본 설정과 Availability의 의미, 평가 시연 준비 |
| [[concepts/build-and-submission]] | Makefile, C++98, README 형식, AI 규칙, 디펜스 수정 요청 |
| [[concepts/bonus]] | 쿠키·세션, 복수 CGI |

## Analysis

| 페이지 | 요약 |
|---|---|
| [[analysis/subject-vs-evaluation]] | 모순·제약(EAGAIN vs errno, HEAD, 허용 함수 범위(Date·exit), half-close, HTTP 버전, REMOTE_ADDR, read/write 외 errno, waitpid 매크로), 정리본 vs 원문 차이표, 해소된 미확인 |
