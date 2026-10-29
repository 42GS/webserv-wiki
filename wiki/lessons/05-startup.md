---
title: "레슨 5: 서버가 켜질 때"
type: lesson
sources: [raw/subject.md, raw/design-checks-observed.md]
updated: 2026-10-29
---

# 레슨 5: 서버가 켜질 때

이전: [[lessons/04a-cpp98-basics]] · 다음: [[lessons/06-config-parsing]]

> [!example] 쉬운 예
> 가게 문을 열기 전 순서: 운영 규칙표를 읽고(설정), 벽시계를 맞추고(시계), "불나면 정리하고 나가자" 약속을 정하고(시그널), 문을 열고(listen), 손님을 맞기 시작한다(이벤트 루프).

`src/main.cpp:48-93` (줄임):

```cpp
int main(int argc, char** argv) {
  if (argc > limits::kMaxArgc) { /* usage 출력 */ return EXIT_FAILURE; }
  const char* configPath = (argc == limits::kMaxArgc) ? argv[1] : limits::kDefaultConfigPath;
  configs = loadConfigFile(configPath);          // 1. 설정 (실패 → ConfigError → 종료 1)
  Clock clock(limits::kClockFile);
  if (!clock.refresh()) return fail(...);        // 2. 시계
  signals::install();                            // 3. 시그널
  EventLoop loop(clock);
  ChildReaper reaper;                            // server보다 먼저 선언 → 더 오래 산다
  Server server(configs, loop, reaper, clock.now());
  if (!server.openListeners(error)) return fail(error);   // 4. listen
  try { loop.run(server); }                      // 5. 루프 (SIGINT까지)
  catch (const std::exception& error) { return fail(...); }
  return EXIT_SUCCESS;                           // 소멸자들이 모두 정리
}
```

## 5.1 인자

설정 파일은 명령줄 인자로 받거나 기본 경로를 쓴다 (raw/subject.md:127). 인자가 없으면 `conf/default.conf`, 두 개 이상이면 사용법을 출력하고 끝낸다 (`kMaxArgc = 2`: 프로그램 이름 + 설정 파일).

## 5.2 시계: 왜 파일로 시간을 재나?

> [!example] 쉬운 예
> 교실에 시계가 없고 시계를 보는 것도 금지라고 하자. 대신 우체국은 쓸 수 있다. 엽서를 한 장 보내면 우체국이 날짜 도장을 찍어 준다. 그 도장을 보고 지금 몇 시인지 안다.

타임아웃에는 지금 시각이 필요하다 (요청이 무한히 멈추면 안 됨, raw/subject.md:139). 그런데 허용 함수 목록(raw/subject.md:113)에 `time()` 같은 시간 함수가 없다. 그래서 시계 파일을 `open` → 1바이트 `write` → `close` → `stat`으로 수정 시각을 읽는다 (`src/core/Clock.cpp:14-30`).

> [!tip] 왜 이렇게?
> - 사용자 결정 10: 평가자가 문제 삼을 수 없는 보수적인 쪽 → [[analysis/design-decisions]] 10.
> - 이 값이 `time()`과 같은지 macOS와 Ubuntu 22.04 컨테이너에서 6번씩 재서 모두 같았다 (raw/design-checks-observed.md:60-80).
> - "poll 타임아웃 횟수로 어림하기"는 버렸다. 요청이 계속 들어오면 poll이 매번 일찍 돌아와 시간이 흐르지 않은 것처럼 보인다.
> - 시계는 루프 한 바퀴에 한 번만 갱신한다 (`src/core/EventLoop.cpp:29`). 그 바퀴의 모든 타임아웃 판단이 같은 시각을 쓴다.
> - 날짜 문자열(`Sun, 06 Nov 1994 08:49:37 GMT`)도 `gmtime` 없이 직접 계산한다. Howard Hinnant의 civil_from_days 알고리즘의 숫자를 그대로 썼다 (`src/core/HttpDate.cpp:61-77`).

## 5.3 객체가 사라지는 순서

C++에서는 함수가 끝날 때 지역 변수가 **선언의 역순**으로 소멸한다. `server`가 먼저 사라지며 모든 연결을 지우고(각 연결의 CGI 자식은 `reaper`에 넘김), 그다음 `reaper`가 남은 자식을 모두 `SIGKILL`하고 기다린다 (`src/core/ChildReaper.cpp:17-23`). 그래서 `reaper`를 `server`보다 먼저 선언했다 (`src/main.cpp:69-74`).

> [!info] 평가 때
> "Ctrl-C를 누르면 어떻게 정리되나요?" → 시그널 핸들러는 플래그만 세우고([[lessons/14-resilience]]), 루프가 플래그를 보고 빠져나온 뒤 `main`이 반환하며 소멸자가 모두 정리한다. valgrind로 돌린 뒤 SIGINT로 끄면 "All heap blocks were freed"가 나온다 → [[analysis/mock-evaluation]].
