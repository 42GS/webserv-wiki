---
title: 설계 결정 목록
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc3875.txt, raw/rfc6265.txt, raw/rfc7578.txt, raw/nginx-core-module.md, raw/nginx-request-processing.md, raw/nginx-index-module.md, raw/nginx-rewrite-module.md]
updated: 2026-10-16
---

# 설계 결정 목록

문서로 답이 정해지지 않아 사용자가 정한 것을 모았다. 각 결정의 근거와 구현에 주는 영향, 디펜스에서 설명할 점을 적는다.
문서가 답을 정하는 규칙(RFC MUST 등)은 여기 넣지 않고 각 concept 페이지에 둔다.

| # | 결정 | 날짜 | 관련 페이지 |
|---|---|---|---|
| 1 | 멀티플렉서는 `poll()` | 2026-10-15 | [[concepts/io-multiplexing]] |
| 2 | root 위로 올라가는 `..`는 400 + 연결 닫기 | 2026-10-15 | [[concepts/security]] |
| 3 | 경로의 `%2F`는 400으로 거부 | 2026-10-15 | [[concepts/security]] |
| 4 | virtual host는 구현하지 않음 | 2026-10-15 | [[concepts/configuration-file]] |
| 5 | HEAD를 지원함 | 2026-10-15 | [[concepts/http-features]] |
| 6 | index 파일이 CGI 확장자면 CGI로 실행 | 2026-10-15 | [[concepts/configuration-file]], [[concepts/cgi]] |
| 7 | 업로드는 서버가 `multipart/form-data`만 받아 저장 | 2026-10-15 | [[concepts/file-upload]] |
| 8 | 보너스 쿠키·세션은 CGI 예제로 보여 줌 | 2026-10-15 | [[concepts/bonus]] |
| 9 | 설정 파일은 NGINX 문법을 따름 | 2026-10-16 | [[concepts/configuration-file]], [[analysis/design]] |

1~3은 앞서 정한 것을 함께 모았다. 근거는 각 관련 페이지에 있다.

## 4. virtual host 구현하지 않음

- 근거: subject는 virtual host를 범위 밖으로 두되 구현해도 된다고 한다 (raw/subject.md:151). 평가표는 같은 `interface:port`에 여러 사이트를 설정하면 에러여야 하고, virtual host를 구현했다면 그것도 유효하다고 한다 (raw/evaluation-sheet-en.md:108).
- 구현: 같은 `interface:port`가 설정에 두 번 나오면 **설정 파싱 단계에서 에러 메시지와 함께 시작하지 않는다**. server 선택은 요청을 받은 `address:port`만으로 끝나고 `Host`로 고르지 않는다 (**판단**).
- HTTP/1.1 요청의 `Host` 누락·중복·잘못된 값은 여전히 400이다 (MUST, raw/rfc9112.txt:445-448). virtual host가 없어도 요청 검증은 한다.
- 디펜스: 평가표의 "Port issues" 항목에서 같은 포트 중복 설정이 에러로 끝나는 것을 보여 준다.

## 5. HEAD 지원

- 근거: RFC 9110은 범용 서버에 GET과 HEAD를 MUST로 요구한다 (raw/rfc9110.txt:3794-3795). subject는 GET·POST·DELETE만 요구하지만 (raw/subject.md:147), 평가자는 브라우저 점검에서 임의 테스트를 할 수 있다 (raw/evaluation-sheet-en.md:103).
- 구현:
  - GET과 같은 처리를 하고 응답 본문만 보내지 않는다 (MUST NOT, raw/rfc9110.txt:3987-3988). 헤더는 GET과 같게 보낸다 (SHOULD, raw/rfc9110.txt:3993-3994).
  - `Content-Length`를 보낸다면 GET이었을 때와 같은 값이어야 한다 (raw/rfc9110.txt:3226-3230).
  - CGI가 HEAD 요청에 본문을 출력하면 서버가 버린다 (MUST, raw/rfc3875.txt:1143-1145).
- 라우트의 허용 메서드 목록에 GET이 있으면 HEAD도 허용할지는 정해야 한다. NGINX `limit_except`는 GET을 허용하면 HEAD도 허용한다 (raw/nginx-core-module.md:795). 이를 따른다 (**판단**).

## 6. index 파일이 CGI 확장자면 CGI로 실행

- 근거: NGINX는 index 파일을 찾으면 그 경로로 내부 리다이렉트하고 location을 다시 찾으므로, `index.php`는 CGI location에서 처리된다 (raw/nginx-request-processing.md:168, raw/nginx-index-module.md:46).
- 구현: 디렉토리 요청에서 index 파일을 찾으면 `디렉토리 경로 + index 파일 이름`으로 요청을 다시 처리한다. CGI 확장자 규칙에 걸리면 CGI로 실행한다 (**판단**).
- 내부 리다이렉트이므로 반복 횟수 상한을 적용하고, 넘으면 500 (NGINX는 10회, raw/nginx-rewrite-module.md:24) → [[concepts/resilience]].
- 효과: CGI 소스가 정적 파일로 그대로 노출되지 않는다 (**판단**).

## 7. 업로드는 서버가 `multipart/form-data`만 저장

- 근거: subject는 라우트별로 업로드를 허용하고 저장 위치를 지정하는 설정을 요구한다 (raw/subject.md:172). 브라우저 폼 업로드 형식이 `multipart/form-data`다 (raw/rfc7578.txt:105-110). 평가는 파일을 올린 뒤 다시 받아 본다 (raw/evaluation-sheet-en.md:82).
- 구현: 업로드가 허용된 라우트에 POST로 온 `multipart/form-data` 본문을 서버가 파싱해 설정된 저장 위치에 쓴다. 절차는 [[concepts/file-upload]] "서버가 처리하는 순서".
- 업로드 라우트에 다른 형식의 본문이 오면 **415**로 거부한다 (**판단**). 415는 요청 내용의 형식이 이 메서드·대상 리소스에서 지원되지 않을 때의 코드다 (raw/rfc9110.txt:7738-7740). 응답에 `Accept`로 받을 수 있는 형식을 알려 줄 수 있다 (raw/rfc9110.txt:7751-7753).
- CGI 확장자 규칙이 걸리는 경로로 온 POST는 업로드가 아니라 CGI로 넘긴다 (**판단**). 업로드 위치에서는 CGI를 실행하지 않는다 → [[concepts/security]].

## 8. 쿠키·세션은 CGI 예제로

- 근거: subject는 쿠키·세션 관리를 "간단한 예제를 제공"하는 형태로 요구한다 (raw/subject.md:215). 서버에 세션 저장소를 두면 식별자용 난수가 필요한데, 허용 함수에 난수 함수가 없고 `/dev/urandom` 읽기는 `poll()` 예외인지 불분명하다 → [[analysis/subject-vs-evaluation]] 1.10절.
- 서버가 할 일:
  - 요청의 `Cookie` 헤더를 CGI에 `HTTP_COOKIE`로 넘긴다 (변수 이름 규칙, raw/rfc3875.txt:1038-1042).
  - CGI가 출력한 `Set-Cookie` 여러 줄을 합치지 않고 모두 응답에 옮긴다 (SHOULD NOT fold, raw/rfc6265.txt:315-319). 응답 헤더 저장 구조가 같은 이름의 헤더를 여러 개 담을 수 있어야 한다.
- 스크립트가 할 일: 식별자 발급, 세션 상태 저장, 쿠키 만료 처리.
- 위험 (**판단**): 평가표 문구는 "웹 서버에 동작하는 세션·쿠키 시스템"이다 (raw/evaluation-sheet-en.md:126). 평가자가 서버 자체의 기능으로 해석할 수 있으므로, 디펜스에서 서버가 쿠키 헤더를 어떻게 전달하는지와 subject의 "예제 제공" 문구를 함께 설명한다.
- 이 결정으로 1.10절의 `/dev/urandom` 질문은 서버 구현에서는 생기지 않는다. 스크립트 언어(Python 등)의 난수 기능은 subject 허용 함수 목록의 대상인지 불분명하다 (**미확인**, 평가자 합의).

## 9. 설정 파일은 NGINX 문법

- 근거: subject는 NGINX 설정의 `server` 섹션을 참고해도 된다고 한다 (raw/subject.md:161). 평가자가 NGINX와 비교하며 볼 수 있다 (raw/subject.md:186).
- 구현: `server { ... }`, `location 경로 { ... }` 블록, `지시자 인자 ...;` 형식, `#` 주석. NGINX에 같은 기능의 지시자가 있으면 그 이름과 인자 형식을 쓴다 (`listen`, `root`, `index`, `autoindex`, `error_page`, `client_max_body_size`, `return`). 크기는 NGINX처럼 `1m` 같은 단위를 받는다 (기본값 표기 `client_max_body_size 1m;`, raw/nginx-core-module.md:355). 지시자 목록과 세부는 [[analysis/design]] 3절.
- NGINX에 없는 기능(업로드 저장 위치, 확장자별 CGI 실행)은 새 지시자를 만든다 (**판단**).
- 허용 메서드는 NGINX `limit_except METHOD ... { deny all; }` 형식으로 받고, 블록 안에는 `deny all;`만 허용한다 (2026-10-16 사용자 선택).
- `root`와 `alias`를 둘 다 지원한다 (2026-10-16 사용자 선택). `root`는 NGINX처럼 URI 전체를 붙이고 (raw/nginx-core-module.md:1516), subject 예시의 매핑(raw/subject.md:169)은 `alias`로 쓴다 (raw/nginx-core-module.md:132-140) → [[concepts/configuration-file]] "subject 예시는 NGINX alias 방식".

## 아직 정하지 않은 것

평가자 합의가 필요한 해석 질문은 [[analysis/subject-vs-evaluation]] 6절 "남은 미확인"에 있다 (허용 함수 범위, `fcntl` "For macOS only", read/write 외 errno, `waitpid` 매크로, `F_SETFD`).
