---
title: 보안 — 경로·주입·길이·splitting·smuggling
type: concept
sources: [raw/rfc9110.txt, raw/rfc9112.txt, raw/rfc3875.txt, raw/nginx-core-module.md, raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc7578.txt, raw/rfc3986.txt, raw/rfc6265.txt, raw/rfc1945.txt, raw/rfc6585.txt, raw/nginx-observed-directory.md]
updated: 2026-10-15
---

# 보안 — 경로·주입·길이·splitting·smuggling

subject와 평가표에는 보안 항목이 따로 없다. 하지만 아래 문제는 대부분 크래시·hang으로 이어지고, 크래시는 곧 0점이다 (raw/subject.md:46, raw/evaluation-sheet-en.md:24). → [[concepts/resilience]]

## 1. 경로 공격 (RFC 9110 17.3)

- URI를 파일 시스템에 매핑하는 서버는 시스템에 특별한 의미가 있는 이름에 접근하지 않아야 한다 (raw/rfc9110.txt:8560-8565).
- 대표적인 예가 상위 디렉토리를 뜻하는 `..`다. 장치로 데이터를 보내는 특수 경로도 있다 (raw/rfc9110.txt:8567-8570).
- HTTP/1.0 명세도 같은 요구를 한다. `..`로 의도한 범위 밖에 접근하는 것을 막아야 하고(must), 설정 파일·스크립트 코드 같은 내부 파일도 내보내면 안 된다 (raw/rfc1945.txt:2809-2823). 과제에서는 CGI 스크립트 원본과 설정 파일이 root 안에 있으면 그대로 노출될 수 있으므로 root 배치에 주의한다 (**판단**).
- 이런 공격의 목적은 DoS 아니면 설정·소스 파일 노출이다 (raw/rfc9110.txt:8577-8580).

### 경로 정규화 절차 (RFC 3986 기준)

요청 경로를 파일 경로로 바꾸기 전에 아래 순서로 정규화한다. 순서가 바뀌면 인코딩된 문자가 구분자로 오해되거나 검사를 우회당한다.

| 순서 | 할 일 | 근거 |
|---|---|---|
| 1 | request-target에서 첫 `?` 앞을 path, 뒤를 query로 나눈다. query는 디코딩하지 않고 CGI `QUERY_STRING`으로 그대로 넘긴다 | raw/rfc3986.txt:1204-1206, raw/rfc3986.txt:1284-1286, raw/rfc3875.txt:809-811 |
| 2 | path를 `/`로 세그먼트로 나눈다. component·subcomponent를 나눈 뒤에 디코딩해야 디코딩된 문자가 구분자로 오해되지 않는다 | raw/rfc3986.txt:754-758, raw/rfc3986.txt:2439-2441 |
| 3 | 세그먼트마다 `%XX`를 **한 번만** 디코딩한다. 16진수는 대소문자 구분 없음. `%`뒤에 16진수 두 자리가 아니면 400 | raw/rfc3986.txt:647-652, raw/rfc3986.txt:767-771 |
| 4 | 디코딩 결과에 NUL(`%00`)이 있으면 거부한다. 원시 데이터를 받지 않는 경우 거부하라고 한다 (should) | raw/rfc3986.txt:2443-2445 |
| 5 | 디코딩 결과에 `/`가 있는 세그먼트(원래 `%2F`)는 거부한다 (**판단**). `/`는 예약 문자라 디코딩하면 의미가 바뀐다. RFC 3875도 인코딩된 `/`가 `PATH_INFO`로 디코딩되는 요청을 거부할 수 있다고 한다 | raw/rfc3986.txt:689-692, raw/rfc3875.txt:736-741 |
| 6 | 빈 세그먼트(연속 `/`)를 합치고, `.`·`..` 세그먼트를 remove_dot_segments 방식으로 제거한다. **`..`가 루트 위로 올라가면 400으로 거부하고 연결을 닫는다** (NGINX 실측, raw/nginx-observed-directory.md:159-164). RFC 3986처럼 루트에서 잘라내지 않는다 (사용자 결정) | raw/rfc3986.txt:1816-1844, raw/rfc3986.txt:2004-2005, raw/rfc3986.txt:2028, raw/nginx-core-module.md:1195-1205 |
| 7 | 정규화된 경로로 location을 매칭하고 root·alias에 붙여 파일 경로를 만든다 → [[concepts/configuration-file]] | raw/nginx-core-module.md:1063-1067 |
| 8 | 보안 검사는 디코딩 이후에 한다. 최종 파일 경로가 해당 root 안에 있는지 확인한다 | raw/rfc3986.txt:2442-2443 |

- `%2e%2e`는 `..`과 동등하다. `%2E`는 비예약 문자 `.`에 해당하고, 비예약 문자의 인코딩은 디코딩해서 같게 본다 (raw/rfc3986.txt:735-743, raw/rfc3986.txt:2234-2236). 3단계에서 디코딩되므로 6단계에서 dot-segment로 처리된다. NGINX도 인코딩된 `..`를 같은 400으로 거부했다 (raw/nginx-observed-directory.md:176-181).
- 두 번 디코딩하면 `%252e%252e` → `%2e%2e` → `..`이 되어 검사를 통과한 뒤 상위 디렉토리를 가리키게 된다. 3단계에서 한 번만 디코딩한다 (raw/rfc3986.txt:767-771).
- 6단계의 dot-segment 제거는 URI 수준의 정리다. 파일 시스템에는 심볼릭 링크 같은 다른 경로가 있을 수 있으므로 8단계 확인을 생략하지 않는다 (**판단**).
- 파일 시스템이 특별한 의미를 주는 문자와 이름은 URI에서 온 데이터로 쓰지 못하게 제한하라고 한다 (raw/rfc3986.txt:2447-2460).

> [!note] NGINX와 순서 차이
> NGINX 문서는 location 매칭에 쓰는 정규화된 URI가 `%XX` 디코딩, `.`·`..` 해석, 연속 `/` 합치기를 거친다고만 하고, 순서와 `%2F` 처리는 적지 않는다 (raw/nginx-core-module.md:1063). NGINX가 `%2F`를 디코딩해 구분자로 쓰는지는 **미확인**이다 (확인: NGINX에 `/a%2Fb` 요청 실측 → [[source-wishlist]] 4-1절). RFC 3986은 세그먼트를 나눈 뒤 디코딩하라고 한다 (raw/rfc3986.txt:754-758). 위 절차는 RFC 순서를 따르고, 해석이 갈릴 수 있는 `%2F`는 5단계에서 거부해 어느 해석으로도 우회되지 않게 했다 (**판단**). 인코딩된 `..`는 NGINX도 400으로 거부했다 (raw/nginx-observed-directory.md:176-181).

과제 적용:
- URI의 `..`가 루트 위로 올라가면 6단계에서 400 + 연결 닫기 (사용자 결정, NGINX와 같음) → [[sources/nginx-observed-directory]].
- 6단계를 통과했는데 8단계에서 최종 파일 경로가 root 밖이면(심볼릭 링크 등) URI 자체는 올바르므로 403으로 거부한다 (**판단**, NGINX 미측정).
- 보안상 `/` 합치기를 끄지 말라고 권한다 (raw/nginx-core-module.md:1207).
- 업로드 파일명(raw/subject.md:172)과 DELETE 대상 경로(raw/evaluation-sheet-en.md:73)에도 같은 검사를 적용한다. multipart의 `filename`은 그대로 쓰지 말고 들어 있는 디렉토리 경로를 쓰지 말라고 한다 (raw/rfc7578.txt:215-220). 기존 파일을 실수로 덮어쓰지 않게 한다 (raw/rfc7578.txt:497-499) → [[concepts/file-upload]].
- 업로드된 파일에는 실행 가능한 내용이 들어 있을 수 있다 (raw/rfc7578.txt:529-530). 업로드 위치에서 CGI가 실행되지 않게 한다 (**판단**) → [[concepts/file-upload]].
- CGI 경로는 script-path와 extra-path로 **나누기 전에** `..`를 제거하거나 해석한다. `PATH_TRANSLATED`를 만들 때도 예상 경로 밖으로 나가지 않게 한다 (raw/rfc3875.txt:1801-1806).
- 서버는 `.`·`..` 경로 세그먼트를 금지할지, 일반 세그먼트로 볼지, 상대 URL 규칙으로 해석할지 정해 두라고 한다 (should, raw/rfc3875.txt:1615-1619, raw/rfc3875.txt:1631-1634).

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
- body 크기 제한(raw/subject.md:165)과 함께 요청줄·헤더 전체 크기에도 상한을 둔다. 헤더 상한 초과는 431 (**판단**). 공격 상황이면 431 대신 연결을 끊어도 된다 (raw/rfc6585.txt:306-308).
- CGI 응답 헤더·본문 길이에도 제한이 없으므로 고정 크기 버퍼를 가정하지 않는다 (raw/rfc3875.txt:1760-1764). 서버가 파싱할 경로 길이·헤더 양의 상한을 정해 두라고 권한다 (raw/rfc3875.txt:1615-1619, raw/rfc3875.txt:1636-1638).
- 느린 클라이언트는 타임아웃으로 끊는다. "요청이 무한히 hang하면 안 됨"(raw/subject.md:139), "hanging connection 없음"(raw/evaluation-sheet-en.md:116)과 같은 요구다.

## 4. Response splitting (RFC 9112 11.1)

- 요청에 인코딩해 넣은 데이터가 디코딩되어 응답 헤더에 그대로 들어가면, 응답이 둘로 나뉜 것처럼 꾸밀 수 있다 (raw/rfc9112.txt:1760-1767).
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

## 6. 세션 (보너스)

- 세션 식별자만 쿠키에 넣고 상태는 서버에 둔다 (**판단**, RFC 6265가 서버들이 흔히 쓰는 방식으로 설명한다, raw/rfc6265.txt:1716-1720). session fixation을 피해야 한다 (SHOULD, raw/rfc6265.txt:1730-1731) → [[concepts/bonus]].
- `Path` 속성은 보안 경계로 믿으면 안 된다 (raw/rfc6265.txt:647-649).

## 관련

- [[concepts/status-codes]], [[concepts/cgi]], [[concepts/resilience]], [[concepts/request-parsing]], [[sources/rfc9110]], [[sources/rfc9112]]
