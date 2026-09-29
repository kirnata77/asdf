# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. 40줄 이하.

## Now - 2026-09-29 (refactor/prep: 리팩터링 준비, 게임 코드는 안 바꿈)

**브랜치 `refactor/prep`** (main에서 분기, 히스토리 공유). 이 브랜치에서 한 일:
DoD 게이트(`python tools/check.py`), 특성 테스트 130개 + 골든 14개, CI(`check.yml`),
post-commit 훅 실행권한 수정(그전엔 리눅스/맥 클론에서 자동 push가 한 번도 안 돌았음),
문서/기억 체계. **main에 병합 전** - PR 여부는 사용자 결정.

**다음:** `.memory/roadmap/refactor.md`의 R1(이름 오타 정리)부터. 각 단계는 골든 불변이 조건.

**믿으면 안 되는 것** ([`known-bugs.md`](.memory/active-issues/known-bugs.md)):
`quest_system.py`는 import하면 NameError. `docs/mobile_apk_build_notes.md`는 끝이 잘려 있고
일부 낡음(상점 비활성, 폰트 이름, `buildozer.spec`이 가리키는 11/13절 없음).
**화면(kivy)은 테스트 범위 밖**, APK 빌드는 CI에서만 확인된다.

**CI `check.yml` 녹색** - run #1(`d8106a6`), #2(`1b64432`) 모두 success, 약 15초.

## 어디에 무엇이 있나

| 읽을 것 | 언제 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | 규칙: 계층, DoD, git |
| [`.memory/README.md`](.memory/README.md) | 어느 기억 파일에 무엇을 쓰나 |
| [`.memory/active-issues/`](.memory/active-issues/) | 값/문서/동작을 믿기 전에 |
| [`.memory/roadmap/`](.memory/roadmap/) | 다음에 할 일, 숫자가 있는 사실 |
| [`.memory/sessions/`](.memory/sessions/) | 왜 그렇게 결정했나 (헛발질 포함) |
| [`docs/`](docs/) | 빌드 노트 |

## 규칙
- *Now*는 세션마다 갱신한다. 숫자가 있는 사실은 roadmap, 경위는 sessions,
  아직 확인 안 된 것/알려진 버그는 active-issues로.
