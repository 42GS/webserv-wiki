---
title: 테스트 계획
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/nginx-core-module.md, raw/macos-observed-sigpipe-leaks.md, raw/posix-poll.md, raw/design-checks-observed.md, raw/posix-recv.md, raw/rfc9112.txt, raw/rfc9110.txt, raw/rfc6585.txt, raw/rfc1945.txt, raw/rfc3986.txt, raw/rfc2046.txt, raw/rfc7578.txt, raw/rfc3875.txt, raw/rfc6265.txt, raw/posix-exit.md, raw/posix-fcntl.md, raw/os-observed-pipe-poll.md, raw/efence-observed-ubuntu2204.md, raw/ubuntu2204-observed-nofile.md]
updated: 2026-10-29
---

# 테스트 계획

요구사항을 한 줄에 하나씩 적고, 무엇으로 어떻게 확인하는지 정한다. 테스트는 이 표에서 나온다. 표에 없는 테스트는 왜 있는지 설명할 수 있어야 하고, 테스트가 없는 줄은 빈칸으로 드러난다.
구현 단계는 [[analysis/implementation-plan]], 설계는 [[analysis/design]], 사용자 결정은 [[analysis/design-decisions]]에 있다.

## 진행 방식

- 단계를 시작할 때 그 단계의 줄을 먼저 채우고, 테스트를 쓴 뒤 구현한다. 0~9단계 모두 채웠다(2026-10-18).
- 테스트를 새로 쓰거나 대응시키면, 코드를 일부러 틀리게 바꿔 그 테스트가 실패하는지 한 번 확인한다. 실패하지 않는 테스트는 아무것도 보장하지 않는다.
- 평가표는 채점에 쓰는 스크립트(테스트·자동화)를 평가자와 함께 검토하라고 한다 (raw/evaluation-sheet-en.md:21). 시연에 스크립트를 쓸 수 있으므로 읽기 쉽게 쓴다 (**판단**).

## 테스트 수준

| 수준 | 무엇 | 실행 |
|---|---|---|
| U | 단위 테스트 (`tests/unit/`, C++98) | `make test` |
| I | 통합 테스트: 서버를 띄우고 소켓으로 요청 (`tests/integration/`, Python). subject는 한 프로그램으로만 시험하지 말고 Python 등으로 테스트를 쓰라고 한다 (raw/subject.md:190) | macOS와 Ubuntu 22.04 컨테이너 |
| R | 코드 읽기 점검. 테스트로 증명할 수 없는 규칙(호출 순서, 금지 사항) | 해당 코드 경로를 직접 읽는다 |
| M | 수동·도구 점검 (valgrind, siege, 브라우저) | Ubuntu 22.04 컨테이너 |

근거 칸의 "설계"는 사용자와 정한 구현 규칙이다. 원문 요구가 아니라 우리 선택이므로, 바꾸면 테스트도 바꾼다.

상태 칸: **있음** = 테스트가 있고, 그 줄의 규칙을 코드에서 일부러 하나 이상 틀리게 바꿨을 때 테스트가 실패하는 것을 확인했다(2026-10-16). 줄 안의 세부 규칙마다 다 바꿔 본 것은 아니다. **확인** = 코드 읽기로 확인했다(날짜). **부족**·**없음** = 할 일. **나중** = 그 단계에서 채운다.
코드 위치(`src/...`, `tests/...`)는 `webserv/` 저장소 기준이다.

## 실행

- 단위: `make test`
- 통합: `make integration`. `WEBSERV_SLOW_TESTS=1`이면 30초 타임아웃 시험과 빌드 규칙 시험(소스 사본에서 전체 빌드)을 더한다. fd 수를 세는 N-04와 CPU 시간을 재는 N-19는 `/proc`이 있는 Linux에서만 돈다. 평가 환경과 같은 Ubuntu 22.04 컨테이너에서 모두 돌린다.
- 일부러 틀리게 바꿔 실패를 확인할 때는 바꾼 소스의 오브젝트와 실행 파일을 지운 뒤 빌드한다. macOS의 GNU Make 3.81에서 같은 초 안에 소스를 바꾸고 되돌리면 다시 컴파일·링크하지 않아, 바꾸기 전 결과로 시험한 일이 있었다 (2026-10-16 관찰. 초 단위 시각 비교 때문으로 본다, **판단**).

## 0. 빌드

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| B-01 | Makefile 규칙 `$(NAME)`, `all`, `clean`, `fclean`, `re` | raw/subject.md:48 | I | 각 규칙이 성공하고 `fclean` 뒤 산출물이 없다 | `test_build.py` `test_b01_b03_rules_build_and_clean` (느린 테스트) | 있음 |
| B-02 | 다시 링크하지 않는다 | raw/subject.md:47, raw/evaluation-sheet-en.md:60 | I | 두 번째 `make`가 아무것도 하지 않는다 | `test_build.py` `test_b02_second_make_does_not_relink` (느린 테스트) | 있음 |
| B-03 | `c++ -Wall -Wextra -Werror`로 컴파일되고, `-std=c++98`을 더해도 컴파일된다 | raw/subject.md:49-50 | I | 컴파일러 기본 표준(플래그 없음)과 `-std=c++98` 모두에서 빌드 성공 | `test_build.py` `test_b01_b03_rules_build_and_clean`(Makefile의 `-std=c++98`), `test_b03_builds_without_std_flag`(`CXXFLAGS=-Wall -Wextra -Werror`로 빌드, 느린 테스트) | 있음 (2026-10-27). 2026-10-25 모의 평가에서 `std::auto_ptr` deprecated 경고 때문에 `-std=c++98` 없이는 빌드되지 않는 것을 찾았고([[analysis/mock-evaluation]]), `std::auto_ptr`를 없앴다 (webserv `664692b`). 되돌리면 Ubuntu 22.04 g++ 11.4.0에서 새 테스트가 실패한다 |
| B-04 | C++ 버전이 있으면 C 헤더 대신 쓴다. 외부 라이브러리·Boost 금지 | raw/subject.md:51-52 | R | `.h` 헤더는 C++ 버전이 없는 POSIX 헤더뿐. 링크에 `-l` 없음 | 코드 읽기 2026-10-16: `.h`는 `arpa/inet.h`, `fcntl.h`, `netinet/in.h`, `poll.h`, `sys/socket.h`, `sys/stat.h`, `unistd.h`뿐 | 확인. 단계마다 다시 본다 |
| B-08 | 허용 함수 목록에 없는 C 함수(`memset`·`strchr`·`strlen`·`<cctype>` 등)를 쓰지 않는다. 시스템 호출은 목록 안의 것만. 목록이 표준 라이브러리에도 적용되는지는 **미확인**이라 엄격한 쪽을 따른다 | raw/subject.md:111-113, raw/subject.md:51, [[analysis/subject-vs-evaluation]] 1.4 | R, U | 호출하는 외부 함수 목록이 허용 목록 안 | 코드 읽기 2026-10-17: 시스템 호출은 목록 안의 것만. C 함수는 `strerror`(목록 안)만 남는다. 문자 판별·숫자 해석은 `http/Ascii`가 C++ 표준 라이브러리(`find_first_not_of`, `<locale>`의 `std::tolower`)와 범위 비교로 한다. 구조체 초기화는 값 초기화. `ascii_test.cpp` 3개 | 있음 |
| B-05 | 다른 웹 서버를 `execve`하지 않는다 | raw/subject.md:128 | R | `execve`는 CGI 실행에만 | 코드 읽기 2026-10-22: `execve`는 `src/cgi/CgiProcess.cpp:226` 한 곳이고, CGI 자식에서 `cgi` 지시자의 프로그램을 실행한다 | 확인 |
| B-06 | README: 저장소 루트, 영어, 첫 줄 이탤릭 정해진 문구, Description·Instructions·Resources(AI 사용 포함). 하나라도 없으면 0점 | raw/subject.md:196-207, raw/evaluation-sheet-en.md:35-44 | I, M | 형식은 테스트, 내용은 9단계에 읽어서 확인 | `test_readme.py` 2개 (첫 줄 형식, 세 절) | 있음(형식). 내용은 E-09에서 사용자가 확인. 첫 줄 login은 `yoshin, jyoo` (사용자 확인, 2026-10-16) |
| B-07 | 제출 파일 종류: `Makefile`, `*.{h, hpp}`, `*.cpp`, `*.tpp`, `*.ipp`, 설정 파일 | raw/subject.md:105 | M | 제출할 파일을 고른다 | — | 나중. 제출 때 파일을 따로 추린다(사용자, 2026-10-16). 그 전까지 저장소에 테스트·도구 파일을 둔다 |

## 1. 설정 파일

"설계 3절"은 [[analysis/design]] 3절 "설정 파일"이다. 현재 테스트 이름은 `tests/unit/config_test.cpp`의 `TEST_CASE`다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| C-01 | 명령줄 인자로 받은 설정 파일을 쓰고, 없으면 기본 경로의 파일을 쓴다 | raw/subject.md:127 | I | 인자 없이 실행하면 `conf/default.conf`로 시작한다 | `test_startup.py` `test_c01_*` 2개 | 있음 |
| C-02 | 인자가 2개 이상이면 사용법을 출력하고 끝낸다 | 설계 (인자는 설정 파일 하나, raw/subject.md:107) | I | 종료 코드 1, 크래시 없음 | `test_startup.py` `test_c02_rejects_two_arguments` | 있음 |
| C-03 | 설정 파일이 없거나 일반 파일이 아니면 원인을 출력하고 시작하지 않는다 | 설계 3절 | U, I | 메시지에 원인. 프로세스는 종료 코드 1 | `reportsMissingFile`, `rejectsDirectoryAsFile`, `test_startup.py` `test_c03_*` 2개 | 있음 |
| C-04 | NGINX 문법: `server`·`location` 블록, `이름 인자;`, `#` 주석 | 설계 3절, [[analysis/design-decisions]] 9 | U | 설계 3절 예시가 그대로 읽힌다 | `parsesDesignExample` (주석 포함) | 있음 |
| C-05 | 문법 오류(`;` 누락, 닫히지 않은 블록, 남는 `}`, 따옴표, 빈 파일)는 거부 | 설계 3절 | U | `ConfigError` | `rejectsSyntaxErrors` | 있음 |
| C-06 | 오류 메시지에 파일 이름과 줄 번호 | 설계 3절 | U | `test.conf:3:` | `reportsLineNumbers` | 있음 |
| C-07 | 알 수 없는 지시자, 잘못된 위치, 인자 개수 오류, 블록 여부 오류는 거부 | 설계 3절 | U | `ConfigError` | `rejectsUnknownOrMisplacedDirectives` | 있음 |
| C-08 | 한 값만 받는 지시자가 두 번 나오면 거부 | 설계 (구현 세부) | U | `duplicate "root"` | `rejectsLocationProblems` (`root`만) | 있음 |
| C-09 | 서버가 listen할 `interface:port`를 여러 개 정의 | raw/subject.md:163 | U | server 하나에 `listen` 여러 줄, server 여러 개 | `acceptsSeparateServersOnDifferentPorts`, `acceptsSeveralListensInOneServer` | 있음 |
| C-10 | `listen 8080;`처럼 주소를 생략하면 `0.0.0.0` | 설계 3절 | U | host `0.0.0.0` | `defaultsWhenNotConfigured` | 있음 |
| C-11 | 잘못된 `listen` 값(포트 0·65536 이상, 잘못된 IPv4, 호스트 이름) 거부 | 설계 3절 | U | `invalid listen` | `rejectsListenProblems`, `acceptsPortBoundaries` | 있음. 주소만(`listen 127.0.0.1;`)과 `*:8000`도 거부한다 (`rejectsListenWithoutPortOrWithWildcard`). NGINX는 둘 다 받지만 거부하기로 했다 ([[analysis/design-decisions]] 13) |
| C-12 | 같은 `interface:port`가 두 번 나오면 에러로 시작하지 않는다 (virtual host 미구현) | raw/evaluation-sheet-en.md:108, [[analysis/design-decisions]] 4 | U, I | `duplicate listen`. 프로세스는 종료 코드 1 | `rejectsListenProblems`, `rejectsDuplicateListenInOneServer`, `test_startup.py` `test_c12_duplicate_listen_stops_startup` | 있음 |
| C-13 | `0.0.0.0:P`와 특정 IP의 `:P`는 겹침으로 거부 | 설계 ([[concepts/configuration-file]] "포트 관련 엣지 케이스") | U | `conflicts with` | `rejectsListenProblems`, `rejectsWildcardAfterSpecificAddress` | 있음 |
| C-14 | 기본 에러 페이지 설정 (`error_page 코드... 경로`) | raw/subject.md:164, raw/evaluation-sheet-en.md:69 | U | 코드별 경로. 300~599 밖 코드, `/`로 시작하지 않는 경로, 같은 코드 중복은 거부 | `parsesDesignExample`, `rejectsBadErrorPages` | 있음 |
| C-15 | 요청 본문 최대 크기 설정. 숫자·`k`·`m` 단위, 1 이상 100MB 이하 | raw/subject.md:165, [[analysis/design-decisions]] 11 | U | 범위 밖·잘못된 단위·넘침은 거부 | `rejectsBodySizeOutsideRange`, `acceptsBodySizeWithoutUnitAndLowerBound`, `locationInheritsServerSettings` (`2k`), `parsesDesignExample` (`10m`) | 있음 |
| C-16 | 라우트는 prefix로 지정하고 정규식은 받지 않는다. 경로는 `/`로 시작. 같은 경로 중복은 거부 | raw/subject.md:166 | U | 수식어(`=`, `~`) 거부 | `rejectsUnknownOrMisplacedDirectives`, `rejectsLocationProblems` | 있음 |
| C-17 | 라우트별 허용 메서드 (`limit_except ... { deny all; }`). GET을 허용하면 HEAD도. 없으면 GET·HEAD만 (2026-10-17 [[analysis/design-decisions]] 16. 그 전에는 전부 허용) | raw/subject.md:167, raw/evaluation-sheet-en.md:73, 설계 3절 | U | 허용 집합. 블록 안 다른 내용·모르는 메서드는 거부 | `parsesDesignExample`, `rejectsBadLocationDirectives` | 있음 |
| C-18 | HTTP 리다이렉트 (`return 코드 URL`) | raw/subject.md:168 | U | 코드와 URL. 301·302·303·307·308이 아니면 거부 (설계) | `parsesDesignExample`, `rejectsBadLocationDirectives` | 있음 |
| C-19 | 파일을 찾을 디렉토리 (`root`, subject 예시는 `alias`). 한 location에 둘 다 있으면 거부. 둘 다 없고 `return`도 없으면 거부 | raw/subject.md:169, 설계 3절 | U | 값 저장과 거부 | `parsesDesignExample`, `rejectsLocationProblems` | 있음 |
| C-20 | 디렉토리 리스팅 켜기·끄기 (`autoindex`), 기본 off | raw/subject.md:170 | U | `on`/`off`만 받는다 | `defaultsWhenNotConfigured`, `locationInheritsServerSettings`, `rejectsBadLocationDirectives` | 있음 |
| C-21 | 디렉토리 요청 때 줄 기본 파일 (`index`), 기본 `index.html` | raw/subject.md:171, raw/evaluation-sheet-en.md:72 | U | 파일 목록 | `defaultsWhenNotConfigured`, `locationInheritsServerSettings` | 있음 |
| C-22 | 업로드 허용과 저장 위치 (`upload_store`) | raw/subject.md:172 | U | 경로 저장 | `parsesDesignExample` | 있음 |
| C-23 | 확장자별 CGI (`cgi .확장자 실행파일`) | raw/subject.md:173 | U | 확장자→실행 파일. `.` 없는 확장자, 중복은 거부 | `parsesDesignExample`, `rejectsBadLocationDirectives` | 있음 |
| C-24 | location은 server 값을 물려받고, 자기 값이 있으면 그것을 쓴다 | 설계 3절 | U | 상속과 덮어쓰기 | `locationInheritsServerSettings` (상속), `locationOverridesServerSettings` (덮어쓰기) | 있음 |
| C-25 | location `/`가 없고 server에 `root`가 있으면 `/`를 만든다. `root`도 없으면 만들지 않는다 | 설계 3절 | U | 있음/없음 | `serverRootCreatesImplicitRootLocation`, `noImplicitRootLocationWithoutServerRoot` | 있음 |
| C-26 | location은 긴 경로부터 정렬 (4단계 가장 긴 prefix 매칭의 준비) | 설계 7절 `matchLocation` | U | 경로 길이 내림차순 | `locationsAreSortedLongestFirst` | 있음. 매칭 자체는 R-02 |
| C-28 | 비정상적으로 깊게 중첩된 설정 파일에도 크래시하지 않는다. 유효한 중첩은 server > location > limit_except 3단계 | raw/subject.md:46, 설계 3절 | U, I | 깊이 4부터 설정 오류, 10만 단계도 종료 코드 1 | `rejectsBlocksNestedTooDeeply`, `test_startup.py` `test_c28_deeply_nested_config_does_not_crash` (10만 단계) | 있음. 고치기 전 10만 단계에서 종료 코드 139 |
| C-29 | `index` 값에 `/`가 들어가면 설정 오류 (root 밖을 가리키지 못하게) | [[concepts/security]] 1절, 설계 | U | `index ../x;`는 오류 | `config_test.cpp` `c29_rejectsIndexNamesWithSlash` | 있음 |
| C-27 | 평가 시연용 설정 파일과 기본 파일을 저장소에 둔다 | raw/subject.md:184 | M | 기능별 설정으로 시연 가능 | 9절 E-01~E-08 (`test_demo.py`) | 있음 |

## 2. 이벤트 루프와 연결

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| N-01 | 모든 I/O를 `poll()` 하나로 처리하고, 읽기·쓰기를 함께 감시한다 | raw/subject.md:130-131, raw/evaluation-sheet-en.md:53 | R | `poll` 호출이 `EventLoop::run` 한 곳뿐 | 코드 읽기 2026-10-25: `poll`은 `src/core/EventLoop.cpp:48` 한 곳. 감시할 이벤트는 handler마다 `wantedEvents()`로 정해 한 배열에 읽기·쓰기가 함께 들어간다 | 확인 |
| N-02 | 준비 알림 없이 소켓을 읽거나 쓰지 않는다. 준비 1회에 I/O 1번은 설계(원문은 EAGAIN까지 반복도 허용) | raw/subject.md:132, raw/subject.md:136, raw/evaluation-sheet-en.md:54 | R | `recv`·`send`·`accept`가 `onEvent` 경로에서만 불린다 | 코드 읽기 2026-10-25: `recv`는 `src/http/Connection.cpp:127`, `send`는 `:168`, 각각 `onEvent`의 `POLLIN`·`POLLHUP`(`:56`)·`POLLOUT`(`:58`) 확인 뒤에만 불린다. `accept`는 `src/core/Listener.cpp:72`, `POLLIN` 확인(`:67`) 뒤. CGI pipe의 `write`·`read`는 `src/cgi/CgiPipes.cpp:31`·`:70`이고 각 `onEvent` 안에서만 불린다. 시계 파일 `write`는 일반 파일이라 예외 (raw/subject.md:134) | 확인 |
| N-03 | 읽기·쓰기 뒤 errno로 동작을 바꾸지 않는다 | raw/subject.md:133, raw/evaluation-sheet-en.md:57 | R | `recv`·`send` 뒤에 errno를 읽는 곳이 없다 | 코드 읽기 2026-10-25: `recv`·`send`와 CGI pipe `read`·`write` 뒤에 errno를 읽지 않는다. errno는 `src/core/Listener.cpp:58`에서 시작 때 listen 소켓 준비(`socket`~`fcntl`) 실패 메시지에만 쓴다 | 확인 |
| N-04 | `recv`·`send` 반환값 0과 -1을 모두 처리하고, 에러면 클라이언트를 제거한다 | raw/evaluation-sheet-en.md:55-56 | R, I | 코드에 두 경우가 있고, 클라이언트가 끊으면 연결이 정리된다 | 코드 읽기 2026-10-25: `src/http/Connection.cpp:130`, `:169`가 0과 -1을 모두 닫기로 처리. `test_connections.py` `test_n04_peer_close_releases_the_socket` (Linux `/proc`에서 서버의 fd 수 확인, macOS에서는 건너뜀) | 있음 |
| N-05 | 여러 포트에서 서로 다른 server로 응답한다 | raw/subject.md:149, raw/evaluation-sheet-en.md:107 | I | 두 포트에 동시에 요청해 모두 응답 | `test_connections.py` `test_n05_concurrent_clients_on_two_ports` (50개) | 있음. 포트별로 다른 내용은 R-17 |
| N-06 | 다른 프로세스가 이미 쓰는 `interface:port`면 메시지를 내고 끝낸다. 크래시하지 않는다 | raw/evaluation-sheet-en.md:109 | I | 두 번째 프로세스가 `Address already in use`, 종료 코드 1. 첫 프로세스는 계속 응답 | `test_startup.py` `test_n06_second_instance_on_same_port_fails_cleanly` | 있음 |
| N-07 | 클라이언트가 요청 도중·응답 도중 끊어도 서버는 계속 동작한다 (`SIGPIPE`로 죽지 않음) | raw/subject.md:46, raw/subject.md:129 | U, I | 끊은 뒤 새 요청에 응답. `SIGPIPE`는 무시, `SIGCHLD`는 기본 동작 | `test_connections.py` `test_n07_*` 3개 (요청 도중 끊김, 응답 전 RST, 8MB 응답 도중 FIN으로 떠남), `signals_test.cpp` `n07_sigpipeIsIgnoredAndSigchldLeftAlone` | 있음 (2026-10-18). `SIGPIPE` 무시를 지우면 단위 테스트가 실패한다. 통합 테스트로는 일으킬 수 없었다: 상대가 RST를 보내면 서버가 `POLLERR`·`POLLHUP`을 먼저 보고 `send` 없이 닫아, 두 번째 `send`(raw/macos-observed-sigpipe-leaks.md:114-117)가 생기지 않는다(macOS·Ubuntu 모두 확인). `SIGPIPE`는 poll과 send 사이, CGI pipe write의 짧은 경쟁에서만 생길 수 있다 (**판단**) |
| N-08 | 요청이 무한히 매달리지 않는다: 머리가 끝나지 않은 연결은 헤더 타임아웃 뒤 닫힌다 | raw/subject.md:139 | I | 30초 뒤 연결이 닫힌다 (3단계부터는 408) | `test_connections.py` `test_n08_unfinished_head_gets_408` (느린 테스트, 약 30초) | 있음. 3단계부터 408 |
| N-09 | 머리가 상한을 넘으면 연결을 닫는다 (3단계부터는 431) | 설계 12절 `kMaxHeaderBytes` | I | 16384바이트를 넘게 보내면 닫힌다 | `test_connections.py` `test_n09_oversized_head_gets_431` | 있음. 3단계부터 431 |
| N-10 | `SIGINT`·`SIGTERM`이면 모든 fd와 메모리를 정리하고 정상 종료한다 | 설계 10절. 누수 검사 raw/evaluation-sheet-en.md:25 | I, M | 종료 코드 0. valgrind 오류·누수 0, 열린 fd는 표준 3개 | `test_startup.py` `test_n10_*` 2개, `test_cgi.py` `test_g20_*` 2개. 8절 절차로 통합 테스트 전체의 서버를 valgrind에서 SIGINT로 끈다 | 있음 (2026-10-18, 8절) |
| N-11 | `siege -b`로 빈 페이지 GET availability 99.5% 초과 | raw/evaluation-sheet-en.md:114 | M | 99.5% 초과 | 8절 절차 (siege 4.0.7, `-b -c 50`) | 확인 (2026-10-18): 정적 5분 1,355,986건, 정적·CGI·404 혼합 3분 105,100건, 둘 다 availability 100%, 실패 0 |
| N-12 | 계속 돌려도 메모리가 끝없이 늘지 않고 매달린 연결이 없다 | raw/evaluation-sheet-en.md:115-117 | M | 장시간 siege 동안 메모리 일정 | 8절 절차 (30초마다 RSS·fd·자식 수) | 확인 (2026-10-18): 두 실행 내내 RSS 1.7~2.7MB, 끝난 뒤 fd 4개(시작과 같음)·CGI 자식 0개 |
| N-13 | 시계: 시계 파일의 수정 시각을 현재 시각으로 쓴다. 시작 때 실패하면 시작하지 않는다 | [[analysis/design-decisions]] 10, 설계 4절 "시계" | U, I | 갱신 성공 시 값이 0보다 크고 줄지 않는다. 쓸 수 없는 경로면 `refresh()`가 false | `clock_test.cpp` 2개, `test_startup.py` `test_n13_unusable_clock_file_stops_startup` | 있음 |
| N-14 | 이벤트 루프: 처리 중 `unwatch`는 그 바퀴 끝에 반영. `onEvent` 예외는 그 handler의 `onFailure()`로 | 설계 4절 | U | pipe fd와 가짜 handler로 확인 | `event_loop_test.cpp` 3개 | 있음 |
| N-15 | IPv4 주소 변환 (listen 주소 → `sockaddr_in`). 접속한 주소 → 문자열은 G-01 (`g01_addressAndPathText`) | 설계 (구현 세부) | U | 네트워크 바이트 순서 | `parsesIpv4`, `buildsSockaddrInNetworkOrder` (`tests/unit/socket_address_test.cpp`) | 있음 |
| N-16 | 모든 소켓은 non-blocking | raw/subject.md:129 | R | listen 소켓과 accept한 소켓 모두 `O_NONBLOCK` | 코드 읽기 2026-10-25: `src/core/Listener.cpp:51`(listen, `bind`·`listen` 뒤에 켬), `:86`(accept한 소켓, 실패하면 닫음) | 확인 |
| N-17 | `fcntl`은 `F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC`만 | raw/subject.md:155-157 | R | 다른 플래그 없음 | 코드 읽기 2026-10-25: `fcntl` 호출은 위 두 곳과 CGI pipe의 부모 쪽 끝 두 개(`src/cgi/CgiProcess.cpp:158-159`)로, 모두 `F_SETFL, O_NONBLOCK` | 확인 |
| N-18 | `poll()`이 메인 루프 안에 있다 | raw/evaluation-sheet-en.md:53 | R | `main` → `EventLoop::run` → `poll` | 코드 읽기 2026-10-25: `src/main.cpp:86` `loop.run(server)`, `run`이 매 바퀴 `pollOnce`에서 `poll` | 확인 |
| N-19 | `POLLOUT`은 보낼 데이터가 있을 때만 켠다 (안 그러면 busy waiting) | raw/posix-poll.md:175, [[concepts/io-multiplexing]] "POLLOUT은 보낼 데이터가 있을 때만" (**판단**) | R, I | 연결이 대기 중이어도 서버가 CPU를 거의 쓰지 않는다 | 코드 읽기 2026-10-25: `src/http/Connection.cpp:41` `wantedEvents`는 `WRITE` 상태에서만 `POLLOUT`. `test_connections.py` `test_n19_idle_connections_do_not_spin` (Linux `/proc`에서 CPU 시간 확인: 대기 연결 10개, 2초 동안 0.2초 미만) | 있음 |
| N-20 | `POLLERR`·`POLLNVAL`이면 클라이언트를 제거 | raw/evaluation-sheet-en.md:55, [[concepts/io-multiplexing]] "revents 처리" | R | 연결을 닫는다 | 코드 읽기 2026-10-25: `src/http/Connection.cpp:46` | 확인 |
| N-21 | 디스크 파일의 동기 I/O가 루프를 멈추지 않는다 | raw/evaluation-sheet-en.md:59 | R | 설정 파일은 시작 때만, 시계 파일은 바퀴마다 1바이트 | 코드 읽기 2026-10-25: `src/main.cpp:58` 시작 때 설정 읽기. 시계는 `Clock::refresh` | 확인. 정적 파일은 R-16 |
| N-22 | 메모리가 부족해도 크래시하지 않는다 | raw/subject.md:46 | R, M | 할당 실패가 예외로 오면 그 연결만 정리 | 코드 읽기: `Server::adopt`가 생성 실패를 잡고, `onEvent` 예외는 `onFailure`로 간다 (N-14). 다만 Ubuntu 컨테이너에서 메모리가 바닥나면 `bad_alloc` 없이 프로세스가 강제 종료됐다 (raw/design-checks-observed.md:119-123) | 부족: 예외가 오지 않는 경우는 본문 상한(결정 11)으로만 막는다 |
| N-24 | 헤더 수신 타임아웃은 받기 시작한 때부터 잰다. 바이트를 조금씩 계속 보내도 연장되지 않는다 (본문·전송은 무입력·무진행 기준) | raw/subject.md:139, 설계 12절 | I | 5초마다 1바이트씩 보내도 약 30초 뒤 408 | `test_connections.py` `test_n24_trickled_head_still_times_out` (느린 테스트, 5초마다 1바이트) | 있음 |
| N-25 | 이벤트 처리 밖(타임아웃 점검, poll 목록 만들기)에서 난 예외도 프로세스를 비정상 종료시키지 않는다. 연결 하나에서 나면 그 연결만 닫고, 그 밖이면 원인을 출력하고 종료 코드 1 | raw/subject.md:46, raw/evaluation-sheet-en.md:24 | R | `Server::afterIteration`이 연결마다 예외를 잡고, `main`이 마지막으로 잡는다 | 코드 읽기 + 예외 주입 실험 2026-10-17: 타임아웃 점검에서 던지면 그 연결만 닫히고 새 요청은 200, poll 처리에서 던지면 `webserv: stopped: ...`와 종료 코드 1 | 확인 |
| N-23 | 평가자가 `valgrind`·`leaks`·`e_fence`로 돌려도 오류·누수가 없다. `e_fence`에서는 heap 경계 오류가 곧 크래시 | raw/evaluation-sheet-en.md:25, [[concepts/resilience]] "SIGINT·SIGTERM과 누수 검사" | M | valgrind 오류 0, still reachable까지 누수 0. e_fence에서 크래시 없음 | 8절 절차: 단위 테스트와 통합 테스트 전체를 valgrind와 e_fence 아래에서 | 확인 (2026-10-18, Ubuntu 22.04 컨테이너). macOS `leaks`는 평가 환경이 아니고 SIGINT 종료를 검사하지 못해 (raw/macos-observed-sigpipe-leaks.md:224-226) 쓰지 않는다 |
| N-26 | fd가 다 차 `accept`가 실패해도 루프가 쉬지 않고 돌지 않고, fd가 풀리면 다시 받는다 | raw/subject.md:139, 8절 R5 | I | fd 한도 16인 서버에 32개 연결: 2초 동안 CPU 10% 미만, 연결을 닫으면 200 | `test_connections.py` `test_n26_*` (Linux) | 있음. 고치기 전에는 10%를 넘어 실패 |

- N-01~N-03은 0점 조건이다 (raw/evaluation-sheet-en.md:53, raw/subject.md:136, raw/evaluation-sheet-en.md:57). 테스트가 통과해도 지켰다는 증거가 되지 않으므로, 단계마다 코드 경로를 읽어 확인하고 결과를 이 페이지에 적는다.

## 3. 요청 파서

읽은 위키: [[analysis/implementation-plan]] 3단계, [[analysis/design]] 5·6·11·12절, [[concepts/request-parsing]], [[concepts/status-codes]], [[concepts/security]] 3·5절. 경로 디코딩·`..` 처리([[concepts/security]] 1절)는 설계상 Router의 일이라 4단계다.
"설계 6절"의 선택 중 위키에 없던 것은 [[analysis/design]] 6절 "구현 세부"에 적는다. 단위 테스트는 `RequestParser`에 바이트를 넣어 결과와 상태 코드를 본다. 통합 테스트는 서버에 소켓으로 보내 응답 코드를 본다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| P-01 | 요청이 몇 번에 나뉘어 와도 같은 결과. 덜 온 것과 문법 오류를 구분 | raw/posix-recv.md:62 | U | 어느 위치에서 나눠 넣어도 결과가 같다. 덜 왔으면 `NEED_MORE` | `request_parser_test.cpp` `p01_*` 2개 (모든 위치에서 나눠 넣기) | 있음 |
| P-02 | 한 번에 요청 둘이 와도 첫 요청만 소비하고 나머지는 남긴다 | 설계 5절 pipelining (5단계에서 사용) | U | 남은 바이트가 그대로 버퍼에 있다 | `request_parser_test.cpp` `p02_leavesTheNextRequestInTheBuffer` | 있음 |
| P-03 | 줄 끝은 CRLF. LF 하나도 받는다(MAY). LF가 뒤따르지 않는 CR은 400 | raw/rfc9112.txt:283-291 | U | LF만 쓴 요청 성공. bare CR은 400 | `request_parser_test.cpp` `p03_lineEndings` (chunk 확장 안의 CR 포함), `test_requests.py` `test_p03_lf_only_request_is_accepted` | 있음 |
| P-04 | 요청줄 앞의 빈 줄은 무시 (SHOULD) | raw/rfc9112.txt:301-303 | U | 앞에 CRLF가 있어도 성공 | `request_parser_test.cpp` `p04_ignoresEmptyLinesBeforeTheRequestLine` | 있음 |
| P-05 | 요청줄은 `method SP request-target SP HTTP-version`. 구분자는 SP 하나만 받는다(설계: 관대한 파싱은 smuggling 위험). target 안 공백 포함 잘못된 요청줄은 400 | raw/rfc9112.txt:377-388, raw/rfc9112.txt:425-435 | U | SP 두 개, 탭, 요소 누락은 400 | `request_parser_test.cpp` `p05_requestLineNeedsSingleSpaces` | 있음 |
| P-06 | 메서드는 대소문자 구분. 모르는 메서드는 501. 구현한 어떤 메서드보다 긴 메서드도 501. token 문자가 아니면 400 | raw/rfc9110.txt:3799-3801, raw/rfc9112.txt:391-393 | U, I | `get`·`PUT`·`UNKNOWN`은 501, 크래시 없음 (raw/evaluation-sheet-en.md:80) | `request_parser_test.cpp` `p06_methods`, `test_requests.py` `test_p06_unknown_method_is_501` | 있음 |
| P-07 | request-target이 상한보다 길면 414 (MUST). 요청줄 상한 `kMaxRequestLine` 8192 (8000 이상 권장) | raw/rfc9112.txt:393-399, 설계 12절 | U, I | 8192 이하 성공, 넘으면 414 | `request_parser_test.cpp` `p07_longTargetIs414` (8192 경계), `test_requests.py` `test_p07_long_target_is_414` | 있음 |
| P-08 | 버전은 `HTTP/숫자.숫자`, 대소문자 구분. 메이저가 1이 아니면 505. 1.x의 높은 마이너는 1.1로 처리(SHOULD). 버전이 없으면 400 | raw/rfc9112.txt:333-337, raw/rfc9110.txt:7908-7910, raw/rfc9110.txt:2061-2065, [[concepts/request-parsing]] 2절 | U | `HTTP/2.0` 505, `HTTP/1.2`는 1.1, `http/1.1`·`HTTP/1`·버전 없음은 400 | `request_parser_test.cpp` `p08_versions`, `test_requests.py` `test_p08_unsupported_major_version_is_505` | 있음 |
| P-09 | target은 origin-form과 absolute-form(MUST)을 받는다. 첫 `?`에서 path와 query를 나눈다. 둘 다 아니면 400 | raw/rfc9112.txt:454, raw/rfc9112.txt:508-516, raw/rfc3986.txt:1204-1206 | U | `/a?b=1` → path `/a`, query `b=1`. `http://h:8080/a?q` → path `/a`, query `q`. `*`·`a/b`는 400 | `request_parser_test.cpp` `p09_targets` | 있음 |
| P-10 | 헤더는 `name ":" OWS value OWS`. 이름은 대소문자 무시. 이름과 `:` 사이 공백은 400 (MUST). 값 앞뒤 공백 제외 | raw/rfc9112.txt:697-701, raw/rfc9112.txt:714-729 | U | `Host : x`는 400. `host:  x  `의 값은 `x` | `request_parser_test.cpp` `p10_headerFieldSyntax` | 있음 |
| P-11 | 요청줄과 첫 헤더 사이의 공백 줄, obs-fold는 400 (둘 다 MUST 중 거부 쪽을 고름) | raw/rfc9112.txt:308-313, raw/rfc9112.txt:746-751 | U | 400 | `request_parser_test.cpp` `p11_linesStartingWithWhitespace` | 있음. 공백으로 시작하는 줄은 헤더 이름 검사(token)가 거부한다. 따로 두었던 검사는 테스트로 구분할 수 없어 뺐다 |
| P-12 | HTTP/1.1에 Host가 없으면 400. 버전과 관계없이 Host가 두 줄 이상이거나 값이 잘못되면 400 (MUST) | raw/rfc9112.txt:445-448 | U, I | 400. HTTP/1.0에 Host가 없으면 성공 | `request_parser_test.cpp` `p12_hostRules`, `test_requests.py` `test_p12_missing_host_is_400` | 있음 |
| P-13 | 헤더가 상한(`kMaxHeaderBytes` 16384)을 넘으면 431 (MUST 4xx, 431은 **판단**) | raw/rfc9110.txt:1568-1572, raw/rfc6585.txt:177-184 | U, I | 431 | `request_parser_test.cpp` `p13_largeHeaderSectionIs431`, `test_requests.py` `test_p13_large_header_section_is_431`, `test_connections.py` `test_n09_oversized_head_gets_431` | 있음 |
| P-14 | 본문 길이: TE와 CL이 함께 오면 400 후 닫기(MAY 거부를 고름, 닫기는 MUST). 마지막 coding이 chunked가 아니면 400. 모르는 coding은 501. CL이 잘못되면 400(같은 값 목록 `42, 42`는 예외). 둘 다 없으면 0. HTTP/1.0에 TE가 있으면 400 후 닫기. HTTP/1.0 POST에 CL이 없으면 400 | raw/rfc9112.txt:880-889, raw/rfc9112.txt:930-934, raw/rfc9112.txt:950-965, raw/rfc9112.txt:980-981, raw/rfc9112.txt:851-852, raw/rfc1945.txt:1763-1765 | U | 각 경우의 코드 | `request_parser_test.cpp` `p14_bodyLengthRules` | 있음 |
| P-15 | CL 숫자 변환 오버플로를 막는다 (MUST) | raw/rfc9110.txt:3251-3254 | U | 아주 긴 숫자는 400 | `request_parser_test.cpp` `p15_hugeContentLengthDoesNotOverflow` | 있음 |
| P-16 | CL이 본문 상한을 넘으면 본문을 읽기 전에 413 | raw/rfc9110.txt:7710-7714, 설계 6절 | U, I | `HEAD_DONE` 뒤 상한 설정, 413 | `request_parser_test.cpp` `p16_contentLengthOverTheLimitIs413`, `test_requests.py` `test_p16_body_limit_follows_the_location`, `router_test.cpp` 2개 | 있음 |
| P-17 | chunked 해제. 16진수 크기 오버플로를 막고(MUST), 모르는 확장은 무시(MUST)하되 길이를 제한, trailer는 버린다(MAY). 해제한 크기가 상한을 넘으면 413 | raw/rfc9112.txt:1078-1081, raw/rfc9112.txt:1108-1113, raw/rfc9112.txt:1126-1134, [[analysis/design-decisions]] 11 | U, I | 본문이 이어 붙여진다. 깨진 chunk는 400. 넘으면 413 | `request_parser_test.cpp` `p17_chunkedBodies`, `test_requests.py` `test_p17_chunked_body_limit` | 있음 |
| P-18 | CL만큼 오기 전에 끊기거나 타임아웃이면 불완전한 요청. 머리·본문 수신 타임아웃이면 408 후 닫기(MAY). 첫 바이트 전이면 그냥 닫기(5단계부터 15초, K-08) | raw/rfc9112.txt:973-978, raw/rfc9112.txt:1253-1255, raw/rfc9110.txt:7641-7643, 설계 5절 | I | 408 후 닫힘 (느린 테스트) | `test_requests.py` `test_p18_*` 2개 (본문 도중 408, 아무것도 안 보낸 연결은 응답 없이 닫힘), `test_connections.py` `test_n08_unfinished_head_gets_408` (모두 느린 테스트) | 있음 |
| P-19 | 오류 응답의 상태줄 `HTTP-version SP status-code SP reason-phrase`, 문법 오류 뒤에는 연결을 닫는다(SHOULD) | raw/rfc9112.txt:652, raw/rfc9112.txt:690-693, raw/rfc9112.txt:319-324 | I | 상태줄과 `Connection: close`, 그 뒤 닫힘 | `test_requests.py` `test_p19_error_response_format_and_close` | 있음. 오류 응답의 에러 페이지는 R-14 |
| P-21 | 파서 비용이 입력 길이에 비례한다. 작은 chunk가 많아도 recv 1번 처리가 루프를 오래 붙잡지 않는다 | raw/subject.md:148 (항상 가용). 파서 비용과 잇는 것은 **판단** | M | 1바이트 chunk 6MB 처리 CPU 시간 | 측정 (scratch 벤치마크, 최적화 없는 빌드): 1바이트 chunk 6MB가 1.6초 → 0.2초 (2026-10-16) | 확인. 테스트로 남기지 않음(시간 측정은 기계마다 다르다) |
| P-20 | telnet·curl로 시연할 수 있다 | raw/evaluation-sheet-en.md:77 | M | 시연 절차 | README의 curl 명령 (E-09, 2026-10-18 실행) | curl은 확인. telnet 시연 자료는 없음 |

## 4. 라우팅, 정적 파일, 응답

읽은 위키: [[analysis/implementation-plan]] 4단계, [[analysis/design]] 1·2·7·8절, [[concepts/http-features]], [[concepts/configuration-file]], [[concepts/security]] 1절, [[concepts/status-codes]], [[sources/nginx-observed-directory]]. 위키에 없던 선택은 [[analysis/design]] 7절 "구현 세부"에 적는다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| R-01 | 경로 정규화: 세그먼트로 나눈 뒤 `%XX`를 한 번만 디코딩, 잘못된 `%`·`%00`·`%2F`는 400, 연속 `/` 합치기, `.`·`..` 제거, 루트 위로 가면 400 + 닫기 | raw/rfc3986.txt:647-652, raw/rfc3986.txt:767-771, raw/rfc3986.txt:2443-2445, raw/rfc3986.txt:689-692, [[concepts/security]] "경로 정규화 절차", [[analysis/design-decisions]] 2·3 | U, I | 정규화 결과와 400 | `path_resolver_test.cpp` 6개, `router_test.cpp` `r01_r02_*`, `test_static.py` `test_r01_bad_paths_are_400` | 있음 |
| R-02 | location은 정규화한 경로의 가장 긴 prefix | raw/nginx-core-module.md:1067 | U | 3단계 `router_test.cpp`를 정규화 경로로 | `router_test.cpp` `routerPicksTheLongestPrefix`, `r01_r02_routesTheNormalizedPath` | 있음 |
| R-03 | `root`는 URI 전체를 붙이고, `alias`는 location 부분을 바꿔 끼운다 (subject 예시는 alias) | raw/nginx-core-module.md:1504-1516, raw/nginx-core-module.md:132-140, raw/subject.md:169 | U, I | `/kapouet/pouic/toto/pouet` → `/tmp/www/pouic/toto/pouet` | `router_test.cpp` `r03_rootAndAliasMapping`, `test_static.py` `test_r03_alias_follows_the_subject_example` | 있음 |
| R-04 | `return`은 그 코드와 `Location`으로 응답 | raw/subject.md:168, raw/rfc9110.txt:7378-7379 | U, I | 301 + `Location: /new/` | `router_test.cpp` `r04_returnRedirects`, `test_static.py` `test_r04_return_redirects` | 있음 |
| R-05 | 라우트에서 막은 메서드는 405 + `Allow` (MUST) | raw/rfc9110.txt:7603-7607, raw/evaluation-sheet-en.md:73 | U, I | 405, `Allow`에 그 location이 받는 메서드 | `router_test.cpp` `r05_r19_*`, `test_static.py` `test_r05_r19_method_not_allowed_has_allow` | 있음 |
| R-06 | 파일 GET은 200, `Content-Length`(SHOULD), 확장자로 정한 `Content-Type`(SHOULD) | raw/rfc9110.txt:3243-3246, raw/rfc9110.txt:2944-2949 | I | 파일 내용 그대로 | `http_date_test.cpp` `r06_mimeTypeByExtension`, `test_static.py` `test_r06_file_with_type_and_length` | 있음 |
| R-07 | HEAD는 본문 없이 GET과 같은 헤더. `Content-Length`도 GET 값 | raw/rfc9110.txt:3987-3988, raw/rfc9110.txt:3993-3994, raw/rfc9110.txt:3226-3230, [[analysis/design-decisions]] 5 | I | 본문 0바이트, 헤더는 GET과 같음 | `response_stream_test.cpp` `r07_*`, `test_static.py` `test_r07_head_has_get_head_without_body` | 있음 |
| R-08 | 없는 파일은 404 | raw/rfc9110.txt:7589-7591, raw/evaluation-sheet-en.md:100 | I | 404 | `router_test.cpp` `r08_missingFileIs404`, `test_static.py` `test_r08_r14_*` | 있음 |
| R-09 | 읽을 수 없는 파일은 403 | raw/rfc9110.txt:7571-7572, [[concepts/status-codes]] | I | 403 (컨테이너는 root라 macOS에서만 의미 있음) | `test_static.py` `test_r09_unreadable_file_is_403` (root면 건너뜀: 컨테이너에서는 돌지 않고 macOS에서 확인) | 있음 |
| R-10 | 끝에 `/` 없는 디렉토리 요청은 `/`를 붙인 경로로 301 (**판단**, NGINX 실측과 같음) | [[concepts/configuration-file]] "디렉토리 요청 처리 순서", [[sources/nginx-observed-directory]] | I | 301 + `Location: /dir/` | `router_test.cpp` `r10_r11_r12_r13_directories`, `test_static.py` `test_r10_*` | 있음 |
| R-11 | 디렉토리 요청에는 index 파일을 적은 순서대로 찾아 준다 | raw/subject.md:171, raw/evaluation-sheet-en.md:72 | I | index 내용 | `router_test.cpp` `r10_r11_r12_r13_directories`, `test_static.py` `test_r11_*` | 있음 |
| R-12 | index가 없고 `autoindex on`이면 HTML 목록 | raw/subject.md:170, raw/evaluation-sheet-en.md:101 | I | 200, 파일 이름이 링크로 나온다. 이름은 HTML 이스케이프 | `router_test.cpp` `r10_r11_r12_r13_directories`, `test_static.py` `test_r12_listing_escapes_names` | 있음 |
| R-13 | index가 없고 `autoindex off`면 403 (**판단**, NGINX 실측과 같음) | [[concepts/status-codes]] | I | 403 | `router_test.cpp` `r10_r11_r12_r13_directories`, `test_static.py` `test_r13_*` | 있음 |
| R-14 | 설정한 에러 페이지가 있으면 그 파일, 없으면 기본 에러 페이지 | raw/subject.md:143, raw/subject.md:164, raw/evaluation-sheet-en.md:69 | I | 404에 설정한 파일 내용, 상태 코드는 404 그대로 | `test_static.py` `test_r08_r14_*` (설정한 파일), `test_r14_default_error_page_without_configuration` | 있음 |
| R-15 | 2xx·3xx·4xx 응답에 `Date` (MUST, 시계가 있으므로). 형식은 IMF-fixdate | raw/rfc9110.txt:2313-2317, raw/rfc9110.txt:1855-1858, raw/rfc9110.txt:1873-1895, [[analysis/design-decisions]] 10 | U, I | `Sun, 06 Nov 1994 08:49:37 GMT` 형식 | `http_date_test.cpp` `r15_formatsImfFixdate`, `test_static.py` `test_r15_responses_carry_date` | 있음 |
| R-16 | 큰 파일은 나눠 읽어 보낸다. 루프를 멈추지 않는다 | raw/subject.md:134, raw/evaluation-sheet-en.md:59, 설계 8절 | I | 10MB 파일이 그대로 도착 | `response_stream_test.cpp` `r16_streamsLargeFileInPieces`, `test_static.py` `test_r16_large_file_arrives_intact` (10MB) | 있음 |
| R-17 | 여러 포트에서 서로 다른 사이트 | raw/subject.md:149, raw/evaluation-sheet-en.md:107 | I | 포트마다 다른 root의 내용 | `test_static.py` `test_r17_ports_serve_different_sites` | 있음 |
| R-18 | 정적 웹사이트를 브라우저로 끝까지 본다 | raw/subject.md:145, raw/evaluation-sheet-en.md:99 | M | 시연용 `www/` | 사용자가 브라우저로 확인 (2026-10-18, 9단계 표 R-18·F-14 행) | 확인 |
| R-20 | alias를 쓰는 location은 떼고 남은 경로가 비었거나 `/`로 시작할 때만 그 location의 파일로 본다. 아니면 404 ([[analysis/design-decisions]] 14) | raw/rfc9110.txt:8560-8565, [[concepts/security]] 1절 | U, I | `location /kapouet { alias www/; }`에서 `/kapouet../secret/s.txt`가 404 | `router_test.cpp` `r20_aliasCoversOnlyWholeSegments`, `test_static.py` `test_r20_alias_cannot_reach_outside` | 있음. 고치기 전에는 alias 밖 파일이 200 |
| R-21 | HEAD 요청에는 오류 응답(파서 오류, 408)에도 본문을 보내지 않는다 (MUST NOT) | raw/rfc9110.txt:3987-3988 | I | HEAD에 413: 헤더만 오고 본문 0바이트 | `test_requests.py` `test_r21_head_error_has_no_body` | 있음 |
| R-19 | 4단계에서 POST·DELETE는 정적 리소스에 대해 405 (업로드·삭제는 6단계) | 설계 7절 순서 | I | 405 + `Allow` | `router_test.cpp` `r05_r19_*`, `test_static.py` `test_r05_r19_*`, `test_requests.py` P-16·P-17 (POST가 405) | 있음. 6단계부터는 `upload_store`가 없는 location의 POST와 `limit_except`에 없는 DELETE가 405다 (F-09, F-12, D-04) |

## 5. 연결 관리

읽은 위키: [[analysis/implementation-plan]] 5단계, [[analysis/design]] 5·12절, [[concepts/connection-management]], [[analysis/subject-vs-evaluation]] 1.5·1.6, [[sources/close-after-413-observed]], [[concepts/testing]] siege 절. 위키에 없던 선택은 [[analysis/design]] 5절 "구현 세부"에 적는다.
통합 테스트 하네스의 `exchange`는 5단계부터 응답 하나를 `Content-Length`로 끊어 읽는다. 연결이 닫히는지 보는 테스트만 닫힐 때까지 읽는다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| K-01 | HTTP/1.1 요청은 응답 뒤에도 연결을 유지한다 (SHOULD 지원). 404·405 같은 오류 응답도 요청을 다 읽었으면 유지 | raw/rfc9112.txt:1337-1340, raw/rfc9112.txt:1350-1351 | I | 한 연결에서 요청 두 개가 모두 응답을 받고, 응답에 `Connection: close`가 없다 | `test_keepalive.py` `test_k01_connection_stays_open_after_a_response` (200·404·200) | 있음 |
| K-02 | 요청에 `close` 옵션이 있으면 그 응답에 `Connection: close`를 붙이고 응답 뒤 닫는다. 뒤 요청은 처리하지 않는다 (MUST). 옵션은 대소문자 무시, 쉼표 목록 | raw/rfc9112.txt:1347-1348, raw/rfc9112.txt:1521-1526, raw/rfc9110.txt:2581, raw/rfc9110.txt:1699-1702 | U, I | `Connection: Keep-Alive, CLOSE`에도 닫는다. 같은 연결에 이어 보낸 요청에는 응답이 없다 | `request_parser_test.cpp` `k02_k03_persistence`, `test_keepalive.py` `test_k02_close_option_ends_the_connection` | 있음 |
| K-03 | HTTP/1.0 요청은 `keep-alive` 옵션이 있어도 응답 뒤 닫는다 (**판단**: 1.0 keep-alive를 받아들일지는 수신자가 정한다) | raw/rfc9112.txt:1353-1359, raw/rfc1945.txt:420-422 | U, I | `Connection: close` 후 닫힘 | `request_parser_test.cpp` `k02_k03_persistence`, `test_keepalive.py` `test_k03_http10_closes_even_with_keep_alive` | 있음 |
| K-04 | 한 번에 온 요청 여러 개(pipelining)에 받은 순서대로 응답한다 (MUST) | raw/rfc9112.txt:1399-1404, P-02 | I | 요청 둘을 한 번에 보내면 응답 둘이 순서대로 온다 | `test_keepalive.py` `test_k04_pipelined_requests_are_answered_in_order` (GET·404·HEAD·GET 한 번에) | 있음. 남은 바이트를 바로 파싱하지 않게 바꾸면 실패한다 |
| K-05 | 요청을 끝까지 믿을 수 없는 오류(파서 오류, 408)와 경로 400(결정 2)은 `Connection: close` 후 닫는다 | raw/rfc9112.txt:1374-1377, [[analysis/design-decisions]] 2 | I | 400·413 뒤 닫힘 | `test_keepalive.py` `test_k05_untrusted_requests_close_the_connection` (Host 없음, `/../x`, 413) | 있음 |
| K-06 | 본문을 다 읽지 않고 응답(413)하면 남은 입력을 읽어 버린 뒤 닫는다. 클라이언트가 본문을 계속 보내도 응답을 받는다 | raw/rfc9112.txt:1539-1546, [[sources/close-after-413-observed]] | I | 10MB 본문을 보내는 동안 413을 받는다 | `test_keepalive.py` `test_k06_whole_body_can_be_sent_after_413` (실측의 Python 클라이언트처럼 본문 10MB를 다 보낸 뒤 읽는다) | 있음. DRAIN을 빼면 `sendall`이 Broken pipe로 실패한다(3회 모두). 처음 쓴 "보내는 도중 읽기" 테스트는 DRAIN을 빼도 통과해서 바꿨다 |
| K-07 | 버리기(DRAIN)에는 무입력 1초, 총 5초 상한 | 설계 12절 `kDrainIdle`·`kDrainTotal` | I | 413 뒤 아무것도 안 보내면 약 1초 뒤, 계속 보내면 약 5초 뒤 닫힌다 | `test_keepalive.py` `test_k07_*` 2개 (무입력이면 4초 안에, 계속 보내면 4초 이상 10초 안에 닫힘) | 있음 |
| K-08 | 요청 첫 바이트를 기다리는 연결(새 연결, keep-alive 대기)은 15초 뒤 응답 없이 닫는다 | raw/rfc9112.txt:1465-1466, 설계 12절 `kKeepAliveTimeout` | I | 응답 하나 뒤 아무것도 안 보내면 약 15초 뒤 닫힘 (느린 테스트) | `test_keepalive.py` `test_k08_idle_keep_alive_connection_is_closed`, `test_requests.py` `test_p18_silent_connection_is_closed_without_response` (새 연결, 둘 다 느린 테스트) | 있음 |
| K-09 | 응답을 읽지 않는 클라이언트는 전송이 30초 동안 진행되지 않으면 닫는다 | 설계 12절 `kSendTimeout`, [[concepts/connection-management]] 타임아웃 표 | I | 큰 파일을 읽지 않고 기다리면 닫히고, 그 뒤 받은 바이트가 파일보다 적다 (느린 테스트) | `test_keepalive.py` `test_k09_unread_response_times_out` (64MB 파일, 느린 테스트). macOS에서 버퍼가 찬 뒤 5초 뒤에도 `send`가 한 번 더 진행돼서 40초를 기다린다 | 있음 |
| K-10 | keep-alive 연결도 머리 타임아웃은 요청의 첫 바이트부터 잰다 | 설계 12절, N-24 | I | keep-alive 대기 뒤 보낸 미완성 머리가 약 30초 뒤 408 (느린 테스트) | `test_keepalive.py` `test_k10_head_timeout_starts_at_the_first_byte` (5초 쉰 뒤 미완성 머리, 느린 테스트) | 있음 |
| K-11 | `siege -b`를 오래 돌려도 메모리가 늘지 않고 매달린 연결이 없다 | raw/evaluation-sheet-en.md:114-117 | M | availability 99.5% 초과, 메모리 일정 | 2026-10-17 Ubuntu 22.04 컨테이너, siege 4.0.7 `-b -c 50 -t 60S`, 빈 페이지. `connection = close`: 690,358건, availability 100%, 실패 0. `keep-alive`: 3,476,698건, 100%, 실패 0, 실행 중 연결 50개 유지. 서버 RSS는 두 실행 모두 1.9~3.1MB에서 늘지 않았고, 끝난 뒤 fd는 시작 때와 같은 4개. siege를 셸 백그라운드(`&`)로 돌리면 "Lifting the server siege..." 뒤 siege가 끝나지 않는 일이 두 번 있었다. 그때 서버에는 클라이언트 연결이 없었고 siege 쪽 소켓은 CLOSE_WAIT였다(서버는 이미 닫음). 포그라운드로 돌리면 세 번 모두 정상 종료 | 확인. 더 긴 실행과 절차는 N-11·N-12, 8절 |

## 6. 업로드와 DELETE

읽은 위키: [[analysis/implementation-plan]] 6단계, [[concepts/file-upload]], [[analysis/design-decisions]] 7·11, [[analysis/design]] 1·3·7·12절, [[concepts/http-features]] 메서드별 규칙, [[concepts/status-codes]], [[concepts/security]] 1절, [[analysis/subject-vs-evaluation]] 1.4절. 새로 정한 것은 [[analysis/design-decisions]] 15~17, 위키에 없던 선택은 [[analysis/design]] 7절 "구현 세부 (단계 6)"에 적는다.
업로드는 `F-`, 삭제는 `D-`로 쓴다. 통합 테스트는 `test_upload.py`다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| F-01 | `multipart/form-data`로 올린 파일을 바이트 그대로 저장하고 GET으로 다시 받는다. 구분자 앞의 CRLF는 내용이 아니다 | raw/subject.md:146, raw/evaluation-sheet-en.md:82, raw/rfc2046.txt:1073-1076 | U, I | CRLF로 끝나고 구분자 비슷한 바이트가 든 내용이 그대로 저장되고 GET 본문도 같다 | `multipart_test.cpp` `f01_f03_*`, `router_test.cpp` `f01_postToAnUploadLocation`, `test_upload.py` `test_f01_*` | 있음 |
| F-02 | 201에 처음 저장한 파일의 `Location`, 본문에 저장한 파일 목록 (SHOULD). GET으로 닿지 않는 저장 위치면 `Location`을 붙이지 않는다 | raw/rfc9110.txt:4050-4055 | I | `Location: /upload/a.txt`, 본문 `/upload/a.txt\n/upload/c%20d.txt\n`. 닿지 않으면 `Location` 없이 이름만 | `test_upload.py` `test_f02_*` 2개 | 있음 |
| F-03 | 파일이 아닌 필드와 `filename=""`인 part는 건너뛰고, 파일이 하나도 없으면 400 | raw/rfc7578.txt:207-213, 설계 7절 | U, I | 필드·빈 파일 입력이 섞여도 파일 하나만 저장. 필드만 있으면 400 | `multipart_test.cpp` `f01_f03_*`, `test_upload.py` `test_f03_*` | 있음 |
| F-04 | multipart 파싱: preamble·epilogue 무시, 구분자 뒤 공백(transport-padding) 처리 (MUST), 내용은 아무 바이트 | raw/rfc2046.txt:1110-1112, raw/rfc2046.txt:1239-1244, raw/rfc2046.txt:1269 | U | NUL·CRLF가 든 내용, 빈 내용 | `multipart_test.cpp` `f04_*` 2개 | 있음 |
| F-05 | 요청 `Content-Type`이 `multipart/form-data`가 아니거나 없으면 415 | [[analysis/design-decisions]] 7, raw/rfc9110.txt:7738-7740 | U, I | urlencoded, `text/plain`, 없음, `multipart/mixed` 모두 415 | `multipart_test.cpp` `f05_f06_*`, `test_upload.py` `test_f05_*` | 있음 |
| F-06 | boundary가 없거나 잘못됨(1~70자 bchars, 공백으로 끝나지 않음), 본문 문법 오류(첫·마지막 구분자 없음, 구분자 줄에 다른 글자, name 있는 `form-data` disposition 없음)는 400 | raw/rfc2046.txt:1200-1214, raw/rfc7578.txt:197-201 | U, I | 400, 아무것도 저장 안 됨 | `multipart_test.cpp` `f05_f06_*`, `f06_*`, `test_upload.py` `test_f06_*` | 있음 |
| F-07 | 파일 이름의 디렉토리 부분(`/`, `\`)은 버린다. 남은 이름이 비었거나 `.`·`..`이거나 255바이트보다 길면 400 (리뷰 전에는 긴 이름이 500) | raw/rfc7578.txt:215-220 | I | `../../evil.txt`는 저장 위치의 `evil.txt`. `..`, `dir/`, `x/..`, 256바이트 이름은 400, 255바이트는 201 | `test_upload.py` `test_f07_*` 2개 | 있음 |
| F-08 | 저장 위치에 있는 이름, 한 요청 안에서 겹치는 이름은 409. 그 요청의 파일은 하나도 저장하지 않는다. 본문에 충돌한 이름 | [[analysis/design-decisions]] 17, raw/rfc7578.txt:497-499, raw/rfc9110.txt:7655-7657 | I | 409, 앞 파일도 저장 안 됨, 기존 파일 내용 그대로, 디렉토리 이름도 409 | `test_upload.py` `test_f08_*` | 있음 |
| F-09 | `upload_store`가 없는 location의 POST는 405이고 `Allow`에 POST가 없다 | [[analysis/design-decisions]] 16 | U, I | `limit_except GET POST`인데 저장 위치가 없으면 405 + `Allow: GET, HEAD` | `router_test.cpp` `f09_f12_d04_*`, `test_upload.py` `test_f09_*` | 있음 |
| F-10 | chunked 본문의 업로드 | raw/subject.md:179, [[concepts/request-parsing]] | I | 해제한 본문이 그대로 저장 | `test_upload.py` `test_f10_*` | 있음 (파서의 chunked 시험은 P-xx) |
| F-11 | parameter 문법: 이름은 대소문자 무시, 값은 token이나 quoted-string, quoted-pair는 뒤 옥텟으로 (MUST). `=` 앞뒤 공백, 닫히지 않은 따옴표, 같은 이름 두 번은 오류 | raw/rfc9110.txt:1789-1792, raw/rfc9110.txt:1818-1825, raw/rfc9110.txt:1833-1834 | U | 값과 오류 | `field_syntax_test.cpp` 3개 | 있음 |
| F-12 | `limit_except`가 없는 location은 POST·DELETE를 받지 않는다 | [[analysis/design-decisions]] 16 | U, I | 405 + `Allow: GET, HEAD`, 파일은 그대로 | `config_test.cpp` `parsesDesignExample`, `router_test.cpp` `f09_f12_d04_*`, `test_upload.py` `test_f12_*` | 있음 |
| F-13 | 쓰기 실패는 500이고 그 요청이 만든 파일을 지운다 | 설계 7절 | I, R | 저장 위치가 없으면 500 | `test_upload.py` `test_f13_missing_store_is_500`. 여러 파일 중 중간 실패 뒤 지우기는 실패를 만들 방법이 없어 코드 읽기로 확인 (2026-10-17) | 있음, 지우기는 확인 |
| D-01 | DELETE는 일반 파일을 지우고 204 (본문·`Content-Length` 없음). 뒤 GET은 404 | raw/rfc9110.txt:4235-4236, raw/rfc9110.txt:3238-3239, raw/evaluation-sheet-en.md:79 | I | 같은 연결에서 DELETE 뒤 GET이 404 (204의 길이 처리 확인) | `test_upload.py` `test_d01_*` | 있음 |
| D-02 | 없는 파일의 DELETE는 404 | raw/rfc9110.txt:7589-7591 | U, I | 404 | `router_test.cpp` `d02_d03_*`, `test_upload.py` `test_d02_d03_*` | 있음 |
| D-03 | 디렉토리의 DELETE는 403 (**판단**, 일반 파일만 지움) | raw/rfc9110.txt:7571-7572 | U, I | `/` 있음·없음 모두 403, 디렉토리 그대로 | `router_test.cpp` `d02_d03_*`, `test_upload.py` `test_d02_d03_*` | 있음 |
| D-04 | `limit_except`에 DELETE가 없으면 405 + `Allow` (평가 "권한 없이 DELETE") | raw/evaluation-sheet-en.md:73, raw/rfc9110.txt:7603-7607 | U, I | 405 + `Allow: GET, HEAD`, 파일 그대로 | `router_test.cpp` `f09_f12_d04_*`, `test_upload.py` `test_d04_*` | 있음 |
| D-05 | root 밖은 지울 수 없다 (`..`는 400, 결정 2) | [[analysis/design-decisions]] 2 | U | 400 | `router_test.cpp` `d02_d03_*` | 있음. DELETE도 GET과 같은 정규화를 거친다. 정규화의 변이 확인은 R-01 |
| D-06 | 서버가 바꿀 수 없는 디렉토리 안의 파일 DELETE는 403 | raw/rfc9110.txt:7571-7572 | I | 403, 파일 그대로 (컨테이너는 root라 macOS에서만 의미 있음) | `test_upload.py` `test_d06_*` (root면 건너뜀) | 있음 |
| F-15 | 한 요청의 파일은 5개까지, 넘으면 413이고 아무것도 저장하지 않는다 | [[analysis/design-decisions]] 18, raw/rfc9110.txt:7710-7712 | I | 6개는 413, 5개는 201 | `test_upload.py` `test_f15_*` | 있음 |
| F-16 | multipart 파싱은 본문 크기에 비례하는 시간 안에 끝난다 (루프를 멈추지 않음) | raw/subject.md:139, 6단계 코드 리뷰 | U, I | 빈 줄 없는 part 약 1만 개인 1MB 본문이 2초 안에 400. 헤더가 구분자 CRLF에서 끝나는 part도 받는다 | `multipart_test.cpp` `f04_headersEndingAtTheDelimiter`, `test_upload.py` `test_f16_*` | 있음. 고치기 전 8.24초 |
| F-14 | 브라우저 폼으로 올린 파일을 다시 받는다 | raw/evaluation-sheet-en.md:82 | M | 같은 파일 | 사용자가 브라우저로 확인 (2026-10-18, 9단계 표 R-18·F-14 행) | 확인 |

일부러 틀리게 바꾼 확인 (2026-10-17): 통합 테스트 20개 변이(리뷰 뒤 추가한 빈 줄 찾기 범위·파일 수 상한·이름 길이 상한 포함, 쓰기 실패 무시, CRLF를 내용에 포함, 미디어 타입 검사 제거, 경로 버리기 제거, 기존 이름·겹치는 이름 검사 제거, 저장 위치 없는 POST 허용, 기본 허용에 POST·DELETE 추가, `std::remove` 생략, 디렉토리 삭제 허용, 권한 검사 제거, `Location` 매핑 검사 제거, 빈 `filename` 저장, 파일 없음 허용, 없는 파일 404 제거, DELETE 분기 제거, 409 본문의 이름 제거)와 단위 테스트 10개 변이(quoted-pair 처리, 같은 parameter 검사, padding 건너뛰기, preamble 찾기, boundary 길이·끝 공백, 마지막 구분자, 값 뒤 글자, disposition 두 번, `limit_except`가 기본값을 비우지 않음)가 모두 해당 테스트를 실패시켰다.

## 7. CGI

읽은 위키: [[analysis/implementation-plan]] 7단계, [[concepts/cgi]], [[analysis/design]] 4·5·9·10·12·14절, [[analysis/design-decisions]] 6·12, [[analysis/subject-vs-evaluation]] 1.4·1.7·1.9·1.11, [[concepts/security]] 2절, [[concepts/resilience]] 시그널 처리, [[sources/php-cgi-observed-env]]. 위키에 없던 선택은 [[analysis/design]] 9절 "구현 세부 (단계 7)"에 적는다.
CGI는 `G-`로 쓴다 (`C-`는 설정). 통합 테스트는 `test_cgi.py`이고, 스크립트는 테스트를 돌리는 Python(`sys.executable`)으로 실행한다. `php-cgi`는 Ubuntu 22.04 컨테이너에만 있다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| G-01 | 메타변수: 요청 전체와 인자가 CGI에 보인다. `PATH_INFO`는 디코딩, `QUERY_STRING`은 그대로, 같은 헤더는 `, `로 합치고, `Authorization`·`Content-Length`·`Content-Type`은 `HTTP_`로 넘기지 않는다. `Proxy`와 이름에 `_`가 든 헤더도 넘기지 않는다 (2026-10-29) | raw/subject.md:178, raw/rfc3875.txt:1044-1046, raw/rfc3875.txt:1052-1055, raw/rfc3875.txt:1051-1052, [[concepts/cgi]] 2절 | U, I | 변수 값 표 그대로. `HTTP_PROXY` 없음, `X_Forwarded_For`가 아니라 `X-Forwarded-For` 값 | `cgi_test.cpp` `g01_metaVariables`·`g01_addressAndPathText`, `router_test.cpp` `g01_g09_g10_scripts`, `test_cgi.py` `test_g01_*` | 있음 |
| G-02 | POST 본문은 스크립트의 표준 입력으로, `CONTENT_LENGTH`·`CONTENT_TYPE`과 함께 | raw/evaluation-sheet-en.md:90, raw/rfc3875.txt:1073-1075, raw/rfc3875.txt:637-640 | I | 본문과 길이가 그대로 | `test_cgi.py` `test_g02_*` | 있음 |
| G-03 | chunked 본문은 해제해 넘기고 `CONTENT_LENGTH`를 다시 계산한다 (MUST) | raw/subject.md:179, raw/rfc3875.txt:1093-1097 | I | 해제한 7바이트와 `CONTENT_LENGTH=7` | `test_cgi.py` `test_g03_*` | 있음 |
| G-04 | 스크립트는 자기 디렉토리에서 실행된다 | raw/subject.md:181, raw/evaluation-sheet-en.md:89, raw/rfc3875.txt:1565-1566 | I | 상대 경로 파일을 읽는다 | `test_cgi.py` `test_g04_*` | 있음 |
| G-05 | 무한 루프 스크립트: 다른 요청은 그동안 처리되고, 10초 뒤 504 | raw/evaluation-sheet-en.md:91-93, raw/rfc3875.txt:1255-1258, 설계 12절 | I | 다른 GET이 2초 안에 200, 루프는 10초 이상 뒤 504 | `test_cgi.py` `test_g05_*` (약 11초) | 있음 |
| G-06 | 출력이 CGI 응답이 아니면(출력 없이 종료, 헤더 아닌 줄, `Content-Type` 없는 문서 등) 502 | raw/rfc3875.txt:1295-1296, [[concepts/cgi]] 5절 | U, I | 502, 서버는 계속 응답 | `cgi_test.cpp` `g06_invalidOutputs`, `test_cgi.py` `test_g06_*` | 있음 |
| G-07 | `Status`는 상태 코드로, `Set-Cookie` 여러 줄은 그대로, 스크립트의 `Content-Length`·`Date`·`Connection`·`Transfer-Encoding`은 버린다(서버 값과 충돌, SHOULD 해결). `Keep-Alive`·`Proxy-Connection`·`TE`·`Upgrade`도 버린다 (2026-10-29, [[analysis/design]] 9절). 204·304는 본문을 버린다 | raw/rfc3875.txt:1295-1299, raw/rfc3875.txt:1496-1498, raw/rfc6265.txt:315-319, raw/rfc9110.txt:7042-7043, raw/rfc9110.txt:7477-7478, raw/rfc9110.txt:2604-2617 | U, I | 418, `Set-Cookie` 2줄, `Content-Length`·`Date` 1줄씩, 연결 단위 헤더 없음 | `cgi_test.cpp` `g07_documentResponse`, `test_cgi.py` `test_g07_*` | 있음 |
| G-08 | local redirect는 그 경로를 다시 처리하고(GET), client redirect는 302 (MUST). 자기 자신으로의 반복은 내부 리다이렉트 상한 뒤 500 | raw/rfc3875.txt:1310-1314, raw/rfc3875.txt:1324-1326, [[analysis/design-decisions]] 6 | U, I | 다른 스크립트의 출력, 302 + `Location`, 500 | `cgi_test.cpp` `g08_redirects`, `test_cgi.py` `test_g08_*` | 있음 |
| G-09 | index 파일이 CGI 확장자면 CGI로 실행 | [[analysis/design-decisions]] 6 | U, I | `/cgi/`가 `index.py`의 출력 | `router_test.cpp` `g01_g09_g10_scripts`, `test_cgi.py` `test_g09_*` | 있음 |
| G-10 | 스크립트는 `limit_except`가 허용한 메서드를 모두 받고(DELETE도 스크립트가 처리), 막힌 메서드는 405 + `Allow`. `cgi`가 없는 location의 `.py`는 실행하지 않고 파일로 보낸다 | 설계 9절, [[analysis/design-decisions]] 16 | U, I | DELETE가 스크립트에 가고 파일은 남는다. GET만 허용한 location의 POST는 405 + `Allow: GET, HEAD` | `router_test.cpp` `g01_g09_g10_scripts`, `test_cgi.py` `test_g10_*` | 있음 |
| G-11 | HEAD에는 본문을 보내지 않는다 (MUST discard) | raw/rfc3875.txt:1143-1145 | I | `Content-Length`는 GET 값, 본문 0바이트 | `test_cgi.py` `test_g11_*` | 있음 |
| G-12 | 큰 입력(3MB)과 출력(300KB)이 그대로 오간다. 출력이 16MB를 넘으면 502 | 설계 12절 `kMaxCgiOutputBytes` | I | 바이트 일치, 넘으면 502 | `test_cgi.py` `test_g12_*` | 있음 |
| G-13 | 본문을 읽지 않고 끝나는 스크립트에도 서버가 멈추거나 죽지 않는다 | [[concepts/cgi]] 1절 "입력 pipe", [[concepts/resilience]] SIGPIPE | I | 512KB 본문에도 200 | `test_cgi.py` `test_g13_*` | 있음 |
| G-14 | CGI 응답 뒤에도 연결을 유지한다(출력을 모은 뒤 `Content-Length`를 붙인다) | raw/rfc9112.txt:1372-1374 | I | 같은 연결에서 두 번 200 | `test_cgi.py` `test_g14_*` | 있음 |
| G-15 | 끝난 자식은 `waitpid(WNOHANG)`으로 회수해 좀비가 남지 않는다 | raw/posix-exit.md:58-64, [[concepts/cgi]] "자식 회수" | I | 요청 3개 뒤 서버의 자식 0개 (Linux `/proc`) | `test_cgi.py` `test_g15_*` | 있음 |
| G-16 | 스크립트가 도는 중 클라이언트가 RST로 끊으면 스크립트를 죽이고 회수한다 | 설계 4절 소유 관계 | I | 끊은 뒤 서버의 자식 0개 (Linux) | `test_cgi.py` `test_g16_*` | 있음 |
| G-17 | `php-cgi`로 GET·POST | raw/subject.md:182, [[concepts/cgi]] "php-cgi가 추가로 요구하는 변수" | I | `php GET hi`, `php POST data` | `test_cgi.py` `test_g17_*` (`/usr/bin/php-cgi`가 있을 때, Ubuntu 컨테이너) | 있음 |
| G-18 | `cgi` 지시자의 프로그램은 절대 경로여야 한다 (스크립트 디렉토리에서 실행하므로) | 설계 9절 | U | 설정 오류 | `config_test.cpp` `rejectsBadLocationDirectives` | 있음 |
| G-19 | 스크립트는 서버의 다른 fd(다른 클라이언트 소켓 등)를 물려받지 않는다 | raw/posix-fcntl.md:52, [[analysis/subject-vs-evaluation]] 1.11 | I | 스크립트의 `/dev/fd`에 0·1·2와 목록용 하나뿐 | `test_cgi.py` `test_g19_*` | 있음 |
| G-20 | SIGINT로 서버를 끄면 실행 중인 스크립트와 출력을 끝내고도 남은 스크립트를 모두 끝내고 회수한다 | [[concepts/resilience]] 시그널 처리, 설계 10절 | I | exit 0, 스크립트 프로세스가 남지 않음 (Linux) | `test_cgi.py` `test_g20_*` 2개 | 있음 |
| G-21 | 출력 pipe는 `POLLHUP`만 와도 `read()`해서 EOF를 확인한다 | raw/os-observed-pipe-poll.md:178, raw/os-observed-pipe-poll.md:193 | R | 코드 읽기 | `CgiStdout::onEvent` | 확인 (2026-10-18). `POLLIN` 없이 닫게 바꿔도 Ubuntu에서 G-12가 통과해 테스트로는 구별되지 않는다 |
| G-22 | 큰 CGI 출력이 응답이 되며 여러 번 복사되지 않는다 | 8절 R4 | I | 15MB 출력 하나에 최대 메모리 증가가 출력의 2.5배 미만 | `test_cgi.py` `test_g22_*` (Linux `VmHWM`) | 있음. 고치기 전 코드에서는 63MB 증가로 실패. 본문을 `swap` 대신 한 번 복사하게 바꾸면 그 복사가 잠깐만 있어 통과한다 (이 테스트는 약 4배로 돌아가는 것을 잡는다). 2026-10-23에 문서가 있는 클라이언트 리다이렉트(RFC 3875 6.2.4절, raw/rfc3875.txt:1330-1335) 15MB도 추가했다 (`test_g22_large_redirect_document_is_not_copied`) |

일부러 틀리게 바꾼 확인 (2026-10-18): fd 닫기 생략, 시간 초과 없앰, `Status` 무시, 스크립트 `Content-Length` 통과, 리다이렉트 상한 없앰, `chdir` 생략, 본문 쓰기 생략, `CONTENT_LENGTH` 생략, 스크립트 메서드 검사 생략, 출력 상한 없앰(macOS), 회수 생략, 연결 삭제 때 kill 생략, 종료 때 reaper의 kill·wait 생략(Ubuntu)이 모두 해당 테스트를 실패시켰다. 처음에는 스크립트 `Content-Length` 통과(G-07이 헤더를 dict로 읽음), 메서드 검사 생략(설정이 모든 메서드를 허용), reaper의 kill 생략(G-20의 루프 스크립트는 연결 삭제 때 이미 죽음)을 잡지 못해 테스트를 고쳤다.

## 8. 안정성 점검

읽은 위키: [[analysis/implementation-plan]] 8단계, [[concepts/resilience]] (요구 목록, 시그널, 누수 검사), [[concepts/testing]] siege 절, 이 페이지 2절의 N-07·N-10~N-12·N-22·N-23, [[sources/efence-observed-ubuntu2204]], [[sources/valgrind-observed-sigint]].
2절의 남은 줄(N-07, N-10, N-11, N-12, N-23)은 그 자리에서 고쳤다. 이 절은 절차와 코드 리뷰 결과다.

### 절차 (Ubuntu 22.04 컨테이너)

- valgrind로 통합 테스트 전체: `WEBSERV_WRAPPER="valgrind --quiet --error-exitcode=99 --leak-check=full --show-leak-kinds=all --errors-for-leak-kinds=all --track-fds=yes --log-file=/vg/%p.log" python3 -m unittest discover -s tests/integration`. 하네스는 각 서버를 SIGINT로 끄고 종료 코드 0을 요구하므로, 오류나 누수(still reachable 포함)가 있으면 그 테스트가 실패한다. 기록 파일의 fd 목록에서 표준 3개 말고 보이는 하나는 valgrind 자신의 기록 파일이다(부모에게서 상속).
- e_fence로 단위·통합 테스트 전체: `LD_PRELOAD=libefence.so.0.0 ./run_tests`, `WEBSERV_WRAPPER="env LD_PRELOAD=libefence.so.0.0" python3 -m unittest discover -s tests/integration`. `-lefence`로 빌드한 바이너리에는 `libefence`가 링크되지 않았다 (raw/efence-observed-ubuntu2204.md:389-395) → [[sources/efence-observed-ubuntu2204]]. 이미지에 `electric-fence` 2.2.6을 설치해 썼다. CGI 자식은 서버가 만든 환경만 받으므로 `LD_PRELOAD`가 넘어가지 않는다.
- siege: 서버를 띄우고 30초마다 `/proc/<pid>`에서 RSS·fd 수·자식 수를 적으며, siege를 포그라운드로 돌린다(백그라운드에서 멈춘 적이 있다, K-11). siege 4.0.7은 설정 파일이 없으면 요약을 JSON으로 낸다(소문자 키). 최장 응답 5.91초의 원인은 **미확인**(확인: 같은 부하에서 `ss -ltn`으로 listen 큐 넘침 확인).
- 시간 기준이 있는 테스트는 감쌌을 때 10배까지 늦어도 되게 했다 (`WRAPPER_SLOWDOWN`). F-16이 valgrind에서 2.78초 걸려 2초 기준을 넘었다.

### 결과 (2026-10-18)

| 점검 | 결과 |
|---|---|
| valgrind, 통합 테스트 103개 | 시간 기준 하나(F-16, 위)만 실패하고 모두 통과. 서버 기록 133개 모두 오류 0, 누수 0 |
| e_fence, 단위 102개 | 모두 통과 |
| e_fence, 통합 테스트 103개 | 모두 통과 (건너뜀 11개는 느린 테스트와 root 권한 시험) |
| siege 정적 5분 (`-b -c 50`, 빈 페이지) | 1,355,986건, availability 100%, 실패 0, 최장 5.91초 |
| siege 혼합 3분 (정적·100KB 파일·Python CGI·404) | 105,100건, availability 100%, 실패 0, 최장 1.00초 |
| 서버 상태 (30초마다) | RSS 1.7~2.7MB에서 늘지 않음. 끝난 뒤 fd 4개, CGI 자식 0개, SIGINT로 exit 0 |
| 다시 점검 (2026-10-29, webserv `13982df`, 로그 기능 뒤) | valgrind 아래 단위 105개·통합 124개 통과(건너뜀 17개: 느린 테스트, root 권한 시험, 감싼 실행에서 빼는 N-26·G-22). 기록 160개 중 서버 기록 106개는 모두 오류 0, 누수 0, 끝날 때 fd는 표준 3개와 valgrind 기록 파일뿐(로그 파일 두 개도 닫힘). 나머지 54개는 빈 기록이다. CGI 자식이 `execve`로 바뀌어 valgrind가 추적을 그만둔 것으로 본다 (**판단**). siege 60초(`-b -c 50`, 빈 페이지) 1,664,629건, availability 100%, RSS 3.2MB → 2.3MB, fd 수 변화 없음, 접근 로그 120MB |

### 코드 리뷰 (안정성)

| # | 위치 | 문제 | 처리 |
|---|---|---|---|
| R1 | `CgiProcess::runChild` | `fork` 뒤 자식에서 예외(`bad_alloc`)가 나면 서버 코드로 풀려 나가 자식이 두 번째 서버처럼 같은 소켓을 처리한다 | 자식 코드 전체를 잡아 `std::exit(1)` (webserv `d4ce794`) |
| R2 | `~CgiProcess` | `reaper_.adopt`의 `push_back`이 던지면 소멸자에서 예외가 나가 `std::terminate`될 수 있다 | 잡아서 `SIGKILL` 후 그 자리에서 `waitpid` |
| R3 | `ChildReaper::reap` | 매 바퀴 vector를 할당하는데, 연결별 예외 처리 밖이라 실패하면 서버가 끝난다 | 할당 없이 제자리에서 지운다 |
| R4 | CGI 출력 → 응답 | 출력(최대 16MB)이 pipe 버퍼, `substr`, `CgiOutput` 복사, `ProcessOutcome` 복사로 약 4벌이 됐다. 메모리가 바닥나면 예외 없이 프로세스가 끝난다 (raw/design-checks-observed.md:119-123) | 본문을 `swap`으로 옮긴다 (webserv `6b4ffc2`). 15MB 출력 하나의 최대 메모리 증가가 63MB에서 약 31MB로 줄었다(G-22). 남은 한 벌은 전송 버퍼. 문서가 있는 클라이언트 리다이렉트 경로는 이 수정에서 빠져 본문을 두 번 더 복사했다(`redirectOutput`에서 한 번, 결과 대입에서 한 번). 2026-10-23에 종류만 정하는 `redirectKind`로 바꿔 복사를 없앴다 (webserv `8f8dc8a`). Ubuntu에서 잰 최대 메모리 증가는 고치기 전에도 출력의 2.0배로 문서 경로와 같았다. 늘어난 복사본이 전송 버퍼가 생기기 전에 해제되기 때문이다(**판단**). 그래서 이 수정은 15MB 복사 두 번의 시간을 줄이고 주석과 코드를 맞춘 것이고, 새 G-22 테스트는 이 복사가 돌아오는 것은 잡지 못한다 |
| R5 | `Listener::onEvent` | fd가 다 차서 `accept`가 실패하면 listen 소켓이 계속 읽기 가능이라 루프가 쉬지 않고 돈다 | `accept`가 실패하면 listener를 멈추고, 연결이 닫히거나 1초가 지나면 다시 poll한다 (`6b4ffc2`, N-26). 원인은 errno로 가리지 않는다 (1.8절). Ubuntu 22.04 systemd 패키지의 기본 한도는 soft 1024 (raw/ubuntu2204-observed-nofile.md:16) → [[sources/ubuntu2204-observed-nofile]]. 평가 PC 셸의 실제 값은 **미확인**(확인: `ulimit -n`). 개발 컨테이너는 Docker 기본 20480 |

R1~R3은 실패를 만들 방법이 없어 코드 읽기로 확인했다(2026-10-18). R4·R5는 처음에 기록만 하려다 사용자 지적으로 고쳤다. 고친 뒤 siege 60초(`-b -c 50`)가 323,246건, availability 100%였다.
감싼 실행(`WEBSERV_WRAPPER`)에서는 측정 테스트 N-26(감싸는 도구도 fd가 필요)과 G-22(도구의 메모리가 서버 것으로 잡힘)를 건너뛴다.

## 9. README와 시연 준비

읽은 위키: [[analysis/implementation-plan]] 9단계, [[concepts/build-and-submission]], [[concepts/bonus]], [[concepts/testing]] 시연 준비, [[concepts/cgi]] 6절(Python 스크립트), raw/evaluation-sheet-en.md:33-130(평가 항목 전체).
시연 자료는 webserv `83f413c`: `www/`, `www2/`, `conf/default.conf`·`ports.conf`·`same-port.conf`, README. `test_demo.py`는 저장소의 설정을 포트만 바꿔 저장소 루트에서 띄운다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| E-01 | 같은 `interface:port`의 두 사이트는 설정 오류(virtual host 미구현). 여러 interface·port에 서로 다른 사이트 | raw/evaluation-sheet-en.md:107-108, [[analysis/design-decisions]] 4 | I | `same-port.conf`는 `duplicate listen`, 종료 코드 1. `ports.conf`는 주소마다 다른 사이트 | `test_demo.py` `test_e01_*` 2개 (`127.0.0.2`는 Linux만) | 있음 |
| E-02 | 정적 웹사이트(HTML, CSS, 그림) | raw/subject.md:145, raw/evaluation-sheet-en.md:99 | I | 200과 알맞은 `Content-Type` | `test_e02_static_site` | 있음 |
| E-03 | 설정 항목: 디렉토리 목록, 다른 디렉토리로의 route와 그 index, 리다이렉트, 바꾼 404 페이지, 권한 없는 DELETE, 다른 포트의 사이트 | raw/evaluation-sheet-en.md:69-73, raw/evaluation-sheet-en.md:100-102 | I | 200·301·404(사용자 페이지)·405 | `test_e03_configuration_features` | 있음 |
| E-04 | 평가표의 본문 크기 시험 명령 (`Content-Type: plain/text`, 짧은 본문과 긴 본문) | raw/evaluation-sheet-en.md:70 | I | 짧으면 CGI가 받은 본문을 돌려주고, 64바이트를 넘으면 413 | `test_e04_body_limit` | 있음 |
| E-05 | 업로드한 파일을 다시 받고 지운다 | raw/evaluation-sheet-en.md:82 | I | 201 → 200(같은 내용) → 204 → 404 | `test_e05_upload_get_delete` (지우지 못하면 정리 단계에서 지운다) | 있음 |
| E-06 | CGI: GET, POST, 상대 경로, 메타변수, 에러 스크립트 502, 무한 루프 504 | raw/evaluation-sheet-en.md:88-93 | I | 각 결과 | `test_e06_cgi`, `test_e06_infinite_loop` (느린 테스트) | 있음 |
| E-07 | 쿠키·세션 (보너스): 식별자만 쿠키에, 모르는 식별자는 새로 발급, 로그아웃은 과거 날짜 `Expires` | raw/evaluation-sheet-en.md:126, raw/subject.md:215, [[concepts/bonus]] 세션 | I | 방문 수 1 → 2, 위조한 식별자는 새 세션, 로그아웃 쿠키 만료 | `test_e07_cookie_session` | 있음. 식별자는 Python `secrets`로 만든다. 스크립트 언어의 난수 기능이 허용 함수 목록의 대상인지는 결정 8의 **미확인** 그대로 |
| E-08 | 여러 CGI (보너스): Python과 PHP | raw/subject.md:216, raw/evaluation-sheet-en.md:130 | I | PHP 페이지 200 | `test_e08_php` (`/usr/bin/php-cgi`가 있을 때) | 있음 |
| E-09 | README: 이탤릭 첫 줄, Description·Instructions·Resources, AI를 어떤 작업·부분에 썼는지 | raw/evaluation-sheet-en.md:35-44, raw/subject.md:196-207 | I, M | 형식은 B-06. 내용은 사람이 읽는다 | `test_readme.py` (형식). README의 curl 명령은 2026-10-18 macOS에서 실행해 적힌 결과를 확인(`loop.py`, PHP, siege 제외) | 형식 있음. 내용은 사용자가 확인 (2026-10-18) |
| E-10 | siege 시험용 빈 페이지가 저장소에 있다 | raw/evaluation-sheet-en.md:114 | I | `/empty.html`이 200, `Content-Length: 0`, 본문 없음. README의 siege 명령이 이 페이지를 쓴다 | `test_demo.py` `test_e10_empty_page_for_siege` | 있음 (2026-10-27, webserv `5ca93a2`). 파일을 지우면 실패한다 |
| R-18, F-14 | 브라우저로 정적 사이트를 끝까지 보고, 폼으로 업로드한 파일을 다시 받는다. 네트워크 탭의 요청·응답 헤더 | raw/evaluation-sheet-en.md:97-103, raw/evaluation-sheet-en.md:82 | M | 페이지, 404, 목록, 리다이렉트가 보이고 업로드한 파일이 같다 | 사용자가 브라우저로 확인 (2026-10-18) | 확인 |

- 시연 자료의 판단: 사이트 루트는 `limit_except` 없이 읽기 전용(결정 16)이고, 업로드한 `.py`는 `cgi`가 없는 `/upload/`에 저장되어 실행되지 않는다 ([[analysis/design-decisions]] 7). 본문 크기 시험은 평가표 명령이 `plain/text` 본문이라 업로드(415)가 아닌 본문을 돌려주는 CGI(`/limit/echo.py`, 상한 64바이트)로 보인다.
- `127.0.0.2`는 Ubuntu 22.04 컨테이너에서 바로 bind되고 macOS에서는 `Can't assign requested address`였다(2026-10-18 실행). 평가는 Ubuntu에서 한다.

## 10. 운영 로그

읽은 위키: [[analysis/design-decisions]] 19, [[analysis/design]] 11절, raw/subject.md:134-136 (일반 파일은 `poll()` 예외).
구현은 webserv `13982df`. 로그 줄은 `[IMF-fixdate] 내용` 형식이다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| L-01 | 응답마다 접근 로그 한 줄: 클라이언트 주소, 클라이언트가 보낸 요청 줄, 상태, 본문 바이트(HEAD는 0). 오지 않은 부분은 `-`. 제어 문자는 `?`로 바꿔 한 줄을 지킨다 | 결정 19 | U, I | `127.0.0.1 "GET / HTTP/1.1" 200 15` | `logger_test.cpp` 3개, `test_logs.py` `test_l01_*` 2개 | 있음 |
| L-02 | 시작과 (SIGINT로) 종료를 오류 로그에 남긴다 | 결정 19 | I | `started: <설정 경로>`, `shutting down` | `test_l02_start_and_stop_are_logged` | 있음 |
| L-03 | CGI의 잘못된 출력(502)·시간 초과(504)를 오류 로그에 남긴다 | 결정 19 | I | `CGI response invalid: /cgi/garbage.py (502)`, `CGI timed out and was killed: /cgi/loop.py (504)` | `test_l03_*` 2개 (시간 초과는 느린 테스트) | 있음 |
| L-04 | 로그 파일을 열 수 없으면 시작하지 않는다 | 결정 19 | I | 종료 코드 1, `cannot open log files` | `test_l04_missing_log_directory_stops_startup` | 있음 |
| L-05 | 끝나지 않은 요청(408), 멈춘 전송, CGI 시작 실패(500), `accept()` 실패를 오류 로그에 남긴다 | 결정 19 | R | 코드 읽기: `Connection::checkTimeout`, `RequestProcessor::startCgi`, `Server::acceptFailed` | 없음 (30초 시간 제한·fd 고갈을 만들어야 함) | 코드 읽기만 |

- 결과 (2026-10-29): macOS 단위 105, Ubuntu 22.04 단위 105와 통합 124(느린 테스트 포함, root라 2개 건너뜀) 통과.
