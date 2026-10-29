---
title: POSIX errno — 실패한 함수가 남기는 오류 번호, 반환값이 실패를 알릴 때만 의미 있음
type: source
sources: [raw/posix-errno.md, raw/subject.md]
updated: 2026-10-29
---

# POSIX errno

원본: `raw/posix-errno.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/errno.html>을 2026-10-29에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-errno.md:1-3). 원본 HTML은 `raw/posix-errno.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-errno.md:5-7).

> [!note] 변환 검증
> 2026-10-29 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음, 구조 차이 없음.

## 과제와 관련된 부분

과제는 읽기·쓰기 뒤에 errno를 보고 서버 동작을 바꾸는 것을 금지한다 (raw/subject.md:133). 서버는 시작할 때 listen 소켓을 열지 못한 이유를 출력하는 곳에서만 errno를 읽는다 (`webserv/src/core/Listener.cpp:58`). 기초 설명은 [[lessons/02a-unix-system-calls]].

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (23-25) | `errno`는 오류 번호를 담는 `int` 값. 함수가 설정한다고 한 경우에만 정의되고, 반환값이 유효하다고 알릴 때만 봐야 한다 | [[lessons/02a-unix-system-calls]] |
| DESCRIPTION (29) | 값의 이름(`EAGAIN` 등)은 각 함수 페이지의 ERRORS에 있다 | 각 `sources/posix-*` |
| APPLICATION USAGE (55) | 오류를 판단하려면 호출 전에 0으로 두고 다음 호출 전에 본다 | — |

## 핵심

- `errno`는 매크로가 펼쳐지는 lvalue로, 많은 함수가 오류 값을 돌려주는 데 쓴다 (raw/posix-errno.md:23).
- 형은 `int`이고 `<errno.h>`에 정의된다. 처음 스레드에서 프로그램 시작 때는 0이고, 그 뒤로는 설정한다고 명시한 함수를 부른 뒤에만 정의된다. 다음 함수 호출이 바꿀 때까지 유지된다 (raw/posix-errno.md:25).
- errno의 값은 함수의 반환값이 그것이 유효하다고 알릴 때만 봐야 한다 (raw/posix-errno.md:25). 성공한 호출 뒤의 errno는 그 함수가 바꾸지 않는다고 명시하지 않은 한 정해지지 않았다(unspecified) (raw/posix-errno.md:25).
- 어떤 함수도 errno를 0으로 설정하지 않는다 (raw/posix-errno.md:25).
- 값의 이름은 각 함수 페이지의 ERRORS 절에 있다 (raw/posix-errno.md:29).

## 과제 적용 (판단)

- 과제 규칙 (raw/subject.md:133) 때문에 서버는 `recv`·`send`·`read`·`write`의 -1을 "실패"로만 보고, `EAGAIN`인지 `ECONNRESET`인지 가리지 않는다. 준비된 fd에만 한 번 읽거나 써서 `EAGAIN`을 구분할 필요가 없게 했다 → [[lessons/04-poll]], [[lessons/15-defense-qa]] Q7.
- `accept`·`fork`·`pipe` 같은 다른 함수 뒤에 errno를 봐도 되는지는 이 위키의 열린 질문이다. 서버는 이 경우에도 원인을 가리지 않는다 → [[analysis/subject-vs-evaluation]] 1.8절.

## 관련

- [[sources/posix-read]], [[sources/posix-write]], [[sources/posix-recv]], [[sources/posix-send]], [[lessons/02a-unix-system-calls]]
