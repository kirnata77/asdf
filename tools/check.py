"""완료 기준(DoD) 게이트 - 커밋 전에 이것 하나만 돌린다.

    python tools/check.py

1. compileall  : 모든 .py 파일 문법 검사
2. ruff check  : 정의 안 된 이름, 안 쓰는 import 등 (pyproject.toml 설정)
3. pytest      : tests/ (kivy 없이 gameflow 이하 로직만 헤드리스로 검사)

하나라도 실패하면 0이 아닌 코드로 끝난다. Windows/리눅스 어디서나 돈다.
필요한 도구: pip install pytest ruff
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STEPS = [
    ("compileall", [sys.executable, "-m", "compileall", "-q",
                    "-x", r"[\\/](\.buildozer|bin|\.git)[\\/]", "."]),
    ("ruff check", [sys.executable, "-m", "ruff", "check", "."]),
    ("pytest", [sys.executable, "-m", "pytest"]),
]


def main():
    failed = []
    for name, cmd in STEPS:
        if name == "pytest" and not os.path.isdir(os.path.join(ROOT, "tests")):
            print(f"== {name}: tests/ 없음, 건너뜀")
            continue
        print(f"== {name}")
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
