---
title: POSIX fcntl()
type: source
sources: [raw/posix-fcntl.md, raw/subject.md]
updated: 2026-10-15
---

# POSIX fcntl()

원본: `raw/posix-fcntl.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/fcntl.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/posix-fcntl.md:1-4). 원본 HTML은 `raw/posix-fcntl.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-fcntl.md:6).

> [!note] 변환 검증
> `tools/posix_wrap.py` → `tools/nginx2md.py`로 변환하고 `tools/verify_md.py`로 검증했다. 28,091자, 단어 5,520개가 같았다 (PASS).
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: SYNOPSIS가 한 줄로 합쳐짐, F_SETOWN_EX 항목(raw/posix-fcntl.md:74-84)의 글머리표와 하위 목록 없음, `<p>`가 든 목록 글머리표·번호 없음.

## 과제와 관련된 부분

subject는 `fcntl()`을 `F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC`로만 쓰게 한다 (raw/subject.md:155-157).

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| `F_SETFD` (50-52) | fd 플래그 설정. `FD_CLOEXEC`면 exec 때 fd가 닫힘 | [[analysis/subject-vs-evaluation]] |
| `F_GETFL`·`F_SETFL` (54-60) | 파일 상태 플래그 읽기·설정 (`O_NONBLOCK`) | [[concepts/io-multiplexing]] |
| RETURN VALUE (170-200) | `F_SETFL` 성공 시 -1이 아닌 값 | [[concepts/io-multiplexing]] |
| APPLICATION USAGE (391) | 플래그는 읽고-수정하고-쓰기로 다루라고 권장 | [[analysis/subject-vs-evaluation]] |

다루지 않는 부분: 잠금(lock), `F_DUPFD` 계열, 소유자(`F_SETOWN`) 관련.
