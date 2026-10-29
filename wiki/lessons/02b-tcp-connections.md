---
title: "레슨 2B: TCP 연결이 맺어지고 끊어지는 과정"
type: lesson
sources: [raw/rfc9293.txt, raw/posix-socket.md, raw/posix-listen.md, raw/posix-accept.md, raw/posix-close.md, raw/rfc9112.txt]
updated: 2026-10-29
---

# 레슨 2B: TCP 연결이 맺어지고 끊어지는 과정

이전: [[lessons/02a-unix-system-calls]] · 다음: [[lessons/03-http-basics]]

코드 기준: webserv 커밋 `4db9510`. [[lessons/02-networking-basics]]에서 IP·포트·소켓과 "TCP는 바이트를 순서대로 보내지만 경계는 지키지 않는다"를 봤다. 이 장은 그 연결이 어떻게 생기고 어떻게 없어지는지를 본다.

## 2B.1 TCP가 약속하는 것

TCP는 응용 프로그램에 믿을 수 있고 순서가 지켜지는 바이트 흐름을 준다 (raw/rfc9293.txt:243-244). 포트 번호로 서비스를 구분한다 (raw/rfc9293.txt:266-267). 용어도 정해 두자.

| 용어 | 뜻 | 원문 |
|---|---|---|
| 소켓(주소) | IP 주소와 TCP 포트를 이은 것. 예: `127.0.0.1:8080` | raw/rfc9293.txt:4162-4164 |
| 연결 | 소켓 한 쌍(내 쪽, 상대 쪽)으로 구분되는 통신 경로 | raw/rfc9293.txt:3960-3961 |
| 포트 | 한 컴퓨터 안에서 연결을 나누는 번호 | raw/rfc9293.txt:4052-4054 |

같은 서버 포트 8080에 손님 100명이 붙어도 연결이 섞이지 않는 이유가 여기 있다. 손님마다 상대 쪽 소켓(손님 IP와 포트)이 달라 소켓 쌍이 서로 다르다 **(판단)**.

## 2B.2 연결 맺기: 3-way handshake

> [!example] 쉬운 예
> 무전기로 대화를 시작할 때: A "들리나? 내 번호는 100번부터 셀게." → B "들린다, 100번 받았어. 내 번호는 300번부터." → A "300번 받았어." 세 번 주고받아야 둘 다 상대가 들었다는 걸 확인한다.

양쪽이 서로의 시작 번호를 보내고 확인받아야 하므로 SYN → SYN·ACK → ACK 세 메시지가 오간다. 이것이 3-way handshake다 (raw/rfc9293.txt:1063-1074).

```text
   클라이언트                                   서버(LISTEN)
1. SYN-SENT     --> SYN(seq=100)            --> SYN-RECEIVED
2. ESTABLISHED  <-- SYN,ACK(seq=300,ack=101) <-- SYN-RECEIVED
3. ESTABLISHED  --> ACK(ack=301)            --> ESTABLISHED
```
(raw/rfc9293.txt:1256-1268의 그림을 줄인 것)

이 과정은 OS의 TCP가 한다. 서버 프로그램이 하는 일은 소켓 함수 네 개뿐이다.

| 서버 코드 | 하는 일 | 원문 |
|---|---|---|
| `socket()` (`src/core/Listener.cpp:40`) | 주소 없는 소켓을 만들고 fd를 돌려준다 | raw/posix-socket.md:25 |
| `bind()` (`:43`) | 그 소켓에 내 주소(`127.0.0.1:8080`)를 붙인다 | [[sources/posix-bind]] |
| `listen()` (`:48`) | 연결을 받는 소켓으로 표시한다 | raw/posix-listen.md:25 |
| `accept()` (`:74`) | 대기열에서 다 맺어진 연결 하나를 꺼내 새 fd로 준다 | raw/posix-accept.md:28 |

`accept`가 돌려준 fd는 그 손님 전용이다. 이 fd로는 다른 연결을 받을 수 없고, 원래 listen 소켓은 계속 손님을 받는다 (raw/posix-accept.md:52).

## 2B.3 listen 대기열(backlog)

> [!example] 쉬운 예
> 식당 앞 대기 의자다. 손님(연결)이 도착하면 의자에 앉아 기다리고, 직원이 `accept`로 한 명씩 안으로 모신다. 의자가 다 차면 새 손님은 바로 앉지 못한다.

- `listen`의 `backlog`는 대기열에 쌓일 미처리 연결 수를 제한하는 힌트다. 구현은 값을 조용히 줄일 수 있고, `SOMAXCONN`까지는 지원해야 한다 (raw/posix-listen.md:27).
- 대기열에는 아직 덜 맺어진 연결도 들어갈 수 있다 (raw/posix-listen.md:29).
- 서버는 `SOMAXCONN`을 넘긴다 (`src/core/Listener.cpp:48`).

> [!info] 실측
> 기존 구현(backlog 128)과 비교할 때, 연결 1000개를 한꺼번에 열 때 기존 구현은 5.15~6.2초가 걸렸고 그중 연결 5번이 약 1.02초씩 멈췄다. 이 서버(`SOMAXCONN`, 컨테이너에서 4096)는 0.11~0.19초였다 ([[log]] 2026-10-29 "운영 로그 구현, 기존 구현과 poll·성능 실측 비교"). 대기열이 차서 SYN을 다시 보내느라 늦어진 것으로 본다 **(판단)**.

## 2B.4 연결 끊기: FIN, half-close, RST

> [!example] 쉬운 예
> 전화를 끊을 때 "나는 할 말 다 했어"(FIN)라고 말해도, 상대는 아직 할 말을 계속할 수 있다. 상대도 "나도 끝"이라고 하면 통화가 끝난다. 그런데 상대가 말하는 중에 내가 그냥 수화기를 내려놓으면, 통화가 툭 끊기며 상대가 마지막 말을 못 할 수 있다(RST).

- **CLOSE는 "더 보낼 것이 없다"는 뜻이다.** 닫은 쪽도 상대가 닫을 때까지 계속 받을 수 있다 (raw/rfc9293.txt:1530-1546, raw/rfc9293.txt:2635-2637).
- **두 방향은 따로 닫힌다.** 한쪽만 닫힌 half-closed 상태가 있다 (raw/rfc9293.txt:1638-1643).
- **읽지 않은 데이터가 남은 채로 닫으면 RST.** CLOSE 뒤 더 읽지 못하는 방식으로 닫는 호스트가, 받은 데이터가 남은 채로 닫거나 닫은 뒤 데이터가 오면 RST를 보내야 한다(SHOULD) (raw/rfc9293.txt:1645-1651).
- **RST의 피해.** RST가 클라이언트의 아직 읽지 않은 응답까지 지울 수 있다 (raw/rfc9112.txt:1539-1546).
- **TIME-WAIT.** 먼저 닫은 쪽은 TIME-WAIT 상태로 2×MSL 동안 머문다 (MUST, raw/rfc9293.txt:1653-1654).
- **소켓 파괴.** 소켓은 그 소켓의 fd가 모두 닫혀야 파괴된다 (raw/posix-close.md:42).

`src/http/Connection.cpp:228-236` — 응답을 다 보낸 뒤:

```cpp
void Connection::finishResponse() {
  if (!keepAlive_) {
    changeState(requestConsumed_ ? CLOSED : DRAIN);
    return;
  }
  parser_.reset();
  changeState(READ_HEAD);
  parseInput();
}
```

keep-alive가 아니면 요청을 다 읽었는지(`requestConsumed_`)에 따라 바로 닫거나(CLOSED) 남은 입력을 먼저 읽어 버린다(DRAIN). keep-alive면 파서를 비우고 같은 연결로 다음 요청을 받는다.

> [!tip] 왜 이렇게?
> - **DRAIN:** 413처럼 본문을 다 읽지 않고 응답한 경우, 바로 닫으면 남은 데이터 때문에 RST가 나가 손님이 응답을 못 받을 수 있다 (raw/rfc9293.txt:1645-1651, raw/rfc9112.txt:1539-1546). 그래서 남은 입력을 잠깐(1초 무입력, 최대 5초, `include/core/Limits.hpp:95-97`) 읽어 버린 뒤 닫는다. 실측: 바로 닫으면 macOS에서 손님이 reset을 받았고, 읽고 버린 뒤 닫으면 12번 모두 413을 받았다 → [[sources/close-after-413-observed]], [[lessons/08-connection]] 8.3.
> - **`SO_REUSEADDR` (`src/core/Listener.cpp:42`):** 서버가 먼저 닫은 연결은 TIME-WAIT로 남는다 (raw/rfc9293.txt:1653-1654). 그래서 재시작 직후 같은 포트에 `bind`할 때 이 옵션이 필요했다(실측) → [[sources/os-observed-bind]].

## 2B.5 TCP keep-alive와 HTTP keep-alive는 다르다

| | TCP keep-alive | HTTP keep-alive |
|---|---|---|
| 무엇 | 오래 조용한 연결이 살아 있는지 보는 탐침 패킷 (raw/rfc9293.txt:2035-2040) | 한 연결로 요청을 여러 개 주고받는 것 ([[lessons/03-http-basics]] 3.4) |
| 기본값 | 꺼짐(MUST), 켜도 간격 2시간 이상 (raw/rfc9293.txt:2041-2044, raw/rfc9293.txt:2046-2050) | HTTP/1.1은 기본으로 유지 |
| 이 서버 | 쓰지 않는다 | 쓴다. 다음 요청을 15초 기다린다 (`include/core/Limits.hpp:87`) |

## 2B.6 루프백과 여러 주소

`127.0.0.1`은 "내 컴퓨터 자신"이다 ([[lessons/02-networking-basics]] 2.3). `conf/ports.conf`는 `127.0.0.1`과 `127.0.0.2`에 서로 다른 사이트를 연다. Ubuntu 22.04에서는 `127.0.0.2`에 바로 `bind`됐고, macOS에서는 `Can't assign requested address`로 실패했다(2026-10-18 실행, [[analysis/test-plan]] 9절). 평가는 Ubuntu에서 하므로 이 설정으로 "다른 interface의 다른 사이트"를 보여 줄 수 있다.

> [!info] 평가 때
> - "Address already in use"가 나면: 같은 포트를 다른 프로세스가 쓰고 있다. 두 번째 서버는 이유를 출력하고 종료 코드 1로 끝나고, 첫 서버는 계속 응답한다 ([[lessons/15-defense-qa]] Q9).
> - "Connection reset by peer"를 본다면: 서버가 읽지 않은 데이터를 남긴 채 닫은 경우다. 이 서버는 DRAIN으로 이를 피한다.

> [!question]- 확인 문제 1: `accept`가 돌려준 fd로 `accept`를 또 부르면?
> 안 된다. 받은 소켓은 다른 연결을 받을 수 없다. 연결을 더 받는 것은 원래 listen 소켓이다 (raw/posix-accept.md:52).

> [!question]- 확인 문제 2: 서버가 응답을 보내고 바로 `close`했는데 손님이 응답을 못 받았다. 왜일까?
> 손님이 보낸 데이터(본문 나머지나 다음 요청)를 서버가 다 읽지 않은 채 닫으면 RST가 나갈 수 있고(raw/rfc9293.txt:1645-1651), 그 RST가 손님 쪽의 아직 읽지 않은 응답을 지울 수 있다 (raw/rfc9112.txt:1539-1546). 남은 입력을 읽어 버린 뒤 닫으면 피할 수 있다.

> [!question]- 확인 문제 3: 서버의 keep-alive 15초는 TCP keep-alive 설정일까?
> 아니다. HTTP 연결에서 다음 요청의 첫 바이트를 기다리는 서버의 시간 제한이다 (`include/core/Limits.hpp:87`). TCP keep-alive는 OS가 보내는 탐침이고 기본으로 꺼져 있다 (raw/rfc9293.txt:2041-2044).
