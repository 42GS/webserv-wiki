# Ubuntu 22.04 실측: 도구 버전, siege 설정, php-cgi·valgrind 재측정

> 측정일: 2026-10-15. 평가 PC가 Ubuntu 22.04라서(사용자 확인, 2026-10-15), Ubuntu 22.04 공식 Docker 이미지에 apt 기본 패키지를 설치하고 버전·설정을 출력하고, 24.04에서 했던 php-cgi·valgrind 측정을 같은 스크립트로 다시 실행했다. 출력은 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 컨테이너의 커널은 OrbStack VM의 Linux 커널이다. 평가 PC의 Ubuntu 22.04 커널과 다르다.

## 목적

1. 평가 PC와 같은 배포판의 기본 패키지 버전 (php-cgi, valgrind, python3, siege)
2. siege 기본 설정 파일과 실제 적용값
3. php-cgi·valgrind 측정(`raw/php-cgi-observed-env.md`, `raw/valgrind-observed-sigint.md`)이 22.04 패키지에서도 같은지
4. 위키의 siege 원본(`raw/siege.pod`, `raw/siegerc.in`, `raw/siege-sock.c`, 모두 master)과 설치된 4.0.7 태그 파일의 차이

## 환경

### Dockerfile

```
FROM ubuntu@sha256:5ec03bb3441e8b0bf3b4f9cd4629a1ae763010dc3035bb8da3ae6cf026486401
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends php-cgi g++ valgrind procps siege python3 && rm -rf /var/lib/apt/lists/*
```

## 명령

```
docker build -t webserv-u2204 .
docker run --rm -v $S/versions.sh:/versions.sh:ro webserv-u2204 /versions.sh > out-versions.txt 2>&1
docker run --rm -v $S/siege.sh:/siege.sh:ro -v $D:/in:ro webserv-u2204 /siege.sh > out-siege.txt 2>&1
docker run --rm -v $S/www:/www:ro -v $S/cases.sh:/cases.sh:ro webserv-u2204 /cases.sh > out-php.txt 2> err-php.txt
docker run --rm --user nobody -v $S/denied.sh:/denied.sh:ro webserv-u2204 /denied.sh > out-denied.txt 2> err-denied.txt
docker run --rm -v $S/sigleak.cpp:/src/sigleak.cpp:ro -v $S/run.sh:/run.sh:ro webserv-u2204 timeout 120 /run.sh > out-vg.txt 2>&1
for f in siege.pod:raw/siege.pod siegerc.in:raw/siegerc.in sock.c:raw/siege-sock.c; do a=${f%%:*}; b=${f#*:}; echo "\$ diff v4.0.7/$a $b"; diff $D/$a $b; echo; done > out-diff.txt
```

- `cases.sh`, `denied.sh`, `/www`의 PHP 파일은 `raw/php-cgi-observed-env.md`에 적은 것과 같은 파일이다 (`cmp`로 확인).
- `run.sh`, `sigleak.cpp`는 `raw/valgrind-observed-sigint.md`에 적은 것과 같은 파일이다 (`cmp`로 확인).
- `$D`에는 siege 저장소 태그 `v4.0.7`의 파일 3개를 받았다: `https://raw.githubusercontent.com/JoeDog/siege/v4.0.7/{doc/siege.pod,doc/siegerc.in,src/sock.c}`. SHA-256:

```
8179c046ffcbb8c1b1d85f10dbf5b891c3391bc30f93bb2ff10a7521156aed9d  siege.pod
65a886c6a5a059a2ccb4c45e7100c7d7d0c521a60434eb8890dea0c713acf175  siegerc.in
b594f481164acbcafb4dfe2fce5751ab8c1d3fdb9a5276b320c89aefd5b973c1  sock.c
```

### versions.sh

```sh
#!/bin/sh
# Print OS and tool versions, and the siege config values the wiki relies on.
grep PRETTY_NAME /etc/os-release
uname -sr
dpkg-query -W -f '${Package} ${Version}\n' php8.1-cgi valgrind g++ siege python3 2>&1
echo
php-cgi -v | head -1
valgrind --version
python3 --version
python3 -c 'import cgi; print("import cgi: ok")' 2>&1 | tail -1
siege -V 2>&1 | head -2
echo
echo "## siege config files"
ls -l /etc/siege/ 2>&1
echo "## non-comment lines of /etc/siege/siegerc"
grep -v '^[[:space:]]*#' /etc/siege/siegerc | grep -v '^[[:space:]]*$'
```

### siege.sh

```sh
#!/bin/sh
# First siege run creates ~/.siege/siege.conf; compare it with the system template, then show effective settings.
siege -V 2>&1
ls -l /root/.siege/
cmp /root/.siege/siege.conf /etc/siege/siegerc && echo "siege.conf == /etc/siege/siegerc"
echo "## diff <siege v4.0.7 doc/siegerc.in> /etc/siege/siegerc"
diff /in/siegerc.in /etc/siege/siegerc
echo "## siege -C"
siege -C 2>&1
```

## 출력: versions.sh

```
PRETTY_NAME="Ubuntu 22.04.5 LTS"
Linux 7.0.14-orbstack-00380-ga7e0a2dc9535
g++ 4:11.2.0-1ubuntu1
php8.1-cgi 8.1.2-1ubuntu2.26
python3 3.10.6-1~22.04.1
siege 4.0.7-1build3
valgrind 1:3.18.1-1ubuntu2

PHP 8.1.2-1ubuntu2.26 (cgi-fcgi) (built: Sep  2 2026 12:42:10)
valgrind-3.18.1
Python 3.10.12
import cgi: ok
New configuration template added to /root/.siege
Run siege -C to view the current settings in that file

## siege config files
total 28
-rw-r--r-- 1 root root 21245 Mar 25  2022 siegerc
-rw-r--r-- 1 root root   627 Mar 25  2022 urls.txt
## non-comment lines of /etc/siege/siegerc
verbose = true
color = on
quiet = false
json_output = true
show-logfile = true
logging = false
gmethod = HEAD
parser = true
nofollow = ad.doubleclick.net
nofollow = pagead2.googlesyndication.com
nofollow = ads.pubsqrd.com
nofollow = ib.adnxs.com
limit = 255
protocol = HTTP/1.1
chunked = true
cache = false
connection = close
concurrent = 25
delay = 0.0 
internet = false
benchmark = false
accept-encoding = gzip, deflate
url-escaping = true
unique = true
```

## 출력: siege.sh

```
New configuration template added to /root/.siege
Run siege -C to view the current settings in that file
SIEGE 4.0.7

Copyright (C) 2018 by Jeffrey Fulmer, et al.
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.

total 24
-rw-r--r-- 1 root root 21245 Oct 15 14:11 siege.conf
siege.conf == /etc/siege/siegerc
## diff <siege v4.0.7 doc/siegerc.in> /etc/siege/siegerc
19c19
< # logfile = $(HOME)/var/siege.log
---
> # logfile = $(HOME)/var/log/siege.log
89c89
< # Logfile, the default siege logfile is $PREFIX/var/siege.log This
---
> # Logfile, the default siege logfile is /var/log/siege.log This
## siege -C
CURRENT  SIEGE  CONFIGURATION
Mozilla/5.0 (unknown-aarch64-linux-gnu) Siege/4.0.7
Edit the resource file to change the settings.
----------------------------------------------
version:                        4.0.7
verbose:                        false
color:                          true
quiet:                          true
debug:                          false
protocol:                       HTTP/1.1
HTML parser:                    enabled
get method:                     HEAD
connection:                     close
concurrent users:               25
time to run:                    n/a
repetitions:                    n/a
socket timeout:                 30
cache enabled:                  false
accept-encoding:                gzip, deflate
delay:                          0.000 sec
internet simulation:            false
benchmark mode:                 false
failures until abort:           1024
named URL:                      none
URLs file:                      /etc/siege/urls.txt
thread limit:                   255
logging:                        false
log file:                       /var/log/log/siege.log
resource file:                  /root/.siege/siege.conf
timestamped output:             false
comma separated output:         false
allow redirects:                true
allow zero byte data:           true
allow chunked encoding:         true
upload unique files:            true
json output:                    true
no-follow:
 - ad.doubleclick.net
 - pagead2.googlesyndication.com
 - ads.pubsqrd.com
 - ib.adnxs.com
proxy auth:                     
www auth:                       
```

## 출력: siege v4.0.7 태그 파일과 raw(master) 파일의 diff

```
$ diff v4.0.7/siege.pod raw/siege.pod
216c216,220
< $_PROGRAM's urls.txt parser supports comments and variables.
---
> $_PROGRAM's urls.txt parser supports comments and variables. Since 
> $_PROGRAM uses the dollar sign ($) as a prefix for scalar variables,
> you should escape any variable you want to send to the server:
> 
>   https://$(HOST)/siege/jsoner.php POST {"price": "\$10 per mile"}
233c237
< proceding run. You could, for example, mark the file with your 
---
> proceeding run. You could, for example, mark the file with your
379c383
<       completes its transactions. Shown above, the test took 14.67 
---
>       completes its transactions. Shown above, the test took 58.57 

$ diff v4.0.7/siegerc.in raw/siegerc.in
30c30
< # Color mode: This option works in conjuction with verbose mode. 
---
> # Color mode: This option works in conjunction with verbose mode.
70c70
< json_output = true
---
> json_output = false
523a524,529
> # 
> # Auth URL. This feature is similar to the Login URL except it's invoked 
> # for form-based authentication after a 403 challenge. If the server responds
> # with 403 Forbidden, siege will attempt form based authentication with a
> # auth-url whose hostname matches the current hostname. You can set more than
> # one auth-url. Siege will attempt to select the appropriate one.
524a531,535
> # ex: auth-url = https://www.joedog.org/lemme-in POST user=ted&pass=excellent
> #
> # auth-url = 
> 
> #
554c565
< # certificate. It is not neccessary to specify a certificate in order to use
---
> # certificate. It is not necessary to specify a certificate in order to use

$ diff v4.0.7/sock.c raw/siege-sock.c
97c97
< #if defined(__GLIBC__)
---
> #if defined(HAVE_GETADDRINFO)
146c146
< #if defined(__GLIBC__)
---
> #if defined(HAVE_GETADDRINFO)
159c159
<       NOTIFY(ERROR, "%s", gai_strerror(res));
---
>       NOTIFY(ERROR, "%s: %s", gai_strerror(res), hn);
185c185
<    * Let's just hope gethostbyname is tread-safe
---
>    * Let's just hope gethostbyname is thread-safe
191c191
< #if !defined(__GLIBC__)
---
> #if !defined(HAVE_GETADDRINFO)
222c222
< #endif /* end of __GLIBC__ not defined */
---
> #endif /* end of HAVE_GETADDRINFO not defined */
236c236
< #if defined(__GLIBC__)
---
> #if defined(HAVE_GETADDRINFO)

```

## 출력: php-cgi cases.sh (stdout)

```
root
PHP 8.1.2-1ubuntu2.26 (cgi-fcgi) (built: Sep  2 2026 12:42:10)
Copyright (c) The PHP Group
Zend Engine v4.1.2, Copyright (c) Zend Technologies
    with Zend OPcache v8.1.2-1ubuntu2.26, Copyright (c), by Zend Technologies

## A. CGI meta-variables absent
$ env -i SCRIPT_FILENAME=/www/t.php /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/t.php
SCRIPT_FILENAME=/www/t.php
PATH_TRANSLATED=(unset)
PATH_INFO=(unset)
[exit=0]

## B. REDIRECT_STATUS
$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/ini.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

cgi.force_redirect='1'
cgi.redirect_status_env=''
cgi.fix_pathinfo='1'
cgi.discard_path='0'
doc_root=''
php_ini_loaded_file='/etc/php/8.1/cgi/php.ini'
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php /usr/bin/php-cgi  </dev/null
<b>Security Alert!</b> The PHP CGI cannot be accessed directly.

<p>This PHP CGI binary was compiled with force-cgi-redirect enabled.  This
means that a page will only be served up if the REDIRECT_STATUS CGI variable is
set, e.g. via an Apache Action directive.</p>
<p>For more information as to <i>why</i> this behaviour exists, see the <a href="http://php.net/security.cgi-bin">manual page for CGI security</a>.</p>
<p>For more information about changing this behaviour or re-enabling this webserver,
consult the installation file that came with this distribution, or visit 
<a href="http://php.net/install.windows">the manual page</a>.</p>
[exit=255]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php REDIRECT_STATUS=0 /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/t.php
SCRIPT_FILENAME=/www/t.php
PATH_TRANSLATED=(unset)
PATH_INFO=(unset)
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php REDIRECT_STATUS= /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/t.php
SCRIPT_FILENAME=/www/t.php
PATH_TRANSLATED=(unset)
PATH_INFO=(unset)
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php HTTP_REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
<b>Security Alert!</b> The PHP CGI cannot be accessed directly.

<p>This PHP CGI binary was compiled with force-cgi-redirect enabled.  This
means that a page will only be served up if the REDIRECT_STATUS CGI variable is
set, e.g. via an Apache Action directive.</p>
<p>For more information as to <i>why</i> this behaviour exists, see the <a href="http://php.net/security.cgi-bin">manual page for CGI security</a>.</p>
<p>For more information about changing this behaviour or re-enabling this webserver,
consult the installation file that came with this distribution, or visit 
<a href="http://php.net/install.windows">the manual page</a>.</p>
[exit=255]

## C. Which variable names the script
$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 PATH_TRANSLATED=/www/t.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/t.php
SCRIPT_FILENAME=/www/t.php
PATH_TRANSLATED=/www/t.php
PATH_INFO=(unset)
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php PATH_TRANSLATED=/www/other.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/t.php
SCRIPT_FILENAME=/www/t.php
PATH_TRANSLATED=/www/other.php
PATH_INFO=(unset)
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php PATH_TRANSLATED=/www/other.php REDIRECT_URL=/t.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/other.php
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php PATH_TRANSLATED=/www/other.php REDIRECT_STATUS=200 /usr/bin/php-cgi -d cgi.fix_pathinfo=0  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/other.php
[exit=0]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/t.php PATH_INFO=/x/y PATH_TRANSLATED=/www/x/y REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Content-type: text/html; charset=UTF-8

ran=/www/t.php
SCRIPT_FILENAME=/www/t.php
PATH_TRANSLATED=/www/x/y
PATH_INFO=/x/y
[exit=0]

## D. Script not found / not readable
$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/www/missing.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Status: 404 Not Found
Content-type: text/html; charset=UTF-8

No input file specified.
[exit=255]

$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Status: 404 Not Found
Content-type: text/html; charset=UTF-8

No input file specified.
[exit=255]

```

cases.sh의 stderr는 0바이트(비어 있음)였다.

## 출력: php-cgi denied.sh (stdout)

```
nobody
---------- 1 nobody nogroup 16 Oct 15 14:08 /tmp/denied.php
$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/tmp/denied.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Status: 403 Forbidden
Content-type: text/html; charset=UTF-8

Access denied.
[exit=255]
```

## 출력: php-cgi denied.sh (stderr)

```
PHP Warning:  Unknown: Failed to open stream: Permission denied in Unknown on line 0
```

## 출력: valgrind run.sh

```
valgrind-3.18.1
g++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0
## mode=default
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak default   (kill -INT <pid> after 2s)
[exit=130]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak default
==PID== 
==PID== 
==PID== Process terminating with default action of signal 2 (SIGINT)
==PID==    at 0x4B79C54: pause (pause.c:31)
==PID==    by 0x1089EF: main (sigleak.cpp:22)
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 73,784 bytes in 12 blocks
==PID==   total heap usage: 12 allocs, 0 frees, 73,784 bytes allocated
==PID== 
==PID== 80 bytes in 1 blocks are still reachable in loss record 1 of 3
==PID==    at 0x4866AE8: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x10897F: main (sigleak.cpp:15)
==PID== 
==PID== 1,000 bytes in 10 blocks are still reachable in loss record 2 of 3
==PID==    at 0x4866AE8: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x1089A3: main (sigleak.cpp:17)
==PID== 
==PID== 72,704 bytes in 1 blocks are still reachable in loss record 3 of 3
==PID==    at 0x4865058: malloc (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x492EB07: ??? (in /usr/lib/aarch64-linux-gnu/libstdc++.so.6.0.30)
==PID==    by 0x4005623: call_init (dl-init.c:70)
==PID==    by 0x4005623: call_init (dl-init.c:26)
==PID==    by 0x400572B: _dl_init (dl-init.c:117)
==PID==    by 0x4017CC7: ??? (in /usr/lib/aarch64-linux-gnu/ld-linux-aarch64.so.1)
==PID== 
==PID== LEAK SUMMARY:
==PID==    definitely lost: 0 bytes in 0 blocks
==PID==    indirectly lost: 0 bytes in 0 blocks
==PID==      possibly lost: 0 bytes in 0 blocks
==PID==    still reachable: 73,784 bytes in 12 blocks
==PID==         suppressed: 0 bytes in 0 blocks
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)

## mode=return
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak return   (kill -INT <pid> after 2s)
[exit=0]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak return
==PID== 
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 1,080 bytes in 11 blocks
==PID==   total heap usage: 12 allocs, 1 frees, 73,784 bytes allocated
==PID== 
==PID== 1,000 bytes in 10 blocks are indirectly lost in loss record 1 of 2
==PID==    at 0x4866AE8: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x1089A3: main (sigleak.cpp:17)
==PID== 
==PID== 1,080 (80 direct, 1,000 indirect) bytes in 1 blocks are definitely lost in loss record 2 of 2
==PID==    at 0x4866AE8: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x10897F: main (sigleak.cpp:15)
==PID== 
==PID== LEAK SUMMARY:
==PID==    definitely lost: 80 bytes in 1 blocks
==PID==    indirectly lost: 1,000 bytes in 10 blocks
==PID==      possibly lost: 0 bytes in 0 blocks
==PID==    still reachable: 0 bytes in 0 blocks
==PID==         suppressed: 0 bytes in 0 blocks
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 1 errors from 1 contexts (suppressed: 0 from 0)

## mode=exit
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak exit   (kill -INT <pid> after 2s)
[exit=0]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak exit
==PID== 
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 1,080 bytes in 11 blocks
==PID==   total heap usage: 12 allocs, 1 frees, 73,784 bytes allocated
==PID== 
==PID== 80 bytes in 1 blocks are still reachable in loss record 1 of 2
==PID==    at 0x4866AE8: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x10897F: main (sigleak.cpp:15)
==PID== 
==PID== 1,000 bytes in 10 blocks are still reachable in loss record 2 of 2
==PID==    at 0x4866AE8: operator new[](unsigned long) (in /usr/libexec/valgrind/vgpreload_memcheck-arm64-linux.so)
==PID==    by 0x1089A3: main (sigleak.cpp:17)
==PID== 
==PID== LEAK SUMMARY:
==PID==    definitely lost: 0 bytes in 0 blocks
==PID==    indirectly lost: 0 bytes in 0 blocks
==PID==      possibly lost: 0 bytes in 0 blocks
==PID==    still reachable: 1,080 bytes in 11 blocks
==PID==         suppressed: 0 bytes in 0 blocks
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)

## mode=cleanup
$ valgrind --leak-check=full --show-leak-kinds=all /tmp/sigleak cleanup   (kill -INT <pid> after 2s)
[exit=0]
==PID== Memcheck, a memory error detector
==PID== Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
==PID== Using Valgrind-3.18.1 and LibVEX; rerun with -h for copyright info
==PID== Command: /tmp/sigleak cleanup
==PID== 
==PID== 
==PID== HEAP SUMMARY:
==PID==     in use at exit: 0 bytes in 0 blocks
==PID==   total heap usage: 12 allocs, 12 frees, 73,784 bytes allocated
==PID== 
==PID== All heap blocks were freed -- no leaks are possible
==PID== 
==PID== For lists of detected and suppressed errors, rerun with: -s
==PID== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)

```
