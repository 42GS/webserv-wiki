---
title: webserv 개요
type: overview
sources: [raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# webserv 개요

C++98로 HTTP 서버를 만드는 42 과제. 실행은 `./webserv [configuration file]` (raw/subject.md:118).
근거 소스: [[sources/subject]], [[sources/evaluation-sheet-en]] (평가표 영어 원문), [[sources/rfc9110]] (HTTP 의미론), [[sources/rfc9112]] (HTTP/1.1 메시지·연결), [[sources/rfc3875]] (CGI/1.1), [[sources/nginx-core-module]], [[sources/nginx-request-processing]] (NGINX 비교 기준), [[sources/posix-poll]], [[sources/posix-signal-h]], [[sources/posix-send]], [[sources/posix-recv]], [[sources/posix-waitpid]], [[sources/posix-bind]] (POSIX), [[sources/siege]], [[sources/siegerc]] (부하 테스트 도구). 구버전 한국어 정리본 [[sources/evaluation-sheet]]은 이력용이다.

## 무엇이 점수를 결정하나

평가는 단계 순서대로 진행되고, 앞 단계에서 걸리면 뒤는 보지 않는다.

1. **README 검사** — 필수 요소 하나라도 없으면 0점 (raw/evaluation-sheet-en.md:35-44) → [[concepts/build-and-submission]]
2. **코드 질의 — I/O 멀티플렉싱** (raw/evaluation-sheet-en.md:46-61). 단일 `poll()`류, read/write 동시 감시, readiness 없는 I/O 금지, `errno` 금지. 하나라도 틀리면 0점·종료. → [[concepts/io-multiplexing]]
3. **설정 파일** 기능 시연 (raw/evaluation-sheet-en.md:63-73) → [[concepts/configuration-file]]
4. **기본 HTTP 동작**과 정확한 status code (raw/evaluation-sheet-en.md:75-82) → [[concepts/http-features]]
5. **CGI** (raw/evaluation-sheet-en.md:84-93) → [[concepts/cgi]]
6. **브라우저·포트·siege** (raw/evaluation-sheet-en.md:95-118) → [[concepts/testing]], [[concepts/configuration-file]]
7. **보너스** — 필수 완벽 통과 시에만 (raw/evaluation-sheet-en.md:122) → [[concepts/bonus]]

모든 단계를 관통하는 조건: 크래시하면 즉시 0점 (raw/subject.md:46, raw/evaluation-sheet-en.md:24) → [[concepts/resilience]].

## 현재 종합 판단

- 구조의 중심은 **이벤트 루프 하나**다. socket·listen socket·CGI pipe가 모두 같은 `poll()`에 들어가야 한다 (raw/subject.md:130, raw/subject.md:136).
- 평가표가 subject보다 엄격하다 (`-1`/`0` 모두 처리, 에러 시 클라이언트 제거, README 0점, siege 99.5% 초과). 양쪽을 모두 만족하게 구현한다. → [[analysis/subject-vs-evaluation]]
- 평가표는 EAGAIN까지 반복 I/O를 허용하지만 errno 금지와 충돌한다. **readiness 1회에 I/O 1번**이 안전하다. → [[concepts/io-multiplexing]]
- virtual host는 선택 사항이다. 구현하지 않으면 같은 `interface:port` 중복 설정을 에러로 거부한다 (raw/evaluation-sheet-en.md:108). → [[concepts/configuration-file]]
- status code는 상황별 표 [[concepts/status-codes]]를 기준으로 정한다. 평가에서 코드가 틀리면 점수가 없다 (raw/evaluation-sheet-en.md:67). UNKNOWN 메서드는 501, 막힌 메서드는 405 + `Allow` (raw/rfc9110.txt:3800-3804, raw/rfc9110.txt:4724-4725).
- 요청 파서는 RFC 9112 순서(요청줄 → 헤더 → 본문 길이 → chunked)를 따른다. Host 누락, 헤더 이름 뒤 공백, 잘못된 `Content-Length`는 400 MUST다 → [[concepts/request-parsing]].
- 연결은 HTTP/1.1 기준 persistent가 기본이다. 본문을 다 읽지 않고 응답(413 등)하면 연결을 닫는다 → [[concepts/connection-management]].
- CGI에서 서버는 application gateway다. 본문 un-chunk, 메타변수 구성, EOF까지 출력 수집, CGI 응답을 HTTP 응답으로 변환하는 일이 서버 책임이다. 타임아웃은 504, 형식 오류는 502 → [[concepts/cgi]].
- subject의 root 예시는 NGINX `alias` 방식이다. location은 정규화된 URI(query 제외)에 대해 가장 긴 prefix로 매칭한다 → [[concepts/configuration-file]].
- server 선택은 `address:port` → Host 순서다. 맞는 이름이 없으면 그 포트의 default server(기본은 첫 server)가 처리한다 → [[concepts/configuration-file]].
- `poll()`은 `POLLHUP`·`POLLERR`를 요청하지 않아도 알려 준다. `POLLOUT`은 보낼 데이터가 있을 때만 켜야 busy waiting을 피한다. CGI 출력은 `POLLHUP` 뒤에도 EOF까지 읽는다 → [[concepts/io-multiplexing]].
- `SIGPIPE`의 기본 동작은 프로세스 종료이고, 끊긴 소켓에 `send`해도 발생한다. `signal(SIGPIPE, SIG_IGN)`으로 막아야 크래시 0점을 피한다 → [[concepts/resilience]].
- `recv`가 0이면 상대가 정상 종료한 것, -1이면 에러다. 둘 다 errno 없이 클라이언트를 정리한다. readiness 1회에 I/O 1번이면 EAGAIN을 구분할 일이 생기지 않는다 → [[concepts/io-multiplexing]].
- CGI 자식은 `waitpid(pid, &status, WNOHANG)`으로 회수한다. `WNOHANG`이 없으면 루프가 멈춘다. `SIGCHLD`는 `SIG_IGN`으로 바꾸지 않는다 → [[concepts/cgi]].
- 같은 포트를 쓰는 webserv를 하나 더 띄우면 `bind`가 `EADDRINUSE`로 실패한다. 이때 에러 메시지와 함께 정상 종료해야 한다. 한 설정 안의 중복은 파싱 단계에서 거부한다 → [[concepts/configuration-file]].
- siege의 Availability는 소켓 연결 성공률이다. 4xx·5xx는 깎이지 않고 연결 거부·끊김·타임아웃이 깎인다. 기본 설정의 siege는 요청마다 새 연결을 맺으므로 `accept`와 응답 후 종료 처리가 핵심이다 → [[concepts/testing]].
- 시연 준비물(기능별 설정 파일, 정적 사이트, CGI 정상/에러/무한 루프 스크립트)도 제출물이다 (raw/subject.md:184).

## 열린 질문

- virtual host를 구현할지 (선택 사항, 디펜스에서 이유 설명) → [[concepts/configuration-file]]
- 42 EvalHub 원문이 intra 현재 평가표와 같은지 → [[sources/evaluation-sheet-en]]
- HEAD를 지원할지 (RFC는 MUST, subject는 요구 안 함) → [[analysis/subject-vs-evaluation]]
- Date 헤더: 허용 함수 목록이 `<ctime>`에도 적용되는지 → [[analysis/subject-vs-evaluation]]
- `shutdown` 없이 연결을 안전하게 닫는 방법 → [[concepts/connection-management]]
- read/write 외 함수(`poll`, `bind`)의 errno를 봐도 되는지, `waitpid` 매크로를 써도 되는지 → [[analysis/subject-vs-evaluation]]
- `php-cgi`가 추가로 요구하는 환경 변수 (PHP 매뉴얼 확인 필요) → [[concepts/cgi]]
- NGINX 실측이 필요한 동작: 끝에 `/`가 없는 디렉토리 요청의 301, `limit_except`로 막힌 메서드의 코드, Host 없는 HTTP/1.1 요청의 코드 → [[source-wishlist]]
- index 파일이 CGI 확장자일 때 CGI로 실행할지 → [[concepts/configuration-file]]
