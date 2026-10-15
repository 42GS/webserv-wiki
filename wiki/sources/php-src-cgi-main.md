---
title: PHP 소스 — php-cgi 진입점 (sapi/cgi/cgi_main.c)
type: source
sources: [raw/php-src-cgi_main.c, raw/php-cgi-force-redirect.md, raw/php-ini-core.md, raw/rfc3875.txt]
updated: 2026-10-15
---

# PHP 소스 — php-cgi 진입점 (sapi/cgi/cgi_main.c)

원본: `raw/php-src-cgi_main.c`. <https://raw.githubusercontent.com/php/php-src/6d99ccc268b5ec88cc281eb3e90e29b59677fda3/sapi/cgi/cgi_main.c>를 2026-10-15에 받아 그대로 저장했다. C 소스라 변환하지 않았다.

- 커밋 `6d99ccc268b5ec88cc281eb3e90e29b59677fda3` (2024-09-26)는 받을 때 `PHP-8.3` 브랜치에서 이 파일을 마지막으로 바꾼 커밋이었다. (받을 때 GitHub API에서 본 값이고 raw 파일에는 없다.)
- Ubuntu 24.04의 `php8.3-cgi`는 `8.3.6-0ubuntu0.24.04.11`이고, changelog에 `REDIRECT_STATUS` 검사를 고친 CVE-2024-8927 패치가 들어 있다 (2026-10-15 컨테이너에서 확인, raw에 없음). 태그 `php-8.3.6` 원본은 이 패치 전이라 `HTTP_REDIRECT_STATUS`도 받는다 (같은 날 태그 파일을 받아 읽음, raw에 없음). 그래서 패치 뒤 브랜치 파일을 받았다. 평가 PC의 php-cgi가 같은 코드인지는 **미확인**이다 (평가 때 `php-cgi -v`).
- 받은 목적: php-cgi가 실행할 파일을 어느 변수로 찾는지, `REDIRECT_STATUS` 값에 조건이 있는지 → [[concepts/cgi]] "php-cgi가 추가로 요구하는 변수". 아래 내용은 코드를 읽은 결과이고, 실제 실행 결과는 [[sources/php-cgi-observed-env]]에 있다.

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| `init_request_info` 앞부분 (1158-1170) | 실행할 파일 경로를 `SCRIPT_FILENAME`에서, 없으면 `PATH_TRANSLATED`에서 가져옴 | [[concepts/cgi]] |
| `cgi.fix_pathinfo` 처리 (1212-1423) | `REDIRECT_URL`이 있을 때의 Apache용 처리, 파일이 없을 때 경로를 잘라 `PATH_INFO`를 만드는 처리 | [[concepts/cgi]] |
| `fix_pathinfo` 꺼짐 (1424-1434) | PHP 4.3 이전 방식 | [[concepts/cgi]] |
| CGI 모드 판정 (1787-1795) | 환경 변수 4개 중 하나가 있으면 CGI 모드 | [[concepts/cgi]] |
| `force_redirect` 검사 (1886-1924) | `REDIRECT_STATUS`가 없으면 거부 | [[concepts/cgi]] |
| 스크립트 열기 실패 (2469-2478) | 403 "Access denied." 또는 404 "No input file specified." | [[concepts/cgi]] |

다루지 않는 부분: FastCGI, Windows·RISC OS 전용 코드, 명령행 옵션 처리, 인증 헤더 처리.

## 원문으로 확인한 것

### 실행할 파일을 찾는 변수

- 먼저 `SCRIPT_FILENAME`을 실행할 파일 경로로 잡고, 이것이 없고 `PATH_TRANSLATED`가 있을 때만 `PATH_TRANSLATED`를 쓴다 (raw/php-src-cgi_main.c:1161-1170).
- `cgi.fix_pathinfo`가 켜져 있으면(raw/php-src-cgi_main.c:1212, 기본값 `1`, raw/php-ini-core.md:426) 예외가 하나 있다. `PATH_TRANSLATED`와 `REDIRECT_URL`이 모두 있고 `PATH_TRANSLATED`가 앞에서 잡은 경로와 다르면 `PATH_TRANSLATED`로 바꾼다. 주석은 이것을 거의 Apache 전용 처리라고 한다 (raw/php-src-cgi_main.c:1229-1240).
- 같은 설정에서 경로가 `/`로 끝나거나 `realpath`로 풀리지 않으면, `/`를 따라 거슬러 올라가며 `stat`해서 경로에서 `PATH_INFO`를 떼어 내려 한다. 주석은 파일이 없을 때의 처리이고 `/info.php/test` 같은 URL을 위한 것이라고 한다 (raw/php-src-cgi_main.c:1248-1260).
- `cgi.fix_pathinfo`가 꺼져 있으면(1212줄 `if`의 `else`, 들여쓰기로 짝을 확인) PHP 4.3 이전 방식이다. `cgi.discard_path`가 꺼져 있고 `PATH_TRANSLATED`가 있으면 **`PATH_TRANSLATED`가 실행할 파일이 된다** (raw/php-src-cgi_main.c:1424-1434). 주석은 이 방식을 쓰지 말아야 하지만 호환성을 위해 둔다고 한다 (raw/php-src-cgi_main.c:1425).

### CGI 모드와 `REDIRECT_STATUS`

- `SERVER_SOFTWARE`, `SERVER_NAME`, `GATEWAY_INTERFACE`, `REQUEST_METHOD` 중 하나라도 환경에 있으면 CGI로 실행된 것으로 본다 (raw/php-src-cgi_main.c:1787-1795).
- CGI 모드이고 `cgi.force_redirect`가 켜져 있으면, `cgi.redirect_status_env`에 지정한 변수(지정이 없으면 `REDIRECT_STATUS`)가 환경에 있는지 본다 (raw/php-src-cgi_main.c:1886-1898).
  - 검사는 `getenv`가 NULL인지뿐이다 (raw/php-src-cgi_main.c:1898). 값은 보지 않는다. [[sources/php-cgi-force-redirect]]에도 값의 조건은 없었다.
  - 변수가 없으면 응답 코드를 400으로 정하고 "Security Alert!" 안내문을 출력한 뒤 실패로 끝난다 (raw/php-src-cgi_main.c:1898-1901, raw/php-src-cgi_main.c:1921-1922).
- `HTTP_REDIRECT_STATUS`는 이 코드에서 검사하지 않는다. 주석은 환경 변수를 신뢰할 수 없는 쪽이 설정할 수 있는 경우에 대비해 `cgi.redirect_status_env` 설정을 먼저 본다고 한다 (raw/php-src-cgi_main.c:1888-1891).
  - **판단:** `HTTP_`로 시작하는 변수는 클라이언트 요청 헤더에서 만들어지므로 (raw/rfc3875.txt:1038-1042), 클라이언트가 `Redirect-Status` 헤더를 보내면 이 검사를 통과할 수 있었다. 그래서 빠진 것으로 본다. 변경 이유를 적은 공식 문서는 받지 않았다.

### 스크립트를 열지 못할 때

- CGI 모드에서 스크립트를 열지 못하면, `errno`가 `EACCES`일 때 응답 코드 403과 "Access denied."를, 그 밖에는 404와 "No input file specified."를 출력한다 (raw/php-src-cgi_main.c:2469-2478).

## 과제 적용 (판단)

- 서버는 실행할 스크립트의 절대 경로를 `SCRIPT_FILENAME`으로 넘긴다. php-cgi는 이 값을 `PATH_TRANSLATED`보다 먼저 쓴다.
- 서버는 `REDIRECT_URL`을 넘기지 않는다. 넘기면 `PATH_TRANSLATED` 쪽 파일이 실행될 수 있다.
- `PATH_TRANSLATED`는 RFC 3875대로 `PATH_INFO`가 있을 때만 넣는다 (raw/rfc3875.txt:803-805 → [[concepts/cgi]]). 평가 PC의 php.ini가 `cgi.fix_pathinfo=0`이면 `PATH_TRANSLATED`가 실행할 파일이 되므로, `/t.php/x/y` 요청에서 `/x/y`에 해당하는 파일을 PHP로 실행하려 할 수 있다. 평가 PC 설정은 **미확인**이다 (평가 때 `php-cgi -i`).
- `REDIRECT_STATUS`에는 어떤 값이든 넣으면 된다. 흔한 값 `200`을 쓴다.
