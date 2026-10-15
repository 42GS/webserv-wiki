---
title: NGINX 실측 — 경로의 `%2F`(인코딩된 `/`)
type: source
sources: [raw/nginx-observed-encoded-slash.md, raw/nginx-core-module.md, raw/rfc3986.txt, raw/rfc3875.txt]
updated: 2026-10-15
---

# NGINX 실측 — 경로의 `%2F`

원본: `raw/nginx-observed-encoded-slash.md`. NGINX 공식 Docker 이미지(nginx/1.30.6)를 띄우고 같은 Docker 네트워크의 curl 컨테이너에서 요청한 응답과 NGINX 로그를 그대로 담았다 (2026-10-15, raw/nginx-observed-encoded-slash.md:3-4, raw/nginx-observed-encoded-slash.md:13-18). 이미지는 [[sources/nginx-observed-directory]] 측정과 같은 digest다.
NGINX 문서는 location 매칭 전 정규화가 `%XX` 디코딩, `.`·`..` 해석, 연속 `/` 합치기를 거친다고만 하고 순서와 `%2F` 처리는 적지 않는다 (raw/nginx-core-module.md:1063). 그래서 측정했다.

## 결과

| 요청 | 응답 | 근거 |
|---|---|---|
| `/a/b.txt` (비교 기준) | 200, `location /a/`(`X-Loc: a`), 파일 `a/b.txt` | raw/nginx-observed-encoded-slash.md:85-96 |
| `/a%2Fb.txt` | 위와 같음: `location /a/`에 매칭되고 `a/b.txt`를 보냄 | raw/nginx-observed-encoded-slash.md:100-111 |
| `/a%2fb.txt` (소문자) | 위와 같음. curl이 `%2F`로 바꿔 보냈다 (로그) | raw/nginx-observed-encoded-slash.md:115-126, raw/nginx-observed-encoded-slash.md:198 |
| `/echo/x%2Fy` | `$uri=/echo/x/y` | raw/nginx-observed-encoded-slash.md:137 |
| `/echo/a%2F..%2Fb` | `$uri=/echo/b`. `/echo/a/../b`와 같다 | raw/nginx-observed-encoded-slash.md:148, raw/nginx-observed-encoded-slash.md:159 |
| `/echo/a%2F%2Fb` | `$uri=/echo/a/b` | raw/nginx-observed-encoded-slash.md:170 |
| `/a%2F..%2F..%2Fetc%2Fpasswd` | 400, `Connection: close` | raw/nginx-observed-encoded-slash.md:174-179 |

- NGINX는 `%2F`를 디코딩해 **경로 구분자로 쓴다**. 파일 매핑, location 매칭, `$uri` 모두 그렇다.
- 디코딩으로 생긴 `/`·`..`도 dot-segment 처리와 연속 `/` 합치기의 대상이 된다. 즉 **디코딩을 먼저 하고 정규화한다** (위 결과에서 끌어낸 정리, **판단**).
- 디코딩된 `..`가 root 위로 올라가면 인코딩되지 않은 `..`처럼 400으로 거부하고 연결을 닫는다 ([[sources/nginx-observed-directory]]와 같음).

## 과제 적용

- RFC 3986은 component를 나눈 뒤 디코딩하라고 한다 (raw/rfc3986.txt:754-758). NGINX는 이 순서가 아니다.
- 이 과제는 디코딩 결과에 `/`가 생기는 세그먼트를 **400으로 거부한다** (사용자 결정, 2026-10-15). RFC 3875도 인코딩된 `/`가 `PATH_INFO`로 디코딩되는 요청을 거부할 수 있다고 한다 (raw/rfc3875.txt:736-741). NGINX와 동작이 다르므로 디펜스에서 이유를 설명한다 → [[concepts/security]] 경로 정규화 절차 5단계.

> [!note] 측정 범위
> 기본 설정(`merge_slashes`는 기본값 `on`, raw/nginx-core-module.md:1190)의 NGINX 한 버전에서 측정했다. `merge_slashes off`, `alias`, 정규식 location에서의 동작은 측정하지 않았다.
