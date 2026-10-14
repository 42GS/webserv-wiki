---
title: status code — 상황별 선택
type: concept
sources: [raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc3875.txt, raw/nginx-core-module.md, raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# status code — 상황별 선택

> [!danger] 평가표
> 평가 중 status code가 틀리면 관련 항목 점수를 주지 않는다 (raw/evaluation-sheet-en.md:67). subject도 정확한 status code를 요구한다 (raw/subject.md:142).

과제에서 실제로 마주치는 상황 순서로 정리했다. "근거"는 RFC 9110 정의 문장의 위치다.
RFC가 특정 코드를 직접 지정하지 않는 상황은 **판단**으로 표시했다. 판단 항목은 디펜스에서 이유를 설명할 수 있어야 한다.

## 정상 처리

| 상황 | 코드 | 근거 | 비고 |
|---|---|---|---|
| 정적 파일·index 파일 GET 성공 | 200 | raw/rfc9110.txt:6917 | |
| 디렉토리 리스팅 생성 성공 | 200 | raw/rfc9110.txt:6917 | |
| 업로드로 새 파일 생성 (POST) | 201 | raw/rfc9110.txt:4050-4053, raw/rfc9110.txt:6970-6974 | 만든 리소스를 가리키는 `Location`을 보낸다 (SHOULD) |
| POST 처리 성공, 새 리소스 없음 (예: 폼 처리) | 200 | raw/rfc9110.txt:6917 | |
| CGI document 응답 | CGI `Status` 값, 없으면 200 | raw/rfc3875.txt:1295-1296, raw/rfc3875.txt:1447 | 형식 `Status: 3자리코드 SP reason-phrase` |
| DELETE 성공, 응답 본문 없음 | 204 | raw/rfc9110.txt:4235-4236 | 204에는 `Content-Length`를 보내면 안 됨 (MUST NOT, raw/rfc9110.txt:3238-3239) |
| DELETE 성공, 결과를 본문으로 설명 | 200 | raw/rfc9110.txt:4238-4239 | |

## 리다이렉트 (설정 파일의 redirection)

| 상황 | 코드 | 근거 | 비고 |
|---|---|---|---|
| 영구 이동, 메서드가 바뀌어도 됨 | 301 | raw/rfc9110.txt:7367-7369 | 브라우저가 POST를 GET으로 바꿀 수 있음 (raw/rfc9110.txt:7384-7387) |
| 영구 이동, 메서드 유지 | 308 | raw/rfc9110.txt:7507-7509, raw/rfc9110.txt:7386-7387 | |
| 임시 이동, 메서드가 바뀌어도 됨 | 302 | raw/rfc9110.txt:7395-7398 | |
| 임시 이동, 메서드 유지 | 307 | raw/rfc9110.txt:7492-7494 | 클라이언트는 메서드를 바꾸면 안 됨 (MUST NOT) |
| CGI가 `Location: 절대URI`만 출력 (client redirect) | 302 | raw/rfc3875.txt:1318-1326 | 서버가 302를 생성 (MUST). `Location`이 `/경로`면 local redirect로, 서버가 그 경로를 다시 처리한다 (raw/rfc3875.txt:1303-1314) |
| POST 결과로 다른 리소스를 GET하게 함 | 303 | raw/rfc9110.txt:4065-4068, raw/rfc9110.txt:7413-7416 | |

- 모든 3xx 응답에 `Location`을 보낸다. 301·302·307에서는 SHOULD다 (raw/rfc9110.txt:7378-7379, raw/rfc9110.txt:7400-7401, raw/rfc9110.txt:7499-7500). 303은 정의상 `Location`의 URI를 가리킨다 (raw/rfc9110.txt:7413-7415).
- `Location`은 상대 참조도 된다. 대상 URI 기준으로 해석된다 (raw/rfc9110.txt:4743-4745).
- 끝에 `/`가 없는 디렉토리 요청을 NGINX가 301로 보내는지는 **미확인**이다 (NGINX 문서로 확인, [[source-wishlist]]).

## 클라이언트 오류

| 상황 | 코드 | 근거 | 비고 |
|---|---|---|---|
| 요청줄·헤더 문법 오류, 잘못된 framing | 400 | raw/rfc9110.txt:7543-7546, raw/rfc9112.txt:319-324 | 보낸 뒤 연결을 닫음 (SHOULD) |
| HTTP/1.1 요청에 Host 없음, Host 두 줄 이상, Host 값 오류 | 400 | raw/rfc9112.txt:445-448 | MUST |
| 헤더 이름과 `:` 사이에 공백 | 400 | raw/rfc9112.txt:714-719 | MUST |
| `Content-Length` 값이 잘못됨 (TE 없음) | 400 | raw/rfc9112.txt:956-965 | MUST, 보낸 뒤 연결 닫음 |
| `Transfer-Encoding`의 마지막 coding이 chunked가 아님 | 400 | raw/rfc9112.txt:950-954 | MUST, 보낸 뒤 연결 닫음 |
| 경로에 파일이 없음, 잘못된 URL | 404 | raw/rfc9110.txt:7589-7591 | 평가 "Try an incorrect URL" (raw/evaluation-sheet-en.md:100) |
| 파일은 있지만 접근을 거부 (권한 없음 등) | 403 | raw/rfc9110.txt:7571-7572 | |
| 리스팅 off이고 index 파일도 없는 디렉토리 | 403 | raw/rfc9110.txt:7571-7572 | **판단**. NGINX index·autoindex 모듈 문서에도 이 경우의 코드가 없다 (raw/nginx-index-module.md:12, raw/nginx-autoindex-module.md:12). NGINX 실측으로 확인 → [[source-wishlist]] |
| `..` 등으로 root 밖을 가리키는 경로 | 403 또는 404 | raw/rfc9110.txt:8563-8568 | **판단**. RFC는 접근을 피하라고만 하고 코드는 지정하지 않음. 404는 존재 여부를 숨긴다 (raw/rfc9110.txt:7589-7591) |
| 라우트에서 허용하지 않은 메서드 (알려진 메서드) | 405 | raw/rfc9110.txt:3802-3804, raw/rfc9110.txt:7603-7607 | `Allow` 헤더 MUST. 평가 "DELETE with and without permission" (raw/evaluation-sheet-en.md:73) |
| 클라이언트가 제한 시간 안에 요청을 다 보내지 않음 | 408 | raw/rfc9110.txt:7641-7643 | 닫기 전에 에러 응답을 보낼 수 있음 (MAY, raw/rfc9112.txt:1253-1255) → [[concepts/connection-management]]  NGINX는 헤더 전체 수신 시간, 본문 read 간격 기준으로 408을 보낸다 (raw/nginx-core-module.md:317, raw/nginx-core-module.md:347) |
| chunked 요청을 받지 않기로 한 경우 | 411 | raw/rfc9110.txt:7692-7694, raw/rfc9112.txt:999-1000 | MAY. subject가 un-chunk를 요구하므로(raw/subject.md:179) 이 과제에서는 쓰지 않는다. `Content-Length`도 TE도 없는 요청은 본문 길이 0이다 (raw/rfc9112.txt:980-981) |
| body가 `client_max_body_size` 초과 | 413 | raw/rfc9110.txt:7710-7714 | 평가 body 제한 테스트 (raw/evaluation-sheet-en.md:70). 남은 본문을 읽지 않으면 응답 후 연결을 닫아야 함 (raw/rfc9112.txt:1374-1377) |
| URI가 너무 김 | 414 | raw/rfc9110.txt:7722-7724, raw/rfc9112.txt:393-395 | MUST  NGINX는 요청줄이 헤더 버퍼 하나보다 크면 414 (raw/nginx-core-module.md:781) |
| 헤더 한 줄이 서버 상한보다 큼 | 400 또는 431 | raw/nginx-core-module.md:781 | NGINX는 헤더 한 줄이 버퍼 하나보다 크면 400을 보낸다 (raw/nginx-core-module.md:781). 431은 RFC 6585 정의로, 정확한 정의는 **미확인** (raw/rfc9110.txt:8628-8629) |

## 서버 오류

| 상황 | 코드 | 근거 | 비고 |
|---|---|---|---|
| 모르는 메서드 (평가의 UNKNOWN 요청) | 501 | raw/rfc9110.txt:3800-3801, raw/rfc9110.txt:7871-7874 | 평가 항목은 크래시하지 않는 것 (raw/evaluation-sheet-en.md:80). 구현한 어떤 메서드보다 긴 메서드도 501 (raw/rfc9112.txt:391-393) |
| 모르는 transfer coding | 501 | raw/rfc9112.txt:851-852 | SHOULD |
| 지원하지 않는 HTTP 메이저 버전 | 505 | raw/rfc9110.txt:7908-7911 | |
| 예상하지 못한 내부 오류 (파일 열기 실패, `fork` 실패 등) | 500 | raw/rfc9110.txt:7865-7867 | |
| CGI 출력이 CGI 응답 형식에 맞지 않음, 출력 없이 종료 | 502 | raw/rfc9110.txt:7882-7884, raw/rfc3875.txt:423 | 서버는 CGI에 대해 application gateway다 (raw/rfc3875.txt:423). 스크립트가 규격을 어겨도 서버가 올바른 응답 책임을 진다 (raw/rfc3875.txt:433-437). RFC 3875가 코드를 직접 지정하지는 않음 → [[concepts/cgi]] 5절 |
| CGI가 제한 시간 안에 응답하지 않음 (무한 루프) | 504 | raw/rfc9110.txt:7901-7904, raw/rfc3875.txt:423 | 타임아웃 후 스크립트 종료는 MAY (raw/rfc3875.txt:1255-1258). 평가 무한 루프 테스트 (raw/evaluation-sheet-en.md:91) |
| 일시적 과부하 | 503 | raw/rfc9110.txt:7888-7891 | 과부하에 반드시 쓸 필요는 없음 (raw/rfc9110.txt:7895-7897) |

## 공통 규칙

- reason phrase는 권장일 뿐이다. 바꾸거나 빼도 된다 (raw/rfc9110.txt:6841-6844). 빼더라도 status code 뒤 공백은 보내야 한다 (MUST, raw/rfc9112.txt:690-693).
- 에러 응답 본문은 설정된 에러 페이지를, 없으면 기본 에러 페이지를 쓴다 (raw/subject.md:143, raw/subject.md:164).

## 관련

- [[concepts/http-features]], [[concepts/configuration-file]], [[concepts/security]], [[concepts/request-parsing]], [[sources/rfc9110]], [[sources/rfc9112]]
