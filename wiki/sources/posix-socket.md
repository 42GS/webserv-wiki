---
title: POSIX socket() — 통신 끝점을 만들고 fd를 돌려줌
type: source
sources: [raw/posix-socket.md, raw/subject.md]
updated: 2026-10-29
---

# POSIX socket()

원본: `raw/posix-socket.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/socket.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-socket.md:1-3). 원본 HTML은 `raw/posix-socket.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-socket.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[OB]` 표시가 링크로, `[Option Start]`·`[Option End]` 그림이 `<img>` 태그로 남음 (raw/posix-socket.md:107).

## 과제와 관련된 부분

서버가 listen 소켓을 만드는 첫 호출이다 (`webserv/src/core/Listener.cpp:40`, `socket(AF_INET, SOCK_STREAM, 0)`). 기초 설명은 [[lessons/02a-unix-system-calls]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (25) | 이름(주소)이 없는 소켓을 만들고 fd를 돌려준다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (45-49) | `SOCK_STREAM`: 순서가 지켜지고 믿을 수 있는 양방향 연결형 바이트 흐름 | [[lessons/02b-tcp-connections]] |
| DESCRIPTION (59-71) | `type`에 `SOCK_NONBLOCK` 등의 플래그를 OR할 수 있다 (Issue 8에서 추가) | 아래 "과제 적용" |
| RETURN VALUE (81) | 성공하면 음이 아닌 fd, 실패하면 -1과 errno | [[sources/posix-errno]] |
| ERRORS (91-93) | 프로세스의 fd를 다 쓰면 `EMFILE` | [[concepts/resilience]] |

## 핵심

- `socket()`은 통신 영역 안에 아직 주소가 붙지 않은(unbound) 소켓을 만들고, 소켓을 다루는 다른 함수에 쓸 fd를 돌려준다 (raw/posix-socket.md:25).
- `domain`은 주소 체계, `type`은 통신의 의미를 정하는 소켓 종류, `protocol`이 0이면 그 종류의 기본 프로토콜을 쓴다 (raw/posix-socket.md:41, raw/posix-socket.md:45, raw/posix-socket.md:39).
- `SOCK_STREAM`은 순서가 지켜지고(sequenced), 믿을 수 있고(reliable), 양방향인 연결형(connection-mode) 바이트 흐름이다 (raw/posix-socket.md:47-49).
- `type`에 `SOCK_CLOEXEC`·`SOCK_CLOFORK`·`SOCK_NONBLOCK` 플래그를 OR할 수 있다 (raw/posix-socket.md:59-71). 이 세 플래그는 Issue 8(POSIX.1-2024)에서 추가됐다 (raw/posix-socket.md:169).
- 성공하면 음이 아닌 정수인 소켓 fd를, 실패하면 -1을 돌려주고 errno를 설정한다 (raw/posix-socket.md:81).
- 프로세스가 쓸 수 있는 fd를 모두 열었으면 `EMFILE`로 실패한다 (raw/posix-socket.md:91-93).

## 과제 적용 (판단)

- 서버는 `SOCK_NONBLOCK` 플래그 대신 `fcntl(fd, F_SETFL, O_NONBLOCK)`으로 non-blocking을 켠다 (`webserv/src/core/Listener.cpp:51`). 과제가 허용한 방법이 `fcntl`의 `F_SETFL`·`O_NONBLOCK`이고 (raw/subject.md:155-157), 이 플래그는 POSIX.1-2024에서 들어온 것이라 오래된 시스템과의 호환도 덜 확실하다.

## 관련

- [[sources/posix-listen]], [[sources/posix-accept]], [[sources/posix-bind]], [[sources/posix-fcntl]], [[sources/posix-close]], [[lessons/02a-unix-system-calls]], [[lessons/02b-tcp-connections]]
