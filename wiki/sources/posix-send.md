---
title: POSIX send()
type: source
sources: [raw/posix-send.md]
updated: 2026-10-15
---

# POSIX send()

원본: `raw/posix-send.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/send.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-send.md:1-4). 원본 HTML은 `raw/posix-send.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-send.md:6).

> [!note] 변환 방법
> [[sources/posix-poll]]과 같은 전처리·변환·검증을 거쳤다. 공백을 뺀 4,275자가 같았고, 단어 단위 차이 28건은 모두 태그 경계 분리였다.
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: SYNOPSIS가 한 줄로 합쳐짐, flags 안쪽 정의 목록이 평탄화됨.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| `MSG_NOSIGNAL` (58-60) | `SIGPIPE`를 보내지 않게 하는 플래그 | [[concepts/resilience]] |
| non-blocking 동작 (66) | 공간이 없으면 실패, `poll()`로 시점 판단 | [[concepts/io-multiplexing]] |
| RETURN VALUE (74) | 보낸 바이트 수 또는 -1 | [[concepts/io-multiplexing]] |
| `ECONNRESET`, `EPIPE` (90-92, 118-120) | 상대가 끊은 연결 | [[concepts/resilience]] |
| APPLICATION USAGE (156) | flags 0이면 `write()`와 같음 | [[concepts/io-multiplexing]] |

## 핵심

- 연결이 끊긴 SOCK_STREAM 소켓에 보내면 `EPIPE`로 실패하고, `MSG_NOSIGNAL`이 없으면 `SIGPIPE`도 발생한다 (raw/posix-send.md:118-120).
- `MSG_NOSIGNAL`을 주면 `SIGPIPE`는 보내지 않지만 `EPIPE`는 그대로 돌려준다 (raw/posix-send.md:58-60).
