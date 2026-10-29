---
title: Ubuntu 22.04 실측 — 도구 버전, siege 설정, php-cgi·valgrind 재측정
type: source
sources: [raw/ubuntu2204-observed-tools.md, raw/php-cgi-observed-env.md, raw/valgrind-observed-sigint.md, raw/siegerc.in, raw/siege-sock.c, raw/siege.pod]
updated: 2026-10-29
---

# Ubuntu 22.04 실측 — 도구 버전, siege 설정, php-cgi·valgrind 재측정

원본: `raw/ubuntu2204-observed-tools.md`. 평가 PC가 Ubuntu 22.04라서(사용자 확인, 2026-10-15) 22.04 공식 Docker 이미지에 apt 기본 패키지를 설치해 버전과 설정을 출력하고, 24.04에서 했던 측정을 같은 스크립트로 다시 실행했다 (raw/ubuntu2204-observed-tools.md:3-4).

- 이미지: `Ubuntu 22.04.5 LTS` (raw/ubuntu2204-observed-tools.md:82). 커널은 OrbStack VM의 `7.0.14`라서 평가 PC의 22.04 커널과 다르다 (raw/ubuntu2204-observed-tools.md:4, raw/ubuntu2204-observed-tools.md:83). 커널이 정하는 동작(소켓·pipe·`poll`)은 이 측정으로 22.04 기준을 확인할 수 없다.
- 평가 PC가 apt 기본 패키지와 기본 설정 파일을 그대로 쓰는지는 **미확인**이다 (확인: 평가 PC에서 `siege -V`, `siege -C`, `php-cgi -v`, `python3 --version`, `valgrind --version`).
- 2026-10-29 사용자 보고 (평가 PC): siege가 설치되어 있지 않고 sudo 권한이 없다. `php-cgi -v`는 동작하고(버전은 보고받지 않음), 경로는 `conf/default.conf`가 쓰는 `/usr/bin/php-cgi`다. 그래서 보너스 "여러 CGI"(Python·PHP)를 기본 설정 그대로 보여 줄 수 있다. sudo 없이 siege를 쓰는 방법은 [[concepts/testing]] "sudo 없이 siege 쓰기".

## 패키지 버전

| 도구 | 패키지 버전 | 실행 버전 | 근거 |
|---|---|---|---|
| php-cgi | `php8.1-cgi 8.1.2-1ubuntu2.26` | PHP 8.1.2 | raw/ubuntu2204-observed-tools.md:85, raw/ubuntu2204-observed-tools.md:90 |
| valgrind | `1:3.18.1-1ubuntu2` | valgrind-3.18.1 | raw/ubuntu2204-observed-tools.md:88, raw/ubuntu2204-observed-tools.md:91 |
| Python | `python3 3.10.6-1~22.04.1` | Python 3.10.12. `import cgi` 성공 | raw/ubuntu2204-observed-tools.md:86, raw/ubuntu2204-observed-tools.md:92-93 |
| siege | `4.0.7-1build3` | SIEGE 4.0.7 | raw/ubuntu2204-observed-tools.md:87, raw/ubuntu2204-observed-tools.md:133 |
| g++ | `4:11.2.0-1ubuntu1` | (valgrind 측정에서) g++ 11.4.0 | raw/ubuntu2204-observed-tools.md:84, raw/ubuntu2204-observed-tools.md:433 |

## siege 설정

- siege를 처음 실행하면 `~/.siege`에 설정 템플릿을 만든다는 안내가 나오고 (raw/ubuntu2204-observed-tools.md:131-132), 만들어진 `/root/.siege/siege.conf`는 `/etc/siege/siegerc`와 같은 파일이었다 (raw/ubuntu2204-observed-tools.md:141-142).
- `/etc/siege/siegerc`는 v4.0.7 태그의 `doc/siegerc.in`과 주석 속 로그 경로 2줄만 다르다 (raw/ubuntu2204-observed-tools.md:143-151).
- `siege -C`로 본 적용값 (raw/ubuntu2204-observed-tools.md:157-188):

| 항목 | 값 | 근거 |
|---|---|---|
| protocol | `HTTP/1.1` | raw/ubuntu2204-observed-tools.md:162 |
| connection | `close` | raw/ubuntu2204-observed-tools.md:165 |
| concurrent users | 25 | raw/ubuntu2204-observed-tools.md:166 |
| socket timeout | 30 | raw/ubuntu2204-observed-tools.md:169 |
| delay | 0.000 sec | raw/ubuntu2204-observed-tools.md:172 |
| benchmark mode | false | raw/ubuntu2204-observed-tools.md:174 |
| failures until abort | 1024 | raw/ubuntu2204-observed-tools.md:175 |
| thread limit | 255 | raw/ubuntu2204-observed-tools.md:178 |
| json output | true | raw/ubuntu2204-observed-tools.md:188 |

- 설정 파일에는 `verbose = true`, `quiet = false`인데 (raw/ubuntu2204-observed-tools.md:102-104) `siege -C`는 `verbose: false`, `quiet: true`로 보였다 (raw/ubuntu2204-observed-tools.md:158-160). 원인은 확인하지 않았다. 서버 동작과는 관계없는 출력 설정이다.

## siege v4.0.7과 위키 원본(master)의 차이

위키의 siege 원본 3개는 master 브랜치 파일이다. 설치된 4.0.7의 태그 파일과 diff를 떴다 (raw/ubuntu2204-observed-tools.md:198-276).

| 파일 | 차이 | 위키 내용에 주는 영향 | 근거 |
|---|---|---|---|
| `src/sock.c` | 이름 해석 부분(97~236줄)의 조건부 컴파일 매크로, 오류 메시지, 주석 오타뿐. 줄 수가 같다 | 없음. [[sources/siege-sock]]이 인용한 범위 중 다른 줄은 `new_socket` 안의 236줄(`#if` 조건 매크로) 하나다. 그 뒤의 준비 검사·timeout·`socket_read` 부분은 diff에 나오지 않는다 | raw/ubuntu2204-observed-tools.md:246-275 |
| `doc/siegerc.in` | `json_output` 기본값(4.0.7은 `true`, master는 `false`), `auth-url` 설명 추가, 오타 | [[sources/siegerc]]가 다룬 설정(connection, protocol, timeout, failures, concurrent, limit, delay, benchmark, cache)은 차이 없음 | raw/ubuntu2204-observed-tools.md:219-244 |
| `doc/siege.pod` | urls.txt 변수 설명 추가, 오타, 예시 수치 | 없음 | raw/ubuntu2204-observed-tools.md:201-217 |

## php-cgi 재측정

- 같은 스크립트로 실행한 결과가 24.04(`raw/php-cgi-observed-env.md`)와 같았다. 버전 줄과 `php.ini` 경로(`/etc/php/8.1/cgi/php.ini`)만 다르다 (raw/ubuntu2204-observed-tools.md:278-404).
  - 기본 설정: `cgi.force_redirect='1'`, `cgi.fix_pathinfo='1'` (raw/ubuntu2204-observed-tools.md:301-306).
  - `REDIRECT_STATUS`가 없거나 `HTTP_REDIRECT_STATUS`만 있으면 헤더 없는 안내문과 exit 255 (raw/ubuntu2204-observed-tools.md:309-319, raw/ubuntu2204-observed-tools.md:339-349). `REDIRECT_STATUS=0`·빈 값은 실행됨 (raw/ubuntu2204-observed-tools.md:321-337).
  - `REDIRECT_URL`이나 `cgi.fix_pathinfo=0`이면 `PATH_TRANSLATED` 쪽(`other.php`) 실행 (raw/ubuntu2204-observed-tools.md:370-380).
  - 없는 파일 404, 읽을 수 없는 파일 403, 둘 다 exit 255 (raw/ubuntu2204-observed-tools.md:392-404, raw/ubuntu2204-observed-tools.md:416-420).
- 403일 때 stderr 경고 문구만 다르다: 22.04는 `PHP Warning:  Unknown: Failed to open stream` (raw/ubuntu2204-observed-tools.md:426).
- 22.04 패키지도 `HTTP_REDIRECT_STATUS`를 받지 않는다. 패키지 changelog에 CVE-2024-8927 패치가 있다 (2026-10-15 컨테이너에서 `changelog.Debian.gz` 확인, raw에 없음).

## valgrind 재측정

- 네 모드의 LEAK SUMMARY가 24.04(`raw/valgrind-observed-sigint.md`)와 같은 분류로 나왔다 (raw/ubuntu2204-observed-tools.md:429-555):
  - `default`: SIGINT 기본 동작으로 종료, definitely lost 0, still reachable 73,784바이트 (raw/ubuntu2204-observed-tools.md:443, raw/ubuntu2204-observed-tools.md:468-471)
  - `return`: definitely lost 80바이트 (raw/ubuntu2204-observed-tools.md:499)
  - `exit`: definitely lost 0, still reachable 1,080바이트 (raw/ubuntu2204-observed-tools.md:530-533)
  - `cleanup`: "All heap blocks were freed -- no leaks are possible" (raw/ubuntu2204-observed-tools.md:552)
- 라이브러리 블록 크기만 다르다 (22.04는 72,704바이트, raw/ubuntu2204-observed-tools.md:459).

## 과제 적용 (판단)

- 평가 PC가 기본 패키지를 쓴다면 php-cgi·valgrind에 대한 기존 결론([[sources/php-cgi-observed-env]], [[sources/valgrind-observed-sigint]])이 그대로 맞는다.
- Python 3.10에는 `cgi` 모듈이 있다. 그래도 3.11부터 deprecated이고 3.13에서 제거되므로 ([[sources/pep-0594]]) 다른 환경에서도 돌도록 `cgi` 모듈을 쓰지 않는 기존 방침을 유지한다.
- siege는 4.0.7이고, 위키의 siege 분석은 이 버전에도 맞는다. 평가 PC의 siege 설정이 기본이라면 요청마다 새 연결(`connection: close`), HTTP/1.1, 소켓 timeout 30초다.
