---
title: 보너스
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/rfc6265.txt, raw/rfc3875.txt]
updated: 2026-10-15
---

# 보너스

| 항목 | subject | 평가표 |
|---|---|---|
| 쿠키와 세션 관리 (간단한 예제 제공) | raw/subject.md:215 | raw/evaluation-sheet-en.md:126 |
| 복수 CGI 타입 | raw/subject.md:216 | raw/evaluation-sheet-en.md:130 |

> [!warning] 조건
> 필수 항목이 완벽히 통과해야만 평가한다 (raw/subject.md:218). 평가표는 "에러 처리가 제대로 동작"하는 것까지 조건으로 적는다 (raw/evaluation-sheet-en.md:122).

## 쿠키와 세션

### 동작 방식

- 서버가 응답에 `Set-Cookie`를 넣으면 클라이언트는 이후 요청에 `Cookie` 헤더로 돌려준다. 서버는 그 내용을 무시하거나 원하는 용도로 쓸 수 있다 (raw/rfc6265.txt:299-304).
- `Set-Cookie`는 어떤 응답에든 넣을 수 있고, 4xx·5xx 응답의 것도 클라이언트가 처리한다 (raw/rfc6265.txt:306-310).

### Set-Cookie

| 규칙 | 근거 |
|---|---|
| 형식: `Set-Cookie: 이름=값` 뒤에 `; 속성`이 0개 이상 | raw/rfc6265.txt:455-457 |
| 값에 쓸 수 없는 문자: 제어 문자, 공백, `"`, `,`, `;`, `\`. 임의 데이터는 Base64 등으로 인코딩 (SHOULD) | raw/rfc6265.txt:459-463, raw/rfc6265.txt:493-495 |
| 한 응답에 `Set-Cookie`를 여러 개 넣을 수 있고, 하나로 합치면 안 됨 (SHOULD NOT) | raw/rfc6265.txt:310-319 |
| 같은 응답에 같은 이름의 쿠키를 두 번 넣지 않음 (SHOULD NOT) | raw/rfc6265.txt:511-513 |
| `Max-Age`는 0이 아닌 숫자로 시작. `Expires`는 rfc1123 날짜 | raw/rfc6265.txt:469-476 |
| 둘 다 있으면 `Max-Age`가 우선. 둘 다 없으면 브라우저 세션이 끝날 때까지 | raw/rfc6265.txt:587-591 |
| `Path`를 생략하면 요청 경로의 "디렉토리"가 기본값 | raw/rfc6265.txt:637-640 |
| `HttpOnly`면 스크립트 API로 쿠키를 읽을 수 없음 | raw/rfc6265.txt:681-684 |
| 쿠키 삭제: 과거 날짜의 `Expires`로 같은 쿠키를 다시 보냄 | raw/rfc6265.txt:544-545 |

과제 적용 (**판단**):
- **응답 헤더 저장 구조:** 같은 이름의 헤더를 여러 개 담을 수 있어야 한다. "이름 → 값 하나" 구조면 두 번째 `Set-Cookie`가 첫 번째를 덮어쓴다. CGI가 출력하는 `Set-Cookie` 여러 줄도 그대로 전달한다 → [[concepts/cgi]].
- **세션 쿠키는 `Path=/`를 명시**해 사이트 전체에서 같은 쿠키가 돌아오게 한다.
- **삭제는 고정된 과거 날짜 문자열**(예: 1970년 1월 1일)의 `Expires`로 한다. 서버 문법상 `Max-Age=0`은 허용되지 않는다 (raw/rfc6265.txt:471). 고정 문자열이면 시간 함수가 필요 없어 허용 함수 범위 질문을 피한다 → [[analysis/subject-vs-evaluation]] 1.4절.
- 만료 시간을 주고 싶으면 날짜 계산이 필요 없는 `Max-Age`를 쓴다. 다만 일부 브라우저는 `Max-Age`를 지원하지 않는다고 한다 (raw/rfc6265.txt:583-585).

### Cookie 요청 헤더

| 규칙 | 근거 |
|---|---|
| 형식: `Cookie: 이름=값; 이름=값` | raw/rfc6265.txt:700-701 |
| 속성(만료, 경로, Secure 등)은 돌아오지 않는다 | raw/rfc6265.txt:709-713 |
| 같은 이름의 쿠키가 여러 개 올 수 있고, 순서에 의존하면 안 됨 (SHOULD NOT) | raw/rfc6265.txt:719-724 |
| 쿠키가 돌아오지 않아도 적절히 동작해야 함 (SHOULD) | raw/rfc6265.txt:1482-1484 |
| 브라우저는 쿠키 하나에 최소 4096바이트를 지원해야 함. 서버의 헤더 크기 상한은 이를 감안 | raw/rfc6265.txt:1471-1472 |

### 세션

- 정보를 쿠키에 직접 넣지 말고, **세션 식별자(nonce)만 쿠키에 넣고 상태는 서버에 둔다**. 서버는 식별자를 키로 상태를 찾는다 (raw/rfc6265.txt:1716-1720).
- session fixation을 피해야 한다 (SHOULD, raw/rfc6265.txt:1730-1731). 공격자가 자기 식별자를 피해자에게 심어 두고 나중에 그 식별자로 접근하는 공격이다 (raw/rfc6265.txt:1732-1747). 클라이언트가 보낸, 서버가 모르는 식별자는 받아들이지 않고 서버가 새로 발급한다 (**판단**).
- 식별자는 추측하기 어려워야 한다 (**판단**: 추측할 수 있으면 남의 세션을 쓸 수 있다. RFC 6265는 이 요구를 직접 적지 않는다). 허용 함수에는 난수 함수가 없다 (raw/subject.md:113). `/dev/urandom`을 `open`·`read`로 읽는 방법은 [[analysis/subject-vs-evaluation]] 1.10절의 질문에 걸린다.

### 구현 방식 (열린 설계 질문)

- subject는 "간단한 예제를 제공"하라고 하고 (raw/subject.md:215), 평가표는 "웹 서버에 동작하는 세션·쿠키 시스템"을 본다 (raw/evaluation-sheet-en.md:126).
- 서버가 직접 세션 저장소를 두고 쿠키를 발급할지, CGI 예제 스크립트가 `Set-Cookie`를 출력하고 서버는 헤더를 그대로 전달할지는 문서가 정하지 않는다. 어느 쪽이든 서버는 `Cookie` 헤더를 CGI에 `HTTP_COOKIE`로 넘겨야 한다. subject는 클라이언트가 보낸 요청 전체를 CGI가 쓸 수 있어야 한다고 한다 (raw/subject.md:178). 변수 이름 규칙은 RFC 3875를 따른다 (raw/rfc3875.txt:1038-1042). RFC 3875 자체는 모든 헤더를 변수로 만들 의무는 없다고 한다 (raw/rfc3875.txt:1051-1052).

## 관련

- [[concepts/cgi]], [[concepts/security]], [[sources/rfc6265]]
