# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. **40줄/6KB 이하, 한 줄 200자 이하**(게이트가 검사).

## Now - 2026-10-10
- **진행 중:** `CHANGELOG.md` 추가, 버전 major.minor.patch(0.1.1), 릴리스 절차(브랜치 `claude/changelog-release-flow`). 병합 뒤 Claude가 `v0.1.1` 태그 push. 사용자: 옛 `latest-apk` 릴리스 삭제.
- **직전 병합:** #70 APK 빌드는 `v*` 태그로만, #69 워크플로 권한, #68 `graft/` 추적 해제, #67 규칙/스킬을 저장소 안으로. 드랍표 1차 정리, 주류 - [game-rules](.memory/roadmap/game-rules.md). #66은 열림.
- **다음:** 좀비/네임드 3종 개인 드랍. 드랍표 안에 표 지원, 던전 공용 드랍 D01~D10(세트 D03~). 주류 얻을 곳 미정. [피드백](.memory/roadmap/play-feedback-2026-10-07.md).
- **다음(사용자 결정):** 속성강화 규칙, 몬스터 개인 드랍표 "미정", 임시 그림 교체. 레벨 12~20 미정: 13 스킬, 16 각성 특성, 17 스킬 개화 선택지, 18 각성 스킬.
- **2차수:** 웨스트코스트(T03, D10 보스 클리어로 개방) + 하늘성 D11~D16은 지도 틀만. 몬스터/인카운트/보스 전투몬스터 미정. 풀 시나리오 S7은 계획 상태.
- 풀 시나리오 S1~S6·S8 구현([계획](.memory/roadmap/scenario-tests.md) 전부 완료). 구조 점검 N0~N7 전부 완료: [architecture_review.md](docs/architecture_review.md) 10절, [refactor.md](.memory/roadmap/refactor.md).
- 리팩터링 보고서 후속(종족 속성, skill 6모듈, 팝업 도우미, 몬스터 기본값 표 등): [refactoring_report.md](docs/refactoring_report.md) 9절. combat 순환은 안 함 - 이유 거기.
- 테스트 689개(이 브랜치, 2026-10-10 이 세션에서 측정). 커버리지 94.44%는 옛 값 - 이 세션에서는 측정하지 못했다.
- CI `ui-smoke`는 PR을 막는다. 병합된 PR의 브랜치는 이름과 상관없이 자동 삭제(`delete-merged-branch.yml`). 기본 브랜치는 2026-10-07에 `main` -> `main-branch`.
- 옛 *Now*의 경위 문단 원문: [보관본](.memory/sessions/2026-10-10-memory-index-archive.md).

## 믿으면 안 되는 것 ([`known-bugs.md`](.memory/active-issues/known-bugs.md))
- **실기기 미확인(화면 기준 기기 = 사용자 폰 갤럭시 S24):** 세이브 유지(N1c, 사용자가 직접 확인), 세로 화면의 지도 칸 수/감옥 2x2 모양, [뒤로] 키 전달,
  한글 조합 입력 중 6자 자르기, 새 팝업들.
- **확인 대기:** 레벨 2 파티의 D04 밸런스(이슈 #41), 마법사 `빗자루` 착용 불가. 미구현: 버프포션(샤프아이) 사용, 자동전투 포션 사용.
- `buildozer.spec` 주석의 빌드 노트 절 번호는 옛 번호(대응표: 빌드 노트 4절). **화면(kivy)은 테스트 범위 밖**, APK 빌드는 CI에서만 확인된다.
- 점검 경위: [`2026-10-03-remaining-work-audit.md`](.memory/sessions/2026-10-03-remaining-work-audit.md).

## 어디에 무엇이 있나

| 읽을 것 | 언제 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md), [`.claude/rules/`](.claude/rules/), [`.claude/skills/`](.claude/skills/) | 규칙: 완료 기준·가드레일, 주제별 규칙, 절차 |
| [`.memory/README.md`](.memory/README.md) | 어느 기억 파일에 무엇을 쓰나 |
| [`.memory/active-issues/`](.memory/active-issues/) | 값/문서/동작을 믿기 전에 |
| [`.memory/roadmap/`](.memory/roadmap/) | 다음에 할 일, 숫자가 있는 사실(`game-rules.md`) |
| [`.memory/sessions/`](.memory/sessions/) | 왜 그렇게 결정했나 (헛발질 포함) |
| [`README.md`](README.md), [`docs/`](docs/) | 실행/개발 입구, 빌드 노트, 구조 점검 보고서 |

## 규칙
- *Now*는 세션마다 갱신한다. 숫자가 있는 사실은 roadmap, 경위는 sessions, 아직 확인 안 된 것/알려진 버그는 active-issues로.
