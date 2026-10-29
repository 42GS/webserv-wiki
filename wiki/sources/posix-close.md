---
title: POSIX close() — fd를 반납, 마지막 fd가 닫히면 pipe 데이터 버림·소켓 파괴
type: source
sources: [raw/posix-close.md]
updated: 2026-10-29
---

# POSIX close()

원본: `raw/posix-close.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/close.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-close.md:1-3). 원본 HTML은 `raw/posix-close.source.html`. 같은 페이지에 Issue 8에서 더해진 `posix_close()`가 있다.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-close.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `[XSI]`·`[SHM]` 표시가 링크로, 선택 범위 그림이 `<img>` 태그로 남음, EXAMPLES 코드가 들여쓴 코드 블록이 됨, SEE ALSO의 `exec` 링크 앞에 빈 링크가 하나 생김 (raw/posix-close.md:163).

## 과제와 관련된 부분

연결·파일·pipe를 다 쓰면 `close`로 반납한다. CGI 자식은 `execve` 전에 상속받은 fd(3 이상)를 모두 닫는다 (`webserv/src/cgi/CgiProcess.cpp:90-105`). 기초 설명은 [[lessons/02a-unix-system-calls]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (26) | fd를 반납해 다음 `open` 등이 다시 쓸 수 있게 한다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (28) | 시그널로 끊긴 경우 말고는 오류가 나도 fd는 닫힌다 (`EBADF` 제외) | 아래 "과제 적용" |
| DESCRIPTION (30, 32) | pipe의 fd가 모두 닫히면 남은 데이터는 버린다. 열린 파일 설명은 마지막 fd가 닫힐 때 풀린다 | [[lessons/13-cgi]] |
| DESCRIPTION (42) | 소켓은 그 소켓의 fd가 모두 닫혀야 파괴된다 | [[lessons/02b-tcp-connections]] |
| APPLICATION USAGE (133) | `fork` 뒤 `close`를 반복하는 방식은 멀티스레드 부모에서 안전하지 않다 | 아래 "과제 적용" |

## 핵심

- `close()`는 fd를 반납한다. 반납이란 다음 `open()` 등이 그 fd 번호를 다시 돌려줄 수 있게 하는 것이다 (raw/posix-close.md:26).
- 시그널로 끊기면 결과가 여럿 중 하나로 정해지지 않았다(unspecified). 그 밖의 오류에서는 (`EBADF`, 즉 처음부터 잘못된 fd를 빼고) fd가 닫힌다 (raw/posix-close.md:28).
- pipe에 연결된 fd가 모두 닫히면 pipe에 남은 데이터는 버린다 (raw/posix-close.md:30). 열린 파일 설명은 그것을 가리키는 fd가 모두 닫힐 때 풀린다 (raw/posix-close.md:32).
- 소켓은 그 소켓의 fd가 모두 닫혀야 파괴된다 (raw/posix-close.md:42).
- 성공하면 0, 실패하면 -1과 errno (raw/posix-close.md:48).
- 구현은 자식 프로세스가 물려받아야 하는 fd를 쓸 수 있다. 그래서 `close()`는 프로그램이 직접 얻은 fd와 표준 fd 세 개에만 이식성 있게 쓸 수 있다. 멀티스레드 부모에서 `fork` 뒤 `exec` 전에 `close`를 반복해 fd 새어 나감을 막는 방식은 안전하지 않고, 물려줄 것이 아니면 처음부터 `FD_CLOEXEC`로 여는 것이 권장된다 (raw/posix-close.md:133).

## 과제 적용 (판단)

- 서버는 `close()`의 결과를 보지 않는 곳이 많다. 원문상 `EBADF`·`EINTR`이 아니면 fd는 닫히고(raw/posix-close.md:28), 서버는 시그널 핸들러를 `SIGINT`·`SIGTERM`에만 둬 플래그만 세운다 ([[lessons/14-resilience]] 14.1). 그래서 다시 닫을 일이 없다고 본다.
- CGI 자식은 `/dev/fd`를 읽어 3 이상의 fd를 모두 닫는다. 원문이 경고하는 상황(raw/posix-close.md:133)과 두 가지가 다르다. 첫째, 서버는 스레드가 하나라 `fork`와 다른 스레드의 `open` 사이에 경쟁이 없다. 둘째, 닫은 직후 `execve`로 다른 프로그램이 되므로, 구현이 부모 쪽에 쓰던 fd가 닫혀도 서버 코드에는 영향이 없다. `FD_CLOEXEC`를 쓰지 않는 이유는 과제가 `fcntl`의 `F_SETFD`를 허용 목록에 넣지 않았기 때문이다 → [[concepts/cgi]] 1절, [[analysis/subject-vs-evaluation]] 1.11절.
- 클라이언트 소켓을 닫으면 소켓이 파괴되므로(raw/posix-close.md:42), 아직 읽지 않은 요청이 남아 있으면 상대에게 reset이 갈 수 있다. 그래서 서버는 닫기 전에 남은 입력을 읽어 버리는 DRAIN 상태를 둔다 → [[lessons/08-connection]] 8.3, [[lessons/02b-tcp-connections]].

## 관련

- [[sources/posix-open]], [[sources/posix-dup]], [[sources/posix-pipe]], [[sources/posix-fork]], [[sources/posix-exec]], [[lessons/02a-unix-system-calls]]
