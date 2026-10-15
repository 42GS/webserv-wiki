---
title: PHP 매뉴얼 — Case 2: using cgi.force_redirect
type: source
sources: [raw/php-cgi-force-redirect.md]
updated: 2026-10-15
---

# PHP 매뉴얼 — Case 2: using cgi.force_redirect

원본: `raw/php-cgi-force-redirect.md`. <https://www.php.net/manual/en/security.cgi-bin.force-redirect.php>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/php-cgi-force-redirect.md:1-4). 원본 HTML은 `raw/php-cgi-force-redirect.source.html`.
PHP 매뉴얼 "Installed as CGI binary" 장의 한 절이다 (원본 HTML의 탐색 메뉴, 변환 범위 밖). 같은 장의 다른 절(공격 유형, 공개 파일만 두기, doc_root, 웹 트리 밖에 두기)은 받지 않았다.

> [!note] 변환 검증
> `tools/extract_div.py`로 본문 div(`security.cgi-bin.force-redirect`)만 잘라 `tools/nginx2md.py`로 변환하고 `tools/verify_md.py`로 검증했다. 684자, 단어 121개가 같았다 (PASS). 페이지 아래의 사용자 댓글은 공식 자료가 아니라서 제외했다.
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이 없음.

## 핵심

- `cgi.force_redirect`가 켜져 있으면 PHP는 웹 서버의 리다이렉트 규칙을 거친 요청만 처리한다. URL로 php를 직접 호출하는 것을 막기 위한 설정이다 (raw/php-cgi-force-redirect.md:8).
- 이 옵션은 Apache에서만 시험됐고, Apache가 리다이렉트된 요청에 설정하는 **비표준 CGI 환경 변수 `REDIRECT_STATUS`**에 의존한다 (raw/php-cgi-force-redirect.md:17).
- 웹 서버가 직접 요청과 리다이렉트된 요청을 구분할 방법을 주지 못하면 이 설정을 쓸 수 없다 (raw/php-cgi-force-redirect.md:17).
- 기본값은 [[sources/php-ini-core]].

## 이 문서로 확인하지 못한 것

- `REDIRECT_STATUS`에 어떤 값을 넣어야 하는지. 소스로 확인했다: 값은 보지 않고 변수가 있는지만 본다 → [[sources/php-src-cgi-main]].
