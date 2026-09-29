# 2026-09-29 CLAUDE.md 정리

사용자 요청: CLAUDE.md의 중복/불필요한 규칙 정리, 다른 프로젝트(lakehouse-k8s)의 CLAUDE.md에서
쓸 만한 점을 가져오기.

## 바꾼 것
- **post-commit 자동 push 훅 제거.** 커밋마다 push하면 로컬 커밋을 작업 중에 다듬을 수 없고
  (amend/rebase가 강제 push가 됨), 검증 전 상태가 원격에 올라갔다. 이제 규칙은
  "로컬 커밋은 작업 중 고쳐도 됨, 게이트 통과한 작업만 push, push한 커밋은 고치지 않음".
- **줄끝은 pre-commit 훅으로.** `.githooks/pre-commit`이 `tools/fix_eol.py`를 돌려 작업 트리를
  LF로 맞춘다(스테이지 내용은 .gitattributes가 이미 LF로 정규화). CLAUDE.md의 긴 줄끝 절은
  웹 업로드 예외만 남기고 줄였다. `test_repo_hygiene.py`의 훅 이름도 pre-commit으로.
- 가져온 것: 돌리지 못한 검증은 `NOT VERIFIED:`로(화면 한정 -> 전체), 값은 데이터가 아니라
  실행 결과로 확인, 되돌리기 어려운 명령은 실행 시점에 허락, `git add -A` 전에 `git status`,
  위험한 단계 전 커밋, 커밋 본문에 "이전 믿음과 그 비용".
- 낡는 숫자(스킬 62개, 커버리지 94% 등)는 CLAUDE.md에서 뺐다 - 숫자는 roadmap/MEMORY에.

## 검증
- `python tools/check.py` 통과(커밋 직전). 훅은 CRLF 임시 파일로 변환되는 것을 직접 확인.
