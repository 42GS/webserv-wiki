---
title: 보안 — 경로·주입·길이·splitting·smuggling
type: concept
sources: [raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc3875.txt, raw/nginx-core-module.md, raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# 보안 — 경로·주입·길이·splitting·smuggling

subject와 평가표에는 보안 항목이 따로 없다. 하지만 아래 문제는 대부분 크래시·hang으로 이어지고, 크래시는 곧 0점이다 (raw/subject.md:46, raw/evaluation-sheet-en.md:24). → [[concepts/resilience]]

## 1. 경로 공격 (RFC 9110 17.3)

- URI를 파일 시스템에 매핑하는 서버는 시스템에 특별한 의미가 있는 이름에 접근하지 않아야 한다 (raw/rfc9110.txt:8560-8565).
- 대표적인 예가 상위 디렉토리를 뜻하는 `..`다. 장치로 데이터를 보내는 특수 경로도 있다 (raw/rfc9110.txt:8567-8570).
- 이런 공격의 목적은 DoS 아니면 설정·소스 파일 노출이다 (raw/rfc9110.txt:8577-8580).

과제 적용:
- root 매핑(raw/subject.md:169)으로 경로를 만든 뒤, 결과가 해당 라우트의 root 밖으로 나가지 않는지 확인한다. 응답 코드 선택은 [[concepts/status-codes]] 참고.
- percent-encoding된 `..`(예: `%2e%2e`)도 디코딩한 뒤에 검사해야 한다. 디코딩 규칙은 RFC 3986에서 확인 (**미확인**, [[source-wishlist]] P2).
- NGINX는 location 매칭 전에 `%XX` 디코딩 → `.`·`..` 해석 → 연속 `/` 합치기 순서로 URI를 정규화한다 (raw/nginx-core-module.md:1063). 같은 순서로 정규화한 뒤 매칭하고 경로를 만들면, 인코딩된 `..`로 우회하는 것을 막을 수 있다. 보안상 `/` 합치기를 끄지 말라고 권한다 (raw/nginx-core-module.md:1207).
- 업로드 파일명(raw/subject.md:172)과 DELETE 대상 경로(raw/evaluation-sheet-en.md:73)에도 같은 검사를 적용한다.
- CGI 경로는 script-path와 extra-path로 **나누기 전에** `..`를 제거하거나 해석한다. `PATH_TRANSLATED`를 만들 때도 예상 경로 밖으로 나가지 않게 한다 (raw/rfc3875.txt:1801-1806).
- 서버는 `.`·`..` 경로 세그먼트를 금지할지, 일반 세그먼트로 볼지, 상대 URL 규칙으로 해석할지 정해 두어야 한다 (raw/rfc3875.txt:1631-1634).

## 2. 명령·코드 주입 (RFC 9110 17.4)

- 요청 데이터(메서드, URI, 헤더, 본문)는 모두 신뢰할 수 없다. 명령 실행이나 인터프리터로 넘어가면 명령으로 해석될 수 있다 (raw/rfc9110.txt:8586-8591).
- 요청 데이터를 명령으로 해석되는 곳에 쓰지 말고, 고정된 문자열과 비교한 결과로만 동작하라고 권한다 (raw/rfc9110.txt:8601-8605).
- 로그 파일처럼 저장했다가 나중에 처리하는 데이터에도 같은 주의가 필요하다 (raw/rfc9110.txt:8609-8611).

과제 적용:
- CGI는 `execve`로 실행한다 (raw/subject.md:113). 셸을 거치지 않고 인자 배열을 직접 넘기면 셸 해석으로 생기는 주입을 피할 수 있다.
- 스크립트는 보통 서버와 같은 사용자 권한으로 실행되므로, 서버 프로세스·설정·문서·로그를 건드리지 못하게 해야 한다 (raw/rfc3875.txt:1722-1725).
- CGI 환경 변수에 요청 값이 들어간다 (raw/subject.md:178). 그 값을 스크립트가 어떻게 쓰는지는 스크립트 책임이지만, 서버는 값을 그대로 전달할 뿐 해석하지 않는다. → [[concepts/cgi]]

## 3. 길이 공격 (RFC 9110 17.5)

- 텍스트 기반이라 매우 길거나 매우 느린 데이터 스트림에 취약하다 (raw/rfc9110.txt:8615-8618).
- URI가 너무 길면 414, 본문이 너무 크면 413으로 거부할 수 있다 (raw/rfc9110.txt:8626-8628).
- 메서드, 헤더 이름, 숫자 값, chunk 길이까지 처리량을 제한해야 한다. 그렇지 않으면 버퍼·산술 오버플로로 인한 임의 코드 실행이나 DoS에 노출된다 (raw/rfc9110.txt:8631-8636).
- `Content-Length`는 매우 큰 수일 수 있으니 정수 변환 오버플로를 막아야 한다 (MUST, raw/rfc9110.txt:3251-3254).

과제 적용:
- body 크기 제한(raw/subject.md:165)과 함께 요청줄·헤더 전체 크기에도 상한을 둔다.
- CGI 응답 헤더·본문 길이에도 제한이 없으므로 고정 크기 버퍼를 가정하지 않는다 (raw/rfc3875.txt:1760-1764). 서버가 파싱할 경로 길이·헤더 양의 상한을 정해 두라고 권한다 (raw/rfc3875.txt:1636-1638).
- 느린 클라이언트는 타임아웃으로 끊는다. "요청이 무한히 hang하면 안 됨"(raw/subject.md:139), "hanging connection 없음"(raw/evaluation-sheet-en.md:116)과 같은 요구다.

## 4. Response splitting (RFC 9112 11.1)

- 요청에 인코딩해 넣은 데이터가 디코딩되어 응답 헤더에 그대로 들어가면, 응답이 둘로 나뉜 것처럼 꾸밀 수 있다 (raw/rfc9112.txt:1760-1766).
- 예: request-target의 파라미터가 리다이렉트의 `Location`에 그대로 들어가는 경우. 인코딩된 CRLF로 응답 하나를 여러 개처럼 보이게 만든다 (raw/rfc9112.txt:1772-1778).
- `%0D`·`%0A` 필터만으로는 부족하다. 더 효과적인 방법은 서버 핵심 코드 외에는 헤더 영역에 CR·LF를 쓰지 못하게 하는 것이다 (raw/rfc9112.txt:1780-1790).

과제 적용:
- 헤더 값을 쓰는 함수 한 곳에서 CR·LF를 거부한다. 리다이렉트 `Location`, CGI가 출력한 헤더를 응답에 옮길 때 모두 이 함수를 거친다 → [[concepts/cgi]].

## 5. Request smuggling (RFC 9112 11.2)

- 수신자마다 파싱이 다른 점을 이용해, 무해해 보이는 요청 안에 다른 요청을 숨기는 기법이다 (raw/rfc9112.txt:1794-1799).
- RFC 9112는 이를 막으려고 본문 길이 결정 규칙(6.3)을 엄격하게 정했다 (raw/rfc9112.txt:1801-1803).

과제 적용:
- `Content-Length`와 `Transfer-Encoding`이 같이 오거나 `Content-Length`가 잘못된 요청은 규칙대로 처리하고 연결을 닫는다 → [[concepts/request-parsing]] 4절.
- 관대한 파싱(여러 공백 허용 등)은 smuggling 위험이 있다 (raw/rfc9112.txt:385-388).

## 관련

- [[concepts/status-codes]], [[concepts/cgi]], [[concepts/resilience]], [[concepts/request-parsing]], [[sources/rfc9110]], [[sources/rfc9112]]
