---
title: NGINX 소스 — lingering close (ngx_http_request.c, ngx_socket.h)
type: source
sources: [raw/nginx-src-ngx_http_request.c, raw/nginx-src-ngx_socket.h, raw/rfc9112.txt, raw/subject.md]
updated: 2026-10-25
---

# NGINX 소스 — lingering close (`ngx_http_request.c`, `ngx_socket.h`)

원본: NGINX `release-1.30.6` 태그(커밋 `fb0e979c6dd63c018958b41eeb844947c5c21264`)의 두 파일을 2026-10-16에 받아 그대로 저장했다. C 소스라 변환하지 않았다. 버전은 [[sources/nginx-observed-encoded-slash]] 실측에 쓴 nginx/1.30.6과 같다.

| raw 파일 | 받은 URL | sha256 |
|---|---|---|
| `raw/nginx-src-ngx_http_request.c` | <https://raw.githubusercontent.com/nginx/nginx/release-1.30.6/src/http/ngx_http_request.c> | `6aa0cff0840047d8c073514bfa668d87cb787f85a1ea0a7b1759fa560c711088` |
| `raw/nginx-src-ngx_socket.h` | <https://raw.githubusercontent.com/nginx/nginx/release-1.30.6/src/os/unix/ngx_socket.h> | `240097e95d918622678a2f89ea6b0b42be06d89fea3dcc7bbcf4c173d51b25fa` |

- 태그와 커밋은 받을 때 `git ls-remote`로 본 값이고 raw 파일에는 없다.
- 받은 목적: [[concepts/connection-management]]의 **미확인** — NGINX가 `lingering_close`에서 `shutdown`을 쓰는지. 문서에는 동작만 있고 구현은 없다 → [[sources/nginx-core-module]].

## 과제와 관련된 부분

| 부분 (줄) | 내용 |
|---|---|
| 요청 종료 후 분기 (2955-2987) | 본문을 다 읽지 못했으면 keep-alive를 끄고 `lingering_close` 표시를 켠다 (2955-2958). keep-alive가 가능하면 keep-alive로 간다 (2960-2974). 아니면 설정이 `always`이거나, `on`이면서 표시가 켜졌거나 버퍼에 읽지 않은 데이터가 있거나 읽기 준비 상태이거나 파이프라인 요청이 있을 때 lingering close로 간다 (2976-2985). 그 밖에는 바로 닫는다 (2987) |
| `ngx_http_set_lingering_close` (3641-3708) | 읽기 핸들러를 lingering 핸들러로 바꾸고 (3675-3676), 쓰기 핸들러를 빈 핸들러로 바꾼다 (3683-3684). **`ngx_shutdown_socket(c->fd, NGX_WRITE_SHUTDOWN)`을 호출**하고 실패하면 닫는다 (3693-3698). `lingering_timeout` 타이머를 걸고, 이미 읽을 수 있으면 바로 핸들러를 부른다 (3703-3707) |
| `ngx_http_lingering_close_handler` (3727-3767) | 타임아웃이면 닫는다 (3727-3730). `lingering_time`이 지났으면 닫는다 (3732-3736). 읽을 수 있는 동안 버퍼로 `recv`를 반복하고, 0이나 오류면 닫는다 (3738-3752). 남은 시간과 `lingering_timeout` 중 작은 값으로 타이머를 다시 건다 (3761-3767) |
| `ngx_socket.h` 매크로 | `NGX_WRITE_SHUTDOWN`은 `SHUT_WR` (raw/nginx-src-ngx_socket.h:15), `ngx_shutdown_socket`은 `shutdown` (raw/nginx-src-ngx_socket.h:66) |

표의 줄 번호는 `raw/nginx-src-ngx_http_request.c` 기준이다.

## 정리

- NGINX의 lingering close는 `shutdown(fd, SHUT_WR)`로 쓰기 쪽만 닫은 뒤 (raw/nginx-src-ngx_http_request.c:3693-3698, raw/nginx-src-ngx_socket.h:15, raw/nginx-src-ngx_socket.h:66), 들어오는 데이터를 읽어 버리다가 상대가 닫거나(0), 오류가 나거나, 시간이 다 되면 닫는다 (raw/nginx-src-ngx_http_request.c:3727-3752).
- RFC 9112가 설명하는 half-close 방식(쓰기 쪽만 먼저 닫고 상대가 닫을 때까지 읽음, raw/rfc9112.txt:1548-1555)과 같은 순서다 (**판단**).
- 요청을 마친 뒤 keep-alive가 가능하면 먼저 keep-alive로 가고, lingering close 조건은 그다음에 본다 (raw/nginx-src-ngx_http_request.c:2960-2987). keep-alive 처리(`ngx_http_set_keepalive`) 안에서도 쓰이는지는 그 함수를 읽지 않아 **미확인**이다.

## 과제 적용 (판단)

- `shutdown`은 subject 허용 함수 목록에 없다 (raw/subject.md:113). 그래서 NGINX 방식 중 "읽고 버리다가 시간이 되면 `close()`"만 따라 할 수 있다. 쓰기 쪽을 먼저 닫아 FIN을 보내는 단계는 빠진다.
- 이 차이 때문에 서버의 FIN은 lingering 읽기를 마치고 `close()`할 때에야 나간다. 그동안 클라이언트는 응답이 끝났다는 것을 `Content-Length`나 chunked 끝으로 알아야 한다. 응답에 길이를 정확히 넣어야 하는 이유가 하나 더 생긴다.
- NGINX처럼 항상 하지 않고, 본문을 다 읽지 않았거나 버퍼에 남은 입력이 있을 때만 lingering 읽기를 하는 조건(2976-2985)을 참고할 수 있다.

> [!note] 범위
> 두 파일만 받았다. `ngx_http_close_request`, `c->recv`(`ngx_unix_recv`), 이벤트 모듈 등 이 함수들이 부르는 코드는 받지 않았다. TLS 경로(`#if (NGX_HTTP_SSL)`, 3655-3673)는 과제와 관계없어 읽지 않았다.
