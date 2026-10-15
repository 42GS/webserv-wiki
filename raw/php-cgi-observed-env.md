# php-cgi 실측: 실행할 파일을 찾는 변수와 `REDIRECT_STATUS`

> 측정일: 2026-10-15. Ubuntu 24.04 공식 Docker 이미지에 `php-cgi` 패키지를 설치하고, 환경 변수를 바꿔 가며 php-cgi를 직접 실행한 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 웹 서버 없이 `env -i`로 CGI 환경을 흉내 냈다. stdin은 `/dev/null`이다.

## 목적

1. `REDIRECT_STATUS`의 값에 조건이 있는지
2. 실행할 파일을 `SCRIPT_FILENAME`과 `PATH_TRANSLATED` 중 어느 것으로 찾는지
3. 스크립트가 없거나 읽을 수 없을 때의 출력

## 환경

```
base image: ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55   (ubuntu:24.04, arm64)
package: php8.3-cgi 8.3.6-0ubuntu0.24.04.11
```

### Dockerfile

```
FROM ubuntu@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends php-cgi && rm -rf /var/lib/apt/lists/*
```

## 파일 (`/www`, 읽기 전용 마운트)

### t.php

```php
<?php
echo "ran=", __FILE__, "\n";
foreach (array('SCRIPT_FILENAME', 'PATH_TRANSLATED', 'PATH_INFO') as $k)
    echo $k, "=", isset($_SERVER[$k]) ? $_SERVER[$k] : '(unset)', "\n";
```

### ini.php

```php
<?php
foreach (array('cgi.force_redirect', 'cgi.redirect_status_env', 'cgi.fix_pathinfo', 'cgi.discard_path', 'doc_root') as $k)
    echo $k, "=", var_export(ini_get($k), true), "\n";
echo "php_ini_loaded_file=", var_export(php_ini_loaded_file(), true), "\n";
```

### other.php

```php
<?php
echo "ran=", __FILE__, "\n";
```

`/www/missing.php`는 없다.

## 명령

```
docker build -t webserv-phpcgi-test .
docker run --rm -v $S/www:/www:ro -v $S/cases.sh:/cases.sh:ro webserv-phpcgi-test /cases.sh > out.txt 2> err.txt
docker run --rm --user nobody -v $S/denied.sh:/denied.sh:ro webserv-phpcgi-test /denied.sh > out-denied.txt 2> err-denied.txt
```

### cases.sh

```sh
#!/bin/sh
# Run php-cgi with a clean environment per case; print the command, full output, exit status.
B="GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1"
run() {
    echo "\$ env -i $*  </dev/null"
    env -i "$@" </dev/null
    echo "[exit=$?]"
    echo
}
id -un
/usr/bin/php-cgi -v
echo
echo "## A. CGI meta-variables absent"
run SCRIPT_FILENAME=/www/t.php /usr/bin/php-cgi
echo "## B. REDIRECT_STATUS"
run $B SCRIPT_FILENAME=/www/ini.php REDIRECT_STATUS=200 /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php REDIRECT_STATUS=0 /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php REDIRECT_STATUS= /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php HTTP_REDIRECT_STATUS=200 /usr/bin/php-cgi
echo "## C. Which variable names the script"
run $B PATH_TRANSLATED=/www/t.php REDIRECT_STATUS=200 /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php PATH_TRANSLATED=/www/other.php REDIRECT_STATUS=200 /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php PATH_TRANSLATED=/www/other.php REDIRECT_URL=/t.php REDIRECT_STATUS=200 /usr/bin/php-cgi
run $B SCRIPT_FILENAME=/www/t.php PATH_TRANSLATED=/www/other.php REDIRECT_STATUS=200 /usr/bin/php-cgi -d cgi.fix_pathinfo=0
run $B SCRIPT_FILENAME=/www/t.php PATH_INFO=/x/y PATH_TRANSLATED=/www/x/y REDIRECT_STATUS=200 /usr/bin/php-cgi
echo "## D. Script not found / not readable"
run $B SCRIPT_FILENAME=/www/missing.php REDIRECT_STATUS=200 /usr/bin/php-cgi
run $B REDIRECT_STATUS=200 /usr/bin/php-cgi
```

### denied.sh

```sh
#!/bin/sh
# Run as an unprivileged user: a script file with mode 000 cannot be opened.
id -un
printf '<?php echo "x";\n' > /tmp/denied.php
chmod 000 /tmp/denied.php
ls -l /tmp/denied.php
echo "\$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/tmp/denied.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null"
env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/tmp/denied.php REDIRECT_STATUS=200 /usr/bin/php-cgi </dev/null
echo "[exit=$?]"
```

## 출력: cases.sh (stdout)

```
root
PHP 8.3.6 (cgi-fcgi) (built: Sep  2 2026 12:56:02)
Copyright (c) The PHP Group
Zend Engine v4.3.6, Copyright (c) Zend Technologies
    with Zend OPcache v8.3.6, Copyright (c), by Zend Technologies

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
php_ini_loaded_file='/etc/php/8.3/cgi/php.ini'
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

## 출력: denied.sh (stdout)

```
nobody
---------- 1 nobody nogroup 16 Oct 15 12:35 /tmp/denied.php
$ env -i GATEWAY_INTERFACE=CGI/1.1 REQUEST_METHOD=GET SERVER_PROTOCOL=HTTP/1.1 SCRIPT_FILENAME=/tmp/denied.php REDIRECT_STATUS=200 /usr/bin/php-cgi  </dev/null
Status: 403 Forbidden
Content-type: text/html; charset=UTF-8

Access denied.
[exit=255]
```

## 출력: denied.sh (stderr)

```
PHP Warning:  PHP Request Startup: Failed to open stream: Permission denied in Unknown on line 0
```
