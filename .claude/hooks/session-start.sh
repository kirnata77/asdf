#!/bin/bash
# 클라우드 세션을 시작할 때마다 graft(코드 그래프 CLI)를 설치하고, 연결 파일이 빠졌으면 다시 쓰고(init), 그래프를 만든다.
# init 옵션: 홈 디렉터리(~/.claude*)와 다른 에이전트용 파일은 건드리지 않고, 커밋된 statusLine도 덮지 않는다.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

npm install -g @nanonets/graft
graft telemetry disable
graft init --yes --no-global --no-agents --no-statusline
