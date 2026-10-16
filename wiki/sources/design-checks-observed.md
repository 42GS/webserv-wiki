---
title: 실측 — 설계 확인 3건 (파일 시계, 큰 본문 메모리, 자식의 std::exit)
type: source
sources: [raw/design-checks-observed.md, raw/subject.md]
updated: 2026-10-16
---

# 실측 — 설계 확인 3건 (파일 시계, 큰 본문 메모리, 자식의 `std::exit`)

원본: `raw/design-checks-observed.md`. [[analysis/design]]의 가정 3가지를 macOS와 Ubuntu 22.04 컨테이너에서 확인한 프로그램과 출력을 그대로 담았다 (2026-10-16, raw/design-checks-observed.md:3-4).

## 1. 파일 수정 시각 시계

- `open(O_TRUNC)` → `write` 1바이트 → `close` → `stat`의 `st_mtime`이 macOS, 컨테이너 내부 파일시스템, 호스트 마운트 모두에서 6번 다 `time()`과 같았다 (raw/design-checks-observed.md:60-80).
- 적용 (**판단**): 시간 함수 없이 초 단위 현재 시각을 얻을 수 있다 → [[analysis/design-decisions]] 10.

## 2. 큰 본문을 메모리에 모을 때

- 메모리를 256MB로 제한한 컨테이너에서 `std::string`에 1GB를 모으려 하자 128MB를 넘긴 뒤 `Killed`, 종료 코드 137로 끝났다. `std::bad_alloc`은 잡히지 않았다 (raw/design-checks-observed.md:119-123).
- 제한 없이 모으자 8192MB 뒤 `Killed`가 나왔다. 이 환경의 `vm.overcommit_memory`는 1이다 (raw/design-checks-observed.md:129-135).
- 적용 (**판단**): 메모리가 바닥나면 예외 대신 프로세스가 강제로 끝날 수 있다. `bad_alloc`을 잡는 것은 방어가 되지 않으므로 본문 크기 상한을 설정 단계에서 강제한다 → [[analysis/design-decisions]] 11. Ubuntu 기본값(`overcommit_memory` 0)에서 결과가 다른지는 확인하지 않았다.

## 3. `execve`가 실패한 자식의 `std::exit(1)`

- 부모가 버퍼에 남긴 출력이 `fork` 뒤 자식의 `std::exit`에서 한 번 더 나왔다. `fork` 전에 `fflush`하면 한 번만 나왔다. macOS와 Ubuntu 22.04가 같았고, 부모는 `waitpid`로 종료 코드 1을 받았다 (raw/design-checks-observed.md:183-194).
- 적용 (**판단**): CGI 자식은 표준 출력을 pipe에 연결한 상태라, flush되지 않은 서버 출력이 남아 있으면 그 내용이 CGI 출력에 섞인다. `fork` 직전에 표준 출력·에러를 flush한다 → [[analysis/design-decisions]] 12.
