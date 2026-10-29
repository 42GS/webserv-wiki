---
title: POSIX open() — 파일과 fd를 잇는다, 접근 모드와 O_CREAT·O_EXCL·O_APPEND·O_TRUNC
type: source
sources: [raw/posix-open.md]
updated: 2026-10-29
---

# POSIX open()

원본: `raw/posix-open.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-open.md:1-3). 원본 HTML은 `raw/posix-open.source.html`. 같은 페이지에 `openat()`이 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-open.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[OH]`·`[SIO]`·`[XSI]` 표시가 링크로, 선택 범위 그림이 `<img>` 태그로 남음, EXAMPLES·RATIONALE 코드가 들여쓴 코드 블록이 됨, SEE ALSO의 `exec` 링크 앞에 빈 링크가 하나 생김 (raw/posix-open.md:386).

## 과제와 관련된 부분

서버는 정적 파일 (`webserv/src/fs/FileReader.cpp:15`, `webserv/src/http/ResponseStream.cpp:92`, `O_RDONLY`), 업로드 파일 (`webserv/src/fs/FileWriter.cpp:21`, `O_WRONLY | O_CREAT | O_EXCL`), 로그 파일 (`webserv/src/core/Logger.cpp:42`, `O_WRONLY | O_CREAT | O_APPEND`)을 `open`으로 연다. 기초 설명은 [[lessons/02a-unix-system-calls]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (27-31) | 파일과 fd를 잇는 "열린 파일 설명"을 새로 만들고, 위치는 파일 처음 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (35-55) | 접근 모드는 정확히 하나: `O_RDONLY`, `O_WRONLY`, `O_RDWR` 등 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (59-61) | `O_APPEND`: 쓰기마다 끝으로 | [[sources/posix-write]] |
| DESCRIPTION (71-73, 83-85) | `O_CREAT`: 없으면 일반 파일로 만듦. `O_EXCL`과 함께면 있으면 실패, 확인과 생성은 원자적 | [[concepts/file-upload]] |
| DESCRIPTION (121-123) | `O_TRUNC`: 있는 일반 파일을 길이 0으로 | 아래 "과제 적용" |
| RETURN VALUE (149) | 성공하면 fd, 실패하면 -1과 errno, 실패하면 아무 파일도 만들거나 바꾸지 않음 | [[sources/posix-errno]] |
| ERRORS (159-161) | `O_CREAT`·`O_EXCL`인데 파일이 있으면 `EEXIST` | [[analysis/design-decisions]] 17 |

## 핵심

- `open()`은 파일과 fd를 잇는다. 파일을 가리키는 "열린 파일 설명(open file description)"과 그것을 가리키는 fd를 만든다 (raw/posix-open.md:27). 이 설명은 새것이라 다른 프로세스와 나누지 않는다 (raw/posix-open.md:29).
- 파일 위치는 파일의 처음으로 정한다 (raw/posix-open.md:31).
- `oflag`는 플래그의 OR이고, 처음 다섯 가지 접근 모드 중 정확히 하나를 줘야 한다 (raw/posix-open.md:35). 읽기 전용은 `O_RDONLY`, 쓰기 전용은 `O_WRONLY`다 (raw/posix-open.md:41-43, raw/posix-open.md:53-55).
- `O_APPEND`면 쓰기마다 파일 위치를 끝으로 옮긴다 (raw/posix-open.md:59-61).
- `O_CREAT`는 파일이 없으면 일반 파일로 만들고, 권한 비트는 세 번째 인자에서 프로세스의 umask로 지운 비트를 뺀 값이 된다 (raw/posix-open.md:71-73).
- `O_CREAT`와 `O_EXCL`을 함께 주면 파일이 이미 있을 때 실패한다. 있는지 확인하는 것과 만드는 것은 같은 이름을 `O_EXCL`·`O_CREAT`로 여는 다른 스레드에 대해 원자적이다. 경로가 심볼릭 링크면 무엇을 가리키든 `EEXIST`로 실패한다 (raw/posix-open.md:83-85).
- `O_TRUNC`는 이미 있는 일반 파일을 쓰기로 열 때 길이를 0으로 자른다 (raw/posix-open.md:121-123).
- 성공하면 음이 아닌 fd를 돌려주고, 실패하면 -1과 errno를 돌려주며 아무 파일도 만들거나 바꾸지 않는다 (raw/posix-open.md:149).

## 과제 적용 (판단)

- 업로드 파일은 `O_CREAT | O_EXCL`로 만든다. 같은 이름의 파일이 있으면 `open`이 실패하므로, 미리 확인한 뒤 그 사이에 다른 요청이 같은 이름을 만들어도 덮어쓰지 않는다 (raw/posix-open.md:85) → [[analysis/design-decisions]] 17.
- 시계 파일은 `O_TRUNC`로 매번 비우고 1바이트를 써서 수정 시각을 갱신한다 (`webserv/src/core/Clock.cpp:15-16`) → [[analysis/design-decisions]] 10.
- 로그 파일은 `O_APPEND`로 열어 각 줄을 끝에 덧붙인다 → [[analysis/design-decisions]] 19.

## 관련

- [[sources/posix-close]], [[sources/posix-read]], [[sources/posix-write]], [[sources/posix-errno]], [[lessons/02a-unix-system-calls]]
