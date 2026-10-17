# 실측: Ubuntu 22.04 패키지의 기본 fd 한도 (systemd `DefaultLimitNOFILE`)

> 측정일: 2026-10-18. 깨끗한 `ubuntu:22.04` Docker 이미지에 `apt-get install systemd`로 패키지를 설치하고, 함께 설치된 설정 파일을 읽었다. 명령과 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 컨테이너에서는 systemd가 실행되지 않으므로 실제로 적용된 한도가 아니라 패키지의 기본 설정을 읽은 것이다. 평가 PC의 데스크톱 셸이 이 값을 물려받는지는 이 파일로 알 수 없다.

```
$ docker run --rm ubuntu:22.04 sh -c 'apt-get update && apt-get install -y systemd; ...'
$ dpkg -l systemd | tail -1
ii  systemd        249.11-0ubuntu3.23 arm64        system and service manager
$ sed -n 8,11p /etc/systemd/system.conf
# Entries in this file show the compile time defaults. Local configuration
# should be created by either modifying this file, or by creating "drop-ins" in
# the system.conf.d/ subdirectory. The latter is generally recommended.
# Defaults can be restored by simply deleting this file and all drop-ins.
$ grep -n NOFILE /etc/systemd/system.conf /etc/systemd/user.conf
/etc/systemd/system.conf:64:#DefaultLimitNOFILE=1024:524288
/etc/systemd/user.conf:40:#DefaultLimitNOFILE=
$ grep -n nofile /etc/security/limits.conf
27:#        - nofile - max number of open file descriptors
```
