---
title: 구현 순서
type: analysis
sources: [raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-16
---

# 구현 순서

위키의 결론을 구현 단계로 묶었다. 순서는 **판단**이다. 기준은 두 가지다. 각 단계가 끝나면 서버를 실제로 띄워 curl·브라우저로 확인할 수 있어야 하고, 뒤 단계가 앞 단계의 구조를 뜯어고치지 않아야 한다.
클래스·인터페이스는 [[analysis/design]]에 있다. 각 단계의 세부 규칙은 링크한 concept 페이지에 있다. 사용자가 정한 것은 [[analysis/design-decisions]]에 있다.

## 전체 구조 (판단)

```
main
 ├─ Config        설정 파일 → ServerConfig[] / LocationConfig[]   (네트워크와 무관)
 ├─ EventLoop     poll() 하나. listen·client socket·CGI pipe를 모두 등록
 │   └─ Connection   연결별 상태기계: 요청 읽기 → 처리 → 응답 쓰기 → (keep-alive | 버리기 후 close)
 │        ├─ RequestParser   바이트 → Request (요청줄·헤더·본문, chunked 해제)
 │        ├─ Router          Request + Config → 처리 방식 (정적·리다이렉트·업로드·DELETE·CGI·에러)
 │        ├─ Handler들       정적 파일 / autoindex / 업로드 / DELETE / CGI
 │        └─ ResponseBuilder 상태줄·헤더·본문 → 보낼 바이트
 └─ Signals       SIGPIPE 무시, SIGINT·SIGTERM은 플래그만 세움
```

- 모든 소켓·pipe I/O는 `poll()`이 준비됐다고 알린 뒤에만, 준비 1회에 `recv`/`send`/`read`/`write` 1번만 한다 (raw/subject.md:130-133) → [[concepts/io-multiplexing]].
- Handler는 결과를 바로 쓰지 않는다. 응답 바이트를 Connection의 쓰기 버퍼에 넣고, 실제 전송은 `POLLOUT` 때 EventLoop가 한다. CGI도 pipe fd를 EventLoop에 등록해서 처리한다.

## 단계

### 0. 저장소 뼈대

- 만들 것: `Makefile`(`c++`, `-Wall -Wextra -Werror -std=c++98`, 규칙 `NAME`·`all`·`clean`·`fclean`·`re`), 디렉토리 구조, `README.md` 틀 → [[concepts/build-and-submission]].
- 완료 기준: `make`, `make re`가 경고 없이 되고, 두 번째 `make`에서 다시 링크하지 않는다.
- README의 필수 요소가 하나라도 빠지면 0점이다 (raw/evaluation-sheet-en.md:35-44). 틀을 처음에 만들어 두고 마지막에 채운다.

### 1. 설정 파일 파서

- 만들 것: 토크나이저와 파서, `ServerConfig`·`LocationConfig` 구조체, 검증. 실행 인자가 없으면 기본 경로의 설정 파일을 쓴다 (raw/subject.md:127).
- 지원할 항목 (raw/subject.md:163-173): `listen`(interface:port 여러 개), `error_page`, `client_max_body_size`, `location`과 그 안의 허용 메서드·`return`·`root`·`autoindex`·`index`·업로드 허용과 저장 위치·CGI 확장자 → [[concepts/configuration-file]] "NGINX 지시자 대응표".
- 검증: 같은 `interface:port`가 두 번 나오면 에러 메시지를 내고 시작하지 않는다 (결정 4, raw/evaluation-sheet-en.md:108). `0.0.0.0`과 특정 IP의 같은 포트도 거부한다 → [[concepts/configuration-file]] "포트 관련 엣지 케이스".
- 완료 기준: 정상 설정 파일과 잘못된 설정 파일 여러 개를 넣어 파싱 결과를 출력해 확인한다. 네트워크 코드 없이 시험할 수 있다.

### 2. 이벤트 루프와 고정 응답

- 만들 것: listen 소켓 여러 개(`SO_REUSEADDR`, non-blocking), `poll()` 루프, `accept`, 연결별 읽기·쓰기 버퍼, 모든 요청에 같은 200 응답을 보내고 닫기.
- 시그널: `SIGPIPE` 무시, `SIGINT`·`SIGTERM`은 플래그만 세우고 루프가 모든 fd와 메모리를 정리한 뒤 끝낸다 → [[concepts/resilience]] "시그널 처리".
- `POLLOUT`은 보낼 데이터가 있을 때만 켠다. `recv`가 0이나 -1이면 errno를 보지 않고 연결을 정리한다 → [[concepts/io-multiplexing]].
- 완료 기준: 여러 포트에 curl이 동시에 붙어도 응답이 오고, Ctrl-C 뒤 valgrind가 "All heap blocks were freed"를 보인다. 이 단계에서 `siege -b`를 한 번 돌려 둔다 (평가 기준 99.5% 초과, raw/evaluation-sheet-en.md:114).

### 3. 요청 파서

- 만들 것: 바이트가 조금씩 들어와도 이어서 처리하는 상태기계. 요청줄 → 헤더 → 본문 길이 결정 → 본문(`Content-Length` 또는 chunked 해제) → [[concepts/request-parsing]].
- 크기 제한: 요청줄·헤더 상한, `client_max_body_size` 초과는 413 → [[concepts/security]] "길이 공격".
- 완료 기준: telnet/nc로 정상·불완전·잘못된 요청(Host 누락, 잘못된 `Content-Length`, 깨진 chunked 등)을 보내 [[concepts/status-codes]] 표와 같은 코드가 나온다.

### 4. 라우팅, 정적 파일, 응답 생성

- 만들 것:
  - location 선택(정규화한 경로의 가장 긴 prefix) → [[concepts/configuration-file]] "location 매칭".
  - 경로 정규화: query 분리 → 디코딩 한 번 → `%00`·`%2F` 거부(결정 3) → `..` 처리(root 위로 가면 400 + 닫기, 결정 2) → root 매핑 → [[concepts/security]] "경로 정규화 절차".
  - GET·HEAD(결정 5), 허용되지 않은 메서드는 405 + `Allow`.
  - 디렉토리: `/` 없으면 301, index 파일, autoindex, 둘 다 없으면 403 → [[concepts/configuration-file]] "디렉토리 요청 처리 순서".
  - `return` 리다이렉트, 기본 에러 페이지와 설정된 에러 페이지 (raw/subject.md:143).
  - ResponseBuilder: 상태줄, `Content-Length`, `Content-Type`, `Connection` → [[concepts/http-features]] "응답 헤더 규칙".
- 완료 기준: 정적 사이트 하나를 브라우저로 끝까지 볼 수 있다 (raw/subject.md:145). 각 경우의 상태 코드를 curl로 확인한다.

### 5. 연결 관리

- 만들 것: keep-alive 판단, `Connection: close`, 타임아웃(헤더 수신·본문 수신·응답 전송·keep-alive 대기), 본문을 다 읽지 않고 응답한 연결은 읽어서 버리다가 상한에 닿으면 `close()` → [[concepts/connection-management]].
- 완료 기준: 응답 없이 열어 둔 연결이 타임아웃으로 정리된다. 큰 본문에 413을 보내도 클라이언트가 응답을 받는다. `siege -b`를 오래 돌려도 메모리가 늘지 않고 hang이 없다 (raw/evaluation-sheet-en.md:114-117).

### 6. 업로드와 DELETE

- 만들 것: 업로드 허용 location의 POST에서 `multipart/form-data`를 파싱해 저장(결정 7), 다른 형식은 415. 파일 이름에서 경로를 버리고 덮어쓰기를 막는다. DELETE → [[concepts/file-upload]], [[concepts/http-features]] "메서드별 규칙".
- 완료 기준: 브라우저 폼으로 올린 파일을 다시 GET으로 받아 내용이 같다. DELETE 뒤 GET이 404다.

### 7. CGI

- 만들 것: 확장자로 CGI를 고르고 `fork`·`execve`. 메타변수(php-cgi용 `REDIRECT_STATUS`·`SCRIPT_FILENAME` 포함)를 만들고, 스크립트 디렉토리에서 실행한다. 입력·출력 pipe를 EventLoop에 등록하고 본문을 넘긴다(chunked는 해제한 뒤, raw/subject.md:179). 출력은 EOF까지 모아 CGI 응답을 HTTP 응답으로 바꾼다. 타임아웃이면 504로 응답하고 자식을 끝낸다. 형식 오류는 502. 자식은 `waitpid(..., WNOHANG)`으로 회수한다 → [[concepts/cgi]].
- index 파일이 CGI 확장자면 내부 리다이렉트로 CGI를 실행하고, 내부 리다이렉트 횟수에 상한을 둔다 (결정 6).
- 완료 기준: php-cgi와 Python 스크립트로 GET·POST(일반, chunked)가 된다. 무한 루프 스크립트에도 서버가 멈추지 않는다. 에러를 내는 스크립트에는 502가 간다.

### 8. 안정성 점검

- [[concepts/resilience]] "요구 목록"을 하나씩 확인한다: valgrind 누수, 긴 시간 `siege -b`, 클라이언트 중간 끊김, 동시 연결, 같은 포트로 두 번째 실행 시 에러 후 종료.
- 테스트는 한 도구로만 하지 않고 Python 등으로 스크립트를 쓴다 (raw/subject.md:190) → [[concepts/testing]].

### 9. 시연 준비와 마무리

- 기능별 설정 파일, 정적 사이트, CGI 스크립트(정상·에러·무한 루프)를 저장소에 넣는다 (raw/subject.md:184).
- README를 채운다 (raw/subject.md:196-203).
- 보너스는 필수가 모두 통과해야 평가된다 (raw/subject.md:218). 쿠키·세션은 CGI 예제(결정 8), CGI 여러 종류(raw/subject.md:216) → [[concepts/bonus]].

## 진행 중 정할 것

- 평가자와 합의할 해석 질문(허용 함수 범위, `fcntl`, errno, `waitpid` 매크로, `F_SETFD`)은 [[analysis/subject-vs-evaluation]] 6절에 있다. 구현은 위키의 판단대로 하고, 디펜스에서 설명한다.
- 단계마다 새로 정해야 할 것이 생기면 [[analysis/design-decisions]]에 추가한다.
