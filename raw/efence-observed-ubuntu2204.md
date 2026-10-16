# Electric Fence 실측 (Ubuntu 22.04): 누수 보고 여부

> 측정일: 2026-10-16. 평가 PC와 같은 Ubuntu 22.04 이미지(`raw/ubuntu2204-observed-tools.md`의 `webserv-u2204`)에 apt 패키지 electric-fence를 설치하고, 패키지 문서를 읽은 뒤 C++98 테스트 프로그램 세 개를 Electric Fence로 실행한 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 이미지가 man·doc 파일을 설치하지 않으므로 문서는 `apt-get download`로 받은 `.deb`을 `dpkg-deb -x`로 풀어 읽었다. man page는 macOS의 `mandoc -T utf8 | col -b`로 렌더링했다. SIGINT는 `kill -INT <pid>`로 보냈다.

## 목적

평가표가 누수 검사 도구로 드는 `e_fence`가 해제하지 않은 heap(SIGINT 종료 포함)을 보고하는지.

## 환경

```
base image: webserv-u2204 (FROM ubuntu@sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401, raw/ubuntu2204-observed-tools.md 참고)
```

### Dockerfile

```
FROM webserv-u2204
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends electric-fence man-db && rm -rf /var/lib/apt/lists/*
```

### 패키지

```
$ apt-get download electric-fence; sha256sum *.deb
electric-fence_2.2.6_arm64.deb
0a98196eb9c0fa14e385c64459830ec0132d2be4221395c41c329fa7a9da613f  electric-fence_2.2.6_arm64.deb
```

## 패키지 문서

### `/usr/share/man/man3/libefence.3.gz` (렌더링 결과 312줄 중 1-75줄 발췌)

```
efence(3)		   Library Functions Manual		     efence(3)

NAME
       efence - Electric Fence Malloc Debugger

SYNOPSIS
       #include <stdlib.h>

       void * malloc (size_t size);

       void free (void *ptr);

       void * realloc (void *ptr, size_t size);

       void * calloc (size_t nelem, size_t elsize);

       void * memalign (size_t alignment, size_t size);

       int posix_memalign (void ** memptr, size_t alignment, size_t size);

       void * valloc (size_t size);

       extern int EF_DISABLE_BANNER;

       extern int EF_ALIGNMENT;

       extern int EF_PROTECT_BELOW;

       extern int EF_PROTECT_FREE;

       extern int EF_ALLOW_MALLOC_0;

       extern int EF_FILL;

DESCRIPTION
       Electric Fence helps you detect two common programming bugs: software
       that overruns the boundaries of a malloc() memory allocation, and
       software that touches a memory allocation that has been released by
       free(). Unlike other malloc() debuggers, Electric Fence will detect
       read accesses as well as writes, and it will pinpoint the exact
       instruction that causes an error. It has been in use at Pixar since
       1987, and at many other sites for years.

       Electric Fence uses the virtual memory hardware of your computer to
       place an inaccessible memory page immediately after (or before, at the
       user's option) each memory allocation. When software reads or writes
       this inaccessible page, the hardware issues a segmentation fault,
       stopping the program at the offending instruction. It is then trivial
       to find the erroneous statement using your favorite debugger. In a
       similar manner, memory that has been released by free() is made
       inaccessible, and any code that touches it will get a segmentation
       fault.

       Simply linking your application with libefence.a will allow you to
       detect most, but not all, malloc buffer overruns and accesses of free
       memory.	If you want to be reasonably sure that you've found all bugs
       of this type, you'll have to read and understand the rest of this man
       page.

USAGE
       Link your program with the library libefence.a .  Make sure you are not
       linking with -lmalloc, -lmallocdebug, or with other malloc-debugger or
       malloc-enhancer libraries.  You can only use one at a time.  If your
       system administrator has installed Electric Fence for public use,
       you'll be able to use the -lefence argument to the linker, otherwise
       you'll have to put the path-name for libefence.a in the linker's
       command line.  You can also use dynamic linking. If you're using a
       Bourne shell, the statement export LD_PRELOAD=libefence.so.0.0 will
       cause Electric Fence to be loaded to run all dynamic executables.  The
       command ef command runs a single command under Electric Fence.

       Some systems will require special arguments to the linker to assure
       that you are using the Electric Fence malloc() and not the one from
       your C library.

```

### `/usr/share/doc/electric-fence/README` (전문)

```
This is Electric Fence 2.2

Electric Fence is a different kind of malloc() debugger. It uses the virtual
memory hardware of your system to detect when software overruns the boundaries
of a malloc() buffer. It will also detect any accesses of memory that has
been released by free(). Because it uses the VM hardware for detection,
Electric Fence stops your program on the first instruction that causes
a bounds violation. It's then trivial to use a debugger to display the
offending statement.

This version should run on all systems that support POSIX mmap() and
mprotect(). This includes Linux, Unix, and I think even BeOS.

Complete information on the use of Electric Fence is in the manual page
libefence.3 .

	Thanks

	Bruce Perens
	bruce@perens.com
```

### `/usr/share/doc/electric-fence/README.Debian` (전문)

```
electric-fence for DEBIAN
-------------------------

This package has been orphaned for a while now, so Matthew Vernon
<matthew@debian.org> has taken it up (the next paragraph is superceded by
this one). Note also that I've moved the manpage back to libefence.3

The official maintainer of this package is Siggy Brentrup <bsb@debian.org>.
But he apparently lost his net.access, so this version was made
by joost witteveen, <joostje@debian.org>. 

This package now also contains a shared library of electric fence.
Thus, you don't need to recompile any programmes any more, all
you need to do is

LD_PRELOAD=libefence.so.0.0  your-buggy-programme

and efence's malloc will be used.

Oh, and note that if you're using c++, you and want to statically link
your c++ programmes, you shouldn't use g++ to link libefence.a, but
rather
    gcc -o myprog myprog.o -lstdc++ -lg++ -lefence 
(if you use g++, the order is different, and efence's malloc doesn't get used)


```

## 프로그램

`sigleak.cpp`는 `raw/valgrind-observed-sigint.md`의 것과 같은 파일이다 (`diff`로 확인). 모드: `default`(핸들러 없음), `return`(해제 없이 `main` 반환), `exit`(해제 없이 `std::exit(0)`), `cleanup`(모두 해제 후 반환).

### `sigleak.cpp`

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

### `lost.cpp` (대조: 포인터를 잃고 정상 종료)

```cpp
// Control: loses the only pointer to heap blocks, then exits normally.
#include <cstdio>

static char** g_sink = 0;

int main()
{
    char** blocks = new char*[10];
    for (int i = 0; i < 10; ++i)
        blocks[i] = new char[100];
    g_sink = blocks;
    g_sink = 0;      // drop the only reference
    blocks = 0;
    std::printf("lost pointer, exiting\n");
    return 0;
}
```

### `overrun.cpp` (대조: heap 블록 끝을 1바이트 넘겨 씀)

```cpp
// Control: writes one byte past the end of a heap block.
#include <cstdio>

int main()
{
    char* block = new char[100];
    std::printf("writing block[100]\n");
    std::fflush(stdout);
    block[100] = 'x';
    std::printf("still running after overrun\n");
    delete[] block;
    return 0;
}
```

## 명령

```
docker build -t webserv-u2204-efence .
docker run --rm -v $D/src:/src:ro -v $D/run.sh:/run.sh:ro webserv-u2204-efence timeout 120 /run.sh > out.txt 2>&1
```

### run.sh

```sh
#!/bin/sh
# Builds the test programs, then runs each with Electric Fence preloaded
# (LD_PRELOAD, as README.Debian describes) and linked (-lefence).
dpkg-query -W electric-fence g++
g++ --version | head -1
for p in sigleak lost overrun; do
    g++ -std=c++98 -Wall -Wextra -Werror -g -o /tmp/$p /src/$p.cpp
    g++ -std=c++98 -Wall -Wextra -Werror -g -o /tmp/$p-linked /src/$p.cpp -lefence
done
for mode in default return exit cleanup; do
    echo "## mode=$mode (LD_PRELOAD)"
    echo "\$ LD_PRELOAD=libefence.so.0.0 /tmp/sigleak $mode   (kill -INT <pid> after 2s)"
    ( sleep 2; kill -INT $(pgrep -f "/tmp/sigleak $mode") ) &
    LD_PRELOAD=libefence.so.0.0 /tmp/sigleak $mode
    echo "[exit=$?]"
    wait
    echo
done
for mode in default cleanup; do
    echo "## mode=$mode (-lefence)"
    echo "\$ /tmp/sigleak-linked $mode   (kill -INT <pid> after 2s)"
    ( sleep 2; kill -INT $(pgrep -f "/tmp/sigleak-linked $mode") ) &
    /tmp/sigleak-linked $mode
    echo "[exit=$?]"
    wait
    echo
done
echo "## lost (LD_PRELOAD)"
echo "\$ LD_PRELOAD=libefence.so.0.0 /tmp/lost"
LD_PRELOAD=libefence.so.0.0 /tmp/lost
echo "[exit=$?]"
echo
echo "## lost (-lefence)"
echo "\$ /tmp/lost-linked"
/tmp/lost-linked
echo "[exit=$?]"
echo
echo "## overrun (no Electric Fence)"
echo "\$ /tmp/overrun"
/tmp/overrun
echo "[exit=$?]"
echo
echo "## overrun (LD_PRELOAD)"
echo "\$ LD_PRELOAD=libefence.so.0.0 /tmp/overrun"
LD_PRELOAD=libefence.so.0.0 /tmp/overrun
echo "[exit=$?]"
echo
echo "## overrun (-lefence)"
echo "\$ /tmp/overrun-linked"
/tmp/overrun-linked
echo "[exit=$?]"
```

## 출력

```
electric-fence	2.2.6
g++	4:11.2.0-1ubuntu1
g++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0
## mode=default (LD_PRELOAD)
$ LD_PRELOAD=libefence.so.0.0 /tmp/sigleak default   (kill -INT <pid> after 2s)

  Electric Fence 2.2 Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
[exit=130]

## mode=return (LD_PRELOAD)
$ LD_PRELOAD=libefence.so.0.0 /tmp/sigleak return   (kill -INT <pid> after 2s)

  Electric Fence 2.2 Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
[exit=0]

## mode=exit (LD_PRELOAD)
$ LD_PRELOAD=libefence.so.0.0 /tmp/sigleak exit   (kill -INT <pid> after 2s)

  Electric Fence 2.2 Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
[exit=0]

## mode=cleanup (LD_PRELOAD)
$ LD_PRELOAD=libefence.so.0.0 /tmp/sigleak cleanup   (kill -INT <pid> after 2s)

  Electric Fence 2.2 Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
[exit=0]

## mode=default (-lefence)
$ /tmp/sigleak-linked default   (kill -INT <pid> after 2s)
[exit=130]

## mode=cleanup (-lefence)
$ /tmp/sigleak-linked cleanup   (kill -INT <pid> after 2s)
[exit=0]

## lost (LD_PRELOAD)
$ LD_PRELOAD=libefence.so.0.0 /tmp/lost

  Electric Fence 2.2 Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
lost pointer, exiting
[exit=0]

## lost (-lefence)
$ /tmp/lost-linked
lost pointer, exiting
[exit=0]

## overrun (no Electric Fence)
$ /tmp/overrun
writing block[100]
still running after overrun
[exit=0]

## overrun (LD_PRELOAD)
$ LD_PRELOAD=libefence.so.0.0 /tmp/overrun

  Electric Fence 2.2 Copyright (C) 1987-1999 Bruce Perens <bruce@perens.com>
writing block[100]
Segmentation fault
[exit=139]

## overrun (-lefence)
$ /tmp/overrun-linked
writing block[100]
still running after overrun
[exit=0]
```

## `-lefence`로 빌드한 바이너리의 링크 확인

위 실행과 별도의 컨테이너에서 `run.sh`와 같은 명령으로 `overrun.cpp`를 다시 빌드한 뒤 확인했다. `ldd` 출력의 주소 `(0x…)`는 지웠다.

```
$ ldd /tmp/overrun-linked
	linux-vdso.so.1
	libstdc++.so.6 => /lib/aarch64-linux-gnu/libstdc++.so.6
	libc.so.6 => /lib/aarch64-linux-gnu/libc.so.6
	libm.so.6 => /lib/aarch64-linux-gnu/libm.so.6
	/lib/ld-linux-aarch64.so.1
	libgcc_s.so.1 => /lib/aarch64-linux-gnu/libgcc_s.so.1
```
