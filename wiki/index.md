---
title: Index
type: overview
updated: 2026-10-25
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
| [[sources/nginx-src-lingering-close]] | NGINX 1.30.6 소스 — lingering close는 `shutdown(fd, SHUT_WR)` 뒤 읽고 버리다가 닫음, 진입 조건 | `raw/nginx-src-ngx_http_request.c`, `raw/nginx-src-ngx_socket.h` |
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
| [[sources/siege-sock]] | siege 소켓 코드 — `timeout`은 읽기마다의 준비 검사에 쓰임, select 구현상 응답 대기에 실효 없음(판단, 실측으로 뒷받침) | `raw/siege-sock.c` |
| [[sources/siege-observed-ubuntu2204]] | siege 4.0.7 실측(Ubuntu 22.04) — 응답 없는 서버에 timeout 무효(150초), `Connection: close` 요청, `-b`가 `-d`보다 우선, `O_NDELAY`=`O_NONBLOCK` | `raw/siege-observed-ubuntu2204.md` |
| [[sources/siegerc]] | siege 기본 설정 템플릿 — connection=close, protocol, timeout, failures | `raw/siegerc.in` |
| [[sources/os-observed-bind]] | OS 실측(macOS·Ubuntu) — 재시작 직후 bind, `SO_REUSEADDR`, `0.0.0.0`과 특정 IP 충돌 | `raw/os-observed-bind.md` |
| [[sources/os-observed-pipe-poll]] | OS 실측(macOS·Ubuntu) — 한쪽이 닫힌 pipe의 `poll()` 비트 차이 | `raw/os-observed-pipe-poll.md` |
| [[sources/valgrind-observed-sigint]] | valgrind 실측(Ubuntu 24.04) — SIGINT 기본 종료는 still reachable, 해제 없이 return은 definitely lost, 정리 후 종료만 깨끗함 | `raw/valgrind-observed-sigint.md` |
| [[sources/macos-observed-sigpipe-leaks]] | macOS 실측 — `MSG_NOSIGNAL`·`SO_NOSIGPIPE` 지원, `leaks -atExit`는 SIGINT 종료에 출력 없이 exit 0, 해제 없는 return도 0 leaks | `raw/macos-observed-sigpipe-leaks.md` |
| [[sources/design-checks-observed]] | 설계 확인 실측 — 파일 `stat` 수정 시각이 `time()`과 일치, 메모리 고갈 시 `bad_alloc` 없이 `Killed`, 자식 `std::exit`이 flush 안 된 부모 버퍼를 다시 출력 | `raw/design-checks-observed.md` |
| [[sources/close-after-413-observed]] | 413 뒤 연결 종료 실측(Ubuntu 22.04·macOS) — 바로 close는 macOS에서 reset·curl 실패, 읽고 버리다 close는 12/12 응답 수신(`shutdown`과 차이 없음) | `raw/close-after-413-observed.md` |
| [[sources/efence-observed-ubuntu2204]] | Electric Fence 2.2.6 실측(Ubuntu 22.04) — 누수 보고 없음, heap 1바이트 초과가 segfault, `-lefence` 링크는 효과 없고 `LD_PRELOAD`만 동작 | `raw/efence-observed-ubuntu2204.md` |
| [[sources/ubuntu2204-observed-nofile]] | Ubuntu 22.04 systemd 패키지의 기본 fd 한도 — `DefaultLimitNOFILE=1024:524288`(soft 1024), `limits.conf`에 `nofile` 없음 | `raw/ubuntu2204-observed-nofile.md` |
| [[sources/ubuntu2204-observed-tools]] | Ubuntu 22.04(평가 PC) 실측 — php 8.1·valgrind 3.18·Python 3.10·siege 4.0.7, `siege -C` 값, php-cgi·valgrind 결과 동일, siege 4.0.7과 master 차이 | `raw/ubuntu2204-observed-tools.md` |
| [[sources/fs-observed-remove-name-length]] | 파일 시스템 실측(macOS·Ubuntu) — `std::remove`는 빈 디렉토리도 지움(비지 않으면 -1), 이름 상한 Ubuntu 255바이트·macOS는 글자 수 | `raw/fs-observed-remove-name-length.md` |
| [[sources/posix-remove]] | POSIX `remove()` — 파일이면 `unlink`, 디렉토리면 `rmdir`과 같음 (ISO C 밖의 확장) | `raw/posix-remove.md` |
| [[sources/posix-rmdir]] | POSIX `rmdir()` — 빈 디렉토리만 지움, 비어 있지 않으면 실패하고 그대로 | `raw/posix-rmdir.md` |
| [[sources/posix-exit]] | POSIX `_Exit()` — 프로세스 종료의 결과(좀비, fd 닫힘, 자식 입양) | `raw/posix-exit.md` |
| [[sources/posix-socket]] | POSIX `socket()` — 주소 없는 소켓을 만들고 fd를 돌려줌, `SOCK_STREAM`, Issue 8의 `SOCK_NONBLOCK` | `raw/posix-socket.md` |
| [[sources/posix-listen]] | POSIX `listen()` — 연결 받는 소켓으로 표시, backlog는 대기열 힌트(`SOMAXCONN`까지 지원) | `raw/posix-listen.md` |
| [[sources/posix-accept]] | POSIX `accept()` — 대기열의 첫 연결을 새 소켓 fd로, 비었으면 EAGAIN, O_NONBLOCK 상속은 구현마다 다름 | `raw/posix-accept.md` |
| [[sources/posix-read]] | POSIX `read()` — 최대 nbyte, 짧게 읽힐 수 있음, 빈 pipe는 쓰는 쪽이 없으면 0(EOF), 소켓이면 recv와 같음 | `raw/posix-read.md` |
| [[sources/posix-write]] | POSIX `write()` — 일부만 쓰일 수 있음, O_APPEND, non-blocking pipe 규칙, 읽는 쪽 없는 pipe는 EPIPE·SIGPIPE | `raw/posix-write.md` |
| [[sources/posix-open]] | POSIX `open()` — 열린 파일 설명과 fd, 접근 모드, O_CREAT·O_EXCL(원자적 생성)·O_APPEND·O_TRUNC | `raw/posix-open.md` |
| [[sources/nginx-index-module]] | NGINX index 모듈 — `/`로 끝나는 요청, 파일 목록 순서, 내부 리다이렉트 | `raw/nginx-index-module.md` |
| [[sources/nginx-autoindex-module]] | NGINX autoindex 모듈 — index가 없을 때 리스팅, 기본 off, 형식 | `raw/nginx-autoindex-module.md` |
| [[sources/rfc7578]] | RFC 7578 multipart/form-data — part 구조, Content-Disposition, filename 주의 | `raw/rfc7578.txt` |
| [[sources/rfc2046]] | RFC 2046 MIME — 5.1 multipart 문법 (구분자, 마지막 구분자, preamble) | `raw/rfc2046.txt` |
| [[sources/rfc3986]] | RFC 3986 URI — percent-encoding, dot-segment 제거, 상대 경로 해석, 디코딩 순서 | `raw/rfc3986.txt` |
| [[sources/nginx-rewrite-module]] | NGINX rewrite 모듈 — `return` 리다이렉트, 내부 리다이렉트 10회 상한 | `raw/nginx-rewrite-module.md` |
| [[sources/php-cgi-force-redirect]] | PHP 매뉴얼 — cgi.force_redirect와 REDIRECT_STATUS | `raw/php-cgi-force-redirect.md` |
| [[sources/php-ini-core]] | PHP 매뉴얼 — core php.ini 중 CGI 관련 설정과 기본값 | `raw/php-ini-core.md` |
| [[sources/php-src-cgi-main]] | PHP 소스 `cgi_main.c` — 실행 파일은 `SCRIPT_FILENAME` 우선, CGI 모드 판정, `REDIRECT_STATUS`는 있는지만 검사, 403·404 | `raw/php-src-cgi_main.c` |
| [[sources/php-cgi-observed-env]] | php-cgi 실측(Ubuntu 24.04) — 소스 동작 확인, `REDIRECT_STATUS` 없으면 헤더 없는 출력, 404·403은 exit 255 | `raw/php-cgi-observed-env.md` |
| [[sources/pep-0594]] | PEP 594 — Python `cgi`·`cgitb` 모듈 3.13 제거, 대체 수단 | `raw/pep-0594.md` |
| [[sources/rfc6265]] | RFC 6265 쿠키 — Set-Cookie·Cookie 문법, 속성, 세션 식별자 | `raw/rfc6265.txt` |
| [[sources/posix-fcntl]] | POSIX `fcntl()` — F_SETFL·O_NONBLOCK, F_SETFD·FD_CLOEXEC | `raw/posix-fcntl.md` |
| [[sources/iana-http-status-codes]] | IANA status code 레지스트리 — 코드 이름(reason phrase)과 정의 문서 | `raw/iana-http-status-codes.txt` |
| [[sources/rfc6585]] | RFC 6585 추가 status code — 431 정의, 선택 사항, 공격 시 연결 종료 | `raw/rfc6585.txt` |
| [[sources/cpp-core-guidelines]] | C++ Core Guidelines — SF.21·SF.22 이름 없는 namespace (헤더에는 쓰지 않고, 내부용은 모두 그 안에) | `raw/cpp-core-guidelines.md` |
| [[sources/google-cpp-style-guide]] | Google C++ Style Guide — Internal Linkage (다른 파일이 참조하지 않는 정의는 `.cc`의 이름 없는 namespace에), Function Definitions (정의 주석은 선언 주석을 되풀이하지 않음) | `raw/google-cpp-style-guide.md` |
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
| [[concepts/file-upload]] | 업로드 요구사항, multipart 구조·파싱 규칙(RFC 2046)과 처리 순서, filename 처리, 업로드 위치와 CGI 위험, 업로드 결정(multipart만, 그 밖은 415) |
| [[concepts/security]] | 경로 정규화 절차(8단계), 경로 공격(`..`), 명령 주입, 길이 공격, response splitting, request smuggling |
| [[concepts/resilience]] | 크래시·hang·누수 금지 요구, 내부 리다이렉트 반복 상한, 시그널 처리표 (SIGPIPE 무시, SIGINT 정리 후 종료) |
| [[concepts/testing]] | tester·siege·curl 등 도구, siege 옵션·기본 설정과 Availability의 의미, 평가 시연 준비 |
| [[concepts/build-and-submission]] | Makefile, C++98, README 형식, AI 규칙, 디펜스 수정 요청 |
| [[concepts/bonus]] | 쿠키·세션 (Set-Cookie·Cookie 규칙, 헤더 저장 구조, 삭제, 세션 설계, 구현 방식), 복수 CGI |

## Analysis

| 페이지 | 요약 |
|---|---|
| [[analysis/subject-vs-evaluation]] | 모순·제약(EAGAIN vs errno, HEAD, 허용 함수 범위(Date·exit), half-close, HTTP 버전, REMOTE_ADDR, read/write 외 errno, waitpid 매크로, /dev/urandom, fcntl 허용 목록, POSIX poll vs macOS 실측), 정리본 vs 원문 차이표, 해소된 미확인 |
| [[analysis/design]] | 클래스·인터페이스 설계 — 파일 배치, 모듈 책임, 설정 구조체, `IoHandler`/`EventLoop`, Connection 상태기계와 상태별 타임아웃, 파서·라우터·응답·CGI 인터페이스, 에러 처리, 상수 |
| [[analysis/implementation-plan]] | 구현 순서 10단계(뼈대 → 설정 파서 → 이벤트 루프 → 요청 파서 → 라우팅·정적 → 연결 관리 → 업로드·DELETE → CGI → 안정성 → 시연 준비)와 모듈 구조, 단계별 완료 기준. 모두 완료(2026-10-18) |
| [[analysis/test-plan]] | 테스트 계획 — 요구사항 한 줄마다 근거·테스트 수준(단위·통합·코드 읽기·수동)·기대 결과·현재 테스트·상태. 0~9단계 전체, 8절 안정성 점검(valgrind·e_fence·siege)과 코드 리뷰, 일부러 틀린 코드로 실패 확인 |
| [[analysis/mock-evaluation]] | 평가표 순서대로 따라 한 모의 평가(2026-10-25, Ubuntu 22.04 컨테이너): 항목별 결과, 발견한 것(`-std=c++98` 없는 빌드 실패, 빈 페이지 없음), 서버 문제가 아닌 현상, poll→I/O 코드 경로 디펜스 메모 |
| [[analysis/design-decisions]] | 사용자가 정한 설계 결정 18건 (poll, `..`·`%2F` 400, virtual host 미구현, HEAD 지원, index→CGI, 업로드는 multipart만, 세션은 CGI 예제, NGINX 설정 문법, 파일 시계·`Date`, 본문 상한 100MB, CGI 자식 `std::exit`, `listen`은 `IPv4:port`·`port`만, alias는 경로 경계에서만, 삭제는 `std::remove`, `limit_except` 없으면 GET·HEAD만, 같은 이름 업로드는 409, 업로드 파일은 요청당 5개)과 근거·구현 영향 |

## Lessons

webserv 코드를 처음부터 배우는 학습 노트. 비유 → 이론 → 코드(파일:줄, webserv `5ca93a2`) → 구현 이유 → 평가 팁 → 확인 문제 순서.

| 페이지 | 요약 |
|---|---|
| [[lessons/00-guide]] | 읽는 법, 상자(콜아웃) 종류, 추천 순서 |
| [[lessons/01-request-journey]] | 요청 한 개가 서버를 지나가는 8단계, 모듈별 책임 |
| [[lessons/02-networking-basics]] | 프로세스, fd, 소켓·포트, TCP 스트림, 블로킹·논블로킹 |
| [[lessons/03-http-basics]] | 요청·응답 모양, 상태 코드 표, Content-Length와 chunked, keep-alive |
| [[lessons/04-poll]] | poll 하나 규칙(0점 조건), revents 처리, 준비 1회 I/O 1번, POLLOUT과 busy waiting |
| [[lessons/05-startup]] | main 순서, 파일로 만든 시계, 소멸 순서 |
| [[lessons/06-config-parsing]] | lexer → 지시어 나무 → builder, 규칙 표, 상속, 시작을 거부하는 설정 |
| [[lessons/07-event-loop]] | IoHandler, 한 바퀴, 지연 unwatch, accept 실패 시 listener 멈춤, Server 소유 |
| [[lessons/08-connection]] | Connection 상태기계와 타임아웃, DRAIN 실측 근거, keep-alive·pipelining, CGI 대기 |
| [[lessons/09-request-parser]] | 파서 상태, HEAD_DONE, RFC 선택표, 크기 상한, Host 검사 |
| [[lessons/10-routing]] | 경로 정규화, location 매칭과 alias 경계, root·alias, 결정 순서, 디렉토리 요청 |
| [[lessons/11-response]] | finish(Date·HEAD·close), 에러 페이지, Content-Type, ResponseStream과 response splitting |
| [[lessons/12-upload-delete]] | multipart 구조, 저장 전 검사(415·400·413·409), O_EXCL, DELETE와 std::remove |
| [[lessons/13-cgi]] | 스크립트 찾기, 메타변수, pipe·fork·dup2·execve, pipe poll, 출력 해석, 좀비 회수 |
| [[lessons/14-resilience]] | 시그널, 예외 세 겹, 점검 결과 |
| [[lessons/15-defense-qa]] | 평가표 코드 질의 순서의 예상 질문 14개와 알려진 약점 |
| [[lessons/16-glossary]] | 용어 사전 |
