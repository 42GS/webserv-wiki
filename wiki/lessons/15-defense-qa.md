---
title: "레슨 15: 평가 예상 질문"
type: lesson
sources: [raw/evaluation-sheet-en.md, raw/os-observed-pipe-poll.md, raw/subject.md, raw/rfc3875.txt]
updated: 2026-10-29
---

# 레슨 15: 평가 예상 질문

이전: [[lessons/14-resilience]] · 다음: [[lessons/16-glossary]]

평가표 "Check the code and ask questions"(raw/evaluation-sheet-en.md:46-61) 순서를 따랐다. 눌러서 답을 본다.

> [!question]- Q1. HTTP 서버의 기본을 설명해 주세요.
> 클라이언트가 TCP로 접속해 요청 줄·헤더·본문으로 된 요청을 보내면, 서버는 그것을 해석해 자원을 찾고 상태 줄·헤더·본문으로 된 응답을 돌려준다. 우리 서버는 설정 파일의 server·location 규칙에 따라 정적 파일, 디렉토리 목록, 리다이렉트, 업로드, 삭제, CGI 중 하나로 처리한다 ([[lessons/03-http-basics]], [[lessons/10-routing]]).

> [!question]- Q2. 어떤 이벤트 메커니즘을 쓰고, 왜요?
> `poll()`이다 ([[analysis/design-decisions]] 1). POSIX 표준이라 개발 환경(macOS)과 평가 환경(Ubuntu)에서 같은 코드가 돈다. 두 OS에서 직접 실측했다 (raw/os-observed-pipe-poll.md:171, raw/os-observed-pipe-poll.md:186). 디펜스에서 설명할 메커니즘도 하나뿐이다. "epoll은 Linux 전용, kqueue는 BSD·macOS 전용"이라는 말은 흔하지만 OS 문서로 확인하지 않아 근거로 쓰지 않는다 (**미확인**, [[concepts/io-multiplexing]]).

> [!question]- Q3. poll은 어떻게 동작하나요?
> fd 배열과 fd마다 기다릴 이벤트(POLLIN, POLLOUT)를 넘기면, 하나라도 준비되거나 시간이 다 될 때까지 기다렸다가 fd마다 일어난 일(revents)을 채워 돌려준다. 1초 타임아웃으로 불러, 아무 일이 없어도 1초마다 타임아웃을 검사한다 ([[lessons/04-poll]], [[lessons/07-event-loop]]).

> [!question]- Q4. poll을 하나만 쓰나요? accept와 클라이언트 읽기·쓰기는?
> 하나만 쓴다 (`src/core/EventLoop.cpp:48`). listen 소켓, 클라이언트 소켓, CGI pipe가 모두 `IoHandler`라 한 배열에 들어간다. listen 소켓이 POLLIN이면 `accept` 한 번 (`src/core/Listener.cpp:69-74`), 클라이언트가 POLLIN이면 `recv` 한 번 (`src/http/Connection.cpp:164`), POLLOUT이면 `send` 한 번 (`:205`).

> [!question]- Q5. poll에서 클라이언트 I/O까지 코드 경로를 보여 주세요.
> `src/main.cpp:92` `loop.run(server)` → `EventLoop::run` (`src/core/EventLoop.cpp:24`) → `pollOnce`의 `poll` (`:48`) → `dispatch` (`:57-70`) → `Connection::onEvent` (`src/http/Connection.cpp:76`) → POLLIN·POLLHUP이면 `receiveOnce`의 `recv` (`:164`), POLLOUT이면 `sendOnce`의 `send` (`:205`).

> [!question]- Q6. read/recv/write/send가 에러를 내면 클라이언트를 지우나요? 0과 -1을 모두 처리하나요?
> 그렇다. `recv`·`send`가 0이나 -1이면 `changeState(CLOSED)`로 가고 (`src/http/Connection.cpp:167`, `:206`), 그 바퀴 끝에 `Server::afterIteration`이 연결을 지운다. CGI pipe (`src/cgi/CgiPipes.cpp:31`, `:70`), 파일 읽기·쓰기, 시계 쓰기도 0과 -1을 모두 처리한다.

> [!question]- Q7. errno를 쓰나요?
> read/write/recv/send 뒤에는 읽지 않는다. `src/core/Listener.cpp:60` 한 곳에서만 읽는데, 시작할 때 listen 소켓을 열지 못한 이유를 출력하기 위해서다. poll이 -1이어도 errno를 보지 않는다. 준비 한 번에 I/O 한 번만 해서 EAGAIN을 구분할 필요가 없다 ([[lessons/04-poll]]).

> [!question]- Q8. 디스크 파일을 동기로 읽어도 루프가 멈추지 않나요?
> 설정 파일은 시작할 때만 읽는다. 정적 파일은 1MB 이하만 통째로 읽고, 더 크면 POLLOUT마다 64KB씩 읽어 보낸다. 시계 파일은 바퀴마다 1바이트다. 업로드는 본문을 다 받은 뒤 한 번에 쓴다 ([[lessons/11-response]]).

> [!question]- Q9. 같은 포트로 webserv를 두 개 띄우면?
> 두 번째는 `bind`가 실패해 "cannot listen on 127.0.0.1:8080: Address already in use"를 출력하고 종료 코드 1로 끝난다. 첫 번째는 계속 응답한다 (raw/evaluation-sheet-en.md:109, [[analysis/mock-evaluation]]).

> [!question]- Q10. 같은 interface:port에 사이트를 두 개 설정하면?
> virtual host를 구현하지 않았으므로 설정 오류로 시작하지 않는다 (`conf/same-port.conf`, [[analysis/design-decisions]] 4). 평가표는 이 방식과 virtual host 구현 모두 맞다고 한다 (raw/evaluation-sheet-en.md:108).

> [!question]- Q11. 쿠키·세션은 서버의 기능인가요?
> 서버는 `Cookie`를 `HTTP_COOKIE`로 CGI에 넘기고, CGI가 낸 `Set-Cookie` 여러 줄을 합치지 않고 응답에 옮긴다. 세션 식별자 발급과 저장은 예제 스크립트가 한다. subject가 "간단한 예제 제공"으로 요구하기 때문이다 (raw/subject.md:215, [[analysis/design-decisions]] 8). 평가자가 "웹 서버의 세션 시스템"(raw/evaluation-sheet-en.md:126)을 어떻게 볼지는 설명이 필요하다.

> [!question]- Q12. 허용 함수에 없는 std::exit, std::remove를 왜 썼나요?
> subject 51줄이 C 함수를 써도 되고 C++ 버전을 쓰라고 하기 때문이다 (raw/subject.md:51). 시스템 호출은 목록 안의 것만 쓴다. 시간은 목록 안의 함수(open·write·close·stat)로 얻는다 ([[lessons/05-startup]]). 평가자가 111~113줄 목록만 허용으로 읽을 수 있어 설명이 필요한 지점이다 ([[analysis/subject-vs-evaluation]] 1.4).

> [!question]- Q13. Ubuntu에서도 fcntl을 쓰는 이유는?
> non-blocking으로 만들려면 `fcntl(fd, F_SETFL, O_NONBLOCK)`이 필요하고, 허용된 플래그(`F_SETFL`, `O_NONBLOCK`)만 쓴다 (raw/subject.md:155-157). 그 절의 제목이 "For macOS only"라 평가자 해석은 확인이 필요하다 ([[overview]] 열린 질문). `FD_CLOEXEC`(`F_SETFD`)는 쓰지 않고 자식에서 fd를 직접 닫는다 ([[lessons/13-cgi]]).

> [!question]- Q14. 연결이 영원히 매달리지 않게 하는 방법은?
> 상태마다 시간 제한이 있다: 첫 바이트 15초, 머리 30초(첫 바이트부터), 본문·전송 무진행 30초, DRAIN 1초/5초, CGI 10초. 머리는 진행이 있어도 연장하지 않아 1바이트씩 보내는 공격을 막는다 ([[lessons/08-connection]]).

> [!question]- Q15. 로그는 남기나요? 어디에, 왜 그렇게요?
> `logs/access.log`(응답마다 한 줄)와 `logs/error.log`(시작·종료, CGI 실패·시간 초과, 끝나지 않은 요청, `accept` 실패)에 남긴다. stderr가 아니라 일반 파일에 쓰는 이유는, 일반 디스크 파일만 `poll()` 없이 읽고 써도 되기 때문이다 (raw/subject.md:134). stderr는 pipe일 수 있다 **(판단)**. 자세히: [[lessons/14-resilience]] 14.4, [[analysis/design-decisions]] 19.

> [!question]- Q16. CGI에 요청 헤더를 다 넘기나요? 위험한 것은 없나요?
> `HTTP_*`로 넘기되 네 종류는 뺀다. 인증 정보인 `Authorization`, 다른 변수로 넘기는 `Content-Length`·`Content-Type` (SHOULD, raw/rfc3875.txt:1052-1055), 스크립트의 바깥 요청을 공격자 프록시로 돌릴 수 있는 `Proxy`(httpoxy), `-` 헤더와 같은 변수가 되는 `_` 이름 헤더다. 반대로 스크립트가 낸 연결용 헤더(`Connection`, `Keep-Alive`, `Transfer-Encoding`, `Upgrade` 등)는 응답에 옮기지 않는다 ([[lessons/13-cgi]] 13.2·13.5).

> [!question]- Q17. 부하를 얼마나 견디나요?
> 평가표는 처리량이 아니라 availability 99.5% 초과, 메모리가 끝없이 늘지 않음, 매달린 연결 없음을 본다 (raw/evaluation-sheet-en.md:113-118). Ubuntu 컨테이너에서 `siege -b -c 50 -t 60S` 빈 페이지: 166만 건, availability 100%, 최장 0.04초, RSS 3.2MB → 2.3MB, fd 수 변화 없음 (2026-10-29, webserv `13982df`). keep-alive를 지원하고, 1MB가 넘는 파일은 64KB씩 나눠 보내 큰 파일도 메모리를 거의 쓰지 않는다. 다른 구현과의 실측 비교는 [[log]] 2026-10-29 항목.

> [!info] 모의 평가에서 찾아 고친 두 가지 (webserv `664692b`, `5ca93a2`)
> 1. `-std=c++98` 없이 `c++ -Wall -Wextra -Werror`로 빌드하면 `std::auto_ptr` deprecated 경고가 오류가 되던 것을 고쳤다. `std::auto_ptr`를 없애고 실패 경로에서 직접 지운다. subject는 이 플래그로 컴파일하고 `-std=c++98`을 더해도 빌드되라고 한다 (raw/subject.md:49-50). 이 빌드를 시험하는 테스트가 있다 ([[analysis/test-plan]] B-03).
> 2. 평가표의 siege 기준인 빈 페이지(raw/evaluation-sheet-en.md:114)로 `www/empty.html`(0바이트)을 넣었다. README의 siege 명령은 `siege -b -c 50 -t 1M http://127.0.0.1:8080/empty.html`이다 ([[analysis/test-plan]] E-10).
