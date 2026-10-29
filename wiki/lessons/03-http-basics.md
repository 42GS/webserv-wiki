---
title: "레슨 3: HTTP라는 약속"
type: lesson
sources: [raw/subject.md, raw/rfc9112.txt, raw/rfc9110.txt, raw/evaluation-sheet-en.md]
updated: 2026-10-29
---

# 레슨 3: HTTP라는 약속

이전: [[lessons/02b-tcp-connections]] · 다음: [[lessons/03a-urls-and-http-details]]

> [!example] 쉬운 예
> 식당 주문서를 생각하자. 맨 윗줄에 "무엇을, 어느 메뉴로, 어떤 양식으로" 쓰고, 그 아래 "포장해 주세요", "맵지 않게" 같은 메모를 줄마다 쓴다. 빈 줄을 하나 남기고 그 밑에 첨부물을 붙인다. 식당은 같은 모양의 영수증을 돌려준다. HTTP가 바로 이런 주문서와 영수증 양식이다.

## 3.1 요청의 모양

```text
POST /upload/ HTTP/1.1          ← 요청 줄: 메서드 SP 대상 SP 버전
Host: 127.0.0.1:8080            ← 헤더 줄: 이름 ":" 값
Content-Type: text/plain
Content-Length: 5
                                ← 빈 줄 = 머리(head) 끝
hello                           ← 본문(body), 정확히 5바이트
```
(줄 끝은 CRLF = `\r\n`)

- **메서드**: 무엇을 하고 싶은지. 과제 필수는 GET, POST, DELETE다 (raw/subject.md:147). 우리는 HEAD도 지원한다 ([[analysis/design-decisions]] 5).
- **대상**: `/path?query` 꼴. `?` 뒤는 query다.
- **Host 헤더**: HTTP/1.1에서는 꼭 있어야 한다. 없거나 두 번 오거나 값이 이상하면 400을 보내야 한다 (MUST, RFC 9112 3.2, raw/rfc9112.txt:445-448).

## 3.2 응답의 모양과 상태 코드

```text
HTTP/1.1 404 Not Found          ← 상태 줄: 버전 SP 코드 SP 이유 문구
Content-Type: text/html
Date: Sat, 24 Oct 2026 22:47:17 GMT
Content-Length: 277

<!DOCTYPE html> ...
```

> [!example] 쉬운 예
> 상태 코드는 택배 결과 스티커다. 200 "잘 배달됨", 301 "이사 갔어요, 새 주소는 여기", 404 "그런 집 없어요", 403 "있지만 못 들어가요", 500 "우리 쪽 실수예요".

| 코드 | 뜻 | 우리 서버가 쓰는 곳 (예) |
|---|---|---|
| 200 | 성공 | 파일, 목록, CGI 결과 |
| 201 | 새로 만들어짐 | 업로드 성공 |
| 204 | 성공, 보낼 내용 없음 | DELETE 성공 |
| 301 | 영구 이동 | 끝에 `/` 없는 디렉토리, `return 301` |
| 400 | 잘못된 요청 | 문법 오류, Host 없음, root 위로 가는 `..`, `%2F` |
| 403 | 금지 | 읽을 수 없는 파일, 목록 꺼진 디렉토리, 디렉토리 DELETE |
| 404 | 없음 | 없는 파일, 맞는 location 없음 |
| 405 | 메서드 허용 안 함 | `limit_except`에 없는 메서드 (+ `Allow`) |
| 408 | 요청 시간 초과 | 요청을 보내다 멈춘 손님 |
| 409 | 충돌 | 같은 이름의 업로드 |
| 413 | 내용이 너무 큼 | 본문 상한 초과, 업로드 파일 6개 이상 |
| 414 | URI가 너무 김 | 요청 줄 8192바이트 초과 |
| 415 | 지원하지 않는 형식 | multipart가 아닌 업로드 |
| 431 | 헤더가 너무 큼 | 헤더 16384바이트 초과 |
| 500 | 서버 내부 오류 | 파일 쓰기 실패, 내부 리다이렉트 반복 |
| 501 | 구현 안 됨 | 모르는 메서드(`PUT`, `UNKNOWN`) |
| 502 | 잘못된 게이트웨이 응답 | CGI 출력 형식 오류 |
| 504 | 게이트웨이 시간 초과 | CGI가 10초 안에 끝나지 않음 |
| 505 | HTTP 버전 미지원 | `HTTP/2.0` 요청 |

> [!danger] 주의
> 평가표는 상태 코드가 틀리면 그 항목 점수를 주지 말라고 한다 (raw/evaluation-sheet-en.md:67). 상황별 코드와 근거는 [[concepts/status-codes]].

## 3.3 본문 길이 알리기: Content-Length와 chunked

> [!example] 쉬운 예
> 택배를 보내는 방법이 두 가지다. ① 상자에 "사과 5개"라고 미리 써서 보내기(Content-Length). ② 여러 번 나눠 보내며 매번 "이번엔 3개", "이번엔 2개" 하고 마지막에 "0개 = 끝"을 보내기(chunked).

```text
5\r\n
hello\r\n
6\r\n
 world\r\n
0\r\n            ← 크기 0 = 끝 (크기는 16진수)
\r\n
```

둘이 함께 오면 서버와 중간 장비가 다르게 해석할 수 있다. 이 틈을 이용한 공격이 **request smuggling**이다. 그래서 둘 다 온 요청은 400으로 거부하고 연결을 닫는다. RFC 9112 6.1은 이런 요청을 거부해도 된다(MAY)고 하고, 어느 쪽이든 응답 뒤 연결은 반드시 닫으라(MUST)고 한다 (raw/rfc9112.txt:880-884, `src/http/RequestParser.cpp:536-538`).

## 3.4 연결 유지(keep-alive)

> [!example] 쉬운 예
> 질문 하나 할 때마다 전화를 끊고 다시 거는 대신, 끊지 않고 질문을 여러 개 하는 것이다.

HTTP/1.1은 기본적으로 연결을 유지한다. 요청에 `Connection: close`가 있으면 그 응답 뒤 닫아야 한다 (MUST, RFC 9112 9.6, raw/rfc9112.txt:1521-1526). 요청을 연달아 보내는 것(pipelining)도 받을 수 있고, 응답은 받은 순서대로 보내야 한다 (MUST, RFC 9112 9.3.2, raw/rfc9112.txt:1399-1404). 자세한 규칙은 [[concepts/connection-management]].

> [!question]- 확인 문제: HEAD 요청에 서버는 무엇을 보내야 할까?
> GET이었을 때와 같은 머리만 보내고 내용은 보내면 안 된다 (MUST NOT, RFC 9110 9.3.2, raw/rfc9110.txt:3987-3988). `Content-Length`도 GET이었다면 보냈을 값이다 (raw/rfc9110.txt:3226-3230). 우리 서버는 응답을 다 만든 뒤 `omitBody`만 켠다 (`src/app/RequestProcessor.cpp:313`).
