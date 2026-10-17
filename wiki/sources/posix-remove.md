---
title: POSIX remove() — 파일이면 unlink, 디렉토리면 rmdir
type: source
sources: [raw/posix-remove.md, raw/posix-rmdir.md, raw/fs-observed-remove-name-length.md]
updated: 2026-10-17
---

# POSIX remove()

원본: `raw/posix-remove.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/remove.html>을 2026-10-17에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-remove.md:1-3). 원본 HTML은 `raw/posix-remove.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-remove.md:5-7).

> [!note] 변환 검증
> 2026-10-17 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: EXAMPLES 코드 안의 `<br>`가 빈 줄 두 개가 됨(raw/posix-remove.md:60-61), `[Option Start]`·`[Option End]` 그림이 `<img>` 태그로 남음, 마지막 `<p>&nbsp;</p>`가 공백 줄이 됨.

## 과제와 관련된 부분

C++98 `<cstdio>`의 `std::remove`로 DELETE를 구현한다 ([[analysis/design-decisions]] 15). 이 페이지는 그 동작을 정한다.

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (31) | 그 이름으로 파일에 더 접근할 수 없게 한다 (ISO C와 같은 부분) | [[analysis/design-decisions]] 15 |
| DESCRIPTION (33-35) | 디렉토리가 아니면 `unlink`, 디렉토리면 `rmdir`과 같다 (CX: ISO C 밖의 POSIX 확장) | [[analysis/design]] 7절 |
| RETURN VALUE·ERRORS (39, 43) | `rmdir()`·`unlink()`를 따른다 | [[sources/posix-rmdir]] |

## 핵심

- `remove()`는 경로가 가리키는 파일을 그 이름으로 더 접근할 수 없게 한다. 그 이름으로 다시 열면 새로 만들지 않는 한 실패해야 한다 (raw/posix-remove.md:31).
- 경로가 디렉토리가 아니면 `remove(path)`는 `unlink(path)`와 같아야 하고, 디렉토리이면 `rmdir(path)`와 같아야 한다 (raw/posix-remove.md:33-35).
- 이 두 문장에는 CX 표시가 있다 (raw/posix-remove.md:33). Issue 6 변경 기록은 ISO C 밖의 확장에 표시를 했다고 하고, 이 두 동작을 SUS에 맞춘 새 요구로 적는다 (raw/posix-remove.md:90-94). 즉 디렉토리를 지우는 동작은 ISO C가 아니라 POSIX가 정한다.
- 반환값과 오류는 `rmdir()`이나 `unlink()`를 따른다 (raw/posix-remove.md:39, raw/posix-remove.md:43). `rmdir()`은 빈 디렉토리만 지운다 → [[sources/posix-rmdir]].

## 과제 적용 (판단)

- DELETE의 라우터는 일반 파일인지 확인한 뒤에만 `std::remove`를 부른다 ([[analysis/design]] 7절). 그 사이에 다른 프로세스가 같은 경로를 빈 디렉토리로 바꾸면 `remove`는 `rmdir`처럼 그 디렉토리를 지운다 (raw/posix-remove.md:35). 비어 있지 않은 디렉토리는 지워지지 않는다 → [[sources/posix-rmdir]].
- macOS와 Ubuntu 22.04에서 실제로 이렇게 동작했다: 빈 디렉토리는 지워지고, 비어 있지 않은 디렉토리는 -1로 남았다(실측) → [[sources/fs-observed-remove-name-length]].
- 이 틈을 막을지는 사용자가 정한다(2026-10-17 보류) → [[analysis/design-decisions]] 15.

## 관련

- [[sources/posix-rmdir]], [[sources/fs-observed-remove-name-length]], [[analysis/design-decisions]] 15, [[analysis/subject-vs-evaluation]] 1.4절
