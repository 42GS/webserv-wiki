---
title: "레슨 2A: 운영체제에게 부탁하기 — 시스템 콜 기초"
type: lesson
sources: [raw/posix-open.md, raw/posix-read.md, raw/posix-write.md, raw/posix-close.md, raw/posix-errno.md, raw/posix-fork.md, raw/posix-exec.md, raw/posix-pipe.md, raw/posix-dup.md, raw/subject.md]
updated: 2026-10-29
---

# 레슨 2A: 운영체제에게 부탁하기 — 시스템 콜 기초

이전: [[lessons/02-networking-basics]] · 다음: [[lessons/02b-tcp-connections]]

코드 기준: webserv 커밋 `4db9510`. 이 장은 [[lessons/02-networking-basics]]의 fd 설명을 이어서, 서버가 실제로 부르는 함수들이 무엇을 약속하는지 원문으로 본다.

> [!example] 쉬운 예
> 프로그램은 식당 손님이고 운영체제는 주방이다. 손님은 직접 주방에 들어가 불을 켤 수 없다. 대신 정해진 주문서("파일 열어 주세요", "이 사람 데려와 주세요")를 내면 주방이 처리하고 결과를 돌려준다. 이 주문서가 **시스템 콜**이다. 이 위키에서는 POSIX가 정한 `open`, `read`, `fork` 같은 함수를 그렇게 부른다.

## 2A.1 파일 열기·읽기·쓰기·닫기

> [!example] 쉬운 예
> 도서관에서 책을 빌리면(`open`) 번호표(fd)를 준다. 번호표로 몇 쪽씩 읽고(`read`), 메모를 끼우고(`write`), 다 보면 번호표를 돌려준다(`close`). 책갈피(파일 위치)는 읽은 만큼 자동으로 넘어간다.

| 함수 | 하는 일 | 원문 |
|---|---|---|
| `open` | 파일과 fd를 잇는 "열린 파일 설명"을 새로 만든다. 위치는 파일 처음 | raw/posix-open.md:27, raw/posix-open.md:31 |
| `read` | 최대 `nbyte`를 읽고 읽은 바이트 수를 돌려준다. 파일 끝이면 0 | raw/posix-read.md:26, raw/posix-read.md:34 |
| `write` | 최대 `nbyte`를 쓰고 쓴 바이트 수를 돌려준다 | raw/posix-write.md:27, raw/posix-write.md:99 |
| `close` | fd를 반납해 다음 `open`이 그 번호를 다시 쓸 수 있게 한다 | raw/posix-close.md:26 |

**가장 중요한 약속: 요청한 만큼 다 된다는 보장이 없다.** `read`는 남은 바이트가 적거나, 시그널로 끊기거나, pipe에 당장 있는 바이트가 적으면 `nbyte`보다 적게 읽을 수 있다 (raw/posix-read.md:56). `write`도 쓴 수가 `nbyte`보다 작을 수 있다 (raw/posix-write.md:99). 그래서 "한 번 불렀으니 끝"이 아니라 반환값을 보고 이어서 처리해야 한다.

`src/fs/FileReader.cpp:13-35` — 작은 파일 전체 읽기 (줄여 옮기고, 오른쪽 주석은 설명을 위해 붙였다):

```cpp
const int fd = open(path.c_str(), O_RDONLY);       // 읽기 전용으로 연다
if (fd < 0) return false;                           // -1이면 실패
for (;;) {
  const ssize_t got = read(fd, buffer, sizeof(buffer));
  if (got == 0) break;                              // 0 = 파일 끝
  if (got < 0 || ...) { ok = false; break; }        // -1 = 오류
  content.append(buffer, got);                      // 읽은 만큼만 붙인다
}
close(fd);                                          // 번호표 반납
```

> [!tip] 왜 이렇게?
> - 0이 나올 때까지 반복하는 이유: 한 번의 `read`가 파일 전체를 준다는 보장이 없다 (raw/posix-read.md:56).
> - 일반 파일은 `poll()` 없이 바로 읽어도 된다. 과제가 일반 디스크 파일은 예외로 둔다 (raw/subject.md:134). 소켓과 pipe는 다르다 → [[lessons/04-poll]].
> - `close`를 모든 경로에서 부른다. 안 하면 fd가 바닥나 새 연결을 받지 못한다 → [[lessons/07-event-loop]].

## 2A.2 실패는 반환값으로, 이유는 errno로

함수 대부분은 실패하면 -1을 돌려주고 `errno`라는 정수에 이유(`EAGAIN`, `EMFILE` 등)를 넣는다 (raw/posix-open.md:149, raw/posix-read.md:76). `errno`는 반환값이 실패를 알릴 때만 봐야 하고, 성공한 호출 뒤의 값은 정해져 있지 않다 (raw/posix-errno.md:25).

> [!danger] 0점 조건
> 읽기·쓰기 뒤에 `errno`를 보고 서버 동작을 바꾸는 것은 엄격히 금지다 (raw/subject.md:133). 서버는 `recv`·`send`·`read`·`write`의 -1을 그냥 "실패"로 보고 연결이나 pipe를 닫는다. 준비된 fd에만 한 번씩 읽고 쓰기 때문에 `EAGAIN`을 구분할 필요가 없다 → [[lessons/04-poll]], [[lessons/15-defense-qa]] Q7.

## 2A.3 프로세스 복제: fork

> [!example] 쉬운 예
> 요리사(프로세스)가 분신술을 써서 똑같은 요리사를 하나 더 만든다. 분신은 하던 일, 들고 있던 번호표(fd)까지 똑같이 갖고 있다. 둘을 구분하는 방법은 하나다. 분신술의 결과로 원래 요리사는 "분신의 번호"를, 분신은 "0"을 받는다.

- `fork()`는 새 프로세스를 만든다. 자식은 몇 가지를 빼면 부모의 정확한 복사본이다 (raw/posix-fork.md:26).
- 자식은 부모 fd의 사본을 갖고, 같은 번호의 fd는 같은 열린 파일을 가리킨다 (raw/posix-fork.md:34).
- 성공하면 자식에는 0, 부모에는 자식의 프로세스 ID(pid)를 돌려준다. 실패하면 부모에 -1 (raw/posix-fork.md:82).

과제는 `fork`를 CGI에만 쓰게 한다 (raw/subject.md:144). 서버는 CGI 스크립트를 실행할 때만 `fork`한다 (`src/cgi/CgiProcess.cpp:171`).

## 2A.4 다른 프로그램으로 변신: execve

> [!example] 쉬운 예
> 분신이 이번에는 변신술을 쓴다. 겉모습(프로세스 번호)은 그대로인데 머릿속이 통째로 "파이썬 요리사"로 바뀐다. 변신에 성공하면 원래 기억으로 돌아오지 않는다. 돌아왔다면 변신에 실패한 것이다.

- exec 함수는 현재 프로세스 이미지를 새 이미지로 바꾸고, 성공하면 돌아오지 않는다 (raw/posix-exec.md:33). 돌아왔다면 실패이고 -1이다 (raw/posix-exec.md:191).
- `argv`(명령줄 인자)와 `envp`(환경 변수)는 널 포인터로 끝나는 문자열 배열이다 (raw/posix-exec.md:67, raw/posix-exec.md:69).
- 열린 fd는 `FD_CLOEXEC`가 없으면 새 프로그램에서도 열려 있다 (raw/posix-exec.md:75). 현재 작업 디렉토리도 이어진다 (raw/posix-exec.md:157).
- 무시하도록 설정한 시그널은 (`SIGCHLD` 말고) 계속 무시된다 (raw/posix-exec.md:91).

**환경 변수**는 `envp` 배열의 `"이름=값"` 문자열이다. CGI는 요청 정보를 이 방식으로 스크립트에 넘긴다(`REQUEST_METHOD=GET`, `QUERY_STRING=...`) (`src/cgi/CgiEnv.cpp:141-147`) → [[lessons/13-cgi]] 13.2.

## 2A.5 프로세스 사이의 관: pipe와 dup2

> [!example] 쉬운 예
> 두 방 사이에 관을 뚫는다. 한쪽 구멍에 말을 넣으면(쓰는 끝) 다른 쪽 구멍으로 먼저 넣은 말부터 나온다(읽는 끝). `dup2`는 문패를 바꿔 다는 것이다. 분신의 "입"(표준 출력, 1번) 자리에 관의 구멍을 달아 두면, 분신은 평소처럼 말하는데 그 말이 관을 타고 원래 요리사에게 간다.

- `pipe()`는 읽는 끝 `fildes[0]`과 쓰는 끝 `fildes[1]`을 만든다. 쓴 것을 먼저 쓴 순서대로 읽는다 (raw/posix-pipe.md:26, raw/posix-pipe.md:28).
- 쓰는 끝을 연 프로세스가 하나도 없을 때 빈 pipe를 읽으면 0, 즉 끝이다 (raw/posix-read.md:40, raw/posix-pipe.md:30).
- `dup2(a, b)`는 fd `b`가 `a`와 같은 것을 가리키게 한다. `b`가 열려 있으면 먼저 닫는다 (raw/posix-dup.md:31).

CGI 하나에 pipe 두 개를 쓰는 배선 (`src/cgi/CgiProcess.cpp`):

```text
            input pipe                         output pipe
서버 ──write──▶ [1]═══▶[0] ──dup2──▶ 스크립트 0번(표준 입력)
서버 ◀──read─── [0]◀═══[1] ◀──dup2── 스크립트 1번(표준 출력)

1. pipe 두 개를 만든다                              (:56-61)
2. fork                                             (:171)
3. 부모: 자식 쪽 끝(input[0], output[1])을 닫는다   (:173-174)
4. 자식: dup2로 0·1번에 연결                        (:214)
         3번 이상 fd를 모두 닫는다                  (:217)
         스크립트 디렉토리로 chdir                  (:218)
         SIGPIPE를 기본 동작으로                    (:219)
         execve                                     (:226)
```

> [!tip] 왜 이렇게?
> - **부모가 자식 쪽 끝을 닫는 이유:** 서버가 출력 pipe의 쓰는 끝을 들고 있으면, 스크립트가 끝나도 "쓰기로 연 프로세스"가 남아 `read`가 0을 주지 않는다 (raw/posix-pipe.md:30, raw/posix-read.md:40). 서버는 스크립트 출력이 끝난 것을 영영 모르게 된다.
> - **자식이 3번 이상을 닫는 이유:** 자식은 부모의 fd를 모두 물려받고(raw/posix-fork.md:34), exec 뒤에도 그대로 남는다(raw/posix-exec.md:75). 닫지 않으면 스크립트가 다른 손님의 소켓을 쥐고 있게 된다. `FD_CLOEXEC`를 켜는 `F_SETFD`는 과제 허용 목록에 없어 직접 닫는다 → [[sources/posix-close]].
> - **`SIGPIPE`를 되돌리는 이유:** 서버는 `SIGPIPE`를 무시하는데, 무시 설정은 exec 뒤에도 남는다(raw/posix-exec.md:91). 스크립트는 보통 프로그램처럼 실행되게 기본값으로 돌린다 → [[sources/posix-exec]].

> [!info] 평가 때
> "CGI의 표준 입출력을 어떻게 연결했나요?"라는 질문에는 위 배선 그림 하나로 답할 수 있다. `fork`는 CGI에만 쓴다는 규칙(raw/subject.md:144)과, 부모가 쓰지 않는 끝을 닫아야 EOF가 온다는 점을 함께 말한다.

> [!question]- 확인 문제 1: `read`가 요청한 1024바이트보다 적은 300바이트를 돌려줬다. 오류일까?
> 아니다. `read`는 남은 바이트가 적거나 pipe에 당장 있는 바이트가 적으면 요청보다 적게 읽을 수 있다 (raw/posix-read.md:56). 오류는 -1이고, 0은 끝이다.

> [!question]- 확인 문제 2: 서버가 `fork` 뒤 출력 pipe의 쓰는 끝을 닫는 것을 잊으면?
> 스크립트가 출력을 끝내고 종료해도, 서버 자신이 쓰는 끝을 들고 있어 pipe가 "쓰기로 열린" 채로 남는다 (raw/posix-pipe.md:30). 그러면 `read`가 0(EOF)을 돌려주지 않아, 서버는 CGI 시간 제한(10초)에 걸릴 때까지 기다리게 된다 **(판단)**.

> [!question]- 확인 문제 3: `execve` 다음 줄의 코드는 언제 실행될까?
> `execve`가 실패했을 때만이다. 성공하면 돌아오지 않는다 (raw/posix-exec.md:33). 그래서 그 다음에는 자식을 끝내는 `std::exit(EXIT_FAILURE)`만 있다 (`src/cgi/CgiProcess.cpp:229`).
