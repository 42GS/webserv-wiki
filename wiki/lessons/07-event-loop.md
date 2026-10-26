---
title: "레슨 7: 이벤트 루프"
type: lesson
sources: [raw/subject.md, raw/ubuntu2204-observed-nofile.md]
updated: 2026-10-27
---

# 레슨 7: 이벤트 루프

이전: [[lessons/06-config-parsing]] · 다음: [[lessons/08-connection]]

> [!example] 쉬운 예
> 회전목마가 한 바퀴 돌 때마다 직원이 하는 일: ① 탈 사람 명단을 만든다(poll 목록). ② 손 든 사람을 확인한다(poll). ③ 손 든 사람만 한 명씩 처리한다(onEvent). ④ 떠난 사람을 명단에서 지운다. ⑤ 시계를 보고, 너무 오래 앉아만 있는 사람에게 내리라고 한다(타임아웃).

## 7.1 IoHandler: 모두 같은 모양으로

poll에 등록되는 것은 listen 소켓(`Listener`), 손님 연결(`Connection`), CGI 입력 pipe(`CgiStdin`), 출력 pipe(`CgiStdout`) 네 종류다. 모두 같은 인터페이스를 구현한다.

`include/core/IoHandler.hpp` (요약):

```cpp
class IoHandler {
 public:
  virtual int   fd() const = 0;
  virtual short wantedEvents() const = 0;   // 매 바퀴 다시 묻는다
  virtual void  onEvent(short revents) = 0; // I/O는 최대 1번
  virtual void  onFailure() = 0;            // onEvent에서 예외가 나왔을 때
};
```

> [!tip] 왜 인터페이스?
> 루프는 "fd가 몇 번이고 무엇을 기다리는지"만 알면 된다. 소켓인지 pipe인지 몰라도 되니 하나의 `poll()` 배열에 모두 넣을 수 있다. 이것이 "poll 하나로 모든 I/O"(raw/subject.md:130)를 지키는 구조다. 구체 클래스가 아니라 추상에 기대는 설계(DIP)이기도 하다.

## 7.2 한 바퀴

`src/core/EventLoop.cpp:24-55`:

```cpp
void EventLoop::run(LoopObserver& observer) {
  while (!observer.shouldStop()) {      // SIGINT/SIGTERM 플래그
    pollOnce();
    clock_.refresh();                   // 바퀴마다 시계 갱신
    observer.afterIteration(clock_.now());  // 타임아웃, 닫힌 연결 정리, 자식 회수
  }
}
void EventLoop::pollOnce() {
  std::vector<IoHandler*> polled(handlers_);
  std::vector<pollfd> fds(polled.size());
  for (...) { fds[i].fd = polled[i]->fd(); fds[i].events = polled[i]->wantedEvents(); }
  const int ready = poll(&fds[0], fds.size(), limits::kPollTimeoutMs);  // 1000ms
  if (ready <= 0) return;             // -1이어도 errno를 보지 않는다
  dispatch(polled, revents);
}
```

- **poll 타임아웃 1초**: 아무 일이 없어도 1초마다 깨어나 타임아웃을 검사한다.
- **poll이 -1**: 시그널로 끊겼거나 실패한 것이다. errno를 보지 않고 다음 바퀴로 간다. 시그널이었다면 `shouldStop()`이 참이 되어 루프가 끝난다.
- **dispatch**: revents가 있는 handler의 `onEvent`를 부르고, 예외가 나면 그 handler에만 `onFailure`를 알린다 (`EventLoop.cpp:57-70`). 연결 하나의 문제(예: 메모리 부족 예외)가 서버 전체를 끝내지 않는다.

> [!tip] 왜 unwatch를 바로 안 지우나?
> `onEvent` 처리 중에 handler가 "나 빼 줘"(unwatch)를 부를 수 있다(예: CGI pipe가 EOF를 읽고 닫힐 때). 목록을 도는 중에 바로 지우면 순회가 깨지므로, 표시만 해 두고 바퀴 끝에 뺀다 (`EventLoop.cpp:19-22`, `:72-79`). 표시된 handler는 그 바퀴에 다시 부르지 않는다 (`:61`).

## 7.3 Listener: 손님 받기

`src/core/Listener.cpp:64-98` (줄임):

```cpp
short Listener::wantedEvents() const { return paused_ ? 0 : POLLIN; }

void Listener::onEvent(short revents) {
  if ((revents & POLLIN) == 0) return;
  const int clientFd = accept(fd_, ...);
  if (clientFd < 0) { paused_ = true; return; }      // 잠시 멈춤
  fcntl(clientFd, F_SETFL, O_NONBLOCK); getsockname(...);
  where.remoteAddress = ...; where.localAddress = ...; where.localPort = ...;
  acceptor_.adopt(clientFd, where);                  // Server가 Connection을 만든다
}
```

> [!tip] 왜 accept가 실패하면 멈추나? (fd 고갈)
> fd가 다 차면 `accept`가 실패한다. 그런데 기다리는 손님은 그대로라 listen 소켓은 계속 "읽을 것 있음"이다. 그대로 두면 poll이 매번 바로 돌아와 루프가 쉬지 않고 돈다(fd 한도 16 실험에서 CPU 10% 초과). 그래서 실패하면 listener를 잠시 멈추고(`wantedEvents`가 0), 연결이 하나 닫히거나 1초가 지나면 다시 켠다 (`src/core/Server.cpp:99-102`, [[analysis/test-plan]] 8절 R5). 실패 원인은 errno로 가리지 않는다.
>
> 참고: Ubuntu 22.04 systemd 기본 fd 한도는 soft 1024다 (raw/ubuntu2204-observed-nofile.md:16). 평가 PC의 실제 값은 **미확인**이다 (확인: `ulimit -n`).

## 7.4 Server: 소유자이자 관찰자

- `Server`는 listener와 연결을 **소유**한다(만들고 지우는 책임). `EventLoop`는 아무것도 소유하지 않고 가리키기만 한다. 주인이 하나뿐이라 C++98에서도 해제 경로가 분명하다.
- `adopt`: 새 `Connection`을 만들다 메모리 부족 예외가 나면 그 fd만 닫고 계속한다 (`Server.cpp:55-71`).
- `afterIteration`: 모든 연결에 `checkTimeout`을 부르고, 닫힌 연결을 지우고, 끝난 CGI 자식을 회수한다 (`Server.cpp:79-103`).

> [!question]- 확인 문제: poll을 쓰는 곳은 코드에 몇 군데인가?
> 딱 한 곳, `src/core/EventLoop.cpp:48`이다. `src/main.cpp:86`의 `loop.run(server)` → `run` → `pollOnce` 순서로 메인 루프 안에서 불린다.
