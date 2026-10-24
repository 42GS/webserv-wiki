---
title: webserv 설계 (클래스·인터페이스)
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/nginx-core-module.md, raw/design-checks-observed.md, raw/cpp-core-guidelines.md, raw/google-cpp-style-guide.md, raw/rfc9110.txt, raw/rfc9112.txt, raw/siegerc.in, raw/rfc2046.txt, raw/rfc7578.txt, raw/posix-remove.md, raw/fs-observed-remove-name-length.md, raw/rfc3875.txt]
updated: 2026-10-25
---

# webserv 설계 (클래스·인터페이스)

구현 전에 정하는 설계다. 이 페이지의 구조·이름·값은 모두 **판단**이다. 지켜야 할 규칙은 각 concept 페이지에 있고, 여기서는 그 규칙을 어느 클래스가 맡는지 정한다. 단계 순서는 [[analysis/implementation-plan]]에 있다.

설계가 지켜야 할 핵심 제약:
- 모든 클라이언트·listen·CGI pipe I/O는 `poll()` 하나를 거친다. readiness가 표시된 fd에만 I/O를 하고, read·write 뒤 errno로 동작을 바꾸지 않는다 (raw/subject.md:130-133, raw/subject.md:136) → [[concepts/io-multiplexing]].
- `fork`는 CGI에만 쓴다 (raw/subject.md:144).
- 요청이 무한히 멈추면 안 된다 (raw/subject.md:139).

## 1. 파일 배치

```
Makefile  README.md
conf/                 시연용 설정 파일 (기능별)
www/                  시연용 정적 사이트, 에러 페이지, CGI 스크립트
src/
  main.cpp
  config/   ConfigLexer  ConfigSyntax  DirectiveRules  ConfigBuilder  ServerBuilder  LocationBuilder
            SharedSettings  ConfigValues  ConfigLimits  ConfigLoader  ConfigError  ServerConfig  BuildContext
  core/     EventLoop  IoHandler  Server  Listener  ListenContext  SocketAddress  ChildReaper  Signals  Clock
            HttpDate  Limits
  fs/       FileInfo  FilePath  FileReader  FileWriter
  http/     Connection  Request  RequestParser  HeaderMap  Response  ResponseStream  StatusCodes  StatusText
            MimeTypes  Methods  HeaderNames  Hex  Ascii  FieldSyntax  Multipart
  app/      RequestProcessor  ProcessOutcome
  route/    Router  RouteResult  PathResolver
  handler/  StaticHandler  AutoindexHandler  UploadHandler  DeleteHandler  StatusPage
  cgi/      CgiProcess  CgiPipes  CgiEnv  CgiOutput
tests/                unit/(C++ 단위 테스트), integration/(Python 통합 테스트)
```

- 헤더는 `include/<모듈>/`, 소스는 `src/<모듈>/`에 같은 이름으로 둔다(`-Iinclude`, 2026-10-16 사용자 요청). 단위 테스트는 `tests/unit/`, `make test`로 실행한다. 코드 포맷은 clang-format Google 스타일(`Standard: c++03`)이고 `make format`으로 맞춘다 (2026-10-16 사용자 선택).
- config 모듈은 단계 1 리팩토링에서 `ConfigLexer` → `ConfigSyntax` → `ConfigBuilder`(서버 목록·listen 충돌) → `ServerBuilder`·`LocationBuilder`(값 해석)로 나눴다. 지시자의 위치·인자 수·블록 여부·반복 가능 여부는 `DirectiveRules`의 표 하나에 있다.
- 공용 `util/`은 두지 않는다. 문자열 처리 같은 도우미는 그것을 쓰는 모듈 안에 둔다. 두 모듈 이상에서 같은 이유로 쓰게 되면 그때 뺀다. 이 규칙으로 4단계 리뷰 뒤에 파일 종류 확인과 파일 읽기를 `fs/`로, 16진수 해석을 `http/Hex`로 뺐다. 6단계에서는 요청 파서 안에 있던 token·목록·공백 처리를 multipart 파서도 쓰게 되어 `http/FieldSyntax`로 뺐다(parameter·quoted-string 해석을 더함).
- 헤더에는 다른 파일이 쓰는 상수·자료형만 둔다 (2026-10-17 사용자 결정. 2026-10-16의 "상수와 자료형은 모두 헤더에" 규칙을 가독성 때문에 바꿨다). 여러 파일이 쓰는 어휘(상태 코드 `http/StatusCodes.hpp`, 헤더 이름, 메서드 이름)와 12절의 조정용 값(`core/Limits.hpp`, 본문 상한은 `config/ConfigLimits.hpp`)은 헤더에 둔다. 한 `.cpp`에서만 쓰는 상수·표와 그 행 타입은 그 `.cpp`의 이름 없는 namespace 맨 위에 둔다. 한 `.cpp`에서만 쓰는 보조 클래스·함수도 그 `.cpp`의 이름 없는 namespace에 둔다. 근거: C++ Core Guidelines SF.22는 다른 파일에 내보내지 않는 것을 모두 이름 없는 namespace에 두라고 하고, 구현 파일에 정의한 "helper" 클래스·함수를 예로 든다 (raw/cpp-core-guidelines.md:19791-19796, raw/cpp-core-guidelines.md:19816). SF.21은 헤더에 이름 없는 namespace를 쓰지 말라고 한다 (raw/cpp-core-guidelines.md:19758-19762). Google C++ Style Guide도 다른 파일이 참조하지 않는 `.cc` 파일의 정의에 internal linkage를 권하고 `.h` 파일에는 쓰지 말라고 한다 (raw/google-cpp-style-guide.md:434). 이렇게 두면 다른 파일이 같은 이름을 선언해도 서로 독립이다 (raw/google-cpp-style-guide.md:438). 자세한 내용은 [[sources/cpp-core-guidelines]], [[sources/google-cpp-style-guide]]. 의미가 바로 옆 코드나 주석에서 보이는 값(문법상 글자 위치, 진법, `%XX`의 2, fd의 -1, 참고한 알고리즘의 숫자)은 리터럴로 쓴다.
- 주석은 Doxygen 형식이고, 영어 문장 바로 아래 줄에 같은 뜻의 한국어를 쓴다 (2026-10-17 사용자 결정). 파일마다 `@file`, 헤더의 모든 선언과 `.cpp`의 이름 없는 namespace 함수에 `@brief`·`@param[in/out]`·`@return`을 단다. 매개변수 없는 조회 함수는 `@brief`만. 구조체·클래스 멤버 주석은 선언 위 한 줄(`/** 영어 / 한국어 */`), 열거값과 정렬한 상수 표는 줄 끝 `/**< */`. 헤더에 문서가 있는 함수는 `.cpp` 정의에서 되풀이하지 않고, 구현 쪽 이유만 적는다. 근거: Google C++ Style Guide는 정의의 주석에 선언의 주석을 되풀이하지 말고 어떻게 하는지에 집중하라고 하고 (raw/google-cpp-style-guide.md:2645), 정의에 쓸 내용으로 쓴 기법, 단계 개요, 다른 방법 대신 이 방법을 고른 이유를 예로 든다 (raw/google-cpp-style-guide.md:2643). 복사 금지용 private 선언은 `/// @cond`로 문서에서 뺀다. 테스트 코드도 같은 형식을 쓴다 (2026-10-23 사용자 결정). 단위 테스트(C++)는 파일마다 `@file`을 달고, 테스트 헤더의 선언과 이름 없는 namespace 도우미에 위 태그를 단다. `TEST_CASE` 본문에는 이름이 내용을 말하므로 문서 주석을 달지 않는다. 테스트 ID를 쓰는 파일은 `@file` 설명에 "Test IDs (X-xx) refer to the test plan in the wiki" 문장을 둔다. 통합 테스트(Python)는 Doxygen 태그 없이 docstring과 `#` 주석에 영어 줄 바로 아래 한국어 줄을 쓴다. 모듈과 도우미 함수·메서드에는 docstring을 단다. `test_*` 메서드에는 docstring을 달지 않고 위의 `#` 주석으로 설명한다. docstring을 달면 `unittest -v`가 테스트 이름 다음 줄에 그 첫 줄을 찍기 때문이다 (2026-10-23 Ubuntu 22.04의 Python 3.10.12와 macOS의 Python 3.14.7에서 직접 실행해 확인). src처럼 줄 끝의 짧은 표기 주석(`// a.b.c.d` 같은 것)은 영어만 둔다.
- 로그 모듈은 필요해질 때 만든다.

## 2. 모듈과 책임

| 모듈 | 책임 | 하지 않는 것 |
|---|---|---|
| `config` | 설정 파일을 읽어 검증된 `ServerConfig` 목록을 만든다. 잘못되면 시작 전에 에러로 끝낸다 | 네트워크·HTTP |
| `core` | `poll()` 루프, 객체 수명 관리(`Server`), 자식 회수, 시그널 | HTTP 의미 해석 |
| `http` | 연결의 소켓 I/O와 상태 전이, 요청 파싱, 응답 직렬화 | 요청을 어떻게 처리할지 결정 |
| `app` | 완성된 요청 하나를 받아 응답 또는 CGI 실행으로 바꾼다 (Router → Handler 조율) | 소켓 I/O |
| `route` | 요청 + 설정 → 처리 방식 결정 (경로 정규화, location 선택, 메서드 검사) | 실제 처리 |
| `fs` | 파일 종류·크기·권한 확인, 작은 일반 파일 읽기, 새 파일 쓰기 (config·route·handler가 같이 씀) | 경로 결정, 응답 |
| `handler` | 결정된 방식대로 응답을 만든다 (정적 파일, 리스팅, 업로드, 삭제, 에러 페이지) | 소켓 I/O |
| `cgi` | 자식 프로세스 실행, pipe I/O, CGI 출력 → `Response` | 소켓 I/O, 자식 회수 |

의존 방향 (화살표는 "안다"):

```
main → config, core
core(Server) → http(Connection) → app → route, handler, cgi
cgi → core의 인터페이스(IoRegistry, IoHandler)만
EventLoop → IoHandler, LoopObserver 인터페이스만
```

## 3. 설정 파일 (NGINX 문법, 결정 9)

### 문법

- `server { ... }` 블록 여러 개, 그 안에 `location 경로 { ... }` 블록. 지시자는 `이름 인자 ...;`, `#`부터 줄 끝까지 주석.
- 크기는 숫자 또는 `k`·`m` 단위 (`client_max_body_size 1m;`, raw/nginx-core-module.md:356).
- 같은 이름의 지시자가 server와 location에 모두 있으면 location 값을 쓴다. location에 없으면 server 값을 물려받는다.

### 지시자

| 지시자 | 위치 | 형식 | NGINX와 관계 |
|---|---|---|---|
| `listen` | server | `listen 127.0.0.1:8080;`, `listen 8080;` | 같은 이름. 주소를 생략하면 `0.0.0.0` |
| `error_page` | server | `error_page 404 /errors/404.html;` (코드 여러 개 가능) | 같은 이름. 내부 리다이렉트 대신 그 파일을 읽어 보낸다 |
| `client_max_body_size` | server, location | `client_max_body_size 10m;` | 같은 이름. **0과 100MB 초과는 설정 오류** (NGINX는 0이면 검사 안 함, 결정 11) |
| `root` | server, location | `root /var/www;` | 같음. URI 전체를 root 뒤에 붙인다: `location /i/ { root /data/w3; }`에서 `/i/top.gif` → `/data/w3/i/top.gif` (raw/nginx-core-module.md:1504-1512, raw/nginx-core-module.md:1516) |
| `alias` | location | `alias /tmp/www/;` | 같음. location 부분을 바꿔 끼운다: `location /i/ { alias /data/w3/images/; }`에서 `/i/top.gif` → `/data/w3/images/top.gif` (raw/nginx-core-module.md:132-140). subject 예시(raw/subject.md:169)는 이 방식이다 |
| `index` | server, location | `index index.html index.php;` | 같음 |
| `autoindex` | server, location | `autoindex on;` | 같음. 기본 off |
| `return` | location | `return 301 /new/;` | 같음. 코드와 URL을 함께 받는다 |
| `limit_except` | location | `limit_except GET POST { deny all; }` | 같은 형식. 블록 안에는 `deny all;`만 받는다. GET을 허용하면 HEAD도 허용 (raw/nginx-core-module.md:795) |
| `upload_store` | location | `upload_store /var/www/uploads;` | **새 지시자**. 있으면 그 location이 POST를 업로드로 받는다 (POST도 `limit_except`에 있어야 함) |
| `cgi` | location | `cgi .php /usr/bin/php-cgi;` | **새 지시자**. 확장자와 실행 파일 |

- `limit_except`가 없는 location은 GET과 HEAD만 받는다. POST·DELETE는 `limit_except`에 적어야 열린다 ([[analysis/design-decisions]] 16, 2026-10-17. 그 전에는 모든 메서드를 허용했다). 막힌 메서드는 405 + `Allow`, 모르는 메서드는 501 → [[concepts/configuration-file]] "라우트 규칙을 응답으로 옮길 때".
- 알 수 없는 지시자, 잘못된 위치의 지시자, 인자 개수가 틀린 지시자는 설정 오류다.
- 한 location에 `root`와 `alias`가 함께 있으면 설정 오류로 한다. location에 둘 다 없으면 server의 `root`를 물려받는다. `return`이 없는 location이 물려받은 것까지 포함해 `root`·`alias`가 모두 없으면 파일 경로를 만들 수 없으므로 설정 오류다.
- 정규식 location은 지원하지 않으므로 (raw/subject.md:166) NGINX `alias`의 정규식 관련 규칙은 해당하지 않는다.

### 예시

```nginx
server {
    listen 127.0.0.1:8080;
    root /var/www/site;
    index index.html;
    error_page 404 /errors/404.html;
    client_max_body_size 1m;

    location / {
        limit_except GET { deny all; }
    }
    location /upload/ {
        limit_except GET POST DELETE { deny all; }
        upload_store /var/www/site/upload;
        client_max_body_size 10m;
    }
    location /cgi-bin/ {
        cgi .php /usr/bin/php-cgi;
        cgi .py /usr/bin/python3;
    }
    location /kapouet/ {
        alias /tmp/www/;          # /kapouet/pouic → /tmp/www/pouic (subject 예시)
    }
    location /old/ {
        return 301 /new/;
    }
}
```

### 데이터

```cpp
struct ListenAddr {            // interface:port 하나
    std::string    host;       // "0.0.0.0" 또는 IP
    unsigned short port;
};

struct LocationConfig {
    std::string                        path;          // prefix
    std::string                        root;          // root 또는 alias 중 하나만 값이 있음
    std::string                        alias;
    std::vector<std::string>           indexFiles;
    bool                               autoindex;
    std::set<std::string>              allowedMethods;  // limit_except. 없으면 GET, HEAD (결정 16)
    int                                returnCode;      // 0이면 리다이렉트 없음
    std::string                        returnUrl;
    std::string                        uploadStore;     // 비면 업로드 불가
    std::map<std::string, std::string> cgiByExtension;  // ".php" -> "/usr/bin/php-cgi"
    size_t                             maxBodySize;
};

struct ServerConfig {
    std::vector<ListenAddr>     listens;
    std::map<int, std::string>  errorPages;   // 404 -> "/errors/404.html"
    std::vector<LocationConfig> locations;    // 상속을 반영한 최종 값
};
```

- `loadConfigFile(path)`(`config/ConfigLoader`)는 `std::vector<ServerConfig>`를 돌려주거나 `ConfigError`(파일·줄 번호 포함)를 던진다. server 값의 상속은 파싱 단계에서 끝내, 실행 중에는 `LocationConfig`만 보면 되게 한다.
- 검증: 같은 `interface:port` 중복, `0.0.0.0`과 특정 IP의 같은 포트 → [[concepts/configuration-file]] "포트 관련 엣지 케이스", 결정 4.
- virtual host가 없으므로(결정 4) `ListenAddr` 하나에 `ServerConfig`가 하나 대응한다.
- 설정 객체는 프로그램이 끝날 때까지 `main`이 갖는다. 다른 객체는 `const` 참조로만 쓴다.
- 구현에서 정한 세부 (단계 1, 2026-10-16):
  - `listen` 주소는 점으로 구분한 IPv4만 받는다(`localhost` 같은 이름은 설정 오류). 주소만 쓴 형식과 `*:port`도 설정 오류다 (결정 13).
  - 따옴표 문자열은 지원하지 않는다(설정 오류).
  - location `/`가 없고 server에 `root`가 있으면 그 값으로 location `/`를 만든다. server에 `root`도 없으면 만들지 않고, 맞는 location이 없는 요청은 404가 된다.
  - 구문 트리는 C++98에서 불완전 타입의 `std::vector`를 멤버로 둘 수 없어 노드 인덱스로 연결한다.
  - 설정 파일이 일반 파일이 아니면(디렉토리 등) 설정 오류다.

## 4. 이벤트 루프와 객체 소유

### 인터페이스

```cpp
class IoHandler {                          // poll에 등록되는 것
public:
    virtual ~IoHandler() {}
    virtual int   fd() const = 0;
    virtual short wantedEvents() const = 0;   // 매 바퀴 다시 묻는다
    virtual void  onEvent(short revents) = 0; // I/O는 최대 1번
    virtual void  onFailure() = 0;            // onEvent에서 예외가 나왔을 때
};

class IoRegistry {                         // 등록·해제만. 소유하지 않는다
public:
    virtual ~IoRegistry() {}
    virtual void watch(IoHandler* handler) = 0;
    virtual void unwatch(IoHandler* handler) = 0;
};

class LoopObserver {                       // 매 바퀴 끝에 불림
public:
    virtual ~LoopObserver() {}
    virtual void afterIteration(time_t now) = 0;
    virtual bool shouldStop() const = 0;
};

class EventLoop : public IoRegistry {
public:
    explicit EventLoop(Clock& clock);
    void watch(IoHandler* handler);
    void unwatch(IoHandler* handler);       // 순회 중이면 표시만 하고 바퀴 끝에 뺀다
    void run(LoopObserver& observer);       // shouldStop()이 참이 될 때까지
};
```

- `EventLoop`는 아무것도 소유하지 않고 `delete`하지 않는다. 한 바퀴: poll 목록 구성 → `poll(kPollTimeoutMs)` → 각 handler의 `onEvent` → `unwatch`된 것 정리 → `clock.refresh()` → `observer.afterIteration(clock.now())`.
- `wantedEvents()`를 매번 묻기 때문에 `POLLOUT`은 보낼 데이터가 있을 때만 켜진다 → [[concepts/io-multiplexing]] "POLLOUT은 보낼 데이터가 있을 때만".
- `poll()`이 -1이면 errno를 보지 않고 다음 바퀴로 간다. 시그널로 깬 경우 `shouldStop()`이 참이 된다.
- `revents`에 `POLLHUP`·`POLLERR`·`POLLNVAL`이 있으면 `POLLIN`이 없어도 `onEvent`에 넘긴다.
- `onEvent`에서 나온 예외는 `EventLoop`가 잡아 그 handler에 `onFailure()`를 알린다 (11절).

### 시계 (`Clock`)

허용 함수 목록(raw/subject.md:113)에 시간 함수가 없다. 그래서 목록 안의 함수만으로 현재 시각을 얻는다 (사용자 결정, 2026-10-16).

```cpp
class Clock {
public:
    explicit Clock(const std::string& path);  // 시계용 파일 경로
    bool   refresh();    // open(O_WRONLY|O_CREAT|O_TRUNC) → write 1바이트 → close → stat. 실패하면 false
    time_t now() const;  // 마지막 refresh의 st_mtime (초 단위, UTC 기준 epoch)
};
```

- 파일에 쓰면 수정 시각이 갱신되고, `stat`으로 그 시각을 읽는다. 바퀴마다 한 번만 갱신해 그 바퀴의 모든 타임아웃 판단에 같은 값을 쓴다.
- 시작할 때 `refresh()`가 실패하면 원인을 출력하고 시작하지 않는다. 실행 중 실패하면 이전 값을 유지한다(그 동안 타임아웃이 늦어진다).
- 이 시각으로 `Date` 헤더와 리스팅의 파일 시각을 만든다. 날짜 변환(epoch 초 → `Sun, 06 Nov 1994 08:49:37 GMT`)도 직접 계산한다 (`gmtime` 등을 쓰지 않음).
- macOS와 Ubuntu 22.04 컨테이너에서 이 방식의 값이 `time()`과 같았다 (raw/design-checks-observed.md:60-80) → [[sources/design-checks-observed]].

### 소유 관계

| 객체 | 소유자 | 지우는 시점 |
|---|---|---|
| `ServerConfig` 목록 | `main` | 프로그램 끝 |
| `Listener` | `Server` | 서버 종료 |
| `Connection` | `Server` (`std::map<int, Connection*>`) | `afterIteration`에서 `isClosed()`인 것 |
| `CgiProcess` | 그 요청의 `Connection` (하나만) | CGI 완료 후 또는 `Connection` 소멸 시 |
| `CgiPipe` (입력·출력) | 그 `CgiProcess` | `CgiProcess` 소멸 시 (먼저 `unwatch`) |
| 끝난 자식의 pid | `ChildReaper` | `waitpid`로 회수되면 |

- 소유자가 하나뿐이라 C++98에서도 해제 경로가 분명하다. 다른 객체는 참조만 갖고, 수명이 더 긴 쪽만 참조한다(`Connection` → `ServerConfig`, `CgiProcess` → 자기 `Connection`이 가진 요청의 본문).
- `Server`는 `LoopObserver`를 구현한다. `afterIteration`에서 연결 타임아웃 점검 → 닫힌 연결 삭제 → `ChildReaper::reap()`를 차례로 한다. `Listener`가 `accept`하면 `Server::adopt(fd, ...)`로 `Connection`을 넘긴다.

```cpp
class Server : public LoopObserver, public AcceptHandler {   // AcceptHandler: Listener가 accept한 fd를 넘기는 곳
public:
    Server(const std::vector<ServerConfig>& configs, IoRegistry& registry, ChildReaper& reaper, time_t now);
    ~Server();                                  // 모든 연결 삭제(CGI 자식은 reaper로), listener 삭제
    bool openListeners(std::string& error);     // 실패하면 false, error에 원인
    void adopt(int clientFd, const ListenContext& where);
    void afterIteration(time_t now);
    bool shouldStop() const;                    // signals::stopRequested()
};

class ChildReaper {
public:
    ~ChildReaper();                             // 남은 자식을 SIGKILL하고 기다린다
    void adopt(pid_t pid);                      // 이미 kill했거나 출력이 끝난 자식
    void reap();                                // waitpid(pid, &status, WNOHANG)로 하나씩
};
```

## 5. Connection

`Connection`은 소켓 I/O와 상태 전이만 맡는다. 요청 처리는 `RequestProcessor`, 본문 출처(메모리·파일)는 `ResponseStream`에 맡긴다.

```
READ_HEAD ──머리 완성──▶ READ_BODY ──본문 완성──▶ (RequestProcessor) ─┬─▶ WRITE ──다 보냄──┬─ keep-alive ─▶ READ_HEAD
    │                        │                                      │                  └─ close ──────▶ DRAIN 또는 CLOSED
    │                        │                                      └─▶ WAIT_CGI ──followCgi(출력 끝)──▶ WRITE
    └──── 파싱 에러·크기 초과 ────┴──────────▶ (에러 응답) WRITE → DRAIN → CLOSED
```

| 상태 | `wantedEvents` | 타임아웃 (넘으면) |
|---|---|---|
| `READ_HEAD` | `POLLIN` | 헤더 수신 (408 후 닫기. 첫 바이트 전의 keep-alive 대기는 그냥 닫기) |
| `READ_BODY` | `POLLIN` | 본문 수신 (408 후 닫기) |
| `WAIT_CGI` | 0 (pipe는 `CgiProcess`가 등록) | CGI 타임아웃 (504, 자식 종료) |
| `WRITE` | `POLLOUT` | 응답 전송 (닫기) |
| `DRAIN` | `POLLIN` | 무입력·총 시간 상한 (닫기) |

```cpp
class Connection : public IoHandler {
public:
    Connection(int fd, const ListenContext& where, const CgiServices& services, time_t now);
    ~Connection();                               // CGI가 남아 있으면 kill 후 reaper에 넘김
    int   fd() const;
    short wantedEvents() const;
    void  onEvent(short revents);
    void  onFailure();                           // 예외 등 → CLOSED
    void  checkTimeout(time_t now);              // WAIT_CGI면 followCgi()
    bool  isClosed() const;
private:
    enum State { READ_HEAD, READ_BODY, WAIT_CGI, WRITE, DRAIN, CLOSED };
    void  receiveOnce();                         // recv 1번. DRAIN이면 버린다
    void  sendOnce();                            // send 1번
    void  parseInput();                          // inBuffer_를 파서에 넣고 결과에 따라 처리
    void  handleOutcome(const ProcessOutcome& outcome);   // 응답, CGI 대기, local redirect
    void  followCgi();                           // 끝난 CGI의 결과를 받거나 504
    void  startResponse(const Response& response);
    void  startErrorResponse(int status);        // 다 읽지 못한 요청의 오류 응답
    void  finishResponse();                      // 응답을 다 보낸 뒤: 다음 요청, DRAIN, 닫기
    void  changeState(State next);
    bool  hasTimedOut() const;

    int                 fd_;
    State               state_;
    RequestParser       parser_;
    RequestProcessor    processor_;              // ListenContext(server 블록, 두 끝의 주소)를 가진다
    ResponseStream      stream_;
    CgiProcess*         cgi_;                    // 소유. WAIT_CGI 동안만
    const Request*      current_;                // 파싱한 요청이나 redirected_
    Request             redirected_;             // 마지막 local redirect의 요청
    int                 localRedirects_;
    std::string         inBuffer_;
    bool                keepAlive_;
    bool                requestConsumed_;        // false면 응답 뒤 DRAIN
    time_t              now_;
    time_t              stateSince_;
    time_t              lastProgress_;
};
```

- `ListenContext`는 `ServerConfig` 포인터와 원격 주소, 로컬 주소·포트를 묶은 값이다. 생성자 인자를 4개 이하로 유지한다. 주소는 읽는 곳이 없어 4차 코드 리뷰에서 뺐다가 CGI(`REMOTE_ADDR` 등, 7단계)에서 다시 넣었다 (9절 구현 세부).
- `recv`가 0이면 상대가 닫은 것, -1이면 에러다. 둘 다 errno 없이 `CLOSED`로 간다 → [[concepts/io-multiplexing]] "recv·send 반환값 처리".
- keep-alive 판단과 `DRAIN` 규칙 → [[concepts/connection-management]]. 본문을 다 읽지 않고 응답했으면 `DRAIN`을 거친다 ([[sources/close-after-413-observed]]).
- pipelining: 응답을 다 보낸 뒤 `inBuf_`에 남은 바이트로 다음 요청을 파싱한다 → [[concepts/connection-management]] "pipelining".
- 구현 세부 (단계 5, 2026-10-17, **판단**. 기준은 결정 13의 "요구사항에 부합하고 안전한 쪽"). 근거 줄과 테스트는 [[analysis/test-plan]] 5절.
  - 유지 여부는 파서가 머리를 끝낼 때 `Request::persistent`로 정한다. HTTP/1.1은 `Connection`에 `close` 옵션이 없으면 유지한다. HTTP/1.0은 `keep-alive` 옵션이 있어도 닫는다. RFC 9112 9.3은 1.0 keep-alive를 받아들일지 수신자에게 맡긴다 (raw/rfc9112.txt:1353-1359). siege 기본 설정은 HTTP/1.1이다 (raw/siegerc.in:213).
  - 응답 뒤 유지하는지는 `RequestProcessor`가 `Response::keepAlive`로 정한다. 요청이 유지를 원하고 응답이 400이 아닐 때만 유지한다. 400은 경로 오류(결정 2)이거나 파서 오류다. 파서 오류와 408은 `errorResponse`로 만들고 항상 닫는다. 404·405·403 등은 요청을 다 읽었으므로 유지한다. 닫는 응답에만 `Connection: close`를 붙인다.
  - `DRAIN`은 요청을 다 읽지 못하고 응답한 뒤(파서 오류, 408)에만 거친다. 다 읽은 요청에 닫는 응답을 보냈으면 바로 닫는다. `DRAIN`에서는 받은 바이트를 파싱하지 않고 버린다.
  - 요청 첫 바이트를 기다리는 시간은 새 연결이든 keep-alive든 `kKeepAliveTimeout`(15초)이고, 넘으면 응답 없이 닫는다. 머리 타임아웃(30초)은 요청의 첫 바이트를 받은 때부터 잰다.
  - 시계가 초 단위라 모든 타임아웃은 경과 초가 상한보다 **클 때** 넘은 것으로 본다. 같을 때로 보면 초가 바뀐 직후에 실제로는 거의 0초 뒤에도 넘을 수 있고, `DRAIN` 무입력 1초에서 이 오차가 상한 전체와 같아진다(테스트로 확인).
  - pipelining: 응답을 다 보내면 파서를 초기화하고 `inBuffer_`에 남은 바이트를 바로 파싱한다. 응답을 보내는 동안(`WRITE`)에는 읽지 않으므로 응답 순서가 요청 순서와 같다.

## 6. 요청 파싱

```cpp
class HeaderMap {                    // 이름 대소문자 무시, 같은 이름 여러 값
public:
    void add(const std::string& name, const std::string& value);
    bool has(const std::string& name) const;
    const std::string* first(const std::string& name) const;
    std::vector<std::string> all(const std::string& name) const;   // Set-Cookie 여러 줄
    size_t count(const std::string& name) const;                    // Host 중복 → 400
};

struct Request {
    std::string method, target, path, query, version;
    HeaderMap   headers;
    std::string body;                // chunked는 해제된 상태
    bool        persistent;          // 응답 뒤 연결 유지를 원함 (5절)
};

class RequestParser {
public:
    enum Result { NEED_MORE, HEAD_DONE, DONE, ERROR };
    RequestParser();                      // 크기 상한은 core/Limits.hpp
    Result  feed(std::string& buf);       // buf 앞부분을 소비
    void    setMaxBodySize(size_t n);     // HEAD_DONE 뒤 location 결정 후 호출
    int     errorStatus() const;          // 400, 413, 414, 431, 501, 505 등
    bool    hasStarted() const;           // 이 요청의 바이트가 왔는지. 시간 초과 때 408인지 그냥 닫는지 정한다 (5절)
    const Request& request() const;
    void    reset();                      // 다음 요청
};
```

- 순서: 요청줄 → 헤더 → 본문 길이 결정 → 본문 → [[concepts/request-parsing]]. 코드는 [[concepts/status-codes]].
- 머리가 끝나면 `HEAD_DONE`을 돌려준다. `Connection`이 `RequestProcessor::bodyLimitFor(request)`로 location의 상한을 받아 `setMaxBodySize`를 부른 뒤 계속 넣는다. 그래서 `Content-Length`가 상한을 넘으면 본문을 읽기 전에 413을 낸다.
- 구현 세부 (단계 3, 2026-10-16). RFC가 여러 처리를 허용하는 곳에서 고른 것이다 (**판단**). 기준은 결정 13 때 사용자가 정한 "요구사항에 부합하고 안전한 쪽"이다. 근거 줄은 [[analysis/test-plan]] 3절.
  - LF 하나만 쓴 줄 끝은 받는다(MAY). 유일하게 관대한 쪽을 고른 것이다. 서버 앞에 다른 수신자(프록시)가 없어 해석이 갈릴 상대가 없고, nc로 시험할 때 줄 끝이 LF라서 받는 편이 시연에 안전하다. LF가 뒤따르지 않는 CR은 400.
  - 요청줄 구분자는 SP 하나만 받는다. 관대한 파싱(MAY)은 smuggling 위험이 있어 쓰지 않는다.
  - 요청줄과 첫 헤더 사이의 공백 줄, obs-fold는 무시·치환하지 않고 400으로 거부한다.
  - `Transfer-Encoding`과 `Content-Length`가 함께 오면 400으로 거부하고 닫는다(TE로 처리하는 MAY 대신).
  - `HTTP/1.x`에서 x가 2 이상이면 1.1로 처리한다(SHOULD). 메이저가 1이 아니면 505.
  - absolute-form(`http://host[:port]/path`)은 path와 query만 쓴다. virtual host가 없으므로 host 부분은 server 선택에 쓰지 않는다(결정 4). `*`(asterisk-form)와 authority-form은 400. 메서드가 OPTIONS·CONNECT면 그 전에 501이다.
  - chunk 확장은 무시하고, chunk 크기 줄 하나의 길이에 상한(`kMaxChunkLine` 4096)을 두어 넘으면 400. trailer는 버리되 헤더 상한 안에서만 받는다.
  - 오류 응답 뒤에는 항상 연결을 닫는다. 5단계부터는 요청을 다 읽지 못했으면 닫기 전에 남은 입력을 버린다(DRAIN, 5절).
  - 본문 상한을 고르는 location은 `Router::matchLocation`(가장 긴 prefix)으로 찾는다. 3단계에서는 디코딩 전 경로로 찾고, 4단계에서 정규화한 경로로 바꾼다. 맞는 location이 없으면(그 요청은 404가 된다) NGINX 기본값 1MB를 쓴다.
  - 3단계의 오류 응답 본문은 "코드 reason-phrase" 한 줄이다. 에러 페이지와 `Date`는 4단계.

## 7. 요청 처리 (app, route, handler)

```cpp
struct ProcessOutcome {
    enum Kind { RESPONSE, CGI, LOCAL_REDIRECT };
    Kind        kind;
    Response    response;          // RESPONSE
    CgiProcess* cgi;               // CGI. 소유권이 호출자에게 넘어감
    Request     redirect;          // LOCAL_REDIRECT: 대신 답할 요청
};

class RequestProcessor {
public:
    RequestProcessor(const ListenContext& where, const CgiServices& services);
    size_t         bodyLimitFor(const Request& req) const;
    ProcessOutcome process(const Request& req, time_t now) const;     // 응답 또는 시작한 CGI
    ProcessOutcome afterCgi(const Request& req, CgiProcess& cgi, time_t now) const;  // 응답 또는 local redirect. 출력을 가져간다(11절)
    Response       statusResponse(int status, const Request& req, time_t now) const;      // 504 등
    Response       errorResponse(int status, const std::string& method, time_t now) const;  // 파서 오류·408
};

struct RouteResult {
    enum Kind { STATIC_FILE, DIRECTORY_LISTING, REDIRECT, UPLOAD, DELETE, CGI, ERROR };
    Kind        kind;
    int         status;          // REDIRECT, ERROR
    std::string redirectTo;      // REDIRECT: Location 값
    std::string allow;           // ERROR 405: Allow 값
    std::string fsPath;          // 매핑한 파일 경로 (STATIC_FILE, DIRECTORY_LISTING, DELETE, CGI)
    std::string uploadStore;     // UPLOAD: 저장할 디렉토리
    std::string interpreter;     // CGI: "cgi" 지시자의 프로그램
    std::string scriptName;      // CGI: 스크립트 URI 경로 (디코딩)
    std::string pathInfo;        // CGI: 스크립트 뒤 경로 (디코딩)
    std::string pathTranslated;  // CGI: pathInfo의 매핑
    std::string urlPath;         // DIRECTORY_LISTING, UPLOAD: 정규화한 요청 경로
};

class Router {
public:
    explicit Router(const ServerConfig& server);
    const LocationConfig* matchLocation(const std::string& path) const;   // 가장 긴 prefix, alias면 세그먼트 경계까지 (결정 14)
    const LocationConfig* locationFor(const std::string& encodedPath) const;  // 정규화 후 matchLocation (본문 상한)
    RouteResult route(const Request& req) const;
    bool mapToFile(const std::string& uriPath, std::string& fsPath) const;    // 에러 페이지·업로드 Location의 매핑
};
```

- `RequestProcessor::process`: `Router::route` → `RouteResult::Kind`에 따라 Handler 하나를 부른다. CGI면 `CgiProcess`를 만들어 `start`한 뒤 넘긴다. HEAD는 결과 `Response`의 본문 전송만 끈다 (결정 5).
- `Router::route` 순서: 경로 정규화(`PathResolver`) → location 선택 → 파일 경로 매핑(`root`면 URI 전체를 붙이고, `alias`면 location prefix를 바꿔 끼운다) → `return` → CGI 확장자 → `limit_except` 검사 → 업로드 POST → DELETE → 파일·디렉토리 → [[concepts/security]] "경로 정규화 절차", [[concepts/configuration-file]] "디렉토리 요청 처리 순서". 스크립트를 `limit_except` 검사보다 먼저 찾는 것은 두 경우의 메서드 기준이 달라서다: 스크립트는 `limit_except`가 허용한 메서드면 받고(아래 9절 "메서드"), 다른 경로는 그 location이 답할 수 있어야 한다(`answers()`, 아래 "메서드"). 2026-10-22 주석 점검에서 7단계 구현 뒤 이 줄의 순서가 코드와 달라진 것을 찾아 고쳤다.
- index 파일을 찾으면 그 경로로 `route`를 다시 부른다(CGI 확장자면 CGI가 된다). 다시 부르는 횟수는 `kMaxInternalRedirects`까지, 넘으면 500 (결정 6).
- 업로드는 본문 전체가 메모리에 모인 뒤(`client_max_body_size`로 상한, `Content-Length`를 알면 그만큼 `reserve`) 파일 하나를 `open` → `write`(다 쓸 때까지 반복) → `close`로 한 번에 저장한다. 일반 파일이라 `poll()`이 필요 없다 (raw/subject.md:134). 구현이 단순한 쪽으로 정했다 (사용자 결정, 2026-10-16).
- Handler는 상태가 없는 함수다: `bool serveStaticFile(const RouteResult&, Response&)`(실패하면 false), `UploadResult storeUpload(const RouteResult&, const Request&)` 등. 인자는 3개 이하(`buildStatusPage`·`createdResponse`가 3개).
- `buildStatusPage(status, configuredPages, router)` (`handler/StatusPage`): 설정된 에러 페이지 파일이 있으면 그 파일, 없거나 읽지 못하면 내장 기본 페이지 (raw/subject.md:143). 리다이렉트 응답의 본문도 이것으로 만든다. 4단계 리뷰에서 `ErrorPageBuilder`에서 이름을 바꾸고, Router를 매번 만들지 않고 `RequestProcessor`의 것을 받게 했다.
- 구현 세부 (단계 4, 2026-10-16, **판단**. 기준은 결정 13의 "요구사항에 부합하고 안전한 쪽"):
  - Router는 3단계에서 `http/`에 만들었던 것을 설계대로 `route/`로 옮긴다. `bodyLimitFor`는 `RequestProcessor`로 옮기고 정규화한 경로로 location을 찾는다. 정규화가 실패하거나 맞는 location이 없는 요청은 기본 상한(1MB)으로 본문을 받은 뒤 라우팅에서 400·404로 답한다(머리 단계에서 따로 끊는 경로를 두지 않아 단순하다).
  - `root`·`alias`가 상대 경로면 서버를 실행한 디렉토리 기준이다(시계 파일과 같은 기준).
  - 에러 페이지 URI는 같은 server의 location 매핑(root·alias)으로 파일 경로를 만든다. 일반 파일이 아니거나 읽지 못하면 내장 기본 페이지를 쓴다. 에러 페이지를 처리하다 다시 에러가 나도 다시 찾지 않으므로 반복이 생기지 않는다.
  - `Content-Type`: 확장자 표(html, htm, css, js, json, txt, png, jpg, jpeg, gif, svg, ico, pdf). 표에 없으면 `application/octet-stream`. NGINX 문서의 기본값은 `text/plain`이지만 (raw/nginx-core-module.md:386), 모르는 내용을 브라우저가 글자로 해석하지 않게 하는 쪽을 골랐다. RFC도 `Content-Type`이 없을 때 수신자가 이 타입으로 볼 수 있다고 한다 (raw/rfc9110.txt:2944-2949).
  - 디렉토리 목록은 이름만 보인다(크기·시각 없음, [[concepts/configuration-file]] "디렉토리 요청 처리 순서"의 판단). 이름은 HTML 이스케이프하고 링크는 퍼센트 인코딩한다. `.`으로 시작하는 이름도 보이되 `.`과 `..`은 뺀다.
  - 심볼릭 링크가 root 밖을 가리키는지는 확인하지 못한다. 허용 함수(raw/subject.md:113)에 `lstat`·`realpath`·`readlink`가 없다. URI의 `..`는 정규화에서 막는다.
  - 4단계의 POST·DELETE: 업로드·삭제 처리는 6단계라서, 그 전까지는 정적 리소스가 받지 않는 메서드로 보고 405와 `Allow: GET, HEAD`를 보냈다. 6단계 구현은 아래.
  - `Connection: close`는 5단계(keep-alive)까지 모든 응답에 붙였다. 5단계부터는 닫는 응답에만 붙인다 (5절 구현 세부).
- 구현 세부 (단계 6, 2026-10-17). 사용자가 정한 것은 [[analysis/design-decisions]] 15~17이고, 나머지는 **판단**이다:
  - 메서드: `limit_except`가 허용하고 그 location이 답할 수 있는 메서드만 받는다. POST는 `upload_store`가 있어야 답한다. 405의 `Allow`도 같은 기준으로 만든다 (결정 16).
  - 업로드 요청 검사 (`UploadHandler`, `http/Multipart`). part 헤더의 끝(빈 줄)은 그 part 안에서만 찾는다. 리뷰 전에는 본문 끝까지 찾아서, 빈 줄 없는 part가 많은 1MB 본문에 8.24초 동안 루프가 멈췄다(실측, macOS). 고친 뒤 0.063초다:
    - 요청 `Content-Type`이 없거나 `multipart/form-data`가 아니면 415 (결정 7).
    - boundary가 없거나, 끝이 공백이 아닌 1~70자의 bchars가 아니면 400 (raw/rfc2046.txt:1200-1214).
    - 본문이 multipart 문법에 맞지 않으면 400. 첫 구분자나 마지막 구분자가 없을 때, 구분자 줄에 공백 말고 다른 글자가 있을 때, part에 `name`이 있는 `Content-Disposition: form-data`가 없을 때다 (MUST, raw/rfc7578.txt:197-201).
    - part 헤더는 `Content-Disposition`만 본다. `Content-Type`·`Content-Disposition`·`Content-Transfer-Encoding` 밖의 헤더는 무시해야 한다 (MUST, raw/rfc7578.txt:345-348). part의 `Content-Type`과 `Content-Transfer-Encoding`도 쓰지 않고 내용을 보낸 그대로 저장한다 (**판단**. `Content-Transfer-Encoding`은 보내지 말라는 SHOULD NOT이다, raw/rfc7578.txt:328-329).
  - parameter 읽기:
    - RFC 9110 5.6.6 문법으로 읽는다. quoted-string 안의 `\`는 뒤 옥텟으로 바꾼다 (MUST, raw/rfc9110.txt:1789-1792).
    - 그래서 `filename="C:\\Users\\a.txt"`(구분자마다 `\` 두 개)는 `C:\Users\a.txt`로 풀리고, 마지막 `\` 뒤의 `a.txt`로 저장된다. `filename="C:\Users\a.txt"`(`\` 하나)는 `C:Usersa.txt`로 풀린다. 둘 다 저장 위치 밖으로 나가지 않는다 ([[analysis/test-plan]] F-07).
    - 브라우저가 파일 이름의 `\`를 어떻게 보내는지는 **미확인**이다. 확인 방법: 이름에 `\`가 든 파일을 브라우저로 올리고 요청을 캡처한다.
    - 같은 parameter가 두 번 오면 값이 모호하므로 400이다.
  - 파일 저장:
    - `filename`이 비어 있지 않은 part만 파일로 본다. 다른 필드와 `filename=""`인 part는 무시하고, 파일이 하나도 없으면 400이다.
    - 이름은 마지막 `/`나 `\` 뒤만 쓴다 (디렉토리 경로를 쓰지 말 것, raw/rfc7578.txt:215-220). 그 결과가 비었거나 `.`·`..`이면 400이다.
    - 이름이 255바이트보다 길면 400이다. 리뷰 전에는 `open`이 실패해 500이었다. Ubuntu 22.04 컨테이너는 255바이트까지 만들고 256바이트(ASCII)와 258바이트(한글 86자)는 실패했다. macOS(APFS)는 765바이트(한글 255자)도 만들어 글자 수로 세는 것으로 보인다(**판단**) (raw/fs-observed-remove-name-length.md:73-75, raw/fs-observed-remove-name-length.md:95-97, raw/fs-observed-remove-name-length.md:103-105). 평가 환경에 맞춰 바이트로 센다.
    - 파일 part는 5개까지이고, 넘으면 413이다 (결정 18). 넘는 순간 멈춰서, 그 뒤 이름은 디스크에서 찾지 않는다.
    - 모든 이름을 쓰기 전에 검사한다. 같은 이름이 있으면 아무것도 저장하지 않는다 (결정 17).
    - 파일은 `O_CREAT | O_EXCL`, 모드 0644(umask 적용)로 만든다. 쓰기가 실패하면 이 요청이 만든 파일을 `std::remove`로 지우고 500을 보낸다 (결정 15).
    - 저장 위치가 없거나 디렉토리가 아니면 파일을 만들 수 없어 500이다.
    - 본문은 메모리에 모은 뒤 쓴다(위 업로드 방식). part 내용은 복사하지 않고 본문 안의 범위로 넘긴다.
  - 업로드 응답 (`UploadHandler`가 만들고 `RequestProcessor`는 고르기만 한다. 리뷰 전에는 `RequestProcessor`가 만들었다):
    - 201의 `Location`은 처음 저장한 파일이다. URI는 POST 경로의 디렉토리 + 파일 이름이고, 그 URI가 저장한 파일로 다시 매핑될 때만 붙인다. `upload_store`는 GET으로 닿지 않는 경로일 수 있다.
    - 201 본문은 저장한 파일의 URI(없으면 이름)를 한 줄씩 적은 `text/plain`이다. 201은 `Location`과 함께, 새 리소스를 가리키며 결과를 설명하는 표현을 보낸다 (SHOULD, raw/rfc9110.txt:4050-4055).
    - 409 본문에는 충돌한 이름을 적는다 (SHOULD, raw/rfc9110.txt:7655-7657). 설정한 `error_page` 대신 이 본문을 쓴다.
    - multipart 오류의 400도 다른 400처럼 응답 뒤 연결을 닫는다 (5절).
  - 삭제:
    - 일반 파일만 지우고 204를 보낸다 (raw/rfc9110.txt:4235-4236).
    - 없으면 404이다. 디렉토리와 그 밖의 종류, 그리고 파일이 든 디렉토리에 쓰기·검색 권한(`access(W_OK | X_OK)`)이 없는 경우는 403이다. `std::remove`가 실패하면 500이다.
    - 경로는 GET과 같이 정규화(결정 2)를 거치므로 root 밖은 지울 수 없다.
    - 일반 파일인지 검사한 뒤 `std::remove`를 부르기 전에 다른 프로세스가 그 경로를 빈 디렉토리로 바꾸면 지워진다 (`remove`는 디렉토리면 `rmdir`, raw/posix-remove.md:35). 그대로 두기로 했다 (사용자 결정) → [[analysis/design-decisions]] 15.

## 8. 응답

```cpp
struct Response {
    int         status;
    HeaderMap   headers;
    std::string body;            // 메모리 본문
    std::string bodyFile;        // 큰 정적 파일이면 경로 (body 대신)
    size_t      bodyFileSize;
    bool        omitBody;        // HEAD
    bool        keepAlive;       // 응답 뒤 연결 유지 (5절)
};

class ResponseStream {           // 직렬화한 머리 + 본문(메모리 또는 파일)을 조금씩 내보낸다
public:
    bool        reset(const Response& res);   // 본문 파일을 열지 못하면 false
    bool        hasPending() const;
    const char* data() const;    // 다음에 보낼 바이트
    size_t      size() const;
    bool        consume(size_t n);   // send가 보낸 만큼. 비면 파일에서 다음 조각을 읽어 채운다. 읽지 못하면 false
};
```

- `Content-Length`는 204를 빼고 항상 넣는다 → [[concepts/http-features]] "응답 헤더 규칙". 응답에 chunked는 쓰지 않는다: 정적 파일은 `stat` 크기, CGI 출력은 EOF까지 모은 뒤의 길이를 쓴다.
- `Date` 헤더를 2xx·3xx·4xx 응답에 보낸다. 시계가 있는 origin server의 MUST다 (raw/rfc9110.txt:2313-2317). 값은 `Clock::now()`를 IMF-fixdate 형식으로 바꾼 것이다 (raw/rfc9110.txt:1855-1858). 5xx에도 보낸다(MAY, 같은 문장).
- 일반 파일은 `poll()` 없이 읽어도 되지만 루프를 멈추게 하면 안 된다 (raw/subject.md:134, raw/evaluation-sheet-en.md:59). 그래서 `kInMemoryFileLimit`보다 큰 파일은 `ResponseStream`이 `kFileChunkSize`씩 나눠 읽는다.

## 9. CGI

7단계 구현 (2026-10-18). 처음 설계의 `CgiObserver`(완료 콜백)와 `CgiContext`는 만들지 않았다. 아래 "구현 세부"에 이유가 있다.

```cpp
struct CgiServices { IoRegistry& registry; ChildReaper& reaper; };   // 모든 CGI가 쓰는 것

struct CgiLaunch {                      // 실행할 것
    std::string interpreter;            // "cgi" 지시자의 프로그램 (절대 경로)
    std::string directory;              // 스크립트 디렉토리 (chdir)
    std::string scriptFile;             // 프로그램 인자인 스크립트 파일 이름
    std::vector<std::string> environment;  // buildCgiEnvironment()
};

class CgiProcess {
public:
    CgiProcess(const CgiLaunch& launch, const std::string& body, const CgiServices& services);
    ~CgiProcess();                  // pipe 닫기. 출력이 안 끝난 자식은 SIGKILL. pid는 reaper로
    bool start(time_t now);         // pipe, fork, execve. 실패하면 false → 500
    bool isDone() const;            // 출력 EOF
    bool failed() const;            // 읽기 오류, 출력 상한 초과 → 502
    void takeOutput(std::string& into);   // 출력을 swap으로 넘긴다 (11절)
    bool hasTimedOut(time_t now) const;   // kCgiTimeout 안에 출력이 안 끝남 → 504
private:
    CgiStdin*  stdin_;              // IoHandler: 본문을 write
    CgiStdout* stdout_;             // IoHandler: EOF까지 read
};

std::vector<std::string> buildCgiEnvironment(const Request&, const RouteResult& script, const ListenContext&);
CgiOutput parseCgiOutput(std::string& output);   // RESPONSE, LOCAL_REDIRECT, INVALID. 본문을 가져간다
```

- 흐름: `RequestProcessor::process`가 CGI 결정을 받으면 `startCgi`(검사 → 환경 → `CgiProcess::start`)를 하고 `ProcessOutcome::CGI`를 돌려준다. `Connection`은 `WAIT_CGI`로 가서, 루프 한 바퀴마다 `checkTimeout`에서 `followCgi()`로 확인한다. 끝났으면 `afterCgi`가 출력을 응답(또는 local redirect)으로 바꾸고, 시간을 넘었으면 504.
- `CgiEnv`가 메타변수를 만든다. php-cgi용 `REDIRECT_STATUS`·`SCRIPT_FILENAME`을 넣고 `REDIRECT_URL`은 넣지 않는다 → [[concepts/cgi]] "메타변수".
- `fork` 전: 스크립트를 읽을 수 없으면 403, 프로그램이 없으면 404, 실행할 수 없으면 403 (결정 12). 표준 출력·에러를 flush한다 (결정 12).
- 자식: `dup2`로 표준 입출력 연결 → 상속받은 fd(3 이상)를 모두 `close` → 스크립트 디렉토리로 `chdir` → `SIGPIPE`를 기본 동작으로 → `execve(프로그램, [프로그램, 스크립트 파일 이름], 환경)`. 실패하면 `std::exit(1)` (결정 12). 부모는 출력 없이 EOF를 받으므로 502가 된다.
- 출력 pipe는 `POLLHUP`만 와도 `read`해서 0(EOF)을 확인한다. 입력 pipe는 본문을 다 쓰거나 `POLLERR`·`POLLHUP`이면 닫는다 → [[concepts/cgi]] "1. 호출 절차".
- 판정은 종료 코드가 아니라 출력으로 한다: 형식이 맞으면 그 응답, 아니면 502, 타임아웃이면 504 → [[concepts/cgi]] "5. 실패 처리". 종료 상태를 읽지 않으므로 `waitpid` 매크로를 쓰지 않는다 → [[analysis/subject-vs-evaluation]] 1.9절.
- `CgiProcess`는 `waitpid`를 하지 않는다. 출력이 끝났거나 `kill`한 자식의 pid를 `ChildReaper`에 넘기고, 회수는 `Server::afterIteration`이 바퀴마다 `ChildReaper::reap()`(`WNOHANG`)으로 한다. `Connection`이 먼저 닫혀도 같은 경로로 회수된다. 서버가 끝날 때 `ChildReaper` 소멸자가 남은 자식을 `SIGKILL`하고 기다린다(`main`에서 `Server`보다 먼저 선언해 더 오래 산다).
- 구현 세부 (단계 7, 2026-10-18, **판단**. 시험은 [[analysis/test-plan]] 7절):
  - 스크립트 찾기: location 뒤 경로를 앞에서부터 조각 단위로 보고, 마지막 조각이 `cgi` 확장자로 끝나며 일반 파일인 첫 앞부분을 스크립트로, 나머지를 `PATH_INFO`로 본다. 서버는 경로의 앞부분을 스크립트로 정하고 나머지는 스크립트가 해석한다 (raw/rfc3875.txt:457-464). 확장자와 같은 이름의 디렉토리는 스크립트가 아니다.
  - 메서드: 스크립트 경로로 온 요청은 `limit_except`가 허용한 메서드면 모두 스크립트에 넘긴다(DELETE 포함, 스크립트가 `REQUEST_METHOD`를 보고 처리). 막힌 메서드의 `Allow`는 `limit_except`의 메서드다. 업로드·삭제의 `answers()` 규칙은 스크립트가 아닐 때만 쓴다. 그래서 6단계 OOP 리뷰 4번(시그니처 변경)은 필요 없어졌다.
  - 경로 변수: 자식은 스크립트 디렉토리에서 실행되고 `getcwd()`는 허용 함수가 아니다 (raw/subject.md:113). 그래서 `SCRIPT_FILENAME`은 스크립트 경로가 절대 경로가 아니면 파일 이름만 넣고, `PATH_TRANSLATED`(SHOULD)는 매핑 결과가 절대 경로일 때만 넣는다. 위키의 php-cgi 실측은 절대 경로로만 했다. 상대 이름과 스크립트 인자를 함께 줘도 Ubuntu 22.04의 php-cgi가 GET·POST를 처리했다 ([[analysis/test-plan]] G-17).
  - `cgi` 지시자의 프로그램이 절대 경로가 아니면 설정 오류다. `chdir` 뒤라 상대 경로를 찾을 수 없다.
  - 상속 fd 닫기: `FD_CLOEXEC`를 쓸 수 없어 (1.11절) 자식에서 허용 함수 `opendir`·`readdir`로 `/dev/fd`를 읽어 3 이상을 닫는다. Ubuntu 컨테이너의 열 수 있는 fd 한도가 20480이라 번호를 차례로 모두 닫는 것보다 낫다(2026-10-18 `ulimit -n`).
  - 출력: 스크립트의 `Content-Length`·`Transfer-Encoding`·`Connection`·`Date`는 버리고 서버 값을 쓴다. 스크립트가 연결에 영향을 주는 헤더를 보내면 서버는 지울 수 있고 서버 헤더와의 충돌을 해결해야 한다 (SHOULD, raw/rfc3875.txt:1493-1498). 204·304는 본문을 버리고 304에는 `Content-Length`를 보내지 않는다 (raw/rfc9110.txt:7042-7043, raw/rfc9110.txt:7477-7478, raw/rfc9110.txt:3232-3236). `Status`의 reason phrase는 쓰지 않고 서버의 것을 보낸다. 1xx `Status`는 502.
  - 출력은 스크립트가 `Content-Length`를 줘도 EOF까지 읽는다. subject는 "`Content-Length`가 없으면 EOF가 끝"이라고 하지만 (raw/subject.md:180), RFC 3875는 EOF까지 모두 읽어야 한다고 한다 (MUST, raw/rfc3875.txt:1521-1524).
  - 출력 상한 `kMaxCgiOutputBytes`(16MB): 출력은 응답 전에 메모리에 모으므로 끝없이 출력하는 스크립트가 시간 초과까지 메모리를 키울 수 있다. 넘으면 자식을 죽이고 502.
  - local redirect: 다시 처리할 메서드를 RFC가 정하지 않는다 (raw/rfc3875.txt:1310-1314). 원래 요청이 HEAD면 HEAD, 아니면 본문 없는 GET으로, `Host`만 옮겨 처리한다. 반복은 `kMaxInternalRedirects`(10)까지, 넘으면 500 (결정 6).
  - 완료 확인: 완료 콜백 대신 `Connection::checkTimeout`(루프 한 바퀴마다, 이벤트 분배 밖)에서 확인한다. 끝난 프로세스를 그 pipe의 `onEvent` 안에서 지우는 일이 없고, 인터페이스가 하나 줄어든다. 응답이 늦어지는 시간은 그 바퀴의 끝까지다.
  - 클라이언트 끊김: `WAIT_CGI` 동안 소켓은 이벤트 0으로 poll한다. RST로 끊기면 `POLLHUP`·`POLLERR`로 알고 연결을 닫아 스크립트를 죽인다. 정상 종료(FIN)는 알 수 없어서 스크립트가 끝나거나 CGI 시간 초과(10초)가 지난 뒤 정리된다(2026-10-18 Ubuntu 컨테이너에서 확인). 시간 상한이 있으므로 hang은 아니다.
  - 출력은 끝냈지만 계속 도는 스크립트는 죽이지 않고 reaper에 넘긴다(마무리 중일 수 있음). 서버가 끝날 때 reaper가 죽인다.
  - `Connection` 생성자는 `(fd, where, services, now)`다. `ListenContext`에 원격 주소와 로컬 주소·포트를 다시 넣었다 (`REMOTE_ADDR`, `SERVER_NAME`, `SERVER_PORT`). 로컬 주소는 `getsockname`, 문자열은 `ntohl`로 직접 만든다 (1.7절).

## 10. 시그널

- `signals::install()`: `SIGPIPE` → `SIG_IGN`, `SIGINT`·`SIGTERM` → 플래그만 세우는 핸들러. `SIGCHLD`는 기본 동작 → [[concepts/resilience]] "시그널 처리".
- 플래그(`volatile sig_atomic_t`)는 `Signals.cpp` 안의 파일 범위 변수다. 다른 곳은 `signals::stopRequested()`로만 읽는다. 시그널 핸들러가 쓸 수 있는 곳이 전역뿐이라 전역 상태 금지의 예외로 둔다.
- 종료: `loop.run(server)`가 끝나면 `main`이 반환하며 지역 객체가 선언의 역순으로 소멸한다. `~Server`(모든 연결 삭제 → 각 CGI 자식은 출력이 안 끝났으면 `kill`하고 reaper로, listener 삭제) → `~ChildReaper`(남은 자식 `SIGKILL` 후 `waitpid`) 순서다. 처음 설계의 `Server::shutdown()`·`ChildReaper::killAndReapAll()`은 소멸자로 대신해 만들지 않았다. valgrind에서 "All heap blocks were freed"가 나와야 한다 ([[sources/valgrind-observed-sigint]]).

## 11. 에러 처리 방침

| 종류 | 처리 |
|---|---|
| 설정 오류, listen 실패 (`bind` 등) | 원인 메시지를 stderr에 쓰고 종료 코드 1로 끝낸다 |
| 요청 오류 (파싱, 라우팅) | 해당 4xx 응답. 연결 유지 여부는 [[concepts/connection-management]] |
| 처리 중 서버 문제 (`fork`·`pipe` 실패, 파일을 읽지 못함) | 500. 파일이 없으면 404, 권한이 없으면 403 |
| handler 안의 예외 (`std::bad_alloc` 등) | `EventLoop`가 잡아 `onFailure()` → 그 연결만 닫는다. 단 메모리가 바닥나면 예외 없이 프로세스가 끝날 수 있어 이것만으로는 방어가 안 된다 ([[sources/design-checks-observed]]). 본문 크기 상한(결정 11)이 실제 방어다 |
| 소켓 I/O -1·0 | 그 연결만 닫는다 |

- 예외는 설정 파싱과 요청 처리 내부에서만 던진다. 서버 프로세스는 어떤 요청에도 끝나지 않아야 한다 (raw/evaluation-sheet-en.md:24).
- 8단계 리뷰에서 더한 규칙 (2026-10-18, **판단**):
  - `fork` 뒤 자식에서는 모든 예외를 잡아 `std::exit(1)`로 끝낸다. 풀려 나가면 자식이 서버 코드로 돌아가 같은 소켓을 처리하는 두 번째 서버가 된다.
  - 소멸자에서는 예외를 내보내지 않는다. `~CgiProcess`는 reaper에 넘기지 못하면 그 자리에서 `SIGKILL` 후 기다린다.
  - 연결별 예외 처리 밖에서 매 바퀴 도는 코드(`ChildReaper::reap`)는 할당하지 않는다.
  - `accept`가 실패하면 listener를 멈춘다(`wantedEvents` 0). `Server::afterIteration`이 연결이 닫혔거나 1초가 지났을 때 다시 켠다. fd가 다 찬 동안 루프가 쉬지 않고 도는 것을 막는다.
  - 큰 CGI 출력은 pipe 버퍼에서 응답까지 `swap`으로 옮겨 복사하지 않는다 (`CgiProcess::takeOutput`, `parseCgiOutput`이 인자의 본문을 가져감).
  - 결과와 점검 절차는 [[analysis/test-plan]] 8절.

## 12. 상수 (초기값, 시험하며 조정)

코드에서는 `core/Limits.hpp`의 `limits::`에 있다(본문 상한 두 개는 `config/ConfigLimits.hpp`의 `config_limits::`). 시간 값의 코드 이름에는 `Seconds`가 붙는다(`kKeepAliveTimeoutSeconds` 등). 표에 없는 `kMaxArgc`(2)는 프로그램 이름과 설정 파일 하나라는 인자 수 상한이다.

| 이름 | 값 | 비고 |
|---|---|---|
| `kPollTimeoutMs` | 1000 | 타이머 점검 주기 |
| `kRecvBufferSize` | 65536 | `recv` 1번 크기 |
| `kMaxRequestLine` | 8192 | 넘으면 414 |
| `kMaxHeaderBytes` | 16384 | 넘으면 431 |
| `kMaxChunkLine` | 4096 | chunk 크기 줄(확장 포함) 상한. 넘으면 400 |
| `kHeaderTimeout` | 30초 | 요청 첫 바이트부터 |
| `kBodyTimeout` | 30초 (무입력 기준) | |
| `kSendTimeout` | 30초 (무진행 기준) | |
| `kKeepAliveTimeout` | 15초 | 요청 첫 바이트를 기다리는 시간 (새 연결 포함) |
| `kCgiTimeout` | 10초 | 무한 루프 스크립트 시연. 넘으면 504 |
| `kMaxCgiOutputBytes` | 16MB | 메모리에 모으는 CGI 출력 상한. 넘으면 502 |
| `kPipeIoSize` | 65536 | CGI pipe의 `read`·`write` 1번 크기 |
| `kDrainIdle` / `kDrainTotal` | 1초 / 5초 | 413 실측에서 쓴 값 |
| `kMaxInternalRedirects` | 10 | NGINX와 같음 |
| `kDefaultMaxBodySize` | 1MB | NGINX 기본값 `1m`과 같음 |
| `kMaxBodySizeCeiling` | 100MB | 설정 허용 상한 (결정 11) |
| `kInMemoryFileLimit` | 1MB | 넘으면 나눠 읽음 |
| `kFileChunkSize` | 65536 | 나눠 보내는 파일의 `read` 1번 크기 |
| `kFileReadSize` | 65536 | 통째로 읽는 작은 파일의 `read` 1번 크기 |
| `kMaxErrorPageSize` | 1MB | 설정한 에러 페이지 파일 상한. 넘으면 내장 페이지 |
| `kMaxUploadFiles` | 5 | 업로드 요청 하나가 저장하는 파일 수. 넘으면 413 (결정 18) |
| `kClockFile` | `.webserv_clock` | 실행 디렉토리 기준 |
| `kDefaultConfigPath` | `conf/default.conf` | 인자가 없을 때 |

## 13. 설계 원칙 대조

`~/.claude/rules/engineering.md`의 원칙과 이 설계를 대조한 결과다.

| 원칙 | 설계에서 지킨 방법 |
|---|---|
| SRP | `Connection`은 I/O·상태만, 처리 조율은 `RequestProcessor`, 본문 출처는 `ResponseStream`, 자식 회수는 `ChildReaper` |
| 리소스 해제 | 모든 객체에 소유자가 하나 (4절 표). `EventLoop`는 소유하지 않는다 |
| DIP·낮은 결합도 | `EventLoop`는 `IoHandler`·`LoopObserver`만 안다. `cgi`는 이벤트 루프를 `IoRegistry` 인터페이스로만 안다 (`ChildReaper`는 구체 클래스) |
| 파라미터 4개 이하 | `ListenContext`, `CgiServices`, `CgiLaunch`로 묶었다 |
| 높은 응집도·YAGNI | 공용 `util/`과 로그 모듈을 두지 않는다 |
| 매직 넘버 금지 | 12절 상수. 의미가 바로 옆에서 보이는 값은 리터럴로 쓴다 (1절) |

의도한 예외:
- **OCP**: `RequestProcessor`는 `RouteResult::Kind`로 분기한다. 처리 방식이 7개로 고정이고 늘어날 계획이 없어, Handler 인터페이스 계층보다 분기 하나가 읽기 쉽다 (KISS, 우선순위상 가독성이 유지보수성보다 앞섬).
- **전역 상태**: 시그널 플래그 하나 (10절).
- **데메테르**: 설정 구조체(`LocationConfig` 등)는 행동 없는 데이터라 필드를 직접 읽는다. 행동이 있는 객체끼리는 체인 호출을 하지 않는다.

## 14. 정해야 할 것

- 상수 값은 평가를 통과하는 범위에서 시험하며 조정한다 (사용자 결정, 2026-10-16).
- 7단계(CGI) 설계 때 다시 볼 것 (6단계 OOP 리뷰, 2026-10-17 사용자 동의). 7단계 결과 (2026-10-18):
  - `Connection`의 상태 분기: `WAIT_CGI`를 더하며 고친 곳은 `checkTimeout`(맨 앞에서 `followCgi`로 넘김)과 `hasTimedOut`(항상 false) 두 곳이었다. `wantedEvents`·`onEvent`·`receiveOnce`는 기존 분기로 맞았다. 그래서 State 패턴으로 바꾸지 않았다 (**판단**).
  - Router의 `answers(location, method)`: 스크립트를 메서드 검사 전에 찾게 해서 시그니처를 바꿀 필요가 없었다 (9절 구현 세부).
