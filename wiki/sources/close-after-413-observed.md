---
title: 실측 — 413 뒤 바로 close vs 읽고 버리다 close (Ubuntu 22.04, macOS)
type: source
sources: [raw/close-after-413-observed.md, raw/rfc9112.txt, raw/subject.md]
updated: 2026-10-16
---

# 실측 — 413 뒤 바로 `close()` vs 읽고 버리다 `close()` (Ubuntu 22.04, macOS)

원본: `raw/close-after-413-observed.md`. 요청 머리만 읽고 413을 보낸 뒤 세 방식으로 연결을 끝내는 시험 서버를 만들고, 10MB 본문을 보내는 curl과 Python 클라이언트로 Ubuntu 22.04 컨테이너와 macOS에서 실행한 출력을 그대로 담았다 (2026-10-16, raw/close-after-413-observed.md:3-4).

- 서버 방식: `close`(바로 `close()`), `drain`(1초 동안 데이터가 없거나 EOF거나 총 5초가 될 때까지 읽어 버린 뒤 `close()`), `shutdown`(`shutdown(SHUT_WR)` 뒤 `drain`과 같음, NGINX 방식 참고용) (raw/close-after-413-observed.md:15-19).
- 클라이언트: curl은 `Expect`를 끄고 본문을 보낸다. Python은 본문 전체를 보낸 뒤에야 읽는다 (raw/close-after-413-observed.md:107-108).
- 받은 목적: [[analysis/subject-vs-evaluation]] "남은 미확인" — `shutdown` 없이 읽고 버리다가 닫는 것으로 클라이언트가 응답을 잃지 않는지 ([[sources/nginx-src-lingering-close]]에서 생김).
- curl 결과는 `http_code`와 종료 코드로 본다. `body=` 값은 이전 시도에서 남은 파일일 수 있다 (raw/close-after-413-observed.md:5).

## 결과

방식마다 curl 3회, Python 3회.

| 방식 | Ubuntu 22.04 (Docker) | macOS 26.6.2 |
|---|---|---|
| `close`, curl | 3회 모두 413 (raw/close-after-413-observed.md:192-205) | 2회 413, **1회 실패**: `curl: (55) Send failure: Broken pipe`, `http_code=000` (raw/close-after-413-observed.md:354-368) |
| `close`, Python | 보내기는 `Broken pipe`, 413(81바이트)을 받고 정상 EOF. 3회 같음 (raw/close-after-413-observed.md:207-223) | 보내기 `Broken pipe`, 413(81바이트)을 받은 뒤 읽기에서 **`Connection reset by peer`**. 3회 같음 (raw/close-after-413-observed.md:370-386) |
| `drain`, curl·Python | 6회 모두 413, Python은 정상 EOF (raw/close-after-413-observed.md:225-256) | 6회 모두 413, Python은 정상 EOF (raw/close-after-413-observed.md:388-419) |
| `shutdown`, curl·Python | 6회 모두 413 (raw/close-after-413-observed.md:258-289) | 6회 모두 413 (raw/close-after-413-observed.md:421-452) |

- curl이 보낸 양(`size_upload`)은 10MB보다 훨씬 적었다. 응답을 받고 업로드를 멈춘 것으로 보인다 (**판단**). Ubuntu의 `drain`·`shutdown`에서 서버가 버린 양은 약 60KB~1.7MB였다 (raw/close-after-413-observed.md:225-238, raw/close-after-413-observed.md:258-271). Python은 본문을 끝까지 보내므로 서버가 10MB(10485760바이트)를 모두 읽어 버렸다 (raw/close-after-413-observed.md:240-244).

## 해석 (판단)

- RFC 9112는 바로 닫으면 TCP reset 때문에 클라이언트가 마지막 응답을 읽지 못할 수 있다고 한다 (raw/rfc9112.txt:1539-1546). macOS의 `close`에서 실제로 reset이 생겼고, curl은 한 번 응답을 받지 못했다. Linux 컨테이너에서는 이번 6회에 문제가 없었지만 타이밍에 따라 달라질 수 있다고 본다.
- `drain`은 두 OS에서 12/12 모두 응답을 받았고, `shutdown`을 쓴 결과와 차이가 없었다. 이 측정 범위에서는 `shutdown` 없이 읽고 버리다가 닫는 것으로 충분했다.
- 끝까지 보내는 클라이언트는 본문 전부를 보내므로 버리는 단계에 시간·양의 상한이 필요하다. 시험 서버는 1초 무입력 또는 총 5초를 썼다.

## 과제 적용 (판단)

- `shutdown`이 허용 함수에 없으므로 (raw/subject.md:113) 본문을 다 읽지 않고 응답한 연결(413, 400 등)은 응답을 다 보낸 뒤 바로 닫지 않고, 읽기만 하면서 버리다가 상한에 닿거나 EOF가 오면 `close()`한다 → [[concepts/connection-management]].
- 버리는 단계도 `poll()`로 기다리는 non-blocking 처리여야 한다. 시험 서버는 한 연결만 다루는 단순한 구조라 그대로 쓸 수 없다.

> [!note] 측정 범위
> 모두 loopback이다. 실제 네트워크 지연, 여러 연결 동시 처리, 브라우저 클라이언트는 측정하지 않았다. Ubuntu 쪽 커널은 OrbStack VM(7.0.14)이라 평가 PC의 22.04 커널과 다르다.
