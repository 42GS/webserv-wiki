---
title: webserv 설계 (클래스·인터페이스)
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/nginx-core-module.md, raw/design-checks-observed.md]
updated: 2026-10-17
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
  fs/       FileInfo  FileReader
  http/     Connection  Request  RequestParser  HeaderMap  Response  ResponseStream  StatusCodes  StatusText
            MimeTypes  Methods  Hex
  app/      RequestProcessor  ProcessOutcome
  route/    Router  RouteResult  PathResolver
  handler/  StaticHandler  AutoindexHandler  UploadHandler  DeleteHandler  StatusPage
  cgi/      CgiProcess  CgiContext  CgiEnv  CgiPipe  CgiOutputParser  CgiObserver
tests/                Python 테스트 스크립트
```

- 헤더는 `include/<모듈>/`, 소스는 `src/<모듈>/`에 같은 이름으로 둔다(`-Iinclude`, 2026-10-16 사용자 요청). 단위 테스트는 `tests/unit/`, `make test`로 실행한다. 코드 포맷은 clang-format Google 스타일(`Standard: c++03`)이고 `make format`으로 맞춘다 (2026-10-16 사용자 선택).
- config 모듈은 단계 1 리팩토링에서 `ConfigLexer` → `ConfigSyntax` → `ConfigBuilder`(서버 목록·listen 충돌) → `ServerBuilder`·`LocationBuilder`(값 해석)로 나눴다. 지시자의 위치·인자 수·블록 여부·반복 가능 여부는 `DirectiveRules`의 표 하나에 있다.
- 공용 `util/`은 두지 않는다. 문자열 처리 같은 도우미는 그것을 쓰는 모듈 안에 둔다. 두 모듈 이상에서 같은 이유로 쓰게 되면 그때 뺀다. 이 규칙으로 4단계 리뷰 뒤에 파일 종류 확인과 파일 읽기를 `fs/`로, 16진수 해석을 `http/Hex`로 뺐다.
- 상수와 자료형은 `.cpp`가 아니라 헤더에 둔다 (2026-10-16 사용자 요청). 상태 코드는 `http/StatusCodes.hpp`, 12절의 조정용 값은 `core/Limits.hpp`(본문 상한은 `config/ConfigLimits.hpp`), 나머지는 그것을 쓰는 컴포넌트의 헤더에 컴포넌트 이름의 namespace로 둔다(예: `request_parser::`, `http_date::`).
- 로그 모듈은 필요해질 때 만든다.

## 2. 모듈과 책임

| 모듈 | 책임 | 하지 않는 것 |
|---|---|---|
| `config` | 설정 파일을 읽어 검증된 `ServerConfig` 목록을 만든다. 잘못되면 시작 전에 에러로 끝낸다 | 네트워크·HTTP |
| `core` | `poll()` 루프, 객체 수명 관리(`Server`), 자식 회수, 시그널 | HTTP 의미 해석 |
| `http` | 연결의 소켓 I/O와 상태 전이, 요청 파싱, 응답 직렬화 | 요청을 어떻게 처리할지 결정 |
| `app` | 완성된 요청 하나를 받아 응답 또는 CGI 실행으로 바꾼다 (Router → Handler 조율) | 소켓 I/O |
| `route` | 요청 + 설정 → 처리 방식 결정 (경로 정규화, location 선택, 메서드 검사) | 실제 처리 |
| `fs` | 파일 종류·크기·읽기 권한 확인, 작은 일반 파일 읽기 (config·route·handler가 같이 씀) | 경로 결정, 응답 |
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
- 크기는 숫자 또는 `k`·`m` 단위 (`client_max_body_size 1m;`, raw/nginx-core-module.md:355).
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
| `upload_store` | location | `upload_store /var/www/uploads;` | **새 지시자**. 있으면 그 location에서 업로드 허용 |
| `cgi` | location | `cgi .php /usr/bin/php-cgi;` | **새 지시자**. 확장자와 실행 파일 |

- `limit_except`가 없는 location은 서버가 아는 메서드(GET, HEAD, POST, DELETE)를 모두 허용한다. 막힌 메서드는 405 + `Allow`, 모르는 메서드는 501 → [[concepts/configuration-file]] "라우트 규칙을 응답으로 옮길 때".
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
    std::set<std::string>              allowedMethods;  // limit_except. 비면 전부 허용
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

- `ConfigParser::parse(path)`는 `std::vector<ServerConfig>`를 돌려주거나 `ConfigError`(파일·줄 번호 포함)를 던진다. server 값의 상속은 파싱 단계에서 끝내, 실행 중에는 `LocationConfig`만 보면 되게 한다.
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
    EventLoop(LoopObserver& observer, Clock& clock);
    void watch(IoHandler* handler);
    void unwatch(IoHandler* handler);       // 순회 중이면 표시만 하고 바퀴 끝에 뺀다
    void run();
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

- 소유자가 하나뿐이라 C++98에서도 해제 경로가 분명하다. 다른 객체는 참조만 갖고, 수명이 더 긴 쪽만 참조한다(`Connection` → `ServerConfig`, `CgiProcess` → `CgiObserver`인 자기 `Connection`).
- `Server`는 `LoopObserver`를 구현한다. `afterIteration`에서 연결 타임아웃 점검 → 닫힌 연결 삭제 → `ChildReaper::reap()`를 차례로 한다. `Listener`가 `accept`하면 `Server::adopt(fd, ...)`로 `Connection`을 넘긴다.

```cpp
class Server : public LoopObserver {
public:
    Server(const std::vector<ServerConfig>& configs, EventLoop& loop, ChildReaper& reaper);
    bool openListeners();                       // 실패하면 원인 출력 후 false
    void adopt(int clientFd, const ListenContext& where);
    void afterIteration(time_t now);
    bool shouldStop() const;                    // Signals::stopRequested()
    void shutdown();                            // 모든 연결·CGI 정리
};

class ChildReaper {
public:
    void adopt(pid_t pid);                      // 이미 kill했거나 출력이 끝난 자식
    void reap();                                // waitpid(pid, &status, WNOHANG)로 하나씩
    void killAndReapAll();                      // 종료 시
};
```

## 5. Connection

`Connection`은 소켓 I/O와 상태 전이만 맡는다. 요청 처리는 `RequestProcessor`, 본문 출처(메모리·파일)는 `ResponseStream`에 맡긴다.

```
READ_HEAD ──머리 완성──▶ READ_BODY ──본문 완성──▶ (RequestProcessor) ─┬─▶ WRITE ──다 보냄──┬─ keep-alive ─▶ READ_HEAD
    │                        │                                      │                  └─ close ──────▶ DRAIN 또는 CLOSED
    │                        │                                      └─▶ WAIT_CGI ──onCgiFinished──▶ WRITE
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
class Connection : public IoHandler, public CgiObserver {
public:
    Connection(int fd, const ListenContext& where, IoRegistry& registry, ChildReaper& reaper);
    ~Connection();                               // CGI가 남아 있으면 kill 후 reaper에 넘김
    int   fd() const;
    short wantedEvents() const;
    void  onEvent(short revents);
    void  onFailure();                           // 예외 등 → CLOSED
    void  checkTimeout(time_t now);
    bool  isClosed() const;
    void  onCgiFinished(const Response& res);    // CgiObserver
private:
    enum State { READ_HEAD, READ_BODY, WAIT_CGI, WRITE, DRAIN, CLOSED };
    void  receiveOnce();                         // recv 1번
    void  sendOnce();                            // send 1번
    void  handleParsed();                        // RequestProcessor 호출
    void  startResponse(const Response& res);    // ResponseStream 준비, 다음 상태 결정
    void  changeState(State next, time_t now);

    int                 fd_;
    State               state_;
    ListenContext       where_;                  // ServerConfig 참조 + 로컬·원격 주소 (연결마다 다름)
    std::string         inBuf_;
    RequestParser       parser_;
    RequestProcessor    processor_;
    ResponseStream      out_;
    CgiProcess*         cgi_;                    // 소유. WAIT_CGI 동안만
    time_t              stateSince_;
    time_t              lastProgress_;
    bool                keepAlive_;
    bool                requestBodyConsumed_;    // false면 응답 뒤 DRAIN
};
```

- `ListenContext`는 `ServerConfig`와 로컬 `ListenAddr`, 원격 주소를 묶은 값이다. 생성자 인자를 4개 이하로 유지한다. 지금 코드에는 `server`만 있다. 로컬·원격 주소는 읽는 곳이 없어 4차 코드 리뷰에서 뺐고, CGI(`REMOTE_ADDR` 등, 7단계)에서 다시 넣는다.
- `recv`가 0이면 상대가 닫은 것, -1이면 에러다. 둘 다 errno 없이 `CLOSED`로 간다 → [[concepts/io-multiplexing]] "recv·send 반환값 처리".
- keep-alive 판단과 `DRAIN` 규칙 → [[concepts/connection-management]]. 본문을 다 읽지 않고 응답했으면 `DRAIN`을 거친다 ([[sources/close-after-413-observed]]).
- pipelining: 응답을 다 보낸 뒤 `inBuf_`에 남은 바이트로 다음 요청을 파싱한다 → [[concepts/connection-management]] "pipelining".

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
};

class RequestParser {
public:
    enum Result { NEED_MORE, HEAD_DONE, DONE, ERROR };
    explicit RequestParser(const ParserLimits& limits);
    Result  feed(std::string& buf);       // buf 앞부분을 소비
    void    setMaxBodySize(size_t n);     // HEAD_DONE 뒤 location 결정 후 호출
    int     errorStatus() const;          // 400, 413, 414, 431, 501, 505 등
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
  - 3단계에서는 오류 응답 뒤 항상 연결을 닫는다. keep-alive와 본문 버리기(DRAIN)는 5단계.
  - 본문 상한을 고르는 location은 `Router::matchLocation`(가장 긴 prefix)으로 찾는다. 3단계에서는 디코딩 전 경로로 찾고, 4단계에서 정규화한 경로로 바꾼다. 맞는 location이 없으면(그 요청은 404가 된다) NGINX 기본값 1MB를 쓴다.
  - 3단계의 오류 응답 본문은 "코드 reason-phrase" 한 줄이다. 에러 페이지와 `Date`는 4단계.

## 7. 요청 처리 (app, route, handler)

```cpp
struct ProcessOutcome {
    enum Kind { RESPONSE, CGI };
    Kind        kind;
    Response    response;          // RESPONSE
    CgiProcess* cgi;               // CGI. 소유권이 호출자에게 넘어감
};

class RequestProcessor {
public:
    explicit RequestProcessor(const ListenContext& where);
    size_t         bodyLimitFor(const Request& req) const;
    ProcessOutcome process(const Request& req, IoRegistry& registry, CgiObserver& observer);
    Response       errorResponse(int status) const;    // buildStatusPage 사용
};

struct RouteResult {
    enum Kind { STATIC_FILE, DIRECTORY_LISTING, REDIRECT, UPLOAD, DELETE, CGI, ERROR };
    Kind                  kind;
    const LocationConfig* location;
    std::string           fsPath;      // root 매핑 결과
    std::string           scriptPath;  // CGI
    std::string           pathInfo;    // CGI
    int                   status;      // REDIRECT, ERROR
};

class Router {
public:
    explicit Router(const ServerConfig& server);
    const LocationConfig* matchLocation(const std::string& path) const;   // 가장 긴 prefix, alias면 세그먼트 경계까지 (결정 14)
    RouteResult route(const Request& req) const;
};
```

- `RequestProcessor::process`: `Router::route` → `RouteResult::Kind`에 따라 Handler 하나를 부른다. CGI면 `CgiProcess`를 만들어 `start`한 뒤 넘긴다. HEAD는 결과 `Response`의 본문 전송만 끈다 (결정 5).
- `Router::route` 순서: 경로 정규화(`PathResolver`) → location 선택 → 파일 경로 매핑(`root`면 URI 전체를 붙이고, `alias`면 location prefix를 바꿔 끼운다) → `return` → `limit_except` 검사 → CGI 확장자 → 업로드 POST → DELETE → 파일·디렉토리 → [[concepts/security]] "경로 정규화 절차", [[concepts/configuration-file]] "디렉토리 요청 처리 순서".
- index 파일을 찾으면 그 경로로 `route`를 다시 부른다(CGI 확장자면 CGI가 된다). 다시 부르는 횟수는 `kMaxInternalRedirects`까지, 넘으면 500 (결정 6).
- 업로드는 본문 전체가 메모리에 모인 뒤(`client_max_body_size`로 상한, `Content-Length`를 알면 그만큼 `reserve`) 파일 하나를 `open` → `write`(다 쓸 때까지 반복) → `close`로 한 번에 저장한다. 일반 파일이라 `poll()`이 필요 없다 (raw/subject.md:134). 구현이 단순한 쪽으로 정했다 (사용자 결정, 2026-10-16).
- Handler는 상태가 없는 함수다: `Response StaticHandler::serve(const RouteResult&)`, `UploadHandler::store(const RouteResult&, const Request&)` 등. 인자는 2개 이하.
- `buildStatusPage(status, configuredPages, router)` (`handler/StatusPage`): 설정된 에러 페이지 파일이 있으면 그 파일, 없거나 읽지 못하면 내장 기본 페이지 (raw/subject.md:143). 리다이렉트 응답의 본문도 이것으로 만든다. 4단계 리뷰에서 `ErrorPageBuilder`에서 이름을 바꾸고, Router를 매번 만들지 않고 `RequestProcessor`의 것을 받게 했다.
- 구현 세부 (단계 4, 2026-10-16, **판단**. 기준은 결정 13의 "요구사항에 부합하고 안전한 쪽"):
  - Router는 3단계에서 `http/`에 만들었던 것을 설계대로 `route/`로 옮긴다. `bodyLimitFor`는 `RequestProcessor`로 옮기고 정규화한 경로로 location을 찾는다. 정규화가 실패하거나 맞는 location이 없는 요청은 기본 상한(1MB)으로 본문을 받은 뒤 라우팅에서 400·404로 답한다(머리 단계에서 따로 끊는 경로를 두지 않아 단순하다).
  - `root`·`alias`가 상대 경로면 서버를 실행한 디렉토리 기준이다(시계 파일과 같은 기준).
  - 에러 페이지 URI는 같은 server의 location 매핑(root·alias)으로 파일 경로를 만든다. 일반 파일이 아니거나 읽지 못하면 내장 기본 페이지를 쓴다. 에러 페이지를 처리하다 다시 에러가 나도 다시 찾지 않으므로 반복이 생기지 않는다.
  - `Content-Type`: 확장자 표(html, htm, css, js, json, txt, png, jpg, jpeg, gif, svg, ico, pdf). 표에 없으면 `application/octet-stream`. NGINX 문서의 기본값은 `text/plain`이지만 (raw/nginx-core-module.md:386), 모르는 내용을 브라우저가 글자로 해석하지 않게 하는 쪽을 골랐다. RFC도 `Content-Type`이 없을 때 수신자가 이 타입으로 볼 수 있다고 한다 (raw/rfc9110.txt:2944-2949).
  - 디렉토리 목록은 이름만 보인다(크기·시각 없음, [[concepts/configuration-file]] "디렉토리 요청 처리 순서"의 판단). 이름은 HTML 이스케이프하고 링크는 퍼센트 인코딩한다. `.`으로 시작하는 이름도 보이되 `.`과 `..`은 뺀다.
  - 심볼릭 링크가 root 밖을 가리키는지는 확인하지 못한다. 허용 함수(raw/subject.md:113)에 `lstat`·`realpath`·`readlink`가 없다. URI의 `..`는 정규화에서 막는다.
  - 4단계의 POST·DELETE: 업로드·삭제 처리는 6단계라서, 그 전까지는 정적 리소스가 받지 않는 메서드로 보고 405와 `Allow: GET, HEAD`를 보낸다.
  - `Connection: close`는 5단계(keep-alive)까지 모든 응답에 붙인다.

## 8. 응답

```cpp
struct Response {
    int         status;
    HeaderMap   headers;
    std::string body;            // 메모리 본문
    std::string bodyFile;        // 큰 정적 파일이면 경로 (body 대신)
    size_t      bodyFileSize;
    bool        omitBody;        // HEAD
};

class ResponseStream {           // 직렬화한 머리 + 본문(메모리 또는 파일)을 조금씩 내보낸다
public:
    void        reset(const Response& res, bool closeAfter);
    bool        hasPending() const;
    const char* data() const;    // 다음에 보낼 바이트
    size_t      size() const;
    void        consume(size_t n);   // send가 보낸 만큼. 비면 파일에서 다음 조각을 읽어 채운다
};
```

- `Content-Length`는 204를 빼고 항상 넣는다 → [[concepts/http-features]] "응답 헤더 규칙". 응답에 chunked는 쓰지 않는다: 정적 파일은 `stat` 크기, CGI 출력은 EOF까지 모은 뒤의 길이를 쓴다.
- `Date` 헤더를 2xx·3xx·4xx 응답에 보낸다. 시계가 있는 origin server의 MUST다 (raw/rfc9110.txt:2313-2317). 값은 `Clock::now()`를 IMF-fixdate 형식으로 바꾼 것이다 (raw/rfc9110.txt:1855-1858). 5xx에도 보낸다(MAY, 같은 문장).
- 일반 파일은 `poll()` 없이 읽어도 되지만 루프를 멈추게 하면 안 된다 (raw/subject.md:134, raw/evaluation-sheet-en.md:59). 그래서 `kInMemoryFileLimit`보다 큰 파일은 `ResponseStream`이 `kFileChunkSize`씩 나눠 읽는다.

## 9. CGI

```cpp
struct CgiContext {                 // CGI 실행에 필요한 값 묶음
    const Request&       request;
    const RouteResult&   route;
    const ListenContext& where;     // 서버 이름·포트, 원격 주소
};

class CgiObserver {
public:
    virtual ~CgiObserver() {}
    virtual void onCgiFinished(const Response& res) = 0;
};

class CgiProcess {
public:
    CgiProcess(const CgiContext& ctx, IoRegistry& registry, CgiObserver& observer);
    ~CgiProcess();                  // pipe unwatch·close
    bool  start();                  // pipe, fork, execve. 실패하면 false → 500
    void  checkTimeout(time_t now); // 넘으면 kill(SIGKILL) 후 observer에 504
    pid_t releaseChild();           // 회수 책임을 ChildReaper로 넘김
private:
    void  onOutputClosed();         // EOF → CgiOutputParser → observer에 응답(또는 502)
    // CgiPipe stdin_, stdout_ (값으로 보유), pid_t pid_, std::string output_, time_t startedAt_
};
```

- `CgiEnv`가 메타변수 배열을 만든다. php-cgi용 `REDIRECT_STATUS`·`SCRIPT_FILENAME`을 넣고 `REDIRECT_URL`은 넣지 않는다 → [[concepts/cgi]] "메타변수".
- `fork` 전: `access`로 스크립트와 실행 파일을 확인한다(없으면 404, 권한이 없으면 403). 표준 출력·에러를 flush한다 (결정 12).
- 자식: `dup2`로 표준 입출력 연결 → 필요 없는 fd 모두 `close` → 스크립트 디렉토리로 `chdir` → `execve`. 실패하면 `std::exit(1)` (결정 12). 부모는 출력 없이 EOF를 받으므로 502가 된다.
- 출력 pipe는 `POLLHUP`만 와도 `read`해서 0(EOF)을 확인한다. 입력 pipe는 본문을 다 쓰면 닫는다 → [[concepts/cgi]] "1. 호출 절차".
- 판정은 종료 코드가 아니라 출력으로 한다: 형식이 맞으면 그 응답, 아니면 502, 타임아웃이면 504 → [[concepts/cgi]] "5. 실패 처리".
- `CgiProcess`는 `waitpid`를 하지 않는다. 출력이 끝났거나 `kill`한 자식의 pid를 `ChildReaper`에 넘기고, 회수는 `ChildReaper`가 바퀴마다 `WNOHANG`으로 한다. `Connection`이 먼저 닫혀도 같은 경로로 회수된다.

## 10. 시그널

- `Signals::install()`: `SIGPIPE` → `SIG_IGN`, `SIGINT`·`SIGTERM` → 플래그만 세우는 핸들러. `SIGCHLD`는 기본 동작 → [[concepts/resilience]] "시그널 처리".
- 플래그(`volatile sig_atomic_t`)는 `Signals.cpp` 안의 파일 범위 변수다. 다른 곳은 `Signals::stopRequested()`로만 읽는다. 시그널 핸들러가 쓸 수 있는 곳이 전역뿐이라 전역 상태 금지의 예외로 둔다.
- 종료: `run()`이 끝나면 `Server::shutdown()`(모든 연결 삭제 → 각 CGI 자식 `kill` 후 reaper로) → `ChildReaper::killAndReapAll()` → listen 소켓 `close` → `main` 반환. valgrind에서 "All heap blocks were freed"가 나와야 한다 ([[sources/valgrind-observed-sigint]]).

## 11. 에러 처리 방침

| 종류 | 처리 |
|---|---|
| 설정 오류, listen 실패 (`bind` 등) | 원인 메시지를 stderr에 쓰고 종료 코드 1로 끝낸다 |
| 요청 오류 (파싱, 라우팅) | 해당 4xx 응답. 연결 유지 여부는 [[concepts/connection-management]] |
| 처리 중 서버 문제 (`fork`·`pipe` 실패, 파일을 읽지 못함) | 500. 파일이 없으면 404, 권한이 없으면 403 |
| handler 안의 예외 (`std::bad_alloc` 등) | `EventLoop`가 잡아 `onFailure()` → 그 연결만 닫는다. 단 메모리가 바닥나면 예외 없이 프로세스가 끝날 수 있어 이것만으로는 방어가 안 된다 ([[sources/design-checks-observed]]). 본문 크기 상한(결정 11)이 실제 방어다 |
| 소켓 I/O -1·0 | 그 연결만 닫는다 |

- 예외는 설정 파싱과 요청 처리 내부에서만 던진다. 서버 프로세스는 어떤 요청에도 끝나지 않아야 한다 (raw/evaluation-sheet-en.md:24).

## 12. 상수 (초기값, 시험하며 조정)

코드에서는 `core/Limits.hpp`의 `limits::`에 있다(본문 상한 두 개는 `config/ConfigLimits.hpp`의 `config_limits::`). 아직 쓰지 않는 값(keep-alive, CGI, DRAIN)은 그 단계에서 넣는다.

| 이름 | 값 | 비고 |
|---|---|---|
| `kPollTimeoutMs` | 1000 | 타이머 점검 주기 |
| `kRecvBufferSize` | 65536 | `recv` 1번 크기 |
| `kMaxRequestLine` | 8192 | 넘으면 414 |
| `kMaxHeaderBytes` | 16384 | 넘으면 431 |
| `kMaxChunkLine` | 4096 | chunk 크기 줄(확장 포함) 상한. 넘으면 400 |
| `kHeaderTimeout` | 30초 | |
| `kBodyTimeout` | 30초 (무입력 기준) | |
| `kSendTimeout` | 30초 (무진행 기준) | |
| `kKeepAliveTimeout` | 15초 | |
| `kCgiTimeout` | 10초 | 무한 루프 스크립트 시연 |
| `kDrainIdle` / `kDrainTotal` | 1초 / 5초 | 413 실측에서 쓴 값 |
| `kMaxInternalRedirects` | 10 | NGINX와 같음 |
| `kDefaultMaxBodySize` | 1MB | NGINX 기본값 `1m`과 같음 |
| `kMaxBodySizeCeiling` | 100MB | 설정 허용 상한 (결정 11) |
| `kInMemoryFileLimit` | 1MB | 넘으면 나눠 읽음 |
| `kFileChunkSize` | 65536 | 나눠 보내는 파일의 `read` 1번 크기 |
| `kFileReadSize` | 65536 | 통째로 읽는 작은 파일의 `read` 1번 크기 |
| `kMaxErrorPageSize` | 1MB | 설정한 에러 페이지 파일 상한. 넘으면 내장 페이지 |
| `kClockFile` | `.webserv_clock` | 실행 디렉토리 기준 |
| `kDefaultConfigPath` | `conf/default.conf` | 인자가 없을 때 |

## 13. 설계 원칙 대조

`~/.claude/rules/engineering.md`의 원칙과 이 설계를 대조한 결과다.

| 원칙 | 설계에서 지킨 방법 |
|---|---|
| SRP | `Connection`은 I/O·상태만, 처리 조율은 `RequestProcessor`, 본문 출처는 `ResponseStream`, 자식 회수는 `ChildReaper` |
| 리소스 해제 | 모든 객체에 소유자가 하나 (4절 표). `EventLoop`는 소유하지 않는다 |
| DIP·낮은 결합도 | `EventLoop`는 `IoHandler`·`LoopObserver`만 안다. `cgi`는 `IoRegistry`·`CgiObserver` 인터페이스만 안다 |
| 파라미터 4개 이하 | `ListenContext`, `CgiContext`로 묶었다 |
| 높은 응집도·YAGNI | 공용 `util/`과 로그 모듈을 두지 않는다 |
| 매직 넘버 금지 | 12절 상수 |

의도한 예외:
- **OCP**: `RequestProcessor`는 `RouteResult::Kind`로 분기한다. 처리 방식이 7개로 고정이고 늘어날 계획이 없어, Handler 인터페이스 계층보다 분기 하나가 읽기 쉽다 (KISS, 우선순위상 가독성이 유지보수성보다 앞섬).
- **전역 상태**: 시그널 플래그 하나 (10절).
- **데메테르**: 설정 구조체(`LocationConfig` 등)는 행동 없는 데이터라 필드를 직접 읽는다. 행동이 있는 객체끼리는 체인 호출을 하지 않는다.

## 14. 정해야 할 것

- 없음. 상수 값은 평가를 통과하는 범위에서 시험하며 조정한다 (사용자 결정, 2026-10-16).
