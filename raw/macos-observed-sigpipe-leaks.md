# macOS 실측: `MSG_NOSIGNAL`과 `leaks -atExit`의 SIGINT 종료 보고

> 측정일: 2026-10-16. macOS(개발 환경)에서 SDK 헤더를 출력하고, C++98 테스트 프로그램 세 개를 Apple clang으로 빌드해 실행한 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). SIGINT는 터미널 Ctrl-C 대신 `pkill -INT -x sigleak`로 보냈다. 출력의 `Path: /private/tmp/*/...`는 leaks가 출력한 그대로다.

## 목적

1. macOS가 `send`의 `MSG_NOSIGNAL` 플래그를 지원하는지
2. 평가표가 드는 누수 검사 도구 `leaks`가 SIGINT로 끝난 프로세스를 어떻게 보고하는지 (valgrind 측정 `raw/valgrind-observed-sigint.md`와 같은 프로그램)

## 환경

```
$ sw_vers
ProductName:		macOS
ProductVersion:		26.6.2
BuildVersion:		25G83
$ uname -mr
25.6.0 arm64
$ c++ --version | head -2
Apple clang version 21.0.0 (clang-2100.3.34.2)
Target: arm64-apple-darwin25.6.0
$ which leaks
/usr/bin/leaks
```

컴파일: `c++ -std=c++98 -Wall -Wextra -Werror` (`sigleak`, `lost`는 `-g`도 줌).

## 1. `MSG_NOSIGNAL`

### SDK 헤더

```
$ xcrun --show-sdk-path
/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk
$ sed -n 160,170p $SDK/usr/include/sys/socket.h
#define SO_RCVTIMEO     0x1006          /* receive timeout */
#define SO_ERROR        0x1007          /* get error status and clear */
#define SO_TYPE         0x1008          /* get socket type */
#if !defined(_POSIX_C_SOURCE) || defined(_DARWIN_C_SOURCE)
#define SO_LABEL        0x1010          /* deprecated */
#define SO_PEERLABEL    0x1011          /* deprecated */
#ifdef __APPLE__
#define SO_NREAD        0x1020          /* APPLE: get 1st-packet byte count */
#define SO_NKE          0x1021          /* APPLE: Install socket-level NKE */
#define SO_NOSIGPIPE    0x1022          /* APPLE: No SIGPIPE on EPIPE */
#define SO_NOADDRERR    0x1023          /* APPLE: Returns EADDRNOTAVAIL when src is not available anymore */
$ sed -n 593,597p $SDK/usr/include/sys/socket.h
#endif  /* (!_POSIX_C_SOURCE || _DARWIN_C_SOURCE) */

#if __DARWIN_C_LEVEL >= 200809L
#define MSG_NOSIGNAL    0x80000         /* do not generate SIGPIPE on EOF */
#endif /* __DARWIN_C_LEVEL */
```

### 프로그램 (`nosig.cpp`)

loopback TCP 연결을 만들고 클라이언트 쪽을 닫은 뒤, 서버 쪽 소켓에 `send`를 세 번 한다. 모드: `plain`(플래그 없음), `msg_nosignal`(`send` flags에 `MSG_NOSIGNAL`), `so_nosigpipe`(`setsockopt(SO_NOSIGPIPE)`). 이 테스트 프로그램은 반환값 검사를 생략했다.

```cpp
// Sends to a TCP peer that has closed, using one of three SIGPIPE strategies.
#include <arpa/inet.h>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

int main(int argc, char** argv)
{
    const char* mode = argc > 1 ? argv[1] : "plain";
    int lfd = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in addr;
    std::memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = 0;
    bind(lfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    listen(lfd, 1);
    socklen_t len = sizeof(addr);
    getsockname(lfd, reinterpret_cast<sockaddr*>(&addr), &len);

    int cfd = socket(AF_INET, SOCK_STREAM, 0);
    connect(cfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    int sfd = accept(lfd, 0, 0);
    close(cfd);  // peer goes away
    usleep(100000);

    int flags = 0;
    if (std::strcmp(mode, "msg_nosignal") == 0)
        flags = MSG_NOSIGNAL;
    if (std::strcmp(mode, "so_nosigpipe") == 0) {
        int on = 1;
        setsockopt(sfd, SOL_SOCKET, SO_NOSIGPIPE, &on, sizeof(on));
    }
    std::printf("MSG_NOSIGNAL=0x%x\n", MSG_NOSIGNAL);
    for (int i = 1; i <= 3; ++i) {
        ssize_t n = send(sfd, "hello", 5, flags);
        std::printf("send #%d -> %ld errno=%d (%s)\n", i, static_cast<long>(n),
                    n < 0 ? errno : 0, n < 0 ? std::strerror(errno) : "-");
        std::fflush(stdout);
        usleep(100000);
    }
    std::printf("process still alive\n");
    return 0;
}
```

### 출력

```
$ for m in plain msg_nosignal so_nosigpipe; do echo "\$ ./nosig $m"; ./nosig $m; echo "[exit=$?]"; done
$ ./nosig plain
MSG_NOSIGNAL=0x80000
send #1 -> 5 errno=0 (-)
[exit=141]
$ ./nosig msg_nosignal
MSG_NOSIGNAL=0x80000
send #1 -> 5 errno=0 (-)
send #2 -> -1 errno=32 (Broken pipe)
send #3 -> -1 errno=32 (Broken pipe)
process still alive
[exit=0]
$ ./nosig so_nosigpipe
MSG_NOSIGNAL=0x80000
send #1 -> 5 errno=0 (-)
send #2 -> -1 errno=32 (Broken pipe)
send #3 -> -1 errno=32 (Broken pipe)
process still alive
[exit=0]
```

## 2. `leaks -atExit`와 SIGINT

### man page 발췌 (`man leaks | col -b`)

```
     -atExit -- command
		   Launches the specified command and runs leaks when that
		   process exits.  The -atExit argument should be the last
		   argument, followed by -- and the command to launch.	For
		   example:

		   $ leaks -quiet -atExit -- /bin/ls -lt /tmp/

		   Using -atExit will automatically set
		   MallocStackLogging=lite for the specified command so that
		   stack backtraces can be shown for leaked allocations. To
		   use a different setting of that env var, such as YES or NO,
		   you can set the env var prior to running leaks. For
		   example:

		   $ MallocStackLogging=YES leaks -quiet -atExit -- /bin/ls -lt /tmp/

EXIT STATUS
     The leaks command exits with one of the following values:

     0	   No leaks were detected.
     1	   One or more leaks were detected.
     >1    An error occurred.
```

### 프로그램 (`sigleak.cpp`)

`raw/valgrind-observed-sigint.md`의 `sigleak.cpp`와 같은 파일이다 (`diff`로 확인). `new char*[10]`(80바이트)와 `new char[100]` 열 개를 할당하고 SIGINT를 기다린다. 모드: `default`(핸들러 없음), `return`(해제 없이 `main` 반환), `exit`(해제 없이 `std::exit(0)`), `cleanup`(모두 해제 후 반환).

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

### 명령

```sh
for mode in default return exit cleanup; do
    echo "## mode=$mode"
    echo "\$ leaks -atExit -- ./sigleak $mode   (pkill -INT -x sigleak after 2s)"
    ( sleep 2; pkill -INT -x sigleak ) &
    leaks -atExit -- ./sigleak $mode > leaks-$mode.txt 2>&1
    echo "[exit=$?]"
    wait
    cat leaks-$mode.txt
    echo
done
```

`[exit=…]`는 `leaks` 명령의 종료 코드다.

### 출력

```
## mode=default
$ leaks -atExit -- ./sigleak default   (pkill -INT -x sigleak after 2s)
[exit=0]

## mode=return
$ leaks -atExit -- ./sigleak return   (pkill -INT -x sigleak after 2s)
[exit=0]
Process 96825 is not debuggable. Due to security restrictions, leaks can only show or save contents of readonly memory of restricted processes.

Process:         sigleak [96825]
Path:            /private/tmp/*/sigleak
Load Address:    0x104804000
Identifier:      sigleak
Version:         0
Code Type:       ARM64
Platform:        macOS
Parent Process:  leaks [96823]
Target Type:     live task

Date/Time:       2026-10-16 01:22:52.261 +0900
Launch Time:     2026-10-16 01:22:50.196 +0900
OS Version:      macOS 26.6.2 (25G83)
Report Version:  7
Analysis Tool:   /usr/bin/leaks

Physical footprint:         1905K
Physical footprint (peak):  1905K
Idle exit:                  untracked
----

leaks Report Version: 4.0, multi-line stacks
Process 96825: 198 nodes malloced for 13 KB
Process 96825: 0 leaks for 0 total leaked bytes.


## mode=exit
$ leaks -atExit -- ./sigleak exit   (pkill -INT -x sigleak after 2s)
[exit=0]
Process 97299 is not debuggable. Due to security restrictions, leaks can only show or save contents of readonly memory of restricted processes.

Process:         sigleak [97299]
Path:            /private/tmp/*/sigleak
Load Address:    0x102d28000
Identifier:      sigleak
Version:         0
Code Type:       ARM64
Platform:        macOS
Parent Process:  leaks [97297]
Target Type:     live task

Date/Time:       2026-10-16 01:22:55.322 +0900
Launch Time:     2026-10-16 01:22:53.280 +0900
OS Version:      macOS 26.6.2 (25G83)
Report Version:  7
Analysis Tool:   /usr/bin/leaks

Physical footprint:         1905K
Physical footprint (peak):  1905K
Idle exit:                  untracked
----

leaks Report Version: 4.0, multi-line stacks
Process 97299: 198 nodes malloced for 13 KB
Process 97299: 0 leaks for 0 total leaked bytes.


## mode=cleanup
$ leaks -atExit -- ./sigleak cleanup   (pkill -INT -x sigleak after 2s)
[exit=0]
Process 97539 is not debuggable. Due to security restrictions, leaks can only show or save contents of readonly memory of restricted processes.

Process:         sigleak [97539]
Path:            /private/tmp/*/sigleak
Load Address:    0x104440000
Identifier:      sigleak
Version:         0
Code Type:       ARM64
Platform:        macOS
Parent Process:  leaks [97537]
Target Type:     live task

Date/Time:       2026-10-16 01:22:58.103 +0900
Launch Time:     2026-10-16 01:22:56.042 +0900
OS Version:      macOS 26.6.2 (25G83)
Report Version:  7
Analysis Tool:   /usr/bin/leaks

Physical footprint:         1905K
Physical footprint (peak):  1905K
Idle exit:                  untracked
----

leaks Report Version: 4.0, multi-line stacks
Process 97539: 187 nodes malloced for 12 KB
Process 97539: 0 leaks for 0 total leaked bytes.


```

### `default` 재실행과 leaks 없이 실행

```
$ for i in 1 2; do ( sleep 2; pkill -INT -x sigleak ) & leaks -atExit -- ./sigleak default; echo "[exit=$?]"; wait; done
[exit=0]
[exit=0]
$ ( sleep 1; pkill -INT -x sigleak ) & ./sigleak default; echo "[exit=$?]"
[exit=130]
```

## 3. 대조 실험: 포인터를 잃은 뒤 정상 종료

leaks가 이 환경에서 누수를 잡는지 확인하려고, 할당한 블록의 포인터를 모두 지운 뒤 정상 종료하는 프로그램을 같은 방식으로 실행했다.

### 프로그램 (`lost.cpp`)

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

### 출력 (`Binary Images:` 줄부터 끝까지는 생략)

```
$ leaks -atExit -- ./lost
lost pointer, exiting
Process 98459 is not debuggable. Due to security restrictions, leaks can only show or save contents of readonly memory of restricted processes.

Process:         lost [98459]
Path:            /private/tmp/*/lost
Load Address:    0x1003d4000
Identifier:      lost
Version:         0
Code Type:       ARM64
Platform:        macOS
Parent Process:  leaks [98458]
Target Type:     live task

Date/Time:       2026-10-16 01:23:09.929 +0900
Launch Time:     2026-10-16 01:23:09.489 +0900
OS Version:      macOS 26.6.2 (25G83)
Report Version:  7
Analysis Tool:   /usr/bin/leaks

Physical footprint:         2017K
Physical footprint (peak):  2017K
Idle exit:                  untracked
----

leaks Report Version: 4.0, multi-line stacks
Process 98459: 199 nodes malloced for 18 KB
Process 98459: 11 leaks for 1216 total leaked bytes.

STACK OF 1 INSTANCE OF 'ROOT LEAK: <malloc in main>':
4   dyld                                  0x18882c4e4 start + 6992
3   lost                                  0x1003d4548 main + 24  lost.cpp:8
2   libc++abi.dylib                       0x188bae7e8 operator new(unsigned long) + 52
1   libsystem_malloc.dylib                0x188a076c4 _malloc + 96
0   libsystem_malloc.dylib                0x188a231fc _malloc_zone_malloc_instrumented_or_legacy + 152 
====
    11 (1.19K) ROOT LEAK: <malloc in main 0x8fec28000> [96]
       1 (112 bytes) <malloc in main 0x8ff008000> [112]
       1 (112 bytes) <malloc in main 0x8ff008070> [112]
       1 (112 bytes) <malloc in main 0x8ff0080e0> [112]
       1 (112 bytes) <malloc in main 0x8ff008150> [112]
       1 (112 bytes) <malloc in main 0x8ff0081c0> [112]
       1 (112 bytes) <malloc in main 0x8ff008230> [112]
       1 (112 bytes) <malloc in main 0x8ff0082a0> [112]
       1 (112 bytes) <malloc in main 0x8ff008310> [112]
       1 (112 bytes) <malloc in main 0x8ff008380> [112]
       1 (112 bytes) <malloc in main 0x8ff0083f0> [112]



[exit=1]
```
