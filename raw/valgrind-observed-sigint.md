# valgrind 실측: SIGINT로 끝난 프로세스의 누수 보고

> 측정일: 2026-10-15. Ubuntu 24.04 공식 Docker 이미지에 g++와 valgrind를 설치하고, heap을 할당한 뒤 SIGINT를 기다리는 C++98 프로그램을 valgrind로 실행한 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). SIGINT는 터미널 Ctrl-C 대신 `kill -INT <pid>`로 보냈다. valgrind 출력 줄 앞의 `==<pid>==`는 `==PID==`로 바꿨다.

## 목적

1. SIGINT 기본 동작으로 종료하면 valgrind가 해제하지 않은 heap을 어떻게 보고하는지
2. 핸들러를 두고 정상 종료할 때, 해제 여부와 종료 방식(`return`, `exit`)에 따라 보고가 어떻게 달라지는지

## 환경

```
base image: ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55   (ubuntu:24.04, arm64)
```

### Dockerfile

```
FROM ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends g++ valgrind procps && rm -rf /var/lib/apt/lists/*
```

## 프로그램 (`sigleak.cpp`)

```cpp
// Allocates heap memory, waits for SIGINT, then ends in one of four ways.
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <unistd.h>

static volatile sig_atomic_t g_stop = 0;

static void onSignal(int) { g_stop = 1; }

int main(int argc, char** argv)
{
    const char* mode = argc > 1 ? argv[1] : "default";
    const int kBlocks = 10;
    char** blocks = new char*[kBlocks];
    for (int i = 0; i < kBlocks; ++i)
        blocks[i] = new char[100];

    if (std::strcmp(mode, "default") != 0)
        std::signal(SIGINT, onSignal);
    while (!g_stop)
        pause();

    if (std::strcmp(mode, "cleanup") == 0) {
        for (int i = 0; i < kBlocks; ++i)
            delete[] blocks[i];
        delete[] blocks;
        return 0;
    }
    if (std::strcmp(mode, "exit") == 0)
        std::exit(0);
    return 0;  // mode "return": main returns without freeing
}
```

모드: `default`는 핸들러 없음. 나머지는 SIGINT 핸들러를 두고 깨어난 뒤 `return`(해제 없이 `main` 반환), `exit`(해제 없이 `std::exit(0)`), `cleanup`(모두 해제 후 반환).

## 명령

```
docker build -t webserv-valgrind-test .
docker run --rm -v $S/sigleak.cpp:/src/sigleak.cpp:ro -v $S/run.sh:/run.sh:ro webserv-valgrind-test timeout 120 /run.sh > out.txt 2>&1
```

### run.sh

```sh
#!/bin/sh
# For each mode: run the program under valgrind in the foreground (so SIGINT keeps its
# default disposition), send it SIGINT from a background helper, print valgrind's report.
valgrind --version
g++ --version | head -1
g++ -std=c++98 -Wall -Wextra -Werror -g -o /tmp/sigleak /src/sigleak.cpp
for mode in default return exit cleanup; do
    echo "## mode=$mode"
    echo "\$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak $mode   (kill -INT <pid> after 2s)"
    ( sleep 2; kill -INT $(pgrep -f "/tmp/sigleak $mode") ) &
    valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak $mode 2>/tmp/vg.txt
    echo "[exit=$?]"
    wait
    sed 's/^==[0-9]*==/==PID==/' /tmp/vg.txt
    echo
done
```

## 출력

```
valgrind-3.22.0
g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
## mode=default
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak default   (kill -INT <pid> after 2s)
[exit=130]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak default
==PID== 
==PID== 
==PID== Process terminating with default action of signal 2 (SIGINT)
==PID==    at 0x4C16A10: pause (pause.c:31)
==PID==    by 0x1089F3: main (sigleak.cpp:22)
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 74,808 bytes in 12 blocks
==PID==   total heap usage: 12 allocs, 0 frees, 74,808 bytes allocated
==PID== 
==PID== 80 bytes in 1 blocks are still reachable in loss record 1 of 3
==PID==    at 0x4886FFC: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x108983: main (sigleak.cpp:15)
==PID== 
==PID== 1,000 bytes in 10 blocks are still reachable in loss record 2 of 3
==PID==    at 0x4886FFC: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x1089A7: main (sigleak.cpp:17)
==PID== 
==PID== 73,728 bytes in 1 blocks are still reachable in loss record 3 of 3
==PID==    at 0x4885250: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x4965863: ??? (in /usr/lib/aarch64-linux-gnu/libstdc++.so.6.0.33)
==PID==    by 0x4004B13: call_init (dl-init.c:74)
==PID==    by 0x4004B13: call_init (dl-init.c:26)
==PID==    by 0x4004C23: _dl_init (dl-init.c:121)
==PID==    by 0x401AA77: (below main) (dl-start.S:46)
==PID== 
==PID== LEAK SUMMARY:
==PID==    definitely lost: 0 bytes in 0 blocks
==PID==    indirectly lost: 0 bytes in 0 blocks
==PID==      possibly lost: 0 bytes in 0 blocks
==PID==    still reachable: 74,808 bytes in 12 blocks
==PID==         suppressed: 0 bytes in 0 blocks
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)

## mode=return
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak return   (kill -INT <pid> after 2s)
[exit=0]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak return
==PID== 
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 1,080 bytes in 11 blocks
==PID==   total heap usage: 12 allocs, 1 frees, 74,808 bytes allocated
==PID== 
==PID== 1,000 bytes in 10 blocks are indirectly lost in loss record 1 of 2
==PID==    at 0x4886FFC: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x1089A7: main (sigleak.cpp:17)
==PID== 
==PID== 1,080 (80 direct, 1,000 indirect) bytes in 1 blocks are definitely lost in loss record 2 of 2
==PID==    at 0x4886FFC: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x108983: main (sigleak.cpp:15)
==PID== 
==PID== LEAK SUMMARY:
==PID==    definitely lost: 80 bytes in 1 blocks
==PID==    indirectly lost: 1,000 bytes in 10 blocks
==PID==      possibly lost: 0 bytes in 0 blocks
==PID==    still reachable: 0 bytes in 0 blocks
==PID==         suppressed: 0 bytes in 0 blocks
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 0 from 0)

## mode=exit
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak exit   (kill -INT <pid> after 2s)
[exit=0]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak exit
==PID== 
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 1,080 bytes in 11 blocks
==PID==   total heap usage: 12 allocs, 1 frees, 74,808 bytes allocated
==PID== 
==PID== 80 bytes in 1 blocks are still reachable in loss record 1 of 2
==PID==    at 0x4886FFC: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x108983: main (sigleak.cpp:15)
==PID== 
==PID== 1,000 bytes in 10 blocks are still reachable in loss record 2 of 2
==PID==    at 0x4886FFC: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x1089A7: main (sigleak.cpp:17)
==PID== 
==PID== LEAK SUMMARY:
==PID==    definitely lost: 0 bytes in 0 blocks
==PID==    indirectly lost: 0 bytes in 0 blocks
==PID==      possibly lost: 0 bytes in 0 blocks
==PID==    still reachable: 1,080 bytes in 11 blocks
==PID==         suppressed: 0 bytes in 0 blocks
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)

## mode=cleanup
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak cleanup   (kill -INT <pid> after 2s)
[exit=0]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak cleanup
==PID== 
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 0 bytes in 0 blocks
==PID==   total heap usage: 12 allocs, 12 frees, 74,808 bytes allocated
==PID== 
==PID== All heap blocks were freed -- no leaks are possible
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)

```
