---
title: POSIX _Exit(), _exit() — 프로세스 종료의 결과
type: source
sources: [raw/posix-exit.md, raw/posix-signal-h.md]
updated: 2026-10-15
---

# POSIX _Exit(), _exit()

원본: `raw/posix-exit.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/_Exit.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-exit.md:1-4). 원본 HTML은 `raw/posix-exit.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-exit.md:6).

> [!note] 변환 검증
> `tools/posix_wrap.py` → `tools/nginx2md.py`로 변환하고 `tools/verify_md.py`로 검증했다. 공백을 뺀 13,127자와 단어 2,435개가 모두 같았다 (PASS).
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: "Consequences of Process Termination" 목록(raw/posix-exit.md:48-96)의 글머리표와 중첩이 없어, "Otherwise:"(58행) 아래 항목(60-68행)이 위치로만 구분됨.

## 과제와 관련된 부분

"Consequences of Process Termination"(raw/posix-exit.md:40-96)은 **이유와 상관없이** 프로세스가 끝날 때 일어나는 일이다 (raw/posix-exit.md:42). CGI 스크립트가 정상 종료하든 시그널로 죽든 똑같이 적용된다.

| 결과 | 과제와의 연결 | 근거 |
|---|---|---|
| 열린 fd가 모두 닫힘 | 스크립트가 끝나면 출력 pipe가 닫혀 서버에 EOF가 온다 | raw/posix-exit.md:48 |
| 부모가 `SIGCHLD`를 `SIG_IGN`으로 뒀으면 상태 정보를 버리고 바로 사라짐 [XSI] | 좀비는 없지만 종료 상태를 못 받는다 | raw/posix-exit.md:50-54 |
| 그렇지 않으면 **좀비가 됨**. 부모가 `wait`/`waitpid`로 상태를 가져가면 수명이 끝남 | CGI 자식을 회수하지 않으면 좀비가 남는다 | raw/posix-exit.md:58-64 |
| 그렇지 않으면 부모에게 `SIGCHLD`를 보냄. 첫 경우 중 `SA_NOCLDWAIT`가 설정됐을 때 보낼지는 구현 정의 [XSI] | `SIGCHLD` 기본 동작은 무시(I) (raw/posix-signal-h.md:146-154, 304-306) | raw/posix-exit.md:54, 58, 68 |
| 프로세스가 끝나도 그 자식은 끝나지 않고, 시스템 프로세스에 입양됨 | 서버가 꺼져도 실행 중인 CGI는 계속 돈다. 스크립트를 죽여도 손자 프로세스는 남는다 | raw/posix-exit.md:70-72 |
| `wait`/`waitpid`로 받을 수 있는 종료 상태는 하위 8비트 | | raw/posix-exit.md:32 |

다루지 않는 부분: 공유 메모리, 세마포어, 터미널 세션, 메모리 잠금, 메시지 큐, 비동기 I/O (raw/posix-exit.md:74-96).

## 그 밖에

- `_Exit`/`_exit`는 `atexit` 함수와 시그널 핸들러를 부르지 않고, 열린 stream을 flush하지 않는다 (raw/posix-exit.md:36).
- 보통은 `_Exit`/`_exit`보다 `exit()`을 쓰라고 권한다 (raw/posix-exit.md:122).
- 이 함수들은 subject 허용 함수 목록에 없다 → [[analysis/subject-vs-evaluation]] 1.4절.
