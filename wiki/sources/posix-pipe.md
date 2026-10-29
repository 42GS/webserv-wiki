---
title: POSIX pipe() — 읽는 끝 fildes[0]과 쓰는 끝 fildes[1], 먼저 쓴 것이 먼저 읽힘
type: source
sources: [raw/posix-pipe.md, raw/subject.md]
updated: 2026-10-29
---

# POSIX pipe()

원본: `raw/posix-pipe.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/pipe.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-pipe.md:1-3). 원본 HTML은 `raw/posix-pipe.source.html`. 같은 페이지에 Issue 8에서 더해진 `pipe2()`가 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-pipe.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: EXAMPLES 코드가 들여쓴 코드 블록이 되고 `<br>`가 빈 줄이 됨, CHANGE HISTORY의 `<br>` 하나가 `\`로 남음.

## 과제와 관련된 부분

CGI 하나마다 pipe 두 개를 만든다. 하나는 요청 본문을 스크립트의 표준 입력으로, 다른 하나는 스크립트의 표준 출력을 서버로 보낸다 (`webserv/src/cgi/CgiProcess.cpp:56-61`, `:148-175`). 기초 설명은 [[lessons/02a-unix-system-calls]], 흐름은 [[lessons/13-cgi]] 13.3·13.4.

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (26) | `fildes[0]`은 읽는 끝, `fildes[1]`은 쓰는 끝. 처음에는 `O_NONBLOCK`이 꺼져 있다 | [[lessons/13-cgi]] |
| DESCRIPTION (28) | `fildes[1]`에 쓴 것을 `fildes[0]`에서 먼저 쓴 순서대로 읽는다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (30) | 쓰는 끝 fd를 가진 프로세스가 있으면 "쓰기로 열려 있다" | [[sources/posix-read]] |
| RETURN VALUE (54) | 성공 0, 실패 -1과 errno, 실패하면 fd를 만들지 않음 | [[sources/posix-errno]] |
| EXAMPLES (86) | `fork` 뒤 양쪽이 쓰지 않는 끝을 닫는 것이 좋은 습관 | 아래 "과제 적용" |
| RATIONALE (137) | 부모가 읽고 자식이 쓰는 경우, 쓰는 끝이 다른 자식에게 새면 부모가 EOF를 받지 못할 수 있다 | 아래 "과제 적용" |

## 핵심

- `pipe()`는 pipe를 만들고 fd 두 개를 넣는다. `fildes[0]`은 읽는 끝, `fildes[1]`은 쓰는 끝을 가리킨다. 두 fd 모두 `FD_CLOEXEC`가 꺼져 있고, `O_NONBLOCK`도 꺼져 있다(`fcntl`로 켤 수 있다) (raw/posix-pipe.md:26).
- `fildes[1]`에 쓴 데이터를 `fildes[0]`에서 먼저 쓴 것부터(first-in-first-out) 읽는다 (raw/posix-pipe.md:28).
- 프로세스가 읽는 끝(쓰는 끝)을 가리키는 fd를 열고 있으면, 그 프로세스는 pipe를 읽기(쓰기)로 열고 있다 (raw/posix-pipe.md:30). 빈 pipe에서 `read`가 0(EOF)을 돌려주는 조건인 "쓰기로 연 프로세스가 없음"이 이 정의를 따른다 → [[sources/posix-read]].
- 성공하면 0, 실패하면 -1과 errno이고, 실패하면 fd를 하나도 만들지 않는다 (raw/posix-pipe.md:54). fd를 다 쓰면 `EMFILE` (raw/posix-pipe.md:60-62).
- 원문 예제는 `fork` 뒤 두 프로세스가 각자 쓰지 않는 끝을 닫고 나서 데이터를 주고받는 것을 좋은 습관으로 든다 (raw/posix-pipe.md:86).
- 부모가 읽고 자식이 쓰는 경우, 쓰는 끝이 다른 자식에게 새어 나가면 자식이 쓰는 끝을 닫아도 부모가 EOF를 받는다는 보장이 없다 (raw/posix-pipe.md:137).

## 과제 적용 (판단)

- 부모(서버)는 `fork` 뒤 자식 쪽 끝(입력 pipe의 읽는 끝, 출력 pipe의 쓰는 끝)을 바로 닫는다 (`webserv/src/cgi/CgiProcess.cpp:173-174`). 서버가 출력 pipe의 쓰는 끝을 쥐고 있으면, 스크립트가 끝나도 "쓰기로 연 프로세스"가 남아 `read`가 0을 돌려주지 않는다 (raw/posix-pipe.md:30).
- 다른 CGI 자식에게 쓰는 끝이 새는 문제(raw/posix-pipe.md:137)는, 자식이 `execve` 전에 3 이상의 fd를 모두 닫아 막는다 → [[sources/posix-close]].
- 부모 쪽 끝은 `fcntl(F_SETFL, O_NONBLOCK)`으로 non-blocking으로 바꾼 뒤 `poll()`에 등록한다 (`webserv/src/cgi/CgiProcess.cpp:158-159`). pipe는 기다릴 수 있는 I/O라 과제가 `poll()`을 요구한다 (raw/subject.md:136).

## 관련

- [[sources/posix-fork]], [[sources/posix-dup]], [[sources/posix-read]], [[sources/posix-write]], [[sources/posix-close]], [[lessons/13-cgi]]
