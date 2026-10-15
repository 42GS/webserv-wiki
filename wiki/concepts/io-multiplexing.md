---
title: I/O 멀티플렉싱과 non-blocking 규칙
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/posix-poll.md, raw/posix-send.md, raw/posix-recv.md, raw/evaluation-sheet.md, raw/posix-fcntl.md, raw/os-observed-pipe-poll.md]
updated: 2026-10-15
---

# I/O 멀티플렉싱과 non-blocking 규칙

평가의 "Check the code and ask questions" 단계에서 확인하는 영역이다. 여기서 하나라도 불명확하거나 틀리면 평가가 멈춘다 (raw/evaluation-sheet-en.md:61).

## 규칙 목록

| # | 규칙 | subject | 평가표 |
|---|---|---|---|
| 1 | 서버는 항상 non-blocking | raw/subject.md:129 | — |
| 2 | 모든 클라이언트·서버 I/O(listen 포함)에 `poll()`(또는 동등 함수) **하나만** 사용 | raw/subject.md:130 | raw/evaluation-sheet-en.md:52 |
| 3 | read와 write를 **동시에** 감시 | raw/subject.md:131 | raw/evaluation-sheet-en.md:53 |
| 4 | `poll()`이 메인 루프 안에 있음 | — | raw/evaluation-sheet-en.md:53 |
| 5 | event-driven fd(listen/client socket, CGI pipe/FIFO)는 readiness가 표시됐을 때만 I/O | raw/subject.md:132, raw/subject.md:136 | raw/evaluation-sheet-en.md:54, raw/evaluation-sheet-en.md:58 |
| 6 | read/write 후 `errno`로 제어 흐름을 바꾸지 않음 (로그는 가능) | raw/subject.md:133 | raw/evaluation-sheet-en.md:57 |
| 7 | socket I/O가 에러를 반환하면 클라이언트 제거 | — | raw/evaluation-sheet-en.md:55 |
| 8 | 반환값은 `-1`과 `0`을 모두 처리 | — | raw/evaluation-sheet-en.md:56 |
| 9 | 일반 디스크 파일의 동기 I/O가 이벤트 루프를 멈추게(stall) 하지 않음 | — | raw/evaluation-sheet-en.md:59 |

> [!danger] 0점 조건
> - readiness 없이 socket/pipe에 `read`/`recv`/`write`/`send` → 0점 (raw/subject.md:136)
> - `poll()`이 메인 루프에 없거나 read/write를 동시에 검사하지 않음 → 0점, 평가 종료 (raw/evaluation-sheet-en.md:53)
> - read/recv/write/send 후 errno 검사 → 0점, 평가 종료 (raw/evaluation-sheet-en.md:57)

## readiness 1회당 몇 번 I/O 해도 되나

- 영어 원문은 "EAGAIN/EWOULDBLOCK이 나올 때까지 read/write한 뒤 메인 루프로 돌아가도 된다"고 한다 (raw/evaluation-sheet-en.md:54).
- 구버전 한국어 정리본은 "클라이언트당 select() 1회에 read 1번 또는 write 1번"이었다 (raw/evaluation-sheet.md:50). 영어 원문 기준으로 이 제한은 없다.

> [!warning] 모순: EAGAIN까지 반복 vs errno 금지
> EAGAIN이 나왔는지 알려면 `errno`를 봐야 한다. 그런데 subject는 read/write 후 errno로 동작을 바꾸는 것을 금지하고 (raw/subject.md:133), 평가표도 errno는 로그만 허용한다 (raw/evaluation-sheet-en.md:57).
> 따라서 **readiness 1회에 read/write 1번**만 하는 구현이 subject와 평가표 양쪽을 확실히 만족한다 (**판단**). 반복 허용 문구는 "그렇게 해도 감점하지 않는다"로만 읽는다.
> → [[analysis/subject-vs-evaluation]]

## 적용 범위

- 대상: 데이터를 기다릴 수 있는 fd — socket, pipe/FIFO (raw/subject.md:136). 평가표는 TTY도 포함한다 (raw/evaluation-sheet-en.md:58).
  CGI pipe도 포함된다 (raw/evaluation-sheet-en.md:54) → [[concepts/cgi]].
- 예외: 일반 디스크 파일 (raw/subject.md:134, raw/evaluation-sheet-en.md:58). 단, 설정 파일이나 작은 정적 파일 읽기가 루프를 막지 않는지 확인한다 (raw/evaluation-sheet-en.md:59). 큰 파일을 한 번에 읽어 응답하는 구조라면 디펜스에서 설명할 준비가 필요하다.

## 사용할 수 있는 함수

- `select`, `poll`, `epoll_create`/`epoll_ctl`/`epoll_wait`, `kqueue`/`kevent` 중 무엇이든 가능 (raw/subject.md:113, raw/subject.md:121, raw/evaluation-sheet-en.md:50).
- 해당 함수의 매크로·헬퍼(`FD_SET` 등)도 사용 가능 (raw/subject.md:138).

> [!note] 결정: `poll()` 사용 (2026-10-15)
> 개발은 macOS, 평가는 Ubuntu 22.04에서 한다(사용자 결정·확인). POSIX 표준인 `poll()`(raw/posix-poll.md:6)을 쓰면 같은 코드가 양쪽에서 돌고(두 OS에서 실측, raw/os-observed-pipe-poll.md:171, raw/os-observed-pipe-poll.md:186), 디펜스에서 설명할 이벤트 메커니즘도 하나다 (raw/evaluation-sheet-en.md:50). `epoll`은 Linux 전용, `kqueue`는 BSD·macOS 계열 전용이라 한 코드로 두 OS를 지원하기 어렵다고 알려져 있지만, 각 OS 문서로 확인하지 않은 일반 지식이라 이 결정의 근거로 쓰지 않는다 (**미확인** — 확인: Ubuntu `man 7 epoll`의 CONFORMING TO/STANDARDS 절, macOS `man 2 kqueue`).
- `fcntl()`은 `F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC` 플래그로만 사용 가능 (raw/subject.md:155-157).
  - non-blocking 설정은 `fcntl(fd, F_SETFL, O_NONBLOCK)`이다. `F_SETFL`은 파일 상태 플래그를 인자 값으로 설정하고, 성공하면 -1이 아닌 값을 돌려준다 (raw/posix-fcntl.md:58-60, raw/posix-fcntl.md:198-200).
  - POSIX는 `F_GETFL`로 읽어서 수정한 뒤 쓰라고 권하지만 (raw/posix-fcntl.md:391), `F_GETFL`은 허용 목록에 없다. 그래서 인자를 `O_NONBLOCK` 하나로 주면 다른 상태 플래그는 지워질 수 있다. `socket`·`accept`·`pipe`로 막 만든 fd에는 문제가 될 가능성이 낮다고 보지만 근거는 없다 (**판단**) → [[analysis/subject-vs-evaluation]] 1.11절.
  - non-blocking을 지원하지 않는 fd라면 `O_NONBLOCK`이 무시될 수 있다 (raw/posix-fcntl.md:60). 일반 디스크 파일은 `poll()` 대상이 아니므로 상관없다 (raw/subject.md:134).

> [!note] macOS 한정 문구
> `fcntl()` 허용은 "For macOS only" 절에 있다 (raw/subject.md:153-157). Linux에서 `fcntl()` 사용이 허용되는지는 subject 문구만으로는 불분명하다. 허용 함수 목록(raw/subject.md:113)에는 `fcntl`이 들어 있다.
> 평가가 Ubuntu에서 이뤄지므로 이 질문은 실제 쟁점이다. 같은 플래그 제한(`F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC`)을 지켜 Linux에서도 쓰고, 디펜스에서 허용 목록(raw/subject.md:113)을 근거로 설명한다 (**판단**). 평가자 해석은 **미확인** — 확인: 평가 전 평가자·intra 공지와 대조.

## poll() 동작 (POSIX)

### revents 처리

| 비트 | 의미 | 할 일 | 근거 |
|---|---|---|---|
| `POLLIN` | 읽기가 막히지 않음. 결과는 데이터, EOF, 에러 중 하나 | listen 소켓이면 `accept`, 아니면 read 1회. 0이면 상대가 닫은 것 | raw/posix-poll.md:42, raw/posix-poll.md:80, raw/posix-poll.md:98, raw/posix-recv.md:72 |
| `POLLOUT` | 확인 시점에 1바이트 쓰기가 막히지 않았을 것 | write 1회. 일부만 쓰일 수 있으니 보낸 위치를 기록 | raw/posix-poll.md:58, raw/posix-poll.md:171 |
| `POLLERR` | fd 아래 객체의 상태에서만 생기고 read/write가 -1로 알릴 오류 상태. `EAGAIN`은 포함하지 않음 | 클라이언트 제거 | raw/posix-poll.md:70, raw/posix-poll.md:173 |
| `POLLHUP` | 장치 연결 끊김, 또는 pipe·FIFO의 쓰는 쪽이 모두 닫힘. 장치 연결 끊김의 의미는 장치마다 다름. `POLLIN`과 동시에 올 수 있고 `POLLOUT`과는 동시에 오지 않음 | 남은 데이터를 EOF까지 읽은 뒤 정리 (CGI pipe는 [[concepts/cgi]]) | raw/posix-poll.md:74, raw/posix-poll.md:82 |
| `POLLNVAL` | fd가 열려 있지 않음 | 서버 버그 신호. 항목 제거 | raw/posix-poll.md:78 |

- `POLLHUP`·`POLLERR`·`POLLNVAL`은 `events`에 넣지 않아도 조건이 맞으면 설정된다 (raw/posix-poll.md:86). 매 루프에서 항상 확인한다.
- **OS 차이 (실측, [[sources/os-observed-pipe-poll]]):**
  - 비트 검사 순서: Ubuntu는 읽는 쪽이 닫힌 pipe에 `POLLOUT`+`POLLERR`를 함께 보고한다 (raw/os-observed-pipe-poll.md:186). `POLLERR`·`POLLHUP`을 `POLLOUT`보다 먼저 본다 (**판단**).
  - `POLLHUP`만 와도 읽기: Ubuntu는 데이터를 다 읽은 pipe에 `POLLIN` 없이 `POLLHUP`만 보고한다 (raw/os-observed-pipe-poll.md:193). `POLLHUP`에서도 `read()`해서 0을 확인한다 (**판단**).
  - `events=0`으로 남겨 두지 않기: Ubuntu는 `events=0`이어도 `POLLHUP`을 보고하고 macOS는 보고하지 않았다 (raw/os-observed-pipe-poll.md:180, raw/os-observed-pipe-poll.md:195). 다 쓴 fd를 `events=0`으로 남기면 Ubuntu에서 `poll()`이 바로 돌아와 busy waiting이 된다 (raw/posix-poll.md:175). 목록에서 뺀다 (**판단**).
- `POLLERR`로 오류를 알 수 있으므로, read/write 뒤에 errno를 보지 않고도 클라이언트를 제거할 수 있다 → 규칙 6·7.

### POLLOUT은 보낼 데이터가 있을 때만

- 상태를 바꾸지 않고 `poll()`을 다시 부르면 바로 같은 결과가 돌아와 busy waiting이 된다 (raw/posix-poll.md:175).
- 소켓은 대부분 쓰기 가능 상태라서, 보낼 데이터가 없는데 `POLLOUT`을 켜 두면 루프가 쉬지 않고 돈다. 응답이 준비됐을 때 켜고, 다 보내면 끈다 (**판단**).
- 규칙 3(read와 write를 동시에 감시, raw/subject.md:131)은 한 번의 `poll()` 호출이 읽기와 쓰기 관심사를 함께 다룬다는 뜻으로 읽는다. 모든 fd에 항상 `POLLOUT`을 켜라는 뜻은 아니다 (**판단**).

### 그 밖의 동작

| 동작 | 근거 |
|---|---|
| `timeout`이 -1이면 무한 대기, 양수면 최대 대기 시간(ms), 0이면 바로 반환 | raw/posix-poll.md:34, raw/posix-poll.md:88 |
| 반환값: 양수는 이벤트가 있는 fd 수, 0은 타임아웃, -1은 실패(errno 설정) | raw/posix-poll.md:114 |
| fd가 음수인 항목은 무시되고 `revents`가 0이 됨 | raw/posix-poll.md:84 |
| `poll()` 자체는 `O_NONBLOCK`의 영향을 받지 않음 | raw/posix-poll.md:92 |
| 일반 파일은 항상 읽기·쓰기 가능으로 나옴 | raw/posix-poll.md:96 |
| 감시하는 fd에는 항상 `O_NONBLOCK`을 켜라고 권장. 확인 후 실제 I/O 사이에 상태가 바뀔 수 있기 때문 | raw/posix-poll.md:171 |

과제 적용:
- 클라이언트·CGI 타임아웃을 검사하려면 `timeout`을 -1이 아닌 유한한 값으로 주고, 매 루프마다 시간 초과된 연결을 정리한다 → [[concepts/connection-management]].
- 일반 파일이 항상 준비 상태로 나오는 것이 subject가 디스크 파일을 `poll()` 대상에서 빼 준 이유와 맞는다 (raw/subject.md:134).
- `poll()`이 -1을 돌려줄 때 errno를 확인해도 되는지는 [[analysis/subject-vs-evaluation]] 1.8절.

## recv·send 반환값 처리 (POSIX)

평가표는 반환값을 `-1`만 또는 `0`만 검사하면 부족하고 둘 다 처리하라고 한다 (raw/evaluation-sheet-en.md:56).

| 함수 | 반환값 | 의미 | 할 일 | 근거 |
|---|---|---|---|---|
| `recv` | 양수 | 받은 바이트 수. 스트림 소켓이라 메시지 경계가 없음 | 버퍼에 이어 붙이고 파서 진행 | raw/posix-recv.md:62, raw/posix-recv.md:72 |
| `recv` | **0** | 받을 데이터가 없고 상대가 정상적으로 연결을 닫음 | 클라이언트 정리 | raw/posix-recv.md:72 |
| `recv` | -1 | 에러 (`ECONNRESET` 등) | errno를 보지 않고 클라이언트 정리 | raw/posix-recv.md:72, raw/posix-recv.md:88-90 |
| `send` | 양수 | 보낸 바이트 수 | 보낸 만큼 위치를 옮기고, 남았으면 다음 `POLLOUT`에서 이어 보냄 | raw/posix-send.md:74, raw/posix-poll.md:171 |
| `send` | 0 | 이 문서에 따로 정의되지 않음 (0바이트를 보냈다는 뜻) | 길이 0으로 호출하지 않도록 하고, 생기면 클라이언트 정리 (**판단**) | raw/posix-send.md:74 |
| `send` | -1 | 에러 (`EPIPE`, `ECONNRESET` 등) | errno를 보지 않고 클라이언트 정리 | raw/posix-send.md:74, raw/posix-send.md:90-92, raw/posix-send.md:118-120 |

- `send`가 요청한 길이보다 적게 보낼 수 있다는 문장은 `send()` 문서에 명시되어 있지 않다. 다만 `poll()`의 쓰기 가능은 1바이트만 보장하므로 (raw/posix-poll.md:171) 반환값만큼만 진행했다고 가정해야 한다 (**판단**).
- flags가 0이면 `recv`는 `read`와, `send`는 `write`와 같다 (raw/posix-recv.md:142, raw/posix-send.md:156). CGI pipe에는 `read`/`write`를 쓰고 같은 표를 적용한다.

### 왜 readiness 1회에 I/O 1번이면 errno가 필요 없나

- non-blocking 소켓에 읽을 데이터가 없으면 `recv`는 `EAGAIN`/`EWOULDBLOCK`으로 실패하고 (raw/posix-recv.md:66), 보낼 공간이 없으면 `send`가 실패한다 (raw/posix-send.md:66).
- `poll()`의 읽기 준비는 확인한 시점에 호출했다면 막히지 않고 데이터·EOF·에러 중 하나를 돌려줬을 것이라는 뜻이다 (raw/posix-poll.md:80, raw/posix-poll.md:171). 다만 POSIX는 확인 시점과 실제 호출 사이에 상태가 바뀔 수 있다고 한다 (raw/posix-poll.md:171). 단일 스레드 서버에서 같은 fd를 다른 곳에서 읽거나 쓰지 않으면 이런 경우는 드물다고 보고, 한 번 호출한 결과가 -1이면 원인(`EAGAIN` 포함)과 관계없이 클라이언트를 정리한다 (**판단**).
- 반대로 EAGAIN까지 반복해서 읽는 방식(raw/evaluation-sheet-en.md:54)은 마지막 -1이 EAGAIN인지 진짜 에러인지 errno로 구분해야 하므로 규칙 6과 부딪힌다 → 위 "readiness 1회당 몇 번 I/O 해도 되나".

## 디펜스에서 설명해야 할 것

평가표 질문 항목 (raw/evaluation-sheet-en.md:49-54):

1. HTTP 서버의 기본 동작
2. 어떤 이벤트 메커니즘을 썼는지
3. 그 함수가 어떻게 동작하는지
4. 하나의 `poll()`로 accept와 클라이언트 read/write를 어떻게 다루는지
5. `poll()`부터 클라이언트 I/O까지의 코드 경로를 직접 보여주기

## 관련

- [[concepts/resilience]] — hang·크래시 방지
- [[analysis/subject-vs-evaluation]]
- [[sources/posix-poll]], [[sources/posix-send]], [[sources/posix-recv]]
