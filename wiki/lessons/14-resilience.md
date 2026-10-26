---
title: "레슨 14: 절대 죽지 않기"
type: lesson
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/posix-waitpid.md, raw/valgrind-observed-sigint.md, raw/siege.pod]
updated: 2026-10-27
---

# 레슨 14: 절대 죽지 않기

이전: [[lessons/13-cgi]] · 다음: [[lessons/15-defense-qa]]

> [!danger] 0점 조건
> 프로그램은 어떤 경우에도(메모리가 바닥나도) 크래시하거나 예상치 못하게 끝나면 안 된다 (raw/subject.md:46). 평가 중 segfault나 비정상 종료는 0점이다 (raw/evaluation-sheet-en.md:24). 누수도 확인한다 (raw/evaluation-sheet-en.md:25).

자세한 요구 목록: [[concepts/resilience]].

## 14.1 시그널

> [!example] 쉬운 예
> **SIGPIPE**: 상대가 이미 전화를 끊었는데 계속 말하면 기절하는 병이 있다고 하자. 기본 설정이 "기절"이라 서버가 그대로 죽는다. 그래서 "기절하지 말고 실패만 알려 줘"라고 설정한다. **SIGINT**(Ctrl-C): 종이 울리면 책가방을 던지고 뛰어나가지 말고, 정리하고 나가자고 약속한다.

`src/core/Signals.cpp:21-40`:

```cpp
volatile std::sig_atomic_t g_stopRequested = 0;   // 서버의 유일한 전역 상태
void requestStop(int) { g_stopRequested = 1; }     // 핸들러는 플래그만
void install() {
  std::signal(SIGPIPE, SIG_IGN);                   // 끊긴 소켓에 send해도 죽지 않음
  std::signal(SIGINT, requestStop);
  std::signal(SIGTERM, requestStop);
}
```

> [!tip] 왜?
> - SIGPIPE의 기본 동작은 프로세스 종료다 → [[sources/posix-signal-h]]. `send`의 `MSG_NOSIGNAL`로도 막을 수 있지만, CGI pipe의 `write`에는 플래그가 없어 허용 함수 `signal`로 무시하는 쪽을 골랐다 → [[concepts/resilience]].
> - 핸들러에서는 할 수 있는 일이 아주 적어서 플래그만 세운다. 정리는 루프가 끝난 뒤 소멸자가 한다. 핸들러가 닿을 수 있는 곳이 전역뿐이라 "전역 상태 금지"의 의도한 예외다 ([[analysis/design]] 10절).
> - SIGINT 기본 동작으로 끝나면 해제 코드가 실행되지 않아, valgrind가 해제하지 않은 메모리를 still reachable로 보고했다. 모두 해제하고 끝낸 경우만 "All heap blocks were freed"였다 (raw/valgrind-observed-sigint.md:111-138, raw/valgrind-observed-sigint.md:212-215).
> - `SIGCHLD`는 기본 동작으로 둔다. `SIG_IGN`으로 바꾸면 자식의 종료 상태를 받을 수 없게 된다 (raw/posix-waitpid.md:323).

## 14.2 예외는 세 겹으로 막는다

1. **handler 하나**: `onEvent`에서 난 예외 → `EventLoop`가 잡아 그 handler의 `onFailure` → 그 연결만 닫힌다 (`src/core/EventLoop.cpp:62-66`).
2. **타임아웃 점검**: `checkTimeout`에서 난 예외 → `Server`가 잡아 그 연결만 닫는다 (`src/core/Server.cpp:84-88`).
3. **마지막 그물**: 그래도 빠져나온 예외(poll 목록을 만들다 메모리 부족) → `main`이 잡아 메시지를 내고 종료 코드 1 (`src/main.cpp:85-89`). `std::terminate`로 갑자기 끝나지 않는다.

- 소멸자에서는 예외를 내보내지 않는다(`~CgiProcess`는 reaper에 못 넘기면 그 자리에서 죽이고 기다린다).
- 예외 처리 밖에서 매 바퀴 도는 `ChildReaper::reap`은 메모리를 할당하지 않는다(제자리에서 지움).
- 예외 없이 프로세스가 죽는 메모리 고갈은 본문 상한(100MB), CGI 출력 상한(16MB), 업로드 파일 수 상한으로 미리 막는다.

## 14.3 확인한 것

| 점검 | 결과 |
|---|---|
| 단위 테스트 | 102개 통과 |
| 통합 테스트 (Ubuntu, 느린 테스트 포함) | 118개 통과 |
| siege `-b -c 50`, 빈 페이지 2분 | 3,721,561건, availability 100%, RSS 1.9MB 일정 |
| valgrind (통합 테스트 전체, 모의 평가) | 오류 0, 누수 0, 남은 fd는 표준 3개 |
| Electric Fence | 크래시 없음 |

근거: [[analysis/test-plan]] 8절, [[analysis/mock-evaluation]].

> [!example] 쉬운 예 — siege
> siege는 손님 50명을 한꺼번에 들여보내 계속 주문하게 하는 연습 도구다. availability는 "문을 두드린 손님 중 몇 %가 들어왔나"다. 4xx·5xx 응답은 깎이지 않고, 연결이 거부되거나 끊기면 깎인다 (raw/siege.pod:373-378). 평가 기준은 99.5% 초과다 (raw/evaluation-sheet-en.md:114) → [[concepts/testing]].
