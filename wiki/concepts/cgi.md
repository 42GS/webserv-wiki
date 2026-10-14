---
title: CGI
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc3875.txt, raw/rfc9112.txt, raw/rfc9110.txt, raw/posix-poll.md, raw/posix-signal-h.md]
updated: 2026-10-15
---

# CGI

근거 문서는 RFC 3875(CGI/1.1)다. IETF 표준이 아닌 Informational RFC라는 점에 주의한다 → [[sources/rfc3875]].
서버는 CGI에 대해 **application gateway**로 동작한다. 요청을 받아 스크립트를 고르고, CGI 요청으로 바꿔 실행한 뒤, CGI 응답을 클라이언트 응답으로 바꾼다 (raw/rfc3875.txt:423-426).

## 과제 요구사항

| 요구 | 근거 |
|---|---|
| 파일 확장자 기반으로 CGI 실행 (예: `.php`) | raw/subject.md:173 |
| 최소 1개 CGI 지원 (`php-CGI`, Python 등) | raw/subject.md:182 |
| 클라이언트의 전체 요청과 인자를 CGI가 볼 수 있어야 함 — 환경 변수 주의 | raw/subject.md:178 |
| chunked 요청은 서버가 un-chunk; CGI는 EOF를 body 끝으로 봄 | raw/subject.md:179 |
| CGI 출력에 `Content-Length`가 없으면 EOF가 끝 | raw/subject.md:180 |
| 상대 경로 접근을 위해 올바른 디렉토리에서 실행 | raw/subject.md:181, raw/evaluation-sheet-en.md:89 |
| `fork`는 CGI 외 용도로 사용 금지 | raw/subject.md:144 |
| GET과 POST 둘 다 테스트 | raw/evaluation-sheet-en.md:90 |
| 에러 스크립트·무한 루프 스크립트에도 크래시 없이, 에러가 보이게 | raw/evaluation-sheet-en.md:91-93 |

## 1. 호출 절차

| 단계 | 할 일 | 근거 |
|---|---|---|
| 1. 스크립트 선택 | 설정의 확장자 규칙으로 CGI 여부 결정. URI 경로의 앞부분이 스크립트, 나머지는 스크립트가 해석할 경로(`PATH_INFO`) | raw/subject.md:173, raw/rfc3875.txt:457-464 |
| 1-1. `..` 처리 | 경로를 script-path와 extra-path로 **나누기 전에** `..`를 제거하거나 해석 | raw/rfc3875.txt:1801-1803 → [[concepts/security]] |
| 2. 본문 준비 | chunked 등 transfer coding을 제거하고 `CONTENT_LENGTH`를 다시 계산 (MUST). 불가능하면 요청 거부 (SHOULD) | raw/rfc3875.txt:1093-1097, raw/subject.md:179 |
| 3. 환경 구성 | 메타변수를 환경 변수로 전달 (아래 표) | raw/rfc3875.txt:1554-1557 |
| 4. 실행 | `fork` 후 자식에서 작업 디렉토리를 스크립트 디렉토리로 바꾸고 (SHOULD) `execve` | raw/rfc3875.txt:1564-1566, raw/subject.md:113 |
| 5. 입력 전달 | 본문은 스크립트의 표준 입력으로. 최소 `CONTENT_LENGTH` 바이트를 읽을 수 있게 해야 함 (MUST) | raw/rfc3875.txt:1073-1075, raw/rfc3875.txt:1081-1083 |
| 6. 출력 수집 | 표준 출력을 **EOF까지 모두** 읽음 (MUST) | raw/rfc3875.txt:1249-1250, raw/rfc3875.txt:1522-1524 |
| 7. 응답 변환 | CGI 응답을 파싱해 HTTP 응답으로 변환 (아래 3절) | raw/rfc3875.txt:1297-1299 |

설계 제약:
- 스크립트와 연결한 pipe는 데이터를 기다릴 수 있는 fd라서 non-blocking + 단일 `poll()` 대상이다 (raw/subject.md:136, raw/evaluation-sheet-en.md:54) → [[concepts/io-multiplexing]]. 표준 입출력 연결은 허용 함수 `pipe`, `dup2`로 한다 (raw/subject.md:113).
- 스크립트는 서버가 본문을 다 받기 전에 실행해도 된다 (raw/rfc3875.txt:533-536).
- **출력 pipe의 `POLLHUP`:** 스크립트가 출력을 다 쓰고 pipe의 쓰는 쪽을 닫으면 `POLLHUP`이 온다. `POLLHUP`은 `POLLIN`과 동시에 올 수 있다 (raw/posix-poll.md:74). 즉 아직 읽지 않은 출력이 남아 있을 수 있으므로, `POLLHUP`을 보자마자 닫지 말고 `read()`가 0(EOF)을 돌려줄 때까지 읽는다. RFC 3875의 "EOF까지 모두 읽음 (MUST)"(raw/rfc3875.txt:1522-1524)을 지키는 방법이다.
- **입력 pipe:** 스크립트가 본문을 다 읽지 않고 종료하면 서버의 입력 pipe 쓰기가 실패할 수 있다. POSIX는 write가 -1을 돌려줄 오류 상태를 `POLLERR`로 보고한다고 한다 (raw/posix-poll.md:70). 읽는 쪽이 모두 닫힌 pipe가 실제로 어떤 비트로 보고되는지는 이 문서에 없다 (**미확인**, OS별로 실측 필요). `POLLERR`와 `POLLHUP` 둘 다 "입력 전달 중단"으로 처리하면 안전하다. 신호(`SIGPIPE`) 처리는 [[concepts/resilience]].
- 스크립트 출력의 헤더·본문 길이에는 제한이 없다. 고정 크기 버퍼를 가정하면 안 된다 (raw/rfc3875.txt:1760-1764).

## 2. 메타변수 (환경 변수)

메타변수 이름은 대소문자를 구분하지 않고, 값은 별도 언급이 없으면 구분한다 (raw/rfc3875.txt:554-555, raw/rfc3875.txt:598-599). 값이 NULL이면 생략할 수 있다 (raw/rfc3875.txt:597-598).

| 변수 | 필수 | 값 | 근거 |
|---|---|---|---|
| `GATEWAY_INTERFACE` | MUST | `CGI/1.1` | raw/rfc3875.txt:700-703, raw/rfc3875.txt:711 |
| `REQUEST_METHOD` | MUST | 요청 메서드 (대소문자 구분) | raw/rfc3875.txt:910-918 |
| `QUERY_STRING` | MUST | URI의 `?` 뒤. URL 인코딩된 그대로. query가 없으면 **빈 문자열** | raw/rfc3875.txt:809-811, raw/rfc3875.txt:830-832 |
| `SCRIPT_NAME` | MUST | 스크립트를 가리키는 URI 경로 (URL 디코딩된 상태). 비어 있어도 설정 | raw/rfc3875.txt:924-931 |
| `SERVER_NAME` | MUST | 요청이 향한 서버 호스트 이름 또는 주소. virtual host라면 Host 헤더로 고른 값 | raw/rfc3875.txt:940-943, raw/rfc3875.txt:959-962 |
| `SERVER_PORT` | MUST | 요청을 받은 포트. 기본 포트여도 설정 | raw/rfc3875.txt:966-974 |
| `SERVER_PROTOCOL` | MUST | 요청 프로토콜과 버전 (예: `HTTP/1.1`) | raw/rfc3875.txt:978-984 |
| `SERVER_SOFTWARE` | MUST | 서버 이름과 버전 | raw/rfc3875.txt:1017-1020 |
| `REMOTE_ADDR` | MUST | 클라이언트 네트워크 주소 | raw/rfc3875.txt:836-837 |
| `CONTENT_LENGTH` | 본문이 있을 때만 MUST | **transfer coding 제거 후** 본문 길이 | raw/rfc3875.txt:637-640 |
| `CONTENT_TYPE` | 요청에 Content-Type이 있으면 MUST | 요청의 Content-Type | raw/rfc3875.txt:692-696 |
| `PATH_INFO` | 경로 정보가 있을 때 | 스크립트 경로 뒤 나머지. URL 디코딩된 상태, 대소문자 보존 (MUST) | raw/rfc3875.txt:715-721, raw/rfc3875.txt:735-736 |
| `PATH_TRANSLATED` | `PATH_INFO`가 있으면 SHOULD | `PATH_INFO`를 서버 문서 경로로 바꾼 값. `PATH_INFO`가 NULL이면 NULL (MUST) | raw/rfc3875.txt:750-754, raw/rfc3875.txt:803-805 |
| `REMOTE_HOST` | SHOULD | 클라이언트 도메인 이름. 없으면 `REMOTE_ADDR` 값으로 대체 가능 | raw/rfc3875.txt:870-872 |
| `HTTP_*` | SHOULD | 요청 헤더. 이름을 대문자로, `-`를 `_`로 바꾸고 `HTTP_`를 붙임 | raw/rfc3875.txt:1030, raw/rfc3875.txt:1038-1042 |
| `AUTH_TYPE`, `REMOTE_USER` | 인증을 할 때만 MUST | 과제에 인증이 없으므로 설정하지 않는다 | raw/rfc3875.txt:609-611, raw/rfc3875.txt:903-906 |
| `REMOTE_IDENT` | MAY | 설정하지 않는다 | raw/rfc3875.txt:876-880 |

`HTTP_*` 세부 규칙:
- 같은 이름의 헤더가 여러 줄이면 의미가 같은 하나의 값으로 합친다 (MUST, raw/rfc3875.txt:1044-1046).
- `Authorization` 같은 인증 헤더와, 다른 변수로 전달되는 `Content-Length`·`Content-Type`은 빼는 것이 좋다 (SHOULD, raw/rfc3875.txt:1051-1055). `Connection`도 뺄 수 있다 (MAY, raw/rfc3875.txt:1055-1057).
- 서버 고유 변수는 `X_` 접두어를 쓴다 (SHOULD, raw/rfc3875.txt:587-588).

> [!note] php-cgi
> `php-cgi`는 이 표 외에 추가 변수를 요구할 수 있다. PHP 매뉴얼로 확인한다 (**미확인**, [[source-wishlist]] P2).

## 3. CGI 응답 파싱

형식: 헤더 필드 1개 이상 + 빈 줄 + 본문(없어도 됨) (raw/rfc3875.txt:1262-1266).

### 헤더 규칙

| 규칙 | 근거 |
|---|---|
| CGI 필드는 `Content-Type`, `Location`, `Status`. **적어도 하나 MUST**, 각각 한 번만 | raw/rfc3875.txt:1355-1360 |
| 필드 이름은 대소문자 구분 없음. 한 줄에 한 필드, 이어지는 줄 없음 (MUST) | raw/rfc3875.txt:1369-1372 |
| `:` 뒤 공백은 허용, 이름과 `:` 사이 공백은 불허 | raw/rfc3875.txt:1372-1374 |
| 줄바꿈(NL)은 LF. 서버는 CRLF도 받아들여야 함 | raw/rfc3875.txt:1579-1580 |
| HTTP로 보낼 때 CGI 줄바꿈을 CRLF로 바꿔야 함 (MUST) | raw/rfc3875.txt:1487-1491 |
| 본문이 있으면 `Content-Type` MUST. 없을 때 서버가 추측하지 말 것 (SHOULD NOT) | raw/rfc3875.txt:1383-1387 |
| 클라이언트 연결에 영향을 주는 헤더는 스크립트가 보내면 안 됨. 서버는 제거할 수 있고 충돌을 해결해야 함 (SHOULD) | raw/rfc3875.txt:1493-1498 |

### Status

- 형식: `Status: 3자리코드 SP reason-phrase` (raw/rfc3875.txt:1447-1450).
- 없으면 200 (raw/rfc3875.txt:1295-1296, raw/rfc3875.txt:1452-1453).
- 서버는 이 값을 HTTP 상태줄의 코드로 쓰고, 응답 버전에 맞게 출력을 고쳐야 한다 (MUST, raw/rfc3875.txt:1297-1299).

### 응답 유형 4가지

| 유형 | 형태 | 서버 동작 | 근거 |
|---|---|---|---|
| document | `Content-Type` [+ `Status`] + 본문 | 그대로 응답. Status 없으면 200 | raw/rfc3875.txt:1283-1299 |
| local redirect | `Location: /경로[?query]`만 (다른 필드·본문 금지) | 서버가 **그 경로로 요청을 다시 처리**해서 응답 | raw/rfc3875.txt:1303-1314 |
| client redirect | `Location: 절대URI`만 | 서버가 **302** 응답 생성 (MUST) | raw/rfc3875.txt:1318-1326 |
| client redirect + 본문 | `Location` + `Status` + `Content-Type` + 본문 | `Status`는 302 또는 다른 리다이렉트 코드 (MUST) | raw/rfc3875.txt:1330-1342 |

- local과 client는 `Location` 값이 `/`로 시작하는 경로인지, 스킴이 있는 절대 URI인지로 구분한다 (raw/rfc3875.txt:1411-1416, raw/rfc3875.txt:1430-1435).
- HEAD 요청에 스크립트가 본문을 보내면 서버가 버린다 (MUST, raw/rfc3875.txt:1143-1145).

## 4. 본문 입출력 경계 (RFC 9112)

- **입력:** chunked 요청은 RFC 9112 7.1.3 방식으로 디코딩한 본문을 넘긴다 (raw/rfc9112.txt:1141-1163). 절차는 [[concepts/request-parsing]] 5절.
- **출력:** 길이 정보가 없는 HTTP 응답이 연결 종료로 끝나는 것과 같은 원리로, CGI 출력은 EOF로 끝난다 (raw/subject.md:180, raw/rfc9112.txt:983-986).
  - 클라이언트 연결을 유지하려면 응답에 자체 길이가 있어야 한다 (raw/rfc9112.txt:1372-1374). CGI 출력을 EOF까지 모은 뒤 `Content-Length`를 붙여 보내거나, 길이 없이 보낸 뒤 연결을 닫는다 → [[concepts/connection-management]].
- **헤더 전달:** CGI 헤더를 응답에 옮길 때 CR·LF 주입을 막는다 → [[concepts/security]] 4절.

## 5. 실패 처리

- 서버는 스크립트 응답에 타임아웃을 둘 수 있고, 넘으면 프로세스를 종료할 수 있다 (MAY, raw/rfc3875.txt:1255-1258). 서버는 언제든 스크립트를 중단할 수 있다 (raw/rfc3875.txt:539-541).
- 스크립트가 규격을 어겨도 서버는 클라이언트에게 올바른 응답을 보낼 책임이 있다 (MUST, raw/rfc3875.txt:433-437).
- 평가: 무한 루프·에러 스크립트에서도 크래시 없이 에러가 보여야 한다 (raw/evaluation-sheet-en.md:91-93).

| 상황 | 코드 | 근거 |
|---|---|---|
| 스크립트가 타임아웃 안에 응답하지 않음 (무한 루프) | 504 | 서버는 gateway (raw/rfc3875.txt:423), 504 정의 (raw/rfc9110.txt:7901-7904) |
| 출력이 CGI 응답 형식에 맞지 않음 (CGI 필드 없음, 헤더 문법 오류 등), 출력 없이 종료 | 502 | raw/rfc3875.txt:1247, raw/rfc3875.txt:1355-1357, 502 정의 (raw/rfc9110.txt:7882-7884) |
| `fork`·`pipe` 실패 등 서버 내부 문제 | 500 | raw/rfc9110.txt:7865-7867 |

- 타임아웃 시 `kill`로 종료하고 `waitpid`로 회수한다 (raw/subject.md:113). 스크립트가 잡거나 무시할 수 없는 시그널은 `SIGKILL`이다 (raw/posix-signal-h.md:186-190). `SIGTERM`은 스크립트가 잡을 수 있다 (raw/posix-signal-h.md:216-220). 회수하지 않으면 좀비 프로세스가 쌓인다. `WNOHANG` 동작은 POSIX 문서로 확인 (**미확인**, [[source-wishlist]] P2).
- 스크립트가 0이 아닌 종료 코드로 끝났지만 출력이 올바른 경우의 처리는 RFC가 정하지 않는다. 출력 기준으로 판단한다 (**판단**).

## 보너스

- 복수 CGI 타입 처리 (raw/subject.md:216, raw/evaluation-sheet-en.md:130) → [[concepts/bonus]]

## 관련

- [[concepts/configuration-file]] — 확장자 → CGI 매핑 설정
- [[concepts/status-codes]], [[concepts/security]], [[concepts/resilience]], [[concepts/io-multiplexing]]
- [[sources/rfc3875]]
