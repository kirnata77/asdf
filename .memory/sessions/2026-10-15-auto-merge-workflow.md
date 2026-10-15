# 2026-10-15 자동 병합 워크플로 (auto-merge.yml)

## 결정 (사용자, 2026-10-15)

- stella-rain/core의 `auto-merge.yml`을 옮긴다. 세션이 PR을 지켜보다 병합하던 방식(10-14 지시: 자동 병합을 켜고, 안 되면 CI 초록 즉시
  병합)은 세션이 죽으면 PR이 남는다 - 워크플로는 세션과 상관없이 병합한다.
- 병합 대상은 `claude/*` 브랜치뿐(`ccr-*`는 넣지 않음). 초안, `.github/workflows/`·`buildozer.spec`을 바꾸는 PR은 사용자가 병합한다.
- 판정 스크립트는 stella-rain/.github의 재사용 워크플로를 부르지 않고 `tools/auto_merge_gate.py`로 복사했다. 그쪽 `@main`을
  부르면 남의 main이 이 저장소의 쓰기 권한으로 돈다. 대가: 그쪽 수정은 손으로 옮겨야 한다.
- 함께 본 것 중 넣지 않은 것: 비밀값 검사(repo-check), actionlint 워크플로(사용자가 고르지 않음). claude-md-check·eol-check·
  branch-cleanup은 이미 있다(`test_repo_hygiene.py`, `delete-merged-branch.yml`). project-sync 등은 그쪽 조직 전용.

## 옮기며 바꾼 것

- **경쟁 조건:** stella는 `workflow_run.event == 'pull_request'`일 때만 판정한다. asdf의 check.yml은 push와 pull_request 둘 다에서
  돌아 한 커밋에 `check`가 둘 붙으므로, push 실행이 나중에 끝나면 영영 병합되지 않는다. 어느 쪽이 끝나든 판정하게 했다
  (같은 이름 검사가 둘이면 둘 다 끝나야 한다 - `test_같은_이름의_검사가_둘이면_둘_다_끝나야_한다`).
- 기준 브랜치 `main-branch`, 필수 검사 `check`·`ui-smoke`(check.yml 잡 id - `test_repo_hygiene`가 대조).
- GITHUB_TOKEN 병합이라 main-branch push 워크플로(`warm-cache.yml`)와 `delete-merged-branch.yml`이 돌지 않는다. 브랜치는 워크플로가
  지우고, `buildozer.spec` PR은 사용자가 병합하므로 캐시 채우기는 그대로 돈다.

## NOT VERIFIED

- 워크플로의 실제 실행: `workflow_run`은 기본 브랜치의 파일을 읽으므로 이 PR이 병합된 뒤 첫 `claude/*` PR에서 확인한다.
  로컬에서는 actionlint(+shellcheck)와 단위 테스트만 돌렸다.
