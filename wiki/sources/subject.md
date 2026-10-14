---
title: webserv subject (v24.0)
type: source
sources: [raw/subject.md]
updated: 2026-10-15
---

# webserv subject (v24.0)

원본: `raw/subject.md` — `webserv.pdf` version 24.0을 markdown으로 변환한 것 (raw/subject.md:3).

## 한 줄 요약

C++98로 브라우저에서 실제로 쓸 수 있는 HTTP 서버를 만드는 과제 (raw/subject.md:9, raw/subject.md:109).

## 장별 요약

| 장 | 핵심 | 위키 페이지 |
|---|---|---|
| I. Introduction | HTTP와 웹 서버의 역할 설명. 요구사항 없음 (raw/subject.md:26) | — |
| II. General rules | 어떤 경우에도 크래시 금지, Makefile, `c++ -Wall -Wextra -Werror`, C++98, 외부 라이브러리 금지 (raw/subject.md:46-52) | [[concepts/build-and-submission]], [[concepts/resilience]] |
| III. AI Instructions | 이해하고 책임질 수 있는 AI 산출물만 사용 (raw/subject.md:68) | [[concepts/build-and-submission]] |
| IV. Mandatory | 허용 함수 목록, non-blocking + 단일 `poll()` 규칙, 기능 요구사항 (raw/subject.md:100-151) | [[concepts/io-multiplexing]], [[concepts/http-features]] |
| IV.2 macOS | `fcntl()`은 `F_SETFL`, `O_NONBLOCK`, `FD_CLOEXEC`만 허용 (raw/subject.md:155-157) | [[concepts/io-multiplexing]] |
| IV.3 Configuration | NGINX `server` 블록 참고, listen/에러 페이지/body 제한/라우트 규칙, CGI 노트 (raw/subject.md:159-190) | [[concepts/configuration-file]], [[concepts/cgi]] |
| V. README | 첫 줄 이탤릭 문구, Description/Instructions/Resources, 영어 (raw/subject.md:194-207) | [[concepts/build-and-submission]] |
| VI. Bonus | 쿠키·세션, 복수 CGI. 필수 완벽 통과 시에만 평가 (raw/subject.md:211-218) | [[concepts/bonus]] |
| VII. Submission | Git 저장소 내용만 평가, 디펜스 중 소규모 코드 수정 요청 가능 (raw/subject.md:222-230) | [[concepts/build-and-submission]] |

## 0점 조건 (subject 기준)

- 크래시 또는 예기치 않은 종료 → 0점 (raw/subject.md:46)
- socket/pipe 등을 readiness 확인 없이 `read`/`recv`/`write`/`send` → 0점 (raw/subject.md:136)

## 눈여겨볼 점

- HTTP/1.0을 기준점으로 제안하지만 강제하지 않음 (raw/subject.md:123).
- virtual host는 범위 밖이지만 구현해도 됨 (raw/subject.md:151) — 평가표와 충돌, [[analysis/subject-vs-evaluation]] 참고.
- 일반 디스크 파일은 `poll()`을 거치지 않아도 됨 (raw/subject.md:134).
- 테스트는 한 프로그램만으로 하지 말고 Python/Go 등으로 작성 권장 (raw/subject.md:190).
