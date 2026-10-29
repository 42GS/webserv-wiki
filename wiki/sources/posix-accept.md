---
title: POSIX accept() — 대기열의 연결 하나를 꺼내 새 소켓 fd로 돌려줌
type: source
sources: [raw/posix-accept.md]
updated: 2026-10-29
---

# POSIX accept()

원본: `raw/posix-accept.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/accept.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-accept.md:1-3). 원본 HTML은 `raw/posix-accept.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-accept.md:5-7). 같은 페이지에 Issue 8에서 더해진 `accept4()`가 있다.

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음, 구조 차이 없음.

## 과제와 관련된 부분

listen 소켓이 POLLIN이면 서버는 `accept`를 한 번 부른다 (`webserv/src/core/Listener.cpp:72`). 기초 설명은 [[lessons/02b-tcp-connections]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (28) | 대기열의 첫 연결을 꺼내 새 소켓과 새 fd를 만든다 | [[lessons/02b-tcp-connections]] |
| DESCRIPTION (44) | `address`에 상대 주소를 담는다 | [[concepts/cgi]] `REMOTE_ADDR` |
| DESCRIPTION (50) | 대기열이 비었을 때: blocking이면 기다리고, non-blocking이면 `EAGAIN`으로 실패 | [[lessons/04-poll]] |
| DESCRIPTION (52) | 받은 소켓은 다른 연결을 받지 못하고, 원래 소켓은 계속 받는다 | [[lessons/07-event-loop]] |
| DESCRIPTION (54) | 받은 소켓이 `O_NONBLOCK`을 물려받는지는 구현마다 다름 | 아래 "과제 적용" |
| ERRORS (102-104) | fd를 다 쓰면 `EMFILE` | [[concepts/resilience]] |
| APPLICATION USAGE (152) | 연결이 오면 `select()`는 그 소켓을 읽기 가능으로 알린다 | [[sources/posix-poll]] |

## 핵심

- `accept()`는 대기 중인 연결 대기열에서 첫 연결을 꺼내, 같은 종류의 새 소켓을 만들고 그 소켓의 새 fd를 할당한다 (raw/posix-accept.md:28).
- `address`가 널이 아니면 받은 연결의 상대 주소와 그 길이를 담는다 (raw/posix-accept.md:44).
- 대기열이 비었을 때 소켓에 `O_NONBLOCK`이 없으면 연결이 올 때까지 막히고, 있으면 `EAGAIN` 또는 `EWOULDBLOCK`으로 실패한다 (raw/posix-accept.md:50).
- 받은 소켓은 다른 연결을 받지 못한다. 원래 소켓은 열린 채로 남아 계속 연결을 받는다 (raw/posix-accept.md:52).
- listen 소켓에 `O_NONBLOCK`이 있어도 받은 소켓에 붙는지는 구현이 정한다 (implementation-defined) (raw/posix-accept.md:54).
- 성공하면 받은 소켓의 음이 아닌 fd, 실패하면 -1과 errno (raw/posix-accept.md:76). 프로세스의 fd를 다 쓰면 `EMFILE` (raw/posix-accept.md:102-104).
- 연결이 오면 `select()`는 그 소켓을 읽기 준비로 알린다 (raw/posix-accept.md:152). `poll()`에서 같은 상태가 POLLIN으로 보이는 것은 이 위키의 실측과 설계에 따른 것이다 ([[sources/posix-poll]], **판단**).

## 과제 적용 (판단)

- 받은 소켓이 non-blocking을 물려받는지 구현마다 다르므로, 서버는 받자마자 `fcntl(clientFd, F_SETFL, O_NONBLOCK)`을 직접 부른다 (`webserv/src/core/Listener.cpp:87`). 이 호출이 없으면 어떤 OS에서는 클라이언트 소켓이 blocking으로 남을 수 있다.
- `accept`가 실패하면 원인을 errno로 가리지 않고 listener를 잠시 멈춘다 (`webserv/src/core/Listener.cpp:77-81`, [[analysis/design]] 11절). fd가 다 찬 동안(`EMFILE`) listen 소켓이 계속 읽기 가능으로 보여 루프가 쉬지 않고 도는 것을 막는다.

## 관련

- [[sources/posix-socket]], [[sources/posix-listen]], [[sources/posix-bind]], [[sources/posix-fcntl]], [[sources/posix-poll]], [[lessons/02b-tcp-connections]]
