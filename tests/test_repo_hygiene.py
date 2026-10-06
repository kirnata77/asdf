"""저장소 규칙 검사 (코드 동작이 아니라 파일 자체)."""

import os
import subprocess

from tools import fix_eol, scenario_registry


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


# ------------------------------------------------------------ 풀 시나리오 장부


def test_시나리오_문서와_테스트_마커가_일치한다():
    """docs/scenarios.md 표 <-> @pytest.mark.scenario("ID") (CLAUDE.md "풀 시나리오 테스트")."""
    문제 = scenario_registry.점검()
    assert not 문제, "\n".join(문제)


def test_시나리오_대조는_어긋남을_잡는다():
    문서 = """## 시나리오
| ID | 상태 | 기능 | 방법 | 테스트 |
|---|---|---|---|---|
| S1 | 구현 | 전투 | 귀검사 | test_a.py::test_x |
| S2 | 계획 | 성장 | 5직업 | - |
| S2 | 계획 | 중복 | 중복 | - |
| S3 | 구현 | 장비 | 방어구 | test_a.py::test_y |
| s4 | 모름 | | | - |
## 다른 절
| S9 | 구현 | 무시 | 무시 | 무시 |
"""
    표시 = {
        "test_a.py::test_x": "S1",
        "test_a.py::test_z": "S7",
        "test_a.py::test_w": "S2",
    }
    문제 = "\n".join(scenario_registry.대조(scenario_registry.문서_행(문서), 표시))
    assert "ID S2가 중복" in 문제
    assert "ID 형식 오류 's4'" in 문제
    assert "s4: 상태는" in 문제 and "s4: 기능/방법 칸이 비었다" in 문제
    assert "test_z: 문서에 없는 시나리오 ID 'S7'" in 문제
    assert "test_w: 문서에서 S2의 상태가 '구현'이 아니다" in 문제
    assert "S3: 구현인데 마커를 단 테스트가 없다" in 문제
    assert "S3: 문서의 테스트 칸" in 문제
    assert "S2: 계획인데 테스트가 있다" in 문제
    assert "S9" not in 문제 and "S1:" not in 문제


def test_시나리오_마커는_소스에서_읽는다():
    소스 = (
        "import pytest\n"
        '@pytest.mark.scenario("S1")\n'
        "def test_a(): pass\n"
        '@pytest.mark.parametrize("x", [1])\n'
        "def test_b(x): pass\n"
    )
    assert scenario_registry.테스트_표시(소스, "t.py") == {"t.py::test_a": "S1"}
