# OS 실측: pipe의 poll revents

> 측정일: 2026-10-15. 아래 소스를 각 환경에서 컴파일해 실행한 출력을 그대로 붙였다 (포트 번호는 실행마다 다르다).
> 측정: Claude Code 세션 (위키 유지 LLM). 평가 머신이 아닌 개발 Mac과 Docker 컨테이너에서 측정했다.

## 목적

pipe 한쪽 끝이 닫혔을 때 반대쪽 끝을 `poll()`하면 `revents`에 어떤 비트가 오는지, 그 뒤 `write()`·`read()` 결과를 확인한다. CGI 입력·출력 pipe 처리에 쓴다. 테스트 프로그램은 `SIGPIPE`를 무시하도록 설정한다.

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

### pipepoll.c

```c
/* revents reported by poll() on pipe ends after the other end is closed. */
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include "common.h"

static void show(const char *label, int fd, short events) {
    struct pollfd p;
    int r;
    p.fd = fd;
    p.events = events;
    p.revents = 0;
    r = poll(&p, 1, 0);
    printf("%-52s poll=%d revents=0x%03x [%s%s%s%s%s ]\n", label, r, p.revents,
           p.revents & POLLIN ? " POLLIN" : "", p.revents & POLLOUT ? " POLLOUT" : "",
           p.revents & POLLERR ? " POLLERR" : "", p.revents & POLLHUP ? " POLLHUP" : "",
           p.revents & POLLNVAL ? " POLLNVAL" : "");
}

int main(void) {
    int fds[2];
    char b[8];
    ssize_t n;

    signal(SIGPIPE, SIG_IGN);

    pipe(fds);
    close(fds[0]);
    show("[1] read end closed, poll write end (POLLOUT)", fds[1], POLLOUT);
    n = write(fds[1], "x", 1);
    printf("%-52s write=%zd %s\n", "    write() after that", n, n < 0 ? err_name(errno) : "");
    close(fds[1]);

    pipe(fds);
    fcntl(fds[1], F_SETFL, O_NONBLOCK);
    close(fds[0]);
    show("[2] same, write end O_NONBLOCK", fds[1], POLLOUT);
    close(fds[1]);

    pipe(fds);
    close(fds[1]);
    show("[3] write end closed, no data, poll read end (POLLIN)", fds[0], POLLIN);
    n = read(fds[0], b, sizeof b);
    printf("%-52s read=%zd\n", "    read() after that", n);
    close(fds[0]);

    pipe(fds);
    write(fds[1], "abc", 3);
    close(fds[1]);
    show("[4] write end closed, 3 bytes left, poll read end", fds[0], POLLIN);
    n = read(fds[0], b, sizeof b);
    printf("%-52s read=%zd\n", "    read() #1", n);
    show("    after reading all data", fds[0], POLLIN);
    n = read(fds[0], b, sizeof b);
    printf("%-52s read=%zd\n", "    read() #2", n);
    close(fds[0]);

    pipe(fds);
    close(fds[1]);
    show("[5] write end closed, events=0 (nothing requested)", fds[0], 0);
    close(fds[0]);
    return 0;
}
```

## 명령

```
# macOS
cc -Wall -o pipepoll pipepoll.c && ./pipepoll
# Ubuntu
docker run --rm -v "$PWD":/src:ro ubuntu:24.04 bash -c 'apt-get update -qq && apt-get install -y -qq gcc libc6-dev; cd /tmp; gcc -Wall -o pipepoll /src/pipepoll.c && ./pipepoll'
```

## 출력

### pipepoll — macOS

```
[1] read end closed, poll write end (POLLOUT)        poll=1 revents=0x010 [ POLLHUP ]
    write() after that                               write=-1 EPIPE
[2] same, write end O_NONBLOCK                       poll=1 revents=0x010 [ POLLHUP ]
[3] write end closed, no data, poll read end (POLLIN) poll=1 revents=0x011 [ POLLIN POLLHUP ]
    read() after that                                read=0
[4] write end closed, 3 bytes left, poll read end    poll=1 revents=0x011 [ POLLIN POLLHUP ]
    read() #1                                        read=3
    after reading all data                           poll=1 revents=0x011 [ POLLIN POLLHUP ]
    read() #2                                        read=0
[5] write end closed, events=0 (nothing requested)   poll=0 revents=0x000 [ ]
```

### pipepoll — Ubuntu

```
[1] read end closed, poll write end (POLLOUT)        poll=1 revents=0x00c [ POLLOUT POLLERR ]
    write() after that                               write=-1 EPIPE
[2] same, write end O_NONBLOCK                       poll=1 revents=0x00c [ POLLOUT POLLERR ]
[3] write end closed, no data, poll read end (POLLIN) poll=1 revents=0x010 [ POLLHUP ]
    read() after that                                read=0
[4] write end closed, 3 bytes left, poll read end    poll=1 revents=0x011 [ POLLIN POLLHUP ]
    read() #1                                        read=3
    after reading all data                           poll=1 revents=0x010 [ POLLHUP ]
    read() #2                                        read=0
[5] write end closed, events=0 (nothing requested)   poll=1 revents=0x010 [ POLLHUP ]
```
