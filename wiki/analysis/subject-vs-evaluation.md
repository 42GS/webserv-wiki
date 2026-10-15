---
title: subject vs 평가표 — 차이와 모순
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/evaluation-sheet.md, raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc3875.txt, raw/nginx-core-module.md, raw/posix-poll.md, raw/posix-waitpid.md, raw/posix-bind.md, raw/posix-exit.md, raw/nginx-autoindex-module.md, raw/rfc6265.txt, raw/posix-fcntl.md, raw/rfc1945.txt, raw/os-observed-pipe-poll.md]
updated: 2026-10-15
---

# subject vs 평가표 — 차이와 모순

평가표는 영어 원문 [[sources/evaluation-sheet-en]]을 기준으로 한다. 실제 채점은 평가표로 하므로, 둘이 다르면 **양쪽을 모두 만족하는 쪽으로 구현**한다.

## 1. 모순

### 1.1 EAGAIN까지 반복 vs errno 금지

- 평가표: readiness 후 EAGAIN/EWOULDBLOCK이 나올 때까지 read/write해도 된다 (raw/evaluation-sheet-en.md:54).
- subject: read/write 후 errno로 동작을 바꾸는 것은 엄격히 금지 (raw/subject.md:133).
- 평가표 자체도 errno 검사는 0점이고 로그만 허용한다 (raw/evaluation-sheet-en.md:57).
- EAGAIN 여부는 errno로만 알 수 있으므로 반복 허용과 errno 금지가 같이 성립하기 어렵다.
- 판단: **readiness 1회에 read/write 1번**으로 구현한다. 두 문서를 모두 만족한다. → [[concepts/io-multiplexing]]

### 1.2 virtual host — 해소됨

- subject: virtual host는 범위 밖, 구현은 허용 (raw/subject.md:151).
- 평가표 원문: 같은 interface:port에 여러 사이트를 설정하면 에러여야 한다. 단 virtual host를 구현했으면 둘 다 유효 (raw/evaluation-sheet-en.md:108).
- 두 문서가 일치한다. 모순으로 보였던 것은 구버전 정리본의 호스트네임 테스트 항목 때문이었다 (raw/evaluation-sheet.md:65-68). → [[concepts/configuration-file]]

### 1.3 HEAD — subject vs RFC 9110

- RFC 9110: 범용 서버는 GET과 HEAD를 MUST로 지원 (raw/rfc9110.txt:3794-3795).
- subject: GET·POST·DELETE만 요구 (raw/subject.md:147). 평가표도 HEAD를 테스트하지 않는다 (raw/evaluation-sheet-en.md:79).
- 판단: 평가에는 영향이 없다. 구현 비용이 작아서 지원을 고려한다. 지원하지 않는다면 HEAD에 501로 응답한다 (raw/rfc9110.txt:3800-3801). → [[concepts/http-features]]

### 1.4 허용 함수 목록의 범위 — `<ctime>`, `exit` (질문)

subject는 "허용된 syscall/라이브러리 호출" 목록을 준다 (raw/subject.md:111-113). 이 목록이 C/C++ 표준 라이브러리 함수에도 적용되는지가 문구만으로 불분명하다 (**미확인**). 이 질문에 걸리는 경우:

- **Date 헤더:** RFC 9110상 clock이 있는 origin server는 2xx·3xx·4xx 응답에 `Date` MUST, clock이 없으면 보내면 안 됨 (raw/rfc9110.txt:2313-2320). 목록에 시간 함수가 없다 (raw/subject.md:113). → [[concepts/http-features]]
- **디렉토리 리스팅의 시간 표시:** NGINX 리스팅은 파일 시간을 보인다 (raw/nginx-autoindex-module.md:88). 시간 형식으로 바꾸려면 시간 함수가 필요하다. subject는 리스팅 내용을 정하지 않으므로 (raw/subject.md:170) 생략할 수 있다. → [[concepts/configuration-file]]
- **CGI 자식 종료:** `execve`가 실패한 자식은 끝나야 한다. `exit`·`_exit`가 목록에 없다 (raw/subject.md:113). POSIX는 보통 `exit()`을 권하지만 (raw/posix-exit.md:122), `_exit`은 stream을 flush하지 않아 fork된 자식에서 부모의 버퍼를 다시 내보내지 않는다 (raw/posix-exit.md:36). → [[concepts/cgi]]
- 판단 보류. 확인 방법: 동료·평가자 합의 또는 42 공식 답변.

### 1.5 half-close — 허용 함수 목록 vs RFC 9112

- RFC 9112: 즉시 닫으면 TCP reset 때문에 클라이언트가 마지막 응답을 못 읽을 수 있다. 그래서 서버는 보통 write 쪽만 먼저 닫는다 (raw/rfc9112.txt:1539-1555).
- subject: half-close에 쓰는 `shutdown`이 허용 함수 목록에 없다 (raw/subject.md:113).
- 판단: `close()`만 쓴다. 대안으로 응답 후 짧게 읽기만 하다가 닫는다. NGINX의 기본 동작 `lingering_close`가 이 방식이고, 바로 닫는 것은 "프로토콜을 깨므로 쓰지 말라"고 한다 (raw/nginx-core-module.md:888-892). NGINX가 이때 `shutdown`을 쓰는지는 **미확인**. → [[concepts/connection-management]]

### 1.6 HTTP/1.0 기준점 vs HTTP/1.1 기본 동작

- subject: HTTP/1.0을 기준점으로 제안하지만 강제하지 않는다 (raw/subject.md:123).
- RFC 9112: 받은 메시지가 HTTP/1.1이면 persistent가 기본이다 (raw/rfc9112.txt:1350-1351). HTTP/1.1 요청에는 Host가 MUST이고 없으면 400 (raw/rfc9112.txt:437-438, raw/rfc9112.txt:445-448). chunked 파싱은 MUST (raw/rfc9112.txt:1071-1072).
- 브라우저는 HTTP/1.1 이상으로 요청한다 (**미확인**, 평가 시 브라우저 네트워크 탭에서 확인 가능, raw/evaluation-sheet-en.md:97-98).
- RFC 1945 (HTTP/1.0): 요청마다 연결을 닫는 것이 기본이다 (raw/rfc1945.txt:420-422). 1.0 서버는 0.9 요청도 이해하고 클라이언트와 같은 버전으로 응답해야 한다 (raw/rfc1945.txt:694-703). status code 목록에 405·411·413·414·505가 없다 (raw/rfc1945.txt:1487-1501). 과제 필수 메서드인 DELETE는 본문이 아니라 "일관되게 구현되지 않은 기능"인 부록 D에 있다 (raw/rfc1945.txt:3185-3199, raw/rfc1945.txt:3223-3226). 즉 과제 요구사항은 HTTP/1.0만으로 다 설명되지 않는다.
- RFC 9110: 서버는 요청의 메이저 버전 이하에서 자신이 따르는 가장 높은 버전으로 응답한다 (SHOULD, raw/rfc9110.txt:2054-2056). HTTP/1.0 요청에 `HTTP/1.1`로 응답해도 된다.
- 판단: 응답은 `HTTP/1.1`로 보내고, HTTP/1.0 요청은 `keep-alive`가 없으면 응답 후 닫는다. HTTP/0.9는 지원하지 않고 400 (raw/rfc9112.txt:2215-2221) → [[sources/rfc1945]].
- 판단: 응답 버전을 HTTP/1.1로 하면 위 규칙을 따라야 한다. 다만 subject가 chunked 처리(raw/subject.md:179)를 요구하므로 어느 쪽이든 HTTP/1.1 파싱 규칙 대부분은 필요하다. → [[concepts/connection-management]], [[concepts/request-parsing]]

### 1.7 REMOTE_ADDR — 허용 함수 목록 vs RFC 3875

- RFC 3875: `REMOTE_ADDR`는 클라이언트 네트워크 주소로 MUST (raw/rfc3875.txt:836-837).
- subject: 주소를 문자열로 바꾸는 `inet_ntoa`·`inet_ntop`가 허용 함수 목록에 없다. `ntohl`은 있다 (raw/subject.md:113).
- 판단: `accept`로 받은 주소를 `ntohl`로 바꾼 뒤 점 표기 문자열을 직접 만든다. 모순이라기보다 구현 제약이다. → [[concepts/cgi]]

### 1.8 read/write 외 함수의 errno 확인 (질문)

- POSIX: `poll()`은 실패하면 -1을 돌려주고 errno를 설정한다. 원인은 `EAGAIN`, `EINTR`(신호 수신), `EINVAL`이다 (raw/posix-poll.md:114, raw/posix-poll.md:120-132).
- subject: errno 금지는 **read 또는 write 뒤**에 한정된다 (raw/subject.md:133). 평가표도 read/recv/write/send 뒤의 errno 검사를 0점으로 한다 (raw/evaluation-sheet-en.md:57).
- 두 문장의 대상에 `poll()`은 없다. 그래서 `poll()` 실패 원인을 errno로 보는 것이 허용되는지는 문구만으로 판단할 수 없다 (**미확인**).
- 판단: errno를 보지 않고도 처리할 수 있다. `poll()`이 -1을 돌려주면 로그만 남기고 다음 루프로 넘어간다. 평가표는 errno를 로그에 남기는 것은 허용한다 (raw/evaluation-sheet-en.md:57). 이렇게 하면 해석 문제를 피할 수 있다.
- `bind()`도 같은 성격이다. 실패하면 -1을 돌려주고 errno를 설정한다 (raw/posix-bind.md:58). 원인(`EADDRINUSE` 등)을 `strerror`로 출력하는 것은 read/write 뒤가 아니므로 금지 대상이 아닌 것으로 보인다. `strerror`도 허용 함수다 (raw/subject.md:113) (**판단**). 출력만 하고 동작은 바꾸지 않으면(실패하면 종료) 평가표의 "로그는 허용" 범위에도 들어간다.

### 1.9 waitpid 상태 매크로 (질문)

- POSIX: `waitpid`가 돌려준 status는 `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, `WTERMSIG` 같은 매크로로 해석한다 (raw/posix-waitpid.md:72-92).
- subject: 매크로·헬퍼 사용을 명시적으로 허용한 것은 `poll()`과 그 동등 함수뿐이다 (raw/subject.md:138). `waitpid`는 허용 함수지만 (raw/subject.md:113) 그 매크로에 대한 언급은 없다.
- 판단 보류 (**미확인**). 매크로 없이도 CGI 처리는 가능하다. 성공 여부는 CGI 출력 형식으로 판단하고 (→ [[concepts/cgi]] 5절), status는 로그용으로만 쓴다.

### 1.10 `/dev/urandom` 읽기와 poll() 예외 (질문)

- 세션 식별자는 추측하기 어려워야 한다 (**판단**: 추측할 수 있으면 남의 세션을 쓸 수 있다. RFC 6265는 서버가 흔히 식별자만 쿠키에 넣는다고 설명할 뿐 이 요구를 직접 적지 않는다, raw/rfc6265.txt:1716-1720). 허용 함수에는 난수 함수가 없다 (raw/subject.md:113).
- `open`·`read`로 `/dev/urandom`을 읽을 수는 있다. 그러나 `poll()` 없이 읽어도 되는 예외는 "일반 디스크 파일"이다 (raw/subject.md:134). `/dev/urandom`은 장치 파일이라 이 예외에 들어가는지 불분명하다 (**미확인**).
- 판단 보류. 확인 방법: 동료·평가자 합의. 보너스 항목이라 필수 평가에는 영향이 없다.

### 1.11 fcntl 허용 목록 vs POSIX

- subject: `fcntl()`은 `F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC`로만 사용 가능 (raw/subject.md:155-157).
- **`F_GETFL` 없음:** POSIX는 플래그를 `F_GETFL`로 읽고 수정한 뒤 쓰라고 권한다. 잊는 것이 흔한 실수이고, 구현이 기본으로 다른 플래그를 켜 두는 경우도 있다고 한다 (raw/posix-fcntl.md:391). 허용 목록으로는 `F_SETFL`에 `O_NONBLOCK`만 주는 방법뿐이다.
- **`FD_CLOEXEC`에는 `F_SETFD`가 필요:** `FD_CLOEXEC`는 파일 상태 플래그가 아니라 fd 플래그라서 `F_SETFD`로 설정한다 (raw/posix-fcntl.md:50-52). `F_SETFD`는 허용 목록에 없다. 목록의 `F_SETFL`과 `FD_CLOEXEC`는 함께 쓸 수 없는 조합이다.
- 판단: non-blocking은 `fcntl(fd, F_SETFL, O_NONBLOCK)`로 한다. `FD_CLOEXEC` 대신 CGI 자식에서 `execve` 전에 필요 없는 fd를 `close`한다 → [[concepts/cgi]]. `F_SETFD`를 써도 되는지는 **미확인**(평가자 합의).

### 1.12 POSIX `poll()` vs macOS 실측

- POSIX: `POLLHUP`은 `events`에 넣지 않아도 조건이 맞으면 설정해야 한다 (raw/posix-poll.md:86).
- 실측: macOS는 `events=0`인 pipe 읽는 쪽에 쓰는 쪽이 닫혀도 `POLLHUP`을 보고하지 않았다. Ubuntu는 보고했다 (raw/os-observed-pipe-poll.md:180, raw/os-observed-pipe-poll.md:195).
- 판단: 평가는 Ubuntu에서 한다. 다 쓴 fd는 `events=0`으로 두지 말고 poll 목록에서 뺀다. 그러면 두 동작 어느 쪽이든 영향이 없다 → [[sources/os-observed-pipe-poll]].

## 2. 평가표에만 있는 기준

| 기준 | 근거 | 관련 페이지 |
|---|---|---|
| `poll()`이 메인 루프 안에 | raw/evaluation-sheet-en.md:53 | [[concepts/io-multiplexing]] |
| socket I/O 에러 시 클라이언트 제거 | raw/evaluation-sheet-en.md:55 | [[concepts/io-multiplexing]] |
| 반환값 `-1`과 `0` 모두 처리 | raw/evaluation-sheet-en.md:56 | [[concepts/io-multiplexing]] |
| 디스크 파일 동기 I/O가 이벤트 루프를 막지 않음 | raw/evaluation-sheet-en.md:59 | [[concepts/io-multiplexing]] |
| README 필수 요소 누락 시 0점 | raw/evaluation-sheet-en.md:44 | [[concepts/build-and-submission]] |
| 알 수 없는 메서드 처리 | raw/evaluation-sheet-en.md:80 | [[concepts/http-features]] |
| CGI 무한 루프·에러 스크립트 | raw/evaluation-sheet-en.md:91 | [[concepts/cgi]] |
| 같은 port 다중 프로그램 실행에도 일관 동작·크래시 없음 | raw/evaluation-sheet-en.md:109 | [[concepts/configuration-file]] |
| `siege -b` availability 99.5% 초과, 무한 실행 | raw/evaluation-sheet-en.md:114, raw/evaluation-sheet-en.md:117 | [[concepts/testing]] |
| 메모리 누수 검사 | raw/evaluation-sheet-en.md:25 | [[concepts/resilience]] |

## 3. subject에만 있는 기준

| 기준 | 근거 |
|---|---|
| 설정 파일을 인자 **또는 기본 경로**에서 읽기 | raw/subject.md:127 |
| 기본 에러 페이지 내장 | raw/subject.md:143 |
| `fork`는 CGI 전용 | raw/subject.md:144 |
| chunked 요청 un-chunk 후 CGI에 전달 | raw/subject.md:179 |
| `fcntl()` 플래그 제한 | raw/subject.md:157 |

## 4. 한국어 정리본(구버전) vs 영어 원문

| 항목 | 정리본 | 영어 원문 |
|---|---|---|
| README 검사 | 없음 | 필수 요소 누락 시 0점 (raw/evaluation-sheet-en.md:35-44) |
| readiness 1회당 I/O 횟수 | 클라이언트당 read 1번 또는 write 1번 (raw/evaluation-sheet.md:50) | EAGAIN까지 반복 허용 (raw/evaluation-sheet-en.md:54) |
| errno | 검사 시 0점 (raw/evaluation-sheet.md:54) | 같음. 단 로그는 허용 (raw/evaluation-sheet-en.md:57) |
| 디스크 파일 | 언급 없음 | 예외로 명시, 루프를 막지 않는지 확인 (raw/evaluation-sheet-en.md:58-59) |
| 여러 서버 설정 | 다른 포트 + 다른 호스트네임(`curl --resolve`) (raw/evaluation-sheet.md:64-68) | 다른 interface와 port (raw/evaluation-sheet-en.md:68) |
| 같은 포트 중복 | 동작하면 안 됨 (raw/evaluation-sheet.md:112) | 에러. virtual host 구현 시 허용 (raw/evaluation-sheet-en.md:108) |
| 공통 포트 동시 실행 | "서로 다른 설정의 서버" (raw/evaluation-sheet.md:113) | webserv **프로그램 여러 개**를 다른 설정 파일로 (raw/evaluation-sheet-en.md:109) |
| siege 설치 | homebrew (raw/evaluation-sheet.md:43) | apt (raw/evaluation-sheet-en.md:48) |
| siege 부하 조건 | 없음 | `-c`/`-d`/`-r`로 제한, 평가 대상과 합의 (raw/evaluation-sheet-en.md:118) |
| 첨부 테스터 | `ubuntu_tester`, `ubuntu_cgi_tester` 포함 (raw/evaluation-sheet.md:32-33) | `tester`, `cgi_tester`만 (raw/evaluation-sheet-en.md:29-31) |

## 5. 원문으로 해소된 미확인 항목

| 항목 | 결과 |
|---|---|
| "Norm 에러" 플래그 | 원문에도 있다 (raw/evaluation-sheet-en.md:23). 정리 과정의 오류가 아니다. webserv subject에는 Norm 규칙이 없으므로(raw/subject.md:44-52) 공통 템플릿 문구로 보인다 |
| body 제한 `curl` 명령의 URL 누락 | 원문에도 URL이 없다 (raw/evaluation-sheet-en.md:70) |
| 1.6 세 번째 항목의 의미 | webserv 프로그램 여러 개를 다른 설정 파일로 동시에 실행하는 것 (raw/evaluation-sheet-en.md:109) |

## 6. 남은 미확인

subject·평가표 해석에 관한 질문만 모았다. 동작 확인이 필요한 항목(NGINX·OS 실측)은 [[source-wishlist]] 4-1·5-1절.

- 42 EvalHub 원문이 intra의 현재 평가표와 같은지 → [[sources/evaluation-sheet-en]]
- 허용 함수 목록이 `<ctime>`, `exit` 등 표준 라이브러리에도 적용되는지 (Date 헤더, CGI 자식 종료, 리스팅 시간 표시, 1.4절)
- `shutdown` 없이 TCP reset 문제를 줄이는 방법. NGINX `lingering_close` 방식(읽고 버리다가 닫기)을 따를 수 있으나 NGINX가 `shutdown`을 함께 쓰는지는 모름 (1.5절)
- read/write 외 함수(`poll`, `bind`)의 실패 원인을 errno로 봐도 되는지 (1.8절)
- `waitpid` 상태 매크로를 써도 되는지 (1.9절)
- 세션 식별자용 `/dev/urandom` 읽기가 `poll()` 예외에 들어가는지 (1.10절)
- `FD_CLOEXEC`를 위해 `F_SETFD`를 써도 되는지 (1.11절)
- `fcntl()` 허용이 "For macOS only" 절(raw/subject.md:153-157)에 있는데, Ubuntu 평가에서도 인정되는지. 허용 함수 목록(raw/subject.md:113)에는 있다 → [[concepts/io-multiplexing]]
