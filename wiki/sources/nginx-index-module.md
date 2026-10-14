---
title: NGINX ngx_http_index_module
type: source
sources: [raw/nginx-index-module.md]
updated: 2026-10-15
---

# NGINX ngx_http_index_module

원본: `raw/nginx-index-module.md`. <https://nginx.org/en/docs/http/ngx_http_index_module.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/nginx-index-module.md:1-4). 원본 HTML은 `raw/nginx-index-module.source.html`.

> [!note] 변환 검증
> `tools/nginx2md.py`로 변환하고 `tools/verify_md.py`로 검증했다. 851자, 단어 145개가 모두 같았다 (PASS).

## 핵심

| 내용 | 근거 |
|---|---|
| `/`로 끝나는 요청을 처리한다. 같은 요청을 autoindex 모듈도 처리할 수 있다 | raw/nginx-index-module.md:12 |
| 기본값 `index index.html` | raw/nginx-index-module.md:34-35 |
| 파일을 여러 개 지정할 수 있고 적은 순서대로 확인한다. 마지막 항목은 절대 경로일 수 있다 | raw/nginx-index-module.md:40 |
| index 파일을 쓰면 **내부 리다이렉트**가 일어나 다른 location에서 처리될 수 있다 | raw/nginx-index-module.md:46-58 |

## 이 문서로 확인하지 못한 것

- 끝에 `/`가 없는 디렉토리 요청의 처리 (이 모듈은 `/`로 끝나는 요청만 다룬다, raw/nginx-index-module.md:12).
- index 파일을 하나도 찾지 못했을 때의 응답 (autoindex로 넘어가는지, 403인지) → [[source-wishlist]] (autoindex 모듈, NGINX 실측).
