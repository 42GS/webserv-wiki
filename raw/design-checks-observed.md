# 실측: 설계 확인 3건 — 파일 수정 시각 시계, 큰 본문 메모리, 실패한 자식의 std::exit

> 측정일: 2026-10-16. 설계(`wiki/analysis/design.md`)의 가정 3가지를 macOS와 Ubuntu 22.04 Docker 컨테이너(`raw/ubuntu2204-observed-tools.md`의 `webserv-u2204` 이미지)에서 확인한 프로그램과 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 컨테이너 커널은 OrbStack VM이라 평가 PC의 22.04 커널과 다르다.

## 1. 파일 수정 시각으로 현재 시각 얻기

`open(O_WRONLY|O_CREAT|O_TRUNC)` → `write` 1바이트 → `close` → `stat`의 `st_mtime`을 0.7초 간격으로 6번 읽고, 비교용으로 `time()`을 함께 출력한다.

```cpp
// Checks whether open(O_TRUNC)+write+close updates st_mtime, using only
// allowed functions for the clock; time() is called only to compare.
#include <ctime>
#include <cstdio>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>

static long clockNow(const char* path)
{
    int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0)
        return -1;
    if (write(fd, "x", 1) != 1) {
        close(fd);
        return -1;
    }
    close(fd);
    struct stat st;
    if (stat(path, &st) != 0)
        return -1;
    return static_cast<long>(st.st_mtime);
}

int main(int argc, char** argv)
{
    const char* path = argc > 1 ? argv[1] : "clock.tmp";
    for (int i = 0; i < 6; ++i) {
        long fileNow = clockNow(path);
        long sysNow = static_cast<long>(std::time(0));
        std::printf("i=%d stat_mtime=%ld time()=%ld diff=%ld\n",
                    i, fileNow, sysNow, sysNow - fileNow);
        usleep(700000);
    }
    return 0;
}
```

### 명령

```
c++ -std=c++98 -Wall -Wextra -Werror -o clockfile src/clockfile.cpp && ./clockfile $D/clock.tmp
docker run --rm -v $D/src:/src:ro webserv-u2204 sh -c 'g++ -std=c++98 -Wall -Wextra -Werror -o /tmp/c /src/clockfile.cpp && /tmp/c /tmp/clock.tmp'
docker run --rm -v $D/src:/src:ro -v $D:/out webserv-u2204 sh -c 'g++ -std=c++98 -o /tmp/c /src/clockfile.cpp && /tmp/c /out/clock2.tmp'
```

### 출력

```
## macOS
i=0 stat_mtime=1792131044 time()=1792131044 diff=0
i=1 stat_mtime=1792131044 time()=1792131044 diff=0
i=2 stat_mtime=1792131045 time()=1792131045 diff=0
i=3 stat_mtime=1792131046 time()=1792131046 diff=0
i=4 stat_mtime=1792131047 time()=1792131047 diff=0
i=5 stat_mtime=1792131047 time()=1792131047 diff=0
## Ubuntu 22.04 container (overlay fs: /tmp)
i=0 stat_mtime=1792131049 time()=1792131049 diff=0
i=1 stat_mtime=1792131049 time()=1792131049 diff=0
i=2 stat_mtime=1792131050 time()=1792131050 diff=0
i=3 stat_mtime=1792131051 time()=1792131051 diff=0
i=4 stat_mtime=1792131051 time()=1792131051 diff=0
i=5 stat_mtime=1792131052 time()=1792131052 diff=0
## bind mount (/out)
i=0 stat_mtime=1792131053 time()=1792131053 diff=0
i=1 stat_mtime=1792131054 time()=1792131054 diff=0
i=2 stat_mtime=1792131055 time()=1792131055 diff=0
i=3 stat_mtime=1792131055 time()=1792131055 diff=0
i=4 stat_mtime=1792131056 time()=1792131056 diff=0
i=5 stat_mtime=1792131057 time()=1792131057 diff=0
```

## 2. 본문을 std::string에 모을 때 메모리가 바닥나면

64KB씩 `std::string`에 붙여 목표 크기(MB)까지 모은다. `std::bad_alloc`을 잡는다.

```cpp
// Appends 64 KB chunks to one std::string (like collecting a request body)
// until TARGET MB, catching std::bad_alloc.
#include <cstdio>
#include <cstdlib>
#include <new>
#include <string>

int main(int argc, char** argv)
{
    const size_t targetMb = argc > 1 ? std::strtoul(argv[1], 0, 10) : 1024;
    std::string body;
    const std::string chunk(65536, 'a');
    try {
        while (body.size() < targetMb * 1024 * 1024) {
            body.append(chunk);
            if (body.size() % (64 * 1024 * 1024) == 0) {
                std::printf("collected %lu MB\n", static_cast<unsigned long>(body.size() >> 20));
                std::fflush(stdout);
            }
        }
        std::printf("done: %lu MB\n", static_cast<unsigned long>(body.size() >> 20));
    } catch (const std::bad_alloc&) {
        std::printf("caught std::bad_alloc at %lu MB\n", static_cast<unsigned long>(body.size() >> 20));
    }
    return 0;
}
```

### 명령과 출력

```
$ docker run --rm --memory=256m --memory-swap=256m -v $D/src:/src:ro webserv-u2204 sh -c 'g++ -std=c++98 -Wall -Wextra -Werror -o /tmp/g /src/grow.cpp && /tmp/g 1024; echo "[exit=$?]"'
collected 64 MB
collected 128 MB
Killed
[exit=137]
```

메모리 제한 없이 실행했다. 출력이 길어 `tail -3`으로 끝만 보였으므로 `[exit=…]`는 `tail`의 종료 코드다. `Killed`는 프로그램이 아니라 쉘이 출력한 줄로 보인다(프로그램 코드에 이 문자열이 없다).

```
$ docker run --rm -v $D/src:/src:ro webserv-u2204 sh -c 'g++ -std=c++98 -o /tmp/g /src/grow.cpp && /tmp/g 100000000 2>&1 | tail -3; echo "[exit=$?]"; cat /proc/sys/vm/overcommit_memory'
Killed
collected 8064 MB
collected 8128 MB
collected 8192 MB
[exit=0]
1
```

## 3. execve가 실패한 자식이 std::exit(1)로 끝날 때

부모가 줄바꿈 없는 텍스트를 `printf`(파이프로 연결된 stdout이라 버퍼에 남음)한 뒤 `fork`하고, 자식은 없는 파일을 `execve`한 뒤 `std::exit(1)`한다. `flush` 인자를 주면 `fork` 전에 `fflush(stdout)`한다.

```cpp
// A child whose execve fails ends with std::exit(1). Checks whether
// unflushed stdout data from the parent is written twice, with and without
// flushing before fork, and what waitpid reports.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/wait.h>
#include <unistd.h>

int main(int argc, char** argv)
{
    const bool flushFirst = argc > 1 && std::strcmp(argv[1], "flush") == 0;
    std::printf("[parent buffered text]");      // no newline: stays in the stdio buffer when piped
    if (flushFirst)
        std::fflush(stdout);
    pid_t pid = fork();
    if (pid == 0) {
        char* args[] = { const_cast<char*>("/no/such/script"), 0 };
        char* env[] = { 0 };
        execve(args[0], args, env);
        std::exit(1);                            // execve failed
    }
    int status = 0;
    waitpid(pid, &status, 0);
    std::printf("\nchild exited=%d code=%d\n", WIFEXITED(status) ? 1 : 0,
                WIFEXITED(status) ? WEXITSTATUS(status) : -1);
    return 0;
}
```

### 명령

```
c++ -std=c++98 -Wall -Wextra -Werror -o ce src/childexit.cpp && for m in noflush flush; do echo "## macOS $m (stdout piped to cat)"; ./ce $m | cat; done
docker run --rm -v $D/src:/src:ro webserv-u2204 sh -c 'g++ -std=c++98 -Wall -Wextra -Werror -o /tmp/ce /src/childexit.cpp && for m in noflush flush; do echo "## Ubuntu 22.04 $m (stdout piped to cat)"; /tmp/ce $m | cat; done'
```

### 출력

```
## macOS noflush (stdout piped to cat)
[parent buffered text][parent buffered text]
child exited=1 code=1
## macOS flush (stdout piped to cat)
[parent buffered text]
child exited=1 code=1
## Ubuntu 22.04 noflush (stdout piped to cat)
[parent buffered text][parent buffered text]
child exited=1 code=1
## Ubuntu 22.04 flush (stdout piped to cat)
[parent buffered text]
child exited=1 code=1
```
