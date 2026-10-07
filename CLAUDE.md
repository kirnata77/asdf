# 던전앤파이터 모바일 프로토타입

Kivy로 만든 턴제 RPG 프로토타입이다. buildozer로 안드로이드 APK를 빌드한다.
원격 저장소: https://github.com/kirnata77/asdf (기본 브랜치 `main-branch`)

**세션을 시작하면 [`MEMORY.md`](MEMORY.md)부터 읽는다** - 지금 진행 중인 일과 아직
믿으면 안 되는 것이 거기 있다.

## 구조와 계층 규칙

```
main.py            Kivy 앱 진입점, 화면 등록, 크래시 로그 훅
gameflow.py        화면 <-> 로직/데이터 컨트롤러의 창구(재수출만). 화면은 이 파일의 함수만 부른다
game/controller/   컨트롤러 구현 - 주제별 ctl_*.py 15개(battle/shop/party/levelup ...), gameflow.py가 다시 내보낸다
game/screens/      Kivy 화면 (kivy 의존은 여기와 main.py에만)
game/system/       전투, 스킬, 장비, 세이브 등 게임 로직
  combat/            전투 패키지(모듈 목록은 combat/__init__.py). 쓰는 쪽은
                     `from game.system.combat import flow, stats` 처럼 모듈을 직접 불러 쓴다
  skill/             스킬 실행 엔진 모듈 6개(skill_grant -> usage/target -> apply -> attack -> run, 아래로만).
                     쓰는 쪽은 `game.system.skill_system`(재수출 창구)을 부른다
game/data/         직업, 몬스터, 맵, 아이템 데이터(파이썬 딕셔너리)
                     file_path.py = 모든 모듈의 import 경로표 (테스트가 실제 파일과 대조)
game/assets/       폰트, 이미지
tests/             헤드리스 테스트 + golden/*.json (kivy 없이 돈다, 아래 "테스트 지도")
tools/check.py     완료 기준 게이트 (아래)
tools/ui_smoke.py  화면 스모크(kivy + Xvfb, 스크린샷) - CI 밖, 화면 바꿀 때 직접
tools/fix_eol.py   줄끝을 LF로 통일 (pre-commit 훅이 부른다)
.githooks/         pre-commit (줄끝 통일)
docs/              빌드 노트, 구조 점검 보고서, 리뷰 보고서, 시나리오 장부
README.md          입구(실행/개발/구조/빌드 요약)
.memory/           작업 기억 (MEMORY.md가 색인)
```

**계층은 한 방향이다: `screens` -> `gameflow`(창구) -> `controller` -> `system` -> `data`.**
- `game/system/`, `game/data/`, `game/controller/`, `gameflow.py`는 **kivy를 import하지 않는다.** 그래서
  테스트가 화면 없이 돈다(`test_헤드리스_계층은_kivy에_의존하지_않는다`가 지킨다).
- 화면은 `game.system`/`game.controller`를 직접 부르지 않고 `gameflow`를 거친다(`gameflow.xxx_system.`
  으로 우회하는 것도 금지). 화면에 필요한 조회/동작은 주제에 맞는 `game/controller/ctl_*.py`에 함수로
  추가하고 그 모듈의 `__all__`에 넣는다(gameflow.py는 건드리지 않는다 - 창구에는 구현을 두지 않는다).
  `test_화면은_game_system을_직접_쓰지_않는다`와 `test_controller_structure.py`가 지킨다.
- 컨트롤러 모듈은 위에서 아래로만 부른다(registry -> party -> 기능 모듈 -> dungeon/potion/rewards/charview/tavern).
  모듈끼리 순환하거나 다른 모듈의 밑줄 이름을 가져오면 테스트가 실패한다.
- 모듈을 추가/이동/이름변경하면 `game/data/file_path.py`도 같은 커밋에서 고친다.

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
   **로직을 추가/변경하면 테스트도 같이 추가한다** - 어디에 넣을지는 아래 "테스트 지도".
2. **골든 파일(`tests/golden/`)이 바뀌었다면 이유를 커밋에 적는다.** 리팩터링은
   동작을 바꾸지 않는 것이 정의이므로 골든이 바뀌면 안 된다. 동작을 일부러
   바꾼 경우만 `UPDATE_GOLDEN=1 python -m pytest`로 다시 쓰고 diff를 설명한다.
3. **화면(kivy) 변경은 tests/가 못 잡는다.** `python tools/ui_smoke.py`(리눅스는
   `xvfb-run -a -s "-screen 0 720x1280x24"`를 앞에)로 실제 화면을 돌려 확인하고,
   바꾼 동작이 스모크에 없으면 스모크에 단계를 추가한다(주제별 `_단계_*` 제너레이터에 넣는다).
   CI에도 같은 스모크를 도는 `ui-smoke` 잡이 있고, 실패하면 PR을 막는다.
4. **기억 갱신** - `MEMORY.md`의 *Now*와 `.memory/`를 코드와 같은 커밋에서 고친다(아래).
5. **큰 기능은 풀 시나리오로 검증한다** - 아래 "풀 시나리오 테스트".

**돌리지 못한 검증은 통과로 쓰지 않는다.** 커밋 본문에
`NOT VERIFIED: <무엇을> 실행해 보지 못함 - <이유>`로 남긴다. APK 빌드는 CI(`build-apk.yml`)에서만
되고, 화면은 헤드리스 테스트 범위 밖이다.

## 테스트 지도

| 파일 | 무엇을 | 방식 |
|---|---|---|
| `test_systems_basic.py` | 주사위, 효과, 파티, 소지품, 캐릭터 데이터, 마을, 지도, 몬스터AI | 정확한 값 |
| `test_systems_items.py` | 상점, 장비, 세이브, 레벨업 | 정확한 값 |
| `test_gameflow.py` | 새 게임 5직업, 세이브 왕복, 로리엔 보스전 | 골든 |
| `test_gameflow_scenarios.py` | 캠페인(던전 10개/숏컷/마을 개방), 패배/도망/휴식, 상점·장비, 성장 1->10(전직) | 골든 + 값 |
| `test_combat_rules.py` | 수식, 피해, 속성, 사용 가능 여부, 타겟, 효과 적용, 조건 | 정확한 값 |
| `test_combat_skills.py` | 스킬 전수(기본/준비됨) | 골든 |
| `test_combat_monsters.py` | 몬스터 고유 패턴 전수 + 보스 칭호 | 골든 |
| `test_combat_effects.py` | 상태이상/버프/디버프 전수, 반응특성 전투 | 골든 |
| `test_screen_api.py` | 화면용 gameflow 창구, 화면 -> system/controller 직접 호출 금지 | 값 + 규칙 |
| `test_controller_structure.py` | 창구에 구현 금지, 컨트롤러 `__all__` 완전성/이름 겹침/순환 금지, 창구가 쓰이는 이름을 다 내보냄 | 규칙 |
| `test_formula_parity.py` | 수식 평가기가 옛 eval 구현과 같은 값을 내는지(데이터 수식 전부 + 무작위 식), 안전 평가기의 거부 규칙 | 기준 구현과 비교 |
| `test_architecture.py` | combat 모듈 순환은 허용 묶음뿐, combat은 skill_system/skill을 안 부름, skill 패키지는 아래로만, 다른 모듈의 밑줄 이름 금지, 게임 코드에 eval/exec 금지 | 규칙 |
| `test_state_schema.py` | 캐릭터/전투 참가자/게임상태가 `state_schema.py` 표대로인지(칸이 빠지거나 이름이 바뀌면 실패), 불러올 때 핵심 칸 검사 | 규칙 |
| `test_data_integrity.py` | 데이터의 수식이 엄격하게 평가되는지, 몬스터/스킬/버프/던전/마을/상점의 키·이름 참조 | 규칙(허용 목록은 이유와 함께) |
| `test_scenario_*.py` | 풀 시나리오(실제 전투로 처음부터 끝까지, 아래) | 요약 골든 + 값 |
| `test_imports.py`, `test_repo_hygiene.py` | 모듈 import, file_path.py, LF 줄끝, 시나리오 장부 대조 | 규칙 |

- 공용 도우미는 `tests/support.py`(자동 전투, 강제 승리/패배, 경로 걷기, 결정적 성장).
- 무작위는 전부 전역 `random`이라 `random.seed()`로 재현된다. 골든은 시드를 고정해 만든다.
- **데이터를 추가/수정하면** `test_data_integrity.py`가 오타(수식 변수, 특성/버프 이름, 그림 파일, 던전 연결)를 잡는다. 런타임은 평가할 수 없는
  수식을 0으로, 정의 없는 특성을 건너뛰어 조용히 넘어가므로 이 테스트가 유일한 안전망이다. 새 변수/예외는 허용 목록에 이유와 함께 더한다.
- **새 스킬/몬스터/버프/상태이상 데이터를 추가하면** 전수 스윕이 자동으로 포함해 골든이
  바뀐다 - `UPDATE_GOLDEN=1`로 다시 쓰고 새 항목이 맞는지 diff를 읽는다.

## 풀 시나리오 테스트

단위 테스트와 골든 스윕은 기능을 하나씩 검사한다. 기능들이 **이어져 돌아가는지**는 풀 시나리오가
검사한다 - 새 게임 -> 이동/인카운트 -> **실제로 굴리는 전투**(`강제_승리` 금지) -> 보상/성장/장비 -> 다음 전투.
전부 `gameflow` 창구로 진행한다(화면 없이 헤드리스).

- **큰 기능은 풀 시나리오를 추가하거나 갱신해야 끝난 것이다.** 큰 기능 = 게임 진행에 영향을 주는 변경:
  전투 판정/행동 규칙, 직업/스킬/특성/레벨업/전직, 장비/무기/아이템/드랍/보상, 몬스터 패턴/종족,
  던전/마을 진행, 세이브 형식. 작은 수치 조정과 문구/화면 배치는 단위 테스트로 충분하다.
- **시나리오는 `docs/scenarios.md`가 관리한다.** 시나리오마다 한 행: ID, 무엇을 검사하나(기능),
  어떤 방법으로(캐릭터/직업, 무기, 몬스터, 시드, 거치는 단계), 테스트 이름. 시나리오 테스트에는
  `@pytest.mark.scenario("S1")`처럼 ID를 달고, 문서의 ID와 테스트의 ID가 어긋나면 게이트가 실패한다
  (`test_repo_hygiene.py`, 대조 로직은 `tools/scenario_registry.py`). 표의 상태는 `계획`/`구현`.
- 큰 기능을 넣는 커밋/PR은 어느 시나리오가 그 기능을 지나가는지 적는다. 지나가는 시나리오가 없으면
  새로 만든다. 못 돌렸으면 `NOT VERIFIED`.
- 전투 결과 전체 로그를 골든으로 박지 않는다(작은 변경에도 깨진다). 요약(종료, 라운드 범위, 생존, 보상,
  진행도)을 골든/값으로 비교하고 규칙은 불변식으로 단언한다.

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
- **세이브 호환성.** `game/saves/*.json` 형식(세이브 키 이름 포함)을 바꾸면 `save_system.세이브_버전`을
  올리고 `_마이그레이션` 표에 (새 버전, 변환 함수)를 더한다(옛 세이브 테스트 포함). 불러올 때마다 규칙에 맞춰
  다시 계산하는 값(최대HP 등)은 형식이 아니라 규칙이라 `gameflow.게임_불러오기`가 한다.
- **`buildozer.spec`을 바꾸면** CI 캐시 키가 바뀌어 다음 APK 빌드가 SDK/NDK를 새로
  받는다(수십 분). 꼭 필요할 때만 바꾼다.
- **비밀값을 커밋하지 않는다** - 서명 키스토어, 토큰, 비밀번호. CI 비밀은 GitHub Secrets로.

## 줄끝 - 모든 텍스트 파일은 LF

- `.gitattributes`(`* text=auto eol=lf`)가 커밋 시 LF로 정규화하고, `.githooks/pre-commit`이
  `tools/fix_eol.py`로 작업 트리도 LF로 맞춘다. 게이트(`tests/test_repo_hygiene.py`)가 검사한다.
- **GitHub 웹 업로드는 둘 다 거치지 않는다** - CRLF가 그대로 들어가 게이트가 실패하면
  받아서 `python tools/fix_eol.py`로 고친다. 웹에서 훅을 다시 올리면 실행 권한도 사라진다
  (`chmod +x .githooks/pre-commit`).
- 파이썬으로 파일을 쓸 때는 `open(..., "w", newline="\n")`(tests/conftest.py의 골든 쓰기 참고).
- 서식/줄끝 일괄 변경 커밋은 `.git-blame-ignore-revs`에 등록한다
  (`git config blame.ignoreRevsFile .git-blame-ignore-revs`).

## 기억 파일 (MEMORY.md / .memory/)

- `MEMORY.md`는 **색인이다. 40줄 이하, 6KB(6,144바이트) 이하.** 한글은 글자당 3바이트라
  줄 수만 지켜서는 크기가 넘는다 - 둘 다 지킨다. 게이트(`tests/test_repo_hygiene.py`)가 검사하고,
  넘으면 실패한다. 넘칠 때는 규칙/수치 설명을 `.memory/roadmap/game-rules.md`로, 경위는 `sessions/`로
  옮기고 MEMORY.md에는 한 줄 링크만 남긴다. *Now* 절에는 다음에 할 일과 "써 놓았지만
  아직 확인 안 된 것"만 둔다. 세션마다 *Now*를 갱신한다(변화 없음이라도).
- 자세한 내용은 `.memory/` 아래 - 숫자가 있는 사실은 `roadmap/`, 믿으면 안 되는 것은
  `active-issues/`, 헛발질을 포함한 경위는 `sessions/`(자세히는 `.memory/README.md`).
- 기억 파일 수정은 그 내용과 관련된 코드와 **같은 커밋**에 넣는다. 따로 커밋하면
  커밋하는 순간 낡는다.

## Git

### 흐름 - 기능 하나 = 브랜치 하나 = PR 하나 -> `main-branch`

- **`main-branch`에 직접 push하지 않는다.** 기능(버그 수정, 리팩터링 한 단계 포함)마다 `main-branch`에서
  브랜치를 따서 작업한다.
- **PR을 만들기 전에 `git fetch origin main-branch`로 `main-branch`가 최신인지 확인한다.** `main-branch`가 앞서 있으면
  먼저 합쳐서(merge) 충돌을 풀고 게이트를 다시 돌린다. 브랜치도 최신 `main-branch`에서 딴다.
  PR을 열 때 기준 커밋(`origin/main-branch` 해시)을 본문에 적는다.
- **기능이 끝나고 게이트가 통과하면 `main-branch`로 PR을 연다.** 다른 개발자가 `main-branch`의 PR
  목록만 보고 무엇이 왜 들어왔는지 알 수 있어야 한다 - PR 본문에 요점, 이유, 검증한 것,
  남은 것(`NOT VERIFIED` 포함)을 쓴다.
- **CI가 초록이 되면 병합한다.** 병합 실행은 위 가드레일대로 그 순간 사용자 확인을 받는다.
- **병합된 브랜치는 끝난 것이다.** 후속 작업은 최신 `main-branch`에서 새로 시작한다(병합된 브랜치에
  커밋을 더 쌓지 않는다).
- **`main-branch`로 병합된 PR의 브랜치는 이름과 상관없이 자동으로 지워진다**(`.github/workflows/delete-merged-branch.yml`).
  병합 없이 닫힌 PR의 브랜치는 그대로 둔다 - 지우려면 가드레일대로 그 순간 확인을 받는다.

### 커밋 - 한 작업 = 한 커밋, 게이트 통과 후

- **한 문장으로 설명할 수 있는 단위**(계획 한 단계, 버그 하나 수정, 리팩터링 한 걸음)마다
  커밋한다. 파일 하나 고칠 때마다가 아니고, 무관한 작업을 묶지도 않는다.
- **게이트 먼저, 커밋은 그다음.** 검증하지 않은 상태는 커밋하지 않는다. 반쯤 된 작업은
  브랜치에 둔다.
- `git status`를 **`git add -A` 전에** 본다. 내가 하지 않은 기존 변경은 작업과 관련이
  없으면 건드리지 않는다.
- **위험한 단계 전에도 커밋한다**(대량 이동, 골든 재작성 등) - 되돌릴 지점을 남긴다.
- 커밋하지 않는 것: `game/saves/`, `.buildozer/`, `bin/`, zip 파일, 비밀값.

### push - 끝까지 검증된 작업만

- **로컬 커밋은 작업 중에 고쳐도 된다**(`--amend`, `rebase`로 합치기/나누기).
- **작업이 끝나고 게이트가 통과하면 push한다**(`git push -u origin <브랜치>`).
- **원격에 올라간 커밋은 고치지 않는다** - 새 커밋으로 수정한다(강제 push 금지).

### 메시지

- **제목은 바꾼 파일이 아니라 변경의 요점**을 쓴다.
  좋음: `전투 판정 함수를 combat_system에서 분리 -- 동작 불변, 골든 그대로`
  나쁨: `Update combat_system.py`
- **본문에는** 6개월 뒤 독자가 복원할 수 없는 것을 쓴다: 무엇을 왜 바꿨는지(이전 믿음을
  고치는 경우 그 믿음이 무엇이었고 무엇을 치렀는지), 무엇을 검증했고 무엇이 아직 열려 있는지.
