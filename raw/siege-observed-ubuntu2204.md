# siege 실측 (Ubuntu 22.04, siege 4.0.7): 응답 없는 서버, 요청 헤더, `-b`와 `-d`

> 측정일: 2026-10-15. `raw/ubuntu2204-observed-tools.md`와 같은 Docker 이미지(`webserv-u2204`, ubuntu:22.04 + apt `siege 4.0.7-1build3`, `python3`)에서, 컨테이너 안에 Python 테스트 서버를 띄우고 siege를 실행한 출력을 그대로 붙였다.
> 측정: Claude Code 세션 (위키 유지 LLM). 서버와 siege는 같은 컨테이너의 `127.0.0.1`로 통신했다. 컨테이너 커널은 OrbStack VM의 Linux 커널이다.

## 목적

1. 응답하지 않는 서버에 대해 siege의 `timeout` 설정이 요청을 끝내는지
2. `O_NDELAY`와 `O_NONBLOCK`이 같은 값인지 (glibc 헤더)
3. siege가 보내는 요청 헤더 (`Connection`, 프로토콜 버전)
4. `-b`와 `-d`를 함께 줄 때 어느 쪽이 적용되는지

## 테스트 서버 (`srv.py`)

```python
# Minimal test server for observing siege.
#   echo   : read each request head, print it, answer 200 and close.
#   silent : accept and read, but never answer; keep the socket open.
import socket, sys, time

mode, port = sys.argv[1], int(sys.argv[2])
ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ls.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ls.bind(("127.0.0.1", port))
ls.listen(16)
held = []
start = time.time()
while True:
    c, _ = ls.accept()
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = c.recv(4096)
        if not chunk:
            break
        data += chunk
    head = data.split(b"\r\n\r\n")[0].decode("latin-1")
    print("[srv %.1fs] request:" % (time.time() - start), flush=True)
    for line in head.split("\r\n"):
        print("    " + line, flush=True)
    if mode == "echo":
        c.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 3\r\nConnection: close\r\n\r\nok\n")
        c.close()
    else:
        held.append(c)
```

## 명령

```
docker run --rm -v $S:/t:ro webserv-u2204 timeout 400 /t/run.sh > out.txt 2>&1
docker run --rm -v $S:/t:ro webserv-u2204 /t/rc.sh
```

### run.sh

```sh
#!/bin/sh
# Observe siege 4.0.7 against a local test server. Each case prints the command and elapsed seconds.
siege -V 2>&1 | grep SIEGE
grep -n "define O_NDELAY\|define O_NONBLOCK\|define __O_NONBLOCK\|define O_NONBLOCK" /usr/include/*/bits/fcntl-linux.h /usr/include/*/bits/fcntl.h 2>/dev/null
echo
case_run() {
    echo "\$ $*"
    t0=$(date +%s)
    "$@" 2>&1 | grep -v '^\*\*\* SIEGE\|^\*\* Preparing\|^The server is now under siege\|^$'
    echo "[elapsed $(( $(date +%s) - t0 ))s]"
    echo
}
echo "## 1. request headers (echo server)"
python3 -u /t/srv.py echo 8081 > /tmp/echo.log 2>&1 &
sleep 1
case_run siege -c1 -r2 http://127.0.0.1:8081/
case_run siege -b -c1 -r1 http://127.0.0.1:8081/
echo "### server log"
cat /tmp/echo.log
echo
echo "## 2. -d with and without -b (echo server)"
case_run siege -c1 -r3 -d10 http://127.0.0.1:8081/
case_run siege -b -c1 -r3 -d10 http://127.0.0.1:8081/
echo "## 3. server that never answers"
python3 -u /t/srv.py silent 8082 > /tmp/silent.log 2>&1 &
sleep 1
case_run timeout 150 siege -c1 -r1 http://127.0.0.1:8082/
printf 'timeout = 5\n' > /tmp/rc5
case_run timeout 150 siege -R /tmp/rc5 -c1 -r1 http://127.0.0.1:8082/
echo "### server log"
cat /tmp/silent.log
```

### rc.sh

```sh
#!/bin/sh
# Show the effective settings when siege reads a resource file that only sets timeout = 5.
printf 'timeout = 5\n' > /tmp/rc5
echo "\$ siege -R /tmp/rc5 -C"
siege -R /tmp/rc5 -C 2>&1 | grep -i "resource file\|socket timeout\|protocol\|connection"
```

## 출력: run.sh

```
SIEGE 4.0.7
/usr/include/aarch64-linux-gnu/bits/fcntl-linux.h:62:# define O_NONBLOCK	  04000
/usr/include/aarch64-linux-gnu/bits/fcntl-linux.h:65:# define O_NDELAY	O_NONBLOCK

## 1. request headers (echo server)
$ siege -c1 -r2 http://127.0.0.1:8081/
{	"transactions":			           2,
	"availability":			      100.00,
	"elapsed_time":			        0.03,
	"data_transferred":		        0.00,
	"response_time":		        0.00,
	"transaction_rate":		       66.67,
	"throughput":			        0.00,
	"concurrency":			        0.00,
	"successful_transactions":	           2,
	"failed_transactions":		           0,
	"longest_transaction":		        0.00,
	"shortest_transaction":		        0.00
}
[elapsed 0s]

$ siege -b -c1 -r1 http://127.0.0.1:8081/
{	"transactions":			           1,
	"availability":			      100.00,
	"elapsed_time":			        0.01,
	"data_transferred":		        0.00,
	"response_time":		        0.00,
	"transaction_rate":		      100.00,
	"throughput":			        0.00,
	"concurrency":			        0.00,
	"successful_transactions":	           1,
	"failed_transactions":		           0,
	"longest_transaction":		        0.00,
	"shortest_transaction":		        0.00
}
[elapsed 0s]

### server log
[srv 0.8s] request:
    GET / HTTP/1.1
    Host: 127.0.0.1:8081
    Accept: */*
    Accept-Encoding: gzip, deflate
    User-Agent: Mozilla/5.0 (unknown-aarch64-linux-gnu) Siege/4.0.7
    Connection: close
[srv 0.8s] request:
    GET / HTTP/1.1
    Host: 127.0.0.1:8081
    Accept: */*
    Accept-Encoding: gzip, deflate
    User-Agent: Mozilla/5.0 (unknown-aarch64-linux-gnu) Siege/4.0.7
    Connection: close
[srv 0.8s] request:
    GET / HTTP/1.1
    Host: 127.0.0.1:8081
    Accept: */*
    Accept-Encoding: gzip, deflate
    User-Agent: Mozilla/5.0 (unknown-aarch64-linux-gnu) Siege/4.0.7
    Connection: close

## 2. -d with and without -b (echo server)
$ siege -c1 -r3 -d10 http://127.0.0.1:8081/
{	"transactions":			           3,
	"availability":			      100.00,
	"elapsed_time":			       17.25,
	"data_transferred":		        0.00,
	"response_time":		        0.00,
	"transaction_rate":		        0.17,
	"throughput":			        0.00,
	"concurrency":			        0.00,
	"successful_transactions":	           3,
	"failed_transactions":		           0,
	"longest_transaction":		        0.00,
	"shortest_transaction":		        0.00
}
[elapsed 17s]

$ siege -b -c1 -r3 -d10 http://127.0.0.1:8081/
{	"transactions":			           3,
	"availability":			      100.00,
	"elapsed_time":			        0.01,
	"data_transferred":		        0.00,
	"response_time":		        0.00,
	"transaction_rate":		      300.00,
	"throughput":			        0.00,
	"concurrency":			        1.00,
	"successful_transactions":	           3,
	"failed_transactions":		           0,
	"longest_transaction":		        0.01,
	"shortest_transaction":		        0.00
}
[elapsed 0s]

## 3. server that never answers
$ timeout 150 siege -c1 -r1 http://127.0.0.1:8082/
{	"transactions":			           0,
	"availability":			        0.00,
	"elapsed_time":			      150.11,
	"data_transferred":		        0.00,
	"response_time":		        0.00,
	"transaction_rate":		        0.00,
	"throughput":			        0.00,
	"concurrency":			        0.00,
	"successful_transactions":	           0,
	"failed_transactions":		           0,
	"longest_transaction":		        0.00,
	"shortest_transaction":		        0.00
}
[elapsed 151s]

$ timeout 150 siege -R /tmp/rc5 -c1 -r1 http://127.0.0.1:8082/
** SIEGE 4.0.7
Lifting the server siege...
Transactions:		           0 hits
Availability:		        0.00 %
Elapsed time:		      150.08 secs
Data transferred:	        0.00 MB
Response time:		        0.00 secs
Transaction rate:	        0.00 trans/sec
Throughput:		        0.00 MB/sec
Concurrency:		        0.00
Successful transactions:           0
Failed transactions:	           0
Longest transaction:	        0.00
Shortest transaction:	        0.00
 
[elapsed 150s]

### server log
[srv 1.1s] request:
    GET / HTTP/1.1
    Host: 127.0.0.1:8082
    Accept: */*
    Accept-Encoding: gzip, deflate
    User-Agent: Mozilla/5.0 (unknown-aarch64-linux-gnu) Siege/4.0.7
    Connection: close
[srv 151.4s] request:
    GET / HTTP/1.0
    Host: 127.0.0.1:8082
    Accept: */*
    Accept-Encoding: *
    User-Agent: Mozilla/5.0 (unknown-aarch64-linux-gnu) Siege/4.0.7
    Connection: close
```

## 출력: rc.sh

```
$ siege -R /tmp/rc5 -C
Edit the resource file to change the settings.
protocol:                       HTTP/1.0
connection:                     close
socket timeout:                 5
resource file:                  /tmp/rc5
```
