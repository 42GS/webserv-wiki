---
title: NGINX — How nginx processes a request
type: source
sources: [raw/nginx-request-processing.md]
updated: 2026-10-15
---

# NGINX — How nginx processes a request

원본: `raw/nginx-request-processing.md`. <https://nginx.org/en/docs/http/request_processing.html>을 2026-10-15에 받아 markdown으로 옮겼다 (raw/nginx-request-processing.md:1-4). 원본 HTML은 `raw/nginx-request-processing.source.html`.
NGINX가 요청을 받을 때 어느 server, 어느 location이 처리할지 고르는 과정을 예시로 설명한다.

> [!note] 변환 검증
> [[sources/nginx-core-module]]과 같은 방법으로 검증했다. 공백을 뺀 문자열 5,515자가 같았고, 단어 단위 차이 3건은 모두 태그 경계에서 단어가 갈라진 것이었다.
> 2026-10-15 원본 HTML 본문 전체를 변환본과 직접 읽어 대조했다: 글자가 빠지거나 바뀐 곳 없음. 구조 차이: 코드 안 `<b>` 강조와 note 상자 표시가 없음.

## 절 구성

모든 절이 과제와 관련 있어 전부 다룬다.

| 절 (시작 줄) | 내용 | 위키 페이지 |
|---|---|---|
| Name-based virtual servers (10) | Host로 server 선택, default server | [[concepts/configuration-file]] |
| How to prevent processing requests with undefined server names (50) | Host 없는 요청 | [[concepts/request-parsing]] |
| Mixed name-based and IP-based virtual servers (68) | `address:port` → Host 순서의 선택 | [[concepts/configuration-file]] |
| A simple PHP site configuration (118) | location 매칭과 query, index 내부 리다이렉트 | [[concepts/configuration-file]] |

## 핵심

- Host가 어느 server 이름과도 맞지 않거나 Host가 없으면 그 포트의 default server가 처리한다. 지정하지 않으면 첫 server가 default다 (raw/nginx-request-processing.md:34).
- 먼저 IP·포트로 server 후보를 고르고, 그 후보 안에서만 Host를 비교한다 (raw/nginx-request-processing.md:92).
- default server는 server 이름이 아니라 listen 포트의 속성이다 (raw/nginx-request-processing.md:46, raw/nginx-request-processing.md:94).
- location은 query string을 뺀 URI 부분으로만 매칭한다 (raw/nginx-request-processing.md:147).
- index 지시자는 찾은 index 파일로 내부 리다이렉트하고 location을 다시 찾는다 (raw/nginx-request-processing.md:168).
- 444는 NGINX 비표준 코드로, 응답 없이 연결을 닫는다 (raw/nginx-request-processing.md:62). 과제에서는 쓰지 않는다.
