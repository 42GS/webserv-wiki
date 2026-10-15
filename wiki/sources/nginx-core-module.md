---
title: NGINX ngx_http_core_module
type: source
sources: [raw/nginx-core-module.md, raw/subject.md, raw/nginx-observed-directory.md]
updated: 2026-10-15
---

# NGINX ngx_http_core_module

원본: `raw/nginx-core-module.md`. <https://nginx.org/en/docs/http/ngx_http_core_module.html>을 2026-10-15에 받아 `div#content`의 텍스트를 markdown으로 옮겼다 (raw/nginx-core-module.md:1-4). 원본 HTML은 `raw/nginx-core-module.source.html`.
subject는 동작이 궁금하면 NGINX와 비교하라고 하고 (raw/subject.md:186), 설정 파일은 NGINX `server` 섹션을 참고하라고 한다 (raw/subject.md:161). 이 문서는 그 비교 기준이다.

> [!note] 변환 검증
> 변환 스크립트와 별개의 방법(정규식으로 태그 제거)으로 HTML 텍스트를 뽑아 비교했다. 공백을 뺀 문자열 55,481자가 같았다. 단어 단위 차이 153건은 모두 HTML 태그 경계에서 단어가 갈라진 것이었다.
> 문서는 계속 갱신되는 웹 페이지라 받은 날짜 기준이다. 버전 번호가 붙은 문장(예: 1.31.5)이 있다 (raw/nginx-core-module.md:1061).
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: note 상자 표시 없음, `<strong>` 강조 없음, server_name 검색 우선순위 번호 목록(raw/nginx-core-module.md:1734-1740)이 글머리표로 바뀜(순서는 유지), 문단·note가 든 정의 항목(listen 매개변수, 일부 변수)의 글머리표 없음, `$proxy_protocol_tlv_` 안 하위 목록이 변수 목록과 같은 단계로 보임.

## 과제와 관련된 디렉티브

| 묶음 | 디렉티브 (시작 줄) | 위키 페이지 |
|---|---|---|
| 경로 매핑 | `root` (1492), `alias` (124), `location` (1053) | [[concepts/configuration-file]] |
| 서버 선택 | `listen` (924), `server` (1620), `server_name` (1630) | [[concepts/configuration-file]] |
| 에러·body | `error_page` (525), `client_max_body_size` (349) | [[concepts/configuration-file]], [[concepts/status-codes]] |
| 메서드 | `limit_except` (787) | [[concepts/configuration-file]] |
| 타임아웃 | `client_header_timeout` (335), `client_body_timeout` (305), `send_timeout` (1562), `keepalive_timeout` (753) | [[concepts/connection-management]] |
| 헤더 크기 | `client_header_buffer_size` (319), `large_client_header_buffers` (769) | [[concepts/status-codes]] |
| 연결 종료 | `lingering_close` (872), `lingering_time` (896), `lingering_timeout` (910), `reset_timedout_connection` (1418) | [[concepts/connection-management]] |
| 기타 | `merge_slashes` (1183), `types` (1987), `default_type` (379), `absolute_redirect` (14), `port_in_redirect` (1342), `server_name_in_redirect` (1744) | [[concepts/configuration-file]], [[concepts/security]] |

다루지 않는 디렉티브: aio·sendfile·directio 등 성능 튜닝, open_file_cache, resolver, HTTP/2·QUIC, 인증·접근 제어.

## 핵심

- `root`는 URI 전체를 붙이고, `alias`는 location 부분을 바꿔 끼운다 (raw/nginx-core-module.md:1516, raw/nginx-core-module.md:132-140). subject 예시는 `alias` 방식이다.
- location은 정규화된 URI로 매칭하고, prefix 중 가장 긴 것을 고른다 (raw/nginx-core-module.md:1063, raw/nginx-core-module.md:1067).
- `default_server`가 없으면 그 `address:port`의 첫 server가 기본이다 (raw/nginx-core-module.md:963).

## 이 문서로 확인하지 못한 것

- 끝에 `/`가 없는 정적 디렉토리 요청의 301: 이 문서의 301은 `proxy_pass` 등을 쓸 때만 나온다 (raw/nginx-core-module.md:1115). 정적 파일 모듈 문서는 nginx.org에 없다. 과제는 판단으로 301 확정 → [[concepts/configuration-file]]. NGINX 실측에서는 정적 디렉토리에도 301이었다 (raw/nginx-observed-directory.md:77-83) → [[sources/nginx-observed-directory]].
- `limit_except`로 막힌 메서드의 응답 코드: access 모듈 지시자에 맡긴다고만 되어 있다 (raw/nginx-core-module.md:795). access 모듈 문서에도 코드가 없다. 과제는 RFC 기준 405로 확정 → [[concepts/configuration-file]].
