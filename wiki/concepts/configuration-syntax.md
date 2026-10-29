---
title: 설정 파일 문법 — 이 서버가 받는 형식 전체
type: concept
sources: [raw/subject.md, raw/nginx-core-module.md]
updated: 2026-10-29
---

# 설정 파일 문법

이 서버의 설정 파일이 받는 형식을 한곳에 모은 참고 문서다. 코드 기준은 webserv 커밋 `4db9510`(제출 저장소 `5122dee`와 같은 파일)이고, 아래 오류 메시지는 2026-10-29 Ubuntu 22.04 컨테이너에서 제출 코드를 빌드해 직접 실행한 결과다. 설정을 읽는 코드의 구조는 [[lessons/06-config-parsing]], 과제 요구와 NGINX 동작은 [[concepts/configuration-file]]에 있다.

과제는 NGINX 설정의 `server` 부분을 참고해도 된다고 하고 (raw/subject.md:161), 이 서버는 NGINX 문법을 따른다 ([[analysis/design-decisions]] 9).

## 1. 실행

```
./webserv [설정 파일]
```

- 인자가 없으면 `conf/default.conf`를 읽는다 (`include/core/Limits.hpp:25`). 인자가 둘 이상이면 사용법을 출력하고 끝난다 ([[lessons/05-startup]] 5.1). 과제는 명령줄 인자나 기본 경로로 설정 파일을 받으라고 한다 (raw/subject.md:127).
- 설정 파일이 없거나 일반 파일이 아니면(디렉토리 등) 시작하지 않는다 (`src/config/ConfigLoader.cpp:22-26`).
- `root`·`alias`·`upload_store`의 상대 경로는 서버를 실행한 디렉토리 기준이다. 경로를 그대로 이어 붙여 파일을 열기 때문이다 (`src/route/Router.cpp:114-118`) **(판단)**. 예제 설정은 저장소 최상위에서 실행하는 것을 전제로 한다 (`conf/default.conf:1-2`).

## 2. 글자 규칙

| 규칙 | 예 | 코드 |
|---|---|---|
| 토큰은 공백(스페이스, 탭, CR, LF)으로 나뉜다 | | `src/config/ConfigLexer.cpp:19` |
| `{`, `}`, `;`는 붙여 써도 따로 읽는다 | `listen 8080;` = `listen 8080 ;` | `src/config/ConfigLexer.cpp:28-30` |
| `#`부터 줄 끝까지 주석. 단어 중간의 `#`도 주석을 시작한다 | `root www;  # 사이트 파일` | `src/config/ConfigLexer.cpp:64-65` |
| 따옴표(`"`, `'`)는 쓸 수 없다. 공백이 든 경로는 쓸 수 없다 | `root "www";` → 오류 | `src/config/ConfigLexer.cpp:75-76` |
| 지시어 이름, 메서드, `on`/`off`는 대소문자를 구분한다 | `Listen`, `get`, `ON` → 오류 | `src/config/DirectiveRules.cpp:80`, `src/http/Methods.cpp:16-21`, `src/config/SharedSettings.cpp:66` |
| 크기의 단위는 `k`/`K`(1024), `m`/`M`(1024×1024). 단위가 없으면 바이트 | `2K`, `10m`, `64` | `src/config/ConfigValues.cpp:65-84` |
| 숫자는 10진 숫자만 받는다. 부호, 공백, 소수점은 안 된다 | | `src/http/Ascii.cpp:25-39` |

## 3. 구조

```nginx
server {                          # 최상위에는 server 블록만, 하나 이상
    지시어 인자 ... ;
    location /경로 {              # server 안에만
        지시어 인자 ... ;
        limit_except 메서드 ... { deny all; }   # location 안에만
    }
}
```

- 지시어는 `이름 인자... ;` 또는 `이름 인자... { ... }`이다 (`src/config/ConfigSyntax.cpp:118-158`).
- 최상위에는 `server` 블록만 올 수 있고, 하나도 없으면 오류다 (`src/config/ConfigBuilder.cpp:88-103`).
- `server`는 인자를 받지 않고, `listen`이 하나 이상 있어야 한다 (`src/config/ServerBuilder.cpp:144-146`, `:167-169`).
- 블록은 `server` > `location` > `limit_except`의 세 단계까지다. 더 깊으면 지시어 규칙보다 먼저 오류가 난다 (`src/config/ConfigSyntax.cpp:20`, `:140-142`).
- `location` 안의 `location`은 받지 않는다(`location`은 server에서만 허용, `src/config/DirectiveRules.cpp:56`).

## 4. 지시어 한눈에

규칙 표 `src/config/DirectiveRules.cpp:52-66`과 각 지시어를 적용하는 코드를 합친 것이다. "여러 번"이 X인 지시어가 한 블록에 두 번 나오면 `duplicate "이름"` 오류다 (`src/config/DirectiveRules.cpp:119-120`).

| 지시어 | 위치 | 인자 | 여러 번 | 기본값 | 과제 요구 |
|---|---|---|---|---|---|
| `listen` | server | `IPv4:포트` 또는 `포트` | O | 없음(필수) | raw/subject.md:163 |
| `error_page` | server | `코드... URI` | O | 내장 페이지 | raw/subject.md:164 |
| `client_max_body_size` | server, location | 크기 | X | `1m` | raw/subject.md:165 |
| `root` | server, location | 경로 | X | 없음 | raw/subject.md:169 |
| `alias` | location | 경로 | X | 없음 | raw/subject.md:169 |
| `index` | server, location | 파일 이름 1개 이상 | X | `index.html` | raw/subject.md:171 |
| `autoindex` | server, location | `on` 또는 `off` | X | `off` | raw/subject.md:170 |
| `location` | server | 경로 1개 + 블록 | O | 아래 6절 | raw/subject.md:166 |
| `limit_except` | location | 메서드 1개 이상 + `{ deny all; }` | X | GET·HEAD만 | raw/subject.md:167 |
| `return` | location | `코드 URL` | X | 없음 | raw/subject.md:168 |
| `upload_store` | location | 디렉토리 경로 | X | 없음(업로드 불가) | raw/subject.md:172 |
| `cgi` | location | `.확장자 절대경로` | O | 없음 | raw/subject.md:173 |

## 5. 지시어별 설명

### listen

```nginx
listen 127.0.0.1:8080;   # 이 주소의 8080
listen 8080;             # 모든 주소(0.0.0.0)의 8080
```

- 주소는 점으로 구분한 IPv4 네 숫자(각 0~255)만 받는다. `localhost` 같은 이름, 주소만 쓴 형식(`listen 127.0.0.1;`), `*:8080`은 오류다. 포트는 1~65535 (`src/config/ConfigValues.cpp:86-101`, [[analysis/design-decisions]] 13).
- 모든 server를 통틀어 같은 `주소:포트`가 두 번 나오면 오류다. virtual host를 구현하지 않았기 때문이다 ([[analysis/design-decisions]] 4).
- 같은 포트에 `0.0.0.0`과 특정 주소를 함께 쓰는 것도 오류다. macOS에서는 둘 다 bind되지만 Ubuntu에서는 안 되어서 두 OS 모두 거부한다 (`src/config/ConfigBuilder.cpp:45-62`, [[sources/os-observed-bind]]).
- 한 server에 `listen`을 여러 개 쓰면 그 server가 여러 주소에서 응답한다.

### error_page

```nginx
error_page 404 /errors/404.html;
error_page 500 502 504 /errors/50x.html;
```

- 마지막 인자가 URI이고 그 앞이 상태 코드다. URI는 `/`로 시작해야 하고, 코드는 300~599, 한 server에서 같은 코드를 두 번 쓸 수 없다 (`src/config/ServerBuilder.cpp:83-103`, 범위는 `:30-32`).
- URI는 요청 경로와 같은 location 규칙(root·alias)으로 파일을 찾는다. 파일이 일반 파일이 아니거나 1MB를 넘거나 읽을 수 없으면 내장 기본 페이지를 보낸다 (`src/handler/StatusPage.cpp:42-67`, `include/core/Limits.hpp:119`).

### client_max_body_size

```nginx
client_max_body_size 10m;
```

- 1바이트 이상 100MB 이하. `0`과 100MB 초과는 오류다 (`src/config/SharedSettings.cpp:28-38`, `include/config/ConfigLimits.hpp:33`, [[analysis/design-decisions]] 11). 기본값 1MB (`include/config/ConfigLimits.hpp:21`).
- 넘는 요청은 413이다 ([[lessons/09-request-parser]]).

### root와 alias

```nginx
root www;                                  # /a/b.html → www/a/b.html
location /kapouet/ { alias /tmp/www/; }    # /kapouet/pouic → /tmp/www/pouic
```

- `root`는 요청 경로 **전체**를 뒤에 붙이고, `alias`는 location 경로 부분을 떼고 **나머지**를 붙인다 (`src/route/Router.cpp:114-118`). 과제 예시(`/kapouet` → `/tmp/www`)는 `alias` 방식이다 (raw/subject.md:169).
- 문자열을 그대로 이어 붙이므로, `location /docs/ { alias www/documents; }`처럼 location은 `/`로 끝나는데 alias는 아니면 `/docs/a.html`이 `www/documentsa.html`이 된다. location과 alias의 끝 `/`를 맞춰 쓴다 **(판단: 위 코드에서)**.
- 한 location에 `root`와 `alias`를 함께 쓸 수 없다 (`src/config/LocationBuilder.cpp:201-203`).
- location에 둘 다 없으면 server의 `root`를 물려받는다. 물려받을 것도 없고 `return`도 없으면 오류다 (`src/config/LocationBuilder.cpp:204-210`).
- `alias` location은 경로 조각의 경계에서만 맞는다(예: `location /k { alias dir/; }`는 `/k/x`는 맡지만 `/k../x`는 맡지 않는다). 아니면 alias 디렉토리 밖을 가리킬 수 있어서다 (`src/route/Router.cpp:140-145`, [[lessons/10-routing]]).

### index

```nginx
index index.html index.py;
```

- 디렉토리를 요청하면 적은 순서대로 찾는다. 기본값 `index.html` (`src/config/SharedSettings.cpp:15`). 처리 순서는 [[lessons/10-routing]] 10.5.
- 이름에 `/`를 쓸 수 없다. `index ../secret.txt;`로 root 밖을 가리키지 못하게 한다 (`src/config/SharedSettings.cpp:59-63`, [[analysis/design-decisions]] 14).

### autoindex

```nginx
autoindex on;
```

- `on` 또는 `off`, 기본 `off` (`src/config/SharedSettings.cpp:45`, `:65-69`). 켜면 index 파일이 없는 디렉토리에서 목록 HTML을 보낸다.

### location

```nginx
location /upload/ { ... }
```

- 인자는 `/`로 시작하는 경로 하나다. NGINX의 `=`, `~` 같은 modifier와 정규식은 받지 않는다. 과제도 정규식은 필요 없다고 한다 (`src/config/LocationBuilder.cpp:178-184`, raw/subject.md:166).
- 한 server에 같은 경로의 location을 두 번 쓸 수 없다 (`src/config/ServerBuilder.cpp:129-131`).
- 요청에 맞는 location은 **가장 긴 prefix**다. 경로가 긴 location부터 정렬해 두고 앞에서부터 처음 맞는 것을 고른다 (`src/config/ServerBuilder.cpp:137-138`, `src/route/Router.cpp:289-297`).
- prefix는 문자열로 비교한다. `location /files`는 `/files/a`뿐 아니라 `/filesystem`에도 맞는다(root location의 경우. alias location은 위 경계 규칙). 디렉토리를 뜻하면 `/files/`처럼 `/`로 끝내 쓴다 **(판단: `src/route/Router.cpp:289-297`에서)**.
- 맞는 location이 없으면 404다 ([[lessons/10-routing]]).

### limit_except

```nginx
limit_except GET POST DELETE { deny all; }
```

- 적은 메서드만 허용한다. 받는 메서드는 `GET`, `HEAD`, `POST`, `DELETE`뿐이고, 다른 이름(`PUT` 등)은 오류다 (`src/config/LocationBuilder.cpp:91-98`, `src/http/Methods.cpp:10`).
- NGINX처럼 GET을 허용하면 HEAD도 허용한다 (`src/config/LocationBuilder.cpp:102-103`, raw/nginx-core-module.md:795).
- 블록 안에는 `deny all;` 하나만 쓸 수 있다 (`src/config/LocationBuilder.cpp:105-112`).
- **`limit_except`가 없는 location은 GET·HEAD만 받는다.** POST·DELETE는 적어야 열린다 (`src/config/LocationBuilder.cpp:46-55`, [[analysis/design-decisions]] 16).
- 허용하지 않은 메서드는 405 + `Allow`, 서버가 모르는 메서드는 501이다 ([[concepts/configuration-file]] "라우트 규칙을 응답으로 옮길 때").

### return

```nginx
location /old/ { return 301 /about.html; }
```

- 코드는 301, 302, 303, 307, 308만 받는다 (`src/config/LocationBuilder.cpp:23-28`, `:66-75`). URL은 검사하지 않고 `Location`에 그대로 쓴다 (`src/app/RequestProcessor.cpp:268`).
- `return`이 있으면 그 location의 다른 처리보다 먼저 리다이렉트한다 ([[lessons/10-routing]]).

### upload_store

```nginx
location /upload/ {
    limit_except GET POST DELETE { deny all; }
    upload_store www/upload;
}
```

- 있으면 그 location이 `multipart/form-data` POST를 파일 업로드로 받아 이 디렉토리에 저장한다 ([[lessons/12-upload-delete]]). 이 서버가 새로 만든 지시어다 ([[lessons/06-config-parsing]] 6.1).
- POST도 `limit_except`에 있어야 한다. CGI 스크립트가 아닌 경로의 POST는 `upload_store`가 있는 location에서만 받는다 (`src/route/Router.cpp:72-75`).
- 디렉토리가 있는지는 시작할 때 검사하지 않는다 **(판단: 설정 코드에 검사가 없음, `src/config/LocationBuilder.cpp:167-168`)**.

### cgi

```nginx
location /cgi-bin/ {
    limit_except GET POST { deny all; }
    cgi .py  /usr/bin/python3;
    cgi .php /usr/bin/php-cgi;
}
```

- 확장자는 `.`으로 시작하고 두 글자 이상, 프로그램은 절대 경로여야 한다. 한 location에서 같은 확장자를 두 번 쓸 수 없다 (`src/config/LocationBuilder.cpp:126-143`).
- 절대 경로만 받는 이유: 스크립트를 자기 디렉토리에서 실행하므로 상대 경로 프로그램은 거기서 찾을 수 없다 (`src/config/LocationBuilder.cpp:132-138`). 이 서버가 새로 만든 지시어다.
- 실행 과정은 [[lessons/13-cgi]].

## 6. 물려받기와 자동으로 생기는 것

- `index`, `autoindex`, `client_max_body_size`, `root`는 server에 쓰면 location이 물려받고, location에 쓰면 그 location에서만 덮어쓴다 (`src/config/LocationBuilder.cpp:186-205`).
- location은 server 블록을 다 읽은 뒤에 만들므로, server 지시어를 location 뒤에 써도 물려받는다 (`src/config/ServerBuilder.cpp:105-113`의 주석, `:170`).
- location `/`가 없고 server에 `root`가 있으면 location `/`를 자동으로 만든다. 이 location은 server 값을 물려받고 GET·HEAD만 받는다 (`src/config/ServerBuilder.cpp:135-136`, `src/config/LocationBuilder.cpp:214-218`).
- 그래서 가장 짧은 설정은 이렇다(2026-10-29 실행해 시작 확인).

```nginx
server {
    listen 8080;
    root www;
}
```

## 7. 오류 메시지

설정이 잘못되면 서버는 `webserv: 파일:줄: 설명`을 표준 에러에 출력하고 종료 코드 1로 끝난다(크래시가 아니라 시작 거부, `src/main.cpp:31-34`, `src/config/ConfigError.cpp:25-32`). 줄 번호는 문제 지시어의 시작 줄이다.

2026-10-29 Ubuntu 22.04 컨테이너에서 제출 코드(`5122dee`)를 빌드해 실행한 결과 (파일 이름은 `t.conf`로 줄임):

| 잘못된 설정 | 출력 |
|---|---|
| `root "www";` | `t.conf:3: quoted strings are not supported` |
| `listen 8080` (`;` 없음) | `t.conf:2: directive "listen" is not terminated by ";"` |
| 최상위에 `listen 8080;` | `t.conf:1: unknown top-level directive "listen" (only "server" is allowed)` |
| server 블록 없음 | `t.conf:1: no "server" block` |
| server에 `listen` 없음 | `t.conf:1: "server" has no "listen"` |
| `listen 127.0.0.1;` | `t.conf:2: invalid listen address "127.0.0.1" (expected IPv4:port or port, e.g. 127.0.0.1:8080)` |
| `listen 8080;`과 `listen 127.0.0.1:8080;` | `t.conf:6: listen 127.0.0.1:8080 conflicts with 0.0.0.0:8080` |
| `root`를 한 블록에 두 번 | `t.conf:4: duplicate "root"` |
| `client_max_body_size 0;` 또는 `101m;` | `t.conf:4: "client_max_body_size" must be between 1 and 100m` |
| `error_page 200 /x.html;` | `t.conf:4: invalid error_page code "200"` |
| `index ../x;` | `t.conf:4: "index" file name must not contain "/"` |
| `location = /x { }` | `t.conf:4: "location" takes exactly one path (modifiers are not supported)` |
| location 안에 location | `t.conf:4: "location" is not allowed in "location"` |
| `root`·`alias`가 둘 다 없는 location | `t.conf:3: location "/a/" has no "root" or "alias"` |
| 한 location에 `root`와 `alias` | `t.conf:3: "root" and "alias" in the same location` |
| `limit_except PUT { deny all; }` | `t.conf:4: unsupported method "PUT" in "limit_except"` |
| `limit_except GET { allow all; }` | `t.conf:4: "limit_except" block must contain only "deny all;"` |
| `return 404 /b;` | `t.conf:3: "return" code must be 301, 302, 303, 307 or 308` |
| `cgi .py python3;` | `t.conf:4: "cgi" program must be an absolute path` |

## 8. NGINX와 다른 점

| 항목 | NGINX | 이 서버 |
|---|---|---|
| `listen` | 주소만, 포트만, 호스트 이름도 받는다. 주소만 쓰면 포트 80 (raw/nginx-core-module.md:936-943, raw/nginx-core-module.md:959) | `IPv4:포트`와 `포트`만 |
| `client_max_body_size 0` | 크기 검사를 끈다 (raw/nginx-core-module.md:361) | 오류 (1~100MB) |
| `error_page` | 지정 URI로 내부 리다이렉트 ([[concepts/configuration-file]] NGINX 지시자 대응표) | 그 URI의 파일을 읽어 보낸다 ([[analysis/design]] 3절) |
| `limit_except` 블록 | 접근 제어 지시어를 쓴다 (raw/nginx-core-module.md:795) | `deny all;`만 |
| `location` | modifier와 정규식 | prefix만 |
| `limit_except`가 없는 location | 메서드를 제한하지 않는다 **(판단: `limit_except`가 제한을 거는 지시어라서. 문서 문장으로 확인하지 않음)** | GET·HEAD만 |
| `upload_store`, `cgi` | 없음 | 이 서버가 만든 지시어 |
| `server_name` | virtual host | 없음 (같은 `주소:포트` 금지) |

## 관련

- [[lessons/06-config-parsing]] — 설정을 읽는 코드 (lexer → 지시어 나무 → builder)
- [[concepts/configuration-file]] — 과제 요구, NGINX 동작, 포트 엣지 케이스
- [[lessons/10-routing]] — 설정이 요청 처리에 쓰이는 방식
