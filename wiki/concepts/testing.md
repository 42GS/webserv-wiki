---
title: 테스트 도구와 평가 시연
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md, raw/siege.pod, raw/siegerc.in, raw/evaluation-sheet.md, raw/rfc9112.txt, raw/pep-0594.md, raw/siege-sock.c]
updated: 2026-10-15
---

# 테스트 도구와 평가 시연

## 제공·사용되는 도구

| 도구 | 용도 | 근거 |
|---|---|---|
| `tester` | 일반 테스터. 브라우저와 자체 테스트로 잘 동작하면 사용 의무 없음 | raw/evaluation-sheet-en.md:30, raw/subject.md:188 |
| `cgi_tester` | CGI 테스터 | raw/evaluation-sheet-en.md:31 |
| `siege` | 스트레스 테스트. 평가표는 apt 설치 기준 (`sudo apt-get install siege`). 빈 페이지 GET에 `siege -b`로 availability 99.5% 초과 | raw/evaluation-sheet-en.md:48, raw/evaluation-sheet-en.md:113-114 |
| `telnet`, `curl` | 기본 요청 시연 | raw/evaluation-sheet-en.md:77, raw/subject.md:123 |
| 브라우저 네트워크 탭 | 헤더 확인 | raw/evaluation-sheet-en.md:97-98 |
| NGINX | 동작·헤더 비교 기준 | raw/subject.md:141, raw/subject.md:186 |
| `leaks`, `valgrind`, `e_fence` | 누수 검사 | raw/evaluation-sheet-en.md:25 |

## 평가표에 나온 명령

```bash
# body 크기 제한 (raw/evaluation-sheet-en.md:70) — 원문에도 대상 URL이 없다. 평가자가 붙여서 쓴다
curl -X POST -H "Content-Type: plain/text" \
     --data "BODY IS HERE write something shorter or longer than body limit"
```

> [!note] 구버전 정리본과 차이
> 구버전 정리본에 있던 `ubuntu_tester`, `ubuntu_cgi_tester`(raw/evaluation-sheet.md:32-33)와 `curl --resolve` 호스트네임 테스트(raw/evaluation-sheet.md:67)는 영어 원문에 없다 (raw/evaluation-sheet-en.md:29-31, raw/evaluation-sheet-en.md:63-73).

## siege

### 평가 조건

- 빈 페이지에 대한 단순 GET을 `siege -b`로 돌려 availability가 99.5%를 넘어야 한다 (raw/evaluation-sheet-en.md:114).
- 재시작 없이 무한히 돌릴 수 있어야 하고, 메모리가 끝없이 늘거나 연결이 hang하면 안 된다 (raw/evaluation-sheet-en.md:115-117).
- OS에 따라 결과가 다르므로 `-c`, `-d`, `-r`로 초당 연결 수를 제한한다. 값은 평가자가 정하되 평가받는 사람과 **합의**해야 한다 (raw/evaluation-sheet-en.md:118). 미리 자기 환경에서 통과하는 값을 측정해 두면 협상 근거가 된다.

### 옵션 (siege 매뉴얼)

| 옵션 | 의미 | 근거 |
|---|---|---|
| `-c NUM` | 동시 사용자 수. 기본 설정의 상한은 255명이고, 넘기려면 `siege.conf`를 바꿔야 함 | raw/siege.pod:143-155 |
| `-r NUM` | 사용자마다 반복할 횟수 | raw/siege.pod:157-165 |
| `-t NUMm` | 실행 시간 (S·M·H, 예: `-t60S`) | raw/siege.pod:170-180 |
| `-d NUM` | 요청 사이 지연(초). 기본 0.5초 | raw/siege.pod:182-187 |
| `-b` | 벤치마크 모드. 반복 사이에 지연이 없음 | raw/siege.pod:199-202 |

- 명령줄 값이 설정 파일 값보다 우선한다 (raw/siege.pod:18-20).
- 평가표는 `-d`를 "클라이언트가 다시 연결하기 전 최대 대기 시간"이라고 설명한다 (raw/evaluation-sheet-en.md:118). 매뉴얼의 정의는 "요청 사이 지연"이다 (raw/siege.pod:184-187). `-b`와 `-d`를 함께 줬을 때 어느 쪽이 적용되는지는 매뉴얼에 없다 (**미확인**).

### Availability가 재는 것

- 서버가 성공적으로 처리한 **소켓 연결**의 비율이다. 실패에는 타임아웃이 포함된다. **4xx·5xx 응답은 이 값에 포함되지 않고** "Failed transactions"로 따로 기록된다 (raw/siege.pod:373-378).
  - 원문의 계산식 문장은 "socket failures (including timeouts) divided by the sum of all connection attempts"다 (raw/siege.pod:375-376). 글자 그대로 읽으면 실패율이라 앞 문장("successfully handled"의 비율)과 맞지 않는다. 원문의 표현 문제로 보고, 의미는 앞 문장을 따른다 (**판단**).
- 따라서 99.5%를 깎는 것은 status code가 아니라 **연결 수준의 실패**다: 연결 거부, 응답 도중 연결 끊김, 타임아웃. → [[concepts/resilience]]
- Transactions는 리다이렉트와 페이지 요소 요청까지 센다 (raw/siege.pod:365-371). 평가는 빈 페이지라 요소가 없다.
- Successful transactions는 응답 코드가 400 미만인 횟수다 (raw/siege.pod:411-412).

### 기본 설정 (siegerc.in 템플릿)

| 설정 | 기본값 | 서버에 주는 의미 | 근거 |
|---|---|---|---|
| `connection` | `close` | **요청마다 새 TCP 연결** (**판단**). keep-alive는 권장하지 않음 | raw/siegerc.in:255-268 |
| `protocol` | `HTTP/1.1` | HTTP/1.1 파싱 규칙 적용 (Host 필수 등) → [[concepts/request-parsing]] | raw/siegerc.in:213 |
| `timeout` | 30초 | 소켓 연결 타임아웃. 타임아웃은 연결 실패로 집계 → Availability 하락. siege 소스에서 이 값은 `read()` 직전마다 하는 준비 검사의 대기 시간으로도 쓰인다 (raw/siege-sock.c:360-362, raw/siege-sock.c:611-626). 다만 그 검사가 읽기·쓰기 집합을 함께 보므로 응답 대기에는 실제로 걸리지 않을 수 있다 (raw/siege-sock.c:370-374, **판단**) → [[sources/siege-sock]] | raw/siegerc.in:353-354, raw/siege.pod:374-376 |
| `failures` | 1024 | 연결 실패가 이만큼 쌓이면 siege 중단. 4xx·5xx는 세지 않음 | raw/siegerc.in:381-389 |
| `concurrent` / `limit` | 25 / 255 | 기본 동시 사용자 / 상한 | raw/siegerc.in:277, raw/siegerc.in:202 |

- 템플릿이므로 평가 PC의 실제 설정 파일과 다를 수 있다 (**미확인**). 평가 전에 평가자와 `~/.siege/siege.conf`의 `connection`, `protocol`, `timeout`을 함께 확인하면 좋다.
- `delay` 기본값은 매뉴얼(0.5초, raw/siege.pod:186-187)과 템플릿(0.0, raw/siegerc.in:350)이 다르다. 평가표의 availability 확인은 `-b`로 하므로 (raw/evaluation-sheet-en.md:114) 그때는 영향이 없다.

### 서버 구현에 주는 결론

- 기본 설정의 siege는 `connection = close`라 요청마다 연결을 새로 맺는다고 본다 (raw/siegerc.in:268, **판단**). 그래서 99.5%를 좌우하는 것은 **`accept` 처리, 응답 후 연결 종료, 연결이 몰릴 때 거부되지 않는지**다.
- 매뉴얼의 `-g`·`-p` 예시 요청에는 `Connection: close` 헤더가 들어 있다 (raw/siege.pod:92-97, raw/siege.pod:118-123). 부하 테스트 요청에도 넣는지는 매뉴얼에 없다 (**미확인**). 넣는다면 서버는 응답 후 종료를 시작해야 한다 (MUST, raw/rfc9112.txt:1521-1526) → [[concepts/connection-management]].

## 권장 사항

- 한 프로그램으로만 테스트하지 말고 Python/Go 등으로 테스트를 작성 (raw/subject.md:190).
- 평가자는 원칙적으로 설정 파일 외에는 수정하지 않고, 수정하려면 평가받는 사람과 합의해야 하므로 (raw/evaluation-sheet-en.md:24), 시연용 설정·파일·CGI 스크립트(정상/에러/무한 루프)를 미리 준비한다 (raw/subject.md:184, raw/evaluation-sheet-en.md:91). Python으로 쓸 때는 `cgi` 모듈을 쓰지 않는다 (Python 3.13에서 제거, raw/pep-0594.md:188-190, raw/pep-0594.md:218) → [[concepts/cgi]] 6절.

## 관련

- [[concepts/resilience]], [[concepts/cgi]], [[concepts/configuration-file]]
