---
title: "레슨 4: 기다리지 않는 서버와 poll"
type: lesson
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/posix-poll.md]
updated: 2026-10-29
---

# 레슨 4: 기다리지 않는 서버와 poll

이전: [[lessons/03a-urls-and-http-details]] · 다음: [[lessons/04a-cpp98-basics]]

> [!example] 쉬운 예
> 선생님 한 명이 학생 30명의 질문을 받는다고 하자.
> - **나쁜 방법**: 1번 학생 책상 앞에 서서 질문이 생길 때까지 기다리기. 1번이 조용하면 2~30번은 손을 들어도 아무도 못 본다.
> - **좋은 방법(poll)**: 교탁에서 "질문 있는 사람 손 들어!" 하고 교실을 한 번 둘러본다. 손 든 학생에게만 가서 질문 하나를 듣고, 다시 교탁으로 돌아와 둘러본다.
>
> `poll()`이 "손 든 사람 둘러보기"다. 손을 든 학생(준비된 fd)에게만 말을 건다(read/write).

## 4.1 과제의 규칙

- 모든 클라이언트 I/O(listen 포함)에 `poll()`을 **하나만** 쓴다 (raw/subject.md:130).
- `poll()`은 읽기와 쓰기를 **동시에** 감시한다 (raw/subject.md:131).
- `poll()`을 거치지 않고 read/write하지 않는다 (raw/subject.md:132).
- read/write 뒤에 `errno`를 보고 동작을 바꾸지 않는다 (raw/subject.md:133).
- 일반 디스크 파일은 예외다 (raw/subject.md:134).

> [!danger] 0점 조건
> 준비 알림 없이 소켓·pipe를 읽거나 쓰면 0점이다 (raw/subject.md:136). poll이 메인 루프에 없거나 읽기·쓰기를 함께 감시하지 않으면 평가가 그 자리에서 끝난다 (raw/evaluation-sheet-en.md:53). read/write 뒤 errno 검사도 0점·종료다 (raw/evaluation-sheet-en.md:57).

## 4.2 poll이 알려 주는 것

fd마다 기다리는 것(events)을 적어 넘기고, 일어난 일(revents)을 받는다.

| 비트 | 뜻 | 우리 처리 |
|---|---|---|
| `POLLIN` | 읽을 것이 있다 (listen 소켓이면 새 손님) | `recv`/`accept`/`read` 한 번 |
| `POLLOUT` | 지금 쓰면 막히지 않는다 | `send`/`write` 한 번 |
| `POLLHUP` | 상대가 끊었다 | 읽던 중이면 한 번 더 읽어 0(EOF) 확인, 아니면 닫기 |
| `POLLERR`, `POLLNVAL` | 오류, 잘못된 fd | 닫기 |

처리표 근거: [[concepts/io-multiplexing]] "revents 처리". 코드: `src/http/Connection.cpp:76-93`.

> [!tip] 왜 준비 한 번에 I/O 한 번만?
> 평가표는 EAGAIN이 나올 때까지 반복해서 읽어도 된다고 한다 (raw/evaluation-sheet-en.md:54). 하지만 EAGAIN을 알려면 errno를 봐야 하고, errno 검사는 금지다. 둘이 부딪히므로 **준비 알림 한 번에 recv/send 한 번**만 한다. 그러면 errno를 볼 일이 없다 **(판단)** → [[concepts/io-multiplexing]] "EAGAIN 반복 모순".

> [!tip] 왜 POLLOUT은 보낼 게 있을 때만?
> 소켓은 거의 항상 "쓸 수 있음"이다. 보낼 것도 없는데 `POLLOUT`을 요청하면 `poll()`이 매번 바로 돌아와 CPU를 다 쓴다(busy waiting). POSIX도 상태를 바꾸지 않고 poll을 반복하면 busy waiting이 된다고 경고한다 (raw/posix-poll.md:175). 그래서 `Connection::wantedEvents()`는 응답을 보내는 중(`WRITE`)일 때만 `POLLOUT`을 돌려준다 (`src/http/Connection.cpp:69-74`). 대기 연결 10개가 2초 동안 CPU 0.2초 미만을 쓰는지 테스트한다 ([[analysis/test-plan]] N-19).

> [!example] 쉬운 예
> 할 말이 없는데 계속 손을 들면 선생님은 계속 와서 "뭐니?" 하고 물어야 한다. 할 말이 생겼을 때만 손을 든다.

> [!question]- 확인 문제: 정적 파일을 읽을 때는 왜 poll이 필요 없나?
> 과제가 일반 디스크 파일은 readiness 없이 읽고 써도 된다고 명시한다 (raw/subject.md:134). 대신 루프를 오래 멈추면 안 되므로 (raw/evaluation-sheet-en.md:59) 1MB보다 큰 파일은 64KB씩 나눠 읽어 보낸다 ([[lessons/11-response]]).
