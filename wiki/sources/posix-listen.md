---
title: POSIX listen() — 연결을 받을 소켓으로 표시하고 대기열 길이를 정함
type: source
sources: [raw/posix-listen.md]
updated: 2026-10-29
---

# POSIX listen()

원본: `raw/posix-listen.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/listen.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-listen.md:1-3). 원본 HTML은 `raw/posix-listen.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-listen.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음, 구조 차이 없음.

## 과제와 관련된 부분

서버는 listen 소켓을 `listen(fd, SOMAXCONN)`으로 연다 (`webserv/src/core/Listener.cpp:48`). 기초 설명은 [[lessons/02b-tcp-connections]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (25) | 연결형 소켓을 연결을 받는 소켓으로 표시한다 | [[lessons/02b-tcp-connections]] |
| DESCRIPTION (27) | `backlog`는 대기열의 미처리 연결 수를 제한하는 힌트. `SOMAXCONN`까지는 지원해야 함 | 아래 "과제 적용" |
| DESCRIPTION (29-31) | 덜 맺어진 연결도 대기열에 넣을 수 있고, 대기열 길이에 상한이 있을 수 있음 | [[lessons/02b-tcp-connections]] |
| RETURN VALUE (41) | 성공 0, 실패 -1과 errno | [[sources/posix-errno]] |

## 핵심

- `listen()`은 연결형 소켓을 연결을 받아들이는 소켓으로 표시한다 (raw/posix-listen.md:25).
- `backlog`는 listen 대기열에 쌓일 미처리 연결 수를 제한하는 데 쓰는 힌트다. 구현은 값을 조용히 줄일 수 있고, `SOMAXCONN`까지의 값은 지원해야 한다 (raw/posix-listen.md:27).
- 대기열에는 아직 덜 맺어진 연결이 들어갈 수 있고, 덜 맺어진 것과 다 맺어진 것의 상한이 다를 수 있다 (raw/posix-listen.md:29).
- 대기열 길이에는 전체 또는 소켓별 상한이 있을 수 있고, `backlog`가 그보다 크면 상한으로 정해진다 (raw/posix-listen.md:31).
- 성공하면 0, 실패하면 -1을 돌려주고 errno를 설정한다 (raw/posix-listen.md:41).

## 과제 적용 (판단)

- 대기열이 차면 새 연결이 바로 받아들여지지 않는다. 2026-10-29 기존 구현(backlog 128) 비교 실측에서, 연결 1000개를 한꺼번에 열 때 몇 개가 약 1초씩 멈췄다 ([[log]] 2026-10-29 "운영 로그 구현, 기존 구현과 poll·성능 실측 비교"). 이 서버는 `SOMAXCONN`을 넘겨 그런 멈춤이 보이지 않았다.
- `webserv/src/core/Listener.cpp:44`의 주석은 `SOMAXCONN`을 "시스템이 허용하는 가장 긴 대기열"이라고 하지만, 원문은 그 값까지 지원해야 한다고만 하고 최대라고 하지 않는다 (raw/posix-listen.md:27, raw/posix-listen.md:31). 주석이 원문보다 강했다. 2026-10-29에 "모든 시스템이 지원해야 하는 값이고 시스템이 줄일 수 있다"로 고쳤다 (webserv `4db9510`).

## 관련

- [[sources/posix-socket]], [[sources/posix-accept]], [[sources/posix-bind]], [[lessons/02b-tcp-connections]]
