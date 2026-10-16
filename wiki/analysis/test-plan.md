---
title: 테스트 계획
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/nginx-core-module.md, raw/macos-observed-sigpipe-leaks.md, raw/posix-poll.md, raw/design-checks-observed.md, raw/posix-recv.md, raw/rfc9112.txt, raw/rfc9110.txt, raw/rfc6585.txt, raw/rfc1945.txt, raw/rfc3986.txt]
updated: 2026-10-17
---

# 테스트 계획

요구사항을 한 줄에 하나씩 적고, 무엇으로 어떻게 확인하는지 정한다. 테스트는 이 표에서 나온다. 표에 없는 테스트는 왜 있는지 설명할 수 있어야 하고, 테스트가 없는 줄은 빈칸으로 드러난다.
구현 단계는 [[analysis/implementation-plan]], 설계는 [[analysis/design]], 사용자 결정은 [[analysis/design-decisions]]에 있다.

## 진행 방식

- 단계를 시작할 때 그 단계의 줄을 먼저 채우고, 테스트를 쓴 뒤 구현한다. 지금은 0~2단계를 자세히 적었고, 3단계 이후는 항목만 있다.
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
| B-03 | `c++ -Wall -Wextra -Werror`로 컴파일되고, `-std=c++98`을 더해도 컴파일된다 | raw/subject.md:49-50 | I | macOS·Ubuntu 모두 `make re` 성공 | `test_build.py` `test_b01_b03_rules_build_and_clean`이 컴파일 명령의 플래그를 확인 (느린 테스트) | 있음. Ubuntu 빌드는 컨테이너에서 돌린다 |
| B-04 | C++ 버전이 있으면 C 헤더 대신 쓴다. 외부 라이브러리·Boost 금지 | raw/subject.md:51-52 | R | `.h` 헤더는 C++ 버전이 없는 POSIX 헤더뿐. 링크에 `-l` 없음 | 코드 읽기 2026-10-16: `.h`는 `arpa/inet.h`, `fcntl.h`, `netinet/in.h`, `poll.h`, `sys/socket.h`, `sys/stat.h`, `unistd.h`뿐 | 확인. 단계마다 다시 본다 |
| B-08 | 허용 함수 목록에 없는 C 함수(`memset`·`strchr`·`strlen`·`<cctype>` 등)를 쓰지 않는다. 시스템 호출은 목록 안의 것만. 목록이 표준 라이브러리에도 적용되는지는 **미확인**이라 엄격한 쪽을 따른다 | raw/subject.md:111-113, raw/subject.md:51, [[analysis/subject-vs-evaluation]] 1.4 | R, U | 호출하는 외부 함수 목록이 허용 목록 안 | 코드 읽기 2026-10-17: 시스템 호출은 목록 안의 것만. C 함수는 `strerror`(목록 안)만 남고, 문자 판별은 `http/Ascii`, 문자열 길이·검색은 `std::string`, 구조체 초기화는 값 초기화. `ascii_test.cpp` 2개 | 있음 |
| B-05 | 다른 웹 서버를 `execve`하지 않는다 | raw/subject.md:128 | R | `execve`는 CGI 실행에만 | 아직 `execve` 없음 | 나중 (7단계) |
| B-06 | README: 저장소 루트, 영어, 첫 줄 이탤릭 정해진 문구, Description·Instructions·Resources(AI 사용 포함). 하나라도 없으면 0점 | raw/subject.md:196-207, raw/evaluation-sheet-en.md:35-44 | I, M | 형식은 테스트, 내용은 9단계에 읽어서 확인 | `test_readme.py` 2개 (첫 줄 형식, 세 절) | 있음(형식). 내용은 9단계. 첫 줄 login은 `yoshin, jyoo` (사용자 확인, 2026-10-16) |
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
| C-17 | 라우트별 허용 메서드 (`limit_except ... { deny all; }`). GET을 허용하면 HEAD도. 없으면 전부 허용 | raw/subject.md:167, raw/evaluation-sheet-en.md:73, 설계 3절 | U | 허용 집합. 블록 안 다른 내용·모르는 메서드는 거부 | `parsesDesignExample`, `rejectsBadLocationDirectives` | 있음 |
| C-18 | HTTP 리다이렉트 (`return 코드 URL`) | raw/subject.md:168 | U | 코드와 URL. 301·302·303·307·308이 아니면 거부 (설계) | `parsesDesignExample`, `rejectsBadLocationDirectives` | 있음 |
| C-19 | 파일을 찾을 디렉토리 (`root`, subject 예시는 `alias`). 한 location에 둘 다 있으면 거부. 둘 다 없고 `return`도 없으면 거부 | raw/subject.md:169, 설계 3절 | U | 값 저장과 거부 | `parsesDesignExample`, `rejectsLocationProblems` | 있음 |
| C-20 | 디렉토리 리스팅 켜기·끄기 (`autoindex`), 기본 off | raw/subject.md:170 | U | `on`/`off`만 받는다 | `defaultsWhenNotConfigured`, `locationInheritsServerSettings`, `rejectsBadLocationDirectives` | 있음 |
| C-21 | 디렉토리 요청 때 줄 기본 파일 (`index`), 기본 `index.html` | raw/subject.md:171, raw/evaluation-sheet-en.md:72 | U | 파일 목록 | `defaultsWhenNotConfigured`, `locationInheritsServerSettings` | 있음 |
| C-22 | 업로드 허용과 저장 위치 (`upload_store`) | raw/subject.md:172 | U | 경로 저장 | `parsesDesignExample` | 있음 |
| C-23 | 확장자별 CGI (`cgi .확장자 실행파일`) | raw/subject.md:173 | U | 확장자→실행 파일. `.` 없는 확장자, 중복은 거부 | `parsesDesignExample`, `rejectsBadLocationDirectives` | 있음 |
| C-24 | location은 server 값을 물려받고, 자기 값이 있으면 그것을 쓴다 | 설계 3절 | U | 상속과 덮어쓰기 | `locationInheritsServerSettings` (상속), `locationOverridesServerSettings` (덮어쓰기) | 있음 |
| C-25 | location `/`가 없고 server에 `root`가 있으면 `/`를 만든다. `root`도 없으면 만들지 않는다 | 설계 3절 | U | 있음/없음 | `serverRootCreatesImplicitRootLocation`, `noImplicitRootLocationWithoutServerRoot` | 있음 |
| C-26 | location은 긴 경로부터 정렬 (4단계 가장 긴 prefix 매칭의 준비) | 설계 7절 `matchLocation` | U | 경로 길이 내림차순 | `locationsAreSortedLongestFirst` | 있음. 매칭 자체는 4단계에서 시험 |
| C-28 | 비정상적으로 깊게 중첩된 설정 파일에도 크래시하지 않는다. 유효한 중첩은 server > location > limit_except 3단계 | raw/subject.md:46, 설계 3절 | U, I | 깊이 4부터 설정 오류, 10만 단계도 종료 코드 1 | `rejectsBlocksNestedTooDeeply`, `test_startup.py` `test_c28_deeply_nested_config_does_not_crash` (10만 단계) | 있음. 고치기 전 10만 단계에서 종료 코드 139 |
| C-29 | `index` 값에 `/`가 들어가면 설정 오류 (root 밖을 가리키지 못하게) | [[concepts/security]] 1절, 설계 | U | `index ../x;`는 오류 | `config_test.cpp` `c29_rejectsIndexNamesWithSlash` | 있음 |
| C-27 | 평가 시연용 설정 파일과 기본 파일을 저장소에 둔다 | raw/subject.md:184 | M | 기능별 설정으로 시연 가능 | 9단계 | 나중 |

## 2. 이벤트 루프와 연결

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| N-01 | 모든 I/O를 `poll()` 하나로 처리하고, 읽기·쓰기를 함께 감시한다 | raw/subject.md:130-131, raw/evaluation-sheet-en.md:53 | R | `poll` 호출이 `EventLoop::run` 한 곳뿐 | 코드 읽기 2026-10-16: `poll`은 `src/core/EventLoop.cpp:42` 한 곳. 감시할 이벤트는 handler마다 `wantedEvents()`로 정해 한 배열에 읽기·쓰기가 함께 들어간다 | 확인 |
| N-02 | 준비 알림 없이 소켓을 읽거나 쓰지 않는다. 준비 1회에 I/O 1번은 설계(원문은 EAGAIN까지 반복도 허용) | raw/subject.md:132, raw/subject.md:136, raw/evaluation-sheet-en.md:54 | R | `recv`·`send`·`accept`가 `onEvent` 경로에서만 불린다 | 코드 읽기 2026-10-16: `recv`는 `src/http/Connection.cpp:68`, `send`는 `:84`, 각각 `onEvent`의 `POLLIN`·`POLLHUP`(`:46`)·`POLLOUT`(`:48`) 확인 뒤에만 불린다. `accept`는 `src/core/Listener.cpp:63`, `POLLIN` 확인(`:59`) 뒤. 시계 파일 `write`는 일반 파일이라 예외 (raw/subject.md:134) | 확인 |
| N-03 | 읽기·쓰기 뒤 errno로 동작을 바꾸지 않는다 | raw/subject.md:133, raw/evaluation-sheet-en.md:57 | R | `recv`·`send` 뒤에 errno를 읽는 곳이 없다 | 코드 읽기 2026-10-16: `recv`·`send` 뒤에 errno를 읽지 않는다. errno는 `src/core/Listener.cpp:50`에서 시작 때 listen 소켓 준비(`socket`~`listen`) 실패 메시지에만 쓴다 | 확인 |
| N-04 | `recv`·`send` 반환값 0과 -1을 모두 처리하고, 에러면 클라이언트를 제거한다 | raw/evaluation-sheet-en.md:55-56 | R, I | 코드에 두 경우가 있고, 클라이언트가 끊으면 연결이 정리된다 | 코드 읽기: `src/http/Connection.cpp:70`, `:85`가 0과 -1을 모두 닫기로 처리. `test_connections.py` `test_n04_peer_close_releases_the_socket` (Linux `/proc`에서 서버의 fd 수 확인, macOS에서는 건너뜀) | 있음 |
| N-05 | 여러 포트에서 서로 다른 server로 응답한다 | raw/subject.md:149, raw/evaluation-sheet-en.md:107 | I | 두 포트에 동시에 요청해 모두 응답 | `test_connections.py` `test_n05_concurrent_clients_on_two_ports` (50개) | 있음. 포트별로 다른 내용은 4단계에서 시험 |
| N-06 | 다른 프로세스가 이미 쓰는 `interface:port`면 메시지를 내고 끝낸다. 크래시하지 않는다 | raw/evaluation-sheet-en.md:109 | I | 두 번째 프로세스가 `Address already in use`, 종료 코드 1. 첫 프로세스는 계속 응답 | `test_startup.py` `test_n06_second_instance_on_same_port_fails_cleanly` | 있음 |
| N-07 | 클라이언트가 요청 도중·응답 도중 끊어도 서버는 계속 동작한다 (`SIGPIPE`로 죽지 않음) | raw/subject.md:46, raw/subject.md:129 | I | 끊은 뒤 새 요청에 응답 | `test_connections.py` `test_n07_*` 2개 (요청 도중 끊김, 응답 전 RST) | 부족: `SIGPIPE` 무시를 지워도 테스트가 실패하지 않았다. 상대가 닫은 TCP 연결에 `send`하면 1회차는 성공하고 2회차에 프로세스가 끝났다는 실측이 있다 (raw/macos-observed-sigpipe-leaks.md:114-117, [[sources/macos-observed-sigpipe-leaks]]). 고정 응답은 `send` 1번에 끝나므로 2회차가 없다. 4단계에서 끊긴 연결에 여러 번 보내는 큰 응답으로 시험 |
| N-08 | 요청이 무한히 매달리지 않는다: 머리가 끝나지 않은 연결은 헤더 타임아웃 뒤 닫힌다 | raw/subject.md:139 | I | 30초 뒤 연결이 닫힌다 (3단계부터는 408) | `test_connections.py` `test_n08_unfinished_head_gets_408` (느린 테스트, 약 30초) | 있음. 3단계부터 408 |
| N-09 | 머리가 상한을 넘으면 연결을 닫는다 (3단계부터는 431) | 설계 12절 `kMaxHeaderBytes` | I | 16384바이트를 넘게 보내면 닫힌다 | `test_connections.py` `test_n09_oversized_head_gets_431` | 있음. 3단계부터 431 |
| N-10 | `SIGINT`·`SIGTERM`이면 모든 fd와 메모리를 정리하고 정상 종료한다 | 설계 10절. 누수 검사 raw/evaluation-sheet-en.md:25 | I, M | 종료 코드 0. valgrind "All heap blocks were freed" | `test_startup.py` `test_n10_*` 2개 (종료 코드). valgrind는 단계 2에서 손으로 확인 | 부족: valgrind 확인 기록이 커밋 메시지뿐. 8단계에서 절차로 남긴다 |
| N-11 | `siege -b`로 빈 페이지 GET availability 99.5% 초과 | raw/evaluation-sheet-en.md:114 | M | 99.5% 초과 | 없음 (단계 2에서 100% 확인, 기록은 커밋 메시지·대화뿐) | 부족: 8단계에서 절차로 남긴다 |
| N-12 | 계속 돌려도 메모리가 끝없이 늘지 않고 매달린 연결이 없다 | raw/evaluation-sheet-en.md:115-117 | M | 장시간 siege 동안 메모리 일정 | 8단계 | 나중 |
| N-13 | 시계: 시계 파일의 수정 시각을 현재 시각으로 쓴다. 시작 때 실패하면 시작하지 않는다 | [[analysis/design-decisions]] 10, 설계 4절 "시계" | U, I | 갱신 성공 시 값이 0보다 크고 줄지 않는다. 쓸 수 없는 경로면 `refresh()`가 false | `clock_test.cpp` 2개, `test_startup.py` `test_n13_unusable_clock_file_stops_startup` | 있음 |
| N-14 | 이벤트 루프: 처리 중 `unwatch`는 그 바퀴 끝에 반영. `onEvent` 예외는 그 handler의 `onFailure()`로 | 설계 4절 | U | pipe fd와 가짜 handler로 확인 | `event_loop_test.cpp` 3개 | 있음 |
| N-15 | IPv4 주소 변환 (listen 주소 → `sockaddr_in`). 접속한 주소 → 문자열은 7단계에서 다시 | 설계 (구현 세부) | U | 네트워크 바이트 순서 | `parsesIpv4`, `buildsSockaddrInNetworkOrder` (`tests/unit/socket_address_test.cpp`) | 있음 |
| N-16 | 모든 소켓은 non-blocking | raw/subject.md:129 | R | listen 소켓과 accept한 소켓 모두 `O_NONBLOCK` | 코드 읽기 2026-10-16: `src/core/Listener.cpp:48`(listen, `bind`·`listen` 뒤에 켬), `:69`(accept한 소켓, 실패하면 닫음) | 확인 |
| N-17 | `fcntl`은 `F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC`만 | raw/subject.md:155-157 | R | 다른 플래그 없음 | 코드 읽기 2026-10-16: `fcntl` 호출은 위 두 곳, 둘 다 `F_SETFL, O_NONBLOCK` | 확인 |
| N-18 | `poll()`이 메인 루프 안에 있다 | raw/evaluation-sheet-en.md:53 | R | `main` → `EventLoop::run` → `poll` | 코드 읽기 2026-10-16: `src/main.cpp:49` `loop.run(server)`, `run`이 매 바퀴 `poll` | 확인 |
| N-19 | `POLLOUT`은 보낼 데이터가 있을 때만 켠다 (안 그러면 busy waiting) | raw/posix-poll.md:175, [[concepts/io-multiplexing]] "POLLOUT은 보낼 데이터가 있을 때만" (**판단**) | R, I | 연결이 대기 중이어도 서버가 CPU를 거의 쓰지 않는다 | 코드 읽기: `src/http/Connection.cpp:33` `wantedEvents`는 `WRITE` 상태에서만 `POLLOUT`. `test_connections.py` `test_n19_idle_connections_do_not_spin` (Linux `/proc`에서 CPU 시간 확인: 대기 연결 10개, 2초 동안 0.2초 미만) | 있음 |
| N-20 | `POLLERR`·`POLLNVAL`이면 클라이언트를 제거 | raw/evaluation-sheet-en.md:55, [[concepts/io-multiplexing]] "revents 처리" | R | 연결을 닫는다 | 코드 읽기 2026-10-16: `src/http/Connection.cpp:40` | 확인 |
| N-21 | 디스크 파일의 동기 I/O가 루프를 멈추지 않는다 | raw/evaluation-sheet-en.md:59 | R | 설정 파일은 시작 때만, 시계 파일은 바퀴마다 1바이트 | 코드 읽기 2026-10-16: `src/main.cpp:34` 시작 때 설정 읽기. 시계는 `Clock::refresh` | 확인. 4단계 정적 파일에서 다시 본다 |
| N-22 | 메모리가 부족해도 크래시하지 않는다 | raw/subject.md:46 | R, M | 할당 실패가 예외로 오면 그 연결만 정리 | 코드 읽기: `Server::adopt`가 생성 실패를 잡고, `onEvent` 예외는 `onFailure`로 간다 (N-14). 다만 Ubuntu 컨테이너에서 메모리가 바닥나면 `bad_alloc` 없이 프로세스가 강제 종료됐다 (raw/design-checks-observed.md:119-123) | 부족: 예외가 오지 않는 경우는 본문 상한(결정 11)으로만 막는다 |
| N-24 | 헤더 수신 타임아웃은 받기 시작한 때부터 잰다. 바이트를 조금씩 계속 보내도 연장되지 않는다 (본문·전송은 무입력·무진행 기준) | raw/subject.md:139, 설계 12절 | I | 5초마다 1바이트씩 보내도 약 30초 뒤 408 | `test_connections.py` `test_n24_trickled_head_still_times_out` (느린 테스트, 5초마다 1바이트) | 있음 |
| N-25 | 이벤트 처리 밖(타임아웃 점검, poll 목록 만들기)에서 난 예외도 프로세스를 비정상 종료시키지 않는다. 연결 하나에서 나면 그 연결만 닫고, 그 밖이면 원인을 출력하고 종료 코드 1 | raw/subject.md:46, raw/evaluation-sheet-en.md:24 | R | `Server::afterIteration`이 연결마다 예외를 잡고, `main`이 마지막으로 잡는다 | 코드 읽기 + 예외 주입 실험 2026-10-17: 타임아웃 점검에서 던지면 그 연결만 닫히고 새 요청은 200, poll 처리에서 던지면 `webserv: stopped: ...`와 종료 코드 1 | 확인 |
| N-23 | 평가자가 `valgrind`·`leaks`·`e_fence`로 돌려도 오류·누수가 없다. `e_fence`에서는 heap 경계 오류가 곧 크래시 | raw/evaluation-sheet-en.md:25, [[concepts/resilience]] "SIGINT·SIGTERM과 누수 검사" | M | valgrind 오류 0, "All heap blocks were freed" | 단계 2에서 valgrind만 손으로 확인 | 나중 (8단계 절차) |

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
| P-18 | CL만큼 오기 전에 끊기거나 타임아웃이면 불완전한 요청. 머리·본문 수신 타임아웃이면 408 후 닫기(MAY). 첫 바이트 전이면 그냥 닫기 | raw/rfc9112.txt:973-978, raw/rfc9112.txt:1253-1255, raw/rfc9110.txt:7641-7643, 설계 5절 | I | 408 후 닫힘 (느린 테스트) | `test_requests.py` `test_p18_*` 2개 (본문 도중 408, 아무것도 안 보낸 연결은 응답 없이 닫힘), `test_connections.py` `test_n08_unfinished_head_gets_408` (모두 느린 테스트) | 있음 |
| P-19 | 오류 응답의 상태줄 `HTTP-version SP status-code SP reason-phrase`, 문법 오류 뒤에는 연결을 닫는다(SHOULD) | raw/rfc9112.txt:652, raw/rfc9112.txt:690-693, raw/rfc9112.txt:319-324 | I | 상태줄과 `Connection: close`, 그 뒤 닫힘 | `test_requests.py` `test_p19_error_response_format_and_close` | 있음. 오류 응답 본문은 임시(코드와 reason phrase). 에러 페이지는 4단계 |
| P-21 | 파서 비용이 입력 길이에 비례한다. 작은 chunk가 많아도 recv 1번 처리가 루프를 오래 붙잡지 않는다 | raw/subject.md:148 (항상 가용). 파서 비용과 잇는 것은 **판단** | M | 1바이트 chunk 6MB 처리 CPU 시간 | 측정 (scratch 벤치마크, 최적화 없는 빌드): 1바이트 chunk 6MB가 1.6초 → 0.2초 (2026-10-16) | 확인. 테스트로 남기지 않음(시간 측정은 기계마다 다르다) |
| P-20 | telnet·curl로 시연할 수 있다 | raw/evaluation-sheet-en.md:77 | M | 시연 절차 | 없음 | 나중 (9단계) |

## 4. 라우팅, 정적 파일, 응답

읽은 위키: [[analysis/implementation-plan]] 4단계, [[analysis/design]] 1·2·7·8절, [[concepts/http-features]], [[concepts/configuration-file]], [[concepts/security]] 1절, [[concepts/status-codes]], [[sources/nginx-observed-directory]]. 위키에 없던 선택은 [[analysis/design]] 7절 "구현 세부"에 적는다.

| ID | 요구사항 | 근거 | 수준 | 기대 결과 | 현재 테스트 | 상태 |
|---|---|---|---|---|---|---|
| R-01 | 경로 정규화: 세그먼트로 나눈 뒤 `%XX`를 한 번만 디코딩, 잘못된 `%`·`%00`·`%2F`는 400, 연속 `/` 합치기, `.`·`..` 제거, 루트 위로 가면 400 + 닫기 | raw/rfc3986.txt:647-652, raw/rfc3986.txt:767-771, raw/rfc3986.txt:2443-2445, raw/rfc3986.txt:689-691, [[concepts/security]] "경로 정규화 절차", [[analysis/design-decisions]] 2·3 | U, I | 정규화 결과와 400 | `path_resolver_test.cpp` 6개, `router_test.cpp` `r01_r02_*`, `test_static.py` `test_r01_bad_paths_are_400` | 있음 |
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
| R-18 | 정적 웹사이트를 브라우저로 끝까지 본다 | raw/subject.md:145, raw/evaluation-sheet-en.md:99 | M | 시연용 `www/` | 없음 | 나중 (9단계 시연 자료와 함께) |
| R-20 | alias를 쓰는 location은 떼고 남은 경로가 비었거나 `/`로 시작할 때만 그 location의 파일로 본다. 아니면 404 ([[analysis/design-decisions]] 14) | raw/rfc9110.txt:8560-8565, [[concepts/security]] 1절 | U, I | `location /kapouet { alias www/; }`에서 `/kapouet../secret/s.txt`가 404 | `router_test.cpp` `r20_aliasCoversOnlyWholeSegments`, `test_static.py` `test_r20_alias_cannot_reach_outside` | 있음. 고치기 전에는 alias 밖 파일이 200 |
| R-21 | HEAD 요청에는 오류 응답(파서 오류, 408)에도 본문을 보내지 않는다 (MUST NOT) | raw/rfc9110.txt:3987-3988 | I | HEAD에 413: 헤더만 오고 본문 0바이트 | `test_requests.py` `test_r21_head_error_has_no_body` | 있음 |
| R-19 | 4단계에서 POST·DELETE는 정적 리소스에 대해 405 (업로드·삭제는 6단계) | 설계 7절 순서 | I | 405 + `Allow` | `router_test.cpp` `r05_r19_*`, `test_static.py` `test_r05_r19_*`, `test_requests.py` P-16·P-17 (POST가 405) | 있음. 6단계에서 바뀐다 |

## 5단계 이후 (단계를 시작할 때 채운다)

- 5. keep-alive·pipelining·DRAIN
- 6. 업로드(`multipart/form-data`, 415)와 DELETE
- 7. CGI: GET·POST, chunked 본문, 실행 디렉토리, 무한 루프(504), 에러 스크립트(502)
- 8. 안정성: [[concepts/resilience]] "요구 목록"
- 9. README·시연 설정
