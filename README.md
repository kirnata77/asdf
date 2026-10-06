# 던전앤파이터 모바일 프로토타입

Kivy로 만든 턴제 RPG 프로토타입. 5개 직업(귀검사/격투가/거너/마법사/프리스트)으로 파티를 꾸려 마을, 던전, 전투, 성장,
장비/상점을 진행한다. 안드로이드 APK는 buildozer로 빌드한다.

- 원격 저장소: https://github.com/kirnata77/asdf (기본 브랜치 `main`)
- 규칙(계층, 완료 기준, 테스트, git): [`CLAUDE.md`](CLAUDE.md) - 기여 전에 읽는다
- 지금 진행 중인 일: [`MEMORY.md`](MEMORY.md)

## 실행

```
pip install kivy
python main.py
```

세이브는 `game/saves/slot_N.json`에 저장된다(JSON, 슬롯 3개). 화면은 한글 폰트(`game/assets/font/`)를 쓴다.

## 개발

```
pip install pytest pytest-cov ruff==0.16.9   # CI와 같은 버전
git config core.hooksPath .githooks          # 줄끝을 LF로 맞추는 pre-commit 훅
python tools/check.py                        # 완료 기준 게이트: compileall + ruff + pytest + 커버리지
```

- 로직(전투, 스킬, 장비, 세이브 ...)은 kivy 없이 돈다. 테스트(`tests/`)도 화면 없이 돌고, 골든 파일(`tests/golden/`)과 풀 시나리오(`docs/scenarios.md`)로 검증한다.
- 화면을 바꿨다면 `xvfb-run -a -s "-screen 0 720x1280x24" python tools/ui_smoke.py`로 실제 화면을 돌려 본다(리눅스 기준).

## 구조

```
main.py            Kivy 앱 진입점
gameflow.py        화면 <-> 로직 창구 (화면은 이 파일의 함수만 부른다)
game/screens/      Kivy 화면
game/system/       전투(combat/), 스킬, 장비, 세이브 등 게임 로직
game/data/         직업, 몬스터, 던전, 아이템 데이터(파이썬 딕셔너리)
game/assets/       폰트, 이미지
tests/  tools/    테스트, 게이트(check.py)와 화면 스모크(ui_smoke.py)
docs/  .memory/   빌드 노트, 구조 점검 보고서, 작업 기억
```

계층은 한 방향이다: `screens -> gameflow -> system -> data`. 자세한 구조와 점검 결과는 [`docs/architecture_review.md`](docs/architecture_review.md).

## 빌드

APK는 GitHub Actions의 "Build APK" 워크플로(수동 실행)가 만든다. 방법과 주의점은 [`docs/mobile_apk_build_notes.md`](docs/mobile_apk_build_notes.md).

## 문서

| 파일 | 내용 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | 규칙과 완료 기준 |
| [`docs/architecture_review.md`](docs/architecture_review.md) | 구조/아키텍처 점검, 다음 로드맵 |
| [`docs/scenarios.md`](docs/scenarios.md) | 풀 시나리오 장부 |
| [`docs/mobile_apk_build_notes.md`](docs/mobile_apk_build_notes.md) | APK 빌드 노트 |
| [`.memory/`](.memory/README.md) | 작업 기억(진행 상황, 알려진 문제, 경위) |
