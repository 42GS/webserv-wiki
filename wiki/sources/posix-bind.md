---
title: POSIX bind()
type: source
sources: [raw/posix-bind.md]
updated: 2026-10-15
---

# POSIX bind()

원본: `raw/posix-bind.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/bind.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-bind.md:1-4). 원본 HTML은 `raw/posix-bind.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-bind.md:6).

> [!note] 변환 방법
> [[sources/posix-poll]]과 같은 전처리·변환·검증을 거쳤다. 공백을 뺀 6,463자가 같았고, 단어 단위 차이 24건은 모두 태그 경계 분리였다.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (30, 50-52) | 주소 할당, non-blocking에서의 비동기 할당 | [[concepts/configuration-file]] |
| RETURN VALUE (58) | 성공 0, 실패 -1 | [[concepts/resilience]] |
| ERRORS (64-104, 148-160) | `EADDRINUSE`, `EADDRNOTAVAIL`, `EINPROGRESS`, `EACCES` | [[concepts/configuration-file]] |
| APPLICATION USAGE (202) | `getsockname()`으로 할당된 주소 확인 | [[concepts/cgi]] |

다루지 않는 부분: AF_UNIX(경로 소켓) 관련 요구와 에러 (raw/posix-bind.md:48, raw/posix-bind.md:106-146). 과제는 TCP 소켓만 쓴다.

## 핵심

- 이미 쓰이는 주소면 `EADDRINUSE`로 실패한다 (raw/posix-bind.md:66-68).
- 이 기계에서 쓸 수 없는 주소면 `EADDRNOTAVAIL` (raw/posix-bind.md:70-72).
- `O_NONBLOCK` 소켓에서 바로 할당할 수 없으면 `EINPROGRESS`로 실패하고 할당은 나중에 완료된다 (raw/posix-bind.md:50, raw/posix-bind.md:86-88).

## 이 문서로 확인하지 못한 것

- TCP에서 "주소가 쓰이는 중"의 정확한 범위. 서버 재시작 직후 실패 여부와 `SO_REUSEADDR`의 효과, 와일드카드 주소(`0.0.0.0`)와 특정 주소의 충돌 여부 → macOS·Ubuntu 실측으로 확인 [[sources/os-observed-bind]].
- 어떤 주소가 권한이 필요한 "보호된" 주소인지 (raw/posix-bind.md:150-152).
