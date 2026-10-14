---
title: HTTP 기능 요구사항
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc9110.txt]
updated: 2026-10-15
---

# HTTP 기능 요구사항

## 필수 기능

| 기능 | subject | 평가표 |
|---|---|---|
| `GET`, `POST`, `DELETE` | raw/subject.md:147 | raw/evaluation-sheet-en.md:79 |
| 알 수 없는 메서드도 크래시 없이 처리 | — | raw/evaluation-sheet-en.md:80 |
| 정확한 status code | raw/subject.md:142 | raw/evaluation-sheet-en.md:67, raw/evaluation-sheet-en.md:81 |
| 에러 페이지가 설정되지 않아도 기본 에러 페이지 | raw/subject.md:143 | — |
| 완전한 정적 웹사이트 서빙 | raw/subject.md:145 | raw/evaluation-sheet-en.md:99 |
| 파일 업로드 | raw/subject.md:146 | 업로드 후 다운로드 (raw/evaluation-sheet-en.md:82) |
| 표준 브라우저 호환 | raw/subject.md:140 | 네트워크 탭으로 요청·응답 헤더 확인 (raw/evaluation-sheet-en.md:97-98) |
| 여러 포트로 다른 콘텐츠 | raw/subject.md:149 | raw/evaluation-sheet-en.md:107 |
| 요청이 무한히 hang하지 않음 | raw/subject.md:139 | raw/evaluation-sheet-en.md:116 |

> [!danger] status code
> 평가 중 잘못된 status code가 나오면 해당 항목 점수를 주지 않는다 (raw/evaluation-sheet-en.md:67). 상황별 코드는 [[concepts/status-codes]].

## 메서드별 규칙 (RFC 9110 9장)

| 메서드 | 규칙 | 근거 |
|---|---|---|
| GET | 대상 리소스의 현재 표현을 전송. 성공은 200 | raw/rfc9110.txt:3922-3927 |
| GET | 요청 본문에는 정의된 의미가 없다. request smuggling 위험 때문에 거부하고 연결을 닫는 구현도 있다 | raw/rfc9110.txt:3957-3962 |
| POST | 대상 리소스가 자기 방식으로 본문을 처리 (폼 데이터 전달, 새 리소스 생성 등) | raw/rfc9110.txt:4027-4041 |
| POST | 새 리소스를 만들었으면 201 + `Location` (SHOULD) | raw/rfc9110.txt:4050-4053 |
| DELETE | URI 매핑을 제거하는 연산. UNIX `rm`과 비슷하다 | raw/rfc9110.txt:4199-4204 |
| DELETE | 성공 시 202(접수만 함), 204(본문 없음), 200(결과 본문 있음) 중 하나 (SHOULD) | raw/rfc9110.txt:4229-4239 |
| HEAD | GET과 같지만 응답 본문을 보내면 안 됨 (MUST NOT). 헤더는 GET과 같게 (SHOULD) | raw/rfc9110.txt:3987-3988, raw/rfc9110.txt:3993-3994 |
| 공통 | 모르는 메서드는 501, 알지만 허용되지 않은 메서드는 405 (SHOULD) | raw/rfc9110.txt:3800-3804 |
| 공통 | 메서드 토큰은 대소문자를 구분한다. `get`은 `GET`이 아니다 | raw/rfc9110.txt:3748-3751 |

> [!warning] 모순: HEAD
> RFC는 범용 서버라면 GET과 HEAD를 MUST로 지원하라고 한다 (raw/rfc9110.txt:3794-3795). subject는 GET·POST·DELETE만 요구한다 (raw/subject.md:147).
> HEAD를 구현하지 않으면 RFC 기준 501이 된다 (raw/rfc9110.txt:3800-3801). 평가 항목은 아니지만, 구현 비용이 작으므로(GET에서 본문만 뺌) 지원을 고려한다. → [[analysis/subject-vs-evaluation]]

## 응답 헤더 규칙

| 헤더 | 규칙 | 근거 |
|---|---|---|
| `Content-Length` | 본문 크기를 알면 보낸다 (SHOULD, Transfer-Encoding이 없을 때) | raw/rfc9110.txt:3243-3246 |
| `Content-Length` | 1xx·204 응답에는 보내면 안 됨 (MUST NOT) | raw/rfc9110.txt:3238-3239 |
| `Content-Length` | HEAD 응답에 보낼 경우 GET이었을 때와 같은 값이어야 함 | raw/rfc9110.txt:3226-3230 |
| `Content-Type` | 본문이 있으면 보낸다 (SHOULD). 없으면 수신자가 `application/octet-stream`으로 간주하거나 내용을 보고 판단할 수 있음 | raw/rfc9110.txt:2944-2949 |
| `Allow` | 405 응답에 MUST. 다른 응답에는 MAY | raw/rfc9110.txt:4724-4726 |
| `Location` | 201에서는 생성된 리소스, 3xx에서는 리다이렉트 대상을 가리킴. 상대 참조 허용 | raw/rfc9110.txt:4743-4750 |
| `Date` | clock이 있는 origin server는 2xx·3xx·4xx에 MUST. clock이 없으면 보내면 안 됨 | raw/rfc9110.txt:2313-2320 |

> [!warning] 질문: Date 헤더와 허용 함수
> subject의 허용 함수 목록(raw/subject.md:113)에는 시간 함수가 없다. 그 목록이 `<ctime>` 같은 C++ 표준 라이브러리에도 적용되는지는 subject 문구만으로 알 수 없다 (**미확인**). 시간을 얻을 수 없는 서버라면 "clock 없는 서버"로서 Date를 보내지 않는 것이 RFC에 맞는다 (raw/rfc9110.txt:2319-2320). → [[analysis/subject-vs-evaluation]]

## 기준 프로토콜

- HTTP/1.0을 기준점으로 제안, 강제는 아님 (raw/subject.md:123).
- RFC를 읽고 `telnet`, NGINX로 먼저 테스트하라고 권장 (raw/subject.md:123).
- 헤더·동작 비교에 NGINX 사용 가능, HTTP 버전 차이에 주의 (raw/subject.md:141).

## 브라우저 테스트 항목 (Check with a browser)

잘못된 URL, 디렉토리 리스팅, 리다이렉트 URL, 기타 임의 테스트 (raw/evaluation-sheet-en.md:100-103).

## 관련

- [[concepts/configuration-file]] — 라우트별 메서드·리다이렉트·리스팅 설정
- [[concepts/cgi]]
- [[concepts/status-codes]], [[concepts/security]], [[sources/rfc9110]]
