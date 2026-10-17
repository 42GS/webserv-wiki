# 실측: 파일 시스템 2건 — std::remove의 디렉토리 처리, 파일 이름 길이 상한

> 측정일: 2026-10-17. 6단계(업로드·DELETE) 코드 리뷰에서 확인한 프로그램·명령과 출력을 그대로 붙였다. macOS(로컬 APFS, scratchpad 디렉토리)와 Ubuntu 22.04 Docker 컨테이너(`webserv-dev` 이미지, 컨테이너 안 디렉토리)에서 실행했다.
> 측정: Claude Code 세션 (위키 유지 LLM). 컨테이너 커널은 OrbStack VM이라 평가 PC의 22.04 커널과 다르고, 컨테이너 파일 시스템도 평가 PC의 것과 다를 수 있다.

## 1. std::remove: 일반 파일, 빈 디렉토리, 비지 않은 디렉토리

```cpp
// std::remove on a regular file, an empty directory and a non-empty one.
#include <sys/stat.h>

#include <cstdio>
#include <fstream>
#include <iostream>

static void report(const char* what, const char* path) {
  struct stat info;
  const int result = std::remove(path);
  std::cout << what << ": std::remove returned " << result << ", path "
            << (stat(path, &info) == 0 ? "still exists" : "is gone") << "\n";
}

int main() {
  std::ofstream("file.txt") << "x";
  mkdir("empty-dir", 0755);
  mkdir("full-dir", 0755);
  std::ofstream("full-dir/inside.txt") << "y";
  report("regular file", "file.txt");
  report("empty directory", "empty-dir");
  report("non-empty directory", "full-dir");
  return 0;
}
```

빌드: `c++ -Wall -Wextra -Werror -std=c++98 remove_check.cpp -o rc`, 빈 디렉토리 안에서 실행.

macOS 26.6.2, Apple clang version 21.0.0 (clang-2100.3.34.2):

```
regular file: std::remove returned 0, path is gone
empty directory: std::remove returned 0, path is gone
non-empty directory: std::remove returned -1, path still exists
```

Ubuntu 22.04.5 LTS, c++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0:

```
regular file: std::remove returned 0, path is gone
empty directory: std::remove returned 0, path is gone
non-empty directory: std::remove returned -1, path still exists
```

## 2. 파일 이름 길이 상한

ASCII 이름 (`sh ascii_names.sh 2>&1`, 같은 두 환경, 빈 디렉토리 안). 서브셸 `( : > "$f" )`은 만들기에 실패해도 스크립트를 끝내지 않게 하려고 썼다:

```sh
for n in 255 256; do f=$(printf "%${n}s" | tr " " a); if (: > "$f") 2>/dev/null; then echo "$n ok"; else echo "$n fail"; fi; done
getconf NAME_MAX .
```

macOS 출력:

```
255 ok
256 fail
255
```

Ubuntu 출력:

```
255 ok
256 fail
255
```

UTF-8 이름 (한글 `가` U+AC00, UTF-8 3바이트):

```python
import os, sys
os.chdir(sys.argv[1])
for chars in (85, 86, 255):
    name = "가" * chars          # 3 bytes each in UTF-8
    try:
        open(name, "w").close(); r = "ok"
    except OSError as e:
        r = "fail (%s)" % e.strerror
    print("%d Korean chars = %d bytes: %s" % (chars, len(name.encode()), r))
```

macOS 출력:

```
85 Korean chars = 255 bytes: ok
86 Korean chars = 258 bytes: ok
255 Korean chars = 765 bytes: ok
```

Ubuntu 출력:

```
85 Korean chars = 255 bytes: ok
86 Korean chars = 258 bytes: fail (File name too long)
255 Korean chars = 765 bytes: fail (File name too long)
```
