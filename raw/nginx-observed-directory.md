# NGINX 실측: 디렉토리 요청과 `..` 경로

> 측정일: 2026-10-15. 아래 설정·파일로 NGINX 공식 Docker 이미지를 띄우고, 같은 Docker 네트워크의 curl 컨테이너에서 요청한 응답을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 응답 본문은 요청마다 앞 600바이트까지만 출력했다.

## 목적

1. 끝에 `/`가 없는 디렉토리 요청에 301을 보내는지, `Location` 형식
2. 리스팅 off(`autoindex off`) + index 파일 없는 디렉토리의 응답 코드
3. (추가) `..`로 root 밖을 가리키는 요청의 응답 코드

## 환경

```
nginx version: nginx/1.30.6
image: nginx@sha256:908cb0471582493fcf76dcc97e8e52cf9a43a72bcfcb4fe06e6390fb89a19577
curl image: curlimages/curl@sha256:a134550be58ab783810e613ae96fd253c38f7bdd16d9bf9be350700c7a29ac06
curl 8.23.0 (aarch64-unknown-linux-musl) libcurl/8.23.0 OpenSSL/3.5.9 zlib/1.3.2 brotli/1.2.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.5 libssh2/1.11.1 nghttp2/1.70.0 mit-krb5/1.22.2
```

## 설정 (`/etc/nginx/conf.d/default.conf`)

```
server {
    listen       80;
    server_name  localhost;
    root         /usr/share/nginx/html;

    location / {
        autoindex off;
    }
}
```

## 파일 (`/usr/share/nginx/html`)

```
index.html            <p>root</p>
noindex/a.txt         file a          (index 파일 없음)
withindex/index.html  <p>index</p>
```

## 명령

```
docker network create ngxtest
docker run -d --rm --name web --network ngxtest -v $S/html:/usr/share/nginx/html:ro -v $S/default.conf:/etc/nginx/conf.d/default.conf:ro nginx:stable
docker run --rm --network ngxtest -v $S/requests.sh:/requests.sh:ro --entrypoint sh curlimages/curl /requests.sh
docker logs web
```

### requests.sh

```sh
#!/bin/sh
# Each request: print the command, then the full response head (and short body).
req() {
    echo "\$ curl -sS -i --path-as-is $*"
    curl -sS -i --path-as-is "$@" | head -c 600
    echo
    echo
}
req http://web/withindex
req http://web/withindex/
req http://web/noindex
req http://web/noindex/
req http://web/noindex/a.txt
req http://web/../etc/passwd
req http://web/%2e%2e/etc/passwd
req http://web/noindex/../../etc/passwd
req http://web/missing
```

## 출력 (curl)

```
$ curl -sS -i --path-as-is http://web/withindex
HTTP/1.1 301 Moved Permanently
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 169
Location: http://web/withindex/
Connection: keep-alive

<html>
<head><title>301 Moved Permanently</title></head>
<body>
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>


$ curl -sS -i --path-as-is http://web/withindex/
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 13
Last-Modified: Thu, 15 Oct 2026 03:46:00 GMT
Connection: keep-alive
ETag: "6ad04c78-d"
Accept-Ranges: bytes

<p>index</p>


$ curl -sS -i --path-as-is http://web/noindex
HTTP/1.1 301 Moved Permanently
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 169
Location: http://web/noindex/
Connection: keep-alive

<html>
<head><title>301 Moved Permanently</title></head>
<body>
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>


$ curl -sS -i --path-as-is http://web/noindex/
HTTP/1.1 403 Forbidden
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 153
Connection: keep-alive

<html>
<head><title>403 Forbidden</title></head>
<body>
<center><h1>403 Forbidden</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>


$ curl -sS -i --path-as-is http://web/noindex/a.txt
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/plain
Content-Length: 7
Last-Modified: Thu, 15 Oct 2026 03:46:00 GMT
Connection: keep-alive
ETag: "6ad04c78-7"
Accept-Ranges: bytes

file a


$ curl -sS -i --path-as-is http://web/../etc/passwd
HTTP/1.1 400 Bad Request
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 157
Connection: close

<html>
<head><title>400 Bad Request</title></head>
<body>
<center><h1>400 Bad Request</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>


$ curl -sS -i --path-as-is http://web/%2e%2e/etc/passwd
HTTP/1.1 400 Bad Request
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 157
Connection: close

<html>
<head><title>400 Bad Request</title></head>
<body>
<center><h1>400 Bad Request</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>


$ curl -sS -i --path-as-is http://web/noindex/../../etc/passwd
HTTP/1.1 400 Bad Request
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 157
Connection: close

<html>
<head><title>400 Bad Request</title></head>
<body>
<center><h1>400 Bad Request</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>


$ curl -sS -i --path-as-is http://web/missing
HTTP/1.1 404 Not Found
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 03:46:25 GMT
Content-Type: text/html
Content-Length: 153
Connection: keep-alive

<html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.30.6</center>
</body>
</html>
```

## NGINX 로그 (`docker logs web`, 시작 알림 줄 제외)

```
10-listen-on-ipv6-by-default.sh: info: can not modify /etc/nginx/conf.d/default.conf (read-only file system?)
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /withindex HTTP/1.1" 301 169 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /withindex/ HTTP/1.1" 200 13 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /noindex HTTP/1.1" 301 169 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /noindex/ HTTP/1.1" 403 153 "-" "curl/8.23.0" "-"
2026/10/15 03:46:25 [error] 25#25: *4 directory index of "/usr/share/nginx/html/noindex/" is forbidden, client: 192.168.147.3, server: localhost, request: "GET /noindex/ HTTP/1.1", host: "web"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /noindex/a.txt HTTP/1.1" 200 7 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /../etc/passwd HTTP/1.1" 400 157 "-" "-" "-"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /%2E%2E/etc/passwd HTTP/1.1" 400 157 "-" "-" "-"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /noindex/../../etc/passwd HTTP/1.1" 400 157 "-" "-" "-"
2026/10/15 03:46:25 [error] 20#20: *9 open() "/usr/share/nginx/html/missing" failed (2: No such file or directory), client: 192.168.147.3, server: localhost, request: "GET /missing HTTP/1.1", host: "web"
192.168.147.3 - - [15/Oct/2026:03:46:25 +0000] "GET /missing HTTP/1.1" 404 153 "-" "curl/8.23.0" "-"
```
