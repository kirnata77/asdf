# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. 40줄 이하.

## Now - 2026-09-29 (refactor/prep: 리팩터링 준비 완료, PR #1 열림 - 병합 대기)

**PR #1** `refactor/prep` -> `main`, **병합하지 말 것**(사용자 지시). 게임 동작 변경 없음.
이 브랜치: DoD 게이트, CI, 훅 실행권한 수정, **전 파일 CRLF**(`* -text`, 테스트로 강제),
문서/기억 체계, **테스트 247개 · 커버리지 94%**(전 39%) - 게이트 하한 90%.

**다음:** roadmap R0(알려진 버그, 동작 변경이라 따로) 또는 R1(이름 오타)부터. R4(전투 분할)의
선행 조건인 테스트는 끝났다. 모든 단계는 골든 불변이 조건.

**믿으면 안 되는 것** ([`known-bugs.md`](.memory/active-issues/known-bugs.md)):
**귀참을 쓰면 NameError**. 방어구 세트효과는 절대 안 걸린다(구성품 없음). 몬스터 18종은 HP 1로
등장(데이터 "미정"). `quest_system.py` import 불가. 빌드 노트는 낡고 잘림.
**화면(kivy)은 테스트 범위 밖**, APK 빌드는 CI에서만 확인된다.

## 어디에 무엇이 있나

| 읽을 것 | 언제 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | 규칙: 계층, DoD, 테스트 지도, CRLF, git |
| [`.memory/README.md`](.memory/README.md) | 어느 기억 파일에 무엇을 쓰나 |
| [`.memory/active-issues/`](.memory/active-issues/) | 값/문서/동작을 믿기 전에 |
| [`.memory/roadmap/`](.memory/roadmap/) | 다음에 할 일, 숫자가 있는 사실 |
| [`.memory/sessions/`](.memory/sessions/) | 왜 그렇게 결정했나 (헛발질 포함) |
| [`docs/`](docs/) | 빌드 노트 |

## 규칙
- *Now*는 세션마다 갱신한다. 숫자가 있는 사실은 roadmap, 경위는 sessions,
  아직 확인 안 된 것/알려진 버그는 active-issues로.
