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
  받는다(수십 분). 꼭 필요할 때만 바꾼다.
