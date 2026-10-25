---
title: "레슨 12: 업로드와 삭제"
type: lesson
sources: [raw/rfc7578.txt, raw/rfc2046.txt, raw/rfc9110.txt, raw/fs-observed-remove-name-length.md, raw/subject.md, raw/posix-remove.md, raw/evaluation-sheet-en.md]
updated: 2026-10-25
---

# 레슨 12: 업로드와 삭제

이전: [[lessons/11-response]] · 다음: [[lessons/13-cgi]]

## 12.1 multipart/form-data

> [!example] 쉬운 예
> 칸막이가 있는 도시락통을 생각하자. 칸막이마다 같은 특별한 표시(**boundary**)가 붙어 있고, 칸마다 이름표("이름=hello.txt")와 내용물이 들어 있다. 마지막 칸막이에는 "끝"을 뜻하는 `--`가 더 붙는다.

```text
Content-Type: multipart/form-data; boundary=XyZ

--XyZ\r\n
Content-Disposition: form-data; name="file"; filename="a.txt"\r\n
Content-Type: text/plain\r\n
\r\n
hello\r\n              ← 내용은 "hello" (바로 뒤 \r\n은 구분자의 일부)
--XyZ--\r\n            ← 마지막 구분자
```

브라우저 폼 업로드 형식이 `multipart/form-data`다 (raw/rfc7578.txt:105-110). 서버가 이 형식만 직접 해석해 저장하고, 다른 형식은 415로 거부한다 ([[analysis/design-decisions]] 7). 자세한 규칙: [[concepts/file-upload]].

> [!warning] 틀리기 쉬운 곳
> 구분자 앞의 CRLF는 내용이 아니라 구분자에 붙은 것이다 (MUST, raw/rfc2046.txt:1073-1076). 이것을 내용에 넣으면 올린 파일 끝에 `\r\n`이 붙어 파일이 망가진다. 해석기는 구분자를 `"\r\n--" + boundary`로 찾는다 (`src/http/Multipart.cpp:200-201`).

## 12.2 저장 전에 모두 검사

`src/handler/UploadHandler.cpp:201-224` (흐름):

```text
Content-Type이 multipart/form-data 아님        → 415
boundary 없음·잘못됨, 본문 문법 오류          → 400
planFiles: 파일 part마다
   6번째 파일                                  → 413 (결정 18)
   이름: 마지막 "/" 나 "\" 뒤만, 비었거나 "."·"..", 255바이트 초과 → 400
   이미 있는 이름 / 한 요청에 같은 이름 두 번   → 409 (결정 17)
   파일 part가 하나도 없음                      → 400
writeFiles: 하나라도 쓰기 실패 → 이 요청이 만든 파일 지우고 500
성공 → 201 + Location + 저장한 파일 목록
```

> [!tip] 왜 이렇게?
> - **디렉토리 부분 버리기**: `filename="../../evil.txt"`로 저장 위치 밖에 쓰려는 공격을 막는다. RFC 7578은 파일 이름의 디렉토리 경로를 쓰지 말라고 한다 (raw/rfc7578.txt:215-220). `\`는 Windows 경로 구분자라 함께 본다.
> - **같은 이름은 409**: 받는 쪽 파일을 실수로 덮어쓰지 말라고 한다 (raw/rfc7578.txt:497-499). 409는 "현재 상태와 충돌, 고쳐서 다시 보낼 수 있음"의 코드다 (raw/rfc9110.txt:7652-7655). 덮어쓰거나 이름을 바꾸지 않는다 (사용자 결정).
> - **255바이트**: Ubuntu 22.04는 256바이트 이름을 거부했다 (raw/fs-observed-remove-name-length.md:73-75). 전에는 `open` 실패로 500이었는데, 클라이언트 잘못이니 400으로 바꿨다.
> - **파일 5개 상한**: 1MB 요청 하나가 파일 15,000개를 만들 수 있었고 그동안 루프가 멈췄다(실측 0.82초). 사용자가 5개로 정했고, 문법은 맞지만 처리량이 너무 큰 것이라 413을 골랐다 ([[analysis/design-decisions]] 18, 413 정의: raw/rfc9110.txt:7710-7712).
> - **모두 검사한 뒤 쓴다**: 하나라도 문제가 있으면 아무것도 저장하지 않는다. 쓰다 실패해도 이미 쓴 파일을 지워 "전부 아니면 전무"를 지킨다 (`UploadHandler.cpp:189-197`).

> [!example] 쉬운 예 — O_EXCL
> "빈 자리일 때만 앉을게요." 검사와 쓰기 사이에 누가 같은 이름 파일을 만들어도, `O_CREAT | O_EXCL`로 열면 이미 있을 때 실패하므로 덮어쓰지 않는다 (`src/fs/FileWriter.cpp:21`).

## 12.3 DELETE

- 일반 파일만 지우고 204를 보낸다. 없으면 404, 디렉토리나 지울 권한이 없는 곳(그 디렉토리에 쓰기·검색 권한 없음)은 403이다 (`src/route/Router.cpp:159-169`).
- 경로는 GET과 같은 정규화를 거치므로 root 밖은 지울 수 없다.
- 지우는 함수는 `std::remove`다 (`src/handler/DeleteHandler.cpp:15-19`).

> [!tip] 왜 std::remove?
> 허용 함수 목록에 `unlink`도 `remove`도 없다 (raw/subject.md:113). 그런데 subject는 C 함수를 써도 되고 가능하면 C++ 버전을 쓰라고 한다 (raw/subject.md:51). 그래서 C++98 `<cstdio>`의 `std::remove`를 쓴다 ([[analysis/design-decisions]] 15). POSIX에서 `remove`는 파일이면 `unlink`, 디렉토리면 `rmdir`과 같다 (raw/posix-remove.md:33-35).

> [!info] 평가 때
> "권한 없이 DELETE" (raw/evaluation-sheet-en.md:73): `curl -X DELETE http://127.0.0.1:8080/index.html` → 405 + `Allow: GET, HEAD`, 파일 그대로. "권한 있게 DELETE": 업로드한 파일을 `/upload/`에서 지우면 204, 다시 GET하면 404.
