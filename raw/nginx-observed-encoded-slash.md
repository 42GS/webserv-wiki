# NGINX 실측: 경로의 `%2F`(인코딩된 `/`)

> 측정일: 2026-10-15. 아래 설정·파일로 NGINX 공식 Docker 이미지를 띄우고, 같은 Docker 네트워크의 curl 컨테이너에서 요청한 응답을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 응답은 요청마다 앞 400바이트까지만 출력했다.

## 목적

1. 경로의 `%2F`를 디코딩해 경로 구분자로 쓰는지 (파일 매핑, location 매칭, `$uri`)
2. `%2F`와 `..`·연속 `/`가 섞였을 때 디코딩과 정규화의 순서

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

    location /a/ {
        add_header X-Loc a always;
    }

    location /echo/ {
        default_type text/plain;
        return 200 "uri=$uri request_uri=$request_uri\n";
    }

    location / {
        add_header X-Loc root always;
    }
}
```

## 파일 (`/usr/share/nginx/html`)

```
index.html   <p>root</p>
a/b.txt      file a/b
```

## 명령

```
docker network create ngx2f
docker run -d --rm --name web2f --network ngx2f --network-alias web -v $S/html:/usr/share/nginx/html:ro -v $S/default.conf:/etc/nginx/conf.d/default.conf:ro nginx@sha256:908cb0471582493fcf76dcc97e8e52cf9a43a72bcfcb4fe06e6390fb89a19577
docker exec web2f nginx -v
docker run --rm --network ngx2f -v $S/requests.sh:/requests.sh:ro --entrypoint sh curlimages/curl@sha256:a134550be58ab783810e613ae96fd253c38f7bdd16d9bf9be350700c7a29ac06 /requests.sh
docker logs web2f
```

### requests.sh

```sh
#!/bin/sh
# Each request: print the command, then the response head (and short body).
req() {
    echo "\$ curl -sS -i --path-as-is $*"
    curl -sS -i --path-as-is "$@" | head -c 400
    echo
    echo
}
req http://web/a/b.txt
req http://web/a%2Fb.txt
req http://web/a%2fb.txt
req http://web/echo/x%2Fy
req http://web/echo/a%2F..%2Fb
req http://web/echo/a/../b
req http://web/echo/a%2F%2Fb
req http://web/a%2F..%2F..%2Fetc%2Fpasswd
```

## 출력 (curl)

```
$ curl -sS -i --path-as-is http://web/a/b.txt
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 9
Last-Modified: Thu, 15 Oct 2026 08:29:25 GMT
Connection: keep-alive
ETag: "6ad08ee5-9"
X-Loc: a
Accept-Ranges: bytes

file a/b


$ curl -sS -i --path-as-is http://web/a%2Fb.txt
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 9
Last-Modified: Thu, 15 Oct 2026 08:29:25 GMT
Connection: keep-alive
ETag: "6ad08ee5-9"
X-Loc: a
Accept-Ranges: bytes

file a/b


$ curl -sS -i --path-as-is http://web/a%2fb.txt
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 9
Last-Modified: Thu, 15 Oct 2026 08:29:25 GMT
Connection: keep-alive
ETag: "6ad08ee5-9"
X-Loc: a
Accept-Ranges: bytes

file a/b


$ curl -sS -i --path-as-is http://web/echo/x%2Fy
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 38
Connection: keep-alive

uri=/echo/x/y request_uri=/echo/x%2Fy


$ curl -sS -i --path-as-is http://web/echo/a%2F..%2Fb
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 41
Connection: keep-alive

uri=/echo/b request_uri=/echo/a%2F..%2Fb


$ curl -sS -i --path-as-is http://web/echo/a/../b
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 37
Connection: keep-alive

uri=/echo/b request_uri=/echo/a/../b


$ curl -sS -i --path-as-is http://web/echo/a%2F%2Fb
HTTP/1.1 200 OK
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
Content-Type: text/plain
Content-Length: 41
Connection: keep-alive

uri=/echo/a/b request_uri=/echo/a%2F%2Fb


$ curl -sS -i --path-as-is http://web/a%2F..%2F..%2Fetc%2Fpasswd
HTTP/1.1 400 Bad Request
Server: nginx/1.30.6
Date: Thu, 15 Oct 2026 08:29:38 GMT
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


```

## NGINX 로그 (`docker logs web2f`, 시작 알림 줄 제외)

```
10-listen-on-ipv6-by-default.sh: info: can not modify /etc/nginx/conf.d/default.conf (read-only file system?)
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /a/b.txt HTTP/1.1" 200 9 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /a%2Fb.txt HTTP/1.1" 200 9 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /a%2Fb.txt HTTP/1.1" 200 9 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /echo/x%2Fy HTTP/1.1" 200 38 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /echo/a%2F..%2Fb HTTP/1.1" 200 41 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /echo/a/../b HTTP/1.1" 200 37 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /echo/a%2F%2Fb HTTP/1.1" 200 41 "-" "curl/8.23.0" "-"
192.168.147.3 - - [15/Oct/2026:08:29:38 +0000] "GET /a%2F..%2F..%2Fetc%2Fpasswd HTTP/1.1" 400 157 "-" "-" "-"
```
