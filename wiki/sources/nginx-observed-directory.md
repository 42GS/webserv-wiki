---
title: NGINX 실측 — 디렉토리 요청과 `..` 경로
type: source
sources: [raw/nginx-observed-directory.md, raw/rfc9110.txt, raw/subject.md]
updated: 2026-10-15
---

# NGINX 실측 — 디렉토리 요청과 `..` 경로

원본: `raw/nginx-observed-directory.md`. NGINX 공식 Docker 이미지(nginx/1.30.6)를 `autoindex off` 설정으로 띄우고, 같은 Docker 네트워크의 curl 컨테이너에서 요청한 응답과 NGINX 로그를 그대로 담았다 (2026-10-15, raw/nginx-observed-directory.md:3, raw/nginx-observed-directory.md:12-33).
문서로 확인할 수 없던 디렉토리 요청의 응답 코드를 확인하려고 측정했다. subject는 특정 동작이 궁금하면 NGINX와 비교해 볼 수 있다고 한다 (raw/subject.md:186).

## 결과

| 요청 | 응답 | 근거 |
|---|---|---|
| `/withindex` (끝 `/` 없음, index 있음) | 301, `Location: http://web/withindex/` | raw/nginx-observed-directory.md:78-83 |
| `/withindex/` | 200, index 파일 내용 | raw/nginx-observed-directory.md:96, raw/nginx-observed-directory.md:106 |
| `/noindex` (끝 `/` 없음, index 없음) | 301, `Location: http://web/noindex/` | raw/nginx-observed-directory.md:110-115 |
| `/noindex/` (`autoindex off`, index 없음) | 403. 로그: "directory index ... is forbidden" | raw/nginx-observed-directory.md:128, raw/nginx-observed-directory.md:234 |
| `/missing` | 404 | raw/nginx-observed-directory.md:210 |
| `/../etc/passwd` | 400, `Connection: close` | raw/nginx-observed-directory.md:159-164 |
| `/%2e%2e/etc/passwd` (curl이 `%2E%2E`로 보냄) | 400, `Connection: close` | raw/nginx-observed-directory.md:176-181, raw/nginx-observed-directory.md:237 |
| `/noindex/../../etc/passwd` | 400, `Connection: close` | raw/nginx-observed-directory.md:193-198 |

- 디렉토리의 301은 index 파일 유무와 관계없이 보낸다.
- `Location`은 scheme과 host를 포함한 절대 URL이다. 요청의 Host가 `web`이었다 (raw/nginx-observed-directory.md:234).
- root 위로 올라가는 `..`는 인코딩 여부와 관계없이 400이고 연결을 닫는다. 디렉토리 중간에서 올라가도 루트를 넘으면 같다.

## 과제 적용

- 끝에 `/`가 없는 디렉토리 → 301, 리스팅 off + index 없음 → 403: 판단으로 정해 둔 것과 같다 → [[concepts/configuration-file]].
- `Location`: 이 과제는 경로만 보낸다(`/noindex/`). RFC 9110은 상대 참조를 허용한다 (raw/rfc9110.txt:4743-4745). NGINX와 형식만 다르다 (**판단**).
- root 위로 올라가는 `..` → **400 + 연결 닫기** (사용자 결정, 2026-10-15) → [[concepts/security]], [[concepts/status-codes]].

> [!note] 측정 범위
> 기본 설정의 NGINX 한 버전에서 측정했다. `merge_slashes`·심볼릭 링크 등 다른 경우는 측정하지 않았다.
