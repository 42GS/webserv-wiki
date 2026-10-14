---
title: 파일 업로드
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc7578.txt, raw/rfc9110.txt, raw/rfc9112.txt]
updated: 2026-10-15
---

# 파일 업로드

## 요구사항

| 요구 | 근거 |
|---|---|
| 클라이언트가 파일을 업로드할 수 있어야 함 | raw/subject.md:146 |
| 라우트별로 업로드를 허용하고 저장 위치를 지정 | raw/subject.md:172 |
| 평가: 파일 몇 개를 업로드하고 다시 받아 봄 | raw/evaluation-sheet-en.md:82 |
| 평가: body 크기 제한 테스트 | raw/evaluation-sheet-en.md:70 |

subject는 업로드 형식을 정하지 않는다. 브라우저의 폼 파일 업로드는 `multipart/form-data`를 쓴다. 이 형식은 HTML 폼에서 나왔고 대부분의 브라우저와 서버가 구현한다 (raw/rfc7578.txt:105-110). 평가에서 브라우저로 업로드할 수 있으므로 multipart 처리가 사실상 필요하다 (**판단**).

## multipart/form-data 구조

```
Content-Type: multipart/form-data; boundary=AaB03x      ← 요청 헤더

--AaB03x
Content-Disposition: form-data; name="file"; filename="a.txt"
Content-Type: text/plain

(파일 내용)
--AaB03x--
```

위 예시는 RFC 7578의 예시 형식(raw/rfc7578.txt:287-293)을 바탕으로 이해를 돕기 위해 만든 것이다. 마지막 구분자 `--AaB03x--`의 정확한 문법은 RFC 2046 5.1절 소관이다 (**미확인**, [[source-wishlist]]).

| 규칙 | 근거 |
|---|---|
| 본문은 boundary로 나뉜 part들의 연속 | raw/rfc7578.txt:181-182 |
| 구분자는 CRLF + `--` + boundary 값. boundary 값은 `Content-Type`의 `boundary` 파라미터로 주어지며 따옴표로 감싸일 수 있음 | raw/rfc7578.txt:186-193 |
| boundary 구분자는 part 내용 안에 나오면 안 됨 (MUST NOT) | raw/rfc7578.txt:190-191 |
| 각 part는 `Content-Disposition: form-data; name="..."`를 가져야 함 (MUST) | raw/rfc7578.txt:197-200 |
| 파일이면 `filename` 파라미터를 붙여야 함 (SHOULD). 없을 수도 있음 | raw/rfc7578.txt:207-213 |
| `filename*` 형식(RFC 5987)은 쓰면 안 됨 (MUST NOT) | raw/rfc7578.txt:237-239 |
| 한 필드의 여러 파일은 같은 `name`을 가진 별도 part로 보냄 (MUST) | raw/rfc7578.txt:254-256 |
| part의 `Content-Type`은 선택이고 기본은 `text/plain`. 파일은 알맞은 타입, 모르면 `application/octet-stream` | raw/rfc7578.txt:264-267 |
| `Content-Transfer-Encoding`은 보내지 말 것 (SHOULD NOT) | raw/rfc7578.txt:328-329 |
| `Content-Type`·`Content-Disposition`·(제한적으로)`Content-Transfer-Encoding` 외 헤더는 무시 (MUST) | raw/rfc7578.txt:345-348 |

## 서버가 처리하는 순서 (판단)

1. 요청 본문을 끝까지 받는다. chunked면 먼저 디코딩한다 → [[concepts/request-parsing]] 4·5절. body 크기 제한을 넘으면 413 (raw/rfc9110.txt:7710-7714).
2. 요청 `Content-Type`이 `multipart/form-data`인지, `boundary` 파라미터가 있는지 확인한다. 없거나 형식이 틀리면 400 (raw/rfc9110.txt:7543-7546).
3. 구분자로 part를 나눈다. part 내용은 바이너리일 수 있으므로 문자열이 아니라 바이트로 다룬다. 요청 메시지 자체도 octet 열로 파싱해야 한다 (raw/rfc9112.txt:272-277).
4. 각 part의 헤더에서 `name`, `filename`을 읽는다. 파일이 아닌 필드(`filename` 없음)는 저장하지 않거나 무시한다.
5. `filename`을 안전한 이름으로 바꾼다 (아래 절).
6. 설정의 저장 위치에 쓴다. 디스크 파일 쓰기는 `poll()` 대상이 아니다 (raw/subject.md:134).
7. 새 파일을 만들었으면 201 + `Location` (SHOULD, raw/rfc9110.txt:4050-4053) → [[concepts/status-codes]].

## filename 처리

- 파일 이름을 그대로 쓰지 말고, 로컬 파일 시스템 규칙에 맞게 확인·변경하며, 들어 있는 디렉토리 경로 정보는 쓰지 말라고 한다 (raw/rfc7578.txt:215-220).
- 받는 쪽의 기존 파일을 실수로 덮어쓰지 않게 주의하라고 한다 (raw/rfc7578.txt:497-499).
- 과제 적용 (**판단**):
  - `/`와 `..`를 포함한 경로 부분을 버리고 마지막 이름만 쓴다. 빈 이름, `.`, `..`는 거부하거나 서버가 이름을 만든다 → [[concepts/security]] 1절.
  - 같은 이름의 파일이 있으면 덮어쓸지, 다른 이름으로 저장할지, 409로 거부할지 정한다. 409는 대상 리소스의 현재 상태와 충돌할 때의 코드다 (raw/rfc9110.txt:7652-7655).

## 업로드 위치와 CGI

- multipart로 받은 파일에는 실행 가능한 내용이 들어 있을 수 있어 대비가 필요하다 (raw/rfc7578.txt:529-530).
- 업로드 위치가 CGI 확장자 규칙이 적용되는 경로와 겹치면, `.php` 같은 파일을 올린 뒤 GET으로 요청해 서버에서 실행시킬 수 있다. 업로드 위치에서는 CGI를 실행하지 않도록 설정한다 (**판단**) → [[concepts/cgi]], [[concepts/security]].

## 열린 설계 질문

- multipart를 서버가 직접 파싱해 저장할지, CGI 스크립트에 넘길지는 과제 문서가 정하지 않는다. "업로드를 허용하고 저장 위치를 지정"하는 설정 요구(raw/subject.md:172)로 보면 서버가 직접 저장하는 쪽에 가깝다 (**판단**).
- multipart가 아닌 본문(예: `curl --data-binary`로 보낸 원본 바이트)을 받을지. 그때 파일 이름을 어디서 정할지 (예: 요청 경로).
- 업로드한 파일을 다시 받는 경로. 평가는 업로드 후 다시 받아 본다 (raw/evaluation-sheet-en.md:82). 저장 위치가 GET으로 접근 가능한 root 아래인지 설정을 맞춰 둔다.

## 관련

- [[concepts/configuration-file]], [[concepts/http-features]], [[concepts/status-codes]], [[concepts/security]], [[concepts/request-parsing]], [[sources/rfc7578]]
