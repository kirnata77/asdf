"""저장소 규칙 검사 (코드 동작이 아니라 파일 자체)."""

import os

from tools import fix_eol


def test_모든_텍스트파일은_CRLF():
    위반 = fix_eol.lf_files()
    assert not 위반, (
        "CRLF 규칙 위반(CLAUDE.md '줄끝') - `python tools/fix_eol.py`로 고친다:\n"
        + "\n".join(위반)
    )


def test_git_훅은_LF():
    훅폴더 = os.path.join(fix_eol.ROOT, ".githooks")
    for 이름 in os.listdir(훅폴더):
        with open(os.path.join(훅폴더, 이름), "rb") as f:
            assert b"\r\n" not in f.read(), f".githooks/{이름}이 CRLF - sh가 실행하지 못한다"
