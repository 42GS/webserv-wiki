---
title: IANA HTTP Status Code Registry
type: source
sources: [raw/iana-http-status-codes.txt, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# IANA HTTP Status Code Registry

원본: `raw/iana-http-status-codes.txt`. <https://www.iana.org/assignments/http-status-codes/http-status-codes.txt>를 2026-10-15에 받아 그대로 저장했다. IANA가 제공하는 텍스트 형식이라 변환하지 않았다.
레지스트리 마지막 갱신일은 2025-09-15다 (raw/iana-http-status-codes.txt:9-10). 레지스트리의 참조 문서는 RFC 9110 16.2.1절이다 (raw/iana-http-status-codes.txt:29-30).

평가표는 평가 전에 HTTP status code 목록을 찾아 두고, 코드가 틀리면 점수를 주지 말라고 한다 (raw/evaluation-sheet-en.md:67). 이 레지스트리가 그 목록이다.

## 내용

- 클래스: 1xx 정보, 2xx 성공, 3xx 리다이렉트, 4xx 클라이언트 오류, 5xx 서버 오류 (raw/iana-http-status-codes.txt:36-40).
- 코드별 이름과 정의 문서 (raw/iana-http-status-codes.txt:48-123). 과제에서 쓰는 코드의 이름은 [[concepts/status-codes]] "reason phrase" 절.
- 431 "Request Header Fields Too Large"는 RFC 6585 정의다 (raw/iana-http-status-codes.txt:108). 정의 내용은 [[sources/rfc6585]].
