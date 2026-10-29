---
title: "레슨 3A: URL과 HTTP를 조금 더 자세히"
type: lesson
sources: [raw/rfc3986.txt, raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc6265.txt]
updated: 2026-10-29
---

# 레슨 3A: URL과 HTTP를 조금 더 자세히

이전: [[lessons/03-http-basics]] · 다음: [[lessons/04-poll]]

코드 기준: webserv 커밋 `4db9510`. [[lessons/03-http-basics]]에서 요청·응답의 모양을 봤다. 이 장은 주소창의 URL이 요청 줄로 바뀌는 과정, 헤더의 몇 가지 규칙, 메서드의 성질, 쿠키를 본다.

## 3A.1 URL 해부

> [!example] 쉬운 예
> 편지 주소와 같다. "어떤 배송 방식으로(scheme), 어느 건물 몇 번 문으로(host:port), 몇 층 몇 호(path), 메모(query)". 편지 안의 "3쪽을 보세요"(fragment)는 우체부가 아니라 받는 사람이 쓰는 정보다.

URI는 scheme, authority, path, query, fragment로 나뉜다 (raw/rfc3986.txt:861-865). RFC 3986의 예:

```text
foo://example.com:8042/over/there?name=ferret#nose
\_/   \______________/\_________/ \_________/ \__/
 |           |            |            |        |
scheme   authority       path        query   fragment
```
(raw/rfc3986.txt:884-888)

`http://127.0.0.1:8080/cgi-bin/session.py?logout#top`을 나누면:

| 부분 | 값 | 누가 쓰나 |
|---|---|---|
| scheme | `http` | 브라우저: 어떤 규칙으로 말할지 |
| host | `127.0.0.1` | 브라우저: 어느 컴퓨터에 연결할지 |
| port | `8080` | 브라우저: 어느 포트에 연결할지. 없으면 80 (raw/rfc9110.txt:1100-1102) |
| path | `/cgi-bin/session.py` | 서버: 어떤 자원인지 |
| query | `logout` | 서버(여기서는 CGI의 `QUERY_STRING`) |
| fragment | `top` | 브라우저만. 서버로 보내지 않는다 |

- 서버에 직접 요청할 때 요청 줄의 대상에는 path와 query만 넣는다(origin-form, MUST). path가 비었으면 `/`를 보낸다 (raw/rfc9112.txt:454-460). host와 port는 `Host` 헤더로 따로 간다 (raw/rfc9112.txt:461-462).
- fragment는 클라이언트 쪽 처리용이라 대상 URI에서 빠진다 (raw/rfc9110.txt:2379-2381).

그래서 위 URL은 이런 요청이 된다:

```text
GET /cgi-bin/session.py?logout HTTP/1.1
Host: 127.0.0.1:8080
```

서버는 대상을 `?`에서 잘라 path와 query로 나눈다 (`src/http/RequestParser.cpp:458-482`). 대상에 `#`이나 공백·제어 문자가 있으면 받지 않는다 (`src/http/RequestParser.cpp:82-88`).

## 3A.2 퍼센트 인코딩

> [!example] 쉬운 예
> 주소에 쓸 수 없는 글자(공백, 한글, 구분자로 쓰이는 `/`·`?`)는 "그 글자의 번호표"로 바꿔 쓴다. 공백은 `%20`이다.

- 허용되지 않는 글자나 구분자와 겹치는 글자는 `%` 뒤에 그 바이트 값을 16진수 두 자리로 쓴다. `%20`은 공백이다 (raw/rfc3986.txt:636-644).
- 영문자, 숫자, `-` `.` `_` `~`는 특별한 뜻이 없어 그대로 쓴다 (raw/rfc3986.txt:720-724).
- `%2f`와 `%2F`처럼 16진수의 대소문자만 다르면 같은 URI다 (raw/rfc3986.txt:649-652).

예: `/my file.txt`는 `/my%20file.txt`로 보낸다. 한글 `가`는 UTF-8 바이트 `EA B0 80`이라 `%EA%B0%80`이 된다 **(판단: UTF-8로 바꾼 뒤 인코딩하는 것은 브라우저 동작이고, 이 RFC 절이 정하지는 않는다)**.

서버가 퍼센트 인코딩을 언제·어떻게 푸는지(조각을 나눈 뒤 한 번만, `%2F`·`%00`·root 위 `..`는 400)는 [[lessons/10-routing]] 10.1에서 본다.

## 3A.3 헤더의 몇 가지 규칙

**이름은 대소문자를 가리지 않는다.** 필드 이름은 대소문자를 구분하지 않는다 (raw/rfc9110.txt:1468-1470). `Content-Length`, `content-length`, `CONTENT-LENGTH`는 같은 헤더다. 서버는 이름을 ASCII 소문자로 바꿔 비교한다 (`src/http/HeaderMap.cpp:19-25`).

**Content-Type: 본문이 무엇인지.** 본문의 미디어 타입을 알리고, 그 타입이 데이터 형식과 받는 쪽이 처리할 방법을 정한다 (raw/rfc9110.txt:2930-2936). 브라우저는 이것을 보고 HTML로 그릴지, 이미지로 보여 줄지, 내려받을지 정한다 **(판단)**. 서버는 파일 확장자로 정하고 (`src/http/MimeTypes.cpp:26-34`), 모르는 확장자는 `application/octet-stream`(그냥 바이트)으로 보낸다 (`src/http/MimeTypes.cpp:40`).

| 확장자 | Content-Type |
|---|---|
| `.html` | `text/html` |
| `.css` | `text/css` |
| `.png` | `image/png` |
| `.txt` | `text/plain` |
| 모름 | `application/octet-stream` |

**Date: 응답이 만들어진 시각.** 메시지가 만들어진 날짜·시각을 HTTP-date 형식으로 담는다 (raw/rfc9110.txt:2295-2298). 서버가 이 값을 허용 함수만으로 만드는 방법은 [[analysis/design-decisions]] 10.

## 3A.4 메서드의 성질: safe, idempotent

> [!example] 쉬운 예
> 메뉴판을 보는 것(GET)은 몇 번을 해도 식당에 아무 변화가 없다(safe). "3번 테이블 치워 주세요"(DELETE)는 두 번 말해도 결과는 한 번 말한 것과 같다(idempotent). "음식 하나 더 주세요"(POST)는 말할 때마다 하나씩 더 나온다.

- **safe:** 뜻이 사실상 읽기 전용이라 클라이언트가 서버 상태 변화를 요청하지 않는 메서드다 (raw/rfc9110.txt:3815-3818). GET, HEAD, OPTIONS, TRACE가 safe다 (raw/rfc9110.txt:3834-3835).
- **idempotent:** 같은 요청을 여러 번 보낸 효과가 한 번 보낸 효과와 같은 메서드다. PUT, DELETE와 safe 메서드가 해당한다 (raw/rfc9110.txt:3863-3867).

| 메서드 | safe | idempotent | 이 서버에서 |
|---|---|---|---|
| GET | O | O | 파일·목록·CGI |
| HEAD | O | O | GET과 같은 머리, 본문 없음 |
| POST | X | X | 업로드, CGI |
| DELETE | X | O | 파일 삭제 |

> [!tip] 왜 이렇게?
> 사이트 루트처럼 `limit_except`가 없는 location은 GET·HEAD만 받는다 ([[analysis/design-decisions]] 16). 평가자가 아무 곳에나 POST·DELETE를 보내도 파일이 바뀌지 않게, 상태를 바꾸는 메서드는 설정에서 연 곳에서만 받는다.

## 3A.5 쿠키와 세션

> [!example] 쉬운 예
> 놀이공원 손목 밴드다. 처음 들어올 때 입구에서 번호가 적힌 밴드(Set-Cookie)를 채워 주고, 놀이기구를 탈 때마다 밴드를 보여 준다(Cookie). 직원은 밴드 번호로 "아, 이 손님 세 번째 타는구나"를 안다.

HTTP는 요청 하나하나가 따로다. 이전 요청을 기억하려면 서버가 응답에 `Set-Cookie`를 넣고, 브라우저가 다음 요청부터 `Cookie` 헤더로 돌려준다. 서버는 그 내용을 무시해도 되고 원하는 용도로 써도 된다 (raw/rfc6265.txt:299-304).

```text
서버 → 브라우저:  Set-Cookie: SID=31d4d96e407aad42
브라우저 → 서버:  Cookie: SID=31d4d96e407aad42
```
(raw/rfc6265.txt:343-349)

이 서버는 쿠키를 C++에서 다루지 않고 CGI 예제(`www/cgi-bin/session.py`)로 보인다 ([[analysis/design-decisions]] 8). 처음 오면 추측하기 어려운 식별자를 만들어 `Set-Cookie`로 주고 (`www/cgi-bin/session.py:52`), 로그아웃(`?logout`)이면 지난 날짜의 `Expires`로 쿠키를 지운다 (`www/cgi-bin/session.py:43`). 서버는 CGI가 출력한 `Set-Cookie` 줄을 그대로 전달한다. 자세한 규칙은 [[concepts/bonus]] "쿠키와 세션".

## 3A.6 주소창에 URL을 치면 일어나는 일

앞 장들을 한 줄로 이으면 이렇다 **(판단: 각 단계는 링크한 장의 내용을 요약한 것)**.

1. 브라우저가 URL을 나눈다 (3A.1). `127.0.0.1`은 이미 IP라 이름 찾기(DNS)가 필요 없다.
2. `127.0.0.1:8080`에 TCP 연결을 맺는다. 서버는 `poll`이 알려 준 listen 소켓에서 `accept`한다 ([[lessons/02b-tcp-connections]] 2B.2, [[lessons/04-poll]]).
3. 요청 줄과 헤더를 보낸다 (3A.1, [[lessons/03-http-basics]] 3.1).
4. 서버가 요청을 해석하고 ([[lessons/09-request-parser]]), 설정의 location을 골라 파일·목록·CGI·업로드 중 하나로 처리한다 ([[lessons/10-routing]]).
5. 응답이 오면 브라우저는 `Content-Type`을 보고 그린다 (3A.3). HTML 안에 CSS·이미지가 있으면 같은 연결(keep-alive)로 다시 요청한다 ([[lessons/03-http-basics]] 3.4).

> [!info] 평가 때
> - 평가자가 브라우저로 서버를 열 수 있다. `Content-Type`이 틀리면 HTML이 글자 그대로 보이거나 이미지가 깨진다. 개발자 도구의 Network 탭에서 요청·응답 헤더를 바로 보여 줄 수 있다.
> - 쿠키 보너스를 보여 줄 때는 `/cgi-bin/session.py`를 두 번 열어 방문 수가 1 → 2로 느는 것과, 개발자 도구에서 `Cookie` 헤더를 보여 준다 ([[analysis/test-plan]] E-07).

> [!question]- 확인 문제 1: `http://127.0.0.1:8080/a.html#intro`를 열면 서버는 `#intro`를 받을까?
> 받지 않는다. fragment는 클라이언트 쪽 처리용이라 대상 URI에서 빠진다 (raw/rfc9110.txt:2379-2381). 요청 줄은 `GET /a.html HTTP/1.1`이다.

> [!question]- 확인 문제 2: 요청에 `content-length: 5`(소문자)가 왔다. 서버는 이것을 `Content-Length`로 읽어야 할까?
> 그렇다. 필드 이름은 대소문자를 구분하지 않는다 (raw/rfc9110.txt:1468-1470).

> [!question]- 확인 문제 3: DELETE를 두 번 보내면 두 번째 응답은 404일 수 있다. 그래도 idempotent일까?
> 그렇다. idempotent는 서버에 남는 효과가 같다는 뜻이다 (raw/rfc9110.txt:3863-3867). 파일이 지워진 상태는 한 번 보낸 것과 같다. 응답 코드까지 같아야 한다는 뜻은 아니다 **(판단)**.
