# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. **40줄/6KB 이하, 한 줄 200자 이하**(게이트가 검사).

## Now - 2026-10-13
- **진행 중:** 품질 백로그 P1~P10, P1(#106)·P2(#107)·P3(#108)·P4(#110)·P5 끝남 - [quality-plan](.memory/roadmap/quality-plan.md)(새 모듈 3개·게이트 상향 승인됨). 근거: [보고서](docs/code_quality_review.md), #94.
- **릴리스는 사용자가 APK를 요청할 때만**(10-13 지시) - 병합 뒤에 릴리스를 묻지 않는다.
- **직전 병합:** #79 속성강화/내성 합연산·무속성 제외(S10), #78 버프포션 사용·새 3종·고블린 더스트(S9), #77 아이템 구분 주석, #76 개인 드랍 "미정" 정리 - [game-rules](.memory/roadmap/game-rules.md).
- 직전: 레벨 1 공중에뜸 스킬 5종·단죄의 십자가 2회(game-rules, 옛 세이브는 불러올 때 채움, S5 6->2번째 승리), 직업별 특징 주석(10-13). **공격 연출**(10-12): 대상 위 종류 그림 0.5초 - game-rules "공격 연출". 그림 7장 체크무늬 흔적, 실기기 미확인.
- 그림(10-13): 고블린 12종·케라하·비노슈 원본 교체, 카겔/봄 카겔 그림 추가, 벙커워커 삭제. 보라 등짐 그림은 프라그 다른 색이라 안 씀. 배치 규칙은 game-rules "화면 배치".
- 10-13: 키놀·프라그·펜릴 패턴, 루가루 할퀴기 -1. **수치 시뮬레이션은 `scenario.측정_파티_준비/측정_실전`**(조건: game-rules "밸런스 측정 조건"). D06 밸런스 조정 대기.
- **다음:** 정할 것. 주류 얻을 곳 미정. [피드백](.memory/roadmap/play-feedback-2026-10-07.md).
- **다음(사용자 결정):** 업적 보상 확정(항아리?), 창고, 임시 그림 교체. 레벨 12~20 미정: 13 스킬, 16 각성 특성, 17 스킬 개화 선택지, 18 각성 스킬.
- **2차수:** 웨스트코스트(T03, D10 보스 클리어로 개방) + 하늘성 D11~D16은 지도 틀만. 용족 4종(`monster_race_dragon.py`, 10-13)은 데이터만 있고 인카운트/보스 미정. 풀 시나리오 S7은 계획 상태.
- 풀 시나리오 S1~S6·S8~S12 구현([계획](.memory/roadmap/scenario-tests.md) 전부 완료). 구조 점검 N0~N7 전부 완료: [architecture_review.md](docs/architecture_review.md) 10절, [refactor.md](.memory/roadmap/refactor.md).
- 리팩터링 보고서 후속(종족 속성, skill 6모듈, 팝업 도우미, 몬스터 기본값 표 등): [refactoring_report.md](docs/refactoring_report.md) 9절. combat 순환은 안 함 - 이유 거기.
- 테스트 837개, 커버리지 94.57%(게이트 범위)(2026-10-14 측정). 시나리오 공백(숙소·해체·레벨 11~20 등): [이슈 #74](https://github.com/kirnata77/asdf/issues/74) - 제안 S9의 포션은 지금 S9가 다룸, 제안 S10(숙소)은 미착수(새 번호 필요).
- CI `ui-smoke`는 PR을 막는다. 병합된 PR의 브랜치는 이름과 상관없이 자동 삭제(`delete-merged-branch.yml`). 기본 브랜치는 2026-10-07에 `main` -> `main-branch`.
- 옛 *Now*의 경위 문단 원문: [보관본](.memory/sessions/2026-10-10-memory-index-archive.md).

## 믿으면 안 되는 것 ([`known-bugs.md`](.memory/active-issues/known-bugs.md))
- **실기기 미확인(화면 기준 기기 = 사용자 폰 갤럭시 S24):** 세이브 유지(N1c, 사용자가 직접 확인), 세로 화면의 지도 칸 수/감옥 2x2 모양, [뒤로] 키 전달,
  한글 조합 입력 중 6자 자르기, 새 팝업들, 도감·업적 화면(업적 줄 글 크기).
- **확인 대기:** 레벨 2 파티의 D04 밸런스(이슈 #41), 마법사 `빗자루` 착용 불가. 미구현: 자동전투 포션 사용. 버프포션/고블린 더스트는 얻을 곳 미정(판매목록/드랍표에 없음).
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
