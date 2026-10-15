---
title: valgrind 실측 — SIGINT로 끝난 프로세스의 누수 보고
type: source
sources: [raw/valgrind-observed-sigint.md, raw/evaluation-sheet-en.md]
updated: 2026-10-16
---

# valgrind 실측 — SIGINT로 끝난 프로세스의 누수 보고

원본: `raw/valgrind-observed-sigint.md`. Ubuntu 24.04 Docker 이미지에서 heap을 할당한 뒤 SIGINT를 기다리는 C++98 프로그램을 valgrind로 실행하고, `kill -INT`로 SIGINT를 보낸 출력을 그대로 담았다 (2026-10-15, raw/valgrind-observed-sigint.md:3-4).

- 버전: valgrind-3.22.0, g++ 13.3.0 (raw/valgrind-observed-sigint.md:95-96). 옵션은 `--leak-check=full --show-leak-kinds=all` (raw/valgrind-observed-sigint.md:84).
- 프로그램은 `new char*[10]` 하나(80바이트)와 `new char[100]` 열 개(1,000바이트)를 할당한다 (raw/valgrind-observed-sigint.md:40-43).
- 받은 목적: [[concepts/resilience]] "SIGINT·SIGTERM과 누수 검사"의 **미확인** — SIGINT 기본 동작으로 끝나면 누수 검사 도구가 누수로 보고하는지.

## 결과

| 모드 | 끝나는 방식 | LEAK SUMMARY | 근거 |
|---|---|---|---|
| `default` | 핸들러 없음. SIGINT 기본 동작으로 종료 ("Process terminating with default action of signal 2") | definitely 0, indirectly 0, **still reachable 74,808바이트 12블록** (프로그램 할당 1,080바이트 + libstdc++ 블록 73,728바이트). ERROR SUMMARY 0 | raw/valgrind-observed-sigint.md:106, raw/valgrind-observed-sigint.md:111-138 |
| `return` | 핸들러가 플래그를 세우고, 해제 없이 `main`에서 반환 | **definitely lost 80바이트, indirectly lost 1,000바이트**. ERROR SUMMARY 1 error | raw/valgrind-observed-sigint.md:150-169 |
| `exit` | 핸들러가 플래그를 세우고, 해제 없이 `std::exit(0)` | definitely 0, indirectly 0, still reachable 1,080바이트 11블록. ERROR SUMMARY 0 | raw/valgrind-observed-sigint.md:181-200 |
| `cleanup` | 핸들러가 플래그를 세우고, 모두 해제한 뒤 반환 | "All heap blocks were freed -- no leaks are possible". ERROR SUMMARY 0 | raw/valgrind-observed-sigint.md:212-218 |

- `default`에서는 libstdc++ 안에서 할당된 73,728바이트 블록도 still reachable로 나왔다 (raw/valgrind-observed-sigint.md:122-124). 나머지 모드에서는 이 블록이 해제됐다(`1 frees`, raw/valgrind-observed-sigint.md:151, raw/valgrind-observed-sigint.md:182). 정상 종료 과정에서 라이브러리가 푸는 것으로 보인다 (**판단**).
- `default`의 쉘 종료 코드는 130이다 (raw/valgrind-observed-sigint.md:99).

## 과제 적용 (판단)

- SIGINT 기본 동작으로 끝나도 valgrind는 "definitely lost"를 보고하지 않는다. 그러나 해제하지 않은 메모리 전부가 still reachable로 나오고, 라이브러리 블록까지 더해진다. 평가표는 실행이 끝나기 전에 heap 할당을 모두 해제하라고 한다 (raw/evaluation-sheet-en.md:25). still reachable을 누수로 볼지는 평가자 판단이고, 이 출력은 그 요구를 만족한다고 보기 어렵다.
- 해제 없이 `main`에서 반환하면 오히려 definitely lost가 된다 (`return` 모드). 지역 변수가 사라져 포인터를 잃기 때문으로 보인다. 핸들러를 두는 것만으로는 부족하고, 정리를 빠짐없이 해야 한다.
- "All heap blocks were freed"를 보이는 것은 `cleanup` 모드뿐이었다. 기존 판단(핸들러는 플래그만 세우고, 메인 루프가 정리한 뒤 종료)을 유지한다 → [[concepts/resilience]].

> [!note] 측정 범위
> Linux(arm64)의 valgrind 하나만 측정했다. 평가표가 함께 드는 `leaks`·`e_fence`는 측정하지 않았다 (raw/evaluation-sheet-en.md:25). `leaks`는 이후 macOS에서 따로 측정했다 → [[sources/macos-observed-sigpipe-leaks]]. SIGINT는 `kill`로 프로세스 하나에 보냈고, 터미널에서 Ctrl-C를 눌렀을 때와 같은지는 확인하지 않았다. 테스트 프로그램은 `pause()`를 쓰지만 서버에서는 쓰지 않는다.
