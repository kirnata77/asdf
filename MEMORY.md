# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. **40줄/6KB 이하**(게이트가 검사).

## Now - 2026-10-07 (**2차수 시작(#51 병합)**: 마을 웨스트코스트(T03, D10 보스 클리어로 개방) + 하늘성 던전 D11~D16 지도 틀만 - 아몬/세피로타(D11~D14)는 둥근 탑을 반시계로 도는 27x10(출입구는 전부 위아래 첫 줄, 하층 천장 포탈 앞/상층 마을 포탈 앞에 보스, 새 지도 기호 `Y`=하늘(이동불가) - 맵정보 `"타일"`(기호별 한 칸 그림, 맵마다 다르게) 추가 - 탑 4곳은 발판 emerald/벽 skycastlewall/하늘 skyyellow, 푸른 `asset_tile_sky.webp`는 아직 미사용), 미들오션(D15/D16)은 17x7에 포탈 자체가 보스(옛 방식 - 바꿀지 미정). 몬스터/인카운트/보스 전투몬스터 미정, 배경 그림은 헨돈마이어 복사본, 상점은 헨돈마이어와 같음. 보스는 `통행가능화`라 재입장하면 다시 막힌다. 풀 시나리오 S7은 계획 상태. `main`에 #39 레벨 12 스킬강화 + 레벨 16~20 테이블, #35~#38 풀 시나리오 규칙·P0·S1·S2 병합. **미정(사용자가 정할 것)**: 16 각성 특성, 17 스킬 개화 선택지(조건부 추가효과), 18 각성 스킬, 13 스킬)
**작업 흐름**(CLAUDE.md "Git"): 기능마다 `main`에서 브랜치 -> 게이트 통과 -> PR -> CI 초록이면 병합(병합은 사용자 확인). PR 전에 fetch로 main 최신 확인. 큰 기능은 풀 시나리오(`docs/scenarios.md`) - 풀 시나리오 S1~S6 구현(계획 [`scenario-tests.md`](.memory/roadmap/scenario-tests.md) 전부 완료). 확인 대기(known-bugs): 레벨 2 파티의 D04 밸런스(이슈 #41), 마법사 `빗자루` 착용 불가.
push는 검증된 작업만, 자동 push 훅 없음. 줄끝은 pre-commit 훅. `main` 기준 테스트 598개 · 커버리지 94.44%. **구조 점검 로드맵 N0~N7 전부 완료** - 결과는 [`docs/architecture_review.md`](docs/architecture_review.md) 10절, 계획/판단은 [`refactor.md`](.memory/roadmap/refactor.md). **리팩터링 보고서 후속(브랜치 `ccr-881b7ea2-9vlrfc`)**: 종족:루가루(속도+1)/인간(효과 없음) 정의함 - S6 시드 0->1,2. 테스트 전용 함수 6개 삭제. 설정 파일 except 좁힘(+스모크). 매개변수 9개 이상 함수 정리. 복잡도 상위 6개 분해. skill_system -> `game/system/skill/` 6모듈(창구 유지). 팝업 공통 도우미(스크롤_목록/닫기_버튼). 몬스터 기본값 표(`monster_defaults.py`). 결과는 [`refactoring_report.md`](docs/refactoring_report.md) 9절(combat 순환은 안 함 - 이유 거기). **미확인:** 실기기 세이브 유지(N1c, 사용자가 직접 확인) - known-bugs 상단. CI `ui-smoke`는 이제 PR을 막는다(연속 초록 4회 확인 뒤 continue-on-error 삭제).

**실기기 미확인** - [뒤로] 키 전달, 한글 조합 입력 중 6자 자르기, 새 팝업들.

**다음(사용자 결정):** 속성강화 규칙, 몬스터 24종 개인 드랍표 "미정", 던전 D03~D10 공용 드랍 없음, 임시 그림 교체.
미구현: 버프포션(샤프아이) 사용, 자동전투 포션 사용. 점검 경위: [`.memory/sessions/2026-10-03-remaining-work-audit.md`](.memory/sessions/2026-10-03-remaining-work-audit.md).
병합된 PR의 브랜치는 이름과 상관없이 자동 삭제(`delete-merged-branch.yml`, 이전엔 `claude/*`만). `backup`은 #7 병합 무렵 누군가 지웠다(이 세션이 아님, 커밋은 main 이력에 있음).

**믿으면 안 되는 것** ([`known-bugs.md`](.memory/active-issues/known-bugs.md)):
`buildozer.spec` 주석의 빌드 노트 절 번호는 옛 번호(대응표: 빌드 노트 4절).
**화면(kivy)은 테스트 범위 밖**, APK 빌드는 CI에서만 확인된다.

규칙·수치 사실(레벨/속성/HP·MP/포션/병합 이력): [`game-rules.md`](.memory/roadmap/game-rules.md).

## 어디에 무엇이 있나

| 읽을 것 | 언제 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | 규칙: 계층, DoD, 테스트 지도, 가드레일, 줄끝, git |
| [`.memory/README.md`](.memory/README.md) | 어느 기억 파일에 무엇을 쓰나 |
| [`.memory/active-issues/`](.memory/active-issues/) | 값/문서/동작을 믿기 전에 |
| [`.memory/roadmap/`](.memory/roadmap/) | 다음에 할 일, 숫자가 있는 사실 |
| [`.memory/sessions/`](.memory/sessions/) | 왜 그렇게 결정했나 (헛발질 포함) |
| [`README.md`](README.md), [`docs/`](docs/) | 실행/개발 입구, 빌드 노트, 구조 점검 보고서 |

## 규칙
- *Now*는 세션마다 갱신한다. 숫자가 있는 사실은 roadmap, 경위는 sessions,
  아직 확인 안 된 것/알려진 버그는 active-issues로.
