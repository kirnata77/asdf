"""저장소 규칙 검사 (코드 동작이 아니라 파일 자체)."""

import os
import re
import subprocess

from tools import fix_eol, scenario_registry


def test_모든_텍스트파일은_LF():
    위반 = fix_eol.crlf_files()
    assert not 위반, (
        "LF 규칙 위반(.claude/rules/eol.md) - `python tools/fix_eol.py`로 고친다:\n"
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


# ------------------------------------------------------------ 기억 파일 크기

MEMORY_최대_줄 = 40
MEMORY_최대_바이트 = 6 * 1024  # 한글은 글자당 3바이트라 줄 수만으로는 크기가 안 막힌다


def test_MEMORY_md는_줄과_크기_상한을_지킨다():
    """.claude/rules/memory.md - 색인이 길어지면 매 세션 읽는 비용이 커지고 중요한 것이 묻힌다."""
    경로 = os.path.join(fix_eol.ROOT, "MEMORY.md")
    with open(경로, "rb") as f:
        내용 = f.read()
    줄수 = 내용.count(b"\n") + (0 if 내용.endswith(b"\n") or not 내용 else 1)
    assert 줄수 <= MEMORY_최대_줄, (
        f"MEMORY.md가 {줄수}줄이다(상한 {MEMORY_최대_줄}) - 규칙/수치 설명은 "
        ".memory/roadmap/game-rules.md로 옮긴다"
    )
    assert len(내용) <= MEMORY_최대_바이트, (
        f"MEMORY.md가 {len(내용)}바이트다(상한 {MEMORY_최대_바이트}) - 규칙/수치 설명은 "
        ".memory/roadmap/game-rules.md로 옮긴다"
    )


# ------------------------------------------------------------ CLAUDE.md / 규칙 파일 / 스킬

CLAUDE_최대_줄 = 100  # 매 세션 읽는다 - 길면 지시가 덜 지켜진다
규칙_최대_줄 = 80  # .claude/rules/*.md: 해당 파일을 건드릴 때만 읽힌다


def _머리말(텍스트):
    """첫 줄이 ---로 시작하는 머리말의 줄들. 없거나 닫히지 않았으면 None."""
    줄들 = 텍스트.splitlines()
    if not 줄들 or 줄들[0] != "---":
        return None
    for i, 줄 in enumerate(줄들[1:], start=1):
        if 줄 == "---":
            return 줄들[1:i]
    return None


def 규칙_파일_문제(이름, 텍스트):
    """.claude/rules/ 파일이 어기는 규칙들(없으면 빈 목록)."""
    문제 = []
    줄수 = len(텍스트.splitlines())
    if 줄수 > 규칙_최대_줄:
        문제.append(
            f"{이름}: {줄수}줄(상한 {규칙_최대_줄}) - 나누거나 절차는 스킬로 옮긴다"
        )
    머리말 = _머리말(텍스트)
    if 머리말 is None or not any(m.startswith("paths:") for m in 머리말):
        문제.append(
            f"{이름}: 머리말에 paths:가 없다 - 없으면 매 세션 읽힌다(---, paths: 목록, ---로 시작)"
        )
    return 문제


def 스킬_파일_문제(폴더이름, 텍스트):
    """.claude/skills/<폴더>/SKILL.md가 어기는 규칙들."""
    머리말 = _머리말(텍스트)
    if 머리말 is None:
        return [f"{폴더이름}: 머리말(---)이 없다"]
    값 = {}
    for 줄 in 머리말:
        if ":" in 줄 and not 줄.startswith(" "):
            키, _, 내용 = 줄.partition(":")
            값[키.strip()] = 내용.strip()
    문제 = []
    if 값.get("name") != 폴더이름:
        문제.append(f"{폴더이름}: name이 폴더 이름과 다르다({값.get('name')!r})")
    if not 값.get("description"):
        문제.append(f"{폴더이름}: description이 비었다 - 스킬은 이 글로 골라진다")
    설명 = 값.get("description", "")
    if ": " in 설명 or " #" in 설명:
        문제.append(
            f"{폴더이름}: description에 ': ' 또는 ' #'가 있어 YAML이 깨진다 - 풀어 쓰거나 따옴표로 감싼다"
        )
    return 문제


def _읽기(경로):
    with open(경로, encoding="utf-8") as f:
        return f.read()


MEMORY_최대_줄_글자 = 200  # 한 줄에 문단 하나를 통째로 넣는 빈틈을 막는다


def test_MEMORY_md는_한_줄이_200자_이하():
    """.claude/rules/memory.md - 줄 수와 바이트만 막으면 한 줄에 문단을 넣어 색인을 우회한다."""
    텍스트 = _읽기(os.path.join(fix_eol.ROOT, "MEMORY.md"))
    긴_줄 = [
        f"{번호}번째 줄 {len(줄)}자"
        for 번호, 줄 in enumerate(텍스트.splitlines(), start=1)
        if len(줄) > MEMORY_최대_줄_글자
    ]
    assert not 긴_줄, (
        f"MEMORY.md에 {MEMORY_최대_줄_글자}자를 넘는 줄이 있다: {', '.join(긴_줄)} - "
        "항목마다 짧은 한 줄만 두고 자세한 것은 .memory/로 옮긴다"
    )


def test_CLAUDE_md는_100줄_이하():
    """CLAUDE.md는 매 세션 읽힌다. 한 부분에만 해당하는 규칙은 .claude/rules/, 절차는 스킬로."""
    텍스트 = _읽기(os.path.join(fix_eol.ROOT, "CLAUDE.md"))
    줄수 = len(텍스트.splitlines())
    assert 줄수 <= CLAUDE_최대_줄, (
        f"CLAUDE.md가 {줄수}줄이다(상한 {CLAUDE_최대_줄}) - 한 부분에만 해당하는 규칙은 "
        ".claude/rules/<주제>.md(paths: 머리말)로, 절차는 .claude/skills/로 옮긴다"
    )


def test_규칙_파일은_80줄_이하이고_paths를_가진다():
    폴더 = os.path.join(fix_eol.ROOT, ".claude", "rules")
    파일들 = (
        sorted(f for f in os.listdir(폴더) if f.endswith(".md"))
        if os.path.isdir(폴더)
        else []
    )
    문제 = []
    for 이름 in 파일들:
        문제 += 규칙_파일_문제(이름, _읽기(os.path.join(폴더, 이름)))
    assert not 문제, "\n".join(문제)


def test_스킬은_이름과_설명을_가진다():
    폴더 = os.path.join(fix_eol.ROOT, ".claude", "skills")
    이름들 = sorted(os.listdir(폴더)) if os.path.isdir(폴더) else []
    문제 = []
    for 이름 in 이름들:
        경로 = os.path.join(폴더, 이름, "SKILL.md")
        if not os.path.exists(경로):
            문제.append(f"{이름}: SKILL.md가 없다")
            continue
        문제 += 스킬_파일_문제(이름, _읽기(경로))
    assert not 문제, "\n".join(문제)


def test_규칙_파일_검사는_어긋남을_잡는다():
    좋음 = '---\npaths:\n  - "game/**"\n---\n\n# 제목\n'
    assert 규칙_파일_문제("a.md", 좋음) == []
    assert "paths:가 없다" in "\n".join(규칙_파일_문제("b.md", "# 머리말 없음\n"))
    assert "paths:가 없다" in "\n".join(규칙_파일_문제("c.md", "---\nname: x\n---\n"))
    assert "paths:가 없다" in "\n".join(
        규칙_파일_문제("d.md", "---\npaths:\n  - x\n")
    )  # 안 닫힘
    긴 = 좋음 + "줄\n" * 규칙_최대_줄
    assert "줄(상한 80)" in "\n".join(규칙_파일_문제("e.md", 긴))


def test_스킬_검사는_어긋남을_잡는다():
    좋음 = "---\nname: foo\ndescription: 무엇을 언제\n---\n본문\n"
    assert 스킬_파일_문제("foo", 좋음) == []
    assert "머리말(---)이 없다" in "\n".join(스킬_파일_문제("foo", "본문\n"))
    assert "name이 폴더 이름과 다르다" in "\n".join(스킬_파일_문제("bar", 좋음))
    assert "description이 비었다" in "\n".join(
        스킬_파일_문제("foo", "---\nname: foo\ndescription:\n---\n")
    )
    깨짐 = "---\nname: foo\ndescription: 언제 쓰나: 이런 때\n---\n"
    assert "YAML이 깨진다" in "\n".join(스킬_파일_문제("foo", 깨짐))
    assert "YAML이 깨진다" in "\n".join(
        스킬_파일_문제("foo", "---\nname: foo\ndescription: 이것 # 주석\n---\n")
    )


# ------------------------------------------------------------ 풀 시나리오 장부


def test_시나리오_문서와_테스트_마커가_일치한다():
    """docs/scenarios.md 표 <-> @pytest.mark.scenario("ID") (.claude/rules/scenarios.md)."""
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


# ------------------------------------------------------------ APK 빌드 트리거


def _저장소_파일(상대경로):
    return _읽기(os.path.join(fix_eol.ROOT, 상대경로))


def test_APK_빌드는_v_태그_push로만_돈다():
    """CLAUDE.md "Git" - 큰 기능을 끝내면 사용자가 v<version> 태그를 push해 빌드한다. 다른 트리거를 되살리지 않는다."""
    워크플로 = _저장소_파일(".github/workflows/build-apk.yml")
    on = 워크플로.split("\npermissions:")[0]
    assert re.search(r"^  push:\n    tags:\n      - 'v\*'\n", on, re.M), on
    assert (
        "workflow_dispatch" not in on and "paths:" not in on and "branches:" not in on
    )
    assert "$GITHUB_REF_NAME" in 워크플로 or "github.ref_name" in 워크플로
    assert (
        "--notes-file CHANGELOG.md" in 워크플로
    )  # 릴리스 페이지에 이번 마이너의 변경 내역이 보인다


def test_APK_태그_검사가_읽는_spec_버전이_있다():
    """워크플로의 태그-버전 검사와 같은 정규식으로 buildozer.spec의 version을 읽을 수 있어야 한다."""
    워크플로 = _저장소_파일(".github/workflows/build-apk.yml")
    assert "buildozer.spec" in 워크플로 and "does not match" in 워크플로
    줄 = re.findall(r"^version *= *(\S+)\s*$", _저장소_파일("buildozer.spec"), re.M)
    assert len(줄) == 1 and re.fullmatch(r"\d+\.\d+\.\d+", 줄[0]), (
        줄
    )  # major.minor.patch


# ------------------------------------------------------------ CHANGELOG.md


def _spec_버전():
    return re.findall(r"^version *= *(\S+)\s*$", _저장소_파일("buildozer.spec"), re.M)[
        0
    ]


def _변경내역_제목들(본문):
    """`## ` 제목 줄의 이름 목록. 버전 제목은 `## 0.1.1 (날짜)` 꼴이다."""
    return [줄[3:].strip() for 줄 in 본문.splitlines() if 줄.startswith("## ")]


def _변경내역_문제(본문, 버전):
    """CHANGELOG 규칙을 어긴 곳(없으면 빈 목록). 마이너 버전을 릴리스하면 파일을 비우고 새로 시작한다."""
    제목들 = _변경내역_제목들(본문)
    문제 = []
    if not 제목들 or 제목들[0] != "미릴리스":
        문제.append("첫 제목이 `## 미릴리스`가 아니다")
    버전들 = [
        m.group(1)
        for t in 제목들[1:]
        if (m := re.match(r"(\d+\.\d+\.\d+)( \(\d{4}-\d{2}-\d{2}\))?$", t))
    ]
    if len(버전들) != len(제목들) - 1:
        문제.append("버전 제목이 `## x.y.z (YYYY-MM-DD)` 꼴이 아니다")
    if 버전 not in 버전들:
        문제.append(f"buildozer.spec 버전 {버전}의 제목이 없다")
    마이너 = ".".join(버전.split(".")[:2])
    for v in 버전들:
        if ".".join(v.split(".")[:2]) != 마이너:
            문제.append(f"{v}: 현재 마이너 {마이너}가 아니다(마이너 릴리스 때 비운다)")
    if 버전들 != sorted(
        버전들, key=lambda v: tuple(map(int, v.split("."))), reverse=True
    ):
        문제.append("버전 제목이 최신순이 아니다")
    return 문제


def test_CHANGELOG는_규칙을_지킨다():
    """.claude/rules/build-and-save.md - 이 파일이 변경 내역의 유일한 출처다(MEMORY.md는 단기 기억)."""
    문제 = _변경내역_문제(_저장소_파일("CHANGELOG.md"), _spec_버전())
    assert not 문제, "\n".join(문제)


def test_CHANGELOG_검사는_어긋남을_잡는다():
    좋음 = "# 변경 내역\n\n## 미릴리스\n- a\n\n## 0.1.2 (2026-10-11)\n- b\n\n## 0.1.1 (2026-10-10)\n- c\n"
    assert _변경내역_문제(좋음, "0.1.2") == []
    assert any(
        "미릴리스" in m for m in _변경내역_문제("## 0.1.1 (2026-10-10)\n", "0.1.1")
    )
    assert any("0.1.3" in m for m in _변경내역_문제(좋음, "0.1.3"))
    # 마이너를 올렸는데 옛 마이너 내용이 남아 있다
    남음 = "## 미릴리스\n\n## 0.2.0 (2026-11-01)\n\n## 0.1.1 (2026-10-10)\n"
    assert any("0.1.1" in m and "마이너" in m for m in _변경내역_문제(남음, "0.2.0"))
    assert any(
        "최신순" in m
        for m in _변경내역_문제("## 미릴리스\n\n## 0.1.1\n\n## 0.1.2\n", "0.1.2")
    )


# ------------------------------------------------------------ 워크플로 권한과 SDK/NDK 캐시

ANDROID_해시_명령 = "grep '^android\\.' buildozer.spec | sha256sum"


def _워크플로들():
    폴더 = os.path.join(fix_eol.ROOT, ".github", "workflows")
    return {
        n: _읽기(os.path.join(폴더, n))
        for n in sorted(os.listdir(폴더))
        if n.endswith(".yml")
    }


def test_워크플로는_권한을_비우고_checkout은_자격증명을_남기지_않는다():
    """CLAUDE.md "GitHub 워크플로" - 맨 위 `permissions: {}`와 잡별 권한, checkout마다 persist-credentials: false."""
    for 이름, 본문 in _워크플로들().items():
        assert re.search(r"^permissions: \{\}$", 본문, re.M), 이름
        assert 본문.count("uses: actions/checkout@") == 본문.count(
            "persist-credentials: false"
        ), 이름


def test_SDK_NDK_캐시_키는_android_줄만_해시한다():
    """version을 올려도(릴리스마다) 캐시가 유지되고, android.* 줄이 바뀔 때만 키가 바뀐다."""
    for 이름 in ("build-apk.yml", "warm-cache.yml"):
        본문 = _워크플로들()[이름]
        assert ANDROID_해시_명령 in 본문, 이름
        assert "hashFiles('buildozer.spec')" not in 본문, 이름
        assert "restore-keys" in 본문, 이름


def test_태그_빌드는_캐시를_불러오기만_한다():
    """태그 실행이 저장한 캐시는 다음 태그가 못 쓴다 - 저장은 main-branch의 warm-cache.yml만 한다."""
    태그 = _워크플로들()["build-apk.yml"]
    assert "actions/cache/restore@v4" in 태그
    assert "uses: actions/cache@" not in 태그 and "actions/cache/save" not in 태그


def test_캐시_채우기는_main_branch에서_spec이_바뀔_때만_돈다():
    본문 = _워크플로들()["warm-cache.yml"]
    on = 본문.split("\npermissions:")[0]
    assert re.search(
        r"^  push:\n    branches:\n      - main-branch\n    paths:\n      - buildozer\.spec\n",
        on,
        re.M,
    ), on
    assert "schedule" not in on and "tags:" not in on and "workflow_dispatch" not in on
    assert (
        "gh release" not in 본문 and "contents: write" not in 본문
    )  # 릴리스를 만들지 않는다
