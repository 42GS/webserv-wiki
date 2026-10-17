---
title: 설계 결정 목록
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/posix-remove.md, raw/posix-rmdir.md, raw/fs-observed-remove-name-length.md, raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc3875.txt, raw/rfc6265.txt, raw/rfc7578.txt, raw/nginx-core-module.md, raw/nginx-request-processing.md, raw/nginx-index-module.md, raw/nginx-rewrite-module.md, raw/design-checks-observed.md]
updated: 2026-10-17
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
| 10 | 시각은 허용 함수만으로 얻고 `Date`를 보냄 | 2026-10-16 | [[concepts/http-features]], [[analysis/design]] 4절 |
| 11 | `client_max_body_size` 상한 100MB | 2026-10-16 | [[analysis/design]] 3절 |
| 12 | CGI 자식은 `execve` 실패 시 `std::exit`, `fork` 전 `access` 검사 | 2026-10-16 | [[concepts/cgi]], [[analysis/design]] 9절 |
| 13 | `listen`은 `IPv4:port`와 `port`만 받음 | 2026-10-16 | [[concepts/configuration-file]], [[analysis/design]] 3절 |
| 14 | alias location은 경로 경계에서만 맞춤 | 2026-10-16 | [[concepts/security]], [[analysis/design]] 7절 |
| 15 | 파일 삭제는 `std::remove` | 2026-10-17 | [[analysis/subject-vs-evaluation]] 1.4절, [[analysis/design]] 7절 |
| 16 | `limit_except`가 없는 location은 GET·HEAD만 받음 | 2026-10-17 | [[concepts/configuration-file]], [[analysis/design]] 3절 |
| 17 | 같은 이름의 업로드는 409로 거부 | 2026-10-17 | [[concepts/file-upload]] |
| 18 | 업로드 요청 하나의 파일은 5개까지, 넘으면 413 | 2026-10-17 | [[concepts/file-upload]], [[analysis/design]] 7·12절 |

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

## 10. 시각은 허용 함수만으로, `Date`는 보냄

- 근거: 타임아웃이 없으면 요청이 무한히 멈출 수 있어 시각이 필요하다 (raw/subject.md:139). 허용 함수 목록에 시간 함수가 없다 (raw/subject.md:113). 사용자는 평가자가 문제 삼을 수 없는 보수적인 쪽을 원했다.
- 구현: 시계용 파일에 `open`·`write`·`close` 후 `stat`의 수정 시각을 현재 시각으로 쓴다 (모두 목록 안의 함수) → [[analysis/design]] 4절 "시계".
- 시계가 있으므로 RFC 9110대로 2xx·3xx·4xx 응답에 `Date`를 보낸다 (MUST, raw/rfc9110.txt:2313-2317). 날짜 문자열 변환도 직접 계산한다.
- 버린 대안: `time()`은 단순하지만 목록 밖이다. 시간 함수 없이 `poll()` 타임아웃 횟수로 어림하는 방법은 요청이 계속 들어오면 시간이 흐르지 않아 타임아웃이 걸리지 않을 수 있다.
- 디펜스: 왜 파일로 시각을 얻는지(허용 함수 목록) 설명한다.

## 11. `client_max_body_size` 상한 100MB

- 근거: 본문은 메모리에 모은 뒤 저장한다(업로드 단순 방식). 메모리가 바닥나면 `std::bad_alloc` 대신 프로세스가 강제로 끝났다 (raw/design-checks-observed.md:119-123). 서버가 끝나면 0점이다 (raw/evaluation-sheet-en.md:24).
- 구현: 설정의 `client_max_body_size`가 100MB를 넘거나 0(NGINX에서는 검사 안 함)이면 설정 오류로 시작하지 않는다. 0의 의미만 NGINX와 다르다. `Content-Length`를 알면 그 크기만큼 `reserve`해 문자열이 두 배로 커지는 것을 피한다. chunked 본문은 해제한 크기로 상한을 검사한다.
- 남는 위험 (**판단**): 동시 업로드 수 × 상한만큼 메모리가 필요하다. 평가의 업로드 시험은 작은 파일이다.

## 12. CGI 자식 종료: `std::exit` + `fork` 전 `access` 검사

- 쟁점: `execve`가 실패한 자식을 끝낼 `exit`·`_exit`가 허용 목록(raw/subject.md:111-113)에 없다. 한편 subject는 C 함수 사용을 허용하고 C++ 버전을 권한다 (raw/subject.md:51) → [[analysis/subject-vs-evaluation]] 1.4절.
- 결정: 51줄에 따라 C++98 표준 라이브러리의 `std::exit`(`<cstdlib>`)를 쓴다 (사용자 선택, 2026-10-16). `_exit`은 POSIX 함수라 쓰지 않는다.
- 보조 대책: `fork` 전에 `access`(허용 함수)로 스크립트와 실행 파일을 확인해, 없으면 404, 권한이 없으면 403으로 자식을 만들기 전에 끝낸다. `execve` 실패를 완전히 없애지는 못하므로 `std::exit(1)`은 남는다.
- 주의: `std::exit`은 부모에게서 물려받은 출력 버퍼를 다시 내보냈다 (raw/design-checks-observed.md:183-194). 자식의 표준 출력은 CGI pipe이므로 `fork` 직전에 표준 출력·에러를 flush한다. 정적 객체 소멸자에 부작용(파일 삭제, `kill` 등)을 두지 않는다 (**판단**).
- 디펜스: 51줄과 111줄을 함께 보여 주고 해석을 설명한다.

## 13. `listen`은 `IPv4:port`와 `port`만

- 쟁점: NGINX `listen`은 주소만(`listen 127.0.0.1;`), `*:8000`, 호스트 이름도 받고, 주소만 쓰면 포트 80을 쓴다 (raw/nginx-core-module.md:936-943, raw/nginx-core-module.md:959). 설계 3절은 `listen 127.0.0.1:8080;`, `listen 8080;` 두 형식만 정했다.
- 기준: 사용자는 "프로젝트 요구사항에 부합하고 안전한 쪽"을 골라 달라고 했다 (2026-10-16).
- 결정: 두 형식만 받고, 나머지는 받을 수 있는 형식을 알려 주는 오류 메시지와 함께 시작하지 않는다.
- 이유 (**판단**):
  - subject가 요구하는 것은 `interface:port` 쌍을 정하는 것이다 (raw/subject.md:163). `IPv4:port`가 그대로 이 형식이다.
  - 주소만 쓰는 형식은 설정 파일에 보이지 않는 포트 80을 쓰게 된다. 포트가 늘 파일에 적혀 있으면 평가자가 설정만 보고 어디에 붙을지 안다.
  - `*:8000`은 `8000`(= `0.0.0.0:8000`)과 같은 뜻의 다른 표기일 뿐이라 받을 이유가 없다.
  - 거부해도 원인 메시지와 종료 코드 1로 끝나므로 크래시가 아니다. 평가자는 설정 파일을 고칠 수 있다 (raw/evaluation-sheet-en.md:24).
- 시험: [[analysis/test-plan]] C-11 (`rejectsListenWithoutPortOrWithWildcard`).

## 14. alias location은 경로 경계에서만 맞춤

- 쟁점: 2차 코드 리뷰에서 `location /kapouet { alias www/; }` 설정에 `/kapouet../secret/s.txt`를 요청하니 alias 밖의 `secret/s.txt`가 200으로 나왔다(실측, 2026-10-16). `kapouet..`는 점 세그먼트가 아니라서 정규화를 통과하고, location 부분을 떼고 남은 `../secret/s.txt`가 alias 뒤에 붙는다. URI를 파일 시스템에 매핑하는 서버는 시스템에 특별한 의미가 있는 이름에 접근하지 않아야 한다 (raw/rfc9110.txt:8560-8565).
- 결정 (사용자, 2026-10-16): alias를 쓰는 location은 떼고 남은 경로가 비었거나 `/`로 시작할 때만 그 location의 파일로 본다. 아니면 404.
- NGINX와 다른 점 (**판단**): NGINX의 prefix location은 `/kapouetX`처럼 경로 중간에서도 맞는다 ([[concepts/configuration-file]] "location 매칭"). 이 과제는 alias일 때만 경계를 요구한다. `root`는 정규화한 URI 전체를 붙이므로 밖으로 나갈 수 없어 그대로 둔다.
- 함께 고친 것: `index` 값에 `/`가 들어가면 설정 오류로 한다(`index ../secret/s.txt;`도 root 밖 파일을 200으로 보냈다, 실측).
- 시험: [[analysis/test-plan]] R-20, C-29.

## 15. 파일 삭제는 `std::remove`

- 쟁점: DELETE가 동작해야 하는데 (raw/subject.md:147, raw/evaluation-sheet-en.md:79), 허용 함수 목록에 파일을 지우는 `unlink`·`remove`가 없다 (raw/subject.md:113).
- 결정 (사용자, 2026-10-17): 결정 12와 같이 51줄("C 함수 사용 허용, C++ 버전 권장", raw/subject.md:51)에 따라 C++98 `<cstdio>`의 `std::remove`를 쓴다.
- 쓰는 곳: DELETE, 그리고 업로드 쓰기가 중간에 실패했을 때 그 요청이 만든 파일을 지울 때.
- 동작: POSIX에서 `remove()`는 디렉토리가 아니면 `unlink`, 디렉토리면 `rmdir`과 같다 (raw/posix-remove.md:33-35). `rmdir`은 빈 디렉토리만 지운다 (raw/posix-rmdir.md:25). macOS와 Ubuntu 22.04도 그렇게 동작했다 (raw/fs-observed-remove-name-length.md:40-42, raw/fs-observed-remove-name-length.md:48-50).
- 남은 쟁점 (사용자가 정할 것, 2026-10-17 보류): DELETE는 라우터가 일반 파일인지 확인한 뒤 `std::remove`를 부른다. 그 사이에 다른 프로세스가 같은 경로를 빈 디렉토리로 바꾸면 그 디렉토리가 지워진다. 비어 있지 않은 디렉토리는 지워지지 않는다. 서버는 단일 프로세스라 요청끼리는 이 틈을 만들 수 없다 (**판단**).
- 디펜스: 51줄과 111~113줄을 함께 보여 주고 해석을 설명한다 → [[analysis/subject-vs-evaluation]] 1.4절.

## 16. `limit_except`가 없는 location은 GET·HEAD만 받음

- 쟁점: 설계 3절은 `limit_except`가 없는 location에서 모든 메서드를 허용했다. DELETE를 구현하면, 설정에서 `limit_except`를 빠뜨린 location의 사이트 파일을 누구나 지울 수 있다.
- 원문: subject는 라우트마다 받을 메서드 목록을 설정하게 하고 (raw/subject.md:166-167), 평가표는 권한이 있을 때와 없을 때 DELETE를 해 보라고 한다 (raw/evaluation-sheet-en.md:73). 설정이 없을 때의 기본값은 둘 다 정하지 않는다. RFC 9110도 요구가 아니라 설명으로, 서버는 보통 삭제 방법이 정해진 리소스에만 DELETE를 허용한다고 한다 (raw/rfc9110.txt:4213-4215).
- 결정 (사용자, 2026-10-17): `limit_except`가 없는 location은 GET·HEAD만 받는다. 파일을 바꾸는 POST·DELETE는 `limit_except`에 적어야 열린다.
- 함께 본 다른 안: 지금처럼 전부 허용(설정을 빠뜨리면 파일이 지워짐), 전부 막기(정적 사이트도 location마다 `limit_except GET`이 필요하고, server `root`로 자동으로 만드는 location `/`가 쓸모없어짐), DELETE는 `upload_store`가 있는 location에서만(허용 규칙이 두 곳에 생김).
- NGINX와 다른 점: NGINX `limit_except`는 location 안에서 허용할 메서드를 제한하는 지시자다 (raw/nginx-core-module.md:795). 이름과 형식은 같고, 지시자가 없을 때의 기본값만 다르다(결정 11의 `0`과 같은 종류).
- 함께 정한 것 (**판단**): POST는 `upload_store`가 있는 location만 답한다(7단계에서 CGI가 더해진다). `limit_except`에 POST가 있어도 저장 위치가 없으면 405이고 `Allow`에 넣지 않는다.
- 시험: [[analysis/test-plan]] C-17, F-09, F-12, D-04.

## 17. 같은 이름의 업로드는 409로 거부

- 근거: RFC 7578은 filename을 해석할 때 받는 쪽의 파일을 실수로 덮어쓰지 않게 하라고 한다 (raw/rfc7578.txt:497-499). 409는 대상 리소스의 현재 상태와 충돌해서 요청을 끝낼 수 없을 때의 코드이고, 사용자가 충돌을 풀고 다시 보낼 수 있는 경우에 쓴다 (raw/rfc9110.txt:7652-7655).
- 결정 (사용자, 2026-10-17): 저장 위치에 같은 이름이 이미 있으면 409로 거부한다. 다른 이름으로 바꿔 저장하거나 덮어쓰지 않는다. 한 요청 안에 같은 이름이 두 번 와도 409다 (**판단**).
- 구현: 쓰기 전에 모든 파일 이름을 검사해서, 하나라도 충돌하면 아무것도 저장하지 않는다. 409 본문에는 충돌한 이름을 적는다. 서버는 사용자가 충돌 원인을 알 수 있을 만큼의 내용을 만들어야 한다 (SHOULD, raw/rfc9110.txt:7655-7657). 파일은 `O_EXCL`로 만들어, 검사 뒤에 다른 프로세스가 만든 파일도 덮어쓰지 않는다.
- 같은 이름으로 다시 올리려면 먼저 DELETE한다(업로드 location에 DELETE를 허용했을 때).
- 시험: [[analysis/test-plan]] F-08.

## 18. 업로드 요청 하나의 파일은 5개까지

- 쟁점: 6단계 코드 리뷰에서, 크기 상한 안의 본문 하나로 파일을 얼마든지 만들 수 있음을 확인했다. 약 1MB(993,895바이트) 요청 하나가 파일 15,000개를 만들었고, 응답까지 0.82초가 걸렸다(실측, macOS, 2026-10-17). 그동안 이벤트 루프는 다른 연결을 처리하지 못한다.
- 결정 (사용자, 2026-10-17): 한 요청의 파일은 5개까지다(`limits::kMaxUploadFiles`).
- 넘을 때의 코드 (사용자가 400과 413 중 고르게 맡김, **판단**): 413. 400은 잘못된 문법이나 framing처럼 클라이언트 오류로 보이는 요청의 코드다 (raw/rfc9110.txt:7543-7546). 파일 6개짜리 요청은 문법이 맞다. 413은 요청 내용이 서버가 처리하려는 양보다 커서 거절할 때의 코드다 (raw/rfc9110.txt:7710-7712).
- 본문은 끝까지 읽은 뒤이므로 연결은 유지한다(파서의 413과 다름).
- 시험: [[analysis/test-plan]] F-15.

## 아직 정하지 않은 것

평가자 합의가 필요한 해석 질문은 [[analysis/subject-vs-evaluation]] 6절 "남은 미확인"에 있다 (허용 함수 범위, `fcntl` "For macOS only", read/write 외 errno, `waitpid` 매크로, `F_SETFD`).
