# 리팩터링 로드맵

측정: 2026-09-29, 커밋 `1b64432`(refactor/prep) 기준, `wc -l`/`grep -c "^def "`.

## 모든 단계의 완료 조건

1. `python tools/check.py` 통과.
2. **`tests/golden/` 변경 없음** - 리팩터링은 동작 불변. 골든이 바뀌면 리팩터링이 아니다.
3. 파일을 옮기거나 이름을 바꾸면 `game/data/file_path.py`도 같은 커밋에서 고친다
   (`test_file_path_레지스트리가_실제_파일과_일치`가 잡는다).
4. 화면 파일을 건드렸으면 실행 확인, 못 했으면 커밋에 `NOT VERIFIED`.
5. 한 단계 = 한 커밋(큰 단계는 여러 커밋으로 쪼개되 각 커밋이 게이트 통과).

## 현황 (숫자)

| 파일 | 줄 | 함수 | 문제 |
|---|---|---|---|
| `game/system/combat_system.py` | 2706 | 109 | 한 모듈에 전투의 모든 것. `# ====` 절 경계가 이미 있음(아래 R4) |
| `gameflow.py` | 1376 | ~90 | 5직업 x 5종(레벨업/특성/무기/스킬/퍽) import와 레지스트리를 손으로 반복 |
| `game/system/skill_system.py` | 1221 | 35 | combat_system과 서로 위임하는 함수들(“원래 skill_system.py에 있던 함수들” 절) |
| `game/data/monster/monster_race_goblin.py` | 1839 | - | 데이터 - 리팩터링 대상 아님 |

전체 파이썬 약 24,400줄. 테스트 247개(1.5초), 골든 35개, 커버리지 94% (아래 "테스트").

## 단계 (위에서부터 - 위험이 낮고 이후 단계를 쉽게 하는 순서)

- **R0 알려진 버그 정리** - 코드 버그 4건 완료(2026-09-29). 남은 것은 데이터 결정 1건(카잔 습득; 몬스터 HP/AC는 2026-09-30 역할군 공식으로 해결) (리팩터링 아님, 동작 변경 커밋으로 따로)
  ~~`quest_system.py` 빈 모듈화, `equipment_system` 안 쓰는 import~~(완료), ~~귀참 NameError~~(완료), ~~방어구 세트효과 미발동~~(완료), ~~몬스터 18종 HP/AC "미정"~~(완료, 역할군 공식).
  → `.memory/active-issues/known-bugs.md`
- ~~R0.5 줄끝 통일~~ **완료 2026-09-29** - 처음엔 전부 CRLF(`1644c57`)로 했다가, 사용자가 LF로
  정정해 전부 LF로 다시 변환(`* text=auto eol=lf`, 196개 파일). 두 변환 커밋 모두 blame 무시 등록.
- ~~R1 이름 오타 정리~~ **완료 2026-09-29** (파일 12개, 참조 50개 파일, 골든 불변). - `formet` → `format`(8개 파일), `accesery` → `accessory`(4개 파일).
  파일 12개 이름 변경 + 참조 50개 파일. 순수 기계적 변경이라 골든 불변이 확실해야 함.
  세이브 JSON에 모듈명이 들어가는지 먼저 확인(들어가면 호환 처리 필요).
  `job_skill_format.py`/`perks_class_format.py`/`job_ability_format.py`는 이미 올바른 철자.
- ~~R2 gameflow 직업 레지스트리 데이터화~~ **완료 2026-09-29** (import 25줄 -> 표 5줄, 레지스트리 지문 동일, 골든 불변). - 54~135행의 직업별 import 반복을
  `{직업: (분류번호, 파일접미사)}` 표 + `importlib` 한 번으로. 직업 추가가 한 줄이 되게.
  (`importlib`은 이미 전직 레지스트리에서 쓰고 있음, 82행)
- ~~R3 화면 → system 직접 호출 없애기~~ **완료 2026-09-29** (gameflow "화면용 조회" 8개, 정적 규칙 테스트, ui_smoke로 실행 확인). - `screens_battle.py`(skill_system, 비공개
  `_정수_평가` 포함), `screens_party.py`(character_levelup_system)를 gameflow 함수로.
  화면 변경이므로 실행 확인 필요.
- ~~R4 combat_system 분할~~ **완료 2026-09-29** - 12개 모듈(core/formula/participants/traits/status/stats/resources/damage/attacks/monster_actions/reactions/flow), 117개 정의 AST 동일, 주석 278줄 보존, 골든 불변. 아래는 원래 계획: - 이미 있는 절 경계대로 `game/system/combat/` 패키지로:
  수식 평가(126~), 참가자 인스턴스(222~), 특성/칭호 반영(432~849), 상태이상/버프 집계
  (850~1211), 턴 순서(1212~), 명중/피해(1261~), 공격 실행(1547~), 턴 진행(1965~),
  반응특성(2044~), 소환수(2455~). `combat_system.py`는 재수출(re-export)만 남겨서
  gameflow/skill_system의 import가 안 깨지게 한 뒤, 호출부를 천천히 옮긴다.
- ~~R5 호출부를 combat 패키지로 옮기고 skill_system ↔ combat 위임 정리~~ **완료 2026-09-29** -
  gameflow/skill_system/tests/tools가 `game.system.combat.<모듈>`을 직접 쓰고, 호환 모듈
  `combat_system.py`와 skill_system의 순수 위임 함수 5개를 지웠다(`다음_턴`은 실제 동작이 있어 유지).
  주석/docstring의 `combat_system.X` 언급도 `combat.<모듈>.X`로 바꿈. 골든 불변.
- ~~R6 ruff format 적용~~ **완료 2026-09-29** - 135개 파일 서식만 바꾼 커밋(`7905c80`, AST 동일,
  blame 무시 등록), 게이트에 `ruff format --check`, CI ruff 0.16.9 고정.

## 테스트 (R4 전 선행 조건) - 완료 2026-09-29

분할 전에 모든 게임 로직을 테스트로 덮는다는 사용자 결정에 따라 먼저 했다.
247개 통과 + 1 xfail, 1.5초. 커버리지(branch 포함, game/system + gameflow.py):

| 모듈 | 전 | 후 |
|---|---|---|
| combat_system | 43% | 91% |
| skill_system | 6% | 91% |
| gameflow | 61% | 97% |
| 나머지 system 12개 | 9~100% | 97~100% |
| **합계** | **39%** | **94%** |

게이트가 90% 아래로 떨어지면 실패한다(`tools/check.py` `COVERAGE_FLOOR`).
남은 6%는 대부분 데이터에 아직 없는 분기(몬스터 소환수 공격의 일부 타입, 해제시 특성의
일부 조건, 반응 선택 팝업 경로 등) - R4에서 해당 코드를 옮길 때 필요하면 합성 데이터로
보강한다. 테스트 파일별 범위는 CLAUDE.md "테스트 지도".
