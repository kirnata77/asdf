# 던전앤파이터 모바일 프로토타입

Kivy로 만든 턴제 RPG 프로토타입이다. buildozer로 안드로이드 APK를 빌드한다.
원격 저장소: https://github.com/kirnata77/asdf (기본 브랜치 `main-branch`)

**세션을 시작하면 [`MEMORY.md`](MEMORY.md)부터 읽는다** - 지금 진행 중인 일과 아직
믿으면 안 되는 것이 거기 있다.

## 구조와 계층 규칙

**계층은 한 방향이다: `screens` -> `gameflow`(창구) -> `controller` -> `system` -> `data`.**
세부 구조와 모듈 배치는 `.claude/rules/layers.md` (`game/`, `gameflow.py`를 건드릴 때 읽힌다).

## 처음 한 번 (저장소마다)

```
pip install pytest pytest-cov ruff==0.16.9   # CI와 같은 버전 - ruff는 버전마다 서식이 다르다
git config core.hooksPath .githooks          # pre-commit 훅 켜기
```

## 완료 기준 (Definition of Done)

한 작업을 끝냈다고 하려면 다음을 모두 만족해야 한다:

1. **`python tools/check.py` 통과** - compileall + `ruff check` + `ruff format --check` + `pytest` +
   커버리지 하한(game/system + game/controller + gameflow.py, `COVERAGE_FLOOR`). CI(`.github/workflows/check.yml`)도
   모든 push/PR에서 같은 명령을 돌린다. 서식이 걸리면 `python -m ruff format .`.
   **로직을 추가/변경하면 테스트도 같이 추가한다** - 어디에 넣을지는 `.claude/rules/tests.md`의 "테스트 지도".
2. **골든 파일(`tests/golden/`)이 바뀌었다면 이유를 커밋에 적는다.** 리팩터링은
   동작을 바꾸지 않는 것이 정의이므로 골든이 바뀌면 안 된다. 동작을 일부러
   바꾼 경우만 `UPDATE_GOLDEN=1 python -m pytest`로 다시 쓰고 diff를 설명한다.
3. **화면(kivy) 변경은 tests/가 못 잡는다.** `python tools/ui_smoke.py`(리눅스는
   `xvfb-run -a -s "-screen 0 1080x2340x24"`를 앞에)로 실제 화면을 돌려 확인하고,
   바꾼 동작이 스모크에 없으면 스모크에 단계를 추가한다(주제별 `_단계_*` 제너레이터에 넣는다).
   CI에도 같은 스모크를 도는 `ui-smoke` 잡이 있고, 실패하면 PR을 막는다.
4. **기억 갱신** - `MEMORY.md`의 *Now*와 `.memory/`를 코드와 같은 커밋에서 고친다(`.claude/rules/memory.md`).
5. **큰 기능은 풀 시나리오로 검증한다** - `.claude/rules/scenarios.md`.

**돌리지 못한 검증은 통과로 쓰지 않는다.** 커밋 본문에
`NOT VERIFIED: <무엇을> 실행해 보지 못함 - <이유>`로 남긴다. APK 빌드는 CI(`build-apk.yml`)에서만
되고, 화면은 헤드리스 테스트 범위 밖이다.

## 작업 방식 (가드레일)

- **계획 먼저.** 여러 파일에 걸친 변경이나 구조 변경은 먼저 계획(영향 범위,
  단계, 검증 방법)을 보여주고 확인을 받은 뒤 진행한다.
- **리팩터링과 동작 변경을 한 커밋에 섞지 않는다.** 버그를 발견하면 기록
  (`.memory/active-issues/`)하고 따로 고친다.
- **자동 수정은 최대 2번.** 같은 문제로 두 번 고쳐도 게이트가 안 통과하면 멈추고
  상황을 보고한다.
- **값은 데이터 파일이 아니라 실행 결과로 확인한다.** 딕셔너리에 적힌 값이 실제 게임에
  쓰이는지는 별개다(예: "미정" HP가 1로 등장). 테스트나 스모크로 돌려 본 것만 사실로 쓴다.
- **테스트/스모크/플레이 확인에서 "치트" 아이템을 쓰지 않는다** - 레어도 "치트" 아이템(치트용 소검,
  치트용 마법석 등)은 사용자 전용이다. 장착/구매/사용 모두 금지. 예외는 그 치트 아이템 자체를 검사하는 테스트뿐이다.
- **되돌리기 어려운 명령은 실행하는 순간에 따로 허락을 받는다** - 원격 브랜치 강제 push,
  브랜치 삭제, PR 병합, `game/saves/` 삭제. 그 명령이 들어 있는 계획을 승인받은 것은
  실행 허락이 아니다.
- **비밀값을 커밋하지 않는다** - 서명 키스토어, 토큰, 비밀번호. CI 비밀은 GitHub Secrets로.

## 규칙 파일과 스킬

해당 파일을 건드릴 때 읽히는 규칙(`.claude/rules/`, 파일마다 80줄 이하 - 게이트가 검사한다): `layers.md`(구조·계층),
`tests.md`(테스트 지도), `scenarios.md`(풀 시나리오), `build-and-save.md`(세이브 호환성·buildozer), `eol.md`(줄끝),
`memory.md`(`MEMORY.md`/`.memory/`). 절차(브랜치·커밋·push·PR·메시지)는 `.claude/skills/repo-workflow/` 스킬.

## 줄끝 - 모든 텍스트 파일은 LF

- LF 규칙은 `.gitattributes`(`* text=auto eol=lf`)와 pre-commit 훅이 지키고 게이트가 검사한다. 세부는 `.claude/rules/eol.md`.

## 기억 파일 (MEMORY.md / .memory/)

- 세션마다 *Now*를 갱신한다. 기억 파일은 관련 코드와 **같은 커밋**에 넣는다. 세부는 `.claude/rules/memory.md`.

## Git

- **`main-branch`에 직접 push하지 않는다.** 기능마다 최신 `main-branch`에서 브랜치를 따서 게이트 통과 후 PR을 연다.
  PR 병합은 위 가드레일대로 그 순간 사용자 확인을 받는다. 병합된 브랜치는 끝난 것이다(후속 작업은 새로 딴다).
- **게이트 먼저, 커밋은 그다음.** 원격에 올라간 커밋은 고치지 않는다(강제 push 금지). 절차 전체는 `repo-workflow` 스킬.
