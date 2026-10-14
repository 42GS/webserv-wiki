---
title: 빌드·제출·README·AI 규칙
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# 빌드·제출·README·AI 규칙

## 빌드

| 규칙 | 근거 |
|---|---|
| Makefile 제출, 불필요한 relink 금지 | raw/subject.md:47 |
| 규칙 `$(NAME)`, `all`, `clean`, `fclean`, `re` | raw/subject.md:48 |
| `c++`, `-Wall -Wextra -Werror` | raw/subject.md:49 |
| C++98 준수, `-std=c++98` 추가해도 컴파일 | raw/subject.md:50 |
| C 함수보다 C++ 버전 선호 (`<cstring>` > `<string.h>`) | raw/subject.md:51 |
| 외부 라이브러리·Boost 금지 | raw/subject.md:52 |
| 제출 파일: `Makefile`, `*.{h, hpp}`, `*.cpp`, `*.tpp`, `*.ipp`, 설정 파일 | raw/subject.md:105 |
| 다른 웹 서버를 `execve` 할 수 없음 | raw/subject.md:128 |

> [!danger] 평가표
> relink 없이 컴파일되지 않으면 'Invalid compilation' 플래그 (raw/evaluation-sheet-en.md:60).

## README.md (subject V)

> [!danger] 평가표
> 평가 첫 항목이 README 검사다. 필수 요소가 하나라도 없으면 0점 (raw/evaluation-sheet-en.md:35-44).
> 첫 줄은 정해진 문구 그대로("formatted exactly as") 이탤릭이어야 한다 (raw/evaluation-sheet-en.md:39).

저장소 루트, 영어로 작성 (raw/subject.md:196, raw/subject.md:207). 최소 포함:

1. 첫 줄 이탤릭: *This project has been created as part of the 42 curriculum by `<login1>`[, …].* (raw/subject.md:200)
2. Description (raw/subject.md:201)
3. Instructions — 컴파일·설치·실행 (raw/subject.md:202)
4. Resources — 참고 자료와 **AI를 어떤 작업·어떤 부분에 썼는지** (raw/subject.md:203)

## AI 사용 규칙 (subject III)

- 완전히 이해하고 책임질 수 있는 AI 산출물만 사용 (raw/subject.md:68).
- 디펜스에서 설명하지 못하면 실패한다는 예시 (raw/subject.md:92, raw/subject.md:96).

## 제출·디펜스

- Git 저장소 내용만 평가 (raw/subject.md:224, raw/evaluation-sheet-en.md:18).
- 디펜스 중 소규모 수정(동작 변경, 몇 줄 코드, 간단한 기능) 요청 가능, 보통 몇 분 안에 (raw/subject.md:226-228).
