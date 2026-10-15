# OS 실측: bind 재시작·와일드카드 충돌

> 측정일: 2026-10-15. 아래 소스를 각 환경에서 컴파일해 실행한 출력을 그대로 붙였다 (포트 번호는 실행마다 다르다).
> 측정: Claude Code 세션 (위키 유지 LLM). 평가 머신이 아닌 개발 Mac과 Docker 컨테이너에서 측정했다.

## 목적

서버 재시작 직후 같은 포트 `bind` 실패 여부와 `SO_REUSEADDR`의 효과(`reuse`), `0.0.0.0:P`와 `127.0.0.1:P`를 함께 listen할 때 충돌 여부(`wildcard`)를 확인한다. POSIX `bind()` 문서로는 정해지지 않는다.

## 환경

### macOS (개발 환경)

```
ProductName:  macOS ProductVersion:  26.6.2 BuildVersion:  25G83 
Darwin 25.6.0 arm64
Apple clang version 21.0.0 (clang-2100.3.34.2)
```

### Ubuntu (Docker 컨테이너, OrbStack)

```
Ubuntu 24.04.5 LTS
Linux 7.0.14-orbstack-00380-ga7e0a2dc9535 aarch64
gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
image: ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
```

컨테이너의 커널은 OrbStack VM의 Linux 커널이다. 평가 머신의 Ubuntu 커널과 버전이 다를 수 있다.

## 소스

### common.h

```c
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static const char *err_name(int e) {
    switch (e) {
    case 0: return "OK";
    case EADDRINUSE: return "EADDRINUSE";
    case EACCES: return "EACCES";
    case EINVAL: return "EINVAL";
    case EPIPE: return "EPIPE";
    default: return strerror(e);
    }
}

/* Bind (and optionally listen) a TCP socket; returns fd or -1, prints result. */
static int bind_tcp(const char *label, const char *ip, unsigned short port, int reuse, int do_listen) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a;
    int r, e;
    if (reuse) {
        int one = 1;
        setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
    }
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_port = htons(port);
    inet_pton(AF_INET, ip, &a.sin_addr);
    r = bind(fd, (struct sockaddr *)&a, sizeof a);
    e = errno;
    printf("%-44s bind(%s:%u, SO_REUSEADDR=%d) = %d %s", label, ip, port, reuse, r, r ? err_name(e) : "OK");
    if (r == 0 && do_listen) {
        r = listen(fd, 8);
        e = errno;
        printf(", listen = %d %s", r, r ? err_name(e) : "OK");
    }
    printf("\n");
    if (r != 0) { close(fd); return -1; }
    return fd;
}

static unsigned short port_of(int fd) {
    struct sockaddr_in a;
    socklen_t n = sizeof a;
    getsockname(fd, (struct sockaddr *)&a, &n);
    return ntohs(a.sin_port);
}
```

### reuse.c

```c
/* Rebind a port right after a server-side active close (TIME_WAIT on server). */
#include "common.h"

static unsigned short run_session(int server_closes_first, int listener_reuse) {
    int ls = bind_tcp("  listener", "127.0.0.1", 0, listener_reuse, 1);
    unsigned short port = port_of(ls);
    int c = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in a;
    char b;
    int s;
    memset(&a, 0, sizeof a);
    a.sin_family = AF_INET;
    a.sin_port = htons(port);
    inet_pton(AF_INET, "127.0.0.1", &a.sin_addr);
    connect(c, (struct sockaddr *)&a, sizeof a);
    s = accept(ls, NULL, NULL);
    if (server_closes_first) {
        close(s);                 /* server sends FIN first -> server side TIME_WAIT */
        read(c, &b, 1);           /* client sees EOF */
        close(c);
    } else {
        close(c);                 /* client closes first -> client side TIME_WAIT */
        read(s, &b, 1);
        close(s);
    }
    close(ls);
    usleep(100000);
    return port;
}

static void try_rebind(const char *label, unsigned short p, int reuse) {
    int fd = bind_tcp(label, "127.0.0.1", p, reuse, 1);
    if (fd >= 0)
        close(fd);   /* release so the next attempt is independent */
}

int main(void) {
    unsigned short p;
    printf("[A] server closed accepted socket first\n");
    p = run_session(1, 0);
    try_rebind("  rebind without SO_REUSEADDR", p, 0);
    try_rebind("  rebind with SO_REUSEADDR", p, 1);
    printf("[B] client closed first\n");
    p = run_session(0, 0);
    try_rebind("  rebind without SO_REUSEADDR", p, 0);
    try_rebind("  rebind with SO_REUSEADDR", p, 1);
    printf("[C] listener had SO_REUSEADDR=1, server closed accepted socket first\n");
    p = run_session(1, 1);
    try_rebind("  rebind without SO_REUSEADDR", p, 0);
    try_rebind("  rebind with SO_REUSEADDR", p, 1);
    return 0;
}
```

### wildcard.c

```c
/* Two listening sockets on the same port: 0.0.0.0 and 127.0.0.1. */
#include "common.h"

static unsigned short free_port(void) {
    int fd = bind_tcp("  (pick free port)", "0.0.0.0", 0, 0, 0);
    unsigned short p = port_of(fd);
    close(fd);
    return p;
}

static void pair(const char *first, const char *second, int reuse) {
    unsigned short p = free_port();
    int a, b;
    printf("[%s then %s, SO_REUSEADDR=%d on both]\n", first, second, reuse);
    a = bind_tcp("  first", first, p, reuse, 1);
    b = bind_tcp("  second", second, p, reuse, 1);
    if (a >= 0) close(a);
    if (b >= 0) close(b);
}

int main(void) {
    pair("0.0.0.0", "127.0.0.1", 0);
    pair("127.0.0.1", "0.0.0.0", 0);
    pair("0.0.0.0", "127.0.0.1", 1);
    pair("127.0.0.1", "0.0.0.0", 1);
    pair("127.0.0.1", "127.0.0.1", 1);
    return 0;
}
```

## 명령

```
# macOS
cc -Wall -o reuse reuse.c && ./reuse
cc -Wall -o wildcard wildcard.c && ./wildcard
# Ubuntu
docker run --rm -v "$PWD":/src:ro ubuntu:24.04 bash -c 'apt-get update -qq && apt-get install -y -qq gcc libc6-dev; cd /tmp; gcc -Wall -o reuse /src/reuse.c && ./reuse; gcc -Wall -o wildcard /src/wildcard.c && ./wildcard'
```

## 출력

### reuse — macOS

```
[A] server closed accepted socket first
  listener                                   bind(127.0.0.1:0, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  rebind without SO_REUSEADDR                bind(127.0.0.1:51549, SO_REUSEADDR=0) = -1 EADDRINUSE
  rebind with SO_REUSEADDR                   bind(127.0.0.1:51549, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
[B] client closed first
  listener                                   bind(127.0.0.1:0, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  rebind without SO_REUSEADDR                bind(127.0.0.1:51551, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  rebind with SO_REUSEADDR                   bind(127.0.0.1:51551, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
[C] listener had SO_REUSEADDR=1, server closed accepted socket first
  listener                                   bind(127.0.0.1:0, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  rebind without SO_REUSEADDR                bind(127.0.0.1:51553, SO_REUSEADDR=0) = -1 EADDRINUSE
  rebind with SO_REUSEADDR                   bind(127.0.0.1:51553, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
```

### reuse — Ubuntu

```
[A] server closed accepted socket first
  listener                                   bind(127.0.0.1:0, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  rebind without SO_REUSEADDR                bind(127.0.0.1:35845, SO_REUSEADDR=0) = -1 EADDRINUSE
  rebind with SO_REUSEADDR                   bind(127.0.0.1:35845, SO_REUSEADDR=1) = -1 EADDRINUSE
[B] client closed first
  listener                                   bind(127.0.0.1:0, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  rebind without SO_REUSEADDR                bind(127.0.0.1:58033, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  rebind with SO_REUSEADDR                   bind(127.0.0.1:58033, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
[C] listener had SO_REUSEADDR=1, server closed accepted socket first
  listener                                   bind(127.0.0.1:0, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  rebind without SO_REUSEADDR                bind(127.0.0.1:38033, SO_REUSEADDR=0) = -1 EADDRINUSE
  rebind with SO_REUSEADDR                   bind(127.0.0.1:38033, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
```

### wildcard — macOS

```
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[0.0.0.0 then 127.0.0.1, SO_REUSEADDR=0 on both]
  first                                      bind(0.0.0.0:51555, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  second                                     bind(127.0.0.1:51555, SO_REUSEADDR=0) = -1 EADDRINUSE
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[127.0.0.1 then 0.0.0.0, SO_REUSEADDR=0 on both]
  first                                      bind(127.0.0.1:51556, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  second                                     bind(0.0.0.0:51556, SO_REUSEADDR=0) = -1 EADDRINUSE
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[0.0.0.0 then 127.0.0.1, SO_REUSEADDR=1 on both]
  first                                      bind(0.0.0.0:51557, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  second                                     bind(127.0.0.1:51557, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[127.0.0.1 then 0.0.0.0, SO_REUSEADDR=1 on both]
  first                                      bind(127.0.0.1:51558, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  second                                     bind(0.0.0.0:51558, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[127.0.0.1 then 127.0.0.1, SO_REUSEADDR=1 on both]
  first                                      bind(127.0.0.1:51559, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  second                                     bind(127.0.0.1:51559, SO_REUSEADDR=1) = -1 EADDRINUSE
```

### wildcard — Ubuntu

```
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[0.0.0.0 then 127.0.0.1, SO_REUSEADDR=0 on both]
  first                                      bind(0.0.0.0:56673, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  second                                     bind(127.0.0.1:56673, SO_REUSEADDR=0) = -1 EADDRINUSE
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[127.0.0.1 then 0.0.0.0, SO_REUSEADDR=0 on both]
  first                                      bind(127.0.0.1:52709, SO_REUSEADDR=0) = 0 OK, listen = 0 OK
  second                                     bind(0.0.0.0:52709, SO_REUSEADDR=0) = -1 EADDRINUSE
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[0.0.0.0 then 127.0.0.1, SO_REUSEADDR=1 on both]
  first                                      bind(0.0.0.0:59801, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  second                                     bind(127.0.0.1:59801, SO_REUSEADDR=1) = -1 EADDRINUSE
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[127.0.0.1 then 0.0.0.0, SO_REUSEADDR=1 on both]
  first                                      bind(127.0.0.1:54083, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  second                                     bind(0.0.0.0:54083, SO_REUSEADDR=1) = -1 EADDRINUSE
  (pick free port)                           bind(0.0.0.0:0, SO_REUSEADDR=0) = 0 OK
[127.0.0.1 then 127.0.0.1, SO_REUSEADDR=1 on both]
  first                                      bind(127.0.0.1:45287, SO_REUSEADDR=1) = 0 OK, listen = 0 OK
  second                                     bind(127.0.0.1:45287, SO_REUSEADDR=1) = -1 EADDRINUSE
```
