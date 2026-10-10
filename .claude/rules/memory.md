---
paths:
  - "MEMORY.md"
  - ".memory/**"
---

## 기억 파일 (MEMORY.md / .memory/)

- `MEMORY.md`는 **색인이다. 40줄 이하, 6KB(6,144바이트) 이하, 한 줄 200자 이하.** 한글은 글자당 3바이트라
  줄 수만 지켜서는 크기가 넘고, 한 줄에 문단을 넣으면 색인이 아니게 된다 - 셋 다 지킨다. 게이트(`tests/test_repo_hygiene.py`)가 검사하고,
  넘으면 실패한다. 넘칠 때는 규칙/수치 설명을 `.memory/roadmap/game-rules.md`로, 경위는 `sessions/`로
  옮기고 MEMORY.md에는 한 줄 링크만 남긴다. *Now* 절에는 다음에 할 일과 "써 놓았지만
  아직 확인 안 된 것"만 둔다. 세션마다 *Now*를 갱신한다(변화 없음이라도).
- 자세한 내용은 `.memory/` 아래 - 숫자가 있는 사실은 `roadmap/`, 믿으면 안 되는 것은
  `active-issues/`, 헛발질을 포함한 경위는 `sessions/`(자세히는 `.memory/README.md`).
- `MEMORY.md`와 `.memory/`는 세션마다 바뀌는 단기 기억이다. "무엇이 릴리스에 들어갔나"는 여기 쓰지 않고 `CHANGELOG.md`에 쓴다.
- 기억 파일 수정은 그 내용과 관련된 코드와 **같은 커밋**에 넣는다. 따로 커밋하면
  커밋하는 순간 낡는다.
