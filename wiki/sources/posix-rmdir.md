---
title: POSIX rmdir() — 빈 디렉토리만 지움
type: source
sources: [raw/posix-rmdir.md]
updated: 2026-10-17
---

# POSIX rmdir()

원본: `raw/posix-rmdir.md`. <https://pubs.opengroup.org/onlinepubs/9799919799/functions/rmdir.html>을 2026-10-17에 받아 pandoc 3.10과 `pandoc/opengroup-body.lua`로 옮겼다 (raw/posix-rmdir.md:1-3). 원본 HTML은 `raw/posix-rmdir.source.html`.
POSIX.1-2024 (IEEE Std 1003.1-2024) 표준 문서다 (raw/posix-rmdir.md:5-7).

> [!note] 변환 검증
> 2026-10-17 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: ERRORS의 정의 목록(`<dl>`)이 `[오류 이름]` 문단과 설명 문단의 반복이 됨, EXAMPLES 코드 안의 `<br>`가 빈 줄 두 개가 됨(raw/posix-rmdir.md:117-118), `[Option Start]`·`[Option End]` 그림이 `<img>` 태그로 남음.

## 과제와 관련된 부분

`std::remove`는 디렉토리에 대해 `rmdir()`과 같다 ([[sources/posix-remove]]). DELETE가 디렉토리를 만나면 어디까지 지워질 수 있는지를 정한다.

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (25) | 빈 디렉토리일 때만 지운다 | [[sources/posix-remove]] |
| DESCRIPTION (29) | 심볼릭 링크면 실패 (`ENOTDIR`) | |
| DESCRIPTION (35) | 비어 있지 않으면 실패 (`EEXIST` 또는 `ENOTEMPTY`) | [[sources/posix-remove]] |
| RETURN VALUE (41) | 실패하면 디렉토리는 바뀌지 않는다 | |

## 핵심

- `rmdir()`은 경로가 가리키는 디렉토리를 지우되, 빈 디렉토리일 때만 지운다 (raw/posix-rmdir.md:25).
- 비어 있지 않으면 실패하고 errno를 `EEXIST`나 `ENOTEMPTY`로 둔다 (raw/posix-rmdir.md:35).
- 경로가 심볼릭 링크면 실패한다 (raw/posix-rmdir.md:29).
- 실패해서 -1을 돌려주면 그 디렉토리는 바뀌지 않아야 한다 (raw/posix-rmdir.md:41).

## 관련

- [[sources/posix-remove]], [[analysis/design-decisions]] 15
