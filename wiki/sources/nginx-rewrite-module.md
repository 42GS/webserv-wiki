---
title: NGINX ngx_http_rewrite_module
type: source
sources: [raw/nginx-rewrite-module.md, raw/subject.md]
updated: 2026-10-15
---

# NGINX ngx_http_rewrite_module

원본: `raw/nginx-rewrite-module.md`. <https://nginx.org/en/docs/http/ngx_http_rewrite_module.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/nginx-rewrite-module.md:1-4). 원본 HTML은 `raw/nginx-rewrite-module.source.html`.

> [!note] 변환 검증
> `tools/nginx2md.py`로 변환하고 `tools/verify_md.py`로 검증했다. 6,750자, 단어 1,178개가 모두 같았다 (PASS).
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: "repeatedly:" 아래 하위 목록(raw/nginx-rewrite-module.md:16-24)의 상하위 구분이 없음, note가 든 목록 항목(63행) 글머리표 없음.

## 과제와 관련된 부분

| 부분 (시작 줄) | 내용 | 위키 페이지 |
|---|---|---|
| 개요·처리 순서 (10) | URI가 다시 쓰이면 location 검색을 반복하되 10번을 넘지 않음 | [[concepts/resilience]] |
| `return` (105) | 코드와 리다이렉트 URL 또는 본문 텍스트를 돌려주고 처리를 멈춤 | [[concepts/configuration-file]] |
| `rewrite` (127) | 정규식으로 URI를 바꿈. 반복이 10번을 넘으면 500 | [[concepts/resilience]] |

다루지 않는 부분: `if`, `set`, `break`, `rewrite_log`, 변수, 내부 구현. `rewrite`는 PCRE 정규식을 쓰는데 (raw/nginx-rewrite-module.md:12) subject는 정규식이 필요 없다고 하므로 (raw/subject.md:166) 기능 자체는 과제 범위 밖이다.

## 핵심

- `return code URL`: URL을 쓸 수 있는 코드는 301·302·303·307·308. 다른 코드는 본문 텍스트를 줄 수 있다 (raw/nginx-rewrite-module.md:115).
- `return URL`만 쓰면 302 (raw/nginx-rewrite-module.md:117).
- 로컬 URI를 주면 scheme, server_name, port로 완전한 URL을 만든다 (raw/nginx-rewrite-module.md:115).
- 444는 응답 헤더 없이 연결을 닫는 비표준 코드 (raw/nginx-rewrite-module.md:113).
