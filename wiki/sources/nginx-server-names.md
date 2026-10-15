---
title: NGINX Server names
type: source
sources: [raw/nginx-server-names.md, raw/subject.md, raw/evaluation-sheet-en.md, raw/nginx-request-processing.md, raw/rfc9110.txt]
updated: 2026-10-15
---

# NGINX Server names

원본: `raw/nginx-server-names.md`. <https://nginx.org/en/docs/http/server_names.html>을 2026-10-15에 받아 `div#content`의 텍스트를 markdown으로 옮겼다 (raw/nginx-server-names.md:1-4). 원본 HTML은 `raw/nginx-server-names.source.html`.
`server_name`으로 요청을 처리할 server를 고르는 규칙을 다룬다 (raw/nginx-server-names.md:10). virtual host는 선택 사항이므로 (raw/evaluation-sheet-en.md:108) 구현할 때의 기준으로 쓴다.

> [!note] 변환 검증
> `tools/nginx2md.py`로 변환하고 `tools/verify_md.py` PASS (공백을 뺀 9,111자 일치, 단어 1,656개 일치).

## 과제와 관련된 절

| 절 (시작 줄) | 내용 | 위키 페이지 |
|---|---|---|
| 개요 (10) | 매칭 우선순위 | [[concepts/configuration-file]] |
| Wildcard names (50) | `*`의 위치 규칙 | [[concepts/configuration-file]] |
| Miscellaneous names (106) | 빈 이름, IP 주소 Host, `_`, default server | [[concepts/configuration-file]] |
| Virtual server selection (186) | server가 정해지는 시점, 시점별로 적용되는 설정 | [[concepts/configuration-file]] |
| Optimization (212) | 포트에 server가 하나면 이름을 검사하지 않음 (267) | [[concepts/configuration-file]] |

다루지 않는 절: 정규식 이름(subject는 route 규칙에 정규식이 필요 없다고 하고(raw/subject.md:166), 서버 이름에도 필요 없다고 본다 — **판단**), 국제화 도메인, 해시 테이블 튜닝, SSL·SNI, 호환성.

## 핵심

- 매칭 순서: 정확한 이름 → `*`로 시작하는 가장 긴 와일드카드 → `*`로 끝나는 가장 긴 와일드카드 → 처음 맞는 정규식. 처음 맞는 것에서 멈춘다 (raw/nginx-server-names.md:38-46).
- `*`는 이름의 맨 앞이나 맨 끝, 점 경계에만 올 수 있다. `*.example.org`는 `www.sub.example.org`에도 맞는다 (raw/nginx-server-names.md:52).
- 빈 이름 `""`은 Host가 없는 요청에 맞는다. `server_name`이 없으면 빈 이름을 쓴다 (raw/nginx-server-names.md:110-120).
- IP 주소로 요청하면 Host에 IP가 들어오므로 IP를 이름으로 넣어 매칭할 수 있다 (raw/nginx-server-names.md:126).
- `_`는 특별한 이름이 아니다. default server는 `server_name`이 아니라 `listen`의 속성이다 (raw/nginx-server-names.md:150-152, raw/nginx-request-processing.md:46).
- server는 요청줄을 처리한 뒤, Host를 처리한 뒤에 정해진다. 둘 다로 정해지지 않으면 빈 이름을 쓴다 (raw/nginx-server-names.md:188-196).
- 요청줄을 읽기 전에 쓰이는 설정(`client_header_buffer_size`, `merge_slashes`)은 default server 설정을 따른다 (raw/nginx-server-names.md:204).
- 에러 응답은 그 시점에 요청을 맡은 server의 `error_page`로 처리한다 (raw/nginx-server-names.md:208).
- 포트에 server가 하나뿐이면 이름을 검사하지 않는다 (raw/nginx-server-names.md:267).

## 이 문서로 확인하지 못한 것

- 이름 비교의 대소문자 구분: 이 문서에는 없다. RFC 9110은 host가 대소문자를 구분하지 않는다고 한다 (raw/rfc9110.txt:1179-1181).
- Host의 포트를 떼고 비교하는지: 이 문서에는 없다. Host 형식은 `uri-host [ ":" port ]`이다 (raw/rfc9110.txt:2423). 과제는 포트를 떼고 비교 (**판단**).
