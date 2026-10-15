---
title: php-cgi 실측 — 실행할 파일을 찾는 변수와 REDIRECT_STATUS
type: source
sources: [raw/php-cgi-observed-env.md, raw/php-src-cgi_main.c, raw/rfc3875.txt]
updated: 2026-10-15
---

# php-cgi 실측 — 실행할 파일을 찾는 변수와 `REDIRECT_STATUS`

원본: `raw/php-cgi-observed-env.md`. Ubuntu 24.04 Docker 이미지에 `php-cgi` 패키지를 설치하고, `env -i`로 환경 변수를 정해 php-cgi를 직접 실행한 출력을 그대로 담았다 (2026-10-15, raw/php-cgi-observed-env.md:3-4). 웹 서버는 거치지 않았다.

- 버전: `php8.3-cgi 8.3.6-0ubuntu0.24.04.11` (raw/php-cgi-observed-env.md:16), 설정 파일 `/etc/php/8.3/cgi/php.ini`에서 `cgi.force_redirect='1'`, `cgi.fix_pathinfo='1'`, `cgi.discard_path='0'` (raw/php-cgi-observed-env.md:134-139).
- 코드를 읽은 결과는 [[sources/php-src-cgi-main]]. 이 측정은 그 결과가 실제 패키지에서도 같은지 확인한 것이다.

## 결과

공통 변수는 `GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1`이다 (A만 제외, raw/php-cgi-observed-env.md:68, raw/php-cgi-observed-env.md:79).

| 경우 | 넘긴 변수 | 결과 | 근거 |
|---|---|---|---|
| A | 공통 변수 없이 `SCRIPT_FILENAME`만 | `REDIRECT_STATUS` 없이도 실행됨 | raw/php-cgi-observed-env.md:121-128 |
| B1 | `REDIRECT_STATUS` 없음 | "Security Alert!" HTML, **헤더 없음**, exit 255 | raw/php-cgi-observed-env.md:142-152 |
| B2 | `REDIRECT_STATUS=0` | 실행됨 | raw/php-cgi-observed-env.md:154-161 |
| B3 | `REDIRECT_STATUS=` (빈 값) | 실행됨 | raw/php-cgi-observed-env.md:163-170 |
| B4 | `HTTP_REDIRECT_STATUS=200`만 | B1과 같이 거부 | raw/php-cgi-observed-env.md:172-182 |
| C1 | `PATH_TRANSLATED`만 | 그 파일이 실행됨. `SCRIPT_FILENAME`이 같은 값으로 채워짐 | raw/php-cgi-observed-env.md:185-192 |
| C2 | `SCRIPT_FILENAME=t.php`, `PATH_TRANSLATED=other.php` | `t.php` 실행 | raw/php-cgi-observed-env.md:194-201 |
| C3 | C2 + `REDIRECT_URL=/t.php` | `other.php` 실행 | raw/php-cgi-observed-env.md:203-207 |
| C4 | C2 + `-d cgi.fix_pathinfo=0` | `other.php` 실행 | raw/php-cgi-observed-env.md:209-213 |
| C5 | `SCRIPT_FILENAME=t.php`, `PATH_INFO=/x/y`, `PATH_TRANSLATED=/www/x/y` | `t.php` 실행, 세 값이 그대로 보임 | raw/php-cgi-observed-env.md:215-222 |
| D1 | 없는 파일 | `Status: 404 Not Found`, "No input file specified.", exit 255 | raw/php-cgi-observed-env.md:225-230 |
| D2 | `SCRIPT_FILENAME`·`PATH_TRANSLATED` 모두 없음 | D1과 같음 | raw/php-cgi-observed-env.md:232-237 |
| D3 | 읽기 권한 없는 파일 (`nobody`로 실행) | `Status: 403 Forbidden`, "Access denied.", exit 255. stderr에 경고 한 줄 | raw/php-cgi-observed-env.md:246-253, raw/php-cgi-observed-env.md:259 |

- cases.sh 전체(A~D2)에서 stderr 출력은 없었다 (raw/php-cgi-observed-env.md:241). D3의 경고만 stderr로 나왔다.

## 소스와 맞춰 본 것

- B2·B3: 값은 보지 않고 변수가 있는지만 본다는 코드 (raw/php-src-cgi_main.c:1898)와 같다.
- A: `SERVER_SOFTWARE`, `SERVER_NAME`, `GATEWAY_INTERFACE`, `REQUEST_METHOD`가 하나도 없으면 CGI 모드가 아니라서 (raw/php-src-cgi_main.c:1787-1795) `REDIRECT_STATUS` 검사를 하지 않는다 (raw/php-src-cgi_main.c:1887). 실제 서버는 `GATEWAY_INTERFACE`·`REQUEST_METHOD`를 넘기므로 이 경우는 생기지 않는다 (**판단**).
- C1~C4: `SCRIPT_FILENAME` 우선 (raw/php-src-cgi_main.c:1161-1170), `REDIRECT_URL` 예외 (raw/php-src-cgi_main.c:1229-1240), `fix_pathinfo` 꺼짐 예외 (raw/php-src-cgi_main.c:1424-1434)와 같다.
- D1·D3: 열기 실패 처리 (raw/php-src-cgi_main.c:2469-2478)와 같다.
- B1: 코드는 응답 코드를 400으로 정하지만 (raw/php-src-cgi_main.c:1900), 실제 출력에는 `Status` 헤더도 `Content-type`도 없이 HTML만 나왔다 (raw/php-cgi-observed-env.md:142-152). 왜 헤더가 나가지 않는지는 소스에서 확인하지 않았다.

## 과제 적용 (판단)

- B1처럼 헤더 없이 본문만 오는 출력은 RFC 3875의 CGI 필드가 하나도 없으므로 (raw/rfc3875.txt:1355-1357) 502로 처리한다 → [[concepts/cgi]] 5절. `REDIRECT_STATUS`를 빠뜨렸을 때 디펜스에서 보게 되는 증상이다.
- D1·D3은 종료 코드가 255지만 출력은 올바른 CGI 응답이다. 종료 코드가 아니라 출력을 보고 `Status` 값(404·403)을 그대로 응답에 쓴다 → [[concepts/cgi]] 5절의 기존 판단과 같다.
- C3·C4 때문에 `REDIRECT_URL`은 넘기지 않고, `PATH_TRANSLATED`는 `PATH_INFO`가 있을 때만 넣는다 → [[sources/php-src-cgi-main]] "과제 적용".

> [!note] 측정 범위
> Ubuntu 24.04 패키지 하나, arm64 이미지, 웹 서버 없이 직접 실행, GET만 측정했다. POST 본문(`CONTENT_LENGTH`·stdin) 처리는 측정하지 않았다. 평가 PC와 같은 Ubuntu 22.04(php8.1-cgi)에서 같은 스크립트로 다시 측정해 같은 결과를 얻었다 → [[sources/ubuntu2204-observed-tools]].
