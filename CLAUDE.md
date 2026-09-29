# 던전앤파이터 모바일 프로토타입

Kivy로 만든 턴제 RPG 프로토타입이다. buildozer로 안드로이드 APK를 빌드한다.

**세션을 시작하면 [`MEMORY.md`](MEMORY.md)부터 읽는다** - 지금 진행 중인 일과 아직
믿으면 안 되는 것이 거기 있다.

## 구조와 계층 규칙

```
main.py            Kivy 앱 진입점, 화면 등록, 크래시 로그 훅
gameflow.py        화면 <-> 로직/데이터 컨트롤러. 화면은 이 파일의 함수만 부른다
game/screens/      Kivy 화면 (kivy 의존은 여기와 main.py에만)
game/system/       전투, 스킬, 장비, 세이브 등 게임 로직
  combat/            전투 시스템 패키지 12개 모듈(목록은 combat/__init__.py). 쓰는 쪽은
                     `from game.system.combat import flow, stats` 처럼 모듈을 직접 불러 쓴다
game/data/         직업, 몬스터, 맵, 아이템 데이터(파이썬 딕셔너리)
                     file_path.py = 모든 모듈의 import 경로표 (테스트가 실제 파일과 대조)
game/assets/       폰트, 이미지
tests/             헤드리스 테스트 + golden/*.json (kivy 없이 돈다, 아래 "테스트 지도")
tools/check.py     완료 기준 게이트 (아래)
tools/ui_smoke.py  화면 스모크(kivy + Xvfb, 스크린샷) - CI 밖, 화면 바꿀 때 직접
tools/fix_eol.py   줄끝을 LF로 통일 (아래 "줄끝")
docs/              빌드 노트 등 문서
.memory/           작업 기억 (MEMORY.md가 색인)
```

**계층은 한 방향이다: `screens` -> `gameflow` -> `system` -> `data`.**
- `game/system/`, `game/data/`, `gameflow.py`는 **kivy를 import하지 않는다.** 그래서
  테스트가 화면 없이 돈다(`test_헤드리스_계층은_kivy에_의존하지_않는다`가 지킨다).
- 화면은 `game.system`을 직접 부르지 않고 `gameflow`를 거친다(`gameflow.xxx_system.`
  으로 우회하는 것도 금지). 화면에 필요한 조회는 gameflow의 "화면용 조회" 절에 함수로
  추가한다. `test_화면은_game_system을_직접_쓰지_않는다`가 지킨다.
- 모듈을 추가/이동/이름변경하면 `game/data/file_path.py`도 같은 커밋에서 고친다.

원격 저장소: https://github.com/kirnata77/asdf (브랜치 `main`)

## 완료 기준 (Definition of Done)

한 작업을 끝냈다고 하려면 다음을 모두 만족해야 한다:

1. **`python tools/check.py` 통과** - compileall + `ruff check` + `ruff format --check` + `pytest` +
   **커버리지 하한**(game/system + gameflow.py, `COVERAGE_FLOOR` = 90%, 현재 94%).
   도구 설치: `pip install pytest pytest-cov ruff==0.16.9`(CI와 같은 버전). CI(`.github/workflows/check.yml`)도
   모든 push/PR에서 같은 명령을 돌린다.
   **로직을 추가/변경하면 테스트도 같이 추가한다** - 어디에 넣을지는 아래 "테스트 지도".
2. **골든 파일(`tests/golden/`)이 바뀌었다면 이유를 커밋에 적는다.** 리팩터링은
   동작을 바꾸지 않는 것이 정의이므로 골든이 바뀌면 안 된다. 동작을 일부러
   바꾼 경우만 `UPDATE_GOLDEN=1 python -m pytest`로 다시 쓰고 diff를 설명한다.
3. **화면(kivy) 변경은 tests/가 못 잡는다.** `python tools/ui_smoke.py`(리눅스는
   `xvfb-run -a -s "-screen 0 720x1280x24"`를 앞에)로 실제 화면을 돌려 확인하고,
   바꾼 동작이 스모크에 없으면 스모크에 단계를 추가한다. 못 돌렸으면 커밋 본문에
   `NOT VERIFIED: 화면 동작은 실행해 보지 못함`이라고 쓴다.
4. **기억 갱신** - `MEMORY.md`의 *Now*와 `.memory/`를 같은 커밋에서 고친다(아래).

## 테스트 지도

| 파일 | 무엇을 | 방식 |
|---|---|---|
| `test_systems_basic.py` | 주사위, 효과, 파티, 소지품, 캐릭터 데이터, 마을, 지도, 몬스터AI | 정확한 값 |
| `test_systems_items.py` | 상점, 장비, 세이브, 레벨업 | 정확한 값 |
| `test_gameflow.py` | 새 게임 5직업, 세이브 왕복, 로리엔 보스전 | 골든 |
| `test_gameflow_scenarios.py` | 캠페인(던전 10개/숏컷/마을 개방), 패배/도망/휴식, 상점·장비, 성장 1->10(전직) | 골든 + 값 |
| `test_combat_rules.py` | 수식, 피해, 속성, 사용 가능 여부, 타겟, 효과 적용, 조건 | 정확한 값 |
| `test_combat_skills.py` | 스킬 62개 전수(기본/준비됨) | 골든 |
| `test_combat_monsters.py` | 몬스터 29종의 고유 패턴 73개 + 보스 칭호 | 골든 |
| `test_combat_effects.py` | 상태이상 20 / 버프 21 / 디버프 20 전수, 반응특성 10종 전투 | 골든 |
| `test_screen_api.py` | 화면용 gameflow 창구, 화면 -> system 직접 호출 금지 | 값 + 규칙 |
| `test_imports.py`, `test_repo_hygiene.py` | 모듈 import, file_path.py, LF 줄끝 | 규칙 |

- 공용 도우미는 `tests/support.py`(자동 전투, 강제 승리/패배, 경로 걷기, 결정적 성장).
- 무작위는 전부 전역 `random`이라 `random.seed()`로 재현된다. 골든은 시드를 고정해 만든다.
- **새 스킬/몬스터/버프/상태이상 데이터를 추가하면** 전수 스윕이 자동으로 포함해 골든이
  바뀐다 - `UPDATE_GOLDEN=1`로 다시 쓰고 새 항목이 맞는지 diff를 읽는다.

## 작업 방식 (가드레일)

- **계획 먼저.** 여러 파일에 걸친 변경이나 구조 변경은 먼저 계획(영향 범위,
  단계, 검증 방법)을 보여주고 확인을 받은 뒤 진행한다.
- **리팩터링과 동작 변경을 한 커밋에 섞지 않는다.** 버그를 발견하면 기록
  (`.memory/active-issues/`)하고 따로 고친다.
- **자동 수정은 최대 2번.** 같은 문제로 두 번 고쳐도 게이트가 안 통과하면 멈추고
  상황을 보고한다.
- **검증 못 한 것을 검증했다고 쓰지 않는다.** APK 빌드는 CI(`build-apk.yml`)에서만
  되고, 화면은 헤드리스 테스트 범위 밖이다.
- **세이브 호환성.** `game/saves/*.json` 형식(세이브 키 이름 포함)을 바꾸면 이전
  세이브를 불러오는 호환 처리(`gameflow.게임_불러오기` 참고)를 함께 넣는다.
- **`buildozer.spec`을 바꾸면** CI 캐시 키가 바뀌어 다음 APK 빌드가 SDK/NDK를 새로
  받는다(수십 분). 꼭 필요할 때만 바꾼다.

## 줄끝 - 모든 텍스트 파일은 LF

- **저장소의 모든 텍스트 파일(.py, .md, .json, .yml, .toml, .spec, .gitignore, git 훅 등)은
  LF로 저장한다.** 새 파일도 마찬가지다. 예외 없음.
- `.gitattributes`의 `* text=auto eol=lf`: git이 커밋할 때 CRLF를 LF로 정규화하고, 어느
  OS에서나 LF로 체크아웃한다(각자의 `core.autocrlf`와 무관). Windows 편집기가 CRLF로 저장해도
  커밋하면 LF가 된다.
- **GitHub 웹 업로드는 git 정규화를 거치지 않는다** - CRLF 파일을 올리면 그대로 들어가고
  게이트(`tests/test_repo_hygiene.py`)가 실패한다. 받아서 `python tools/fix_eol.py`로 고친다.
- **커밋 전에 `python -m ruff format .` 그리고 `python tools/fix_eol.py`** - 서식을 맞추고
  CR이 섞인 파일을 LF로 바꾼다(ruff format도 `line-ending = "lf"`).
- 파이썬으로 파일을 쓸 때는 `open(..., "w", newline="\n")` - 지정하지 않으면 Windows에서
  CRLF로 써진다(tests/conftest.py의 골든 쓰기 참고).
- 줄끝 통일 커밋들은 `.git-blame-ignore-revs`에 등록돼 있다:
  `git config blame.ignoreRevsFile .git-blame-ignore-revs` (한 번만)

## 기억 파일 (MEMORY.md / .memory/)

- `MEMORY.md`는 **색인이다. 40줄 이하.** *Now* 절에는 다음에 할 일과 "써 놓았지만
  아직 확인 안 된 것"만 둔다. 세션마다 *Now*를 갱신한다(변화 없음이라도).
- 자세한 내용은 `.memory/` 아래 - 어느 파일에 무엇을 쓰는지는 `.memory/README.md`.
- 기억 파일 수정은 그 내용과 관련된 코드와 **같은 커밋**에 넣는다. 따로 커밋하면
  커밋하는 순간 낡는다.

## Git 작업 규칙

**커밋하면 그 커밋을 바로 원격 저장소(origin)에 push한다.** 커밋만 하고 로컬에 쌓아 두지 않는다.

이 과정은 `.githooks/post-commit` 훅이 자동으로 한다. 커밋이 끝나면 훅이 현재 브랜치를 `origin`에 push하고, 처음 올리는 브랜치면 upstream도 설정한다. 리베이스나 체리픽 중에는 건너뛴다.

### 훅 켜기 (저장소마다 한 번)

```
git config core.hooksPath .githooks
```

`git config core.hooksPath`가 `.githooks`를 출력하면 켜진 상태다. 커밋할 때 `[post-commit] origin/<브랜치> 에 push합니다...`가 출력되면 정상이다.

`hint: The '.githooks/post-commit' hook was ignored because it's not set as executable`가
나오면 실행 권한이 빠진 것이다: `chmod +x .githooks/post-commit` (git에는 100755로
저장돼 있다. GitHub 웹에서 이 파일을 다시 올리면 권한이 사라지니 주의).

### 커밋할 때 확인할 것

1. 커밋한 뒤 출력에서 push 성공 여부를 확인한다.
2. `[post-commit] push에 실패했습니다`가 나오면 커밋은 로컬에 남아 있다. 원인(네트워크, 인증, 원격이 앞서 있음 등)을 해결하고 `git push`로 직접 올린다.
3. 훅이 켜져 있지 않은 환경이면 커밋 직후 `git push`를 직접 실행한다.
4. 원격에 이미 올라간 커밋은 `--amend`나 `rebase`로 고치지 말고 새 커밋으로 수정한다(강제 push가 필요해지기 때문).

### 커밋 단위와 메시지

- **한 작업 = 한 커밋.** 파일 하나 고칠 때마다가 아니라, 한 문장으로 설명할 수 있는
  단위(계획 한 단계, 버그 하나 수정, 리팩터링 한 걸음)마다. 게이트 통과 후에 커밋한다.
- **제목은 바꾼 파일이 아니라 변경의 요점을 쓴다.**
  좋음: `전투 판정 함수를 combat_system에서 분리 -- 동작 불변, 골든 그대로`
  나쁨: `Update combat_system.py`
- **본문에는** 무엇을 왜 바꿨는지, 무엇을 검증했고 무엇이 아직 열려 있는지를 쓴다.
- 커밋하지 않는 것: `game/saves/`, `.buildozer/`, `bin/`, zip 파일, 반쯤 된 작업
  (그럴 땐 브랜치를 쓴다).
