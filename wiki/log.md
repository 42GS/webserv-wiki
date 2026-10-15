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

## [2026-10-15] ingest | siege 매뉴얼 (siege.pod)
- 생성: raw/siege.pod (원문 그대로, 커밋 9c240ec), sources/siege
- 갱신: concepts/testing (siege 절: 평가 조건, 옵션표, Availability의 의미, keep-alive), concepts/resilience (99.5% 기준의 실체), concepts/connection-management (keep-alive 미확인 갱신), overview, index, source-wishlist (siegerc.in 추가)
- 해소: -b 의미 (raw/siege.pod:199-202), Availability 정의 (raw/siege.pod:373-378)
- 메모: Availability 계산식 문장은 원문 표현이 앞 문장과 맞지 않아 판단으로 표시. keep-alive는 siegerc.in으로 넘김

## [2026-10-15] ingest | siege 기본 설정 템플릿 (siegerc.in)
- 생성: raw/siegerc.in (원문 그대로, 커밋 9d9c08f), sources/siegerc
- 갱신: concepts/testing (기본 설정표, 서버 구현에 주는 결론), concepts/connection-management (keep-alive 해소), concepts/resilience, overview, index, source-wishlist
- 해소: siege 기본 keep-alive 여부 → connection = close (raw/siegerc.in:268). 단 템플릿이라 설치본과 같은지는 미확인
- 모순: delay 기본값 매뉴얼 0.5초 vs 템플릿 0.0

## [2026-10-15] ingest | POSIX _Exit() — Consequences of Process Termination
- 생성: raw/posix-exit.md (HTML → markdown 변환, verify_md PASS), raw/posix-exit.source.html (원본), sources/posix-exit
- 갱신: concepts/cgi (좀비 해소, fd 닫힘과 EOF, 손자 프로세스, execve 실패 시 종료), concepts/resilience (종료 시 CGI 자식 정리), analysis/subject-vs-evaluation (1.4를 허용 함수 목록 범위로 확장: <ctime>, exit), overview, index, source-wishlist
- 해소: 회수하지 않은 자식은 좀비로 남음 (raw/posix-exit.md:58-64)
- 메모: exit/_exit가 허용 함수 목록에 없음을 subject:113에서 확인

## [2026-10-15] ingest | NGINX ngx_http_index_module
- 생성: raw/nginx-index-module.md (HTML → markdown 변환, verify_md PASS), raw/nginx-index-module.source.html (원본), sources/nginx-index-module
- 갱신: concepts/configuration-file (지시자 대응표 index 행, index와 CGI 근거), overview, index, source-wishlist
- 남음: index 파일이 없을 때의 응답, 끝에 `/`가 없는 디렉토리 요청 → autoindex 모듈·NGINX 실측

## [2026-10-15] ingest | NGINX ngx_http_autoindex_module
- 생성: raw/nginx-autoindex-module.md (HTML → markdown 변환, verify_md PASS), raw/nginx-autoindex-module.source.html (원본), sources/nginx-autoindex-module
- 갱신: concepts/configuration-file ("디렉토리 요청 처리 순서" 절, 지시자 대응표 리스팅 행), concepts/status-codes (403 판단 근거 보강), analysis/subject-vs-evaluation (1.4에 리스팅 시간 표시), overview, index, source-wishlist
- 해소: index 파일이 없으면 보통 autoindex로 넘어감 (raw/nginx-autoindex-module.md:12)
- 남음: autoindex off + index 없음의 응답 코드, `/` 없는 디렉토리 요청 → NGINX 실측

## [2026-10-15] lint | 전체 점검
- 기계 검사: 깨진 링크 0, 인용 범위 0, 고아 페이지 0, 표 칸 수 0 (직전 ingest에서 1건 수정), frontmatter `sources` 누락 16건 → 자동 보완
- 오래된 서술: concepts/status-codes의 "NGINX 문서로 확인"을 실측 대상으로 정정
- 목록 동기화: analysis "남은 미확인"에 1.8·1.9 추가, 1.5 상태 갱신, 해석 질문과 실측 항목 구분. overview 실측 목록에 "리스팅 off + index 없음" 추가
- 공백: 파일 업로드(필수 기능)가 4줄, multipart 0줄. 쿠키·세션(보너스) 각 1줄
- 갱신: CLAUDE.md Lint 절에 표 칸 수, frontmatter, 미확인 목록 동기화, 기능별 공백 점검 추가

## [2026-10-15] ingest | RFC 7578 — multipart/form-data
- 생성: raw/rfc7578.txt (원문 그대로), sources/rfc7578, concepts/file-upload
- 갱신: concepts/security (filename, 실행 가능한 업로드), concepts/configuration-file·http-features·status-codes (file-upload 연결), overview, index, source-wishlist (P2→P1 승격 후 체크, RFC 2046 추가)
- 메모: lint에서 드러난 업로드 공백을 채움. 마지막 구분자 문법은 RFC 2046 소관이라 미확인

## [2026-10-15] ingest | RFC 2046 — MIME Media Types (5.1 Multipart)
- 생성: raw/rfc2046.txt (원문 그대로), sources/rfc2046 (5.1절만 다룸)
- 갱신: concepts/file-upload ("파싱 규칙" 표, 파일 끝 CRLF 경고, part 헤더 문자 판단, 처리 순서 3단계 구체화), sources/rfc7578, overview, index, source-wishlist
- 해소: 마지막 구분자 문법 `--boundary--` (raw/rfc2046.txt:1095-1101, 1251)

## [2026-10-15] schema | NGINX 실측 4건 정리
- 닫음 (RFC 기준 확정): Host 없는 HTTP/1.1 → 400 (raw/rfc9112.txt:445-448), 막힌 메서드 → 405 + Allow (raw/rfc9110.txt:7603-7607)
- 판단 확정, 실측은 선택으로 내림: 끝에 `/`가 없는 디렉토리 요청 → 301 (근거: NGINX 유사 동작 raw/nginx-core-module.md:1115, 상대 링크 해석은 RFC 3986 미확인), 리스팅 off + index 없음 → 403
- 갱신: source-wishlist 4-1, concepts/configuration-file·request-parsing·status-codes, overview, sources/nginx-core-module·nginx-index-module·nginx-autoindex-module

## [2026-10-15] ingest | RFC 3986 — URI Generic Syntax
- 생성: raw/rfc3986.txt (원문 그대로), sources/rfc3986
- 갱신: concepts/security (1절을 "경로 정규화 절차" 8단계로 재작성, NGINX와 순서 차이), concepts/configuration-file (301 판단 근거), concepts/request-parsing (query 분리 후 디코딩), overview, index, source-wishlist
- 해소: `%2e%2e` 디코딩 규칙 (raw/rfc3986.txt:735-743), 상대 링크 해석으로 본 301 근거 (raw/rfc3986.txt:1799-1803, 1640-1645)

## [2026-10-15] ingest | NGINX ngx_http_rewrite_module
- 생성: raw/nginx-rewrite-module.md (HTML → markdown 변환, verify_md PASS), raw/nginx-rewrite-module.source.html (원본), sources/nginx-rewrite-module
- 갱신: concepts/configuration-file (지시자 대응표 마지막 빈칸, `return` 형식과 상대 Location 판단), concepts/resilience (내부 리다이렉트 반복 상한), concepts/cgi (local redirect 연결), overview, index, source-wishlist
- 메모: NGINX 지시자 대응표의 빈칸이 모두 채워짐. rewrite는 정규식이라 과제 범위 밖

## [2026-10-15] schema | 전처리 도구 extract_div.py 추가
- 생성: tools/extract_div.py (id로 지정한 div만 추출, 사용자 댓글 등 제외)
- 갱신: CLAUDE.md 도구 목록
- 검증: php.net 페이지에서 일부러 공백을 지운 사본이 FAIL하는 것을 확인

## [2026-10-15] ingest | PHP 매뉴얼 — cgi.force_redirect, core php.ini (CGI)
- 생성: raw/php-cgi-force-redirect.md, raw/php-ini-core.md (HTML → markdown, extract_div → verify_md PASS), 각 .source.html, sources/php-cgi-force-redirect, sources/php-ini-core
- 갱신: concepts/cgi ("php-cgi가 추가로 요구하는 변수" 절), overview (열린 질문에서 제거), index, source-wishlist
- 해소: php-cgi 추가 변수 → REDIRECT_STATUS (force_redirect 기본 켜짐), SCRIPT_FILENAME
- 남음: REDIRECT_STATUS 값의 조건, php-cgi가 스크립트를 찾는 변수, 평가 PC의 php.ini 값
- 메모: 동작 페이지와 기본값 페이지가 짝이라 한 ingest로 묶음. 사용자 댓글은 비공식이라 제외

## [2026-10-15] ingest | RFC 6265 — HTTP State Management Mechanism
- 생성: raw/rfc6265.txt (원문 그대로), sources/rfc6265
- 갱신: concepts/bonus ("쿠키와 세션" 절 신설), concepts/cgi (Set-Cookie 여러 줄 전달), concepts/security (6절 세션), analysis/subject-vs-evaluation (1.10 /dev/urandom), overview, index, source-wishlist
- 메모: lint에서 1줄이던 쿠키·세션 공백을 채움. 같은 이름 헤더 여러 개를 담는 응답 구조가 필요

## [2026-10-15] lint | 전체 점검 (2차)
- 도구: tools/lint_wiki.py 추가. 일부러 깨진 링크·범위 밖 인용·표 칸 수 오류를 넣은 사본에서 3건 모두 검출 확인
- 기계 검사: 44개 페이지, 문제 0건
- 미확인 24곳 대조: 이미 해소됐는데 남은 표시 없음
- 수정: analysis 1.9·1.10 절 순서 뒤바뀜 정정. overview 열린 질문에 업로드·쿠키 설계 질문과 1.4 범위(리스팅 시간) 추가
- 결정 일관성: 411, readiness당 I/O 1회, 502·504, 403, Date, HEAD, SIGPIPE를 페이지 간 대조 → 일치
- 미결 판단: root 밖 경로의 응답 코드(403 또는 404)
- 기능별 언급: 업로드 16, 쿠키 13, 세션 12 (1차 lint 때 4·1·1). 가장 적은 것은 에러 페이지 6

## [2026-10-15] ingest | POSIX fcntl()
- 생성: raw/posix-fcntl.md (HTML → markdown 변환, verify_md PASS), raw/posix-fcntl.source.html (원본), sources/posix-fcntl
- 갱신: concepts/io-multiplexing (fcntl 근거), concepts/cgi (자식에서 필요 없는 fd 닫기), analysis/subject-vs-evaluation (1.11 fcntl 허용 목록), overview, index, source-wishlist
- 새 쟁점: F_GETFL 없이 F_SETFL만 가능, FD_CLOEXEC는 F_SETFD가 필요한데 허용 목록에 없음

## [2026-10-15] ingest | IANA HTTP Status Code Registry
- 생성: raw/iana-http-status-codes.txt (IANA txt 형식 그대로, 2025-09-15 갱신본), sources/iana-http-status-codes
- 갱신: concepts/status-codes ("reason phrase" 표, 431 행), overview, index, source-wishlist (RFC 6585 추가)
- 메모: reason phrase 표의 각 행은 스크립트로 IANA 원문 줄과 대조

## [2026-10-15] ingest | NGINX Server names
- 생성: raw/nginx-server-names.md (HTML → markdown 변환, verify_md PASS), raw/nginx-server-names.source.html (원본), sources/nginx-server-names
- 갱신: concepts/configuration-file ("이름 매칭 규칙", server가 정해지는 시점), overview, index, source-wishlist
- 메모: 대소문자 무시는 RFC 9110 근거, 포트 제거·정확한 이름만·헤더 상한 포트 단위는 판단

## [2026-10-15] ingest | RFC 1945 HTTP/1.0
- 생성: raw/rfc1945.txt (원문 그대로), sources/rfc1945
- 갱신: analysis/subject-vs-evaluation (1.6 응답 버전·DELETE 부록·0.9), concepts/request-parsing (0.9 → 400, 1.0 POST Content-Length 없으면 400), concepts/security (12.5), concepts/connection-management, concepts/status-codes, overview, index, source-wishlist
- 메모: 응답 버전 HTTP/1.1, 0.9 미지원은 판단. 제안 단계에서 적은 줄 번호 일부가 틀려 반영 전 grep으로 다시 찾음

## [2026-10-15] query | 멀티플렉서 결정: poll()
- 결정: 개발 macOS, 평가 Ubuntu → 두 OS 공통인 POSIX `poll()` 사용 (사용자 결정)
- 갱신: concepts/io-multiplexing (결정 콜아웃, Ubuntu에서 fcntl "For macOS only" 쟁점), overview (판단·열린 질문), source-wishlist (epoll·kqueue 받지 않음 `[-]`)

## [2026-10-15] ingest | RFC 6585 Additional HTTP Status Codes
- 생성: raw/rfc6585.txt (원문 그대로), sources/rfc6585
- 갱신: concepts/status-codes (헤더 상한 초과 → 431 확정, 미확인 해소), concepts/request-parsing (RFC 9110 5.4 MUST), concepts/security, sources/iana-http-status-codes, overview, index, source-wishlist
- 메모: 431 선택은 판단 (NGINX는 400)

## [2026-10-15] schema | extract_div.py 태그 인자, verify_md.py 굵게 표시 처리
- 갱신: tools/extract_div.py (선택 인자 tag, 기본 div — peps.python.org의 `section#pep-content`용), tools/verify_md.py (짝을 이룬 `**…**`만 변환기 표시로 제거, 짝 없는 `**`는 원문 글자로 유지), CLAUDE.md 도구 설명
- 계기: PEP 594 표의 각주 표시 `(2.0**)`가 검증에서 지워져 거짓 FAIL
- 검증: php 페이지 2개는 extract_div 결과가 수정 전과 바이트 단위로 같음. 기존 HTML 변환본 16개 모두 수정 전·후 PASS. 원문 `**`를 지운 사본이 이제 FAIL (수정 전에는 통과했을 경우)

## [2026-10-15] ingest | PEP 594 (Python cgi 모듈 제거)
- 생성: raw/pep-0594.md (HTML → markdown, extract_div section → verify_md PASS), raw/pep-0594.source.html (원본), sources/pep-0594
- 갱신: concepts/cgi (6절 Python 테스트 스크립트 작성), concepts/testing, overview, index, source-wishlist
- 새 미확인: 평가 Ubuntu의 Python 버전 (`cgi`를 쓰지 않으면 결론에 영향 없음)
- 수정: analysis/subject-vs-evaluation 6절에 Ubuntu에서의 `fcntl()` 허용 질문 추가 (멀티플렉서 결정 때 overview에만 넣고 빠뜨림)

## [2026-10-15] query | wishlist 정리: tester 자료 제외
- 결정: 평가 첨부 `tester`, `cgi_tester` 사용법은 받지 않음 (사용자 결정) → source-wishlist `[-]`

## [2026-10-15] ingest | OS 실측: bind, pipe poll (macOS·Ubuntu Docker)
- 생성: raw/os-observed-bind.md, raw/os-observed-pipe-poll.md (소스·명령·출력 그대로), sources/os-observed-bind, sources/os-observed-pipe-poll
- 갱신: concepts/cgi (입력·출력 pipe, 미확인 해소), concepts/io-multiplexing (OS 차이), concepts/configuration-file (SO_REUSEADDR, 0.0.0.0 겹침 거부, 미확인 해소), sources/posix-bind, analysis/subject-vs-evaluation (1.12 macOS vs POSIX), overview, index, source-wishlist 5-1
- 메모: Ubuntu는 OrbStack 커널 7.0.14 컨테이너 기준(평가 머신 커널 아님). 첫 측정은 테스트 코드가 소켓을 닫지 않는 버그로 결과 1건이 틀려 고친 뒤 재측정

## [2026-10-15] ingest | NGINX 실측: 디렉토리 요청과 `..` 경로
- 생성: raw/nginx-observed-directory.md (nginx/1.30.6 Docker, 설정·명령·응답·로그 그대로), sources/nginx-observed-directory
- 갱신: concepts/configuration-file (301·403 실측 근거, Location 형식 차이), concepts/security (6단계: 루트 위 `..` → 400), concepts/status-codes (400 행, 심볼릭 링크 403 행), overview, index, source-wishlist 4-1
- 결정: root 위로 올라가는 `..` → 400 + 연결 닫기 (사용자 결정, NGINX와 같음). 미결이던 403/404 판단 해소
- 메모: 정규화 뒤 최종 경로가 root 밖(심볼릭 링크)인 경우는 403으로 판단 (NGINX 미측정)
- 수정: sources/nginx-observed-directory 인용 줄 105 → 106 (빈 줄을 가리킴, 커밋 후 대조에서 발견)

## [2026-10-15] schema | 인용 검사 강화: 빈 줄 검사, cite_show.py, 커밋 전 순서
- 계기: 정기 lint에도 인용 불일치가 나옴. lint는 줄 번호가 파일 범위 안인지만 봐서, 범위 안의 엉뚱한 줄(빈 줄·다른 줄)과 뜻 차이, 다른 페이지 반영 누락을 못 잡음
- 생성: tools/cite_show.py (git diff 기준 새 인용의 원문 줄 출력)
- 갱신: tools/lint_wiki.py (인용 범위의 첫 줄·끝 줄이 빈 줄이면 오류), CLAUDE.md (7단계를 커밋 전 검사 3단계로: lint → cite_show 대조 → 영향 범위 grep)
- 새 검사로 기존 위키에서 찾은 빈 줄 인용 6건 수정 (모두 이번 세션 작성분): rfc9110 1567-1572→1568-1572, 1567-1570→1568-1570(2곳), rfc6585 7-12→7-11, rfc1945 3185-3191→3185-3199(2곳, 문장이 다음 페이지 3199줄에서 끝남)

## [2026-10-15] lint | 기존 인용 전수 대조
- 범위: 위키 전체 인용 1,376건을 `tools/cite_show.py --all`로 원문과 하나씩 대조 (sources → concepts → analysis·overview·wishlist·log 순)
- 주장과 근거가 맞지 않던 것 (내용 수정):
  - concepts/bonus, analysis/subject-vs-evaluation: "세션 식별자는 추측하기 어려워야"에 근거가 없음 → **판단** 표시
  - concepts/bonus: `HTTP_COOKIE`를 "넘겨야 한다"의 근거가 이름 규칙(rfc3875 1038-1042)뿐 → subject.md:178을 근거로, RFC 3875는 모든 헤더를 넘길 의무가 없음(1051-1052)도 적음
  - concepts/connection-management: "recv 0 = 상대 종료"의 근거가 평가표뿐 → posix-recv.md:72 추가
  - concepts/resilience, concepts/testing: siege `timeout`을 "30초 안에 응답 없으면 실패"로 씀 → 원문은 "socket connection timeouts". 응답 대기에도 걸리는지는 **미확인**, source-wishlist 6절에 siege `src/sock.c` 추가
  - concepts/io-multiplexing: 미확인(epoll·kqueue OS 전용)을 poll 결정의 근거로 씀 → 근거에서 빼고, 양쪽 OS 동작은 pipe/poll 실측으로 인용
  - concepts/configuration-file: "양쪽 OS 모두 EADDRINUSE"에 Ubuntu 줄만 인용 → macOS 줄(os-observed-bind 196) 추가
- 보완: sources/pep-0594 (머리말의 `div#content`는 extract_div.py가 감싼 요소), concepts/resilience (poll -1 근거 줄 명시)
- 문장 중간에서 끊긴 범위 11건을 문장 끝까지 넓힘: rfc2046 934-1306, rfc1945 2809-2823, rfc9110 4050-4055·8563-8570·7492-7495·7413-7416·4724-4726, rfc9112 1760-1767·437-438, rfc3986 1816-1844, rfc3875 1030-1031
- 메모: 근거가 되는 절이 범위 안에서 끝나는 인용은 다음 문장이 같은 줄에서 시작해도 그대로 두었다. log의 기존 항목 인용 25건은 모두 맞았다
- 도구: tools/cite_show.py에 `--all PAGE...` 추가 (6ec5419)

## [2026-10-15] schema | 인용·lint 검사를 직접 읽기로 전환
- 계기: 사용자 지시 — tools의 검사 스크립트는 신뢰도가 낮다. 스크립트 없이 직접 읽고 규칙과 대조한다
- 갱신: CLAUDE.md (ingest 3단계에 "인용마다 즉시 원문 대조", 7단계를 직접 읽기로, "인용 대조 기준" 절 신설, Lint 절에서 lint_wiki.py·cite_show.py 사용 제거)
- 메모: tools/lint_wiki.py, tools/cite_show.py 파일은 남아 있지만 작업 흐름에서 쓰지 않는다. HTML 변환 도구(nginx2md·posix_wrap·extract_div·verify_md)는 ingest용이라 그대로 둔다

## [2026-10-15] lint | 직접 읽기 점검 (스크립트 없이)
- 방법: 페이지마다 위키 문장과 인용한 raw 구간을 직접 열어 "인용 대조 기준"(CLAUDE.md)으로 비교. 검색은 위치 찾기에만 썼다
- 내용 오류: Host 400 규칙의 적용 범위 — Host가 없을 때만 HTTP/1.1 한정이고, 중복·잘못된 값은 모든 버전에 400 (request-parsing, status-codes, sources/rfc9112)
- 근거 없는 결론: NGINX 정규화 순서와 "`%2F`가 구분자가 된다" — 문서는 항목만 나열 → **미확인**, wishlist 4-1에 실측 후보 추가 (security, configuration-file)
- 원문보다 강한 주장: poll 뒤 I/O가 막히지 않는다(POSIX는 상태가 바뀔 수 있다고 함), POLLHUP "연결 끊김", 평가자 수정 "금지"(합의 조건), tester 의무 없음(조건부), 세션 식별자 방식(설명일 뿐), 4096바이트(SHOULD), lingering_close on(휴리스틱), 3xx 모두 Location(304 제외·308 누락), "평가는 앞 단계에서 걸리면 끝"(원문은 코드 질의 단계만), HEAD를 "테스트하지 않는다", cgi `언제든 중단`(에러 상황), `SCRIPT_FILENAME` 권고 대상(스크립트), PEP 594 "typically"
- 오래된 주장: virtual host "평가표와 충돌", NGINX 301·403 "선택 실측"(이미 측정), wishlist를 가리키던 ingest 완료 문서(rfc9112, posix-exit, siegerc), wishlist 4-1 머리말, "Obsidian Web Clipper"
- 판단 표시 누락: 추론 문장 10여 곳에 **판단** 표시
- 인용 범위: 문장 시작·끝이 빠진 범위를 문장 단위로 (rfc9110 3799-3804 등, rfc9112 430-432·807-809, rfc3875 736-741·1197-1199·1615-1619, rfc3986 647-652·1950-1954, rfc7578 189-193·197-201, rfc2046 945-959, rfc1945 1187-1190, rfc6265 1467-1472)
- 표기 오류: rfc3986 7.2절 오기재, rfc6585 7.3절 이름, server_names Optimization 시작 줄, "아래 server 선택 절"(위에 있음)
- 새 **미확인**: NGINX의 `%2F` 처리, RFC 9111이 RFC 7234를 대체했는지(머리말 미확인)
- 구조: 깨진 위키링크 없음, inbound 없는 페이지는 index·log뿐, frontmatter `sources` 누락 없음
- 메모: 점검 중 보조 출력 하나(zsh 단어 분리 오류로 전부 "누락"으로 나옴)가 틀려 버리고, 목록을 나란히 출력해 직접 비교했다

## [2026-10-15] schema | tools 삭제, HTML 변환을 pandoc 3.10으로
- 계기: 사용자 지시 — `tools/` 삭제, HTML→markdown은 라이브러리로
- 삭제: tools/ (cite_show.py, extract_div.py, lint_wiki.py, nginx2md.py, posix_wrap.py, verify_md.py)
- 생성: pandoc/only-id.lua (지정한 id의 요소만 남기는 pandoc Lua 필터, id가 없으면 오류 — 시험함)
- 갱신: CLAUDE.md (디렉토리 구조, "웹 문서 받기": pandoc 3.10 공식 Docker 이미지 digest 고정, 변환 검증은 직접 읽기), source-wishlist "받는 방법"
- 메모: 무료 변환기 4개(pandoc GPL-2.0, turndown MIT, markdownify MIT, html2text GPL-3.0, GitHub 저장소 정보로 확인) 중 사용자가 pandoc 선택. pandoc 3.11부터 `<code>` 없는 `<pre>`를 줄바꿈 텍스트+NBSP로 읽는 변경(#11810)을 3.1~3.12 이미지로 직접 실행해 확인하고 3.10으로 고정 (사용자 결정)
- 메모: 기존 raw HTML 변환본(nginx 6개, POSIX 8개, php 2개, PEP 594, 평가표 영어 원문)은 삭제한 스크립트로만 검증했다. 원본과 직접 읽어 대조하지 않았다 (**미확인**)

## [2026-10-15] lint | 기존 raw HTML 변환본 18개 직접 대조
- 방법: 각 `raw/<name>.source.html` 본문과 `raw/<name>.md`를 절 단위로 나란히 읽었다. raw는 고치지 않았다.
- 결과: 18개 모두 글자가 빠지거나 바뀐 곳 없음. 앞 항목의 "스크립트로만 검증 (**미확인**)" 해소.
- 구조 차이(글자는 같음): `<p>`·note가 든 목록 항목의 글머리표 없음, 중첩 목록 평탄화, 번호 목록이 글머리표로, 표가 줄 단위로 풀림, note 상자·강조 표시 없음, SYNOPSIS 한 줄로 합쳐짐. 파일별 내역은 각 source 페이지 "변환 검증" 콜아웃에 적었다.
- 영향: 위키 인용 가운데 목록 구조에 기대는 문장을 찾아 읽었다. sources/posix-exit의 `SIGCHLD` 전송 행이 "Otherwise" 조건(raw/posix-exit.md:58)을 빠뜨렸고 기본 동작 "무시"에 근거가 없었다 → 조건과 SA_NOCLDWAIT 구현 정의(54행), signal.h 표(raw/posix-signal-h.md:146-154, 304-306) 추가. concepts/cgi·resilience, sources/posix-waitpid의 해당 인용은 조건이 맞아 그대로 둠.
- 갱신: sources 18개 "변환 검증" 콜아웃 (evaluation-sheet-en은 새로 추가), sources/posix-exit.
- 메모: pep-0594 raw 머리말은 "`div#content`"라고 적었지만 실제 본문 요소는 `section#pep-content`다. raw는 고치지 않고 source 페이지에 적었다.
