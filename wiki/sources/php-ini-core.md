---
title: PHP 매뉴얼 — core php.ini 지시자 (CGI 관련)
type: source
sources: [raw/php-ini-core.md]
updated: 2026-10-15
---

# PHP 매뉴얼 — Description of core php.ini directives

원본: `raw/php-ini-core.md`. <https://www.php.net/manual/en/ini.core.php>를 2026-10-15에 받아 markdown으로 옮겼다 (raw/php-ini-core.md:1-4). 원본 HTML은 `raw/php-ini-core.source.html`.

> [!note] 변환 검증
> `tools/extract_div.py`로 본문 div(`ini.core`)만 잘라 변환했다. 20,984자, 단어 3,693개가 같았다 (PASS).
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: 표 행이 한 줄로 평탄화됨, 강조 없음.

## 다루는 범위

페이지 전체가 PHP 핵심 설정 목록이다. 이 위키는 **CGI 관련 설정만** 다룬다.

| 설정 | 기본값 | 의미 | 근거 |
|---|---|---|---|
| `cgi.force_redirect` | `"1"` | 대부분의 웹 서버에서 CGI로 실행할 때 보안에 필요. 정의하지 않으면 PHP가 켠다. IIS 등에서는 꺼야 한다 | raw/php-ini-core.md:428, raw/php-ini-core.md:546-552 |
| `cgi.redirect_status_env` | NULL | `force_redirect`가 켜져 있고 Apache·Netscape가 아니면, PHP가 실행해도 된다고 판단할 환경 변수 이름을 지정해야 할 수 있다. 보안 문제가 생길 수 있다는 주의 | raw/php-ini-core.md:432, raw/php-ini-core.md:558-564 |
| `cgi.fix_pathinfo` | `"1"` | 실제 `PATH_INFO`/`PATH_TRANSLATED` 지원. 스크립트는 `PATH_TRANSLATED` 대신 `SCRIPT_FILENAME`을 쓰라고 권함 | raw/php-ini-core.md:426, raw/php-ini-core.md:542-544 |
| `cgi.rfc2616_headers` | `"0"` | 0이면 응답 코드를 RFC 3875 `Status:` 헤더로 보냄 | raw/php-ini-core.md:434, raw/php-ini-core.md:566-568 |
| `cgi.nph` | `"0"` | 켜면 항상 `Status: 200`을 보냄 | raw/php-ini-core.md:430, raw/php-ini-core.md:554-556 |
| `doc_root` | NULL | `FORCE_REDIRECT` 없이 컴파일된 PHP를 CGI로 쓸 때 설정 권장. 대안이 `cgi.force_redirect` | raw/php-ini-core.md:408, raw/php-ini-core.md:510-512 |

- 기본값은 PHP 기본 설정 기준이다. Ubuntu 22.04 apt 패키지(php8.1-cgi)의 `php.ini`에서도 `cgi.force_redirect`·`cgi.fix_pathinfo`가 1, `cgi.discard_path`가 0이었다 → [[sources/ubuntu2204-observed-tools]]. 평가 PC의 실제 `php.ini` 값은 **미확인**이다 (`php-cgi -i` 등으로 확인).
