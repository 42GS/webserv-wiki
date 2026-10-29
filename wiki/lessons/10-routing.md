---
title: "레슨 10: 길 찾기 (라우팅)"
type: lesson
sources: [raw/rfc3986.txt, raw/nginx-core-module.md, raw/subject.md, raw/rfc9110.txt, raw/nginx-index-module.md]
updated: 2026-10-29
---

# 레슨 10: 길 찾기 (라우팅)

이전: [[lessons/09-request-parser]] · 다음: [[lessons/11-response]]

> [!example] 쉬운 예
> 우체부가 주소를 보고 배달한다. ① 주소를 깨끗하게 고쳐 쓴다("서울시//강남구/./역삼동" → "서울시/강남구/역삼동"). ② 가장 자세하게 맞는 담당 구역을 고른다("서울시 강남구"가 "서울시"보다 자세함). ③ 그 구역 규칙을 본다("이사 갔음", "소포 받기 금지"). ④ 실제 집(파일)을 찾는다.

## 10.1 경로 정리 (정규화)

`src/route/PathResolver.cpp:56-83` (줄임):

```cpp
bool normalizePath(const std::string& encodedPath, std::string& normalized) {
  // "/" 로 조각을 나눈 뒤, 조각마다 %XX를 한 번만 푼다
  if (!decodeSegment(조각, segment)) return false;   // 잘못된 %, %00, %2F → 400
  if (segment == "..") { if (kept.empty()) return false; kept.pop_back(); }  // 루트 위 → 400
  else if (!segment.empty() && segment != ".") kept.push_back(segment);     // "" 와 "." 은 버림
  ...
}
```

- **조각을 나눈 뒤에 푼다**: 먼저 풀면 `%2F`가 `/`가 되어 구분자로 오해된다. RFC 3986 2.4도 나눈 뒤 풀라고 한다 (raw/rfc3986.txt:754-758).
- **한 번만 푼다**: 두 번 풀면 `%2565` → `%65` → `e`처럼 바뀐다. 같은 문자열을 두 번 풀지 말라고 한다 (raw/rfc3986.txt:767-771).
- **`%00` 거부**: 원시 데이터를 받지 않는 곳에서는 거부하라고 한다 (raw/rfc3986.txt:2443-2445).
- **`%2F` 400** ([[analysis/design-decisions]] 3): 예약 문자를 풀면 URI의 뜻이 바뀐다 (raw/rfc3986.txt:689-692). NGINX는 `%2F`를 구분자로 쓰지만 → [[sources/nginx-observed-encoded-slash]], 우리는 해석이 갈리는 것을 아예 거부한다.
- **root 위로 가는 `..`는 400 + 닫기** (결정 2): RFC 3986은 루트에서 잘라 내지만, NGINX 실측처럼 400으로 거부한다 → [[sources/nginx-observed-directory]].

자세한 절차: [[concepts/security]] "경로 정규화 절차".

> [!example] 쉬운 예 — `..`
> "한 칸 뒤로"를 너무 많이 하면 건물 밖으로 나간다. `/../../etc/passwd`는 웹사이트 폴더 밖의 비밀 파일을 달라는 뜻이다. 건물 밖으로 나가려는 순간 "안 돼요(400)"라고 한다.

## 10.2 location 고르기

`src/route/Router.cpp:289-297`, `:140-145`:

```cpp
const LocationConfig* Router::matchLocation(const std::string& path) const {
  for (각 location, 긴 경로부터) {
    if (path가 prefix로 시작하지 않음) continue;
    if (!coversPath(location, path)) return 0;    // alias는 조각 경계에서만
    return &location;
  }
  return 0;                                         // → 404
}
```

location은 이미 긴 것부터 정렬돼 있어서([[lessons/06-config-parsing]]) 처음 맞는 것이 가장 긴 prefix다. NGINX도 prefix 중 가장 긴 것을 고른다 (raw/nginx-core-module.md:1067). 정규식 location은 필요 없다 (raw/subject.md:166).

> [!warning] 버그에서 배운 것 (결정 14)
> `location /kapouet { alias www/; }`에 `/kapouet../secret/s.txt`를 요청하니 alias 밖 파일이 200으로 나왔다. `kapouet..`는 `..` 조각이 아니라 정규화를 통과하고, location 부분을 떼면 `../secret/s.txt`가 alias 뒤에 붙었기 때문이다. 그래서 alias location은 떼고 남은 부분이 비었거나 `/`로 시작할 때만 맞춘다 (`Router.cpp:140-145`, [[analysis/test-plan]] R-20).

## 10.3 root와 alias

> [!example] 쉬운 예
> **root**: "모든 주소 앞에 '우리 동네'를 붙여라." `/i/top.gif` → `/data/w3` + `/i/top.gif`. **alias**: "이 구역 이름을 다른 이름으로 바꿔 끼워라." `/i/`를 `/data/w3/images/`로 바꿔 `/data/w3/images/top.gif`.

`src/route/Router.cpp:114-118`:

```cpp
std::string mapPath(const LocationConfig& location, const std::string& path) {
  if (!location.alias.empty())
    return location.alias + path.substr(location.path.size());   // 앞부분 바꿔 끼우기
  return location.root + path;                                    // URI 전체를 붙이기
}
```

subject의 예시("`/kapouet`이 `/tmp/www`에 root되면 `/kapouet/pouic/toto/pouet`은 `/tmp/www/pouic/toto/pouet`", raw/subject.md:169)는 NGINX로 치면 `alias` 방식이다 **(판단)**. NGINX의 root는 URI 전체를 붙인다 (raw/nginx-core-module.md:1516). 그래서 둘 다 지원한다 (결정 9) → [[concepts/configuration-file]] "subject 예시는 NGINX alias 방식".

## 10.4 결정 순서

`src/route/Router.cpp:328-360`:

```cpp
RouteResult Router::routePath(path, request, internalRedirects) const {
  location = matchLocation(path);           if (없음) return 404;
  if (location->returnCode != 0) return redirect(...);           // 1. return
  script = findScript(*location, path);                          // 2. CGI 스크립트?
  if (script가 있음) { if (!allows(...)) return 405; return script; }
  if (!answers(*location, method)) return 405 + Allow;           // 3. 메서드
  if (method == POST) return upload(...);                        // 4. 업로드
  fsPath = mapPath(*location, path);
  if (method == DELETE) return deletion(fsPath);                 // 5. 삭제
  kind = fileKind(fsPath);                                       // 6. 파일 시스템
  // 없음 → 404 / 디렉토리 → routeDirectory / 일반 파일 아님·못 읽음 → 403 / 아니면 STATIC_FILE
}
```

> [!tip] 왜 스크립트를 메서드 검사보다 먼저 찾나?
> 메서드 기준이 다르기 때문이다. 스크립트는 `limit_except`가 허용한 메서드면 모두 받는다(DELETE도 스크립트가 `REQUEST_METHOD`를 보고 스스로 처리). 일반 경로는 그 location이 그 메서드를 "할 수 있어야" 한다. 예를 들어 POST는 `upload_store`가 있어야 한다 (`Router.cpp:72-75`).

> [!example] 쉬운 예 — 405와 Allow
> 은행 창구에 "이 창구는 입금 불가. 가능한 일: 조회, 출금"이라고 붙어 있는 것과 같다. 405를 보낼 때는 받는 메서드 목록을 `Allow` 헤더로 꼭 알려야 한다 (MUST, RFC 9110 15.5.6, raw/rfc9110.txt:7603-7607, `Router.cpp:90-99`).

## 10.5 디렉토리 요청

1. 끝에 `/`가 없으면 `/`를 붙인 주소로 301 **(판단, NGINX 실측과 같음)**.
2. index 파일을 적힌 순서대로 찾아, 있으면 그 경로로 **다시 라우팅**한다. 그래서 `index.py`면 CGI로 실행된다 (결정 6). NGINX도 index를 내부 리다이렉트로 처리한다 (raw/nginx-index-module.md:46).
3. index가 없고 `autoindex on`이면 목록 HTML (이름은 HTML 이스케이프, 링크는 퍼센트 인코딩).
4. 둘 다 아니면 403 **(판단, NGINX 실측과 같음)**.

코드: `src/route/Router.cpp:375-398`, `src/handler/AutoindexHandler.cpp:103-120`. 근거: [[concepts/configuration-file]] "디렉토리 요청 처리 순서".

> [!question]- 확인 문제: `/docs`(끝 슬래시 없음)를 요청하면 왜 404인가?
> `location /docs/`는 `/docs`에 맞지 않아 `location /`가 처리하고, root인 `www/docs`가 없기 때문이다. NGINX도 끝 슬래시 301은 `proxy_pass` 등을 쓸 때만 한다 (raw/nginx-core-module.md:1115). 정적 파일이면 NGINX도 같다고 본다 **(판단)**.
