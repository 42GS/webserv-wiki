---
title: "레슨 11: 응답 만들고 보내기"
type: lesson
sources: [raw/rfc9110.txt, raw/subject.md, raw/nginx-core-module.md]
updated: 2026-10-27
---

# 레슨 11: 응답 만들고 보내기

이전: [[lessons/10-routing]] · 다음: [[lessons/12-upload-delete]]

## 11.1 RequestProcessor: 결정을 응답으로

`src/app/RequestProcessor.cpp:150-155`, `:304-311`:

```cpp
ProcessOutcome RequestProcessor::process(const Request& request, std::time_t now) const {
  const RouteResult route = router_.route(request);
  if (route.kind == RouteResult::CGI) return startCgi(route, request, now);
  return finished(respond(route, request), request, now);
}
// 모든 응답이 마지막에 지나는 곳
void RequestProcessor::finish(Response& response, const std::string& method,
                              bool keepAlive, std::time_t now) const {
  response.omitBody = (method == methods::kHead);               // HEAD면 본문만 빼기
  response.keepAlive = keepAlive;
  response.headers.add(header_name::kDate, formatHttpDate(now)); // Date
  if (!keepAlive) response.headers.add("Connection", "close");
}
```

- **Date**: 시계가 있는 origin server는 2xx·3xx·4xx 응답에 Date를 꼭 보내야 한다 (MUST, RFC 9110 6.6.1, raw/rfc9110.txt:2313-2317). 시계가 있으므로([[lessons/05-startup]]) 모든 응답에 보낸다.
- **HEAD**: 같은 처리를 하고 본문만 보내지 않는다. 에러 응답도 마찬가지다 ([[analysis/test-plan]] R-21).
- **Connection: close**: 닫는 응답에만 붙인다.

## 11.2 에러 페이지

설정한 `error_page` 파일이 있으면 그 파일을, 없거나 못 읽으면 내장 기본 페이지를 보낸다. 과제가 기본 에러 페이지를 요구한다 (raw/subject.md:143). 에러 페이지 URI도 같은 location 규칙(root·alias)으로 파일을 찾는다 (`src/handler/StatusPage.cpp:44-69`).

> [!tip] 왜 NGINX처럼 내부 리다이렉트를 안 하나?
> NGINX의 `error_page`는 그 URI로 내부 리다이렉트한다. 우리는 파일을 직접 읽어 보낸다. 에러 페이지를 처리하다 또 에러가 나도 다시 찾지 않으니 "에러 페이지가 에러를 내는" 순환이 생기지 않는다 ([[analysis/design]] 7절). 페이지 파일은 1MB 상한이다.

## 11.3 정적 파일과 Content-Type

파일이 1MB 이하면 통째로 읽어 본문에 넣고, 더 크면 경로와 크기만 적어 두고 보낼 때 64KB씩 읽는다 (`src/handler/StaticHandler.cpp:15-28`). `Content-Type`은 확장자 표로 정하고, 모르는 확장자는 `application/octet-stream`이다. NGINX 기본은 `text/plain`이지만 (raw/nginx-core-module.md:386) 모르는 내용을 브라우저가 글자로 해석하지 않게 했다. RFC도 Content-Type이 없으면 받는 쪽이 이 타입으로 볼 수 있다고 한다 (raw/rfc9110.txt:2944-2949) **(판단)**.

## 11.4 ResponseStream: 바이트로 바꾸고 조금씩 보내기

`src/http/ResponseStream.cpp:45-70` (줄임):

```cpp
std::string serializeHead(const Response& response) {
  head << "HTTP/1.1 " << response.status << " " << reasonPhrase(response.status) << "\r\n";
  for (각 헤더) if (isSafeFieldValue(value)) head << name << ": " << value << "\r\n";
  if (status != 204 && status != 304) head << "Content-Length: " << length << "\r\n";
  head << "\r\n";
}
```

> [!example] 쉬운 예 — response splitting
> 편지 중간에 누가 몰래 "편지 끝. 새 편지: 당신은 당첨됐습니다"라고 써 넣으면, 받는 사람은 편지가 두 통 온 줄 안다. 헤더 값 안에 줄바꿈(CR, LF)을 넣으면 응답이 둘로 쪼개지는 것도 같은 원리다. 그래서 줄바꿈이 든 헤더 값은 버린다 (`ResponseStream.cpp:35-37`, RFC 9112 11.1이 권하는 방어) → [[concepts/security]].

- **Content-Length를 늘 붙인다**: 응답에 chunked를 쓰지 않는다. 정적 파일은 `stat` 크기, CGI는 끝까지 모은 길이다. 204에는 보내면 안 되고 (MUST NOT, raw/rfc9110.txt:3238-3239), 304는 200이었을 때의 길이만 보낼 수 있는데 (raw/rfc9110.txt:3232-3236) 그 값을 모르니 보내지 않는다.
- **send가 일부만 보내도 된다**: `consume(n)`이 보낸 만큼 앞으로 가고, 메모리 조각을 다 보내면 파일에서 다음 64KB를 읽어 채운다 (`:106-133`).
- **파일이 중간에 줄었다면**: 이미 보낸 Content-Length와 맞출 수 없으니 연결을 끝낸다 (`src/http/Connection.cpp:175-180`).

> [!question]- 확인 문제: 10MB 파일을 보내는 동안 다른 손님은 기다려야 하나?
> 아니다. POLLOUT마다 64KB 이하를 한 번 `send`하고 루프로 돌아오므로 그 사이 다른 연결도 처리된다. 10MB 파일이 그대로 도착하는지 테스트한다 ([[analysis/test-plan]] R-16).
