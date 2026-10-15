---
title: siege 기본 설정 템플릿 (siegerc.in)
type: source
sources: [raw/siegerc.in, raw/siege.pod, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# siege 기본 설정 템플릿 (siegerc.in)

원본: `raw/siegerc.in`. <https://raw.githubusercontent.com/JoeDog/siege/master/doc/siegerc.in>을 2026-10-15에 받아 그대로 저장했다.

- 이 파일을 마지막으로 바꾼 커밋: `9d9c08f01cf65e10db63f3276fe0dcdb3f72e1af` (2023-04-10). (받을 때 GitHub에서 본 값이고 raw 파일에는 없다.)
- **템플릿**이다. 빌드할 때 `%_VERSION%` 같은 자리표시자가 채워진다 (raw/siegerc.in:1-2). 평가 PC에 설치된 siege의 실제 설정 파일(`$HOME/.siege/siege.conf`, raw/siege.pod:22)이 이 템플릿과 같은지는 **미확인**이다. 평가 때 직접 확인한다.
- 명령줄 옵션이 설정 파일보다 우선한다 (raw/siege.pod:18-20).

## 과제와 관련된 설정

| 설정 | 템플릿 값 | 의미 | 근거 |
|---|---|---|---|
| `connection` | `close` | 요청마다 연결을 새로 맺음 (**판단**). keep-alive는 권장하지 않는다는 경고가 붙어 있음 | raw/siegerc.in:255-268 |
| `protocol` | `HTTP/1.1` | 요청 프로토콜. 서버의 HTTP/1.1 구현이 이상하면 HTTP/1.0으로 바꾸라고 안내 | raw/siegerc.in:205-213 |
| `chunked` | `true` | chunked 응답을 처리 | raw/siegerc.in:216-223 |
| `timeout` | (주석, 기본 30초) | 소켓 연결 타임아웃 | raw/siegerc.in:353-358 |
| `failures` | (주석, 기본 1024) | 연결 실패가 이만큼 쌓이면 중단. 4xx·5xx는 세지 않음 | raw/siegerc.in:381-393 |
| `concurrent` | `25` | 기본 동시 사용자 수 | raw/siegerc.in:271-277 |
| `limit` | `255` | 동시 사용자 상한 | raw/siegerc.in:193-202 |
| `delay` | `0.0` | 요청 사이 지연 | raw/siegerc.in:339-350 |
| `benchmark` | `false` | 기본은 벤치마크 모드 아님 | raw/siegerc.in:406-412 |
| `cache` | `false` | 캐시 재검증(304) 끔 | raw/siegerc.in:226-252 |

다루지 않는 설정: 출력·로그·색상, URL 파일, 쿠키, 프록시, 인증, 인코딩.

> [!warning] 모순: `delay` 기본값
> 매뉴얼은 기본 지연을 0.5초라고 한다 (raw/siege.pod:186-187). 템플릿은 `delay = 0.0`이다 (raw/siegerc.in:350). 템플릿 쪽이 최근 커밋(2023)이지만 실제 값은 설치된 설정 파일이 정한다. 평가표의 availability 확인은 `-b`로 하므로 (raw/evaluation-sheet-en.md:114) 그때는 지연이 없다 (raw/siege.pod:199-202). 부하 테스트에서는 `-d`를 정할 수 있다 (raw/evaluation-sheet-en.md:118).
