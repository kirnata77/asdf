---
paths:
  - "game/system/save_system.py"
  - "game/system/state_schema.py"
  - "buildozer.spec"
  - ".github/workflows/build-apk.yml"
  - "docs/mobile_apk_build_notes.md"
---

## 세이브 호환성과 APK 빌드

- **세이브 호환성.** `game/saves/*.json` 형식(세이브 키 이름 포함)을 바꾸면 `save_system.세이브_버전`을
  올리고 `_마이그레이션` 표에 (새 버전, 변환 함수)를 더한다(옛 세이브 테스트 포함). 불러올 때마다 규칙에 맞춰
  다시 계산하는 값(최대HP 등)은 형식이 아니라 규칙이라 `gameflow.게임_불러오기`가 한다.
- **`buildozer.spec`을 바꾸면** CI 캐시 키가 바뀌어 다음 APK 빌드가 SDK/NDK를 새로
  받는다(수십 분). 꼭 필요할 때만 바꾼다. 릴리스마다 `version`을 올리므로 그때마다 캐시가 바뀐다는 점도 안다.
- **APK는 `v*` 태그 push로만 빌드된다.** 태그는 `v<spec의 version>`이어야 하고, 다르면 빌드가 첫 단계에서 실패한다.
  릴리스 이름은 태그(`v0.1.1`)이고 릴리스 본문은 그때의 `CHANGELOG.md`다.
- **버전은 major.minor.patch.** 변경 내역은 `CHANGELOG.md`만 본다(`MEMORY.md`는 세션 단기 기억). 큰 기능 PR이 `## 미릴리스`에 한 줄을 더한다.
  **릴리스 절차:** (1) 큰 기능이 병합되면 사용자에게 지금 릴리스할지 묻는다. (2) 지금이면 한 PR에서 `buildozer.spec`의 `version`을 올리고
  `## 미릴리스`를 `## x.y.z (날짜)`로 바꾼다(테스트가 둘이 맞는지 검사한다). **패치는 같은 마이너 안에서 쌓고, 마이너 릴리스는
  CHANGELOG를 비우고 새로 시작한다**(테스트가 지난 마이너 제목을 막는다). (3) 사용자가 병합한 뒤 **사용자가** GitHub 웹에서 릴리스를 게시한다:
  Releases -> Draft a new release -> 태그 `v<version>`(publish 때 새로 만들기), Target `main-branch`(병합 커밋), 설명은 CHANGELOG.md의 해당 부분.
  Claude는 태그를 못 만든다(이 세션의 git push가 403, GitHub 도구에도 태그 생성이 없음). 게시하면 태그가 생겨 워크플로가 돌고,
  이미 있는 릴리스에 APK를 붙인다. (4) Claude가 Actions 실행과 릴리스 페이지를 확인해 사용자에게 알린다.
