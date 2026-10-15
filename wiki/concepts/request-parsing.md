---
title: 요청 파싱 — 요청줄부터 chunked까지
type: concept
sources: [raw/rfc9112.txt, raw/rfc9110.txt, raw/subject.md, raw/nginx-request-processing.md, raw/posix-recv.md, raw/rfc3986.txt, raw/rfc1945.txt]
updated: 2026-10-15
---

# 요청 파싱 — 요청줄부터 chunked까지

RFC 9112 기준으로 서버가 요청을 읽는 순서대로 정리했다. 단계마다 실패하면 보낼 코드를 붙였다. 코드 선택 전체는 [[concepts/status-codes]].

> [!note] 비동기 수신과의 관계
> 스트림 소켓에는 메시지 경계가 없어서 `recv`는 도착한 만큼만 돌려준다 (raw/posix-recv.md:62). 요청은 여러 번의 `recv`에 나뉘어 도착하고, 요청 여러 개가 한 번에 올 수도 있다. 이 과제에서는 readiness 1회에 I/O 1번이 안전하다 → [[concepts/io-multiplexing]]. 따라서 파서는 "아직 덜 왔음"과 "문법 오류"를 구분해서, 받은 데이터를 버퍼에 쌓아 가며 단계별로 진행해야 한다.

## 0. 기본 원칙

- 일반적인 절차: 시작줄을 읽고 → 빈 줄까지 헤더를 읽고 → 헤더로 본문이 있는지 판단해서 → 본문 길이만큼 읽는다 (raw/rfc9112.txt:264-270).
- 메시지는 Unicode 문자열이 아니라 **US-ASCII 상위 호환 octet 열**로 파싱해야 한다 (MUST). 문자열 처리는 필드를 잘라낸 뒤에만 안전하다 (raw/rfc9112.txt:272-281).
- 메시지 구조: `start-line CRLF *( field-line CRLF ) CRLF [ message-body ]` (raw/rfc9112.txt:239-242).
- 문법에 맞지 않는 octet 열을 받으면 400을 보내고 연결을 닫는다 (SHOULD, raw/rfc9112.txt:319-324).

## 1. 줄 끝 처리

| 규칙 | 근거 |
|---|---|
| 줄 끝은 CRLF. 단 LF 하나도 줄 끝으로 인정하고 앞의 CR을 무시할 수 있음 (MAY) | raw/rfc9112.txt:283-285 |
| LF가 뒤따르지 않는 bare CR을 받으면 그 요소를 무효로 보거나 SP로 바꿔야 함 (MUST) | raw/rfc9112.txt:287-291 |
| 요청줄 앞의 빈 줄(CRLF)은 최소 하나 무시 (SHOULD) | raw/rfc9112.txt:301-303 |

## 2. 요청줄

형식: `method SP request-target SP HTTP-version` (raw/rfc9112.txt:377).

| 규칙 | 실패 시 | 근거 |
|---|---|---|
| 구분자는 SP 하나. 공백 계열 여러 개를 허용하는 관대한 파싱도 가능(MAY)하지만 smuggling 위험이 있음 | — | raw/rfc9112.txt:379-388 |
| 메서드는 대소문자를 구분 | — | raw/rfc9112.txt:404 |
| 구현한 어떤 메서드보다 긴 메서드 | 501 (SHOULD) | raw/rfc9112.txt:391-393 |
| 파싱하려는 어떤 URI보다 긴 request-target | **414 (MUST)** | raw/rfc9112.txt:393-395 |
| 요청줄 길이는 최소 8000 octet까지 지원 권장 | — | raw/rfc9112.txt:397-399 |
| request-target 안에 공백은 허용되지 않음 | 400 또는 올바르게 인코딩한 target으로 301 (SHOULD). 고쳐서 그냥 처리하지 말 것 | raw/rfc9112.txt:425-435 |
| HTTP-version은 `HTTP/` + 숫자.숫자, 대소문자 구분 | 지원하지 않는 메이저 버전은 505 (raw/rfc9110.txt:7908-7911) | raw/rfc9112.txt:333-337 |
| 버전이 없는 요청줄(HTTP/0.9 `GET URI` 형식) | **400**. HTTP/0.9는 지원하지 않음 (**판단**). 요청줄 문법에 버전이 필수이고 잘못된 요청줄은 400 (SHOULD). 0.9처럼 보이는 요청은 대부분 잘못 만든 1.x 요청이다 | raw/rfc9112.txt:377, raw/rfc9112.txt:430-431, raw/rfc9112.txt:2215-2221, raw/rfc1945.txt:1190 |

### request-target 형식

- 일반 요청은 **origin-form**: `absolute-path [ "?" query ]`. 경로가 비면 클라이언트가 `/`를 보낸다 (raw/rfc9112.txt:454-461).
- 서버는 **absolute-form**(`GET http://host/path HTTP/1.1`)도 받아들여야 한다 (MUST, raw/rfc9112.txt:515-516). 이때 origin server는 Host 헤더를 무시하고 target의 host 정보를 쓴다 (MUST, raw/rfc9112.txt:508-511).
- `?` 뒤의 query는 CGI에 전달해야 하는 정보다 (raw/subject.md:178) → [[concepts/cgi]].
- path는 첫 `?`에서 끝난다 (raw/rfc3986.txt:1204-1206). path와 query를 **먼저 나눈 뒤** path만 디코딩한다. 디코딩을 먼저 하면 `%3F`가 `?`로 바뀌어 query 경계로 오해된다 (raw/rfc3986.txt:754-758). 디코딩과 `..` 처리 순서는 [[concepts/security]] "경로 정규화 절차".

## 3. 헤더

| 규칙 | 실패 시 | 근거 |
|---|---|---|
| 형식: `field-name ":" OWS field-value OWS`. 필드 이름은 대소문자 구분 없음 | — | raw/rfc9112.txt:697-701 |
| 필드 이름과 `:` 사이 공백 | **400 (MUST)** | raw/rfc9112.txt:714-719 |
| 값 앞뒤의 OWS는 값에서 제외 | — | raw/rfc9112.txt:722-729 |
| 시작줄과 첫 헤더 사이의 공백으로 시작하는 줄 | 거부하거나 그 줄들을 무시 (MUST) | raw/rfc9112.txt:308-313 |
| obs-fold(공백으로 시작하는 이어지는 줄) | 400으로 거부하거나 SP로 치환 (MUST) | raw/rfc9112.txt:746-751 |
| HTTP/1.1 요청에 Host가 없음, 두 줄 이상, 값이 잘못됨 | **400 (MUST)** | raw/rfc9112.txt:445-448 |

> [!note] Host가 없을 때
> - **HTTP/1.1** 요청: 400 (MUST, raw/rfc9112.txt:445-448).
> - **HTTP/1.0** 요청: RFC 9112의 400 규칙은 HTTP/1.1 요청에만 적용된다 (raw/rfc9112.txt:445-446). NGINX는 Host가 없는 요청을 그 포트의 default server로 보낸다 (raw/nginx-request-processing.md:34). 이 경우 default server로 처리한다.
> - NGINX가 Host 없는 HTTP/1.1 요청에 실제로 400을 보내는지는 문서에 없지만, RFC 9112가 400을 MUST로 정하므로 이 과제는 400으로 확정한다.
> - server 선택 순서는 [[concepts/configuration-file]] "server 선택" 절.

- 헤더 전체 크기 상한은 RFC가 정하지 않는다. 길이 공격 대비로 서버가 정한다 → [[concepts/security]].

## 4. 본문 길이 결정 (요청)

RFC 9112 6.3의 순서 중 요청에 해당하는 것 (raw/rfc9112.txt:914-1000):

| 순서 | 조건 | 처리 | 근거 |
|---|---|---|---|
| 1 | `Transfer-Encoding`과 `Content-Length`가 둘 다 있음 | TE가 우선. 에러로 다루는 게 좋다. 거부하거나 TE로만 처리하되, **응답 후 연결을 닫음 (MUST)** | raw/rfc9112.txt:930-934, raw/rfc9112.txt:880-884 |
| 2 | TE가 있고 마지막 coding이 chunked | chunked를 디코딩해서 길이 결정 | raw/rfc9112.txt:940-943 |
| 3 | TE가 있는데 마지막 coding이 chunked가 아님 | **400 후 연결 닫음 (MUST)** | raw/rfc9112.txt:950-954 |
| 4 | TE 없이 `Content-Length` 값이 잘못됨 | **400 후 연결 닫음 (MUST)**. 같은 값의 쉼표 목록(`42, 42`)만 예외 | raw/rfc9112.txt:956-965 |
| 5 | 올바른 `Content-Length`만 있음 | 그 값만큼 읽음. 다 오기 전에 연결이 끊기거나 타임아웃이면 불완전한 메시지로 보고 연결을 닫음 (MUST) | raw/rfc9112.txt:973-978 |
| 6 | 둘 다 없음 | **본문 길이 0** | raw/rfc9112.txt:980-981 |

- 요청은 연결 종료로 경계를 정하지 않는다 (raw/rfc9112.txt:994-997).
- `Content-Length` 숫자 변환 시 오버플로를 막아야 한다 (raw/rfc9110.txt:3251-3254).
- 모르는 transfer coding은 501 (SHOULD, raw/rfc9112.txt:851-852).
- HTTP/1.0 요청에 `Transfer-Encoding`이 있으면 framing 오류로 보고 처리 후 연결을 닫음 (MUST, raw/rfc9112.txt:886-889).
- HTTP/1.0에서는 본문이 있는 요청에 `Content-Length`가 필수이고, POST의 길이를 알 수 없으면 400이다 (SHOULD, raw/rfc1945.txt:1657-1663, raw/rfc1945.txt:1763-1765). 그래서 **HTTP/1.0 POST에 `Content-Length`가 없으면 400**, HTTP/1.1이면 위 6번대로 본문 길이 0으로 처리한다 (**판단**) → [[sources/rfc1945]].
- 본문이 body 크기 제한(raw/subject.md:165)을 넘으면 413 → 남은 본문 처리는 [[concepts/connection-management]].

> [!note] 411은 언제 쓰나
> 411은 "본문은 있는데 `Content-Length`가 없는" 요청, 즉 chunked 요청을 거부할 때 쓸 수 있다 (MAY, raw/rfc9112.txt:999-1000). subject는 chunked를 풀어서 처리하라고 요구하므로 (raw/subject.md:179) 이 과제에서 411을 쓸 일은 사실상 없다.

## 5. chunked 디코딩

형식 (raw/rfc9112.txt:1054-1064):

```
chunked-body = *chunk last-chunk trailer-section CRLF
chunk        = chunk-size [ chunk-ext ] CRLF chunk-data CRLF
chunk-size   = 1*HEXDIG
last-chunk   = 1*("0") [ chunk-ext ] CRLF
```

| 규칙 | 근거 |
|---|---|
| chunk-size는 16진수. 크기 0인 chunk 뒤 trailer, 빈 줄로 끝남 | raw/rfc9112.txt:1066-1069 |
| 매우 큰 16진수 값의 오버플로를 막아야 함 (MUST) | raw/rfc9112.txt:1078-1081 |
| 모르는 chunk extension은 무시 (MUST). 총 길이를 제한하고 넘으면 4xx | raw/rfc9112.txt:1108-1113 |
| trailer는 선택적으로 버려도 됨 (MAY). 허용되지 않은 필드를 헤더에 합치면 안 됨 | raw/rfc9112.txt:1126-1134 |
| 크기 0 chunk가 오지 않았으면 불완전한 본문 | raw/rfc9112.txt:1269-1271 |

디코딩 의사코드는 원문 7.1.3에 있다 (raw/rfc9112.txt:1141-1163). 디코딩 후 길이를 `Content-Length`로 삼고 `Transfer-Encoding`에서 chunked를 뺀다 (raw/rfc9112.txt:1162-1163). CGI에 넘길 때도 이렇게 un-chunk한 본문을 쓴다 (raw/subject.md:179) → [[concepts/cgi]].

## 6. 불완전한 요청

- 취소나 타임아웃으로 요청이 불완전하면, 연결을 닫기 전에 에러 응답을 보낼 수 있다 (MAY, raw/rfc9112.txt:1253-1255). 상황에 맞는 코드는 408 (raw/rfc9110.txt:7641-7643).

## 응답 상태줄

- 형식: `HTTP-version SP status-code SP [ reason-phrase ]` (raw/rfc9112.txt:652).
- reason-phrase가 없어도 status-code 뒤의 공백은 보내야 한다 (MUST, raw/rfc9112.txt:690-693).

## 관련

- [[concepts/connection-management]], [[concepts/status-codes]], [[concepts/security]], [[sources/rfc9112]]
