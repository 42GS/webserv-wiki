---
title: Google C++ Style Guide
type: source
sources: [raw/google-cpp-style-guide.md]
updated: 2026-10-17
---

# Google C++ Style Guide

원본: `raw/google-cpp-style-guide.md`. <https://google.github.io/styleguide/cppguide.html>의 원본인 google/styleguide 저장소 gh-pages 브랜치 `cppguide.html`(커밋 0acdb47)을 2026-10-17에 받아, pandoc 3.10으로 `div#content`를 markdown으로 옮겼다 (raw/google-cpp-style-guide.md:1-3). 원본 HTML은 `raw/google-cpp-style-guide.source.html`.

Google이 자기 코드에 쓰는 C++ 작성 규칙이다. 파일 확장자는 `.cc`/`.h`를 쓴다. webserv에서는 [[analysis/design]] 1절의 "상수·자료형·보조 함수를 어디에 두는가" 규칙의 근거로만 쓴다.

> [!note] 변환 검증
> 2026-10-17 Internal Linkage 절(raw/google-cpp-style-guide.md:432-449)을 원본 HTML과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 나머지 절은 대조하지 않았다.

## 과제와 관련된 절

| 절 (시작 줄) | 내용 | 위키 페이지 |
|---|---|---|
| Internal Linkage (432) | 다른 파일이 참조하지 않는 정의는 internal linkage로, 헤더에는 쓰지 않음 | [[analysis/design]] 1절 |

다루지 않는 절: 나머지 전부.

## 핵심

- `.cc` 파일의 정의를 그 파일 밖에서 참조할 필요가 없으면 이름 없는 namespace에 두거나 `static`으로 선언해 internal linkage를 준다. `.h` 파일에는 둘 다 쓰지 않는다 (raw/google-cpp-style-guide.md:434).
- internal linkage를 주면 다른 파일에서 접근할 수 없다. 다른 파일이 같은 이름을 선언해도 두 개체는 서로 독립이다 (raw/google-cpp-style-guide.md:438).
- Decision: 다른 곳에서 참조할 필요가 없는 모든 코드에 internal linkage를 권한다 (encouraged). `.h` 파일에는 쓰지 않는다 (raw/google-cpp-style-guide.md:442).
- 이름 없는 namespace를 닫는 주석은 `}  // namespace`로 쓴다 (raw/google-cpp-style-guide.md:444-449). webserv 코드도 이 형식이다.
