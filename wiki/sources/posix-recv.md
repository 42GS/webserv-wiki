---
title: POSIX recv()
type: source
sources: [raw/posix-recv.md]
updated: 2026-10-15
---

# POSIX recv()

원본: `raw/posix-recv.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/recv.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-recv.md:1-4). 원본 HTML은 `raw/posix-recv.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-recv.md:6).

> [!note] 변환 방법
> [[sources/posix-poll]]과 같은 전처리·변환·검증을 거쳤다. 공백을 뺀 4,187자가 같았고, 단어 단위 차이 24건은 모두 태그 경계 분리였다.
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: SYNOPSIS가 한 줄로 합쳐짐, flags 안쪽 정의 목록이 평탄화됨.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| 스트림 소켓 동작 (62) | 메시지 경계 없음, 도착한 만큼 반환 | [[concepts/request-parsing]] |
| non-blocking 동작 (66) | 데이터가 없으면 `EAGAIN`/`EWOULDBLOCK`으로 실패 | [[concepts/io-multiplexing]] |
| RETURN VALUE (72) | 양수, 0(상대가 정상 종료), -1 | [[concepts/io-multiplexing]] |
| `ECONNRESET` (88-90) | 상대가 강제로 끊음 | [[concepts/io-multiplexing]] |
| APPLICATION USAGE (142-144) | flags 0이면 `read()`와 같음, `poll()`로 시점 판단 | [[concepts/io-multiplexing]] |

## 핵심

- 받을 데이터가 없고 상대가 정상 종료했으면 0을 돌려준다 (raw/posix-recv.md:72).
- SOCK_STREAM에서는 메시지 경계가 없고, 데이터는 도착하는 대로 돌려준다 (raw/posix-recv.md:62). 요청 하나가 여러 번에 나뉘어 오거나 요청 여러 개가 한 번에 올 수 있다는 근거다.
