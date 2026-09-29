# 알려진 버그 / 낡은 문서 / 확인 안 된 것

해결하면 항목을 지우고, 관련 테스트/ruff 예외도 같은 커밋에서 지운다.

## 코드

- **`game/system/quest_system.py` 내용이 `test` 한 단어뿐** - import하면 `NameError`.
  지금은 아무도 import하지 않는다(`file_path.py`의 경로 문자열만 있음). 업로드 전
  원본부터 자리표시자였다(`f041143`에서 지운 파일도 `test`였고 `babd105`가 같은 내용으로
  다시 만듦). 퀘스트 기능을 만들 때 채울 자리 - 그 전까지는 빈 모듈(docstring만)로
  바꾸는 것이 가장 작은 수정.
  - 테스트: `tests/test_imports.py`의 strict xfail - 고치면 XPASS로 실패하니 목록에서 지운다.
  - ruff: `pyproject.toml`의 `F821` 예외도 지운다.
- **새 캐릭터에는 `"전직"` 키가 없다**, 세이브를 불러오면 `게임_불러오기`가
  `전직=None`을 채운다 - 새 게임과 불러온 게임의 캐릭터 dict 모양이 다르다.
  코드는 `.get("전직")`으로 읽어서 지금은 문제 없음. `_캐릭터_생성`에서 `None`으로
  채우면 통일되지만, 골든(new_game_*.json)이 바뀌는 **동작 변경**이라 리팩터링과 분리할 것.
  테스트: `test_세이브_불러오기_왕복`이 현재 차이를 고정.
- **`equipment_system.py:15` 안 쓰는 import** (`character_data_system`) - ruff `F401`
  예외로 둠. 지워도 되는지(순환 import 회피용인지) 확인 후 정리.
- **화면이 system의 비공개 함수를 부른다** - `screens_battle.py`가
  `skill_system._정수_평가`를 직접 호출(555, 502행). 계층 규칙 위반, roadmap R3.

- **줄끝이 섞여 있다** - CRLF 116개, LF 29개(`git ls-files --eol`). 파이썬으로 파일을
  고칠 때 `open(..., newline="")`로 읽고 써야 원래 줄끝이 유지된다 - 안 그러면 diff가 파일
  전체가 된다(이 세션에서 `file_path.py`로 한 번 겪음). 통일은 roadmap R0.5.

## 문서

- **`docs/mobile_apk_build_notes.md`가 낡고 잘려 있다** (2026-09-16 기준, 업로드 때
  옮겨 온 것):
  - 마지막 줄이 문장 중간에서 끝난다(`dnf_mobile.zip만`).
  - `buildozer.spec` 주석이 "빌드 노트 11절/13절"을 가리키는데 노트에는 4절까지만 있다.
  - "상점/NPC/창고 비활성" - 상점은 이제 구현돼 있다(`shop_system.py`, 225줄).
  - 폰트를 `NanumGothic-Regular/Bold.ttf`라고 하지만 실제는 `NanumGothic-Diet.ttf` 1개.
  - 빌드 방법이 Colab 기준 - 지금은 GitHub Actions(`build-apk.yml`)가 빌드한다.
- **`buildozer.spec`의 `package.domain = org.test`** - 원래 값을 몰라 기본값을 씀(spec 주석).
  예전 APK와 다르면 폰에 별도 앱으로 깔리고 세이브가 이어지지 않는다. 확인 안 됨.

## 검증 범위 밖

- **화면(game/screens/, main.py)은 테스트가 없다** - kivy가 필요하고 CI에 없음.
- **APK 빌드**는 `build-apk.yml`에서만 되고, 그 워크플로 파일이 바뀔 때만 자동 실행된다.
  이 브랜치로는 빌드해 보지 않았다. 게임 코드는 안 바뀌었고, `tools/check.py`가
  `source.dir = .`/`include_exts = py` 때문에 APK에 같이 들어가지만 무해하다
  (`tests/`는 `source.exclude_dirs`로 이미 빠짐). 빼려면 spec 수정 = CI 캐시 무효화.
