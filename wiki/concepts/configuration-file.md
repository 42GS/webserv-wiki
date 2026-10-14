---
title: 설정 파일
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc9110.txt, raw/nginx-core-module.md, raw/nginx-request-processing.md]
updated: 2026-10-15
---

# 설정 파일

## 실행 방식

- `./webserv [configuration file]` (raw/subject.md:118).
- 설정 파일은 인자로 받거나 기본 경로에서 읽어야 함 (raw/subject.md:127). 인자 없이 실행해도 동작해야 한다.
- NGINX 설정의 `server` 섹션을 참고하라고 권장 (raw/subject.md:161).

## 필수 기능 (subject IV.3)

| 기능 | subject | 평가표 테스트 |
|---|---|---|
| `interface:port` 쌍 여러 개 listen | raw/subject.md:163 | 여러 interface·port에 여러 사이트 (raw/evaluation-sheet-en.md:68, raw/evaluation-sheet-en.md:107) |
| 기본 에러 페이지 | raw/subject.md:164 | 404 페이지 바꿔보기 (raw/evaluation-sheet-en.md:69) |
| 클라이언트 body 최대 크기 | raw/subject.md:165 | curl로 제한보다 길고 짧은 body POST (raw/evaluation-sheet-en.md:70) |
| 라우트별 허용 메서드 | raw/subject.md:167 | DELETE 허용/비허용 둘 다 (raw/evaluation-sheet-en.md:73) |
| HTTP 리다이렉션 | raw/subject.md:168 | 브라우저로 리다이렉트 URL (raw/evaluation-sheet-en.md:102) |
| 라우트 → 디렉토리 매핑 (root) | raw/subject.md:169 | 라우트별 다른 디렉토리 (raw/evaluation-sheet-en.md:71) |
| 디렉토리 리스팅 on/off | raw/subject.md:170 | 브라우저로 시도 (raw/evaluation-sheet-en.md:101) |
| 디렉토리 요청 시 기본 파일 (index) | raw/subject.md:171 | raw/evaluation-sheet-en.md:72 |
| 업로드 허용 + 저장 위치 | raw/subject.md:172 | 업로드 후 다운로드 (raw/evaluation-sheet-en.md:82) |
| 확장자 기반 CGI 실행 | raw/subject.md:173 | [[concepts/cgi]] |

- 라우트 매칭에 정규식은 필요 없음 (raw/subject.md:166).
- root 예시: `/kapouet` → `/tmp/www` 이면 `/kapouet/pouic/toto/pouet` → `/tmp/www/pouic/toto/pouet` (raw/subject.md:169).
  매칭된 location prefix를 떼고 root에 붙이는 방식이다.

> [!note] subject 예시는 NGINX `alias` 방식 (2026-10-15 확인)
> NGINX `root`는 경로를 만들 때 URI 전체를 root 값 뒤에 붙인다. `location /i/ { root /data/w3; }`에서 `/i/top.gif` → `/data/w3/i/top.gif` (raw/nginx-core-module.md:1507-1512, raw/nginx-core-module.md:1516).
> NGINX `alias`는 location 부분을 바꿔 끼운다. `location /i/ { alias /data/w3/images/; }`에서 `/i/top.gif` → `/data/w3/images/top.gif` (raw/nginx-core-module.md:132-140).
> subject 예시는 `/kapouet`를 떼고 `/tmp/www`에 붙이므로 **`alias` 방식**이다 (raw/subject.md:169). 설정 지시자 이름을 `root`로 하더라도 동작은 이 방식으로 구현하고, 디펜스에서 NGINX `root`와 다르다는 점을 설명할 수 있어야 한다.

## location 매칭 (NGINX 기준)

| 규칙 | 근거 |
|---|---|
| 매칭 전에 URI를 정규화한다: `%XX` 디코딩 → `.`·`..` 해석 → 연속된 `/`를 하나로 | raw/nginx-core-module.md:1063 |
| prefix location 중 **가장 길게 매칭되는 것**을 고른다 | raw/nginx-core-module.md:1067 |
| `=` 수식어는 정확히 일치할 때만 매칭, 일치하면 검색 종료 | raw/nginx-core-module.md:1077 |
| 연속 `/` 합치기는 prefix 매칭이 올바르게 동작하는 데 필요하다. `//scripts/one.php`가 `/scripts/`에 매칭되지 않는 문제를 막는다 | raw/nginx-core-module.md:1195-1205 |

- subject는 정규식이 필요 없다고 하므로 (raw/subject.md:166) prefix 매칭(가장 긴 것)만 구현하면 된다.
- 매칭에는 **query string을 뺀** URI 부분만 쓴다. 같은 인자를 여러 순서로 쓸 수 있기 때문이다 (raw/nginx-request-processing.md:147-152). `?` 뒤는 CGI에 `QUERY_STRING`으로 넘긴다 → [[concepts/cgi]].
- **index와 CGI:** NGINX의 index는 찾은 index 파일로 **내부 리다이렉트**해서 location을 다시 찾는다. 그래서 `index.php`가 선택되면 CGI location에서 처리된다 (raw/nginx-request-processing.md:168). 과제에서도 디렉토리 요청에서 고른 index 파일의 확장자가 CGI라면 CGI로 실행할지 정해 두어야 한다 (**판단**).
- 정규화 순서는 경로 공격 방어와 직결된다 → [[concepts/security]] 1절.

## server 선택 (NGINX 기준)

요청이 들어오면 NGINX는 두 단계로 server를 고른다 (raw/nginx-request-processing.md:92).

1. 요청을 받은 **IP 주소와 포트**를 각 server의 `listen`과 비교해 후보를 고른다.
2. 후보 안에서만 `Host` 헤더를 `server_name`과 비교한다. 맞는 server가 없으면 그 `address:port`의 **default server**가 처리한다.

- 예: `192.168.1.1:80`으로 `www.example.com`을 요청했는데 그 포트의 server에 그 이름이 없으면, 다른 IP의 server에 있더라도 `192.168.1.1:80`의 default server(첫 server)가 처리한다 (raw/nginx-request-processing.md:92).
- default server는 server 이름이 아니라 **listen 포트의 속성**이다. 포트마다 default가 다를 수 있다 (raw/nginx-request-processing.md:46, raw/nginx-request-processing.md:94).
- default를 지정하지 않으면 첫 server가 default다 (raw/nginx-request-processing.md:34, raw/nginx-core-module.md:963).

과제 적용:
- virtual host를 구현하지 않으면 `address:port`마다 server가 하나뿐이므로 1단계에서 끝난다. 같은 `address:port`가 두 번 나오면 설정 에러로 거부한다 (raw/evaluation-sheet-en.md:108).
- virtual host를 구현하면 위 2단계를 그대로 따르면 된다. Host가 없는 요청은 [[concepts/request-parsing]] 3절 참고.

## NGINX 지시자 대응표

subject 기능을 NGINX에서는 어떤 지시자로 하는지 정리했다. 설정 문법을 NGINX와 비슷하게 맞추면 평가자가 이해하기 쉽다 (raw/subject.md:161).

| subject 기능 | NGINX 지시자 | NGINX 동작 | 근거 |
|---|---|---|---|
| `interface:port` listen | `listen` | `address:port`, `address`만(포트 80), `port`만 지정 가능 | raw/nginx-core-module.md:936-943, raw/nginx-core-module.md:959 |
| 서버 이름 (virtual host) | `server_name` | 첫 이름이 primary server name | raw/nginx-core-module.md:1642-1650 |
| 기본 에러 페이지 | `error_page` | 지정 URI로 **내부 리다이렉트**. GET·HEAD 외 메서드는 GET으로 바뀜. 외부 URL이면 기본 302 | raw/nginx-core-module.md:533-542, raw/nginx-core-module.md:577 |
| body 크기 제한 | `client_max_body_size` | 초과 시 413. 기본 1m, 0이면 검사 안 함 | raw/nginx-core-module.md:356, raw/nginx-core-module.md:361 |
| 허용 메서드 | `limit_except` | 허용할 메서드 지정. GET을 허용하면 HEAD도 허용 | raw/nginx-core-module.md:795 |
| 디렉토리 매핑 | `root`, `alias` | 위 콜아웃 참고 | raw/nginx-core-module.md:1516, raw/nginx-core-module.md:132-140 |
| 응답 MIME 타입 | `types`, `default_type` | 확장자 → MIME 타입 매핑(대소문자 무시). 기본 타입 `text/plain` | raw/nginx-core-module.md:2003, raw/nginx-core-module.md:386-391 |
| 리다이렉션 | `return` (rewrite 모듈) | 이 문서 범위 밖 → [[source-wishlist]] P2 | — |
| 디렉토리 리스팅 | `autoindex` (autoindex 모듈) | 이 문서 범위 밖 → [[source-wishlist]] P2 | — |
| 기본 파일 (index) | `index` (index 모듈) | 이 문서 범위 밖 → [[source-wishlist]] P2 | — |

- `limit_except`로 막힌 메서드에 NGINX가 어떤 코드를 보내는지는 문서로 확인하지 못했다 (**미확인**, NGINX 실측 필요). 이 과제에서는 RFC 기준 405 + `Allow`를 따른다 (raw/rfc9110.txt:7603-7607).
- `error_page` 처리 중 또 에러가 나면 마지막 에러의 코드를 보낸다 (raw/nginx-core-module.md:568).

## 라우트 규칙을 응답으로 옮길 때 (RFC 9110)

- **허용 메서드:** 라우트에서 막은 메서드는 405로 응답하고 `Allow`에 허용 메서드 목록을 넣는다 (MUST, raw/rfc9110.txt:4724-4725, raw/rfc9110.txt:7605-7607). 서버가 아예 모르는 메서드는 501이다 (raw/rfc9110.txt:3800-3804).
- **redirection:** 설정에 상태 코드를 같이 적게 하는 게 좋다. 영구/임시, 메서드 유지 여부에 따라 301·302·307·308이 갈린다 (raw/rfc9110.txt:7384-7387, raw/rfc9110.txt:7492-7494). `Location`을 보낸다 (raw/rfc9110.txt:7378-7379). 표는 [[concepts/status-codes]].
- **root 매핑:** 매핑 결과가 root 밖으로 나가지 않게 막는다 (raw/rfc9110.txt:8563-8568) → [[concepts/security]].
- **body 크기 제한:** 초과하면 413 (raw/rfc9110.txt:7710-7714).

## 평가 시 준비물

- 모든 기능을 시연할 설정 파일과 기본 파일을 제출해야 함 (raw/subject.md:184).
- 평가자는 설정 파일 외 파일을 수정하지 않는다 (raw/evaluation-sheet-en.md:24). 시연용 설정을 기능별로 미리 준비해 두는 게 유리하다.

## 포트 관련 엣지 케이스 (Port issues)

| 테스트 | 기대 동작 | 근거 |
|---|---|---|
| 여러 interface·port에 다른 사이트 | 브라우저로 올바른 사이트 확인 | raw/evaluation-sheet-en.md:107 |
| 같은 `interface:port`에 여러 사이트 | **에러**. 단 virtual host를 구현했다면 그대로 동작해도 됨. 둘 다 유효 | raw/evaluation-sheet-en.md:108 |
| 서로 다른 설정 파일로 webserv **프로그램 여러 개**를 같은 interface:port로 동시 실행 | 동작하면 이유를 묻는다. 어떤 선택이든 동작이 일관되고 크래시가 없어야 함 | raw/evaluation-sheet-en.md:109 |

- 세 번째 테스트에서 두 번째 프로세스의 `bind()`는 보통 실패한다. 실패했을 때 에러를 출력하고 정상 종료하는지, 크래시하지 않는지가 핵심이다. `bind()` 실패 조건(`EADDRINUSE`)은 POSIX `bind()` 문서로 확인한다 (**미확인**, [[source-wishlist]] P2).

> [!note] virtual host 모순 해소 (2026-10-15)
> 구버전 정리본은 "다른 호스트네임으로 여러 서버"를 `curl --resolve`로 테스트했다 (raw/evaluation-sheet.md:65-68). 영어 원문에는 이 항목이 없다 (raw/evaluation-sheet-en.md:63-73).
> 원문은 virtual host를 **선택 사항**으로 둔다 (raw/evaluation-sheet-en.md:108). subject도 범위 밖·구현 자유라고 한다 (raw/subject.md:151). 두 문서가 일치한다.
> 구현 선택지:
> - virtual host 미구현: 같은 `interface:port` 중복 설정을 **설정 파싱 단계에서 에러**로 거부한다.
> - virtual host 구현: `Host` 헤더로 서버를 고른다. 디펜스에서 선택 이유를 설명한다.
>   NGINX에서 각 `address:port`에는 기본 server가 있다. `default_server`가 없으면 그 `address:port`를 쓰는 첫 번째 server가 기본이다 (raw/nginx-core-module.md:963). NGINX는 IP 기반과 이름 기반 virtual server를 따로 나누지 않는다 (raw/nginx-core-module.md:1628).
>   `Host`가 어느 `server_name`과도 맞지 않거나 `Host`가 없으면 그 포트의 default server가 처리한다 (raw/nginx-request-processing.md:34). 선택 순서는 아래 "server 선택" 절.
>   `Host`는 대상 URI의 host·port 정보로, 여러 호스트 이름을 서비스할 때 리소스를 구분하는 데 쓰인다 (raw/rfc9110.txt:2414-2417). 형식은 `uri-host [ ":" port ]` (raw/rfc9110.txt:2423).

## 관련

- [[concepts/http-features]], [[concepts/cgi]], [[sources/nginx-core-module]], [[sources/nginx-request-processing]]
