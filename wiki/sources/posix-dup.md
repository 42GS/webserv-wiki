---
title: POSIX dup()·dup2() — fd 복제, dup2는 지정한 번호를 같은 파일로 바꿔 끼움
type: source
sources: [raw/posix-dup.md]
updated: 2026-10-29
---

# POSIX dup()·dup2()

원본: `raw/posix-dup.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/dup.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-dup.md:1-3). 원본 HTML은 `raw/posix-dup.source.html`. 같은 페이지에 Issue 8에서 더해진 `dup3()`가 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-dup.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[TYM]` 표시가 링크로, 선택 범위 그림이 `<img>` 태그로 남음, EXAMPLES 코드가 들여쓴 코드 블록이 됨.

## 과제와 관련된 부분

CGI 자식은 `dup2`로 입력 pipe를 표준 입력(0)에, 출력 pipe를 표준 출력(1)에 연결한다 (`webserv/src/cgi/CgiProcess.cpp:214`). 그러면 스크립트는 pipe를 의식하지 않고 표준 입출력으로 읽고 쓴다. 기초 설명은 [[lessons/02a-unix-system-calls]], 흐름은 [[lessons/13-cgi]] 13.3.

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (27) | `dup(fd)`는 `fcntl(fd, F_DUPFD, 0)`과 같다 | [[sources/posix-fcntl]] |
| DESCRIPTION (31) | `dup2(a, b)`: b가 a와 같은 열린 파일 설명을 가리키게 하고 b를 돌려준다. b가 열려 있으면 먼저 닫는다 | [[lessons/13-cgi]] |
| DESCRIPTION (33) | 성공하면 b의 `FD_CLOEXEC`가 꺼진다 | [[sources/posix-exec]] |
| RETURN VALUE (49) | 성공하면 fd, 실패하면 -1과 errno | [[sources/posix-errno]] |
| RATIONALE (129) | `dup2`만이 기존 fd를 원자적으로 바꿔 끼울 수 있다 | — |

## 핵심

- `dup(fildes)`는 `fcntl(fildes, F_DUPFD, 0)`과 같다. 즉 쓰이지 않는 가장 작은 번호로 fd를 복제한다 (raw/posix-dup.md:27).
- `dup2(fildes, fildes2)`는 `fildes2`가 `fildes`와 같은 열린 파일 설명을 가리키게 하고 `fildes2`를 돌려준다. `fildes2`가 이미 열린 fd면 먼저 닫는다. 둘이 같으면 닫지 않고 그대로 돌려준다. `fildes`가 잘못된 fd면 -1을 돌려주고 `fildes2`를 닫지 않는다 (raw/posix-dup.md:31).
- 성공했고 두 번호가 다르면 `fildes2`의 `FD_CLOEXEC`·`FD_CLOFORK`가 꺼진다 (raw/posix-dup.md:33).
- 성공하면 음이 아닌 fd, 실패하면 -1과 errno (raw/posix-dup.md:49).
- `dup()`은 `fcntl()`로 할 수 있어 중복이지만, `dup2()`는 기존 fd를 원자적으로 바꿔 끼우는 유일한 방법이다 (raw/posix-dup.md:129).

## 과제 적용 (판단)

- 자식에서 `dup2(input[0], 0)`·`dup2(output[1], 1)`을 하면 0과 1이 pipe를 가리키고, 원래의 0·1(서버의 표준 입출력)은 자식에서 닫힌다 (raw/posix-dup.md:31). 그 뒤 원래 pipe fd(`input[0]`, `output[1]`)는 3 이상이라 다른 상속 fd와 함께 닫힌다 → [[sources/posix-close]].
- `dup2` 뒤 0·1의 `FD_CLOEXEC`가 꺼지므로(raw/posix-dup.md:33), `execve` 뒤에도 스크립트의 표준 입출력으로 남는다 → [[sources/posix-exec]].
- `dup2`가 실패하면 자식은 `std::exit(1)`로 끝난다. 부모는 출력 없이 EOF를 받아 502로 답한다 ([[analysis/design]] 9절).

## 관련

- [[sources/posix-pipe]], [[sources/posix-fork]], [[sources/posix-exec]], [[sources/posix-close]], [[sources/posix-fcntl]], [[lessons/13-cgi]]
