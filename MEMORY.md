# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. 40줄 이하.

## Now - 2026-09-30 (B1 도망 규칙 + 치트용 마법석: 브랜치 `claude/gifted-ramanujan-y6xska`, PR 전)

**작업 흐름**(CLAUDE.md "Git"): 기능마다 `main`에서 브랜치 -> 게이트 통과 -> PR -> CI 초록이면 병합(병합은 사용자 확인).
push는 검증된 작업만, 자동 push 훅 없음. 줄끝은 pre-commit 훅. 이 브랜치 기준 테스트 295개 · 커버리지 93.8%.

**이 브랜치:** B1 - 도망은 현재 턴 캐릭터가 굴리고, 실패하면 그 턴이 끝난다. 파티 중 한 명이라도
구속이면 [도망]이 "대상/상태이상" 팝업으로 막힌다 ([`sessions/2026-09-30-flee-rule.md`](.memory/sessions/2026-09-30-flee-rule.md)).
치트용 마법석(레어도 치트, 티어 99, 모든 상점 0골드) - 파티 중 한 명이라도 끼면 무작위 인카운트와
걸음수가 멈춘다, 이벤트 전투는 그대로 ([`sessions/2026-09-30-cheat-magicstone.md`](.memory/sessions/2026-09-30-cheat-magicstone.md)).
**`main`에 있는 것:** 화면 요청 4건, 리뷰 버그 B2~B12 (PR #3).
**실기기 미확인** - [뒤로] 키 전달, 한글 조합 입력 중 6자 자르기.

**다음:** 사용자가 브랜치 정리(두 작업이 한 브랜치에 있음) 후 PR, 아래 사용자 결정 3건(데이터).
원격에 남은 `claude/*` 브랜치 3개(`claude-md-cleanup-mmo8lm`, `ui-fixes`, `modest-mendel-4u7t2p`)는
사용자가 삭제하기로 함 - 세션 프록시가 브랜치 삭제 push를 403으로 막아 GitHub에서 직접.

**믿으면 안 되는 것** ([`known-bugs.md`](.memory/active-issues/known-bugs.md)):
귀검사는 `귀신 : 카잔`을 배울 수 없다(레벨3 목록 누락). 몬스터 18종은 HP 1로
등장(데이터 "미정"). 빌드 노트는 낡고 잘림.
**화면(kivy)은 테스트 범위 밖**, APK 빌드는 CI에서만 확인된다.

## 어디에 무엇이 있나

| 읽을 것 | 언제 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | 규칙: 계층, DoD, 테스트 지도, 가드레일, 줄끝, git |
| [`.memory/README.md`](.memory/README.md) | 어느 기억 파일에 무엇을 쓰나 |
| [`.memory/active-issues/`](.memory/active-issues/) | 값/문서/동작을 믿기 전에 |
| [`.memory/roadmap/`](.memory/roadmap/) | 다음에 할 일, 숫자가 있는 사실 |
| [`.memory/sessions/`](.memory/sessions/) | 왜 그렇게 결정했나 (헛발질 포함) |
| [`docs/`](docs/) | 빌드 노트 |

## 규칙
- *Now*는 세션마다 갱신한다. 숫자가 있는 사실은 roadmap, 경위는 sessions,
  아직 확인 안 된 것/알려진 버그는 active-issues로.
