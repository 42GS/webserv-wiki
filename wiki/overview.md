---
title: webserv 개요
type: overview
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc9110.txt, raw/rfc1945.txt]
updated: 2026-10-16
---

# webserv 개요

C++98로 HTTP 서버를 만드는 42 과제. 실행은 `./webserv [configuration file]` (raw/subject.md:118).
근거 소스: [[sources/subject]], [[sources/evaluation-sheet-en]] (평가표 영어 원문), [[sources/rfc9110]] (HTTP 의미론), [[sources/rfc9112]] (HTTP/1.1 메시지·연결), [[sources/rfc1945]] (HTTP/1.0), [[sources/rfc3875]] (CGI/1.1), [[sources/rfc7578]], [[sources/rfc2046]] (multipart/form-data), [[sources/rfc3986]] (URI), [[sources/php-cgi-force-redirect]], [[sources/php-ini-core]], [[sources/php-src-cgi-main]], [[sources/php-cgi-observed-env]] (php-cgi), [[sources/pep-0594]] (Python `cgi` 모듈 제거), [[sources/rfc6265]] (쿠키), [[sources/iana-http-status-codes]] (status code 목록), [[sources/rfc6585]] (431), [[sources/nginx-core-module]], [[sources/nginx-request-processing]], [[sources/nginx-server-names]], [[sources/nginx-index-module]], [[sources/nginx-autoindex-module]], [[sources/nginx-rewrite-module]] (NGINX 비교 기준), [[sources/posix-poll]], [[sources/posix-signal-h]], [[sources/posix-send]], [[sources/posix-recv]], [[sources/posix-waitpid]], [[sources/posix-bind]], [[sources/posix-exit]], [[sources/posix-fcntl]] (POSIX), [[sources/siege]], [[sources/siegerc]], [[sources/siege-sock]] (부하 테스트 도구), [[sources/os-observed-bind]], [[sources/os-observed-pipe-poll]] (macOS·Ubuntu 실측), [[sources/nginx-observed-directory]], [[sources/nginx-observed-encoded-slash]] (NGINX 실측), [[sources/valgrind-observed-sigint]] (valgrind 실측), [[sources/ubuntu2204-observed-tools]] (평가 PC와 같은 Ubuntu 22.04의 도구 버전·siege 설정·재측정), [[sources/siege-observed-ubuntu2204]] (siege 4.0.7 동작 실측), [[sources/macos-observed-sigpipe-leaks]] (macOS `MSG_NOSIGNAL`·`leaks` 실측), [[sources/efence-observed-ubuntu2204]] (Electric Fence 실측), [[sources/close-after-413-observed]] (413 뒤 연결 종료 방식 실측), [[sources/nginx-src-lingering-close]] (NGINX lingering close 소스). 구버전 한국어 정리본 [[sources/evaluation-sheet]]은 이력용이다.

## 무엇이 점수를 결정하나

평가는 아래 순서로 진행된다. README 필수 요소가 빠지면 0점이고 (raw/evaluation-sheet-en.md:44), 코드 질의 단계에서 하나라도 불명확하거나 틀리면 평가가 멈춘다 (raw/evaluation-sheet-en.md:61).

1. **README 검사** — 필수 요소 하나라도 없으면 0점 (raw/evaluation-sheet-en.md:35-44) → [[concepts/build-and-submission]]
2. **코드 질의 — I/O 멀티플렉싱** (raw/evaluation-sheet-en.md:46-61). 단일 `poll()`류, read/write 동시 감시, readiness 없는 I/O 금지, `errno` 금지. 메인 루프·동시 감시 위반과 errno 검사는 0점·종료다 (raw/evaluation-sheet-en.md:53, raw/evaluation-sheet-en.md:57). → [[concepts/io-multiplexing]]
3. **설정 파일** 기능 시연 (raw/evaluation-sheet-en.md:63-73) → [[concepts/configuration-file]]
4. **기본 HTTP 동작**과 정확한 status code (raw/evaluation-sheet-en.md:75-82) → [[concepts/http-features]]
5. **CGI** (raw/evaluation-sheet-en.md:84-93) → [[concepts/cgi]]
6. **브라우저·포트·siege** (raw/evaluation-sheet-en.md:95-118) → [[concepts/testing]], [[concepts/configuration-file]]
7. **보너스** — 필수 완벽 통과 시에만 (raw/evaluation-sheet-en.md:122) → [[concepts/bonus]]

모든 단계를 관통하는 조건: 크래시하면 즉시 0점 (raw/subject.md:46, raw/evaluation-sheet-en.md:24) → [[concepts/resilience]].

## 현재 종합 판단

- 멀티플렉서는 `poll()`로 정했다. 개발은 macOS, 평가는 Ubuntu 22.04(사용자 확인, 2026-10-15)라 두 OS에서 같은 코드가 돌아야 한다 → [[concepts/io-multiplexing]].
- 구조의 중심은 **이벤트 루프 하나**다. socket·listen socket·CGI pipe가 모두 같은 `poll()`에 들어가야 한다 (raw/subject.md:130, raw/subject.md:136).
- 평가표가 subject보다 엄격하다 (`-1`/`0` 모두 처리, 에러 시 클라이언트 제거, README 0점, siege 99.5% 초과). 양쪽을 모두 만족하게 구현한다. → [[analysis/subject-vs-evaluation]]
- 평가표는 EAGAIN까지 반복 I/O를 허용하지만 errno 금지와 충돌한다. **readiness 1회에 I/O 1번**이 안전하다(판단). → [[concepts/io-multiplexing]]
- 클래스·인터페이스 설계는 [[analysis/design]], 구현 순서와 단계별 완료 기준은 [[analysis/implementation-plan]]에 있다.
- 설계 결정은 [[analysis/design-decisions]]에 모았다 (2026-10-15 사용자 결정): virtual host 미구현(같은 `interface:port` 중복은 설정 에러, raw/evaluation-sheet-en.md:108), HEAD 지원, index 파일이 CGI 확장자면 CGI로 실행, 업로드는 서버가 multipart만 저장(그 밖의 본문은 415, 판단), 쿠키·세션 보너스는 CGI 예제. → [[concepts/configuration-file]]
- status code는 상황별 표 [[concepts/status-codes]]를 기준으로 정한다. 평가에서 코드가 틀리면 점수가 없다 (raw/evaluation-sheet-en.md:67). UNKNOWN 메서드는 501, 막힌 메서드는 405 + `Allow` (raw/rfc9110.txt:3799-3804, raw/rfc9110.txt:4724-4726).
- 요청 파서는 RFC 9112 순서(요청줄 → 헤더 → 본문 길이 → chunked)를 따른다. Host 누락, 헤더 이름 뒤 공백, 잘못된 `Content-Length`는 400 MUST다. 헤더 크기 상한 초과는 4xx MUST이고 431로 응답한다(판단) → [[concepts/request-parsing]].
- 응답은 `HTTP/1.1`로 보낸다(RFC 9110 SHOULD). HTTP/1.0만으로는 과제가 설명되지 않는다(DELETE는 RFC 1945 부록, 405·413 없음). HTTP/0.9는 지원하지 않고 400, HTTP/1.0 POST에 `Content-Length`가 없으면 400 (판단) → [[sources/rfc1945]], [[concepts/request-parsing]].
- 연결은 HTTP/1.1 기준 persistent가 기본이다. 본문을 다 읽지 않고 응답(413 등)하면 연결을 닫는다. 이때 바로 `close()`하지 않고 읽기만 하며 버리다가 상한(무입력 시간·총 시간)에 닿으면 닫는다. 바로 닫으면 macOS에서 reset으로 curl이 응답을 못 받은 경우가 있었고, 읽고 버리면 `shutdown` 없이도 두 OS에서 모두 받았다(실측) → [[concepts/connection-management]].
- CGI에서 서버는 application gateway다. 본문 un-chunk, 메타변수 구성, EOF까지 출력 수집, CGI 응답을 HTTP 응답으로 변환하는 일이 서버 책임이다. 타임아웃은 504, 형식 오류는 502(판단, RFC 3875는 코드를 정하지 않음) → [[concepts/cgi]].
- subject의 root 예시는 NGINX `alias` 방식에 가깝다(판단). 설정은 NGINX 문법으로 하고 `root`(NGINX 방식)와 `alias`(subject 예시 방식)를 둘 다 지원한다(결정 9). 이 과제는 정규식 없이 정규화된 URI(query 제외)의 가장 긴 prefix로 location을 고른다(NGINX는 그 뒤 정규식 location을 검사한다) → [[concepts/configuration-file]].
- server 선택은 `address:port` → Host 순서다. 맞는 이름이 없으면 그 포트의 default server(기본은 첫 server)가 처리한다. virtual host를 구현하면 정확한 이름만, 포트를 떼고 대소문자 무시로 비교한다(판단). 요청줄 이전에 쓰는 헤더 크기 상한은 포트 단위로 둔다 → [[concepts/configuration-file]].
- POSIX상 `poll()`은 `POLLHUP`·`POLLERR`를 요청하지 않아도 알려 준다(macOS는 `events=0`인 pipe에 `POLLHUP`을 보고하지 않았다, 실측). `POLLOUT`은 보낼 데이터가 있을 때만 켜야 busy waiting을 피한다. CGI 출력은 `POLLHUP` 뒤에도 EOF까지 읽는다 → [[concepts/io-multiplexing]].
- `SIGPIPE`의 기본 동작은 프로세스 종료이고, 끊긴 소켓에 `send`해도 발생한다. `signal(SIGPIPE, SIG_IGN)`으로 막아야 크래시 0점을 피한다 → [[concepts/resilience]].
- macOS와 Ubuntu는 pipe의 `poll()` 비트가 다르다. `POLLERR`·`POLLHUP`을 먼저 보고, `POLLHUP`만 와도 EOF까지 읽고, 다 쓴 fd는 목록에서 뺀다. listen 소켓에는 `bind` 전에 `SO_REUSEADDR`를 켜고, `0.0.0.0`과 특정 IP의 같은 포트는 설정에서 거부한다 → [[concepts/io-multiplexing]], [[concepts/configuration-file]].
- `recv`가 0이면 상대가 정상 종료한 것, -1이면 에러다. 둘 다 errno 없이 클라이언트를 정리한다. readiness 1회에 I/O 1번이면 EAGAIN을 구분할 일이 거의 없고, -1이면 원인과 관계없이 정리한다(판단) → [[concepts/io-multiplexing]].
- CGI 자식은 `waitpid(pid, &status, WNOHANG)`으로 회수한다. `WNOHANG`이 없으면 루프가 멈추고, 회수하지 않으면 좀비가 남는다. `SIGCHLD`는 `SIG_IGN`으로 바꾸지 않는다. 서버를 끌 때는 실행 중인 CGI도 끝낸다 → [[concepts/cgi]].
- 같은 포트를 쓰는 webserv를 하나 더 띄우면 `bind`가 `EADDRINUSE`로 실패한다. 이때 에러 메시지와 함께 정상 종료해야 한다. 한 설정 안의 중복은 파싱 단계에서 거부한다 → [[concepts/configuration-file]].
- siege의 Availability는 소켓 연결 성공률이다. 4xx·5xx는 깎이지 않고 연결 거부·끊김·타임아웃이 깎인다. 기본 설정의 siege는 `connection = close`라 요청마다 새 연결을 맺는다고 보고, `accept`와 응답 후 종료 처리를 핵심으로 본다(판단). siege의 `timeout`은 응답 대기를 끊지 않는다(siege 4.0.7 실측: 응답 없는 서버 앞에서 150초 동안 끝나지 않음). siege는 매 요청에 `Connection: close`를 보낸다 → [[concepts/testing]], [[sources/siege-observed-ubuntu2204]].
- 브라우저 업로드는 `multipart/form-data`다. 구분자 앞의 CRLF는 파일 내용이 아니다(포함하면 파일이 손상된다). `filename`은 경로를 버리고 덮어쓰기를 막으며, 업로드 위치에서는 CGI를 실행하지 않는다 → [[concepts/file-upload]].
- 문서로 정해지지 않는 응답은 판단으로 확정했다: 끝에 `/`가 없는 디렉토리 요청은 301, 리스팅 off + index 없음은 403(둘 다 NGINX 실측과 같음). root 위로 올라가는 `..`는 400 + 연결 닫기(NGINX 실측, 사용자 결정). Host 없는 HTTP/1.1은 400, 막힌 메서드는 405 + `Allow` (RFC MUST) → [[concepts/configuration-file]], [[concepts/status-codes]].
- 요청 경로는 query 분리 → 세그먼트 분할 → 한 번만 디코딩 → `%00`·`%2F` 거부 → `..` 제거 → 매핑 → root 안인지 확인 순서로 처리한다. `%2F`는 400으로 거부한다(사용자 결정). NGINX는 `%2F`를 구분자로 쓰고 디코딩을 먼저 하므로 이 점은 NGINX와 다르다(실측) → [[concepts/security]], [[sources/nginx-observed-encoded-slash]].
- 리다이렉트 설정은 `return 코드 URL` 형식으로 받는다. index·`error_page`·CGI local redirect 같은 내부 리다이렉트는 반복 횟수에 상한을 두고 넘으면 500 → [[concepts/configuration-file]], [[concepts/resilience]].
- Python CGI 스크립트에서는 `cgi` 모듈을 쓰지 않는다(3.13에서 제거. Ubuntu 22.04의 Python 3.10에는 아직 있다). `QUERY_STRING`·표준 입력으로 직접 처리한다 → [[concepts/cgi]].
- php-cgi는 기본 설정에서 `REDIRECT_STATUS`가 없으면 실행을 거부한다(값은 보지 않음). 실행할 파일은 `SCRIPT_FILENAME`에서 먼저 찾는다. RFC 3875 변수에 더해 `REDIRECT_STATUS`와 `SCRIPT_FILENAME`을 넣고, `REDIRECT_URL`은 넣지 않는다(판단) → [[concepts/cgi]].
- 보너스 쿠키·세션: 응답 헤더 구조가 같은 이름의 `Set-Cookie` 여러 개를 담을 수 있어야 한다. 세션은 식별자만 쿠키에, 상태는 서버에 둔다 → [[concepts/bonus]].
- non-blocking은 `fcntl(fd, F_SETFL, O_NONBLOCK)`로 설정한다. `FD_CLOEXEC`는 허용 목록상 설정할 방법이 없어, CGI 자식에서 `execve` 전에 필요 없는 fd를 닫는다 → [[concepts/cgi]].
- 시연 준비물(기능별 설정 파일, 정적 사이트, CGI 정상/에러/무한 루프 스크립트)도 제출물이다 (raw/subject.md:184).

## 열린 질문

- 42 EvalHub 원문이 intra 현재 평가표와 같은지 → [[sources/evaluation-sheet-en]]
- 허용 함수 목록이 `<ctime>`, `exit` 같은 표준 라이브러리에도 적용되는지 (Date 헤더, CGI 자식 종료, 리스팅 시간 표시) → [[analysis/subject-vs-evaluation]]
- Ubuntu 평가에서 `fcntl()`(subject상 "For macOS only" 절) 사용이 인정되는지 → [[concepts/io-multiplexing]]
- read/write 외 함수(`poll`, `bind`)의 errno를 봐도 되는지, `waitpid` 매크로를 써도 되는지, `/dev/urandom` 읽기가 `poll()` 예외인지, `FD_CLOEXEC`를 위해 `F_SETFD`를 써도 되는지 → [[analysis/subject-vs-evaluation]]
- 쿠키·세션 보너스를 CGI 예제로 보여 주는 것을 평가자가 "웹 서버의 세션 시스템"으로 인정할지 → [[analysis/design-decisions]] 8
