---
title: "레슨 4A: 이 코드를 읽기 위한 C++98 기초"
type: lesson
sources: [raw/subject.md, raw/cpp-core-guidelines.md]
updated: 2026-10-29
---

# 레슨 4A: 이 코드를 읽기 위한 C++98 기초

이전: [[lessons/04-poll]] · 다음: [[lessons/05-startup]]

코드 기준: webserv 커밋 `4db9510`. 다음 장부터 서버 코드를 본격적으로 읽는다. 그 전에 코드에 계속 나오는 C++ 문법과 습관을 모아 본다. C를 안다고 가정한다.

## 4A.1 C++98이라는 약속

과제는 `c++`와 `-Wall -Wextra -Werror`로 컴파일하고, `-std=c++98`을 붙여도 컴파일돼야 한다고 한다. C 함수 대신 C++ 쪽(`<string.h>` 대신 `<cstring>`)을 고르라고도 한다 (raw/subject.md:49-51).

요즘 C++ 자료에 흔한 문법 중 C++98에 없는 것이 많다. 2026-10-29에 Ubuntu 22.04의 g++ 11.4.0으로 `-std=c++98 -pedantic-errors -Wall -Wextra -Werror`를 주고 직접 컴파일해 확인했다.

| 요즘 문법 | C++98 결과 (실행 확인) | 이 코드에서 대신 쓰는 것 |
|---|---|---|
| `= delete` | 오류: C++11부터 | 복사 함수를 private에 선언만 한다 (4A.4) |
| `nullptr` | 오류: 선언되지 않은 이름 | `0` (`src/core/Server.cpp:55`) |
| `auto x = 1;` | 오류: 타입이 아님 | 타입을 직접 쓴다 |
| `override` | 오류: C++11부터 | 쓰지 않는다 |

아래에서 인용하는 C++ Core Guidelines는 C++11 이후를 기준으로 쓴 문서라 예제에 C++98에 없는 문법이 나온다. 규칙의 이유만 빌려 온다 **(판단)**.

## 4A.2 const와 참조

> [!example] 쉬운 예
> 책을 친구에게 보여 줄 때 복사본을 만들어 줄 수도 있고(값 전달), 원본을 "읽기만 해"라며 보여 줄 수도 있다(`const` 참조). 두꺼운 책이면 복사가 아깝다.

- 읽기만 하는 인자는 싼 타입(정수, 포인터)이면 값으로, 나머지는 `const` 참조로 넘긴다. 두 방법 모두 호출자에게 "인자를 바꾸지 않는다"고 알린다 (raw/cpp-core-guidelines.md:3000). 예: `void f1(const string& s);`는 좋고 `void f2(string s);`는 비쌀 수 있다 (raw/cpp-core-guidelines.md:3007-3009).
- 객체의 보이는 상태를 바꾸지 않는 멤버 함수에는 `const`를 붙인다. 의도가 분명해지고 컴파일러가 실수를 더 잡는다 (raw/cpp-core-guidelines.md:16986-16987).

```cpp
// include/core/Logger.hpp:55
void access(std::time_t now, const std::string& entry) const;
```

`entry`는 `const` 참조라 복사하지 않고 바꾸지도 않는다. 끝의 `const`는 "이 함수는 `Logger`를 바꾸지 않는다"는 약속이다. 그래서 `const Logger&`만 가진 쪽(`ConnectionServices`)도 로그를 쓸 수 있다 ([[analysis/design-decisions]] 19).

## 4A.3 생성자·소멸자와 RAII

> [!example] 쉬운 예
> 도서관 책을 빌리면 반납해야 한다. "빌릴 때 반납 예약을 같이 걸어 두고, 내가 도서관을 나가면 자동으로 반납되게" 하면 잊을 일이 없다. 생성자에서 빌리고 소멸자에서 반납하는 것이 RAII다.

자원을 얻고 돌려주는 함수 쌍(`fopen`/`fclose`, `new`/`delete`)이 있으면, 그 자원을 객체로 감싸 생성자에서 얻고 소멸자에서 돌려주라고 한다. 누수를 막고 직접 관리하는 복잡함을 줄이기 위해서다 (raw/cpp-core-guidelines.md:9468-9470). C++은 객체가 범위를 벗어나면 소멸자를 반드시 부른다. 중간에 `return`하거나 예외가 나도 마찬가지다 **(판단: C++ 표준 절로 확인하지 않음. 위 가이드라인의 "language-enforced constructor/destructor symmetry"가 같은 뜻이다)**.

```cpp
// src/core/Logger.cpp:48, :50
Logger::Logger() : accessFd_(-1), errorFd_(-1) {}
Logger::~Logger() { close(); }
```

`Logger`는 파일 두 개를 `open()`에서 열고, 소멸자에서 닫는다 (`src/core/Logger.cpp:72-77`). `main`의 지역 변수라 `main`이 어떤 길로 끝나도 파일이 닫힌다.

> [!tip] 왜 이렇게?
> 여는 일은 생성자가 아니라 `open()`이 한다. 열기 실패를 `bool`로 돌려받아 "로그 파일을 열 수 없다"는 이유를 출력하고 시작을 거부하려는 것이다 ([[analysis/design-decisions]] 19). 생성자는 값을 돌려줄 수 없어 실패를 알리려면 예외를 던져야 한다 **(판단)**. 돌려주는 쪽은 소멸자 하나라 닫기를 잊을 일은 없다.

## 4A.4 복사 막기

> [!example] 쉬운 예
> 사물함 열쇠(fd)를 복사해 두 사람이 나눠 가지면, 한 사람이 사물함을 반납한 뒤 다른 사람이 엉뚱한 사물함을 열 수 있다. 열쇠는 복사하지 못하게 한다.

C++은 복사 생성자와 대입 연산자를 저절로 만든다. fd를 가진 객체가 복사되면 소멸자 두 개가 같은 fd를 두 번 닫는다 **(판단)**. 가상 함수가 있는 클래스는 값으로 복사하면 파생 부분이 잘려 나가는(slicing) 문제도 있다 (raw/cpp-core-guidelines.md:6596).

C++98에는 `= delete`가 없어서(4A.1) private에 선언만 하고 정의하지 않는다.

```cpp
// include/core/Logger.hpp:67-70
  // Not copyable: declared and never defined (C++98 has no "= delete").
  // 복사하지 않는다: 선언만 하고 정의하지 않는다 (C++98에는 "= delete"가 없다).
  Logger(const Logger&);
  Logger& operator=(const Logger&);
```

밖에서 복사하면 private이라 컴파일 오류가 난다(4A.1과 같은 날 g++ 11.4.0으로 확인: `'L::L(const L&)' is private within this context`). `Server`, `Listener`, `Connection`, `CgiProcess` 등 자원을 가진 클래스가 모두 이렇게 한다 (예: `include/http/Connection.hpp:129`).

## 4A.5 인터페이스와 virtual

> [!example] 쉬운 예
> 콘센트 규격이다. 전기를 주는 쪽(이벤트 루프)은 꽂힌 것이 선풍기인지 충전기인지 모르고, 규격(인터페이스)만 맞으면 전기를 준다.

이벤트 루프는 listen 소켓, 클라이언트 연결, CGI pipe를 모두 같은 방법으로 다룬다. 그 "규격"이 `IoHandler`다.

```cpp
// include/core/IoHandler.hpp:21-47 (Doxygen 주석은 뺐다)
class IoHandler {
 public:
  virtual ~IoHandler() {}
  virtual int fd() const = 0;
  virtual short wantedEvents() const = 0;
  virtual void onEvent(short revents) = 0;
  virtual void onFailure() = 0;
};
```

- `= 0`은 순수 가상 함수다. 몸체가 없고, 파생 클래스가 반드시 채워야 한다. `class Listener : public IoHandler` (`include/core/Listener.hpp:44`), `class Connection : public IoHandler` (`include/http/Connection.hpp:32`)가 그렇게 한다.
- 데이터 멤버가 없는 추상 클래스는 상태를 가진 기반 클래스보다 잘 바뀌지 않는다 (raw/cpp-core-guidelines.md:2170). `IoHandler`에는 데이터가 없다.
- 기반 클래스의 소멸자는 public이면 virtual이어야 한다. 기반 포인터로 파생 객체를 지울 때 소멸자가 virtual이 아니면 정의되지 않은 동작이다 (raw/cpp-core-guidelines.md:5372-5373). 그래서 `virtual ~IoHandler() {}`가 있다.

## 4A.6 new/delete와 소유

`new`로 만든 객체는 `delete`할 책임자(소유자)가 정해져 있어야 한다. `new`의 결과를 그냥 포인터에 두면 새어 나갈 수 있다 (raw/cpp-core-guidelines.md:9789-9790). C++98에는 `std::unique_ptr`가 없고 `std::auto_ptr`는 이후 표준에서 deprecated라, 이 서버는 소유자를 한 곳으로 정하고 그 소멸자에서 지운다 (`src/core/Server.cpp:34-39`의 주석).

| 소유자 | 가진 것 | 지우는 곳 |
|---|---|---|
| `Server` | `std::vector<Listener*> listeners_`, `std::map<int, Connection*> connections_` (`include/core/Server.hpp:130`, `:132`) | `Server::~Server` (`src/core/Server.cpp:22-28`) |
| `EventLoop` | 아무것도 소유하지 않는다. 포인터만 빌린다 (`include/core/IoHandler.hpp:53-54`) | — |

```cpp
// src/core/Server.cpp:40-46 — vector에 넣다가 실패하면 직접 지운다
Listener* listener = new Listener(config, config.listens[j], *this);
try {
  listeners_.push_back(listener);
} catch (...) {
  delete listener;
  throw;
}
```

`push_back`은 메모리가 모자라면 `std::bad_alloc`을 던질 수 있다. 그 순간 `listener`는 아직 누구의 것도 아니라 여기서 지워야 한다 **(판단)**.

## 4A.7 예외

C++ 예외는 `throw`로 던지고 `try`/`catch`로 받는다. 이 서버에서 예외가 나는 곳은 주로 메모리 부족(`std::bad_alloc`)이다 **(판단)**. 과제는 메모리가 모자라도 죽으면 안 된다고 한다 → [[lessons/14-resilience]].

```cpp
// src/core/EventLoop.cpp:57-70 중 일부
try {
  polled[i]->onEvent(revents[i]);
} catch (const std::exception&) {
  polled[i]->onFailure();
}
```

연결 하나에서 예외가 나면 그 연결만 닫고(`Connection::onFailure`는 상태를 CLOSED로 바꾼다, `src/http/Connection.cpp:95`) 서버는 계속 돈다. 그래도 루프 밖까지 온 예외는 `main`이 받아 메시지를 내고 끝낸다 (`src/main.cpp:91-95`).

> [!info] 평가 때
> - "C++98로 컴파일되나?"는 `Makefile`의 플래그로 바로 보여 줄 수 있다 ([[concepts/build-and-submission]]).
> - "fd를 가진 객체가 복사되면?"이라는 질문에는 4A.4의 private 선언을 보여 준다.
> - "메모리가 모자라면?"에는 4A.7의 `try`/`catch`와 [[lessons/14-resilience]]를 보여 준다.

> [!question]- 확인 문제 1: `IoHandler`의 소멸자에서 `virtual`을 빼면 무엇이 문제일까?
> 이벤트 루프나 `Server`가 기반 포인터로 파생 객체를 지울 때 정의되지 않은 동작이 된다 (raw/cpp-core-guidelines.md:5372-5373). 이 서버는 `Server`가 `Connection*`·`Listener*`로 지우지만, 규칙을 지켜 두면 나중에 `IoHandler*`로 지워도 안전하다 **(판단)**.

> [!question]- 확인 문제 2: 복사 생성자를 private에 선언만 하고 정의하지 않으면, 클래스 안에서 실수로 복사할 때는 어떻게 될까?
> 클래스 안에서는 private에 접근할 수 있어 컴파일은 되지만, 정의가 없어 링크할 때 오류가 난다. 2026-10-29에 4A.1과 같은 환경에서 멤버 함수 안에 `return L(*this);`를 넣어 보니 컴파일은 통과하고 링크에서 ``undefined reference to `L::L(L const&)'``가 났다.

> [!question]- 확인 문제 3: `void f(std::string s)`와 `void f(const std::string& s)`의 차이는?
> 앞은 호출할 때마다 문자열을 복사하고, 뒤는 복사하지 않고 읽기만 한다. 둘 다 인자를 바꾸지 않는다는 뜻은 같다 (raw/cpp-core-guidelines.md:3000, raw/cpp-core-guidelines.md:3007-3009).
