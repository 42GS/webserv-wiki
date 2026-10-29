---
title: "레슨 2: 컴퓨터끼리 말하는 법"
type: lesson
sources: [raw/posix-recv.md]
updated: 2026-10-29
---

# 레슨 2: 컴퓨터끼리 말하는 법

이전: [[lessons/01-request-journey]] · 다음: [[lessons/02a-unix-system-calls]]

## 2.1 프로세스

> [!example] 쉬운 예
> 프로그램은 요리책이고, **프로세스**는 그 요리책을 보며 지금 요리하고 있는 요리사다. 같은 요리책으로 요리사가 여러 명 일할 수도 있다. 요리사마다 번호표(**pid**)가 있다.

`./webserv`를 실행하면 프로세스가 하나 생긴다. CGI를 실행할 때는 이 프로세스가 `fork()`로 자기 복사본(자식 프로세스)을 만든다 ([[lessons/13-cgi]]).

## 2.2 파일 디스크립터(fd)

> [!example] 쉬운 예
> 도서관에서 책을 빌리면 "3번" 번호표를 준다. 그다음부터는 "3번 책 주세요", "3번 반납이요"처럼 번호로만 말한다. 운영체제도 파일이나 연결을 열면 작은 정수 번호를 준다. 그 번호가 **fd**다.

- 0, 1, 2번은 처음부터 열려 있다: 표준 입력, 표준 출력, 표준 에러.
- 파일(`open`), 네트워크 연결(`socket`, `accept`), 프로세스 사이의 관(`pipe`)이 모두 fd다. 그래서 모두 `read`/`write`(소켓은 `recv`/`send`)로 다룬다.
- 다 쓴 fd는 `close()`로 돌려줘야 한다. 안 돌려주면 번호표가 바닥나 새 연결을 못 받는다 ([[lessons/07-event-loop]] "fd 고갈").

## 2.3 IP 주소, 포트, 소켓

> [!example] 쉬운 예
> **IP 주소**는 아파트 주소, **포트**는 호수다. "127.0.0.1 아파트 8080호"로 편지를 보내면 그 호수에서 기다리는 프로그램이 받는다. **소켓**은 그 집의 우편함이다.

- `127.0.0.1`은 "내 컴퓨터 자신"이다. `0.0.0.0`으로 열면 "이 컴퓨터의 모든 주소"에서 받는다.
- 서버는 소켓을 만들고(`socket`), 주소에 묶고(`bind`), 손님을 기다린다(`listen`). 이것이 **listen 소켓**이다. 손님이 오면 `accept`가 그 손님 전용 소켓(새 fd)을 만든다.

`src/core/Listener.cpp:40-53` — listen 소켓 열기 (주석은 줄임):

```cpp
bool ok = (fd_ = socket(AF_INET, SOCK_STREAM, 0)) >= 0;
ok = ok &&
     setsockopt(fd_, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(enable)) == 0;
ok = ok && bind(fd_, rawAddress, sizeof(address)) == 0;
ok = ok && listen(fd_, SOMAXCONN) == 0;
// bind 뒤에 non-blocking으로 바꾼다 (POSIX bind)
ok = ok && fcntl(fd_, F_SETFL, O_NONBLOCK) == 0;
```

> [!tip] 왜 이렇게?
> - `SO_REUSEADDR`: 서버를 껐다가 바로 다시 켤 때 "Address already in use"로 실패하지 않게 한다. 재시작 직후 bind를 macOS와 Ubuntu에서 실험했다 → [[sources/os-observed-bind]].
> - `bind`를 마친 뒤에 non-blocking으로 바꾼다. non-blocking 소켓의 `bind`는 바로 끝나지 않고 나중에 끝날 수 있다 → [[sources/posix-bind]].
> - 하나라도 실패하면 이유를 출력하고 종료 코드 1로 끝난다. 이때만 `errno`를 읽는다 (`src/core/Listener.cpp:60`). errno 금지는 read/write 뒤에 대한 것이라 시작 단계의 오류 메시지에 쓰는 것은 괜찮다고 봤다 **(판단)** → [[analysis/subject-vs-evaluation]].

## 2.4 TCP: 순서대로 오는 바이트 줄

> [!example] 쉬운 예
> 종이컵 전화기를 생각하자. 말한 순서대로 들린다. 하지만 "문장 하나"씩 끊어 오지는 않는다. "안녕하" 하고 끊겼다가 "세요"가 올 수도 있다.

TCP는 바이트를 순서대로 보내지만 **메시지 경계를 지켜 주지 않는다**. 스트림 소켓에서는 메시지 경계를 무시한다 (raw/posix-recv.md:62). 그래서 `recv` 한 번에 요청이 반만 올 수도, 두 개가 붙어 올 수도 있다. 요청 해석기([[lessons/09-request-parser]])는 어디서 끊겨도 같은 결과가 나오게 만들었고, 모든 위치에서 나눠 넣는 테스트가 있다 ([[analysis/test-plan]] P-01).

## 2.5 블로킹과 논블로킹

> [!example] 쉬운 예
> 친구에게 전화했는데 친구가 "잠깐만" 하고 10분 동안 말이 없다. **블로킹**은 그동안 수화기를 들고 아무것도 못 하는 것이다. **논블로킹**은 "지금 할 말 없으면 바로 끊어"라고 약속해 두는 것이다. 그러면 다른 친구에게도 전화할 수 있다.

보통 `recv`는 데이터가 올 때까지 멈춘다(블로킹). 서버가 한 손님 때문에 멈추면 다른 손님은 응답을 못 받는다. 그래서 과제는 non-blocking과 `poll()`을 요구한다 ([[lessons/04-poll]]). listen 소켓(`src/core/Listener.cpp:53`), 손님 소켓(`:89`), CGI pipe(`src/cgi/CgiProcess.cpp:158-159`)를 모두 `O_NONBLOCK`으로 바꾼다.

> [!question]- 확인 문제: recv가 0을 돌려주면 무슨 뜻일까? -1은?
> 0은 상대가 정상적으로 닫았다는 뜻이고, -1은 오류다 → [[sources/posix-recv]]. 우리 서버는 둘 다 이유를 묻지 않고(errno를 보지 않고) 연결을 닫는다 (`src/http/Connection.cpp:167`).
