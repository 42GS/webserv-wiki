---
title: OS 실측 — pipe의 poll revents
type: source
sources: [raw/os-observed-pipe-poll.md, raw/posix-poll.md]
updated: 2026-10-15
---

# OS 실측 — pipe의 poll revents

원본: `raw/os-observed-pipe-poll.md`. 테스트 프로그램(`pipepoll.c`)을 macOS와 Ubuntu 24.04 Docker 컨테이너에서 실행한 소스·명령·출력을 그대로 담았다 (2026-10-15). 프로그램은 `SIGPIPE`를 무시하도록 설정한다.

> [!note] 측정 환경의 한계
> 컨테이너의 커널은 OrbStack VM의 Linux 커널이다 (raw/os-observed-pipe-poll.md:24, raw/os-observed-pipe-poll.md:29). 평가 머신의 Ubuntu 커널에서 측정한 것이 아니다.

## 결과

| 경우 | macOS | Ubuntu | 근거 |
|---|---|---|---|
| [1] 읽는 쪽이 닫힌 pipe의 쓰는 쪽 (`events=POLLOUT`) | `POLLHUP` | **`POLLOUT` + `POLLERR`** | raw/os-observed-pipe-poll.md:171, raw/os-observed-pipe-poll.md:186 |
| 그 뒤 `write()` | -1 `EPIPE` | -1 `EPIPE` | raw/os-observed-pipe-poll.md:172, raw/os-observed-pipe-poll.md:187 |
| [2] 같은 조건, 쓰는 쪽 `O_NONBLOCK` | `POLLHUP` | `POLLOUT` + `POLLERR` | raw/os-observed-pipe-poll.md:173, raw/os-observed-pipe-poll.md:188 |
| [3] 쓰는 쪽이 닫히고 데이터 없음 (`events=POLLIN`) | `POLLIN` + `POLLHUP` | **`POLLHUP`만** | raw/os-observed-pipe-poll.md:174, raw/os-observed-pipe-poll.md:189 |
| 그 뒤 `read()` | 0 | 0 | raw/os-observed-pipe-poll.md:175, raw/os-observed-pipe-poll.md:190 |
| [4] 쓰는 쪽이 닫히고 3바이트 남음 | `POLLIN` + `POLLHUP`, `read()`=3 | `POLLIN` + `POLLHUP`, `read()`=3 | raw/os-observed-pipe-poll.md:176-177, raw/os-observed-pipe-poll.md:191-192 |
| 남은 데이터를 다 읽은 뒤 | `POLLIN` + `POLLHUP`, `read()`=0 | **`POLLHUP`만**, `read()`=0 | raw/os-observed-pipe-poll.md:178-179, raw/os-observed-pipe-poll.md:193-194 |
| [5] 쓰는 쪽이 닫힘, `events=0` | **아무것도 안 옴** (`poll`=0) | `POLLHUP` | raw/os-observed-pipe-poll.md:180, raw/os-observed-pipe-poll.md:195 |

> [!warning] 모순: macOS vs POSIX
> POSIX는 `POLLHUP`을 `events`에 넣지 않아도 조건이 맞으면 설정해야 한다고 한다 (raw/posix-poll.md:86). macOS는 `events=0`일 때 쓰는 쪽이 닫힌 pipe에 `POLLHUP`을 보고하지 않았다 (raw/os-observed-pipe-poll.md:180). Ubuntu는 보고했다 (raw/os-observed-pipe-poll.md:195). → [[analysis/subject-vs-evaluation]] 1.12

## 과제 적용 (판단)

- CGI 입력 pipe: Ubuntu는 `POLLERR`와 함께 `POLLOUT`도 켠다. `POLLERR`·`POLLHUP`을 먼저 검사해 입력 전달을 멈춘다. `write()`가 -1이어도 멈춘다 → [[concepts/cgi]].
- CGI 출력 pipe: Ubuntu에서는 데이터를 다 읽고 나면 `POLLIN` 없이 `POLLHUP`만 온다. `POLLHUP`만 와도 `read()`를 불러 0(EOF)을 확인해야 한다. `POLLIN`일 때만 읽으면 EOF를 보지 못하고 `POLLHUP`이 계속 와서 busy waiting이 된다. macOS에서는 드러나지 않는다.
- 다 쓴 fd는 `events=0`으로 남기지 말고 poll 목록에서 뺀다. Ubuntu에서는 `POLLHUP`이 계속 온다 → [[concepts/io-multiplexing]].
