---
title: Ubuntu 22.04 기본 fd 한도 실측 (systemd DefaultLimitNOFILE)
type: source
sources: [raw/ubuntu2204-observed-nofile.md]
updated: 2026-10-18
---

# Ubuntu 22.04 기본 fd 한도 실측

원본: `raw/ubuntu2204-observed-nofile.md`. 깨끗한 `ubuntu:22.04` 이미지에 systemd 패키지(249.11-0ubuntu3.23)를 설치하고 설정 파일을 읽은 것이다 (raw/ubuntu2204-observed-nofile.md:3, raw/ubuntu2204-observed-nofile.md:9). 컨테이너에서는 systemd가 돌지 않으므로 실제로 적용된 값이 아니라 패키지의 기본 설정이다 (raw/ubuntu2204-observed-nofile.md:4).

## 핵심

- `/etc/systemd/system.conf`의 항목은 컴파일 시점의 기본값을 보여 준다고 파일 첫머리에 적혀 있다 (raw/ubuntu2204-observed-nofile.md:11).
- 그 파일의 기본값은 `DefaultLimitNOFILE=1024:524288`이다 (raw/ubuntu2204-observed-nofile.md:16). systemd가 띄우는 프로세스의 fd 한도 기본이 soft 1024, hard 524288이라는 뜻으로 읽었다 (**판단**, `systemd-system.conf(5)`는 읽지 않음).
- `/etc/systemd/user.conf`의 `DefaultLimitNOFILE=`은 비어 있고 (raw/ubuntu2204-observed-nofile.md:17), `/etc/security/limits.conf`에는 `nofile` 설정이 없다(설명 주석뿐, raw/ubuntu2204-observed-nofile.md:19).

## 과제 적용

- 평가 PC 터미널의 `ulimit -n`은 1024일 가능성이 높다 (**판단**). 데스크톱 로그인 셸이 이 기본을 물려받는지와 평가 PC가 설정을 바꿨는지는 **미확인**이다. 확인: 평가 때 `ulimit -n`.
- 1024면 동시 연결은 약 1000개까지다. fd가 다 차도 서버는 쉬지 않고 돌지 않고 연결이 풀리는 대로 받는다 → [[analysis/test-plan]] N-26, 8절 R5.

## 관련

- [[sources/ubuntu2204-observed-tools]], [[concepts/resilience]]
