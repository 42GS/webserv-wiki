---
title: 파일 시스템 실측 — std::remove의 디렉토리 처리, 파일 이름 길이 상한
type: source
sources: [raw/fs-observed-remove-name-length.md, raw/posix-remove.md, raw/posix-rmdir.md]
updated: 2026-10-17
---

# 파일 시스템 실측 (macOS·Ubuntu 22.04)

원본: `raw/fs-observed-remove-name-length.md`. 6단계 코드 리뷰에서 macOS(APFS)와 Ubuntu 22.04 Docker 컨테이너로 확인한 프로그램·명령과 출력이다 (raw/fs-observed-remove-name-length.md:3-4). 컨테이너의 커널과 파일 시스템은 평가 PC와 다를 수 있다 (raw/fs-observed-remove-name-length.md:4).

## std::remove

- 일반 파일과 빈 디렉토리는 두 OS 모두 0을 돌려주고 지워졌다. 비어 있지 않은 디렉토리는 -1을 돌려주고 남았다 (raw/fs-observed-remove-name-length.md:40-42, raw/fs-observed-remove-name-length.md:48-50).
- POSIX가 정한 동작과 같다: 디렉토리면 `rmdir`과 같고 (raw/posix-remove.md:35), `rmdir`은 빈 디렉토리만 지운다 (raw/posix-rmdir.md:25) → [[sources/posix-remove]], [[sources/posix-rmdir]].

## 파일 이름 길이

- ASCII 이름은 두 OS 모두 255자가 되고 256자는 실패했다. `getconf NAME_MAX .`은 둘 다 255였다 (raw/fs-observed-remove-name-length.md:65-67, raw/fs-observed-remove-name-length.md:73-75).
- 한글(UTF-8 3바이트) 이름은 Ubuntu가 255바이트(85자)까지 만들고 258바이트(86자)부터 "File name too long"으로 실패했다. macOS는 765바이트(255자)도 만들었다 (raw/fs-observed-remove-name-length.md:95-97, raw/fs-observed-remove-name-length.md:103-105). macOS는 바이트가 아니라 글자 수로 세는 것으로 보인다 (**판단**).
- 과제 적용: 업로드 파일 이름은 255바이트까지 받고 넘으면 400 → [[analysis/design]] 7절 "구현 세부 (단계 6)".

## 관련

- [[sources/posix-remove]], [[sources/posix-rmdir]], [[analysis/design-decisions]] 15
