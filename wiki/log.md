# Log

## [2026-10-15] schema | 위키 초기 구성
- 생성: CLAUDE.md (스키마), wiki/index.md, wiki/log.md, wiki/overview.md

## [2026-10-15] ingest | webserv subject v24.0
- 생성: sources/subject, concepts/io-multiplexing, concepts/configuration-file, concepts/cgi, concepts/http-features, concepts/resilience, concepts/build-and-submission, concepts/bonus
- 메모: virtual host가 범위 밖이라는 문구(raw/subject.md:151) 기록

## [2026-10-15] ingest | webserv 평가표 (42 EvalHub 정리본)
- 생성: sources/evaluation-sheet, concepts/testing, analysis/subject-vs-evaluation
- 갱신: 모든 concepts 페이지에 평가표 근거 추가, overview
- 메모: 호스트네임 서버 테스트(raw/evaluation-sheet.md:65-68)가 subject와 모순. 정리본이라 원문 대조가 필요한 항목 3건 미확인으로 표시

## [2026-10-15] schema | git 저장소 초기화
- 생성: .git, .gitignore (.DS_Store, Obsidian workspace 파일 제외)

## [2026-10-15] query | 추가할 소스 목록
- 생성: source-wishlist (공식 소스 27건 — P1 9, P2 16, P3 2, 각 URL 접속 확인)
- 갱신: index
- 메모: siege 매뉴얼 joedog.org/siege-manual/ 404 → GitHub doc/siege.pod로 대체

## [2026-10-15] ingest | webserv 평가표 영어 원문 (42 EvalHub)
- 생성: raw/evaluation-sheet-en.md (+ 원본 HTML raw/evaluation-sheet-en.source.html), sources/evaluation-sheet-en
- 갱신: sources/evaluation-sheet (구버전 표시, superseded_by), concepts 전체 (평가표 인용을 영어 원문으로 교체), analysis/subject-vs-evaluation (재작성), overview, index, source-wishlist
- 메모: 정리본은 구버전으로 판단. virtual host 모순 해소(선택 사항), 미확인 3건 해소. 새 모순: EAGAIN까지 반복 허용(raw/evaluation-sheet-en.md:54) vs errno 금지(raw/subject.md:133). 전사는 원문 텍스트와 양방향 대조로 검증

## [2026-10-15] ingest | RFC 9110 — HTTP Semantics
- 생성: raw/rfc9110.txt (원문 그대로), sources/rfc9110, concepts/status-codes (상황별 표), concepts/security
- 갱신: concepts/http-features (메서드·헤더 규칙), concepts/configuration-file (405·리다이렉트·Host), concepts/cgi, concepts/resilience, analysis/subject-vs-evaluation (1.3 HEAD, 1.4 Date), overview, index, source-wishlist
- 메모: 과제 관련 절만 반영 (메서드, Host, 응답 헤더, status code, 보안 17.3~17.5). 캐시·조건부·Range·인증·협상은 범위 밖. 새 쟁점: HEAD MUST vs subject, Date MUST vs 허용 함수. CGI 실패를 502·504로 보는 것은 RFC 3875 확인 전까지 판단으로 표시

## [2026-10-15] ingest | RFC 9112 — HTTP/1.1
- 생성: raw/rfc9112.txt (원문 그대로), sources/rfc9112, concepts/request-parsing, concepts/connection-management
- 갱신: concepts/status-codes (411 행 정정, 400·414·501·408·413 근거 추가), concepts/security (splitting·smuggling), concepts/cgi (입출력 경계), analysis/subject-vs-evaluation (1.5 half-close, 1.6 HTTP 버전), overview, index, source-wishlist
- 정정: status-codes의 "body가 있는데 Content-Length 없음 (chunked도 아님) → 411"은 틀렸다. 그런 요청은 본문 길이 0이다 (raw/rfc9112.txt:980-981). 411은 chunked 거부용 MAY (raw/rfc9112.txt:999-1000)
- 메모: shutdown이 허용 함수에 없음을 subject:113에서 확인

## [2026-10-15] ingest | RFC 3875 — CGI Version 1.1
- 생성: raw/rfc3875.txt (원문 그대로), sources/rfc3875
- 갱신: concepts/cgi (재구성: 호출 절차, 메타변수 표, 응답 파싱, 실패 처리), concepts/status-codes (502·504 근거 보강·판단 표시 제거, CGI document·client redirect 행 추가), concepts/security (CGI `..` 처리 순서, 버퍼 길이, 스크립트 권한), analysis/subject-vs-evaluation (1.7 REMOTE_ADDR), overview, index, source-wishlist
- 해소: CGI 환경 변수 목록, 502·504 근거(서버는 application gateway, raw/rfc3875.txt:423), CGI Status 형식
- 메모: Informational RFC라 IESG 주의 노트가 있음 (raw/rfc3875.txt:27-34). inet_ntoa/inet_ntop가 허용 함수에 없음을 subject:113에서 확인

## [2026-10-15] ingest | NGINX ngx_http_core_module
- 생성: raw/nginx-core-module.md (HTML → markdown 변환), raw/nginx-core-module.source.html (원본), sources/nginx-core-module
- 갱신: concepts/configuration-file (root=alias 방식 확인, location 매칭, NGINX 지시자 대응표, default server), concepts/connection-management (타임아웃 4종, lingering close), concepts/status-codes (408·414·400 NGINX 기준), concepts/security (URI 정규화 순서), analysis/subject-vs-evaluation (1.5 보강), overview, index, source-wishlist (NGINX 실측 절 추가)
- 해소: root/alias 미확인 (subject 예시는 alias 방식)
- 검증: 변환기와 별개로 정규식 태그 제거로 HTML 텍스트 추출 → 공백 제외 55,481자 일치, 단어 diff 153건은 모두 태그 경계 분리
- 메모: 정적 파일 모듈 문서 없음(404), 로컬 NGINX 없음 → 디렉토리 301·limit_except 코드는 실측 항목으로 이관

## [2026-10-15] ingest | NGINX — How nginx processes a request
- 생성: raw/nginx-request-processing.md (HTML → markdown 변환), raw/nginx-request-processing.source.html (원본), sources/nginx-request-processing
- 갱신: concepts/configuration-file (server 선택 2단계, location은 query 제외, index 내부 리다이렉트와 CGI), concepts/request-parsing (Host 없을 때 HTTP/1.1·1.0 구분), overview, index, source-wishlist (실측 항목에 Host 없는 HTTP/1.1 요청 추가)
- 해소: Host 불일치·부재 시 default server 사용 (raw/nginx-request-processing.md:34)
- 검증: 공백 제외 5,515자 일치, 단어 diff 3건은 태그 경계 분리

## [2026-10-15] ingest | POSIX poll()
- 생성: raw/posix-poll.md (HTML → markdown 변환, 본문 범위 전처리), raw/posix-poll.source.html (원본), sources/posix-poll
- 갱신: concepts/io-multiplexing ("poll() 동작" 절: revents 처리표, POLLOUT 관리, 타임아웃·음수 fd), concepts/cgi (출력 pipe POLLHUP, 입력 pipe POLLERR), analysis/subject-vs-evaluation (1.8 poll 실패 errno), overview, index, source-wishlist
- 검증: 공백 제외 11,504자 일치, 단어 diff 78건은 태그 경계 분리
- 도구: opengroup 페이지용 본문 범위 전처리 스크립트 추가 (스크래치패드 tools/posix_wrap.py)

## [2026-10-15] ingest | POSIX <signal.h>
- 생성: raw/posix-signal-h.md (HTML → markdown 변환), raw/posix-signal-h.source.html (원본), sources/posix-signal-h
- 갱신: concepts/resilience ("시그널 처리" 절, SIGINT와 누수 검사), concepts/cgi (타임아웃 시 SIGKILL), overview, index, source-wishlist
- 해소: SIGPIPE 기본 동작 = 비정상 종료 (raw/posix-signal-h.md:192-196, 296-298)
- 남음: 소켓 send에서의 SIGPIPE는 send() 문서로 확인
- 검증: 공백 제외 15,720자 일치, 단어 diff 90건 중 3건은 SEE ALSO 정렬 차이로 직접 확인

## [2026-10-15] ingest | POSIX send(), recv()
- 생성: raw/posix-send.md, raw/posix-recv.md (HTML → markdown 변환), 각 .source.html (원본), sources/posix-send, sources/posix-recv
- 갱신: concepts/io-multiplexing ("recv·send 반환값 처리" 절, 1회 1 I/O가 errno 없이 동작하는 근거), concepts/resilience (소켓 SIGPIPE, MSG_NOSIGNAL 대안), concepts/request-parsing (스트림 경계 근거), overview, index, source-wishlist
- 해소: 소켓 send에서도 SIGPIPE 발생 (raw/posix-send.md:118-120), recv 반환값 0·-1의 의미 (raw/posix-recv.md:72)
- 메모: source-wishlist의 P1 항목 전부 완료
- 검증: send 공백 제외 4,275자, recv 4,187자 일치. 단어 diff는 모두 태그 경계 분리

## [2026-10-15] schema | 초기 커밋
- 커밋 1626315 (main, 49개 파일). 전역 ~/.gitignore의 `**/.gitignore` 규칙 때문에 저장소 .gitignore는 커밋에서 빠짐

## [2026-10-15] ingest | POSIX wait(), waitpid()
- 생성: raw/posix-waitpid.md (HTML → markdown 변환), raw/posix-waitpid.source.html (원본), sources/posix-waitpid
- 갱신: concepts/cgi ("자식 회수" 절: 호출 형태, 반환값표, 상태 매크로, 주의), concepts/resilience (SIGCHLD를 SIG_IGN으로 두면 안 되는 근거), analysis/subject-vs-evaluation (1.9 waitpid 매크로), overview, index, source-wishlist (_Exit() 추가)
- 해소: WNOHANG 동작 (raw/posix-waitpid.md:56-58, 132)
- 정정: concepts/cgi에 근거 없이 사실로 적혀 있던 "회수하지 않으면 좀비가 쌓인다"를 미확인으로 바꿈
- 검증: 공백 제외 20,136자 일치, 단어 diff 178건은 태그 경계 분리

## [2026-10-15] schema | ingest 절차에 lint·커밋 단계 추가
- 갱신: CLAUDE.md Ingest 7단계(lint), 8단계(소스 하나마다 커밋)

## [2026-10-15] ingest | POSIX bind()
- 생성: raw/posix-bind.md (HTML → markdown 변환), raw/posix-bind.source.html (원본), sources/posix-bind
- 갱신: concepts/configuration-file ("bind() 기준 기대 동작" 표), concepts/resilience (시작 단계 실패), analysis/subject-vs-evaluation (1.8을 read/write 외 함수의 errno로 확장), overview, index, source-wishlist (5-1 OS 실측 절 추가)
- 해소: 같은 포트 중복 bind 실패 조건 EADDRINUSE (raw/posix-bind.md:66-68)
- 검증: 공백 제외 6,463자 일치, 단어 diff 24건은 태그 경계 분리

## [2026-10-15] schema | 변환 도구를 저장소로 이동, 검증기 강화
- 생성: tools/nginx2md.py, tools/posix_wrap.py, tools/verify_md.py
- 갱신: CLAUDE.md (디렉토리 구조, "웹 문서 받기" 절과 검증 기준)
- 정정: 이전 검증 방식(태그를 모두 공백으로 바꾼 뒤 비교)은 md에서 공백이 사라진 경우를 잡지 못했다. 블록 태그만 공백으로, 인라인 태그는 제거하도록 바꾸고 단어 목록 완전 일치로 검사한다. 일부러 공백을 지운 사본으로 FAIL을 확인했다
- 재검증: 기존 변환본 8개(nginx 2, posix 6) 모두 새 기준 PASS
