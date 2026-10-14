---
title: NGINX ngx_http_autoindex_module
type: source
sources: [raw/nginx-autoindex-module.md]
updated: 2026-10-15
---

# NGINX ngx_http_autoindex_module

원본: `raw/nginx-autoindex-module.md`. <https://nginx.org/en/docs/http/ngx_http_autoindex_module.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/nginx-autoindex-module.md:1-4). 원본 HTML은 `raw/nginx-autoindex-module.source.html`.

> [!note] 변환 검증
> `tools/nginx2md.py`로 변환하고 `tools/verify_md.py`로 검증했다. 1,318자, 단어 214개가 모두 같았다 (PASS).

## 핵심

| 내용 | 근거 |
|---|---|
| `/`로 끝나는 요청을 처리해 디렉토리 리스팅을 만든다. 보통 index 모듈이 index 파일을 찾지 못했을 때 요청이 넘어온다 | raw/nginx-autoindex-module.md:12 |
| `autoindex` 기본값 `off` | raw/nginx-autoindex-module.md:30-40 |
| 출력 형식 html·xml·json·jsonp, 기본 html | raw/nginx-autoindex-module.md:58-70 |
| HTML 리스팅에 파일 크기(정확한 값 또는 KB·MB·GB 반올림)와 시간(로컬 또는 UTC)이 나온다 | raw/nginx-autoindex-module.md:54, raw/nginx-autoindex-module.md:88 |

## 이 문서로 확인하지 못한 것

- autoindex가 꺼져 있고 index 파일도 없을 때의 응답 코드. 과제에서 403으로 판단 → [[concepts/configuration-file]].
- 끝에 `/`가 없는 디렉토리 요청의 처리 (이 모듈도 `/`로 끝나는 요청만 다룬다, raw/nginx-autoindex-module.md:12).
