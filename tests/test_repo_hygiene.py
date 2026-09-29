"""저장소 규칙 검사 (코드 동작이 아니라 파일 자체)."""

import os
import subprocess

from tools import fix_eol


def test_모든_텍스트파일은_LF():
    위반 = fix_eol.crlf_files()
    assert not 위반, (
        "LF 규칙 위반(CLAUDE.md '줄끝') - `python tools/fix_eol.py`로 고친다:\n"
        + "\n".join(위반)
    )


def test_git_훅도_검사_대상이다():
    """훅(확장자 없음)은 sh가 실행하므로 CR이 섞이면 "/bin/sh^M" 오류가 난다."""
    훅들 = [p for p in fix_eol.text_files() if os.sep + ".githooks" + os.sep in p]
    assert any(p.endswith("pre-commit") for p in 훅들)


def test_gitattributes는_LF_정규화():
    결과 = subprocess.run(
        ["git", "check-attr", "text", "eol", "--", "main.py", ".githooks/pre-commit"],
        cwd=fix_eol.ROOT,
        capture_output=True,
        text=True,
    )
    if 결과.returncode != 0:  # git이 없는 환경(zip으로 받은 경우 등)은 건너뛴다
        return
    for 줄 in (
        "main.py: text: auto",
        "main.py: eol: lf",
        ".githooks/pre-commit: eol: lf",
    ):
        assert 줄 in 결과.stdout, 결과.stdout
