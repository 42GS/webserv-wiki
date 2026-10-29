---
title: POSIX exec — 현재 프로세스를 다른 프로그램으로 바꾼다, argv·envp, 물려받는 fd와 시그널
type: source
sources: [raw/posix-exec.md]
updated: 2026-10-29
---

# POSIX exec (execve 등)

원본: `raw/posix-exec.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-exec.md:1-3). 원본 HTML은 `raw/posix-exec.source.html`. `environ`, `execl`, `execle`, `execlp`, `execv`, `execve`, `execvp`, `fexecve`를 한 페이지에서 다룬다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-exec.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: 선택 범위 표시(`[XSI]` 등)가 링크와 `<img>` 태그로 남음, EXAMPLES 코드가 들여쓴 코드 블록이 되고 `<br>`가 빈 줄이 됨, RATIONALE의 대입 호환 표가 GFM 표가 됨(칸 내용은 같음, raw/posix-exec.md:406-412).

## 과제와 관련된 부분

과제 허용 함수 중 이 페이지의 것은 `execve`다. CGI 자식은 `execve(인터프리터, [인터프리터, 스크립트 파일 이름], 환경)`을 부른다 (`webserv/src/cgi/CgiProcess.cpp:221-226`). 기초 설명은 [[lessons/02a-unix-system-calls]], 흐름은 [[lessons/13-cgi]] 13.3.

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (33) | 현재 프로세스 이미지를 새 이미지로 바꾼다. 성공하면 돌아오지 않는다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (55, 67, 69) | `execve`의 `path`는 실행 파일 경로, `argv`·`envp`는 널 포인터로 끝나는 문자열 배열 | [[concepts/cgi]] 2절 |
| DESCRIPTION (75) | `FD_CLOEXEC`가 없는 fd는 새 이미지에서도 열려 있다 | [[sources/posix-close]] |
| DESCRIPTION (91) | `SIG_IGN`은 (`SIGCHLD` 말고) 그대로 무시, 잡던 시그널은 기본 동작으로 | 아래 "과제 적용" |
| DESCRIPTION (157) | 현재 작업 디렉토리를 물려받는다 | [[lessons/13-cgi]] |
| RETURN VALUE (191) | 돌아왔다면 실패: -1과 errno | [[analysis/design-decisions]] 12 |

## 핵심

- exec 함수들은 현재 프로세스 이미지를 새 프로세스 이미지로 바꾼다. 새 이미지는 실행 가능한 일반 파일로 만든다. 성공한 exec는 돌아오지 않는다. 부르던 이미지가 새 이미지로 덮이기 때문이다 (raw/posix-exec.md:33).
- `execve()`의 `path`는 새 이미지 파일을 가리키는 경로다 (raw/posix-exec.md:55). `PATH`를 찾지 않는다. 찾는 것은 `execlp`·`execvp`뿐이다 (raw/posix-exec.md:57).
- `argv`는 널로 끝나는 문자열을 가리키는 포인터 배열이고 마지막 원소는 널 포인터여야 한다. `argv[0]`은 시작하는 프로그램과 관련된 파일 이름을 가리키는 것이 좋다(should) (raw/posix-exec.md:67).
- `envp`도 널 포인터로 끝나는 문자열 배열이고, 새 이미지의 환경이 된다 (raw/posix-exec.md:69).
- 부르던 프로세스에 열린 fd는 `FD_CLOEXEC`가 설정된 것을 빼고 새 이미지에서도 열려 있다 (raw/posix-exec.md:75).
- 시그널: 기본 동작(`SIG_DFL`)은 그대로, 무시(`SIG_IGN`)는 `SIGCHLD`를 빼고 그대로 무시, 잡도록 설정된 시그널은 기본 동작으로 바뀐다 (raw/posix-exec.md:91).
- 새 프로세스는 현재 작업 디렉토리 등을 물려받는다 (raw/posix-exec.md:157).
- exec가 돌아온다면 실패한 것이고, -1을 돌려주고 errno를 설정한다 (raw/posix-exec.md:191). 권한은 있지만 형식을 알아볼 수 없는 파일이면 `ENOEXEC` (raw/posix-exec.md:233-235).
- fd 0을 읽기용으로, 1·2를 쓰기용으로 열지 않은 채 프로그램을 실행하지 않는 것이 좋다 (raw/posix-exec.md:358).

## 과제 적용 (판단)

- 서버는 `SIGPIPE`를 무시(`SIG_IGN`)한다. 무시 설정은 exec 뒤에도 남으므로(raw/posix-exec.md:91), 자식은 `execve` 전에 `SIGPIPE`를 기본 동작으로 되돌린다(`webserv/src/cgi/CgiProcess.cpp:219`). 스크립트가 보통 프로그램처럼 동작하게 하기 위해서다 ([[analysis/design]] 9절).
- 열린 fd가 그대로 남으므로(raw/posix-exec.md:75), `FD_CLOEXEC`를 쓰지 못하는 이 서버는 exec 전에 3 이상의 fd를 닫는다 → [[sources/posix-close]].
- 작업 디렉토리가 이어지므로(raw/posix-exec.md:157), 자식이 `chdir`로 스크립트 디렉토리에 들어간 뒤 exec하면 스크립트의 상대 경로가 그 디렉토리 기준이 된다. 과제가 요구하는 동작이다 → [[lessons/13-cgi]].
- `execve`는 `PATH`를 찾지 않고(raw/posix-exec.md:55, raw/posix-exec.md:57), 자식은 `chdir` 뒤에 exec하므로 상대 경로는 스크립트 디렉토리 기준이 된다. 그래서 설정의 `cgi` 프로그램은 절대 경로여야 한다 (테스트 계획 G-18).
- 표준 입력·출력은 pipe에 연결하고, 표준 에러는 서버의 것을 물려준다. 0·1·2가 모두 열린 채로 실행된다 (raw/posix-exec.md:358).

## 관련

- [[sources/posix-fork]], [[sources/posix-dup]], [[sources/posix-pipe]], [[sources/posix-close]], [[sources/posix-exit]], [[lessons/13-cgi]]
