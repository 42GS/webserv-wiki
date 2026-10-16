---
title: webserv 설계 (클래스·인터페이스)
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-16
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
  config/   ConfigLexer  ConfigParser  ServerConfig  LocationConfig
  core/     EventLoop  IoHandler  Listener  Signals
  http/     Connection  Request  RequestParser  Response  ResponseBuilder  HeaderMap  StatusCodes  MimeTypes
  route/    Router  RouteResult  PathResolver
  handler/  StaticHandler  AutoindexHandler  UploadHandler  DeleteHandler  ErrorPageBuilder
  cgi/      CgiProcess  CgiEnv  CgiOutputParser  CgiPipe
  util/     StringUtil  TimeUtil  Logger
tests/                Python 테스트 스크립트
```

## 2. 모듈과 책임

| 모듈 | 책임 | 하지 않는 것 |
|---|---|---|
| `config` | 설정 파일을 읽어 검증된 `ServerConfig` 목록을 만든다. 잘못되면 시작 전에 에러로 끝낸다 | 네트워크·HTTP |
| `core` | `poll()` 루프, fd 등록·해제, 타이머 점검, 시그널 플래그 | HTTP 의미 해석 |
| `http` | 연결 상태기계, 요청 파싱, 응답 직렬화 | 파일 시스템 접근 |
| `route` | 요청 + 설정 → 처리 방식 결정 (location 선택, 경로 정규화, 메서드 검사) | 실제 처리 |
| `handler` | 결정된 방식대로 응답을 만든다 (정적 파일, 리스팅, 업로드, 삭제, 에러 페이지) | 소켓 I/O |
| `cgi` | 자식 프로세스 실행, pipe I/O, CGI 출력 → `Response` | 소켓 I/O |

의존 방향: `main → config, core` / `core → (IoHandler 인터페이스만)` / `http → route → handler, cgi` / 모두 `util` 사용. `core`는 HTTP를 모른다.

## 3. 설정 데이터

```cpp
struct ListenAddr {            // interface:port 하나
    std::string host;          // "0.0.0.0" 또는 IP
    unsigned short port;
};

struct LocationConfig {
    std::string                 path;            // prefix, 정규화된 형태
    std::string                 root;
    std::set<std::string>       methods;         // 비어 있으면 GET, HEAD
    std::vector<std::string>    indexFiles;
    bool                        autoindex;
    int                         returnCode;      // 0이면 리다이렉트 없음
    std::string                 returnUrl;
    bool                        uploadEnabled;
    std::string                 uploadStore;
    std::map<std::string, std::string> cgi;      // ".php" -> "/usr/bin/php-cgi"
    size_t                      maxBodySize;     // server 값 상속
};

struct ServerConfig {
    std::vector<ListenAddr>     listens;
    std::map<int, std::string>  errorPages;      // 404 -> "/errors/404.html"
    size_t                      maxBodySize;
    std::vector<LocationConfig> locations;       // 긴 prefix 순으로 정렬해 둠
};
```

- `ConfigParser::parse(path)`는 `std::vector<ServerConfig>`를 돌려주거나 `ConfigError`(파일·줄 번호 포함)를 던진다.
- 검증: 같은 `interface:port` 중복, `0.0.0.0`과 특정 IP의 같은 포트, 알 수 없는 지시자, 범위 밖 값 → [[concepts/configuration-file]] "포트 관련 엣지 케이스", 결정 4.
- 문법은 NGINX `server`/`location` 블록과 비슷하게 한다 → [[concepts/configuration-file]] "NGINX 지시자 대응표".
- virtual host가 없으므로(결정 4) `ListenAddr` 하나에 `ServerConfig`가 하나 대응한다. `Listener`가 자기 `ServerConfig`를 가리킨다.

## 4. 이벤트 루프

```cpp
class IoHandler {                       // poll에 등록되는 모든 것
public:
    virtual ~IoHandler() {}
    virtual int  fd() const = 0;
    virtual short wantedEvents() const = 0;   // POLLIN / POLLOUT 조합. 매 루프마다 다시 물음
    virtual void onEvent(short revents) = 0;  // 이 안에서 I/O는 최대 1번
    virtual void onTick(time_t now) = 0;      // 타임아웃 점검
    virtual bool isDone() const = 0;          // true면 루프가 해제
};

class EventLoop {
public:
    void add(IoHandler* handler);            // 소유권을 가져감
    void run();                              // 종료 플래그가 설 때까지
private:
    std::vector<IoHandler*> handlers_;
    void buildPollSet(std::vector<pollfd>& fds);
    void dispatch(const std::vector<pollfd>& fds);
    void reapDone();                         // isDone()인 handler를 delete, close
};
```

- 구현체: `Listener`(listen 소켓, `accept` → `Connection` 생성), `Connection`(클라이언트 소켓), `CgiPipe`(CGI 입력·출력 pipe 각각).
- 루프 한 바퀴: `buildPollSet` → `poll(timeout 1000ms)` → `dispatch` → 모든 handler에 `onTick` → `reapDone`. 순회 중에는 지우지 않고 끝에서 지운다(순회 중 벡터가 바뀌는 문제를 피함).
- `wantedEvents()`를 매번 다시 묻기 때문에 `POLLOUT`은 보낼 데이터가 있을 때만 켜진다 → [[concepts/io-multiplexing]] "POLLOUT은 보낼 데이터가 있을 때만".
- `poll()`이 -1이면 errno를 보지 않고 다음 바퀴로 간다. 시그널로 깬 경우 종료 플래그가 서 있다 → [[concepts/resilience]].
- `revents`에 `POLLHUP`·`POLLERR`·`POLLNVAL`이 있으면 `POLLIN`이 없어도 `onEvent`에 넘긴다. 처리 규칙은 각 handler가 정한다.

## 5. Connection 상태기계

```
READ_HEAD ──머리 완성──▶ READ_BODY ──본문 완성──▶ PROCESS ─┬─▶ WRITE ──다 보냄──┬─ keep-alive ─▶ READ_HEAD
    │                        │                            │                  └─ close ──────▶ DRAIN 또는 CLOSED
    │                        │                            └─▶ WAIT_CGI ──CGI 완료──▶ WRITE
    └──── 파싱 에러·크기 초과 ────┴──────────▶ (에러 응답) WRITE → DRAIN → CLOSED
```

| 상태 | `wantedEvents` | 타임아웃 (넘으면) |
|---|---|---|
| `READ_HEAD` | `POLLIN` | 헤더 수신 (408 후 닫기. 아무 바이트도 오지 않은 keep-alive 대기는 그냥 닫기) |
| `READ_BODY` | `POLLIN` | 본문 수신 (408 후 닫기) |
| `PROCESS` | 없음 (같은 바퀴 안에서 끝남) | — |
| `WAIT_CGI` | 없음 (`CgiPipe`가 따로 등록됨) | CGI 타임아웃 (504, 자식 종료) |
| `WRITE` | `POLLOUT` | 응답 전송 (닫기) |
| `DRAIN` | `POLLIN` | 무입력·총 시간 상한 (닫기) |

```cpp
class Connection : public IoHandler {
public:
    Connection(int fd, const ServerConfig& server, const ListenAddr& local);
    // IoHandler 구현
private:
    enum State { READ_HEAD, READ_BODY, PROCESS, WAIT_CGI, WRITE, DRAIN, CLOSED };
    State          state_;
    std::string    inBuf_;          // 받은 바이트 (파서가 소비)
    std::string    outBuf_;         // 보낼 바이트
    size_t         outPos_;
    RequestParser  parser_;
    time_t         stateSince_;     // 상태 진입 시각
    time_t         lastActivity_;
    bool           keepAlive_;
    bool           bodyFullyRead_;  // false면 응답 뒤 DRAIN
    CgiProcess*    cgi_;            // WAIT_CGI 동안만
    FileSource*    file_;           // 큰 정적 파일을 나눠 읽을 때
    void           onReadable();    // recv 1번
    void           onWritable();    // send 1번
    void           process();       // Router → Handler → outBuf_
    void           finishResponse(const Response& res);
};
```

- `recv`가 0이면 상대가 닫은 것, -1이면 에러다. 둘 다 errno 없이 `CLOSED`로 간다 → [[concepts/io-multiplexing]] "recv·send 반환값 처리".
- keep-alive 판단과 `DRAIN` 규칙 → [[concepts/connection-management]]. 본문을 다 읽지 않고 응답했으면 `DRAIN`을 거친다 (실측 근거 [[sources/close-after-413-observed]]).
- pipelining: 한 응답을 다 보낸 뒤 `inBuf_`에 남은 바이트로 다음 요청 파싱을 시작한다 → [[concepts/connection-management]] "pipelining".

## 6. 요청 파싱

```cpp
class HeaderMap {                    // 이름 대소문자 무시, 같은 이름 여러 값 허용
public:
    void add(const std::string& name, const std::string& value);
    bool has(const std::string& name) const;
    const std::string* first(const std::string& name) const;
    std::vector<std::string> all(const std::string& name) const;
    size_t count(const std::string& name) const;
};

struct Request {
    std::string method, target, path, query, version;
    HeaderMap   headers;
    std::string body;                // chunked는 해제된 상태
};

class RequestParser {
public:
    enum Result { NEED_MORE, DONE, ERROR };
    explicit RequestParser(const Limits& limits);
    Result  feed(std::string& buf);  // buf 앞부분을 소비
    int     errorStatus() const;     // ERROR일 때 400, 413, 414, 431, 501, 505 등
    void    setMaxBodySize(size_t n);// 머리 완성 뒤 location 결정 후 호출
    const Request& request() const;
    void    reset();                 // keep-alive 다음 요청
};
```

- 순서: 요청줄 → 헤더 → 본문 길이 결정 → 본문 → [[concepts/request-parsing]]. 코드 선택은 [[concepts/status-codes]].
- 본문 상한은 location마다 다르므로, 머리를 다 읽은 뒤 `Router`가 location을 고르고 `setMaxBodySize`를 부른다. 그래서 `Content-Length`가 상한을 넘으면 본문을 읽기 전에 413을 낸다.
- `HeaderMap`이 같은 이름 여러 값을 담는 것은 응답의 `Set-Cookie` 여러 줄 때문이다 (결정 8).

## 7. 라우팅과 처리

```cpp
struct RouteResult {
    enum Kind { STATIC_FILE, DIRECTORY_INDEX, AUTOINDEX, REDIRECT, UPLOAD, DELETE, CGI, ERROR };
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
    const LocationConfig* matchLocation(const std::string& path) const;   // 가장 긴 prefix
    RouteResult route(const Request& req) const;
};
```

- `route()` 순서: 경로 정규화(`PathResolver`) → location 선택 → `return` → 메서드 검사(405 + `Allow`, 모르는 메서드 501) → CGI 확장자 → 업로드 POST → DELETE → 파일·디렉토리 → [[concepts/security]] "경로 정규화 절차", [[concepts/configuration-file]] "디렉토리 요청 처리 순서".
- index 파일이 CGI 확장자면 index 경로로 `route()`를 다시 부른다. 내부 리다이렉트 횟수는 10회까지, 넘으면 500 (결정 6).
- Handler는 상태가 없는 함수 묶음으로 둔다: `Response StaticHandler::serve(const RouteResult&, const Request&)` 등. CGI만 `CgiProcess`를 만든다.
- `ErrorPageBuilder::build(status, server)`: 설정된 에러 페이지 파일이 있으면 그 파일, 없거나 읽지 못하면 내장 기본 페이지 (raw/subject.md:143).

## 8. 응답

```cpp
struct Response {
    int         status;
    HeaderMap   headers;
    std::string body;
    bool        headOnly;       // HEAD: 헤더는 GET과 같게, 본문은 보내지 않음
    bool        closeAfter;     // Connection: close
};

std::string ResponseBuilder::serialize(const Response& res);   // 상태줄 + 헤더 + 본문
```

- `Content-Length`는 204를 빼고 항상 넣는다 → [[concepts/http-features]] "응답 헤더 규칙". 응답에 chunked는 쓰지 않는다: 정적 파일은 `stat` 크기, CGI 출력은 EOF까지 모은 뒤의 길이로 미리 알 수 있다.
- `Date` 헤더는 시간 함수 허용 여부가 정해지지 않아 보류한다 → [[concepts/http-features]] "Date 헤더와 허용 함수".
- HEAD는 GET과 같은 처리 뒤 `headOnly`로 본문만 뺀다 (결정 5).

## 9. 정적 파일 읽기

일반 파일은 `poll()` 없이 읽어도 되지만 루프를 멈추게 하면 안 된다 (raw/subject.md:134, raw/evaluation-sheet-en.md:59).

- 작은 파일(예: 1MB 이하)은 한 번에 읽어 `Response.body`에 넣는다.
- 큰 파일은 `FileSource`가 열어 두고, `Connection`이 `outBuf_`가 비어 갈 때마다 정해진 크기(예: 64KB)씩 읽어 채운다. `Content-Length`는 `stat` 크기로 미리 정한다.
- 업로드 저장도 같은 방식으로 나눠 쓸지는 단계 6에서 정한다.

## 10. CGI

```cpp
class CgiProcess {
public:
    CgiProcess(const RouteResult& route, const Request& req, const ListenAddr& local,
               const std::string& remoteAddr);
    bool start(EventLoop& loop);        // pipe, fork, execve. 실패하면 false → 500
    bool isFinished() const;
    Response takeResponse();            // CgiOutputParser 결과 또는 502/504
    void onTick(time_t now);            // 타임아웃이면 kill(SIGKILL)
    void reap();                        // waitpid(pid, &st, WNOHANG)
private:
    pid_t       pid_;
    CgiPipe*    stdinPipe_;             // 본문 쓰기 (EventLoop 소유)
    CgiPipe*    stdoutPipe_;            // 출력 읽기 (EventLoop 소유)
    std::string output_;
    time_t      startedAt_;
};
```

- `CgiEnv`가 메타변수 배열을 만든다. php-cgi용 `REDIRECT_STATUS`·`SCRIPT_FILENAME`을 넣고 `REDIRECT_URL`은 넣지 않는다 → [[concepts/cgi]] "메타변수".
- 자식: `dup2`로 표준 입출력 연결 → 필요 없는 fd 모두 `close` → 스크립트 디렉토리로 `chdir` → `execve`. `execve` 실패 시 자식 종료 방법은 [[analysis/subject-vs-evaluation]] 1.4절.
- 출력 pipe는 `POLLHUP`만 와도 `read`해서 0(EOF)을 확인한다. 입력 pipe는 본문을 다 쓰면 닫는다 → [[concepts/cgi]] "1. 호출 절차" 설계 제약.
- 판정은 종료 코드가 아니라 출력으로 한다: 형식이 맞으면 그 응답, 아니면 502, 타임아웃이면 504 → [[concepts/cgi]] "5. 실패 처리".
- `Connection`이 먼저 닫혀도 `CgiProcess`는 자식을 `kill`하고 회수할 때까지 남아 있어야 한다. 소유: `CgiProcess`는 별도 목록(`CgiRegistry`)이 갖고, `Connection`은 포인터만 쥔다.

## 11. 에러 처리 방침

| 종류 | 처리 |
|---|---|
| 설정 오류, listen 실패 (`bind` 등) | 원인 메시지를 stderr에 쓰고 종료 코드 1로 끝낸다 |
| 요청 오류 (파싱, 라우팅) | 해당 4xx 응답. 연결 유지 여부는 [[concepts/connection-management]] |
| 처리 중 서버 문제 (파일 열기 실패, `fork` 실패) | 500 (권한 문제면 403, 없으면 404) |
| 메모리 부족 (`std::bad_alloc`) | 그 연결만 닫는다. 서버는 계속 돈다 |
| 소켓 I/O -1·0 | 그 연결만 닫는다 |

- 예외는 설정 파싱과 handler 내부에서만 쓰고, `EventLoop::dispatch`가 handler 하나에서 나온 예외를 잡아 그 handler만 정리한다. 서버 프로세스는 어떤 요청에도 끝나지 않아야 한다 (raw/evaluation-sheet-en.md:24).

## 12. 시그널

- `SIGPIPE` → `SIG_IGN`. `SIGINT`·`SIGTERM` → 핸들러가 `volatile sig_atomic_t` 플래그만 세운다. `SIGCHLD`는 기본 동작 → [[concepts/resilience]] "시그널 처리".
- 종료 시: 모든 CGI 자식 `kill` + `waitpid`, 모든 fd `close`, 모든 handler `delete` 뒤 `main`에서 반환한다 (valgrind에서 "All heap blocks were freed"가 나와야 함, [[sources/valgrind-observed-sigint]]).

## 13. 상수 (초기값, 시험하며 조정)

| 이름 | 값 | 비고 |
|---|---|---|
| `kPollTimeoutMs` | 1000 | 타이머 점검 주기 |
| `kRecvBufferSize` | 65536 | `recv` 1번 크기 |
| `kMaxRequestLine` | 8192 | 넘으면 414 |
| `kMaxHeaderBytes` | 16384 | 넘으면 431 |
| `kHeaderTimeout` | 30초 | |
| `kBodyTimeout` | 30초 (무입력 기준) | |
| `kSendTimeout` | 30초 (무진행 기준) | |
| `kKeepAliveTimeout` | 15초 | |
| `kCgiTimeout` | 10초 | 무한 루프 스크립트 시연 |
| `kDrainIdle` / `kDrainTotal` | 1초 / 5초 | 413 실측에서 쓴 값 |
| `kMaxInternalRedirects` | 10 | NGINX와 같음 |
| `kDefaultMaxBodySize` | 1MB | NGINX 기본값과 같음 |

## 14. 정해야 할 것

- 설정 파일 문법의 세부 (지시자 이름, 단위 표기 `1m` 지원 여부). NGINX와 같게 할지 단순화할지.
- 업로드 저장을 한 번에 쓸지 나눠 쓸지 (9절).
- 위 상수 값.
- `Date` 헤더를 보낼지 (`<ctime>` 사용을 평가자와 합의할지).
