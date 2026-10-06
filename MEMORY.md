# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. **40줄/6KB 이하**(게이트가 검사).

## Now - 2026-10-06 (`main`에 #39 레벨 12 스킬강화 + 레벨 16~20 테이블, #35~#38 풀 시나리오 규칙·P0·S1·S2 병합. 원격 브랜치는 `main`만. **미정(사용자가 정할 것)**: 16 각성 특성, 17 스킬 개화 선택지(조건부 추가효과), 18 각성 스킬, 13 스킬)
**작업 흐름**(CLAUDE.md "Git"): 기능마다 `main`에서 브랜치 -> 게이트 통과 -> PR -> CI 초록이면 병합(병합은 사용자 확인). PR 전에 fetch로 main 최신 확인. 큰 기능은 풀 시나리오(`docs/scenarios.md`) - 풀 시나리오 S1~S6 구현(계획 [`scenario-tests.md`](.memory/roadmap/scenario-tests.md) 전부 완료). 확인 대기(known-bugs): 레벨 2 파티의 D04 밸런스(이슈 #41), 마법사 `빗자루` 착용 불가.
graft(코드 그래프 CLI) 설치: 클라우드 세션 시작 훅(`.claude/hooks/session-start.sh`)이 `npm install -g @nanonets/graft` + `graft init --yes --no-global --no-agents --no-statusline`(연결 파일 재작성 + 그래프 빌드)을 돌린다(`graft/`는 로컬 캐시라 git 무시, 텔레메트리 끔). init이 `.claude/`를 안 바꾼다는 건 이 컨테이너에서만 확인 - **새 세션에서 `git status`가 깨끗한지 사용자가 확인 예정**. MCP `graft`는 훅이 설치하기 전에 떠서 첫 세션엔 연결 실패(CLI는 정상).
push는 검증된 작업만, 자동 push 훅 없음. 줄끝은 pre-commit 훅. `main`(1cbeb02) 기준 테스트 493개 · 커버리지 94.10%. **다음 로드맵 = 구조 점검 N0~N7**(세이브 손상 시 메인 메뉴 예외가 1순위): [`refactor.md`](.memory/roadmap/refactor.md), 근거 [`docs/architecture_review.md`](docs/architecture_review.md). 이 점검은 코드를 안 바꿨다.

**실기기 미확인** - [뒤로] 키 전달, 한글 조합 입력 중 6자 자르기, 새 팝업들.

**다음(사용자 결정):** 속성강화 규칙, 몬스터 24종 개인 드랍표 "미정", 던전 D03~D10 공용 드랍 없음, 임시 그림 교체.
미구현: 버프포션(샤프아이) 사용, 자동전투 포션 사용. 점검 경위: [`.memory/sessions/2026-10-03-remaining-work-audit.md`](.memory/sessions/2026-10-03-remaining-work-audit.md).
원격 브랜치는 `main`뿐 - `backup`은 #7 병합 무렵 누군가 지웠다(이 세션이 아님, 커밋은 main 이력에 있음).

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
