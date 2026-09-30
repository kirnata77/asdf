# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. 40줄 이하.

## Now - 2026-09-30 (PR #3 병합: 리뷰 버그 B2~B12 + 화면 변경 4건이 `main`에 있음)

**작업 흐름**(CLAUDE.md "Git"): 기능마다 `main`에서 브랜치 -> 게이트 통과 -> PR -> CI 초록이면 병합(병합은 사용자 확인).
push는 검증된 작업만, 자동 push 훅 없음. 줄끝은 pre-commit 훅. `main` 기준 테스트 291개 · 커버리지 93.8%.
PR #4: 병합된 `claude/*` 브랜치는 워크플로가 지운다(#3, #4 병합 때 동작 확인).

**`main`에 들어간 것:** 화면 요청 4건 - 기본 성별(귀검사만 m), 이름 최대 6자, 장비 교체
팝업(테두리 칸/상세보기), 핸드폰 [뒤로] 키 ([`sessions/2026-09-30-ui-fixes.md`](.memory/sessions/2026-09-30-ui-fixes.md)).
리뷰 버그 B2~B12 - 사용자 결정: B4 이름 중복은 시작을 막고 안내, B8 같은 이름 몬스터는 "고블린 A/B/C",
B10 버프 수식은 시전자 기준, B11 걸 때 한 번 굴림 ([`sessions/2026-09-30-bug-fixes.md`](.memory/sessions/2026-09-30-bug-fixes.md)).
**실기기 미확인** - [뒤로] 키 전달, 한글 조합 입력 중 6자 자르기.

**다음:** B1(도망 비용) 규칙 결정 후 수정, 아래 사용자 결정 3건(데이터).
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
