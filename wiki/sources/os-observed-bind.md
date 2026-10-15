---
title: OS 실측 — bind 재시작·와일드카드 충돌
type: source
sources: [raw/os-observed-bind.md, raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# OS 실측 — bind 재시작·와일드카드 충돌

원본: `raw/os-observed-bind.md`. 테스트 프로그램(`reuse.c`, `wildcard.c`)을 macOS와 Ubuntu 24.04 Docker 컨테이너에서 실행한 소스·명령·출력을 그대로 담았다 (2026-10-15).

> [!note] 측정 환경의 한계
> 컨테이너의 커널은 OrbStack VM의 Linux 커널(`7.0.14-orbstack`)이다 (raw/os-observed-bind.md:24, raw/os-observed-bind.md:29). 평가 머신의 Ubuntu 커널에서 측정한 것이 아니다. 결과의 원인(커널 내부 동작)은 확인하지 않았고 결과만 기록한다.

## 결과

| 경우 | macOS | Ubuntu | 근거 |
|---|---|---|---|
| [A] listener에 `SO_REUSEADDR` 없음, 서버가 먼저 연결을 닫은 직후 같은 포트로 재bind | 옵션 없으면 `EADDRINUSE`, 켜면 성공 | **옵션을 켜도 `EADDRINUSE`** | raw/os-observed-bind.md:196-197, raw/os-observed-bind.md:213-214 |
| [B] 같은 조건, 클라이언트가 먼저 닫음 | 둘 다 성공 | 둘 다 성공 | raw/os-observed-bind.md:200-201, raw/os-observed-bind.md:217-218 |
| [C] 처음 listener부터 `SO_REUSEADDR`, 서버가 먼저 닫은 직후 재bind | 옵션 없으면 실패, 켜면 성공 | 옵션 없으면 실패, 켜면 성공 | raw/os-observed-bind.md:204-205, raw/os-observed-bind.md:221-222 |
| 같은 `127.0.0.1:P`를 두 소켓이 listen (둘 다 옵션 켬) | 두 번째 `EADDRINUSE` | 두 번째 `EADDRINUSE` | raw/os-observed-bind.md:246-247, raw/os-observed-bind.md:271-272 |
| `0.0.0.0:P`와 `127.0.0.1:P` (옵션 없음, 순서 무관) | 두 번째 `EADDRINUSE` | 두 번째 `EADDRINUSE` | raw/os-observed-bind.md:230-235, raw/os-observed-bind.md:255-260 |
| `0.0.0.0:P`와 `127.0.0.1:P` (둘 다 옵션 켬, 순서 무관) | **둘 다 성공** | **두 번째 `EADDRINUSE`** | raw/os-observed-bind.md:238-243, raw/os-observed-bind.md:263-268 |

## 과제 적용 (판단)

- 모든 listen 소켓에 `bind` 전에 `setsockopt(SO_REUSEADDR)`를 켠다. `setsockopt`는 허용 함수다 (raw/subject.md:113). Ubuntu에서는 처음 listener부터 옵션이 켜져 있어야 재시작 직후 bind가 된다 ([A]와 [C]의 차이).
- 옵션을 켜도 같은 `IP:port`를 이미 listen 중이면 실패하므로, 평가의 "같은 포트로 webserv 여러 개 실행"(raw/evaluation-sheet-en.md:109)은 여전히 `bind` 실패로 드러난다.
- `0.0.0.0:P`와 특정 IP의 `:P`를 함께 설정하면 OS마다 결과가 다르다. 설정 파싱 단계에서 겹침으로 거부해 양쪽에서 같게 동작하게 한다 → [[concepts/configuration-file]].
