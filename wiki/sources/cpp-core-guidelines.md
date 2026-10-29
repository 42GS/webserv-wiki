---
title: C++ Core Guidelines
type: source
sources: [raw/cpp-core-guidelines.md]
updated: 2026-10-29
---

# C++ Core Guidelines

원본: `raw/cpp-core-guidelines.md`. isocpp/CppCoreGuidelines 저장소의 `CppCoreGuidelines.md`를 커밋 33bcd01로 고정해 2026-10-17에 받았다 (raw/cpp-core-guidelines.md:1-2). 원본이 markdown이므로 변환하지 않았다. 출처 머리말 3줄 아래는 받은 파일과 바이트 단위로 같다 (`cmp`로 확인).
편집자는 Bjarne Stroustrup과 Herb Sutter이고, 계속 고쳐 가는 문서다 (raw/cpp-core-guidelines.md:4-13).

C++ 코드 작성 지침이다. webserv에서는 [[analysis/design]] 1절의 "상수·자료형·보조 함수를 어디에 두는가" 규칙의 근거로만 쓴다. 지침은 최신 C++을 기준으로 쓰였으므로, C++98에도 있는 기능에 관한 규칙만 쓴다 (**판단**).

## 과제와 관련된 절

| 절 (시작 줄) | 내용 | 위키 페이지 |
|---|---|---|
| SF.21 (19758) | 헤더에 이름 없는 namespace를 쓰지 않는다 | [[analysis/design]] 1절 |
| SF.22 (19791) | 내보내지 않는 것은 모두 이름 없는 namespace에 둔다 | [[analysis/design]] 1절 |
| I.25 (2166) | 데이터 없는 추상 클래스를 인터페이스로 | [[lessons/04a-cpp98-basics]] 4A.5 |
| F.16 (2996) | 읽기 인자는 싼 타입은 값, 나머지는 `const` 참조 | [[lessons/04a-cpp98-basics]] 4A.2 |
| C.35 (5368) | 기반 클래스 소멸자는 public virtual 또는 protected non-virtual | [[lessons/04a-cpp98-basics]] 4A.5 |
| C.67 (6592) | 다형 클래스의 복사는 막는다 (slicing) | [[lessons/04a-cpp98-basics]] 4A.4 |
| R.1 (9464) | 자원은 RAII로 관리 | [[lessons/04a-cpp98-basics]] 4A.3 |
| R.11 (9785) | `new`·`delete`를 직접 부르지 않는다 (결과는 소유자에게) | [[lessons/04a-cpp98-basics]] 4A.6 |
| Con.2 (16982) | 상태를 바꾸지 않는 멤버 함수는 `const` | [[lessons/04a-cpp98-basics]] 4A.2 |

다루지 않는 절: 나머지 전부. 2026-10-17에 SF.21·SF.22를, 2026-10-29에 위 일곱 절의 제목과 Reason(F.16은 첫 예제까지)만 읽었다. 이 문서는 C++11 이후를 기준으로 해서 예제에 C++98에 없는 문법이 나온다. 레슨은 규칙의 이유만 인용한다.

## 핵심

- SF.21: 헤더에 이름 없는 namespace를 쓰지 않는다. 이유는 "It is almost always a bug to mention an unnamed namespace in a header file." (raw/cpp-core-guidelines.md:19758-19762)
- SF.22: 내보내지 않는(internal/non-exported) 것은 모두 이름 없는 namespace에 둔다. 이유는 바깥에서 그 안의 것에 기댈 수 없기 때문이다. 구현 파일의 정의는 외부로 내보내는 것이 아니면 모두 이름 없는 namespace에 두는 것을 고려하라고 한다 (raw/cpp-core-guidelines.md:19791-19796).
- SF.22의 예: API 클래스와 그 멤버는 이름 없는 namespace에 둘 수 없지만, 구현 파일에 정의한 "helper" 클래스·함수는 이름 없는 namespace에 둔다 (raw/cpp-core-guidelines.md:19816).

## webserv에 적용

- 한 `.cpp`에서만 쓰는 상수·표·행 타입·보조 클래스는 그 `.cpp`의 이름 없는 namespace에 둔다 ([[analysis/design]] 1절).
- 클래스의 private 타입(`RequestParser::State` 등)은 멤버 선언에 쓰이므로 헤더에 남는다. SF.22의 "API 클래스와 그 멤버"에 해당한다 (**판단**).
