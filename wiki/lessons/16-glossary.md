---
title: "레슨 16: 용어 사전"
type: lesson
sources: []
updated: 2026-10-25
---

# 레슨 16: 용어 사전

이전: [[lessons/15-defense-qa]] · 처음: [[lessons/00-guide]]

- **fd (파일 디스크립터)**: 열린 파일·소켓·pipe를 가리키는 작은 정수. 0·1·2는 표준 입력·출력·에러. → [[lessons/02-networking-basics]]
- **소켓 / listen 소켓**: 네트워크 통신의 끝점. listen 소켓은 새 연결을 기다리고, `accept`가 손님 전용 소켓을 만든다.
- **non-blocking**: 할 수 없으면 기다리지 않고 바로 돌아오는 방식.
- **poll / revents**: 여러 fd 중 준비된 것을 한 번에 알려 주는 시스템 호출 / 실제로 일어난 이벤트 비트. → [[lessons/04-poll]]
- **busy waiting**: 할 일이 없는데 계속 확인하며 CPU를 낭비하는 것.
- **이벤트 루프**: poll로 기다리고, 준비된 것을 처리하고, 다시 기다리기를 반복하는 서버의 중심. → [[lessons/07-event-loop]]
- **상태기계**: 지금 상태에 따라 할 일이 정해지고, 사건이 생기면 다음 상태로 옮겨 가는 구조 (`Connection`, `RequestParser`).
- **keep-alive / pipelining**: 한 연결로 여러 요청 / 응답을 기다리지 않고 요청을 연달아 보내기. → [[lessons/08-connection]]
- **chunked**: 본문을 크기가 적힌 조각으로 나눠 보내고 크기 0으로 끝내는 방식. → [[lessons/03-http-basics]]
- **request smuggling**: 본문 길이를 다르게 해석하게 만들어 요청 안에 다른 요청을 숨기는 공격.
- **response splitting**: 헤더 값에 줄바꿈을 넣어 응답을 둘로 쪼개는 공격. → [[lessons/11-response]]
- **정규화**: 경로의 `%XX`를 풀고 `.`·`..`·연속 `/`를 정리하는 것. → [[lessons/10-routing]]
- **location / root / alias**: URL 구역 규칙 / URI 전체를 붙일 디렉토리 / location 부분을 바꿔 끼울 디렉토리.
- **autoindex**: index 파일이 없을 때 디렉토리 목록을 HTML로 보여 주는 기능.
- **multipart/form-data, boundary**: 브라우저 파일 업로드 형식 / 각 부분을 나누는 구분 문자열. → [[lessons/12-upload-delete]]
- **CGI, 메타변수**: 서버가 외부 프로그램에 요청을 넘기는 규약(RFC 3875) / 그때 넘기는 환경 변수. → [[lessons/13-cgi]]
- **pipe, fork, dup2, execve**: 프로세스 사이의 관 / 자기 복제 / fd 바꿔 연결 / 다른 프로그램으로 변신.
- **좀비, waitpid, WNOHANG**: 끝났지만 부모가 확인하지 않은 프로세스 / 확인하기 / 기다리지 않고 확인만.
- **SIGPIPE, SIGINT, SIGKILL**: 끊긴 연결에 쓸 때 / Ctrl-C / 잡을 수 없는 강제 종료. → [[lessons/14-resilience]]
- **RFC, MUST·SHOULD·MAY**: 인터넷 표준 문서 / 반드시·되도록·해도 됨.
- **판단**: 이 위키에서, 원문이 직접 말하지 않아 근거를 보고 내린 결론.
