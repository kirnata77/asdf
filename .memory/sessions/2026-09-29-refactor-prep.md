# 2026-09-29 - 리팩터링 준비 브랜치 (refactor/prep)

## 요청

저장소 분석 + 리팩터링 준비용 새 브랜치("graft 사용"). 업로드된 다른 프로젝트
(lakehouse-k8s)의 CLAUDE.md/MEMORY.md/구조 문서에서 쓸 만한 규칙을 가져와 적용.
계획 먼저.

## 결정

- **"graft"의 의미** - 세 가지 해석을 제시: (1) main에서 보통 분기, 규칙만 이식
  (2) `git replace --graft` + filter-branch로 업로드 커밋 50개를 루트 커밋 하나로 압축한
  새 루트 (3) 로컬 전용 replace. 사용자가 **(1) 보통 브랜치**를 선택. 이유: (2)는 main과
  히스토리가 끊겨 PR 병합에 `--allow-unrelated-histories`가 필요하다. 히스토리 50개가
  전부 "Update X.py"라 정보는 없지만 끊는 비용이 더 크다.
- **이식한 것**: 계획 먼저, 자동 수정 2회 제한, 한 명령 DoD 게이트, 한 작업 한 커밋 +
  요점 중심 커밋 메시지, MEMORY.md 색인(40줄) + `.memory/` 3폴더(한 벌만, 크기 제한),
  black+isort 대신 ruff, 문서는 한 곳(`docs/`).
- **이식 안 한 것**: helm/k8s/노트북/환경별 비밀 관리 전부, 그리고 "push는 수동" -
  이 저장소는 post-commit 훅이 자동 push하는 규칙이 우선.
- **Makefile 대신 `tools/check.py`** - 사용자 경로(`Z:\백업\...`)로 보아 Windows.
- **pyproject.toml은 도구 설정만** - 앱은 buildozer.spec이 빌드하므로 설치형 패키지로
  만들지 않고 `pytest pythonpath=["."]`로 해결.

## 발견 (헛발질 포함)

- **post-commit 훅이 실행 권한 없이(100644) 커밋돼 있었다** - 첫 커밋 때 git이
  "hook was ignored" 경고만 내고 push하지 않았다. 수동 push 후 `update-index --chmod=+x`
  커밋으로 수정, 그 다음 커밋부터 훅이 자동 push함을 확인.
- **ruff가 두 개** - `/root/.local/bin/ruff` 0.15.8과 pip의 0.16.9. 0.16은 기본 규칙이
  넓어서 같은 트리에 0개 vs 61개. `select`를 명시해 버전 무관하게 고정.
- `ruff format`을 돌리면 110개 파일이 바뀐다 - 게이트에서 제외(roadmap R6).
- `quest_system.py`는 내용이 `test`뿐(원본부터). 새 캐릭터에 `전직` 키가 없고 불러오면
  생긴다. 둘 다 고치지 않고 테스트로 현재 동작을 고정 + active-issues에 기록.
- 전투는 전역 `random`만 써서 `random.seed()`로 완전히 재현된다. PYTHONHASHSEED 0/42/미지정
  모두 같은 결과. 고블린 HP 수식 하나를 바꾸면 테스트 5개가 실패함(변이 검사).
- `file_path.py`를 파이썬으로 고쳤더니 diff가 파일 전체가 됨 - CRLF 파일이었다. 저장소에
  CRLF 116 / LF 29가 섞여 있음. `newline=""`로 다시 고침. 통일은 roadmap R0.5.
- `rm -rf tests/golden/*`가 안전 검사에 막혔다 - 필요 없었음(`UPDATE_GOLDEN=1`이 덮어씀).

## 커밋 (refactor/prep)

1. DoD 게이트 (`tools/check.py`, `pyproject.toml`)
2. post-commit 훅 실행 권한
3. 특성 테스트 + 골든
4. CI `check.yml`
5. `file_path.py` 드리프트 테스트
6. 문서/기억 체계 (이 파일)

## 확인된 것

- CI `check.yml` run #1(`d8106a6`)과 #2(`1b64432`) 모두 success(약 15초).

## 열린 것

- main 병합(PR) 여부는 사용자 결정.
- 줄끝 통일을 LF로 할지 CRLF로 할지는 사용자 결정(R0.5).
