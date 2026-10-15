---
title: POSIX <signal.h>
type: source
sources: [raw/posix-signal-h.md, raw/subject.md]
updated: 2026-10-15
---

# POSIX `<signal.h>`

원본: `raw/posix-signal-h.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/signal.h.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-signal-h.md:1-4). 원본 HTML은 `raw/posix-signal-h.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-signal-h.md:6).

> [!note] 변환 방법
> [[sources/posix-poll]]과 같은 전처리·변환·검증을 거쳤다. 공백을 뺀 15,720자가 같았다. 단어 단위 차이 90건 중 87건은 태그 경계 분리였고, 3건은 SEE ALSO 목록에서 diff 정렬이 어긋난 것으로 해당 줄을 직접 비교해 확인했다.
> 시그널 표는 행 단위로 풀어져 있고 헤더 칸이 `****`로 변환됐다. 표에서 한 시그널은 이름, 기본 동작 기호, 설명이 연속된 세 줄이다.
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: 표 3개가 칸마다 한 줄로 풀림(위 설명과 같음), 코드 블록 안 `[CX]`/`[XSI]` 표시가 글자로 남음.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| `SIG_DFL`·`SIG_IGN` (32-44) | 기본 처리 요청, 무시 요청 | [[concepts/resilience]] |
| 시그널 표 (114-292) | 시그널별 기본 동작 | [[concepts/resilience]], [[concepts/cgi]] |
| 기본 동작 기호 (294-310) | T·A·I·S의 뜻 | [[concepts/resilience]] |

다루지 않는 부분: 실시간 시그널, `sigaction`·`siginfo_t` 구조체, 스레드 관련 정의. 과제의 허용 함수는 `signal`과 `kill`뿐이다 (raw/subject.md:113).

## 과제 관련 시그널

| 시그널 | 기본 동작 | 설명 | 근거 |
|---|---|---|---|
| `SIGPIPE` | T (비정상 종료) | 읽는 쪽이 없는 pipe에 씀 | raw/posix-signal-h.md:192-196 |
| `SIGCHLD` | I (무시) | 자식 프로세스 종료·정지 | raw/posix-signal-h.md:146-154 |
| `SIGINT` | T | 터미널 인터럽트 | raw/posix-signal-h.md:180-184 |
| `SIGTERM` | T | 종료 시그널 | raw/posix-signal-h.md:216-220 |
| `SIGKILL` | T | 잡거나 무시할 수 없음 | raw/posix-signal-h.md:186-190 |

기호의 뜻: T는 프로세스 비정상 종료, A는 추가 동작이 있는 비정상 종료, I는 무시, S는 정지 (raw/posix-signal-h.md:296-310).
