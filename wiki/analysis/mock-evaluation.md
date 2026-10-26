---
title: 모의 평가 (2026-10-25)
type: analysis
sources: [raw/evaluation-sheet-en.md, raw/subject.md, raw/rfc9112.txt, raw/rfc3875.txt, raw/nginx-core-module.md]
updated: 2026-10-27
---

# 모의 평가 (2026-10-25)

평가표 영어 원문([[sources/evaluation-sheet-en]])의 순서대로 평가자가 하는 일을 따라 해 본 결과다. 대상은 webserv `60401ad`다. 요구사항별 테스트는 [[analysis/test-plan]]에 있고, 이 페이지는 처음부터 끝까지 한 번에 따라간 기록과 디펜스 메모다.

## 환경

- Ubuntu 22.04.5 컨테이너(`webserv-dev` 이미지에 `git`·`curl`·`telnet`·`nc`·`ss`·electric-fence를 더함)를 썼다. root가 아닌 일반 사용자로 실행했다.
- 빈 폴더에 `git clone`한 사본으로 했다 (raw/evaluation-sheet-en.md:19).
- 컨테이너의 커널은 OrbStack VM 것이라 평가 PC와 다르다 → [[sources/ubuntu2204-observed-tools]].
- 브라우저 항목은 하지 않았다. 2026-10-18에 사용자가 브라우저로 확인한 기록이 있다 ([[analysis/test-plan]] R-18·F-14).

## 결과

| 평가표 항목 | 한 일 | 결과 |
|---|---|---|
| README (raw/evaluation-sheet-en.md:35-44) | 첫 줄과 절 제목, Resources의 AI 문단을 읽음 | 통과. 첫 줄 이탤릭 정해진 문구, Description·Instructions·Resources, AI를 쓴 작업과 부분 |
| 빌드·relink (raw/evaluation-sheet-en.md:60) | `make`, 다시 `make`, 소스 하나 수정 뒤 `make`, `make re`, `clean`, `fclean` | 통과. 두 번째는 "Nothing to be done", 수정 뒤에는 그 파일과 링크만, 경고 0 |
| `-std=c++98` 없이 빌드 (raw/subject.md:49-50) | `make CXXFLAGS="-Wall -Wextra -Werror"` | **실패.** 아래 "발견한 것" 1 |
| poll·readiness·errno (raw/evaluation-sheet-en.md:53-59) | 모든 `read`·`recv`·`write`·`send` 호출을 찾아 읽음 | 통과. 아래 "디펜스 메모" |
| 서로 다른 interface·port의 사이트 (raw/evaluation-sheet-en.md:68, raw/evaluation-sheet-en.md:107) | `conf/ports.conf`로 127.0.0.1:8080·8081, 127.0.0.2:8080, 8082 | 통과. 주소마다 설정한 사이트 |
| 기본 에러 페이지와 그 수정 (raw/evaluation-sheet-en.md:69) | `/nope`, 그리고 `www/errors/404.html`을 바꾼 뒤 다시 요청 | 통과. 404와 설정한 페이지. 파일을 바꾸면 재시작 없이 바뀐 내용 |
| 본문 크기 제한 (raw/evaluation-sheet-en.md:70) | 평가표의 curl 명령 그대로 `/limit/echo.py`(상한 64바이트)에 | 통과. 62바이트는 200(받은 본문을 돌려줌), 더 길면 413 |
| 다른 디렉토리로의 route, 디렉토리 기본 파일 (raw/evaluation-sheet-en.md:71-72) | `/docs/`(alias), `/` | 통과 |
| 허용 메서드, 권한 있는·없는 DELETE (raw/evaluation-sheet-en.md:73) | `DELETE /index.html`, 업로드 뒤 `DELETE /upload/...` | 통과. 405 + `Allow: GET, HEAD`, 파일 그대로. 업로드 파일은 204 뒤 404 |
| telnet·curl로 GET·POST·DELETE, UNKNOWN, 상태 코드 (raw/evaluation-sheet-en.md:77-81) | telnet으로 요청 줄을 쳐서 보냄 | 통과. 200, 501(UNKNOWN·PUT), 400(형식 오류·Host 없음·`..`·`%2F`), 505(`HTTP/2.0`), 414, HEAD 200 본문 없음 |
| 업로드 후 다시 받기 (raw/evaluation-sheet-en.md:82) | 5MB 임의 바이트 파일 | 통과. sha256 같음. 같은 이름은 409, 10MB 상한 위는 413 |
| CGI GET·POST, 상대 경로, 에러 스크립트, 무한 루프 (raw/evaluation-sheet-en.md:88-93) | 시연 스크립트와 평가자가 만들 법한 잘못된 스크립트 9개 | 통과. 문법 오류·빈 출력·헤더 끝 없음·`abort`·헤더 없는 본문·16MB 초과는 502, 스크립트가 준 `Status: 500`은 500. 루프는 11초 뒤 504, 그동안 다른 요청은 바로 200. 서버는 계속 동작 |
| 같은 interface:port 두 사이트 (raw/evaluation-sheet-en.md:108) | `conf/same-port.conf` | 통과. `duplicate listen 127.0.0.1:8080`, 종료 코드 1 |
| 같은 포트로 webserv 하나 더 (raw/evaluation-sheet-en.md:109) | 첫 서버가 도는 동안 두 번째 실행 | 통과. `Address already in use`, 종료 코드 1, 첫 서버는 계속 200 |
| siege (raw/evaluation-sheet-en.md:114-117) | 빈 페이지에 `siege -b -c 50`을 2분, 다시 60초 | 통과. 3,721,561건과 1,854,895건 모두 availability 100%, 실패 0. RSS 1.9MB 일정, 끝난 뒤 fd 5개(표준 3 + listen 2), 서버 쪽 CLOSE_WAIT 0 |
| 누수 (raw/evaluation-sheet-en.md:25) | valgrind로 띄워 정적·404·목록·리다이렉트·업로드·삭제·CGI(정상·에러·413)를 보내고, 루프 CGI가 도는 중에 SIGINT | 통과. "All heap blocks were freed", 오류 0, 열린 fd는 표준 3개와 valgrind 기록 파일. 루프 스크립트도 남지 않음. e_fence로도 같은 요청과 siege 20초에 크래시 없음 |
| 보너스: 쿠키·세션 (raw/evaluation-sheet-en.md:126) | 쿠키 파일로 `session.py`를 세 번, 위조한 쿠키 | 통과. 방문 수 1→2→3, 모르는 식별자에는 새 쿠키 |
| 보너스: 여러 CGI (raw/evaluation-sheet-en.md:130) | `hello.php` | 통과. Python과 PHP |

## 발견한 것

1. **`-std=c++98` 없이는 빌드되지 않는다.** subject는 `c++`와 `-Wall -Wextra -Werror`로 컴파일하라고 하고, `-std=c++98`을 더해도 컴파일돼야 한다고 한다 (raw/subject.md:49-50). Ubuntu 22.04의 g++ 11.4.0은 기본이 C++17이라 `std::auto_ptr` deprecated 경고가 `-Werror`로 오류가 된다 (`src/core/Server.cpp:40`, `src/app/RequestProcessor.cpp:198`). Makefile에는 늘 `-std=c++98`이 들어가므로 평가자가 Makefile로 빌드하면 통과한다. [[analysis/test-plan]] B-03을 "부족"으로 고쳤다. 고치는 방법(예: `auto_ptr` 대신 직접 `delete`하는 `try`/`catch`)은 사용자가 정한다.
2. **저장소에 빈 페이지가 없다.** 평가표의 siege 기준은 빈 페이지다 (raw/evaluation-sheet-en.md:114). README의 siege 명령은 `/`(1,438바이트)이고, `www/`에 0바이트 파일이 없다. 위 결과는 클론 사본에 임시로 만든 `www/empty.html`로 쟀다. 평가자는 설정 파일 말고는 고치지 않아야 하므로 (raw/evaluation-sheet-en.md:24), 시연 자료에 넣어 두는 편이 낫다(**판단**).

> [!info] 처리 (2026-10-27)
> 두 가지 모두 사용자 요청으로 고쳤다: `std::auto_ptr`를 없애고 `-std=c++98` 없는 빌드 테스트를 더했다 (webserv `664692b`, [[analysis/test-plan]] B-03). `www/empty.html`을 넣고 README의 siege 명령을 바꿨다 (webserv `5ca93a2`, [[analysis/test-plan]] E-10). Ubuntu 22.04에서 단위 102개, 통합 118개(느린 테스트 포함) 통과, valgrind 누수·오류 0.

## 서버 문제가 아닌 것 (디펜스에서 물을 수 있음)

- **telnet에 `\r\n`을 파이프로 넣으면 400이다.** telnet은 입력의 CR을 `\r\0`으로 바꿔 보낸다(바이트를 잡아 확인: `\r \0 \r \n`). CR 뒤에 LF가 오지 않으므로 bare CR이고, 수신자는 그 요소를 잘못된 것으로 봐야 한다 (raw/rfc9112.txt:287-291). LF만 넣으면 telnet이 `\r\n`으로 보내 정상이었다(바이트로 확인). 사람이 telnet에서 Enter를 칠 때도 이 경우다(**판단**). 시연할 때는 telnet에 직접 쳐서 보낸다.
- **`/docs`(끝 슬래시 없음)는 404다.** `location /docs/`에 맞지 않아 `location /`가 처리하고, `www/docs`가 없다. NGINX가 끝 슬래시를 붙여 301로 보내는 것은 `proxy_pass` 등으로 처리할 때뿐이다 (raw/nginx-core-module.md:1115). 정적 파일이면 NGINX도 같다고 본다(**판단**, 실측하지 않음).
- **자식을 남기고 끝나는 CGI 스크립트는 10초 뒤 504다.** 스크립트는 응답을 다 출력했지만 `fork`한 손자가 출력 pipe를 쥐고 있어 EOF가 오지 않는다. 서버는 EOF까지 읽어야 한다 (raw/rfc3875.txt:1521-1524). 시간 상한이 있으므로 hang은 아니다.
- 컨테이너에서는 끝난 서버와 손자 프로세스가 zombie로 남았다. 컨테이너의 PID 1(`sleep infinity`)이 회수하지 않아서다. 서버는 "shutting down"을 출력하고 정상 종료했다.

## 디펜스 메모: poll에서 클라이언트 I/O까지 (평가표 54줄)

코드 위치는 webserv `60401ad` 기준이다 (2026-10-25 직접 읽음).

- 메인 루프: `src/main.cpp:86` `loop.run(server)` → `EventLoop::run`이 바퀴마다 `pollOnce` → `src/core/EventLoop.cpp:48`의 `poll` 하나. 모든 fd(listen 소켓, 클라이언트 소켓, CGI pipe)가 한 배열에 들어가고, 각 handler의 `wantedEvents()`로 읽기·쓰기를 함께 감시한다.
- accept: `src/core/Listener.cpp:67` `POLLIN` 확인 → `:72` `accept`. 실패하면 listener를 잠시 멈춘다.
- 클라이언트: `src/http/Connection.cpp:45` `onEvent` → `POLLIN`·`POLLHUP`이면 `:127` `recv`, `POLLOUT`이면 `:168` `send`. 준비 한 번에 I/O 한 번.
- 반환값: `recv`·`send`가 0이나 -1이면 errno를 보지 않고 연결을 닫는다 (`:130`, `:169`). CGI pipe의 `write`·`read`(`src/cgi/CgiPipes.cpp:31`, `:70`), 파일 읽기·쓰기, 시계 파일 쓰기도 0과 -1을 모두 처리한다.
- errno는 `src/core/Listener.cpp:58` 한 곳에서만 읽는다. 시작할 때 listen 소켓을 열지 못한 이유를 출력할 때다.
- 일반 파일은 `poll` 없이 읽고 쓴다 (raw/subject.md:134). 큰 정적 파일은 `ResponseStream`이 64KB씩 나눠 읽어 루프를 멈추지 않는다 ([[analysis/design]] 8절).
