---
title: siege 실측 (Ubuntu 22.04, siege 4.0.7) — 응답 없는 서버, 요청 헤더, -b와 -d
type: source
sources: [raw/siege-observed-ubuntu2204.md, raw/siege-sock.c, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# siege 실측 (Ubuntu 22.04, siege 4.0.7) — 응답 없는 서버, 요청 헤더, `-b`와 `-d`

원본: `raw/siege-observed-ubuntu2204.md`. 평가 PC와 같은 Ubuntu 22.04 이미지의 apt 패키지 siege 4.0.7을, 같은 컨테이너에 띄운 Python 테스트 서버에 대해 실행한 출력을 그대로 담았다 (2026-10-15, raw/siege-observed-ubuntu2204.md:3-4).

- 테스트 서버 `srv.py`는 두 모드다. `echo`는 요청 헤더를 출력하고 200으로 답한 뒤 닫는다. `silent`는 요청을 읽기만 하고 답하지 않은 채 소켓을 열어 둔다 (raw/siege-observed-ubuntu2204.md:15-17).
- 받은 목적: [[sources/siege-sock]]의 판단 2건과 **미확인**(응답 대기에 timeout이 실제로 걸리는지, `O_NDELAY`와 `O_NONBLOCK`이 같은지), [[concepts/testing]]의 **미확인**(부하 요청의 `Connection: close`, `-b`와 `-d`).

## 결과

| 질문 | 결과 | 근거 |
|---|---|---|
| `O_NDELAY`와 `O_NONBLOCK` | glibc 헤더에서 `O_NDELAY`는 `O_NONBLOCK`으로 정의된다 (aarch64 헤더) | raw/siege-observed-ubuntu2204.md:104-105 |
| 응답 없는 서버, 기본 설정 (`socket timeout` 30) | siege가 끝나지 않고 150초 뒤 `timeout 150`에 의해 종료됨. 거래 0건 | raw/siege-observed-ubuntu2204.md:197-211 |
| 응답 없는 서버, `timeout = 5` 설정 파일 (`-R`) | 마찬가지로 150초 뒤 외부 `timeout`으로 종료됨 | raw/siege-observed-ubuntu2204.md:213-229 |
| 위 설정 파일이 적용됐는지 | `siege -R /tmp/rc5 -C`에서 `socket timeout: 5` | raw/siege-observed-ubuntu2204.md:251-256 |
| 부하 요청 헤더 | `GET / HTTP/1.1`, `Host`, `Accept`, `Accept-Encoding`, `User-Agent`, `Connection: close`. `-b`로 보낸 요청도 같음 | raw/siege-observed-ubuntu2204.md:140-161 |
| `-d10`만 | 3회에 17.25초 | raw/siege-observed-ubuntu2204.md:164-178 |
| `-b -d10` | 3회에 0.01초 | raw/siege-observed-ubuntu2204.md:180-194 |

- 응답 없는 서버 측 로그에는 두 요청이 각각 한 번씩만 찍혔다 (raw/siege-observed-ubuntu2204.md:231-245). siege가 기다리는 동안 다시 연결하거나 재시도하지 않았다.
- `protocol` 줄이 없는 설정 파일(`timeout = 5`만 있음)을 쓰면 요청이 `HTTP/1.0`으로 나갔다 (raw/siege-observed-ubuntu2204.md:239-240, raw/siege-observed-ubuntu2204.md:253). 기본 설정 파일에는 `protocol = HTTP/1.1`이 있다 → [[sources/ubuntu2204-observed-tools]].

## 소스 판단과 맞춰 본 것

- [[sources/siege-sock]]은 연결 뒤 `O_NDELAY`를 지워 소켓이 blocking이 되고, 준비 검사가 읽기·쓰기 집합을 함께 봐서 응답 대기에 `timeout`이 실효가 없을 수 있다고 판단했다 (raw/siege-sock.c:290, raw/siege-sock.c:370-374, raw/siege-sock.c:485-486). 헤더 정의와 150초 대기가 이 판단과 맞는다.
- 그 밖의 타이머가 있더라도 150초 안에는 작동하지 않았다. 150초보다 길게 기다리면 끝나는지는 측정하지 않았다.

## 과제 적용 (판단)

- siege는 응답하지 않는 연결을 적어도 150초 동안 스스로 끊지 않았다. 서버가 요청 하나에 답하지 않으면 그 siege 사용자는 멈춘 채로 남고, `-r` 테스트는 끝나지 않는다. 평가표의 "hanging connection 없음"(raw/evaluation-sheet-en.md:116)은 서버가 모든 요청에 반드시 응답하거나 연결을 닫아야 지킬 수 있다 → [[concepts/resilience]].
- siege는 매 요청에 `Connection: close`를 보내므로 서버는 응답 후 연결을 닫는다 → [[concepts/connection-management]].
- 평가표는 availability 확인에 `-b`를 쓴다 (raw/evaluation-sheet-en.md:114). `-d`를 함께 줘도 지연이 없다.

> [!note] 측정 범위
> 서버와 siege가 같은 컨테이너의 loopback으로 통신했고, `-c1`만 측정했다. 헤더는 aarch64 경로로 확인했다. x86_64 경로(`/usr/include/x86_64-linux-gnu/bits/fcntl-linux.h`)는 확인하지 않았다.
