---
title: 추가할 소스 목록
type: overview
updated: 2026-10-15
---

# 추가할 소스 목록

`raw/`에 넣을 후보다. 공식 자료만 넣는다(블로그·위키·포럼 제외).
URL은 2026-10-15에 접속해 HTTP 200을 확인했다. 받아서 넣은 소스는 체크하고 log에 ingest를 남긴다.
받지 않기로 한 항목은 `[-]`로 표시하고 이유를 적는다.

- **P1**: 지금 열려 있는 **미확인** 항목을 해소하거나 0점 위험 영역을 다룸
- **P2**: 필수 기능 구현에 직접 필요
- **P3**: 보너스·보조

## 1. 과제·평가 원문

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P1 | 42 EvalHub 평가표 **영어 원문** — `raw/evaluation-sheet-en.md`로 ingest (2026-10-15) | <https://www.42evalhub.com/common/webserv> | 정리본의 미확인 3건 (Norm 문구, URL 빠진 curl, 1.6 세 번째 항목), "같은 포트" 문구 → [[analysis/subject-vs-evaluation]] | `raw/evaluation-sheet-en.md` |
| [ ] | P2 | 평가 첨부 `tester`, `cgi_tester` 사용법 | 42 intra 평가 페이지 (공개 URL 없음) | 테스터가 기대하는 동작 → [[concepts/testing]] | `raw/tester-notes.md` |

## 2. HTTP 명세 (RFC)

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P1 | RFC 9110 — HTTP Semantics — `raw/rfc9110.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc9110> | 메서드, status code 정의, `Host`, 405 응답의 `Allow` 등 → [[concepts/http-features]] | `raw/rfc9110.txt` |
| [x] | P1 | RFC 9112 — HTTP/1.1 — `raw/rfc9112.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc9112> | 메시지 파싱, `Content-Length`, 7.1 Chunked Transfer Coding → [[concepts/cgi]] un-chunk 요구 | `raw/rfc9112.txt` |
| [x] | P2 | RFC 1945 — HTTP/1.0 — `raw/rfc1945.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc1945> | subject가 기준점으로 제안한 버전 (raw/subject.md:123) | `raw/rfc1945.txt` |
| [x] | P2 | RFC 3986 — URI: Generic Syntax — `raw/rfc3986.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc3986> | 요청 타깃 파싱, percent-encoding, `..` 경로 정규화 | `raw/rfc3986.txt` |
| [x] | P1 | RFC 7578 — multipart/form-data — `raw/rfc7578.txt`로 ingest (2026-10-15, lint에서 업로드 공백이 드러나 P2→P1) | <https://www.rfc-editor.org/rfc/rfc7578> | 브라우저 파일 업로드 형식 | `raw/rfc7578.txt` |
| [x] | P2 | RFC 2046 — MIME Media Types (5.1 Multipart) — `raw/rfc2046.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc2046> | multipart 구분자 문법, 마지막 구분자 `--boundary--` (5.1.1 Common Syntax, 2026-10-15 `close-delimiter` 규칙 존재 확인) → [[concepts/file-upload]] | `raw/rfc2046.txt` |
| [x] | P2 | IANA HTTP Status Code Registry — `raw/iana-http-status-codes.txt`로 ingest (2026-10-15, txt 형식) | <https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml> | 평가표 "status code 목록 검색해 둘 것" (raw/evaluation-sheet.md:63) | `raw/iana-status-codes.md` |
| [x] | P3 | RFC 6585 — Additional HTTP Status Codes — `raw/rfc6585.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc6585> | 431 Request Header Fields Too Large의 정의 (5절, 2026-10-15 존재 확인) → [[concepts/status-codes]] | `raw/rfc6585.txt` |

## 3. CGI

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P1 | RFC 3875 — CGI Version 1.1 — `raw/rfc3875.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc3875> | 4.1 Request Meta-Variables (환경 변수 목록), CGI 응답 형식 → [[concepts/cgi]] 미확인 해소 | `raw/rfc3875.txt` |
| [x] | P2 | PHP 매뉴얼 — Installed as CGI binary — 장 첫 페이지는 목차뿐이라 하위 절 `raw/php-cgi-force-redirect.md`와 기본값 근거 `raw/php-ini-core.md`로 ingest (2026-10-15) | <https://www.php.net/manual/en/security.cgi-bin.php> | `php-cgi` 실행 시 주의점 | `raw/php-cgi-security.md` |
| [x] | P3 | PEP 594 — `raw/pep-0594.md`로 ingest (2026-10-15) | <https://peps.python.org/pep-0594/> | Python 표준 라이브러리 `cgi` 모듈 제거 — Python CGI 스크립트 작성 시 참고 | `raw/pep-0594.md` |

## 4. NGINX (subject가 비교 기준으로 지정, raw/subject.md:141, raw/subject.md:161)

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P1 | ngx_http_core_module — `raw/nginx-core-module.md`로 ingest (2026-10-15) | <https://nginx.org/en/docs/http/ngx_http_core_module.html> | `root` vs `alias` (→ [[concepts/configuration-file]] 미확인), `listen`, `server_name`, `location`, `error_page`, `client_max_body_size` | `raw/nginx-core-module.md` |
| [x] | P1 | How nginx processes a request — `raw/nginx-request-processing.md`로 ingest (2026-10-15) | <https://nginx.org/en/docs/http/request_processing.html> | 같은 포트 + 다른 `server_name` 처리, default server → virtual host 모순 | `raw/nginx-request-processing.md` |
| [x] | P2 | Server names — `raw/nginx-server-names.md`로 ingest (2026-10-15) | <https://nginx.org/en/docs/http/server_names.html> | `server_name` 매칭 규칙 | `raw/nginx-server-names.md` |
| [x] | P2 | ngx_http_index_module — `raw/nginx-index-module.md`로 ingest (2026-10-15) | <https://nginx.org/en/docs/http/ngx_http_index_module.html> | 디렉토리 기본 파일 | `raw/nginx-index-module.md` |
| [x] | P2 | ngx_http_autoindex_module — `raw/nginx-autoindex-module.md`로 ingest (2026-10-15) | <https://nginx.org/en/docs/http/ngx_http_autoindex_module.html> | 디렉토리 리스팅 | `raw/nginx-autoindex-module.md` |
| [x] | P2 | ngx_http_rewrite_module — `raw/nginx-rewrite-module.md`로 ingest (2026-10-15) | <https://nginx.org/en/docs/http/ngx_http_rewrite_module.html> | `return`으로 리다이렉트 | `raw/nginx-rewrite-module.md` |

## 5. 시스템 콜 (POSIX.1-2024, man page)

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P1 | `poll()` — `raw/posix-poll.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html> | `POLLIN`/`POLLOUT`/`POLLHUP`/`POLLERR` 의미 → [[concepts/io-multiplexing]] | `raw/posix-poll.md` |
| [x] | P1 | `<signal.h>` — `raw/posix-signal-h.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/signal.h.html> | `SIGPIPE` 기본 동작 → [[concepts/resilience]] 미확인 해소 | `raw/posix-signal-h.md` |
| [x] | P1 | `send()` / `recv()` — `raw/posix-send.md`, `raw/posix-recv.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/functions/send.html>, <https://pubs.opengroup.org/onlinepubs/9799919799/functions/recv.html> | 반환값 `-1`/`0` 의미, `SIGPIPE` 발생 조건 | `raw/posix-send.md`, `raw/posix-recv.md` |
| [x] | P2 | `fcntl()` — `raw/posix-fcntl.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/functions/fcntl.html> | `F_SETFL`만으로 non-blocking 설정 | `raw/posix-fcntl.md` |
| [x] | P2 | `waitpid()` — `raw/posix-waitpid.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/functions/waitpid.html> | `WNOHANG`으로 CGI 자식 회수 | `raw/posix-waitpid.md` |
| [x] | P2 | `_Exit()` — "Consequences of Process Termination" — `raw/posix-exit.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/functions/_Exit.html> | 회수하지 않은 자식이 좀비가 되는지 (2026-10-15 페이지에 "zombie process" 문장 있음 확인) → [[concepts/cgi]] | `raw/posix-exit.md` |
| [x] | P2 | `bind()` — `raw/posix-bind.md`로 ingest (2026-10-15) | <https://pubs.opengroup.org/onlinepubs/9799919799/functions/bind.html> | 같은 포트 중복 bind 실패 (`EADDRINUSE`) | `raw/posix-bind.md` |
| [-] | P2 | Linux `epoll(7)` — 받지 않음: `poll()` 사용 결정 (2026-10-15) | <https://man7.org/linux/man-pages/man7/epoll.7.html> | Linux에서 epoll을 쓸 경우 | `raw/linux-epoll-7.md` |
| [-] | P2 | FreeBSD `kqueue(2)` — 받지 않음: `poll()` 사용 결정 (2026-10-15) | <https://man.freebsd.org/cgi/man.cgi?query=kqueue&sektion=2> | macOS에서 kqueue를 쓸 경우. macOS 자체 man page는 터미널 `man 2 kqueue`가 더 정확함 | `raw/kqueue-2.md` |

## 4-1. NGINX 실측 (문서로 확인 불가)

> [!note] 정리 (2026-10-15)
> 4건 모두 실측 없이 정했다. 앞의 두 건은 RFC가 답을 정하므로 닫았다. 뒤의 두 건은 RFC가 코드를 정하지 않아 **판단**으로 확정했고, NGINX와 같은지는 디펜스 근거를 보강하는 **선택** 항목으로만 남긴다. subject는 NGINX를 비교 대상으로 쓸 수 있다고 할 뿐 따르라고 하지 않는다 (raw/subject.md:186).

nginx.org에 정적 파일 모듈 문서가 없고(`ngx_http_static_module.html` 404, 2026-10-15 확인), access 모듈 문서에도 응답 코드가 없다. subject가 권하는 대로 NGINX를 직접 실행해 비교한다 (raw/subject.md:186). 로컬에는 NGINX가 설치되어 있지 않다 (2026-10-15 확인).

| | 우선 | 확인할 것 | 방법 | 결과 저장 |
|---|---|---|---|---|
| [ ] | 선택 | 끝에 `/`가 없는 디렉토리 요청에 301을 보내는지, `Location` 형식 — 과제는 **판단**으로 301 확정 ([[concepts/configuration-file]]) | NGINX 설치 후 `curl -i`로 요청 | `raw/nginx-observed-<주제>.md` (명령과 출력 그대로) |
| [x] | — | `limit_except`로 막힌 메서드의 응답 코드 — **닫음**: RFC 9110이 405 + `Allow` MUST (raw/rfc9110.txt:7603-7607) | — | — |
| [ ] | 선택 | 리스팅 off + index 없는 디렉토리의 응답 코드 (index·autoindex 모듈 문서에 없음, 2026-10-15 확인) — 과제는 **판단**으로 403 확정 | 같은 방법 | 같은 형식 |
| [x] | — | Host 헤더 없는 HTTP/1.1 요청의 응답 코드 — **닫음**: RFC 9112가 400 MUST (raw/rfc9112.txt:445-448) | — | — |

## 5-1. OS 실측 (POSIX 문서로 확인 불가)

POSIX가 동작을 정하지 않아 OS별로 직접 확인해야 하는 것. 평가 환경(평가표는 apt 기준, raw/evaluation-sheet-en.md:48)과 개발 환경(macOS)에서 각각 확인한다.

| | 우선 | 확인할 것 | 방법 | 결과 저장 |
|---|---|---|---|---|
| [ ] | P2 | 서버 재시작 직후 같은 포트 `bind` 실패 여부, `SO_REUSEADDR`의 효과 | 서버를 띄워 연결을 맺고 종료한 뒤 바로 재시작 | `raw/os-observed-<주제>.md` (OS, 명령, 출력 그대로) |
| [ ] | P2 | `0.0.0.0:P`와 `127.0.0.1:P`를 함께 `bind`할 때 충돌 여부 | 작은 테스트 프로그램 | 같은 형식 |
| [ ] | P2 | 읽는 쪽이 닫힌 pipe를 `poll`하면 어떤 비트가 오는지 (`POLLERR`/`POLLHUP`) | 작은 테스트 프로그램 | 같은 형식 |

## 6. 테스트 도구

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P2 | siege 매뉴얼 (`doc/siege.pod`) — `raw/siege.pod`로 ingest (2026-10-15) | <https://raw.githubusercontent.com/JoeDog/siege/master/doc/siege.pod> | `-b` 옵션 의미, availability 계산, keep-alive 동작 → [[concepts/testing]]. 기존 `joedog.org/siege-manual/`은 404 | `raw/siege-manual.md` |
| [x] | P2 | siege 기본 설정 템플릿 (`doc/siegerc.in`) — `raw/siegerc.in`으로 ingest (2026-10-15) | <https://raw.githubusercontent.com/JoeDog/siege/master/doc/siegerc.in> | keep-alive 기본값 (`connection`), 동시 사용자 상한 → [[concepts/testing]] | `raw/siegerc.in` |

## 7. 쿠키·세션 (보너스)

| | 우선 | 소스 | URL | 해소할 것 | 제안 파일명 |
|---|---|---|---|---|---|
| [x] | P3 | RFC 6265 — HTTP State Management Mechanism — `raw/rfc6265.txt`로 ingest (2026-10-15) | <https://www.rfc-editor.org/rfc/rfc6265> | `Set-Cookie`/`Cookie` 형식 → [[concepts/bonus]] | `raw/rfc6265.txt` |

## 넣지 않는 것

- C++98 표준(ISO/IEC 14882:1998)은 유료 문서다. cppreference는 커뮤니티 위키라 근거로 쓰지 않는다. 필요해지면 따로 정한다.
- RFC 7230~7235는 대체된 문서라 넣지 않는다. 7230·7231·7232·7233·7235는 RFC 9110이, 7230은 RFC 9112도, 7234(캐싱)는 RFC 9111이 대체했다 (각 RFC 머리말 "Obsoletes:"). 캐싱은 과제 범위 밖이라 RFC 9111도 넣지 않는다.

## 받는 방법

- RFC: `curl -o raw/rfc9110.txt https://www.rfc-editor.org/rfc/rfc9110.txt` — `.txt`가 줄 번호 인용에 가장 좋다.
- HTML 문서: Obsidian Web Clipper로 markdown 변환 후 `raw/`에 저장.
