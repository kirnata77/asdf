#!/bin/bash
# 클라우드 세션을 시작할 때마다 graft(코드 그래프 CLI)를 설치하고 그래프를 만든다.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

npm install -g @nanonets/graft
graft telemetry disable
graft build
