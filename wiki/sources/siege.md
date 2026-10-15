---
title: siege 매뉴얼 (siege.pod)
type: source
sources: [raw/siege.pod, raw/evaluation-sheet-en.md, raw/siegerc.in]
updated: 2026-10-15
---

# siege 매뉴얼 (siege.pod)

원본: `raw/siege.pod`. <https://raw.githubusercontent.com/JoeDog/siege/master/doc/siege.pod>을 2026-10-15에 받아 그대로 저장했다. POD(Perl 문서) 일반 텍스트라 변환하지 않았다.

- 이 파일을 마지막으로 바꾼 커밋: `9c240ec5a16afc811049986e68777417a50da083` (2022-04-17). 받은 날 저장소의 최신 태그는 `v4.2.0`. (둘 다 받을 때 GitHub에서 본 값이고 raw 파일에는 없다.)
- `master` 브랜치 파일이라 이후 바뀔 수 있다. Ubuntu 22.04 apt 패키지는 siege 4.0.7이고, 그 태그의 이 파일과는 urls.txt 변수 설명·오타·예시 수치만 다르다 → [[sources/ubuntu2204-observed-tools]]. 평가 PC에 설치된 버전은 **미확인**이다 (평가 때 `siege -V`로 확인).
- 평가표는 이 도구로 스트레스 테스트를 한다 (raw/evaluation-sheet-en.md:113-118).

## 과제와 관련된 부분

| 부분 (줄) | 내용 | 위키 페이지 |
|---|---|---|
| DESCRIPTION (14-25) | 명령줄이 설정 파일보다 우선, 기본 설정 파일 위치 | [[concepts/testing]] |
| `-c` (143-155) | 동시 사용자 수, 기본 상한 255 | [[concepts/testing]] |
| `-r` (157-168) | 사용자별 반복 횟수 | [[concepts/testing]] |
| `-t` (170-180) | 실행 시간 | [[concepts/testing]] |
| `-d` (182-197) | 요청 사이 지연, 기본 0.5초 | [[concepts/testing]] |
| `-b` (199-202) | 벤치마크 모드, 지연 없음 | [[concepts/testing]] |
| PERFORMANCE STATISTICS (345-424) | Availability 등 통계 항목의 의미 | [[concepts/testing]], [[concepts/resilience]] |

다루지 않는 부분: `-g`·`-p` 디버그 출력, `-f` URL 파일, 로그, `-H`·`-A` 헤더 옵션, FTP.

## 이 문서로 확인하지 못한 것

- keep-alive 여부. 매뉴얼은 설정 파일로도 속성을 정한다고만 한다 (raw/siege.pod:18-20). 기본 설정 템플릿에서 `connection = close`로 확인했다 (raw/siegerc.in:268) → [[sources/siegerc]].
