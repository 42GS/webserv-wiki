---
title: 연결 관리 — keep-alive, 종료, 타임아웃
type: concept
sources: [raw/rfc9112.txt, raw/subject.md, raw/evaluation-sheet-en.md, raw/nginx-core-module.md, raw/siegerc.in, raw/rfc9110.txt, raw/rfc1945.txt, raw/posix-recv.md, raw/nginx-src-ngx_http_request.c, raw/nginx-src-ngx_socket.h, raw/close-after-413-observed.md, raw/ubuntu2204-observed-tools.md]
updated: 2026-10-25
---

# 연결 관리 — keep-alive, 종료, 타임아웃

## persistent connection 판단

HTTP/1.1은 기본이 persistent connection이다. 구현은 이를 지원하는 것이 좋다 (SHOULD, raw/rfc9112.txt:1337-1340).
가장 최근에 받은 메시지를 기준으로 아래 순서대로 판단한다 (raw/rfc9112.txt:1342-1359):

1. `Connection: close`가 있음 → 현재 응답 후 닫음
2. 프로토콜이 HTTP/1.1 이상 → 유지
3. HTTP/1.0이고 `keep-alive` 옵션이 있으며, 수신자가 이를 받아들이기로 함 → 유지
4. 그 외 → 현재 응답 후 닫음

- HTTP/1.0의 기본 동작도 응답 후 서버가 연결을 닫는 것이다 (raw/rfc1945.txt:420-422) → [[sources/rfc1945]].
- 과제 적용 (**판단**, 2026-10-17): HTTP/1.1은 `close` 옵션이 없으면 유지하고, HTTP/1.0은 `keep-alive` 옵션이 있어도 닫는다(3번을 받아들이지 않음). 구현 세부는 [[analysis/design]] 5절.

- persistent를 지원하지 않는 서버는 1xx가 아닌 모든 응답에 `Connection: close`를 보내야 한다 (MUST, raw/rfc9112.txt:1364-1366).
- 연결을 유지하려면 모든 메시지가 자체 길이 정보(`Content-Length` 또는 chunked)를 가져야 한다 (raw/rfc9112.txt:1372-1374). 응답에 길이를 넣지 않으면 연결 종료로 끝을 알려야 하므로 유지할 수 없다 (raw/rfc9112.txt:983-986).

> [!note] siege와 keep-alive
> 평가는 `siege -b`로 availability 99.5% 초과, 무한 실행을 요구한다 (raw/evaluation-sheet-en.md:114, raw/evaluation-sheet-en.md:117). siege 기본 설정 템플릿은 `connection = close`다 (raw/siegerc.in:268). 기본 설정이라면 **요청마다 새 연결**이 생기므로, 연결 재사용보다 `accept`와 응답 후 종료 처리가 중요하다 (**판단**). Ubuntu 22.04 apt 패키지(siege 4.0.7)의 설정도 `connection: close`였다 (raw/ubuntu2204-observed-tools.md:165) → [[sources/ubuntu2204-observed-tools]]. 평가 PC의 설정은 **미확인**이다. 어느 쪽이든 위 판단 규칙을 지키면 된다. Availability가 무엇을 재는지는 [[concepts/testing]] siege 절.

## 요청 본문을 다 읽지 않고 응답할 때 (413 등)

- 서버는 요청 본문 전체를 읽거나, 아니면 응답을 보낸 뒤 연결을 닫아야 한다 (MUST). 그러지 않으면 남은 데이터가 다음 요청으로 잘못 해석된다 (raw/rfc9112.txt:1374-1377).
- 과제 적용: body 크기 제한 초과(raw/subject.md:165)로 413을 보낼 때는 `Connection: close`를 붙이고 닫는 쪽이 단순하다. 413 정의도 연결을 닫을 수 있다고 한다 (raw/rfc9110.txt:7712-7714).

## pipelining

- 클라이언트는 응답을 기다리지 않고 여러 요청을 보낼 수 있다 (MAY, raw/rfc9112.txt:1399-1401).
- 서버는 **받은 순서대로 응답해야 한다** (MUST, raw/rfc9112.txt:1401-1404).
- 과제 적용: 한 번의 `recv`에 요청 두 개가 같이 들어올 수 있다. 첫 요청을 파싱한 뒤 남은 바이트를 버리지 말고 다음 요청의 시작으로 보관한다.

## 타임아웃과 닫힘 감지

- 서버는 보통 비활성 연결에 타임아웃을 둔다. 값은 RFC가 정하지 않는다 (raw/rfc9112.txt:1465-1470).
- NGINX의 타임아웃 종류와 기본값 (참고용):

| NGINX 지시자 | 대상 | 넘으면 | 기본값 | 근거 |
|---|---|---|---|---|
| `client_header_timeout` | 요청 헤더 전체 수신 | 408 | 60s | raw/nginx-core-module.md:342, raw/nginx-core-module.md:347 |
| `client_body_timeout` | 본문의 **연속된 두 read 사이** (전체 전송 시간 아님) | 408 | 60s | raw/nginx-core-module.md:312, raw/nginx-core-module.md:317 |
| `send_timeout` | 응답의 **연속된 두 write 사이** | 연결 닫음 | 60s | raw/nginx-core-module.md:1569, raw/nginx-core-module.md:1574 |
| `keepalive_timeout` | keep-alive 연결의 대기. 0이면 keep-alive 끔 | 연결 닫음 | 75s | raw/nginx-core-module.md:760, raw/nginx-core-module.md:765 |

  과제 적용: 헤더 수신, 본문 수신, 응답 전송, keep-alive 대기를 따로 다루면 "hang 금지"를 상태별로 설명하기 쉽다. CGI 타임아웃은 [[concepts/cgi]] 5절.
- 타임아웃으로 닫을 때는 graceful close를 하고, 상대의 연결 종료 신호를 계속 감시해야 한다 (SHOULD, raw/rfc9112.txt:1472-1476).
- 서버는 언제든 연결을 닫을 수 있다 (MAY, raw/rfc9112.txt:1478-1479).
- 과제 적용: "요청이 무한히 hang하면 안 됨"(raw/subject.md:139), "hanging connection 없음"(raw/evaluation-sheet-en.md:116)을 지키려면 타임아웃이 필요하다. `recv`가 0을 반환하면 상대가 정상 종료한 것이므로 (raw/posix-recv.md:72) 클라이언트를 정리한다. 평가는 반환값 -1과 0을 모두 처리하는지 본다 (raw/evaluation-sheet-en.md:56) → [[concepts/io-multiplexing]].

## 연결 종료

- `Connection: close`를 받은 서버는 그 요청의 최종 응답을 보낸 뒤 종료를 시작해야 하고, 그 뒤 요청은 처리하면 안 된다 (MUST, raw/rfc9112.txt:1521-1526).
- `Connection: close`를 보낸 서버도 그 응답 뒤 종료를 시작해야 한다 (MUST, raw/rfc9112.txt:1528-1531).
- 즉시 `close()`하면 클라이언트가 이미 보낸 데이터 때문에 TCP reset이 생겨, 클라이언트가 마지막 응답을 못 읽을 수 있다 (raw/rfc9112.txt:1539-1546).
- 그래서 서버는 보통 write 쪽만 먼저 닫고(half-close), 상대가 닫을 때까지 읽은 뒤 완전히 닫는다 (raw/rfc9112.txt:1548-1555).

> [!warning] 모순: half-close와 허용 함수
> half-close에 쓰는 `shutdown`은 subject 허용 함수 목록에 없다 (raw/subject.md:113). 이 과제에서는 `close()`만 쓸 수 있다.
> 대안: 응답을 끝까지 보낸 뒤 바로 닫지 않고, 짧은 시간 동안 읽기만 하면서 남은 입력을 버린 뒤 `close()`한다. → [[analysis/subject-vs-evaluation]]
>
> 실측 (10MB 본문에 413, loopback): 바로 `close()`하면 macOS에서 클라이언트 읽기에 `Connection reset by peer`가 났고 curl 1회는 `Send failure: Broken pipe`로 응답을 받지 못했다 (raw/close-after-413-observed.md:359-363, raw/close-after-413-observed.md:370-374). 읽고 버리다가 `close()`하면 Ubuntu 22.04 컨테이너와 macOS에서 12회 모두 413을 받았고, `shutdown`을 쓴 경우와 차이가 없었다 (raw/close-after-413-observed.md:225-256, raw/close-after-413-observed.md:388-419, raw/close-after-413-observed.md:258-289, raw/close-after-413-observed.md:421-452) → [[sources/close-after-413-observed]].
> 본문을 끝까지 보내는 클라이언트에 대해서는 서버가 10MB를 모두 읽어 버렸다 (raw/close-after-413-observed.md:240-244). 버리는 단계에는 무입력 시간과 총 시간의 상한을 둔다 (**판단**, 시험 서버는 1초·5초).
>
> NGINX의 `lingering_close`가 이 방식이다. 연결을 완전히 닫기 전에 클라이언트가 더 보내는 데이터를 기다려 처리한다. 기본값 `on`은 휴리스틱으로 클라이언트가 더 보낼 것 같다고 볼 때만 기다리고, `always`는 항상 기다린다 (raw/nginx-core-module.md:888-890). 기다리는 동안 온 데이터는 읽고 버린다 (raw/nginx-core-module.md:908). 데이터가 `lingering_timeout`(기본 5s) 동안 안 오면 닫고, 오면 읽어 버린 뒤 다시 기다린다. 이 반복은 `lingering_time`(기본 30s)을 넘지 않는다 (raw/nginx-core-module.md:903, raw/nginx-core-module.md:917, raw/nginx-core-module.md:922). 기다리지 않고 바로 닫는 `off`는 "프로토콜을 깨므로 보통은 쓰지 말라"고 한다 (raw/nginx-core-module.md:892).
> NGINX 1.30.6 소스를 보면 lingering close에 들어갈 때 `shutdown(fd, SHUT_WR)`로 쓰기 쪽을 먼저 닫는다 (raw/nginx-src-ngx_http_request.c:3693-3698, raw/nginx-src-ngx_socket.h:15, raw/nginx-src-ngx_socket.h:66). 즉 RFC 9112의 half-close 방식 그대로다 → [[sources/nginx-src-lingering-close]]. 과제에서는 `shutdown` 없이 "읽고 버리다가 `close()`"까지만 따라 할 수 있고, FIN은 `close()` 때 나간다 (**판단**).
> 이 lingering 단계도 non-blocking이어야 하므로 읽기는 `poll()`을 거친다 → [[concepts/io-multiplexing]].

## 관련

- [[concepts/request-parsing]], [[concepts/io-multiplexing]], [[concepts/resilience]], [[sources/rfc9112]], [[sources/nginx-core-module]]
