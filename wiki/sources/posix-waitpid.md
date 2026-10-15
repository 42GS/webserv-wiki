---
title: POSIX wait(), waitpid()
type: source
sources: [raw/posix-waitpid.md, raw/posix-exit.md]
updated: 2026-10-15
---

# POSIX wait(), waitpid()

원본: `raw/posix-waitpid.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/waitpid.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-waitpid.md:1-4). 원본 HTML은 `raw/posix-waitpid.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-waitpid.md:6). `wait()`와 `waitpid()`를 한 페이지에서 정의한다 (raw/posix-waitpid.md:18).

> [!note] 변환 방법
> [[sources/posix-poll]]과 같은 전처리·변환·검증을 거쳤다. 공백을 뺀 20,136자가 같았고, 단어 단위 차이 178건은 모두 태그 경계 분리였다.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| pid 인자 (40-48) | 회수할 자식 지정 | [[concepts/cgi]] |
| `WNOHANG` (56-58) | 끝난 자식이 없으면 기다리지 않음 | [[concepts/cgi]] |
| 종료 상태와 매크로 (64-92) | `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, `WTERMSIG` | [[concepts/cgi]] |
| RETURN VALUE (132) | 자식 PID, 0, -1 | [[concepts/cgi]] |
| ERRORS (148-160) | `ECHILD`, `EINTR`, `EINVAL` | [[concepts/cgi]] |
| APPLICATION USAGE (321-323) | `wait()`·pid -1 비권장, `SIGCHLD`를 `SIG_IGN`으로 두면 상태를 못 받음 | [[concepts/cgi]], [[concepts/resilience]] |
| RATIONALE (329) | 직접 만든 자식만 대상 | [[concepts/cgi]] |

## 다른 문서에서 확인한 것

- 회수하지 않은 자식이 좀비로 남는다는 정의: 이 페이지는 "2.12 Status Information"과 "Consequences of Process Termination"을 참조만 한다 (raw/posix-waitpid.md:30, raw/posix-waitpid.md:323). `_Exit()` 페이지에서 확인했다 (raw/posix-exit.md:58-64) → [[sources/posix-exit]].
