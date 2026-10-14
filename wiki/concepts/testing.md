---
title: 테스트 도구와 평가 시연
type: concept
sources: [raw/subject.md, raw/evaluation-sheet-en.md]
updated: 2026-10-15
---

# 테스트 도구와 평가 시연

## 제공·사용되는 도구

| 도구 | 용도 | 근거 |
|---|---|---|
| `tester` | 일반 테스터 (사용 의무 없음) | raw/evaluation-sheet-en.md:30, raw/subject.md:188 |
| `cgi_tester` | CGI 테스터 | raw/evaluation-sheet-en.md:31 |
| `siege` | 스트레스 테스트. 평가표는 apt 설치 기준 (`sudo apt-get install siege`). 빈 페이지 GET에 `siege -b`로 availability 99.5% 초과 | raw/evaluation-sheet-en.md:48, raw/evaluation-sheet-en.md:113-114 |
| `telnet`, `curl` | 기본 요청 시연 | raw/evaluation-sheet-en.md:77, raw/subject.md:123 |
| 브라우저 네트워크 탭 | 헤더 확인 | raw/evaluation-sheet-en.md:97-98 |
| NGINX | 동작·헤더 비교 기준 | raw/subject.md:141, raw/subject.md:186 |
| `leaks`, `valgrind`, `e_fence` | 누수 검사 | raw/evaluation-sheet-en.md:25 |

## 평가표에 나온 명령

```bash
# body 크기 제한 (raw/evaluation-sheet-en.md:70) — 원문에도 대상 URL이 없다. 평가자가 붙여서 쓴다
curl -X POST -H "Content-Type: plain/text" \
     --data "BODY IS HERE write something shorter or longer than body limit"
```

> [!note] 구버전 정리본과 차이
> 구버전 정리본에 있던 `ubuntu_tester`, `ubuntu_cgi_tester`(raw/evaluation-sheet.md:32-33)와 `curl --resolve` 호스트네임 테스트(raw/evaluation-sheet.md:67)는 영어 원문에 없다 (raw/evaluation-sheet-en.md:29-31, raw/evaluation-sheet-en.md:63-73).

## siege 부하 조건

- OS에 따라 결과가 다르므로 `-c`(클라이언트 수), `-d`(재접속 전 최대 대기), `-r`(반복 횟수)로 초당 연결 수를 제한한다 (raw/evaluation-sheet-en.md:118).
- 파라미터는 평가자가 정하되, 평가받는 사람과 **합의**해야 한다 (raw/evaluation-sheet-en.md:118). 미리 자기 환경에서 통과하는 값을 측정해 두면 협상 근거가 된다.
- 옵션의 정확한 의미는 siege 매뉴얼로 확인한다 (**미확인**, [[source-wishlist]] P2).

## 권장 사항

- 한 프로그램으로만 테스트하지 말고 Python/Go 등으로 테스트를 작성 (raw/subject.md:190).
- 평가자는 설정 파일 외 파일을 수정할 수 없으므로 (raw/evaluation-sheet-en.md:24), 시연용 설정·파일·CGI 스크립트(정상/에러/무한 루프)를 미리 준비한다 (raw/subject.md:184, raw/evaluation-sheet-en.md:91).

## 관련

- [[concepts/resilience]], [[concepts/cgi]], [[concepts/configuration-file]]
