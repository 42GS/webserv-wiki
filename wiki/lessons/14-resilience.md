---
title: "레슨 14: 절대 죽지 않기"
type: lesson
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/posix-waitpid.md, raw/valgrind-observed-sigint.md, raw/siege.pod]
updated: 2026-10-29
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
| valgrind 다시 (2026-10-29, 로그 기능 뒤, 단위 105·통합 124) | 오류 0, 누수 0, 로그 파일도 닫힘 |
| Electric Fence | 크래시 없음 |

근거: [[analysis/test-plan]] 8절, [[analysis/mock-evaluation]].

> [!example] 쉬운 예 — siege
> siege는 손님 50명을 한꺼번에 들여보내 계속 주문하게 하는 연습 도구다. availability는 "문을 두드린 손님 중 몇 %가 들어왔나"다. 4xx·5xx 응답은 깎이지 않고, 연결이 거부되거나 끊기면 깎인다 (raw/siege.pod:373-378). 평가 기준은 99.5% 초과다 (raw/evaluation-sheet-en.md:114) → [[concepts/testing]].

## 14.4 운영 로그 (2026-10-29, webserv `13982df`)

> [!example] 쉬운 예
> 가게 장부가 두 권이다. 손님 장부(`logs/access.log`)에는 손님마다 "몇 시, 누가, 무엇을 주문했고, 어떻게 나갔나"를 한 줄씩 적는다. 사고 장부(`logs/error.log`)에는 "가게 문 열고 닫음, 제빵사가 안 나옴, 손님이 주문하다 말았음" 같은 일만 적는다.

- 접근 로그: 응답마다 한 줄. `[날짜] 127.0.0.1 "GET / HTTP/1.1" 200 15` (클라이언트, 클라이언트가 보낸 요청 줄, 상태, 본문 바이트). 요청 줄이 다 오기 전에 실패하면 빈 부분이 `-`다 (`src/http/Connection.cpp:304-312`).
- 오류 로그: 시작·종료 (`src/main.cpp:83`, `:98`), CGI 시작 실패·잘못된 출력 (`src/app/RequestProcessor.cpp:170`, `:220`), CGI 시간 초과·끝나지 않은 요청·멈춘 전송 (`src/http/Connection.cpp:113`, `:120`, `:271`), `accept()` 실패 (`src/core/Server.cpp:106`).
- 한 줄은 `write()` 한 번이고, `O_APPEND`로 연다 (`src/core/Logger.cpp:42`, `:85-90`). 실패해도 다시 쓰지 않고 서비스를 계속한다.
- 클라이언트가 요청에 넣은 제어 문자는 `?`로 바꾼다 (`src/core/Logger.cpp:26-33`). 줄 끝을 넣어 가짜 로그 줄을 만들지 못하게 한다.
- `Logger`는 `main`이 갖고, 연결들은 `ConnectionServices`로 받은 참조만 쓴다 ([[analysis/design]] 4절).

> [!tip] 왜 stderr가 아니라 파일인가
> 소켓·pipe처럼 기다릴 수 있는 I/O는 `poll()`을 거쳐야 하고, 일반 디스크 파일은 예외다 (raw/subject.md:134, raw/subject.md:136). stdout·stderr는 실행 방법에 따라 pipe일 수 있다(`./webserv | tee`). 그러면 `poll()` 없이 쓰는 셈이 된다 **(판단)**. 그래서 로그는 일반 파일에만 쓴다 ([[analysis/design-decisions]] 19).

> [!warning] `logs/` 디렉토리가 있어야 시작한다
> `mkdir`은 허용 함수가 아니라 (raw/subject.md:113) 서버가 디렉토리를 만들 수 없다. 저장소에 `logs/.gitkeep`이 있고, 저장소 루트에서 실행하면 된다. 없으면 "cannot open log files"를 내고 종료 코드 1로 끝난다.

> [!info] 평가 때
> siege를 `-b -c 50`으로 1분 돌리면 접근 로그가 약 120MB(166만 줄) 쌓인다(2026-10-29 Ubuntu 컨테이너 실측). 메모리는 늘지 않는다(RSS 3.2MB → 2.3MB). 평가 전에 `logs/*.log`를 비워 두고, 평가 중에는 `tail -f logs/error.log`로 사고만 보여 준다.

> [!question]- 확인 문제: 클라이언트가 요청 줄에 CR LF를 넣으면 로그가 두 줄이 되나요?
> 아니다. 로그에 쓰는 텍스트의 제어 문자(CR·LF 포함)는 모두 `?`로 바뀌어, 호출 하나가 언제나 한 줄이다. 단위 테스트 `controlCharactersStayOnOneLine`이 이것을 본다 ([[analysis/test-plan]] L-01).
