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
| [[sources/rfc1945]] | RFC 1945 HTTP/1.0 — 연결 기본 동작, 0.9 요청, Content-Length 필수, DELETE는 부록 | `raw/rfc1945.txt` |
| [[sources/rfc3875]] | RFC 3875 CGI/1.1 (Informational) — 과제 관련 절과 핵심 규칙 | `raw/rfc3875.txt` |
| [[sources/nginx-core-module]] | NGINX core 모듈 — 과제 관련 디렉티브 목록, 변환 검증 방법 | `raw/nginx-core-module.md` |
| [[sources/nginx-request-processing]] | NGINX 요청 처리 — server 선택(포트 → Host), default server, location과 query | `raw/nginx-request-processing.md` |
| [[sources/nginx-server-names]] | NGINX Server names — 이름 매칭 우선순위, 빈 이름, server가 정해지는 시점 | `raw/nginx-server-names.md` |
| [[sources/nginx-observed-directory]] | NGINX 실측 — 디렉토리 301·403, root 위 `..`는 400 | `raw/nginx-observed-directory.md` |
| [[sources/nginx-observed-encoded-slash]] | NGINX 실측 — `%2F`를 디코딩해 경로 구분자로 씀, 디코딩 후 정규화, root 위 `..`는 400 | `raw/nginx-observed-encoded-slash.md` |
| [[sources/posix-poll]] | POSIX `poll()` — 이벤트 비트, 준비 상태의 의미, busy waiting | `raw/posix-poll.md` |
| [[sources/posix-signal-h]] | POSIX `<signal.h>` — 시그널 기본 동작 (SIGPIPE·SIGCHLD·SIGINT 등) | `raw/posix-signal-h.md` |
| [[sources/posix-send]] | POSIX `send()` — EPIPE와 SIGPIPE, MSG_NOSIGNAL, 반환값 | `raw/posix-send.md` |
| [[sources/posix-recv]] | POSIX `recv()` — 반환값 0·-1의 의미, 스트림의 메시지 경계 | `raw/posix-recv.md` |
| [[sources/posix-waitpid]] | POSIX `wait()`·`waitpid()` — WNOHANG, 반환값, 종료 상태 매크로, SIGCHLD | `raw/posix-waitpid.md` |
| [[sources/posix-bind]] | POSIX `bind()` — EADDRINUSE·EADDRNOTAVAIL, non-blocking 비동기 할당 | `raw/posix-bind.md` |
| [[sources/siege]] | siege 매뉴얼 — 옵션(-c·-r·-t·-d·-b), Availability의 의미 | `raw/siege.pod` |
| [[sources/siege-sock]] | siege 소켓 코드 — `timeout`은 읽기마다의 준비 검사에 쓰임, select 구현상 응답 대기 실효는 불확실(판단) | `raw/siege-sock.c` |
| [[sources/siegerc]] | siege 기본 설정 템플릿 — connection=close, protocol, timeout, failures | `raw/siegerc.in` |
| [[sources/os-observed-bind]] | OS 실측(macOS·Ubuntu) — 재시작 직후 bind, `SO_REUSEADDR`, `0.0.0.0`과 특정 IP 충돌 | `raw/os-observed-bind.md` |
| [[sources/os-observed-pipe-poll]] | OS 실측(macOS·Ubuntu) — 한쪽이 닫힌 pipe의 `poll()` 비트 차이 | `raw/os-observed-pipe-poll.md` |
| [[sources/posix-exit]] | POSIX `_Exit()` — 프로세스 종료의 결과(좀비, fd 닫힘, 자식 입양) | `raw/posix-exit.md` |
| [[sources/nginx-index-module]] | NGINX index 모듈 — `/`로 끝나는 요청, 파일 목록 순서, 내부 리다이렉트 | `raw/nginx-index-module.md` |
| [[sources/nginx-autoindex-module]] | NGINX autoindex 모듈 — index가 없을 때 리스팅, 기본 off, 형식 | `raw/nginx-autoindex-module.md` |
| [[sources/rfc7578]] | RFC 7578 multipart/form-data — part 구조, Content-Disposition, filename 주의 | `raw/rfc7578.txt` |
| [[sources/rfc2046]] | RFC 2046 MIME — 5.1 multipart 문법 (구분자, 마지막 구분자, preamble) | `raw/rfc2046.txt` |
| [[sources/rfc3986]] | RFC 3986 URI — percent-encoding, dot-segment 제거, 상대 경로 해석, 디코딩 순서 | `raw/rfc3986.txt` |
| [[sources/nginx-rewrite-module]] | NGINX rewrite 모듈 — `return` 리다이렉트, 내부 리다이렉트 10회 상한 | `raw/nginx-rewrite-module.md` |
| [[sources/php-cgi-force-redirect]] | PHP 매뉴얼 — cgi.force_redirect와 REDIRECT_STATUS | `raw/php-cgi-force-redirect.md` |
| [[sources/php-ini-core]] | PHP 매뉴얼 — core php.ini 중 CGI 관련 설정과 기본값 | `raw/php-ini-core.md` |
| [[sources/pep-0594]] | PEP 594 — Python `cgi`·`cgitb` 모듈 3.13 제거, 대체 수단 | `raw/pep-0594.md` |
| [[sources/rfc6265]] | RFC 6265 쿠키 — Set-Cookie·Cookie 문법, 속성, 세션 식별자 | `raw/rfc6265.txt` |
| [[sources/posix-fcntl]] | POSIX `fcntl()` — F_SETFL·O_NONBLOCK, F_SETFD·FD_CLOEXEC | `raw/posix-fcntl.md` |
| [[sources/iana-http-status-codes]] | IANA status code 레지스트리 — 코드 이름(reason phrase)과 정의 문서 | `raw/iana-http-status-codes.txt` |
| [[sources/rfc6585]] | RFC 6585 추가 status code — 431 정의, 선택 사항, 공격 시 연결 종료 | `raw/rfc6585.txt` |
| [[sources/evaluation-sheet]] | 평가표 한국어 정리본 — **구버전, 영어 원문으로 대체됨** | `raw/evaluation-sheet.md` |

## Concepts

| 페이지 | 요약 |
|---|---|
| [[concepts/io-multiplexing]] | 단일 `poll()`·non-blocking·`errno` 금지 등 9개 규칙, EAGAIN 반복 모순, `revents` 처리표, POLLOUT 관리, recv·send 반환값 처리표, 허용 함수 |
| [[concepts/configuration-file]] | 필수 기능 10개와 평가 테스트 대응, root=NGINX alias 방식, location 매칭, server 선택, 디렉토리 요청 처리 순서, NGINX 지시자 대응표, Port issues, virtual host |
| [[concepts/cgi]] | 호출 절차 7단계, 메타변수 표, CGI 응답 파싱(4가지 유형·Status), 실패 처리(502·504), 자식 회수(waitpid), php-cgi 추가 변수 |
| [[concepts/http-features]] | 필수 기능, 메서드별 규칙(RFC 9110), 응답 헤더 규칙, HEAD·Date 쟁점 |
| [[concepts/status-codes]] | 과제 상황별 status code 선택표 (정상·리다이렉트·4xx·5xx), RFC 근거, reason phrase(IANA 이름) |
| [[concepts/request-parsing]] | 요청줄 → 헤더 → 본문 길이 결정 → chunked 디코딩, 단계별 에러 코드 |
| [[concepts/connection-management]] | keep-alive 판단, 413 이후 처리, pipelining 순서, 타임아웃 4종, lingering close와 `shutdown` 쟁점 |
| [[concepts/file-upload]] | 업로드 요구사항, multipart 구조·파싱 규칙(RFC 2046)과 처리 순서, filename 처리, 업로드 위치와 CGI 위험, 열린 설계 질문 |
| [[concepts/security]] | 경로 정규화 절차(8단계), 경로 공격(`..`), 명령 주입, 길이 공격, response splitting, request smuggling |
| [[concepts/resilience]] | 크래시·hang·누수 금지 요구, 내부 리다이렉트 반복 상한, 시그널 처리표 (SIGPIPE 무시, SIGINT 정리 후 종료) |
| [[concepts/testing]] | tester·siege·curl 등 도구, siege 옵션·기본 설정과 Availability의 의미, 평가 시연 준비 |
| [[concepts/build-and-submission]] | Makefile, C++98, README 형식, AI 규칙, 디펜스 수정 요청 |
| [[concepts/bonus]] | 쿠키·세션 (Set-Cookie·Cookie 규칙, 헤더 저장 구조, 삭제, 세션 설계, 구현 방식), 복수 CGI |

## Analysis

| 페이지 | 요약 |
|---|---|
| [[analysis/subject-vs-evaluation]] | 모순·제약(EAGAIN vs errno, HEAD, 허용 함수 범위(Date·exit), half-close, HTTP 버전, REMOTE_ADDR, read/write 외 errno, waitpid 매크로, /dev/urandom, fcntl 허용 목록, POSIX poll vs macOS 실측), 정리본 vs 원문 차이표, 해소된 미확인 |
