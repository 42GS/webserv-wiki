---
title: "레슨 0: 이 레슨 읽는 법"
type: lesson
sources: [raw/subject.md]
updated: 2026-10-29
---

# 레슨 0: 이 레슨 읽는 법

webserv(C++98 HTTP 서버)가 무엇을, 왜, 어떻게 하는지 처음부터 끝까지 설명하는 학습 노트다. 기초 개념이 없다고 생각하고 썼다.

- 코드 기준: webserv 커밋 `5ca93a2`. 코드 위치는 `src/http/Connection.cpp:127`처럼 **파일:줄**로 적는다. 코드를 고치면 줄 번호가 달라질 수 있다. 2026-10-29에 더한 부분(CGI 헤더 필터링, 운영 로그: 레슨 13의 상자와 13.5, 14.4, 15의 Q15~Q17)은 커밋 `13982df` 기준이고 그 자리에 적어 두었다. 두 커밋(`cad952e`, `13982df`)이 여러 파일의 줄 번호를 바꿨으므로(`git diff --stat 5ca93a2 13982df`), 다른 장의 줄 번호는 `5ca93a2`에서 본다.
- 근거는 `raw/subject.md:130`처럼 위키 원문의 파일:줄, 또는 RFC 절 번호로 적는다. 원문이 직접 말하지 않고 우리가 내린 결론에는 **(판단)** 을 붙였다.

## 상자 읽는 법

> [!example] 쉬운 예
> 비유다. 개념이 처음이면 여기부터 읽는다.

> [!tip] 왜 이렇게?
> 그렇게 만든 이유와 근거(subject, 평가표, RFC, 직접 잰 실험).

> [!info] 평가 때
> 평가자에게 설명할 말과 보여 줄 코드 위치.

> [!danger] 주의
> 0점이 되거나 틀리기 쉬운 곳.

> [!question]- 확인 문제 (눌러서 답 보기)
> 답은 접혀 있다.

## 순서

1. [[lessons/01-request-journey]] — 요청 한 개의 여행 (전체 그림)
2. [[lessons/02-networking-basics]] — 컴퓨터끼리 말하는 법
   - 2A. [[lessons/02a-unix-system-calls]] — 운영체제에게 부탁하기: 시스템 콜 기초
   - 2B. [[lessons/02b-tcp-connections]] — TCP 연결이 맺어지고 끊어지는 과정
3. [[lessons/03-http-basics]] — HTTP라는 약속
   - 3A. [[lessons/03a-urls-and-http-details]] — URL과 HTTP를 조금 더 자세히
4. [[lessons/04-poll]] — 기다리지 않는 서버와 poll
   - 4A. [[lessons/04a-cpp98-basics]] — 이 코드를 읽기 위한 C++98 기초
5. [[lessons/05-startup]] — 서버가 켜질 때
6. [[lessons/06-config-parsing]] — 설정 파일 읽기
7. [[lessons/07-event-loop]] — 이벤트 루프
8. [[lessons/08-connection]] — 연결 하나의 일생
9. [[lessons/09-request-parser]] — 요청 해석기
10. [[lessons/10-routing]] — 길 찾기 (라우팅)
11. [[lessons/11-response]] — 응답 만들고 보내기
12. [[lessons/12-upload-delete]] — 업로드와 삭제
13. [[lessons/13-cgi]] — CGI
14. [[lessons/14-resilience]] — 절대 죽지 않기
15. [[lessons/15-defense-qa]] — 평가 예상 질문
16. [[lessons/16-glossary]] — 용어 사전

추천: 1장 → 2·3·4장(기초) → 5장부터 코드 순서대로. 2A·2B·3A·4A는 기초를 더 채우는 보충 장이다(2026-10-29 추가, 코드 기준 커밋 `4db9510`). 그 장의 개념이 처음이면 본 장 다음에 읽는다. 평가 직전에는 15장만 다시 본다.

더 깊이: [[analysis/design]](클래스 설계), [[analysis/design-decisions]](사용자 결정), [[analysis/test-plan]](요구사항별 테스트), [[analysis/mock-evaluation]](모의 평가), 그리고 각 concept 페이지.
