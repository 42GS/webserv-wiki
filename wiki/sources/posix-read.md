---
title: POSIX read() — fd에서 최대 nbyte를 읽고 읽은 수를 돌려줌, 0은 끝
type: source
sources: [raw/posix-read.md, raw/subject.md]
updated: 2026-10-29
---

# POSIX read()

원본: `raw/posix-read.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/read.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-read.md:1-3). 원본 HTML은 `raw/posix-read.source.html`. 같은 페이지에 `pread()`가 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-read.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[SIO]`·`[SHM]`·`[TYM]`·`[XSI]` 표시가 링크로, 선택 범위 그림이 `<img>` 태그로 남음(raw/posix-read.md:66), EXAMPLES 코드가 들여쓴 코드 블록이 됨, 빈 `<br>`가 `\` 한 줄이 됨(raw/posix-read.md:116).

## 과제와 관련된 부분

서버는 CGI pipe (`webserv/src/cgi/CgiPipes.cpp:70`)와 일반 파일 (`webserv/src/fs/FileReader.cpp:22`, `webserv/src/http/ResponseStream.cpp:121`)을 `read`로 읽는다. 소켓은 `recv`로 읽는다 → [[sources/posix-recv]]. 기초 설명은 [[lessons/02a-unix-system-calls]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (26) | fd에서 최대 `nbyte` 바이트를 버퍼로 읽으려 한다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (30, 34) | 일반 파일은 파일 위치에서 읽고 위치를 늘린다. 끝에서는 0 | [[lessons/11-response]] |
| DESCRIPTION (38-44) | 빈 pipe: 쓰는 쪽이 없으면 0(끝), 있으면 non-blocking은 `EAGAIN`, blocking은 기다림 | [[lessons/13-cgi]] |
| DESCRIPTION (56) | 요청보다 적게 읽을 수 있다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (64) | 소켓이면 플래그 없는 `recv()`와 같다 | [[sources/posix-recv]] |
| RETURN VALUE (76) | 성공하면 읽은 바이트 수(0 이상), 실패하면 -1과 errno | [[sources/posix-errno]] |

## 핵심

- `read()`는 열린 fd에 연결된 파일에서 `nbyte` 바이트를 버퍼로 읽으려 한다 (raw/posix-read.md:26).
- 일반 파일처럼 위치 이동이 되는 파일은 fd의 파일 위치(offset)에서 읽기 시작하고, 실제로 읽은 만큼 위치를 늘린다 (raw/posix-read.md:30). 시작 위치가 파일 끝 이후면 0을 돌려준다 (raw/posix-read.md:34).
- 빈 pipe를 읽을 때 (raw/posix-read.md:38-44):
  - 쓰기 쪽을 연 프로세스가 없으면 0을 돌려준다. 파일 끝(EOF)이라는 뜻이다.
  - 쓰기 쪽이 열려 있고 `O_NONBLOCK`이면 -1과 `EAGAIN`.
  - 쓰기 쪽이 열려 있고 `O_NONBLOCK`이 아니면 데이터가 오거나 모든 쓰기 쪽이 닫힐 때까지 막힌다.
- 성공하면 읽은 바이트 수를 돌려주고, 그 수는 `nbyte`보다 클 수 없다. 남은 바이트가 적거나, 시그널로 끊기거나, pipe 등에 당장 읽을 수 있는 바이트가 적으면 더 적을 수 있다 (raw/posix-read.md:56).
- fd가 소켓이면 플래그 없는 `recv()`와 같다 (raw/posix-read.md:64).
- 성공하면 0 이상의 읽은 바이트 수, 실패하면 -1과 errno (raw/posix-read.md:76).

## 과제 적용 (판단)

- 과제는 일반 디스크 파일의 `read`·`write`에는 `poll()`이 필요 없다고 한다 (raw/subject.md:134). pipe는 기다릴 수 있는 I/O라 `poll()`을 거친 뒤에만 읽는다 (raw/subject.md:136).
- CGI 출력 pipe에서 0은 스크립트가 출력을 끝냈다는 뜻이다(쓰기 쪽이 모두 닫힘, raw/posix-read.md:40). 서버는 0과 -1을 모두 "끝"으로 보고 errno를 읽지 않는다 ([[lessons/13-cgi]] 13.4).
- 한 번에 요청한 만큼 다 읽힌다는 보장이 없으므로(raw/posix-read.md:56), 파일 읽기는 0이 나올 때까지 반복하고 pipe는 POLLIN마다 한 번씩 읽어 쌓는다.

## 관련

- [[sources/posix-write]], [[sources/posix-recv]], [[sources/posix-pipe]], [[sources/posix-open]], [[sources/posix-errno]], [[lessons/02a-unix-system-calls]]
