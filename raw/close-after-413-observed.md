# 실측: 413 응답 뒤 연결을 닫는 방식과 클라이언트가 응답을 받는지

> 측정일: 2026-10-16. 요청 머리만 읽고 413을 보낸 뒤 세 가지 방식으로 연결을 끝내는 C++98 시험 서버를 만들고, 10MB 본문을 보내는 클라이언트(curl, Python)로 Ubuntu 22.04 Docker 컨테이너와 macOS에서 각각 실행한 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 서버와 클라이언트는 같은 호스트의 loopback(127.0.0.1)으로 통신했다.
> 주의: `run.sh`는 curl 응답 파일(`resp`)을 시도마다 지우지 않는다. 그래서 출력의 `body=` 값은 이전 시도에서 남은 내용일 수 있다. curl의 결과는 `http_code`와 `curl exit`로 본다.
> macOS에서는 이 출력 전에 두 번 실행했으나 버렸다: 첫 번째는 서버가 listen하기 전(0.3초 대기)에 curl이 접속해 실패한 뒤 멈췄고, 두 번째는 macOS에 `timeout` 명령이 없어 바로 끝났으며 멈춰 있던 첫 실행이 같은 출력 파일에 계속 써서 파일이 깨졌다. 아래 macOS 출력은 대기를 1초로 바꾼 세 번째 실행이다.

## 목적

`shutdown`이 허용 함수가 아닌 과제에서, 413처럼 본문을 다 읽지 않고 응답한 뒤 (1) 바로 `close()`하는 것과 (2) 들어오는 데이터를 읽어 버리다가 `close()`하는 것이 클라이언트가 응답을 받는 데 차이가 있는지. 참고로 (3) `shutdown(SHUT_WR)` 뒤 읽어 버리는 방식(NGINX lingering close)도 함께 본다.

## 시험 서버 (`srv413.cpp`)

```cpp
// Accepts one connection, reads only the request head, answers 413 with
// "Connection: close", then ends the connection in one of three ways:
//   close    - close() at once
//   drain    - read and discard until EOF, 1 s without data, or 5 s total; then close()
//   shutdown - shutdown(SHUT_WR) first, then drain as above (NGINX-style reference)
#include <arpa/inet.h>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <netinet/in.h>
#include <poll.h>
#include <string>
#include <sys/socket.h>
#include <unistd.h>

static long drain(int fd)
{
    char buf[65536];
    long total = 0;
    time_t start = time(0);
    while (time(0) - start < 5) {
        struct pollfd p;
        p.fd = fd;
        p.events = POLLIN;
        p.revents = 0;
        if (poll(&p, 1, 1000) <= 0)
            break;                       // 1 s without data
        ssize_t n = recv(fd, buf, sizeof(buf), 0);
        if (n <= 0)
            break;                       // EOF or error
        total += n;
    }
    return total;
}

int main(int argc, char** argv)
{
    if (argc != 3) {
        std::fprintf(stderr, "usage: srv413 PORT close|drain|shutdown\n");
        return 2;
    }
    const char* mode = argv[2];
    int lfd = socket(AF_INET, SOCK_STREAM, 0);
    int on = 1;
    setsockopt(lfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));
    sockaddr_in addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<unsigned short>(std::atoi(argv[1])));
    if (bind(lfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0
        || listen(lfd, 1) < 0) {
        std::perror("bind/listen");
        return 1;
    }
    int fd = accept(lfd, 0, 0);
    std::string head;
    char buf[4096];
    while (head.find("\r\n\r\n") == std::string::npos) {
        ssize_t n = recv(fd, buf, sizeof(buf), 0);
        if (n <= 0)
            return 1;
        head.append(buf, n);
    }
    const char* resp = "HTTP/1.1 413 Content Too Large\r\n"
                       "Content-Length: 9\r\n"
                       "Connection: close\r\n\r\n"
                       "too large";
    ssize_t sent = send(fd, resp, std::strlen(resp), 0);
    long drained = 0;
    if (std::strcmp(mode, "shutdown") == 0)
        shutdown(fd, SHUT_WR);
    if (std::strcmp(mode, "close") != 0)
        drained = drain(fd);
    close(fd);
    close(lfd);
    std::fprintf(stderr, "[server] mode=%s head_read=%lu sent=%ld drained=%ld\n",
                 mode, static_cast<unsigned long>(head.size()),
                 static_cast<long>(sent), drained);
    return 0;
}
```

## 클라이언트

### Python (`cli413.py`)

본문 전체를 `sendall()`로 보낸 뒤에야 읽기 시작한다.

```python
# Sends a request head with Content-Length N, then writes the whole body with
# sendall() before reading anything; prints what it could read back.
import socket, sys
port, size = int(sys.argv[1]), int(sys.argv[2])
s = socket.create_connection(("127.0.0.1", port))
s.sendall(b"POST /upload HTTP/1.1\r\nHost: localhost\r\nContent-Length: %d\r\n\r\n" % size)
try:
    s.sendall(b"a" * size)
    print("[client] body sent")
except OSError as e:
    print("[client] send error:", e)
data = b""
try:
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        data += chunk
    print("[client] recv EOF")
except OSError as e:
    print("[client] recv error:", e)
print("[client] received %d bytes, status line: %r" % (len(data), data.split(b"\r\n")[0]))
```

### curl

`-H 'Expect:'`로 `Expect: 100-continue`를 끄고 `--data-binary`로 10MB 파일을 보낸다 (아래 `run.sh`).

## Ubuntu 22.04 (Docker)

### Dockerfile (`webserv-u2204`는 `raw/ubuntu2204-observed-tools.md`의 이미지)

```
FROM webserv-u2204
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
```

### run.sh

```sh
#!/bin/sh
# For each close mode, run the server once per client attempt (3 attempts each
# for curl and the Python client) with a 10 MB body.
SIZE=10485760
curl --version | head -1
python3 --version
g++ -std=c++98 -Wall -Wextra -Werror -o /tmp/srv413 /src/srv413.cpp
head -c $SIZE /dev/zero | tr '\0' a > /tmp/body
port=9000
for mode in close drain shutdown; do
    for i in 1 2 3; do
        port=$((port + 1))
        echo "## mode=$mode client=curl try=$i"
        /tmp/srv413 $port $mode &
        sleep 0.3
        curl -sS -o /tmp/resp -w '[curl] http_code=%{http_code} size_upload=%{size_upload}\n' \
             -H 'Expect:' --data-binary @/tmp/body http://127.0.0.1:$port/upload
        echo "[curl exit=$?] body=$(cat /tmp/resp 2>/dev/null)"
        wait
        echo
    done
    for i in 1 2 3; do
        port=$((port + 1))
        echo "## mode=$mode client=python try=$i"
        /tmp/srv413 $port $mode &
        sleep 0.3
        python3 /src/cli413.py $port $SIZE
        wait
        echo
    done
done
```

### 명령

```
docker build -t webserv-u2204-curl .
docker run --rm -v $D/src:/src:ro -v $D/run.sh:/run.sh:ro webserv-u2204-curl timeout 300 /run.sh > out-linux.txt 2>&1
```

### 출력

```
curl 7.81.0 (aarch64-unknown-linux-gnu) libcurl/7.81.0 OpenSSL/3.0.2 zlib/1.2.11 brotli/1.0.9 zstd/1.4.8 libidn2/2.3.2 libpsl/0.21.0 (+libidn2/2.3.2) libssh/0.9.6/openssl/zlib nghttp2/1.43.0 librtmp/2.3 OpenLDAP/2.5.20
Python 3.10.12
## mode=close client=curl try=1
[server] mode=close head_read=4096 sent=81 drained=0
[curl] http_code=413 size_upload=1245184
[curl exit=0] body=too large

## mode=close client=curl try=2
[server] mode=close head_read=160 sent=81 drained=0
[curl] http_code=413 size_upload=0
[curl exit=0] body=too large

## mode=close client=curl try=3
[server] mode=close head_read=4096 sent=81 drained=0
[curl] http_code=413 size_upload=720896
[curl exit=0] body=too large

## mode=close client=python try=1
[server] mode=close head_read=68 sent=81 drained=0
[client] send error: [Errno 32] Broken pipe
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=close client=python try=2
[server] mode=close head_read=68 sent=81 drained=0
[client] send error: [Errno 32] Broken pipe
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=close client=python try=3
[server] mode=close head_read=68 sent=81 drained=0
[client] send error: [Errno 32] Broken pipe
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=drain client=curl try=1
[server] mode=drain head_read=4096 sent=81 drained=1241248
[curl] http_code=413 size_upload=1245184
[curl exit=0] body=too large

## mode=drain client=curl try=2
[server] mode=drain head_read=4096 sent=81 drained=61600
[curl] http_code=413 size_upload=65536
[curl exit=0] body=too large

## mode=drain client=curl try=3
[server] mode=drain head_read=4096 sent=81 drained=454816
[curl] http_code=413 size_upload=458752
[curl exit=0] body=too large

## mode=drain client=python try=1
[server] mode=drain head_read=68 sent=81 drained=10485760
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=drain client=python try=2
[server] mode=drain head_read=68 sent=81 drained=10485760
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=drain client=python try=3
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=drain head_read=68 sent=81 drained=10485760

## mode=shutdown client=curl try=1
[server] mode=shutdown head_read=4096 sent=81 drained=1765536
[curl] http_code=413 size_upload=1769472
[curl exit=0] body=too large

## mode=shutdown client=curl try=2
[server] mode=shutdown head_read=4096 sent=81 drained=1765536
[curl] http_code=413 size_upload=1769472
[curl exit=0] body=too large

## mode=shutdown client=curl try=3
[server] mode=shutdown head_read=4096 sent=81 drained=1437856
[curl] http_code=413 size_upload=1441792
[curl exit=0] body=too large

## mode=shutdown client=python try=1
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=shutdown head_read=68 sent=81 drained=10485760

## mode=shutdown client=python try=2
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=shutdown head_read=68 sent=81 drained=10485760

## mode=shutdown client=python try=3
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=shutdown head_read=4096 sent=81 drained=10481732

```

## macOS

```
$ sw_vers -productVersion
26.6.2
$ uname -mr
25.6.0 arm64
$ c++ --version | head -1
Apple clang version 21.0.0 (clang-2100.3.34.2)
```

### run-mac.sh

`run.sh`에서 경로를 작업 디렉토리(`$W`)로 바꾸고, 컴파일러를 `c++`로, 서버 기동 대기를 1초로 바꿨다.

```sh
#!/bin/sh
# For each close mode, run the server once per client attempt (3 attempts each
# for curl and the Python client) with a 10 MB body.
W=$1
SIZE=10485760
curl --version | head -1
python3 --version
c++ -std=c++98 -Wall -Wextra -Werror -o $W/srv413 $W/src/srv413.cpp
head -c $SIZE /dev/zero | LC_ALL=C tr "\000" a > $W/body
port=9000
for mode in close drain shutdown; do
    for i in 1 2 3; do
        port=$((port + 1))
        echo "## mode=$mode client=curl try=$i"
        $W/srv413 $port $mode &
        sleep 1
        curl -sS -o $W/resp -w '[curl] http_code=%{http_code} size_upload=%{size_upload}\n' \
             -H 'Expect:' --data-binary @$W/body http://127.0.0.1:$port/upload
        echo "[curl exit=$?] body=$(cat $W/resp 2>/dev/null)"
        wait
        echo
    done
    for i in 1 2 3; do
        port=$((port + 1))
        echo "## mode=$mode client=python try=$i"
        $W/srv413 $port $mode &
        sleep 1
        python3 $W/src/cli413.py $port $SIZE
        wait
        echo
    done
done
```

### 명령

```
./run-mac.sh $D > out-mac2.txt 2>&1
```

### 출력

```
curl 8.7.1 (x86_64-apple-darwin25.0) libcurl/8.7.1 (SecureTransport) LibreSSL/3.3.6 zlib/1.2.12 nghttp2/1.68.1
Python 3.14.7
## mode=close client=curl try=1
[server] mode=close head_read=4096 sent=81 drained=0
[curl] http_code=413 size_upload=327521
[curl exit=0] body=too large

## mode=close client=curl try=2
[server] mode=close head_read=4096 sent=81 drained=0
curl: (55) Send failure: Broken pipe
[curl] http_code=000 size_upload=130913
[curl exit=55] body=too large

## mode=close client=curl try=3
[server] mode=close head_read=4096 sent=81 drained=0
[curl] http_code=413 size_upload=393057
[curl exit=0] body=too large

## mode=close client=python try=1
[server] mode=close head_read=68 sent=81 drained=0
[client] send error: [Errno 32] Broken pipe
[client] recv error: [Errno 54] Connection reset by peer
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=close client=python try=2
[server] mode=close head_read=68 sent=81 drained=0
[client] send error: [Errno 32] Broken pipe
[client] recv error: [Errno 54] Connection reset by peer
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=close client=python try=3
[server] mode=close head_read=68 sent=81 drained=0
[client] send error: [Errno 32] Broken pipe
[client] recv error: [Errno 54] Connection reset by peer
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=drain client=curl try=1
[server] mode=drain head_read=4096 sent=81 drained=520192
[curl] http_code=413 size_upload=524129
[curl exit=0] body=too large

## mode=drain client=curl try=2
[server] mode=drain head_read=4096 sent=81 drained=454656
[curl] http_code=413 size_upload=458593
[curl exit=0] body=too large

## mode=drain client=curl try=3
[server] mode=drain head_read=4096 sent=81 drained=454656
[curl] http_code=413 size_upload=458593
[curl exit=0] body=too large

## mode=drain client=python try=1
[server] mode=drain head_read=68 sent=81 drained=10485760
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=drain client=python try=2
[server] mode=drain head_read=68 sent=81 drained=10485760
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=drain client=python try=3
[server] mode=drain head_read=68 sent=81 drained=10485760
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'

## mode=shutdown client=curl try=1
[server] mode=shutdown head_read=4096 sent=81 drained=454656
[curl] http_code=413 size_upload=458593
[curl exit=0] body=too large

## mode=shutdown client=curl try=2
[server] mode=shutdown head_read=4096 sent=81 drained=520192
[curl] http_code=413 size_upload=524129
[curl exit=0] body=too large

## mode=shutdown client=curl try=3
[server] mode=shutdown head_read=4096 sent=81 drained=454656
[curl] http_code=413 size_upload=458593
[curl exit=0] body=too large

## mode=shutdown client=python try=1
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=shutdown head_read=68 sent=81 drained=10485760

## mode=shutdown client=python try=2
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=shutdown head_read=68 sent=81 drained=10485760

## mode=shutdown client=python try=3
[client] body sent
[client] recv EOF
[client] received 81 bytes, status line: b'HTTP/1.1 413 Content Too Large'
[server] mode=shutdown head_read=68 sent=81 drained=10485760

```
