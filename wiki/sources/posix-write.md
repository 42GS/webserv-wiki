---
title: POSIX write() — fd에 최대 nbyte를 쓰고 쓴 수를 돌려줌, 읽는 쪽 없는 pipe는 EPIPE
type: source
sources: [raw/posix-write.md, raw/subject.md]
updated: 2026-10-29
---

# POSIX write()

원본: `raw/posix-write.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/write.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-write.md:1-3). 원본 HTML은 `raw/posix-write.source.html`. 같은 페이지에 `pwrite()`가 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-write.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[XSI]`·`[SIO]`·`[SHM]`·`[TYM]` 표시가 링크로, 선택 범위 그림이 `<img>` 태그로 남음, EXAMPLES·RATIONALE 코드가 들여쓴 코드 블록이 되고 `<br>`가 빈 줄이 됨, RATIONALE의 표 두 개가 HTML 표로 남음 (raw/posix-write.md:272-328).

## 과제와 관련된 부분

서버는 CGI 입력 pipe (`webserv/src/cgi/CgiPipes.cpp:31`), 업로드 파일 (`webserv/src/fs/FileWriter.cpp:27`), 시계 파일 (`webserv/src/core/Clock.cpp:18`), 로그 파일 (`webserv/src/core/Logger.cpp:89`)에 `write`를 쓴다. 소켓은 `send`로 쓴다 → [[sources/posix-send]]. 기초 설명은 [[lessons/02a-unix-system-calls]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (27, 31) | 최대 `nbyte`를 쓰려 하고, 일반 파일은 파일 위치에서 쓴다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (35) | `O_APPEND`면 쓰기마다 끝으로 옮긴 뒤 쓴다 | [[lessons/14-resilience]] 14.4 |
| DESCRIPTION (55-73) | pipe: 위치 없이 끝에 덧붙임, non-blocking이면 막히지 않고 일부만 쓰거나 `EAGAIN` | [[lessons/13-cgi]] |
| DESCRIPTION (85) | 소켓이면 플래그 없는 `send()`와 같다 | [[sources/posix-send]] |
| RETURN VALUE (99) | 쓴 바이트 수(`nbyte` 이하), 실패하면 -1과 errno | [[sources/posix-errno]] |
| ERRORS (161-163) | 읽는 쪽이 없는 pipe에 쓰면 `EPIPE`와 `SIGPIPE` | [[concepts/resilience]] |

## 핵심

- `write()`는 버퍼의 `nbyte` 바이트를 fd에 연결된 파일에 쓰려 한다 (raw/posix-write.md:27). 일반 파일처럼 위치 이동이 되는 파일은 파일 위치에서 쓰고, 쓴 만큼 위치를 늘린다 (raw/posix-write.md:31).
- `O_APPEND`가 설정돼 있으면 쓰기마다 파일 위치를 파일 끝으로 옮기고, 옮기는 것과 쓰는 것 사이에 다른 파일 수정이 끼어들지 않는다 (raw/posix-write.md:35).
- pipe에 쓰기 (raw/posix-write.md:55-73):
  - pipe에는 파일 위치가 없어 늘 끝에 덧붙인다 (57).
  - `{PIPE_BUF}` 바이트 이하의 쓰기는 다른 스레드의 쓰기와 섞이지 않는다 (59).
  - `O_NONBLOCK`이면 막히지 않는다 (65). `{PIPE_BUF}`보다 큰 쓰기는 한 바이트라도 쓸 수 있으면 쓸 수 있는 만큼 쓰고 그 수를 돌려주고, 전혀 못 쓰면 -1과 `EAGAIN` (69-73).
- pipe가 아닌 non-blocking fd도 당장 다 못 받으면, `O_NONBLOCK`일 때 쓸 수 있는 만큼만 쓰고 그 수를 돌려주거나 -1과 `EAGAIN`이다 (raw/posix-write.md:75-79).
- fd가 소켓이면 플래그 없는 `send()`와 같다 (raw/posix-write.md:85).
- 성공하면 실제로 쓴 바이트 수를 돌려주고, 그 수는 `nbyte`보다 클 수 없다. 실패하면 -1과 errno (raw/posix-write.md:99).
- 어떤 프로세스도 읽으려고 열지 않은 pipe에 쓰면 `EPIPE`로 실패하고 스레드에 `SIGPIPE`도 보낸다 (raw/posix-write.md:161-163).

## 과제 적용 (판단)

- CGI 입력 pipe에 쓰다 스크립트가 먼저 끝나면 읽는 쪽이 사라져 `SIGPIPE`가 온다 (raw/posix-write.md:163). `SIGPIPE`의 기본 동작은 프로세스 종료라서 서버는 이를 무시하도록 설정한다 → [[sources/posix-signal-h]], [[lessons/14-resilience]] 14.1.
- non-blocking pipe와 소켓은 일부만 쓰일 수 있으므로(raw/posix-write.md:71, raw/posix-write.md:79), 서버는 POLLOUT마다 한 번 쓰고 쓴 만큼 앞으로 간다(`written_`). 일반 파일 쓰기(`FileWriter`)는 과제가 `poll()`을 요구하지 않으므로 (raw/subject.md:134) 다 쓸 때까지 반복한다.
- 로그 파일은 `O_APPEND`로 열고 줄마다 `write`를 한 번 부른다. 그래서 각 줄이 파일 끝에 붙는다 (raw/posix-write.md:35, [[analysis/design-decisions]] 19).

## 관련

- [[sources/posix-read]], [[sources/posix-send]], [[sources/posix-pipe]], [[sources/posix-open]], [[sources/posix-signal-h]], [[lessons/02a-unix-system-calls]]
