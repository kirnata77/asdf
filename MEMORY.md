# 현재 상태 - dnf mobile

**색인이지 기록이 아니다.** 낡는 순간 거짓이 되는 것만 여기 둔다. 40줄 이하.

## Now - 2026-09-30 (PR #1 병합됨, 브랜치 `claude/ui-fixes`에서 화면 변경 4건)

**PR #1** `refactor/prep`은 `main`에 병합됐다(사용자 친구가 병합). 자동 push 훅은 없고 줄끝은
pre-commit 훅. 테스트/게이트 숫자는 [`roadmap/`](.memory/roadmap/).

**`claude/ui-fixes`**(main에서 분기, PR 전): 예전 브랜치 `claude/modest-mendel-4u7t2p`의 화면
요청 4건을 새 구조에 다시 적용 - 기본 성별(귀검사만 m, 골든 변경), 이름 최대 6자, 장비 교체
팝업(테두리 칸/상세보기), 핸드폰 [뒤로] 키. 경위: [`sessions/2026-09-30-ui-fixes.md`](.memory/sessions/2026-09-30-ui-fixes.md).
**실기기 미확인** - [뒤로] 키 전달, 한글 조합 입력 중 6자 자르기.

**`claude/bug-fixes`**(`claude/ui-fixes` 위, PR 전): 리뷰 버그 B2~B12를 버그당 커밋 하나로 수정.
사용자 결정 - B4 이름 중복은 시작을 막고 안내, B8 같은 이름 몬스터는 "고블린 A/B/C", B10 버프
수식은 시전자 기준, B11 걸 때 한 번 굴림. **B1(도망 비용)은 보류.** 경위: [`sessions/2026-09-30-bug-fixes.md`](.memory/sessions/2026-09-30-bug-fixes.md).

**다음:** 두 브랜치의 PR/병합(친구 검토), B1 규칙 결정, 아래 사용자 결정 3건(데이터).

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
