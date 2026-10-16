---
title: macOS 실측 — MSG_NOSIGNAL과 leaks -atExit의 SIGINT 종료 보고
type: source
sources: [raw/macos-observed-sigpipe-leaks.md, raw/valgrind-observed-sigint.md, raw/posix-send.md, raw/evaluation-sheet-en.md]
updated: 2026-10-16
---

# macOS 실측 — `MSG_NOSIGNAL`과 `leaks -atExit`의 SIGINT 종료 보고

원본: `raw/macos-observed-sigpipe-leaks.md`. 개발 환경인 macOS에서 SDK 헤더를 출력하고, C++98 테스트 프로그램을 Apple clang으로 빌드해 실행한 출력을 그대로 담았다 (2026-10-16, raw/macos-observed-sigpipe-leaks.md:3-4). 환경은 macOS 26.6.2, arm64, Apple clang 21.0.0이다 (raw/macos-observed-sigpipe-leaks.md:14-24).

- 받은 목적: [[concepts/resilience]]의 **미확인** 두 건 — macOS가 `MSG_NOSIGNAL`을 지원하는지, `leaks`가 SIGINT로 끝난 프로세스를 어떻게 보고하는지.

## 1. `MSG_NOSIGNAL`

- SDK의 `sys/socket.h`에 `MSG_NOSIGNAL`이 `0x80000`으로 정의되어 있다. `__DARWIN_C_LEVEL >= 200809L` 조건 안이다 (raw/macos-observed-sigpipe-leaks.md:51-53). Apple 전용 소켓 옵션 `SO_NOSIGPIPE`도 있다 (raw/macos-observed-sigpipe-leaks.md:46).
- 상대가 닫은 loopback TCP 연결에 `send`를 세 번 했다:

| 방식 | 결과 | 근거 |
|---|---|---|
| 플래그 없음 | 1회차 성공, 2회차에서 프로세스가 끝남. 종료 코드 141 | raw/macos-observed-sigpipe-leaks.md:114-117 |
| `send` flags에 `MSG_NOSIGNAL` | 2·3회차 `-1`, errno 32 (`Broken pipe`). 프로세스는 끝까지 실행 | raw/macos-observed-sigpipe-leaks.md:118-124 |
| `setsockopt(SO_NOSIGPIPE)` | 위와 같음 | raw/macos-observed-sigpipe-leaks.md:125-131 |

- 종료 코드 141은 128 + 13이고, 13은 `SIGPIPE`의 시그널 번호다 (**판단**: 쉘의 시그널 종료 코드 관례와 시그널 번호는 원본에 없다).
- POSIX의 `MSG_NOSIGNAL` 정의(`SIGPIPE`는 보내지 않고 `EPIPE`는 그대로 돌려준다, raw/posix-send.md:58-60)와 같은 동작이다.

## 2. `leaks -atExit`와 SIGINT

- man page: `-atExit`는 명령을 실행하고 그 프로세스가 끝날 때 leaks를 실행한다 (raw/macos-observed-sigpipe-leaks.md:139-143). 종료 코드는 0이 누수 없음, 1이 누수 발견, 1보다 크면 오류다 (raw/macos-observed-sigpipe-leaks.md:156-161).
- 프로그램은 valgrind 측정과 같은 `sigleak.cpp`다 (raw/macos-observed-sigpipe-leaks.md:166) → [[sources/valgrind-observed-sigint]].

| 모드 | leaks 보고 | leaks 종료 코드 | valgrind (비교) | 근거 |
|---|---|---|---|---|
| `default` (SIGINT 기본 동작) | **아무것도 출력하지 않음** | 0 | still reachable | raw/macos-observed-sigpipe-leaks.md:224-226 |
| `return` (해제 없이 `main` 반환) | `0 leaks for 0 total leaked bytes` | 0 | definitely lost 80, indirectly lost 1,000 | raw/macos-observed-sigpipe-leaks.md:228-256 |
| `exit` (해제 없이 `std::exit(0)`) | `0 leaks for 0 total leaked bytes` | 0 | still reachable | raw/macos-observed-sigpipe-leaks.md:259-287 |
| `cleanup` (모두 해제) | `0 leaks for 0 total leaked bytes` | 0 | All heap blocks were freed | raw/macos-observed-sigpipe-leaks.md:290-318 |

- valgrind 열은 Ubuntu 24.04 측정 결과다 (raw/valgrind-observed-sigint.md:111-138, raw/valgrind-observed-sigint.md:157-163, raw/valgrind-observed-sigint.md:192-196, raw/valgrind-observed-sigint.md:212-215).

- `default`를 두 번 더 실행해도 출력 없이 종료 코드 0이었다. leaks 없이 실행하면 종료 코드는 130이었다 (raw/macos-observed-sigpipe-leaks.md:326-330).
- 대조 실험: 포인터를 모두 지운 뒤 정상 종료하는 `lost.cpp`에서는 `11 leaks for 1216 total leaked bytes`를 보고하고 종료 코드 1로 끝났다 (raw/macos-observed-sigpipe-leaks.md:386-388, raw/macos-observed-sigpipe-leaks.md:411). 이 환경에서 leaks가 누수를 잡는다는 뜻이다.
- 출력이 나온 실행마다 "Process … is not debuggable" 안내가 있었다 (raw/macos-observed-sigpipe-leaks.md:231, raw/macos-observed-sigpipe-leaks.md:363). 대조 실험에서 누수가 보고됐으므로 집계에는 지장이 없었다.

## 과제 적용 (판단)

- `MSG_NOSIGNAL`은 macOS와 Linux 모두에서 쓸 수 있다. 다만 pipe(CGI)에 쓰는 `write`에는 flags가 없으므로, `signal(SIGPIPE, SIG_IGN)`을 기본으로 하는 기존 방침은 그대로다 → [[concepts/resilience]].
- SIGINT 기본 동작으로 서버가 죽으면 `leaks -atExit`는 검사 결과를 내지 않는다. 그런데 종료 코드는 0이라 "누수 없음"과 구분되지 않는다. 출력이 없으므로 평가자가 이를 검사 통과로 볼 가능성은 낮다.
- `return` 모드에서 valgrind는 definitely lost를 보고했는데 leaks는 0을 보고했다. 이유는 **미확인**이다 (가능성: leaks가 아직 메모리에 남은 포인터 값을 참조로 본다. 확인: leaks의 스캔 방식 문서). 어느 쪽이든 leaks가 0이라고 해서 valgrind에서도 깨끗하다는 보장은 없다.
- 평가표는 "컴퓨터에 있는 도구"를 쓰라고 하고 leaks, valgrind, e_fence를 예로 든다 (raw/evaluation-sheet-en.md:25). 평가 PC가 Ubuntu 22.04이므로 macOS 도구인 `leaks`보다 valgrind가 쓰일 가능성이 높다 (Ubuntu에 `leaks`가 없는지는 확인하지 않았다). 결론은 바뀌지 않는다: 핸들러는 플래그만 세우고, 메인 루프가 모두 해제한 뒤 종료한다.

> [!note] 측정 범위
> macOS 한 대에서 `leaks -atExit`만 측정했다. 실행 중인 프로세스에 `leaks <pid>`를 거는 방식은 측정하지 않았다. `e_fence`는 [[sources/efence-observed-ubuntu2204]]. SIGINT는 `pkill`로 보냈고 터미널 Ctrl-C와 같은지는 확인하지 않았다.
