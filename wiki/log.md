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

## [2026-10-15] lint | 전체 직접 읽기 점검 (2회차)
- 방법: 모든 페이지(sources 35, concepts 13, analysis, overview, index, wishlist)를 읽고 인용마다 원문 줄을 다시 열어 대조했다. 인용 옆에 원문 줄을 띄워 주는 표시용 스크립트만 썼고 판정은 읽어서 했다.
- 원문보다 강한 주장 정정:
  - subject "you can" 문장을 지시로 씀: NGINX와 비교하라(186), `server` 섹션을 참고하라(161) → 해도 된다 (sources/nginx-core-module, nginx-observed-directory, source-wishlist, concepts/configuration-file).
  - 평가표의 질문을 요구로 씀: "단일 poll()/select()"(평가표 52, 정리본 47) → 하나만 쓰는지 질문.
  - posix-exit 70 "자식을 직접 종료하지 않음"을 "끝나지 않음"으로 씀 → SIGHUP 간접 종료 예외 보충 (sources/posix-exit, concepts/resilience, concepts/cgi).
  - NGINX location 매칭을 "가장 긴 prefix를 고른다"로 씀 → 정규식 검사 단계 보충 (sources/nginx-core-module, concepts/configuration-file, overview).
  - 444 "응답 없이 닫는다"는 request-processing 문서에 없음 → rewrite 모듈 113(응답 헤더 없이) 인용.
  - "평가는 -b라서 지연 없음" → availability 확인에 한정 (sources/siegerc, concepts/testing).
  - RFC 7578 "numerous" → "대부분" 과장 (concepts/file-upload); NGINX 400은 헤더 필드 하나가 버퍼보다 클 때로 한정 (concepts/status-codes); analysis 1.3 HEAD "평가에 영향 없음" → 임의 테스트 가능성.
- 빠진 조건·규범 수준 보충: php force_redirect "Apache에서만 시험"·"대부분의 웹 서버"·IIS 예외, posix-poll 171 "확인한 시점", POLLERR "기반 객체 상태" 조건, RFC 3875 9.8의 should와 대안(1801-1806), 작업 디렉토리 SHOULD, RFC 3986 must/should와 merge 첫 조건(1783-1785), RFC 9112 0.9 "ought to", chunk-ext·처리량 제한 "ought to", nginx-server-names 204의 SNI 조건.
- 판단 표시 추가: siege `connection = close` → 요청마다 새 연결(여러 페이지), CGI `Status` → 상태줄 코드, HTTP_COOKIE 전달, alias 비교, 리스팅 HTML, %XX 오류 400, execve 주입 회피, POLLOUT 관리, pipe-poll 모순의 "조건이 참" 근거(174), overview의 502/504·I/O 1번.
- 인용·표기 정정: 정리본 첨부 31-33 → 32-33, rfc1945 절 이름 2곳, "_" 문장 지시 대상 140 추가, rfc3875 Status 정의 1443-1445, cgi 표의 "1355-1357, 502 정의"가 502행 인용처럼 읽히던 표기, 측정일 인용(os-observed 3-4, nginx-observed 3), REMOTE_ADDR MUST 인용, RFC 7230 대체 관계(9110·9112가 일부씩).
- 출처 표시: siege·siegerc 커밋 정보는 받을 때 GitHub에서 본 값(raw에 없음), PHP 장 이름은 원본 HTML 메뉴.
- 구조: 깨진 위키링크 없음, inbound 없는 페이지는 index·log뿐, 인용한 raw는 모두 frontmatter `sources`에 있음, 표 칸 수 불일치 없음 (목록은 검색으로 뽑고 읽어서 확인).

## [2026-10-15] ingest | siege 소켓 코드 (src/sock.c)
- 생성: raw/siege-sock.c (원문 그대로, 커밋 e2a6bc9, 2023-12-06), sources/siege-sock
- 갱신: concepts/resilience·testing (응답 대기 timeout **미확인** → 원문 확인 + 판단), sources/siegerc, source-wishlist 6절(체크, 나머지 소스 항목 추가), index, overview
- 메모: `timeout`은 연결 직후와 `read()` 직전마다 하는 준비 검사의 대기 시간이다 (raw/siege-sock.c:360-362, raw/siege-sock.c:611-626). 그 검사가 읽기·쓰기 집합을 함께 보므로 응답 대기에는 실효가 없을 수 있다고 판단했다 (raw/siege-sock.c:370-374). 다른 소스 파일의 타이머, `O_NDELAY`와 `O_NONBLOCK`이 같은 값인지, 평가 PC의 siege 버전은 **미확인**.

## [2026-10-15] ingest | NGINX 실측: 경로의 `%2F`
- 생성: raw/nginx-observed-encoded-slash.md (설정·명령·curl 출력·NGINX 로그 그대로, nginx/1.30.6, 디렉토리 실측과 같은 이미지 digest), sources/nginx-observed-encoded-slash
- 갱신: concepts/security (콜아웃의 **미확인** 해소, 5단계를 사용자 결정으로), concepts/status-codes (`%2F` 400 행), source-wishlist 4-1 (마지막 항목 체크), overview, index
- 메모: NGINX는 `%2F`를 디코딩해 경로 구분자로 쓰고(`/a%2Fb.txt` → `location /a/`의 `a/b.txt`), 디코딩으로 생긴 `..`·연속 `/`도 정규화한다 (raw/nginx-observed-encoded-slash.md:100-111, raw/nginx-observed-encoded-slash.md:148, raw/nginx-observed-encoded-slash.md:170). RFC 3986의 "나눈 뒤 디코딩"과 반대 순서다. 사용자 결정(2026-10-15): 이 과제는 `%2F`를 400으로 거부하는 현행 판단을 유지한다. curl은 소문자 `%2f`를 `%2F`로 바꿔 보냈다 (로그 198).

## [2026-10-15] query | 설계 결정 정리
- 생성: analysis/design-decisions (사용자 결정 8건: 기존 3건 + 이번 5건)
- 사용자 결정 (2026-10-15): virtual host 미구현, HEAD 지원, index 파일이 CGI 확장자면 CGI로 실행, 업로드는 서버가 `multipart/form-data`만 저장, 쿠키·세션 보너스는 CGI 예제
- 갱신: concepts/configuration-file·http-features·file-upload·bonus·status-codes(415 행, IANA 이름), analysis/subject-vs-evaluation(1.3, 1.10, 6절), overview(현재 종합 판단, 열린 질문 5건 정리), index
- 메모: 업로드 라우트에 multipart가 아닌 본문이 오면 415로 거부한다 (판단, raw/rfc9110.txt:7738-7740). 세션을 CGI 예제로 하는 것이 평가표의 "웹 서버의 세션 시스템"(raw/evaluation-sheet-en.md:126)으로 인정되는지는 열린 질문으로 남겼다.

## [2026-10-15] ingest | PHP 소스 sapi/cgi/cgi_main.c
- 생성: raw/php-src-cgi_main.c (원문 그대로, PHP-8.3 브랜치 커밋 6d99ccc, 2024-09-26), sources/php-src-cgi-main
- 갱신: concepts/cgi ("php-cgi가 추가로 요구하는 변수" 표와 설명의 **미확인** 2건 해소), sources/php-cgi-force-redirect, source-wishlist 3절, index, overview
- 메모: php-cgi는 실행할 파일을 `SCRIPT_FILENAME`에서 찾고 없을 때만 `PATH_TRANSLATED`를 쓴다 (raw/php-src-cgi_main.c:1161-1170). `REDIRECT_URL`이 함께 있거나 `cgi.fix_pathinfo`가 꺼져 있으면 `PATH_TRANSLATED`가 실행 파일이 된다 (raw/php-src-cgi_main.c:1229-1240, raw/php-src-cgi_main.c:1424-1434). `REDIRECT_STATUS`는 변수가 있는지만 본다 (raw/php-src-cgi_main.c:1898). 태그 php-8.3.6 원본은 `HTTP_REDIRECT_STATUS`도 받지만, Ubuntu 24.04 패키지는 CVE-2024-8927 패치로 받지 않아 패치 뒤 브랜치 파일을 받았다. 평가 PC의 php-cgi 버전과 php.ini는 **미확인**.

## [2026-10-15] ingest | php-cgi 실측: 실행할 파일을 찾는 변수와 REDIRECT_STATUS
- 생성: raw/php-cgi-observed-env.md (Dockerfile·스크립트·php-cgi 출력 그대로, ubuntu:24.04 digest, php8.3-cgi 8.3.6-0ubuntu0.24.04.11), sources/php-cgi-observed-env
- 갱신: concepts/cgi (php-cgi 절에 실측 결과, 5절 종료 코드 판단에 404·403 예), sources/php-src-cgi-main (링크), index, overview
- 메모: 소스를 읽은 결과와 같았다. `REDIRECT_STATUS`는 `0`·빈 값도 통과, `HTTP_REDIRECT_STATUS`는 거부 (raw/php-cgi-observed-env.md:154-182). `SCRIPT_FILENAME`이 우선이고 `REDIRECT_URL`이나 `cgi.fix_pathinfo=0`이면 `PATH_TRANSLATED` 쪽이 실행됐다 (raw/php-cgi-observed-env.md:194-213). `REDIRECT_STATUS`가 없을 때 출력에 헤더가 없다는 점은 소스만 읽어서는 몰랐다 (raw/php-cgi-observed-env.md:142-152). 첫 시도에서 CGI 메타변수 없이 실행해 검사가 생략된 것을 보고, 서버가 넘기는 변수를 넣어 다시 측정했다.

## [2026-10-15] ingest | valgrind 실측: SIGINT로 끝난 프로세스의 누수 보고
- 생성: raw/valgrind-observed-sigint.md (Dockerfile·프로그램·스크립트·valgrind 출력 그대로, ubuntu:24.04 digest, valgrind-3.22.0), sources/valgrind-observed-sigint
- 갱신: concepts/resilience ("SIGINT·SIGTERM과 누수 검사"의 valgrind **미확인** 해소), concepts/testing (링크), index, overview
- 메모: SIGINT 기본 동작으로 끝나면 definitely lost 0, 할당 전부가 still reachable (raw/valgrind-observed-sigint.md:111-138). 핸들러를 두고 해제 없이 `main`에서 반환하면 definitely lost (raw/valgrind-observed-sigint.md:157-163). 모두 해제한 경우만 "All heap blocks were freed" (raw/valgrind-observed-sigint.md:212-215). 기존 판단(플래그 + 정리 후 종료) 유지. `leaks`·`e_fence`는 **미확인**. 첫 시도에서 비대화형 쉘의 백그라운드 작업으로 띄운 `default` 모드가 SIGINT에 끝나지 않아, valgrind를 포그라운드로 돌리고 보조 프로세스가 시그널을 보내게 바꿨다.

## [2026-10-15] ingest | Ubuntu 22.04 실측: 도구 버전, siege 설정, php-cgi·valgrind 재측정
- 사용자 확인 (2026-10-15): 평가 PC는 Ubuntu 22.04.
- 생성: raw/ubuntu2204-observed-tools.md (ubuntu:22.04 digest, apt 기본 패키지, 버전·`siege -C`·siege v4.0.7과 master diff·php-cgi·valgrind 출력 그대로), sources/ubuntu2204-observed-tools
- 갱신: concepts/cgi (php.ini 기본값, Python 버전 **미확인**을 22.04 기준으로 좁힘), concepts/testing (siege 설정 **미확인** → 22.04 실측 + 평가 PC 설정만 미확인), concepts/resilience, concepts/io-multiplexing·overview (평가 OS 22.04), sources/siege·siegerc·siege-sock (4.0.7과 차이), sources/php-ini-core·php-cgi-observed-env·php-src-cgi-main, index
- 메모: 22.04 apt 패키지는 php8.1-cgi 8.1.2, valgrind 3.18.1, Python 3.10.12(`import cgi` 가능), siege 4.0.7 (raw/ubuntu2204-observed-tools.md:84-93). php-cgi·valgrind 결과는 24.04와 같았다. siege 4.0.7의 `sock.c`는 이름 해석 부분만 master와 달라 기존 timeout 분석이 그대로 맞는다. 컨테이너 커널은 OrbStack 7.0.14라서 커널 동작은 22.04 기준으로 확인하지 못한다. 평가 PC가 기본 패키지·설정을 그대로 쓰는지는 **미확인**.

## [2026-10-15] ingest | siege 실측 (Ubuntu 22.04, siege 4.0.7)
- 생성: raw/siege-observed-ubuntu2204.md (테스트 서버 코드·스크립트·출력 그대로, ubuntu2204-observed-tools와 같은 이미지), sources/siege-observed-ubuntu2204
- 갱신: sources/siege-sock (`O_NDELAY` **미확인** 해소, 실제 동작 **미확인** → 실측), concepts/testing (`-b`·`-d` **미확인**, 부하 요청 `Connection: close` **미확인** 해소, timeout 행), concepts/resilience (timeout 행), source-wishlist 6절, overview, index
- 메모: glibc에서 `O_NDELAY`는 `O_NONBLOCK`과 같다 (raw/siege-observed-ubuntu2204.md:104-105). 응답 없는 서버에 대해 siege는 `timeout` 30초·5초 모두 150초 동안 끝나지 않았다 (raw/siege-observed-ubuntu2204.md:197-229). 부하 요청은 HTTP/1.1 + `Connection: close` (raw/siege-observed-ubuntu2204.md:140-161). `-b`가 `-d`보다 우선 (raw/siege-observed-ubuntu2204.md:164-194). `protocol` 줄 없는 설정 파일이면 HTTP/1.0으로 요청했다 (raw/siege-observed-ubuntu2204.md:239-240).

## [2026-10-16] ingest | macOS 실측: MSG_NOSIGNAL과 leaks -atExit의 SIGINT 종료 보고
- 생성: raw/macos-observed-sigpipe-leaks.md (SDK 헤더, 테스트 프로그램 3개, 명령, 출력 그대로), sources/macos-observed-sigpipe-leaks
- 갱신: concepts/resilience (macOS `MSG_NOSIGNAL` **미확인** 해소, `leaks` **미확인** 해소, `e_fence`만 남김), concepts/testing (도구 표), sources/valgrind-observed-sigint (측정 범위 노트), overview, index
- 메모: macOS SDK에 `MSG_NOSIGNAL`이 있고, 끊긴 TCP 연결에 `MSG_NOSIGNAL`·`SO_NOSIGPIPE`로 보내면 프로세스가 살고 `EPIPE`가 돌아왔다 (raw/macos-observed-sigpipe-leaks.md:51-53, raw/macos-observed-sigpipe-leaks.md:118-131). `leaks -atExit`는 SIGINT 기본 종료에서 아무것도 출력하지 않고 exit 0 (raw/macos-observed-sigpipe-leaks.md:224-226), 해제 없이 `main` 반환도 0 leaks (raw/macos-observed-sigpipe-leaks.md:254-256). 대조 실험에서는 누수를 보고했다 (raw/macos-observed-sigpipe-leaks.md:386-388). 기존 판단(플래그 + 정리 후 종료, SIGPIPE 무시) 유지.

## [2026-10-16] ingest | NGINX 1.30.6 소스: lingering close
- 생성: raw/nginx-src-ngx_http_request.c, raw/nginx-src-ngx_socket.h (`release-1.30.6` 태그 원본 그대로), sources/nginx-src-lingering-close
- 갱신: concepts/connection-management (NGINX `shutdown` **미확인** 해소), analysis/subject-vs-evaluation (1.5절, 남은 미확인 문구), overview (근거 소스, 열린 질문 문구), index
- 메모: NGINX는 lingering close에 들어갈 때 `shutdown(fd, SHUT_WR)`을 호출하고 (raw/nginx-src-ngx_http_request.c:3693-3698, raw/nginx-src-ngx_socket.h:15, raw/nginx-src-ngx_socket.h:66), 상대가 닫거나 시간이 다 될 때까지 읽어 버린다 (raw/nginx-src-ngx_http_request.c:3727-3752). 요청 종료 후 keep-alive가 가능하면 keep-alive가 먼저다 (raw/nginx-src-ngx_http_request.c:2960-2987). 과제는 `shutdown`을 쓸 수 없어 "읽고 버리다가 `close()`"만 따른다. 이것으로 충분한지는 **미확인**으로 남겼다.

## [2026-10-16] ingest | Electric Fence 실측 (Ubuntu 22.04)
- 생성: raw/efence-observed-ubuntu2204.md (패키지 문서 발췌, 테스트 프로그램 3개, 명령, 출력, `ldd` 그대로), sources/efence-observed-ubuntu2204
- 갱신: concepts/resilience (`e_fence` **미확인** 해소), concepts/testing (도구 표), sources/valgrind-observed-sigint·macos-observed-sigpipe-leaks (측정 범위 노트), overview, index
- 메모: electric-fence 2.2.6은 누수를 보고하지 않았다. 포인터를 잃은 대조군도 보고 없음 (raw/efence-observed-ubuntu2204.md:351-361). 문서상 대상은 heap 경계 초과와 해제 후 접근이고 (raw/efence-observed-ubuntu2204.md:71-74), 1바이트 초과 쓰기가 segfault가 됐다 (raw/efence-observed-ubuntu2204.md:369-375). g++ `-lefence` 바이너리에는 libefence가 링크되지 않아 효과가 없었다 (raw/efence-observed-ubuntu2204.md:389-395). 원인은 **미확인**.

## [2026-10-16] ingest | 413 뒤 연결 종료 방식 실측 (Ubuntu 22.04, macOS)
- 생성: raw/close-after-413-observed.md (시험 서버·클라이언트 소스, 스크립트, 두 OS 출력 그대로), sources/close-after-413-observed
- 갱신: concepts/connection-management (모순 콜아웃에 실측과 버리기 상한), analysis/subject-vs-evaluation (1.5절 실측 추가, 6절 미확인 삭제), overview (종합 판단 보강, 열린 질문 삭제, 근거 소스), index
- 메모: 바로 `close()`하면 macOS에서 reset이 나고 curl 1회가 응답을 받지 못했다 (raw/close-after-413-observed.md:359-363, raw/close-after-413-observed.md:370-374). 읽고 버리다가 `close()`하면 두 OS 12/12 수신 (raw/close-after-413-observed.md:225-256, raw/close-after-413-observed.md:388-419). macOS에서는 버린 실행이 두 번 있었다(서버 기동 대기 부족, `timeout` 명령 없음). raw에 사유를 적었다. curl 응답 파일을 시도마다 지우지 않아 `body=` 값은 판정에 쓰지 않았다.

## [2026-10-16] query | 구현 순서 정리
- 생성: analysis/implementation-plan (모듈 구조, 단계 0~9, 단계별 완료 기준, 관련 concept 링크)
- 갱신: index, overview
- 메모: 사용자 요청 — 위키 조사가 구현 목적에 비해 깊어져 조사를 멈추고 구현 순서로 정리했다. 남은 미확인 중 코드에 영향 없는 것(x86_64 `O_NDELAY`, siege 나머지 소스)은 진행하지 않는다.

## [2026-10-16] query | 설계 (클래스·인터페이스)
- 생성: analysis/design (파일 배치, 모듈 책임·의존 방향, 설정 구조체, `IoHandler`/`EventLoop`, Connection 상태기계, `HeaderMap`/`RequestParser`/`Router`/`Response`/`CgiProcess` 인터페이스, 정적 파일 나눠 읽기, 에러 처리, 시그널, 상수)
- 갱신: analysis/implementation-plan (설계 링크), index, overview
- 메모: 사용자 선택 — 위키 analysis/에 클래스·인터페이스 수준까지. 모든 구조·값은 판단이다. 정할 것: 설정 문법 세부, 업로드 쓰기 방식, 상수 값, `Date` 헤더.

## [2026-10-16] query | 설계 수정 (설계 원칙 대조, NGINX 설정 문법)
- 갱신: analysis/design (원칙 대조 후 재작성: `RequestProcessor`·`ResponseStream`·`ChildReaper` 분리, 소유자 하나 원칙과 소유 관계 표, `IoRegistry`·`LoopObserver`·`CgiObserver` 인터페이스, `ListenContext`·`CgiContext`로 파라미터 묶음, `util/`·로그 모듈 제거, 3절 NGINX 문법·지시자 표·예시, 13절 원칙 대조와 의도한 예외), analysis/design-decisions (결정 9 NGINX 문법)
- 메모: 사용자 결정 — 설정은 NGINX 문법, 허용 메서드는 `limit_except METHOD ... { deny all; }` 형식(A). 첫 설계가 SRP(`Connection` 과다 책임), 소유권(같은 객체를 두 곳이 포인터로 보유), DIP(`EventLoop` 구체 의존), 파라미터 수에서 원칙을 어겼음을 사용자 질문으로 대조해 찾고 고쳤다. `root` 매핑 방식(NGINX `root` vs subject 예시의 `alias` 방식)은 사용자 결정 대기.

## [2026-10-16] query | root·alias 결정
- 갱신: analysis/design (3절 `root`·`alias` 행, `LocationConfig.alias`, 예시, 설정 오류 규칙, 7절 매핑 단계, 14절 항목 삭제), analysis/design-decisions (결정 9에 `limit_except`·`root`/`alias`), concepts/configuration-file (alias 콜아웃에 결정), overview
- 메모: 사용자 선택 (a) — NGINX 문법을 따르므로 `root`는 NGINX대로 URI 전체를 붙이고, subject 예시 매핑은 `alias`로 쓴다. 한 location에 둘 다 있으면 설정 오류(판단).

## [2026-10-16] query | 업로드 저장·상수·시각과 Date 결정
- 갱신: analysis/design (4절 `Clock`, `IoHandler::onFailure` 누락 보완, `EventLoop`가 바퀴마다 시계 갱신, 7절 업로드 한 번에 저장, 8절 `Date` 보냄, 상수 `kClockFile`, 14절 정리), analysis/design-decisions (결정 10), concepts/http-features (Date 콜아웃에 결정), analysis/subject-vs-evaluation (1.4절, 남은 미확인 문구), overview (열린 질문 문구)
- 메모: 사용자 결정 — 업로드는 단순한 쪽(본문을 모은 뒤 한 번에 저장), 상수는 평가 통과 수준이면 됨, Date는 평가자가 문제 삼을 수 없는 보수적 방향. 타임아웃에 쓰던 `time()`이 허용 함수 목록 밖임을 이때 발견해, 시계용 파일의 `stat` 수정 시각으로 시각을 얻고 RFC 9110 MUST대로 `Date`를 보내기로 했다. `write`가 수정 시각을 갱신하는지는 **미확인**(단계 2에서 두 OS 확인).

## [2026-10-16] ingest | 설계 확인 실측 3건 (파일 시계, 큰 본문 메모리, 자식 std::exit)
- 생성: raw/design-checks-observed.md (프로그램 3개, 명령, macOS·Ubuntu 22.04 출력 그대로), sources/design-checks-observed
- 갱신: analysis/design-decisions (결정 11 본문 상한 100MB, 결정 12 CGI 자식 `std::exit` + `access` 검사), analysis/design (3절 `client_max_body_size`, 7절 `reserve`, 9절 `fork` 전 검사·flush·`std::exit`, 11절 `bad_alloc` 한계, 상수), concepts/cgi, analysis/subject-vs-evaluation (1.4절, 남은 미확인 문구), overview, index
- 메모: 파일 수정 시각 시계는 두 OS에서 `time()`과 일치 (raw/design-checks-observed.md:60-80) → 결정 10의 **미확인** 해소. 메모리 고갈 시 `bad_alloc` 없이 `Killed` (raw/design-checks-observed.md:119-123). 자식 `std::exit`은 flush 안 된 부모 버퍼를 다시 출력 (raw/design-checks-observed.md:183-194). 사용자 결정: 상한 100MB, CGI 종료는 해석 A(`std::exit`) + `access` 보조 대책.

## [2026-10-16] query | 구현 단계 0·1 (webserv 저장소)
- 갱신: analysis/design (3절에 단계 1 구현 세부)
- 메모: 코드 저장소는 `webserv/`(별도 git, 위키 `.gitignore`에 추가). 단계 0 Makefile·README 틀, 단계 1 설정 파서(lexer → 구문 트리 → builder)와 단위 테스트 16개(`make test`). macOS·Ubuntu 22.04 빌드와 테스트 통과, 테스트 값을 일부러 틀리게 바꾸면 실패를 보고함을 확인.

## [2026-10-16] query | 구현 단계 2 (이벤트 루프와 고정 응답)
- 메모: webserv `6f48721`. `EventLoop`(poll 하나, 소유하지 않음), `Server`(Listener·Connection 소유), `Clock`(파일 mtime), `Signals`, `Listener`, 고정 200 응답 `Connection`. `ChildReaper`는 CGI 단계에서 만든다(YAGNI). Ubuntu 22.04 컨테이너, valgrind 아래에서 `siege -b -c 25 -t 20S` 92,279건 availability 100%, `-r 200` 5,000건 100%, SIGINT 뒤 "All heap blocks were freed"·열린 fd 3개(표준). macOS에서 두 포트 동시 50건 200, 같은 포트 두 번째 실행은 "Address already in use"로 종료 코드 1.

## [2026-10-16] query | 테스트 계획 수립과 기존 테스트 점검
- 생성: [[analysis/test-plan]] (요구사항 → 테스트 대응표, 0~2단계 상세, 3단계 이후 항목)
- 갱신: [[analysis/implementation-plan]] (테스트 계획 링크), [[index]] (test-plan 행, design-decisions 건수 8→12 정정)
- 메모: 사용자가 "테스트 계획 없이 테스트를 신뢰할 수 있나"를 물어 시작. webserv `4f27998`(프레임워크: `CHECK_EQ` 이중 평가, 예외가 전체 실행을 멈추던 문제), `d1761bd`(단위 테스트 빈칸 채움, `[0]`→`at()`), `4b68ef5`(통합 테스트 `tests/integration`, `make integration`). 단위 30개, 통합 18개(느린 3개, Linux 전용 1개 포함) Ubuntu 22.04 컨테이너에서 모두 통과. 줄마다 코드를 일부러 틀리게 바꿔 실패를 확인했다. `SIGPIPE` 무시 제거는 지금 테스트로 잡지 못해 4단계로 넘김. valgrind·siege 결과는 아직 커밋 메시지·log에만 있어 8단계에서 절차로 남긴다.

## [2026-10-16] schema | 구현 작업 때 위키 참고 규칙
- 갱신: `CLAUDE.md` 작업 흐름에 "구현 (`webserv/` 코드·테스트)" 절 추가
- 메모: 테스트 계획을 쓰면서 `concepts/io-multiplexing`·`concepts/resilience`·`sources/macos-observed-sigpipe-leaks`를 읽지 않아, 위키에 실측이 있는 SIGPIPE 동작을 판단으로 적고 2단계의 "`POLLOUT`은 보낼 데이터가 있을 때만" 요구를 계획에서 빠뜨렸다. 사용자 요청으로 작업 전 해당 범위 위키를 읽는 규칙을 추가했다.

## [2026-10-16] query | 테스트 계획 0~2단계 위키 대조 보완
- 갱신: [[analysis/test-plan]] (B-04~B-07, N-16~N-23 추가. C-11에 NGINX `listen` 형식 차이, N-07에 SIGPIPE 실측 인용), [[overview]] (열린 질문: 제출 파일 목록 밖 파일)
- 메모: 새 구현 규칙에 따라 `concepts/build-and-submission`, `concepts/configuration-file`, `concepts/io-multiplexing`, `concepts/resilience`, `concepts/connection-management`(타임아웃·종료), `sources/macos-observed-sigpipe-leaks`를 읽고 대조했다. webserv `2ba78ea`: README 형식 테스트, idle CPU(busy waiting) 테스트. 둘 다 일부러 틀린 변경으로 실패 확인. 사용자 결정 필요: README login, `listen` 주소만·`*:port` 형식, 제출 파일 목록 밖 파일.

## [2026-10-16] query | README 저자, listen 형식, 제출 파일
- 갱신: [[analysis/design-decisions]] 13 (`listen`은 `IPv4:port`와 `port`만), [[analysis/design]] 3절 구현 세부, [[analysis/test-plan]] B-06·B-07·C-11, [[overview]] (열린 질문에서 제출 파일 항목 제거)
- 메모: 사용자 답: README 저자는 yoshin, jyoo. `listen`은 "요구사항에 부합하고 안전한 쪽" → 거부 유지, 오류 메시지에 받는 형식을 적음. 제출 파일은 제출 때 따로 추리므로 지금은 다루지 않음. webserv `394ce95`.

## [2026-10-16] query | 구현 단계 3 (요청 파서)
- 갱신: [[analysis/test-plan]] (3절 P-01~P-20 신설, N-08·N-09 기대값 408·431), [[analysis/design]] 6절 구현 세부(RFC가 여러 처리를 허용하는 곳의 선택, 본문 상한용 location 찾기, 임시 오류 본문), 12절 `kMaxChunkLine`
- 메모: 읽은 위키: `implementation-plan` 3단계, `design` 5·6·11·12절, `concepts/request-parsing`, `concepts/status-codes`, `concepts/security` 1·3·5절. webserv `98cb1e2`(HeaderMap·Request·RequestParser), `7c3a966`(Connection 연결, StatusText, Router::matchLocation). 단위 53개, 통합 32개 Ubuntu 22.04에서 모두 통과(느린 테스트 포함). 계획 줄마다 일부러 틀린 코드로 실패 확인. 다른 검사와 겹쳐 테스트로 구분할 수 없는 검사 두 개(요청줄 세 번째 공백, 공백으로 시작하는 헤더 줄)는 뺐다. valgrind 아래 `siege -b -c 25 -t 10S` 7,676건 availability 100%, SIGINT 뒤 "All heap blocks were freed". 주석의 RFC 절 번호 두 곳(9110 2.5→6.2, 9112 9.6→8)을 원문 대조로 바로잡았다.

## [2026-10-16] query | 3단계까지 코드 리뷰
- 갱신: [[analysis/test-plan]] (C-28·N-24·P-21 추가, N-16 줄 번호)
- 메모: 사용자 요청으로 webserv 코드 약 2,600줄을 직접 읽어 리뷰. 고친 것: (1) 헤더 타임아웃이 마지막 수신 기준이라 1바이트씩 보내면 연장됐다. 설계 12절대로 받기 시작한 때부터 잰다 (`8790b61`). (2) 재귀 설정 파서가 10만 단계 중첩에서 segfault(실측 종료 코드 139). 깊이 3 제한 (`e58067d`). (3) 파서가 줄마다 버퍼 앞을 지워 1바이트 chunk 6MB에 CPU 1.6초. 커서 방식으로 0.2초 (`24fd810`). (4) 구현 메서드 목록이 파서와 설정 두 곳에 있었다. `http/Methods`로 하나로 (`cc873ae`). (5) listen 소켓 `O_NONBLOCK`을 `bind`·`listen` 뒤로 (`9854f52`, `concepts/configuration-file` 권고). 남긴 것: `EventLoop`가 `std::exception`만 잡음(코드가 다른 예외를 던지지 않음), 단위 테스트 둘이 실행 위치 의존, 오류 응답 뒤 바로 닫을 때의 리셋은 5단계 DRAIN. 실험 중 커밋 전 수정을 `git checkout`으로 지운 실수가 있어 다시 넣었다. 단위 54, 통합 34 Ubuntu 22.04 통과.

## [2026-10-16] query | 구현 단계 4 (라우팅, 정적 파일, 응답)
- 갱신: [[analysis/test-plan]] (4절 R-01~R-19 신설), [[analysis/design]] 7절 구현 세부(Router를 `route/`로, 상대 root 기준, 에러 페이지 매핑, `Content-Type` 기본값 `application/octet-stream`, 목록 형식, 심볼릭 링크 한계, 4단계의 POST·DELETE는 405, `Connection: close`)
- 메모: 읽은 위키: `implementation-plan` 4단계, `design` 1·2·7·8절, `concepts/http-features`, `concepts/configuration-file`, `concepts/security` 1·4절, `concepts/status-codes`, `sources/nginx-observed-directory`. webserv `dd3a573`(날짜·MIME), `fd5c868`(경로 정규화), `56d0c59`(경로 인코딩), `4922eb8`(Router), `40cb5e8`(Response·ResponseStream), `7404b94`(handler·RequestProcessor·Connection). 단위 74, 통합 50(Ubuntu에서는 root라 1개 건너뜀) 통과, 줄마다 일부러 틀린 코드로 실패 확인. 테스트가 잡은 버그: `strchr`가 NUL도 찾아서 `encodePath`가 NUL을 그대로 두었다. 디렉토리 목록 링크는 `:`이 든 이름이 스킴으로 읽히지 않게 `./`를 붙였다 (raw/rfc3986.txt:1211-1213, raw/rfc3986.txt:1448). valgrind 아래 빈 페이지 `siege -b -c 25 -t 10S` 11,860건 availability 100%, SIGINT 뒤 "All heap blocks were freed".

## [2026-10-16] query | 상수·자료형을 헤더로, 4단계 뒤 리팩토링
- 갱신: [[analysis/design]] 1절(실제 파일 배치, 상수·자료형은 헤더에 두는 규칙, `fs/`·`http/Hex` 분리), 2절(`fs` 모듈), 7절(`ErrorPageBuilder` → `buildStatusPage`), 12절(코드 위치 `core/Limits.hpp`, 값 3개 추가)
- 메모: 사용자 요청으로 `.cpp`에 있던 상수 약 80개와 자료형 6개를 헤더로 옮겼다(webserv `a04e914`). 상태 코드 중복(500 세 곳 등)은 `http/StatusCodes.hpp` 하나로. 이어서 리뷰 항목 리팩토링: Router 한 곳에서 경로→location (`69ca630`), `fs` 모듈 (`3a1632c`), 16진수 도우미 (`5c78725`), `buildStatusPage`·`kHtmlType` (`f99e937`), `Connection::where_` 제거 (`b867737`), 통합 테스트 도우미 (`d755481`). 동작 변경 없음, 단위 77·통합 50(Ubuntu에서 root라 1개 건너뜀) 통과. 사고: Docker 안에서 `clang-format -i`가 방금 길어진 파일을 예전 크기로 잘랐다(세 파일, 빌드 실패로 발견). 마지막 커밋에서 복구했고, 이후 포맷은 표준 입력으로 넘긴다. 헤더에 근거 없이 쓴 "NGINX도 300~599" 주석은 원문에 없어 지웠다.

## [2026-10-17] query | 2차 코드 리뷰와 수정
- 갱신: [[analysis/design-decisions]] 14(alias 경계), [[analysis/test-plan]] (R-20·R-21·C-29), [[concepts/security]] 1절(정규화 뒤 alias 이어 붙이기)
- 메모: 리팩토링 뒤 코드를 다시 읽었다. 실측으로 확인한 보안 문제: `location /k { alias dir/; }`에 `/k../x`가 alias 밖 파일을 200으로 보냈다 → alias location은 경로 경계에서만 맞춤 (webserv `3640847`). `index ../x;` 설정도 root 밖 파일을 보냈다 → `index`에 `/` 금지 (`c949f89`). HEAD 요청의 오류 응답(413·408 등)에 본문이 실렸다 → 모든 응답이 `RequestProcessor::finish`를 거치게 함 (`228de8d`). 메서드·헤더 이름 상수 `http/HeaderNames.hpp` (`de1e6d7`), 쓰지 않는 `RouteResult::location` 제거 (`2065ce7`). 단위 79, 통합 52(Ubuntu에서 root라 1개 건너뜀) 통과, 각 수정은 일부러 되돌려 테스트 실패를 확인.

## [2026-10-17] query | 테스트 코드 상수 규칙, 3·4차 코드 리뷰
- 갱신: [[analysis/test-plan]] (N-25)
- 메모: 테스트 코드에도 상수·자료형은 헤더에 두는 규칙을 적용했다(webserv `639247b` C++ `tests/unit/TestConstants.hpp`·`EventLoopDoubles.hpp`, `dedbfc1` Python은 헤더가 없어 `tests/integration/constants.py`). 3차 리뷰: 이벤트 처리 밖(타임아웃 점검, poll 목록 만들기)의 예외가 `std::terminate`로 이어질 수 있었다 → 연결 단위로 잡고 `main`에서 마지막으로 잡음 (`785f4f2`). 테스트로 만들 수 없어 예외를 일부러 넣은 빌드로 확인했다. 4차 리뷰에서 허용 함수 목록 밖 C 함수(`memset`·`strchr`·`strlen`·`<cctype>`)와 읽지 않는 `ListenContext` 필드를 찾았다(사용자 결정 대기).

## [2026-10-17] query | 4차 코드 리뷰 수정
- 갱신: [[analysis/test-plan]] (B-08 신설, N-15), [[analysis/design]] 5절(`ListenContext`), [[analysis/subject-vs-evaluation]] 1.4(코드는 엄격한 쪽을 따름)
- 메모: 목록 밖 C 함수 `memset`·`strchr`·`strlen`·`<cctype>`를 `http/Ascii`·`std::string`·값 초기화로 바꿨다 (webserv `3dbbcb3`). `isOneOf`는 NUL과 맞지 않는다(전에 `strchr`가 맞춰서 버그가 났다). 읽지 않던 `ListenContext`의 로컬·원격 주소와 `formatIpv4`를 뺐다 (`41fc4b8`, 7단계에서 다시). 단위 81, 통합 52(Ubuntu에서 root라 1개 건너뜀) 통과.

## [2026-10-17] query | 5차 코드 리뷰 수정
- 갱신: [[analysis/test-plan]] B-08
- 메모: 사용자 의견("string 쪽은 라이브러리로 대체해도 된다")에 따라, 4차 수정에서 직접 쓴 문자 판별을 C++ 표준 라이브러리(`std::char_traits`, `std::string::find_first_not_of`, `<locale>`의 `std::tolower`)로 바꿨다. C 함수(`<cctype>`·`<cstring>`)만 피한다는 1.4절 기준은 그대로다. 십진수 해석 세 벌을 `parseDecimal` 하나로 합치면서, 상한이 한 자리 숫자보다 작을 때 뺄셈이 돌아 검사를 통과하던 결함도 고쳤다(지금 쓰는 상한은 모두 9 이상이라 실제로는 나지 않음, **판단**). webserv `7f0ed84`. 단위 82, 통합 52(Ubuntu에서 root라 1개 건너뜀) 통과.
