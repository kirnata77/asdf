"""줄끝 규칙 검사/수정 - 저장소의 모든 텍스트 파일은 CRLF (CLAUDE.md "줄끝").

    python tools/fix_eol.py          # LF가 섞인 파일을 CRLF로 바꾼다
    python tools/fix_eol.py --check  # 바꾸지 않고 위반 파일만 출력(있으면 종료코드 1)

예외: .githooks/ 아래 파일은 sh가 실행하므로 LF여야 한다(CRLF면
"/bin/sh^M: bad interpreter"). 이 스크립트는 그 폴더를 건드리지 않고,
tests/test_repo_hygiene.py가 LF인지 따로 검사한다.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 텍스트로 취급할 확장자/파일명. 이미지(.webp 등)/폰트는 건드리지 않는다.
TEXT_EXTS = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".spec", ".txt",
             ".kv", ".cfg", ".ini", ".csv"}
TEXT_NAMES = {".gitignore", ".gitattributes", ".git-blame-ignore-revs"}

# 저장소 파일이 아닌 폴더(빌드/캐시/세이브/로컬 설정)와 LF 예외 폴더
SKIP_DIRS = {".git", ".buildozer", "bin", "__pycache__", ".pytest_cache",
             ".ruff_cache", ".claude", "venv", ".venv", ".githooks"}
SKIP_PATHS = {os.path.join("game", "saves")}


def text_files():
    for folder, dirs, files in os.walk(ROOT):
        rel = os.path.relpath(folder, ROOT)
        dirs[:] = sorted(d for d in dirs
                         if d not in SKIP_DIRS
                         and os.path.normpath(os.path.join(rel, d)) not in SKIP_PATHS)
        for name in sorted(files):
            if name in TEXT_NAMES or os.path.splitext(name)[1].lower() in TEXT_EXTS:
                yield os.path.join(folder, name)


def has_bare_lf(data):
    return data.count(b"\n") != data.count(b"\r\n")


def to_crlf(data):
    return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def lf_files():
    """CRLF가 아닌 줄이 있는 파일의 상대경로 목록."""
    bad = []
    for path in text_files():
        with open(path, "rb") as f:
            if has_bare_lf(f.read()):
                bad.append(os.path.relpath(path, ROOT))
    return bad


def main(argv):
    bad = lf_files()
    if "--check" in argv:
        for rel in bad:
            print(f"LF 섞임: {rel}")
        return 1 if bad else 0
    for rel in bad:
        path = os.path.join(ROOT, rel)
        with open(path, "rb") as f:
            data = f.read()
        with open(path, "wb") as f:
            f.write(to_crlf(data))
        print(f"CRLF로 변환: {rel}")
    print(f"{len(bad)}개 파일 변환")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
