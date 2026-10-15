---
title: 안정성 (크래시·hang·누수)
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/siege.pod, raw/siegerc.in, raw/posix-signal-h.md, raw/posix-send.md, raw/posix-waitpid.md, raw/posix-bind.md, raw/posix-exit.md, raw/posix-poll.md, raw/nginx-rewrite-module.md, raw/nginx-index-module.md, raw/nginx-core-module.md, raw/rfc3875.txt, raw/siege-sock.c, raw/valgrind-observed-sigint.md]
updated: 2026-10-15
---

# 안정성 (크래시·hang·누수)

subject와 평가표 모두 "서버가 항상 살아 있어야 한다"를 가장 강하게 요구한다.

> [!danger] 0점 조건
> - 어떤 경우에도(메모리 부족 포함) 크래시·예기치 않은 종료 → 0점 (raw/subject.md:46)
> - 디펜스 중 segfault, 예기치 않은/조기/제어되지 않은 종료 → 즉시 0점 (raw/evaluation-sheet-en.md:24)

## 요구 목록

| 요구 | 근거 |
|---|---|
| 클라이언트 연결 끊김을 제대로 처리 | raw/subject.md:129 |
| 요청이 무한히 hang하지 않음 | raw/subject.md:139 |
| 스트레스 테스트에도 항상 가용 | raw/subject.md:148, raw/subject.md:190 |
| heap 할당은 종료 전 모두 해제, 누수 검사 (`leaks`, `valgrind`, `e_fence`) | raw/evaluation-sheet-en.md:25 |
| siege 중 프로세스 메모리가 무한히 늘지 않음 | raw/evaluation-sheet-en.md:115 |
| hang 상태 연결 없음 | raw/evaluation-sheet-en.md:116 |
| 재시작 없이 `siege -b`를 무한히 돌릴 수 있음 | raw/evaluation-sheet-en.md:117 |
| `siege -b` availability 99.5% 초과. Availability는 소켓 연결 성공률이고 4xx·5xx는 포함되지 않는다 → 연결 거부·끊김·타임아웃을 막는 게 핵심. 기본 설정의 siege는 `connection = close`라 요청마다 새 연결을 맺는다고 보고(raw/siegerc.in:268, **판단**), 소켓 타임아웃(설정 파일 설명은 "socket connection timeouts", 기본 30초, raw/siegerc.in:353-354)도 실패로 센다. siege 소스에서 이 값은 `read()` 직전마다 하는 준비 검사의 대기 시간으로도 쓰인다 (raw/siege-sock.c:360-362, raw/siege-sock.c:611-626). 다만 그 검사가 읽기·쓰기 집합을 함께 보므로 응답 대기에는 실제로 걸리지 않을 수 있다 (raw/siege-sock.c:370-374, **판단**) → [[sources/siege-sock]] | raw/evaluation-sheet-en.md:114, raw/siege.pod:373-378 |
| CGI 에러·무한 루프에도 크래시 없이 에러가 보여야 함 | raw/evaluation-sheet-en.md:91-93 |

## 설계로 이어지는 점

- "메모리 부족에도 크래시 금지"(raw/subject.md:46) → `new` 실패(`std::bad_alloc`) 처리 방침이 필요하다.
- hang 금지(raw/subject.md:139) → 클라이언트·CGI 타임아웃이 필요하다.
- **내부 리다이렉트 반복 상한 (판단):** index 파일(raw/nginx-index-module.md:46), `error_page`(raw/nginx-core-module.md:542), CGI local redirect(raw/rfc3875.txt:1303-1314)는 모두 요청을 다른 경로로 다시 처리하게 한다. 에러 페이지 경로가 다시 에러를 내는 식으로 순환하면 요청이 끝나지 않는다. NGINX는 URI가 다시 쓰일 때 location 검색을 10번까지만 반복하고 (raw/nginx-rewrite-module.md:24), 넘으면 500을 돌려준다 (raw/nginx-rewrite-module.md:169). 이 과제도 요청 하나당 내부 리다이렉트 횟수에 상한을 두고, 넘으면 500을 보낸다. `error_page` 처리 중 에러가 나면 NGINX는 마지막 에러의 코드를 보낸다 (raw/nginx-core-module.md:568).
- 시그널 처리 → 아래 절.
- 시작 단계 실패(설정 파일 오류, `bind` 실패 등)는 크래시가 아니라 **원인을 담은 에러 메시지와 함께 정상 종료**해야 한다. `bind`는 실패하면 -1을 돌려준다 (raw/posix-bind.md:58). 원인은 `EADDRINUSE`, `EADDRNOTAVAIL` 등이다 (raw/posix-bind.md:66-72). 메시지에 errno를 쓰는 문제는 [[analysis/subject-vs-evaluation]] 1.8절.

## 시그널 처리

시그널 관련 허용 함수는 `signal`과 `kill`이다 (raw/subject.md:113). POSIX가 정한 기본 동작과 과제에서의 처리:

| 시그널 | 기본 동작 | 과제에서 생기는 상황 | 처리 | 근거 |
|---|---|---|---|---|
| `SIGPIPE` | **비정상 종료** | 읽는 쪽이 없는 pipe에 씀 (CGI가 입력을 다 읽지 않고 종료), 연결이 끊긴 소켓에 `send` | `signal(SIGPIPE, SIG_IGN)`으로 무시 | raw/posix-signal-h.md:192-196, raw/posix-signal-h.md:296-298, raw/posix-signal-h.md:42-44 |
| `SIGCHLD` | 무시 | CGI 자식 종료 | 기본 동작으로 둔다. **`SIG_IGN`으로 바꾸면 안 된다**: 자식의 종료 상태를 받을 수 없게 된다 [XSI] (raw/posix-waitpid.md:323). 회수는 [[concepts/cgi]] "자식 회수" | raw/posix-signal-h.md:146-154 |
| `SIGINT`, `SIGTERM` | 비정상 종료 | 평가자가 Ctrl-C로 서버를 끔 | 아래 "정리 후 종료" | raw/posix-signal-h.md:180-184, raw/posix-signal-h.md:216-220 |

> [!danger] SIGPIPE
> 아무 처리도 하지 않으면 읽는 쪽이 없는 pipe에 쓰는 순간 서버 프로세스가 종료된다 (raw/posix-signal-h.md:192-196, raw/posix-signal-h.md:296-298). 디펜스 중 예기치 않은 종료는 0점이다 (raw/evaluation-sheet-en.md:24).
> 소켓도 마찬가지다. 연결이 끊긴 SOCK_STREAM 소켓에 `send`하면 `EPIPE`로 실패하고, `MSG_NOSIGNAL`이 없으면 `SIGPIPE`가 발생한다 (raw/posix-send.md:118-120). `EPIPE` 실패는 시그널과 별개로 일어나므로, `SIGPIPE`를 무시하면 프로세스는 살고 `send`는 -1을 돌려준다 (**판단**, 120줄에서 끌어낸 추론).
>
> 대안: `send`의 flags에 `MSG_NOSIGNAL`을 주면 `SIGPIPE` 없이 `EPIPE`만 돌려준다 (raw/posix-send.md:58-60). macOS가 이 플래그를 지원하는지는 **미확인**이다. 또 pipe(CGI)에 쓰는 `write`에는 flags가 없어 이 방법을 쓸 수 없다. 그래서 허용 함수 `signal`로 `SIGPIPE`를 무시하는 쪽을 기본으로 한다.

### SIGINT·SIGTERM과 누수 검사

- 평가표는 실행이 끝나기 전에 heap 할당을 모두 해제하라고 한다 (raw/evaluation-sheet-en.md:25).
- `SIGINT`의 기본 동작은 비정상 종료라서 (raw/posix-signal-h.md:180-184) 해제 코드가 실행되지 않는다.
- valgrind(Ubuntu 24.04, 3.22.0)로 실측했다 → [[sources/valgrind-observed-sigint]]:
  - 기본 동작으로 끝나면 definitely lost는 0이지만, 해제하지 않은 메모리가 모두 still reachable로 보고된다 (raw/valgrind-observed-sigint.md:111-138).
  - 핸들러를 두고도 해제 없이 `main`에서 반환하면 definitely lost가 된다 (raw/valgrind-observed-sigint.md:157-163).
  - 모두 해제하고 끝낸 경우만 "All heap blocks were freed -- no leaks are possible"이 나왔다 (raw/valgrind-observed-sigint.md:212-215).
  - still reachable을 누수로 볼지는 평가자 판단이다. `leaks`·`e_fence`의 보고 방식은 **미확인**이다 (확인: 각 도구로 같은 프로그램 실행).
- 판단: 시그널 핸들러에서는 종료 플래그만 세우고, 메인 루프가 플래그를 보고 연결·CGI 자식·메모리를 정리한 뒤 종료한다.
- CGI 자식은 서버가 끝나도 직접 끝나지는 않고(일부 경우 `SIGHUP`으로 간접 종료) 시스템 프로세스에 입양된다 (raw/posix-exit.md:70-72). 그래서 종료할 때 실행 중인 CGI를 `kill`로 끝내고 `waitpid`로 회수해야 한다. 그러지 않으면 무한 루프 스크립트가 서버가 꺼진 뒤에도 계속 돌 수 있다. `poll()` 대기 중 핸들러를 둔 시그널을 잡으면 `poll()`이 -1로 돌아온다 (raw/posix-poll.md:114, raw/posix-poll.md:126-128). 이때도 errno를 보지 않고 플래그만 확인하면 된다 → [[analysis/subject-vs-evaluation]] 1.8절.

## 관련

- [[concepts/io-multiplexing]], [[concepts/testing]], [[concepts/cgi]]
- [[concepts/security]] — 길이 공격·느린 클라이언트도 크래시·hang 원인이 된다
