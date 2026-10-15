---
title: siege 소켓 코드 (src/sock.c)
type: source
sources: [raw/siege-sock.c, raw/siegerc.in, raw/siege.pod, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# siege 소켓 코드 (src/sock.c)

원본: `raw/siege-sock.c`. <https://raw.githubusercontent.com/JoeDog/siege/master/src/sock.c>을 2026-10-15에 받아 그대로 저장했다. C 소스라 변환하지 않았다.

- 이 파일을 마지막으로 바꾼 커밋: `e2a6bc94c0c7ae44fa775f9f74eac5311cefd987` (2023-12-06). (받을 때 GitHub에서 본 값이고 raw 파일에는 없다.)
- `master` 브랜치 파일이다. Ubuntu 22.04 apt 패키지인 siege 4.0.7의 태그 파일과는 이름 해석 부분(97~236줄)의 매크로·메시지·주석만 다르고, 아래 표의 준비 검사·`timeout`·`socket_read` 코드는 같다 (`new_socket` 안에서는 236줄의 `#if` 조건만 다름) → [[sources/ubuntu2204-observed-tools]]. 평가 PC에 설치된 버전은 **미확인**이다 (평가 때 `siege -V`).
- 받은 목적: 설정 `timeout`("socket connection timeouts", raw/siegerc.in:353-354)이 응답을 기다릴 때도 걸리는지 확인하는 것 → [[source-wishlist]] 6절.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| `new_socket` 연결 단계 (234-297) | non-blocking `connect` 뒤 준비 검사, 실패하면 "read check timed out" 후 닫음 | [[concepts/testing]] |
| `__socket_check` (304-316) | fd 번호가 `FD_SETSIZE` 이상이면 `poll`, 아니면 `select`로 검사 | [[concepts/testing]] |
| `__socket_poll` (319-350) | 대기 시간 `timeout`×1000ms, 0이면 15초 | [[concepts/testing]] |
| `__socket_select` (353-390) | 대기 시간 `timeout`초, 0이면 30초. 읽기·쓰기 집합을 함께 검사 | [[concepts/testing]] |
| `socket_read` (578-659) | 일반 HTTP는 `read()` 직전마다 준비 검사, 실패하면 -1 | [[concepts/testing]], [[concepts/resilience]] |

다루지 않는 부분: 이름 해석(`getaddrinfo` 등), SSL, 프록시, 쓰기 함수.

## 원문으로 확인한 것

- `timeout` 값(`my.timeout`)은 준비 검사의 대기 시간으로 쓰인다. `select` 경로는 `timeout`초(0이면 30초) (raw/siege-sock.c:360-362), `poll` 경로는 `timeout`×1000ms(0이면 15초) (raw/siege-sock.c:323).
- `select`와 `poll` 중 무엇을 쓸지는 fd 번호로 정한다. `FD_SETSIZE` 이상일 때만 `poll`이다 (raw/siege-sock.c:304-316).
- 연결 단계: `connect` 뒤 준비 검사가 실패하면 "read check timed out" 경고를 남기고 소켓을 닫고 -1을 돌려준다 (raw/siege-sock.c:271-275).
- 응답 읽기 단계: 일반 HTTP의 `socket_read`는 `read()` 직전마다 준비 검사를 하고, 실패하면 같은 경고를 남기고 -1을 돌려준다 (raw/siege-sock.c:611-626).
- 따라서 `timeout`은 응답 **전체 시간**이 아니라, 읽기를 한 번 하기 전의 **대기마다** 걸린다.

## 코드를 읽고 내린 판단

- **(판단)** `select` 경로는 같은 fd를 읽기 집합과 쓰기 집합에 모두 넣는다 (raw/siege-sock.c:370-374). 쓰기 가능하기만 해도 돌아오므로, 응답을 기다리는 동안에는 이 검사가 대기 없이 통과할 수 있다. 그러면 응답 대기에 실제로 `timeout`이 걸린다고 보기 어렵다.
- **(판단)** 연결이 끝나면 `__socket_block(C->sock, TRUE)`를 부르고 (raw/siege-sock.c:290), 이 함수는 `TRUE`일 때 `O_NDELAY`만 지운다 (raw/siege-sock.c:485-486). Linux에서 `O_NDELAY`가 `O_NONBLOCK`과 같은 값이면 소켓이 blocking이 되어, 응답이 오지 않을 때 `read()`(raw/siege-sock.c:626)가 그대로 막혀 있을 수 있다. glibc 헤더에서 `O_NDELAY`는 `O_NONBLOCK`으로 정의돼 있었다 (aarch64 헤더로 확인) → [[sources/siege-observed-ubuntu2204]].
- **(판단)** `poll` 경로는 감시 fd를 `C->sock + 1`로 넣는다 (raw/siege-sock.c:326). 다만 이 경로는 fd 번호가 `FD_SETSIZE` 이상일 때만 쓰인다 (raw/siege-sock.c:308-309).

## 이 문서로 확인하지 못한 것

- 다른 소스 파일(`client.c` 등)에 별도 타이머나 `SO_RCVTIMEO` 설정이 있는지는 소스로 확인하지 않았다. 실측에서는 응답하지 않는 서버에 대해 siege 4.0.7이 `timeout` 30초·5초 설정 모두에서 150초 동안 끝나지 않았다 → [[sources/siege-observed-ubuntu2204]]. 위 판단과 맞는 결과다.

## 과제 적용 (판단)

- siege의 `timeout`이 느린 응답을 끊어 준다고 기대하지 않는다. 서버가 응답을 끝까지 보내고 연결을 정리하는 것이 Availability(raw/siege.pod:373-378)와 "hanging connection 없음"(raw/evaluation-sheet-en.md:116)의 핵심이라는 기존 판단은 그대로다 → [[concepts/testing]], [[concepts/resilience]].
