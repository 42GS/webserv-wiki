---
title: POSIX fork() — 자신을 복제해 자식 프로세스를 만든다, 자식은 0·부모는 자식 pid를 받음
type: source
sources: [raw/posix-fork.md, raw/subject.md]
updated: 2026-10-29
---

# POSIX fork()

원본: `raw/posix-fork.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/fork.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-fork.md:1-3). 원본 HTML은 `raw/posix-fork.source.html`. 같은 페이지에 Issue 8에서 더해진 `_Fork()`가 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-fork.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[XSI]`·`[ML]`·`[PS]`·`[MSG]`·`[CPT]`·`[TCT]` 표시가 링크로, 선택 범위 그림이 `<img>` 태그로 남음, 빈 `<br>`가 `\` 한 줄이 됨 (raw/posix-fork.md:92), SEE ALSO의 `exec` 링크 앞에 빈 링크가 생김.

## 과제와 관련된 부분

과제는 `fork`를 CGI에만 쓰게 한다 (raw/subject.md:144). 서버는 CGI 스크립트를 실행할 때 한 번 `fork`하고 자식에서 곧바로 `execve`한다 (`webserv/src/cgi/CgiProcess.cpp:171-172`). 기초 설명은 [[lessons/02a-unix-system-calls]], 흐름은 [[lessons/13-cgi]] 13.3.

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (26) | 새 프로세스를 만든다. 자식은 몇 가지를 빼면 부모의 복사본 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (34) | 자식은 부모 fd의 사본을 갖고, 같은 열린 파일 설명을 가리킨다 | [[sources/posix-close]] |
| DESCRIPTION (66) | 자식은 스레드 하나로 만들어진다 | 아래 "과제 적용" |
| RETURN VALUE (82) | 자식에는 0, 부모에는 자식 pid, 실패하면 부모에 -1 | [[lessons/13-cgi]] |
| RATIONALE (130) | 다른 프로그램을 돌리려는 `fork`는 곧 `exec`가 뒤따른다 | [[sources/posix-exec]] |

## 핵심

- `fork()`는 새 프로세스(자식)를 만든다. 자식은 아래에 적은 것을 빼면 부르는 프로세스(부모)의 정확한 복사본이다 (raw/posix-fork.md:26).
- 자식은 부모 fd의 사본을 갖는다(`FD_CLOFORK`가 설정된 것 제외). 자식의 각 fd는 부모의 같은 번호 fd와 같은 열린 파일 설명을 가리킨다 (raw/posix-fork.md:34).
- 자식의 대기 중인 시그널 집합은 비어 있다 (raw/posix-fork.md:48).
- 프로세스는 스레드 하나로 만들어진다. 멀티스레드 프로세스가 `fork`하면 자식은 `exec`가 성공할 때까지 async-signal-safe 연산만 해야 한다 (raw/posix-fork.md:66).
- `fork` 뒤 부모와 자식은 서로 독립적으로 실행될 수 있어야 한다 (raw/posix-fork.md:76).
- 성공하면 자식에는 0을, 부모에는 자식의 프로세스 ID를 돌려주고, 두 프로세스 모두 `fork()`에서 이어서 실행한다. 실패하면 부모에 -1을 돌려주고 자식을 만들지 않으며 errno를 설정한다 (raw/posix-fork.md:82).
- 자원이 모자라거나 프로세스 수 제한을 넘으면 `EAGAIN` (raw/posix-fork.md:88-90).
- `fork`를 부르는 이유는 둘이다. 같은 프로그램에서 새 흐름을 만들거나, 다른 프로그램을 돌리는 새 프로세스를 만드는 것이다. 뒤의 경우 `fork` 다음에 곧 `exec` 함수가 온다 (raw/posix-fork.md:130).

## 과제 적용 (판단)

- 서버는 스레드가 하나라 자식에서 `exec` 전에 async-signal-safe 함수만 써야 한다는 제약(raw/posix-fork.md:66)은 직접 해당하지 않는다. 그래도 자식은 `execve` 전에 할 일을 줄여 `dup2`, fd 닫기, `chdir`, `SIGPIPE` 기본값 복원만 한다 ([[analysis/design]] 9절).
- 자식은 부모의 fd를 모두 물려받으므로(raw/posix-fork.md:34), 다른 클라이언트 소켓과 listen 소켓까지 갖게 된다. 그래서 `execve` 전에 3 이상의 fd를 닫는다 → [[sources/posix-close]], [[concepts/cgi]] 1절.
- 자식은 부모의 메모리 사본을 가지므로, `fork` 직전에 출력 버퍼를 비운다(`webserv/src/cgi/CgiProcess.cpp:169-170`). 비우지 않으면 자식의 `std::exit`이 부모가 아직 내보내지 않은 출력을 한 번 더 내보냈다 → [[analysis/design-decisions]] 12.
- 끝난 자식은 부모가 회수해야 좀비로 남지 않는다 → [[sources/posix-waitpid]], [[sources/posix-exit]].

## 관련

- [[sources/posix-exec]], [[sources/posix-pipe]], [[sources/posix-dup]], [[sources/posix-waitpid]], [[sources/posix-exit]], [[lessons/13-cgi]]
