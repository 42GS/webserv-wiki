---
title: Electric Fence 실측 (Ubuntu 22.04) — 누수를 보고하지 않음
type: source
sources: [raw/efence-observed-ubuntu2204.md, raw/evaluation-sheet-en.md]
updated: 2026-10-16
---

# Electric Fence 실측 (Ubuntu 22.04) — 누수를 보고하지 않음

원본: `raw/efence-observed-ubuntu2204.md`. 평가 PC와 같은 Ubuntu 22.04 이미지에 apt 패키지 electric-fence를 설치하고, 패키지 문서를 읽은 뒤 테스트 프로그램 세 개를 Electric Fence로 실행한 출력을 그대로 담았다 (2026-10-16, raw/efence-observed-ubuntu2204.md:3-4).

- 버전: electric-fence 2.2.6, g++ 11.4.0 (raw/efence-observed-ubuntu2204.md:316-318).
- 받은 목적: [[concepts/resilience]]의 **미확인** — 평가표가 누수 검사 도구로 드는 `e_fence`(raw/evaluation-sheet-en.md:25)가 해제하지 않은 heap을 어떻게 보고하는지.

## 문서

- man page는 Electric Fence가 두 가지 버그를 찾도록 돕는다고 한다: malloc 할당의 경계를 넘는 접근과, `free()`로 해제한 메모리를 건드리는 접근 (raw/efence-observed-ubuntu2204.md:71-74). 할당마다 접근할 수 없는 페이지를 붙여, 그 페이지를 읽거나 쓰면 segmentation fault로 그 명령에서 멈춘다 (raw/efence-observed-ubuntu2204.md:79-87).
- README도 같은 두 가지만 든다 (raw/efence-observed-ubuntu2204.md:118-124).
- 발췌한 man page 앞부분(렌더링 1-75줄)과 README에는 누수(leak)를 찾는다는 설명이 없다. man page 나머지 부분은 "leak"로 검색해 찾지 못했지만 전부 읽지는 않았다.
- 사용법: `-lefence`로 링크하거나 `LD_PRELOAD=libefence.so.0.0`으로 불러온다 (raw/efence-observed-ubuntu2204.md:95-105). Debian 문서는 C++ 프로그램을 g++로 `libefence.a`에 링크하면 efence의 malloc이 쓰이지 않는다고 적는다 (raw/efence-observed-ubuntu2204.md:160-164).

## 결과

| 프로그램 | `LD_PRELOAD` | `g++ ... -lefence` | 근거 |
|---|---|---|---|
| `sigleak default` (SIGINT 기본 동작) | 배너만 출력, exit 130 | 출력 없음, exit 130 | raw/efence-observed-ubuntu2204.md:319-323, raw/efence-observed-ubuntu2204.md:343-345 |
| `sigleak return`·`exit`·`cleanup` | 배너만 출력, exit 0 | (`cleanup`만 실행) 출력 없음, exit 0 | raw/efence-observed-ubuntu2204.md:325-341, raw/efence-observed-ubuntu2204.md:347-349 |
| `lost` (포인터를 잃고 정상 종료) | 배너와 프로그램 출력뿐. **누수 보고 없음**, exit 0 | 같음 (배너 없음) | raw/efence-observed-ubuntu2204.md:351-361 |
| `overrun` (`block[100]`에 씀) | **Segmentation fault, exit 139** | 그대로 실행, exit 0 | raw/efence-observed-ubuntu2204.md:369-381 |

- Electric Fence 없이 `overrun`을 실행하면 1바이트 초과 쓰기 뒤에도 계속 실행됐다 (raw/efence-observed-ubuntu2204.md:363-367).
- `-lefence`로 빌드한 바이너리는 `ldd`에 `libefence`가 나오지 않았다 (raw/efence-observed-ubuntu2204.md:389-395). 그래서 배너가 없고 `overrun`도 잡히지 않았다. 링크에서 빠진 원인은 확인하지 않았다 (**미확인**, 확인: 링크 명령에 `-Wl,--verbose`나 `-Wl,--no-as-needed`를 주고 다시 빌드).

## 과제 적용 (판단)

- `e_fence`는 누수를 보고하지 않는다. 포인터를 잃은 대조군에서도 아무 보고가 없었다. 평가표가 누수 검사 도구로 함께 들지만 (raw/evaluation-sheet-en.md:25), 누수 확인에는 valgrind(Ubuntu)나 leaks(macOS)가 맞다 → [[sources/valgrind-observed-sigint]], [[sources/macos-observed-sigpipe-leaks]].
- 평가자가 `e_fence`를 쓰면 heap 경계 초과나 해제 후 접근이 segmentation fault가 된다. 평소에는 조용히 지나갈 수 있는 1바이트 초과도 크래시가 되고, 디펜스 중 segfault는 0점이다 (raw/evaluation-sheet-en.md:24). 버퍼 인덱스 경계(파서, 응답 버퍼)를 미리 확인해 둔다.
- `-lefence` 링크는 이 환경에서 동작하지 않았으므로, 직접 시험할 때는 `LD_PRELOAD=libefence.so.0.0 ./webserv`로 실행한다.

> [!note] 측정 범위
> arm64 컨테이너에서 측정했다. 커널은 OrbStack VM이라 평가 PC와 다르지만, 이 측정은 라이브러리 동작이라 영향이 작다고 본다 (**판단**). 서버 프로그램 자체를 Electric Fence로 실행해 보지는 않았다.
