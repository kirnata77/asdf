"""완료 기준(DoD) 게이트 - 커밋 전에 이것 하나만 돌린다.

    python tools/check.py

1. compileall  : 모든 .py 파일 문법 검사
2. ruff check  : 정의 안 된 이름, 안 쓰는 import 등 (pyproject.toml 설정)
3. pytest      : tests/ (kivy 없이 gameflow 이하 로직만 헤드리스로 검사)
                pytest-cov가 설치돼 있으면 game/system + gameflow.py 커버리지가
                COVERAGE_FLOOR(%) 아래로 떨어져도 실패한다(CI는 항상 설치).

하나라도 실패하면 0이 아닌 코드로 끝난다. Windows/리눅스 어디서나 돈다.
필요한 도구: pip install pytest ruff pytest-cov
"""

import importlib.util
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 리팩터링 준비(2026-09-29) 시점 94%. 떨어뜨리지 말고, 올리면 이 값도 올린다.
COVERAGE_FLOOR = 90

PYTEST = [sys.executable, "-m", "pytest"]
if importlib.util.find_spec("pytest_cov") is not None:
    PYTEST += ["--cov=game.system", "--cov=gameflow", "--cov-branch",
               "--cov-report=term:skip-covered", f"--cov-fail-under={COVERAGE_FLOOR}"]

STEPS = [
    ("compileall", [sys.executable, "-m", "compileall", "-q",
                    "-x", r"[\\/](\.buildozer|bin|\.git)[\\/]", "."]),
    ("ruff check", [sys.executable, "-m", "ruff", "check", "."]),
    ("pytest", PYTEST),
]


def main():
    failed = []
    for name, cmd in STEPS:
        if name == "pytest" and not os.path.isdir(os.path.join(ROOT, "tests")):
            print(f"== {name}: tests/ 없음, 건너뜀")
            continue
        print(f"== {name}")
        if name == "pytest" and "--cov-branch" not in cmd:
            print("   (pytest-cov 없음 - 커버리지 하한 검사를 건너뜀: pip install pytest-cov)")
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            failed.append(name)
    print()
    if failed:
        print("FAIL: " + ", ".join(failed))
        return 1
    print("PASS: 모든 검사 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main())
