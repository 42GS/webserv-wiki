---
title: POSIX poll()
type: source
sources: [raw/posix-poll.md, raw/subject.md]
updated: 2026-10-15
---

# POSIX poll()

원본: `raw/posix-poll.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/poll.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-poll.md:1-4). 원본 HTML은 `raw/posix-poll.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024, The Open Group Base Specifications Issue 8) 표준 문서다 (raw/posix-poll.md:6).

> [!note] 변환 방법
> opengroup 페이지에는 `div#content`가 없어서, 위쪽 내비게이션 다음부터 "return to top of page" 직전까지를 본문으로 잘라 변환했다. 변환·검증 도구는 [[sources/nginx-core-module]]과 같다. 공백을 뺀 11,504자가 같았고, 단어 단위 차이 78건은 모두 태그 경계에서 단어가 갈라진 것이었다.
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: `<p>`가 든 목록 항목(raw/posix-poll.md:34, 36, 104, 106) 글머리표 없음.

## 과제와 관련된 절

| 절 (시작 줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (28) | 이벤트 플래그, 준비 상태의 의미, 타임아웃, 지원하는 fd 종류 | [[concepts/io-multiplexing]] |
| RETURN VALUE (112) | 양수·0·-1 | [[concepts/io-multiplexing]] |
| ERRORS (118) | `EAGAIN`, `EINTR`, `EINVAL` | [[analysis/subject-vs-evaluation]] |
| APPLICATION USAGE (150) | 준비 상태의 정확한 의미, `O_NONBLOCK` 권장, busy waiting | [[concepts/io-multiplexing]] |
| RATIONALE (179) | FIFO의 `POLLHUP` | [[concepts/cgi]] |

함께 정의된 `ppoll()`은 허용 함수 목록(raw/subject.md:113)에 없으므로 다루지 않는다.

## 핵심

- `POLLHUP`·`POLLERR`·`POLLNVAL`은 요청하지 않아도 조건이 맞으면 `revents`에 설정된다 (raw/posix-poll.md:86).
- `POLLHUP`은 `POLLIN`과 동시에 올 수 있다 (raw/posix-poll.md:74).
- 쓰기 가능은 상태를 확인한 시점에 1바이트 쓰기가 막히지 않았을 것이라는 뜻일 뿐이다 (raw/posix-poll.md:171).
- 상태를 바꾸지 않고 다시 호출하면 busy waiting이 된다 (raw/posix-poll.md:175).
