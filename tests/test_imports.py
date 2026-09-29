"""kivy가 필요 없는 모든 모듈이 import되는지 검사한다(데이터 파일 문법/이름 오류 조기 발견)."""

import importlib
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 알려진 문제 - .memory/active-issues/known-bugs.md. 고치면 strict xfail이
# XPASS로 실패하므로 그때 이 목록에서 지운다.
알려진_깨진모듈 = {
    "game.system.quest_system": "파일 내용이 'test' 한 단어뿐이라 NameError",
}


def _헤드리스_모듈목록():
    모듈들 = ["gameflow"]
    for 하위 in ("game/system", "game/data"):
        for 폴더, _, 파일들 in os.walk(os.path.join(ROOT, 하위)):
            for 파일 in sorted(파일들):
                if 파일.endswith(".py") and 파일 != "__init__.py":
                    상대 = os.path.relpath(os.path.join(폴더, 파일), ROOT)
                    모듈들.append(상대[:-3].replace(os.sep, "."))
    return sorted(모듈들)


def _파라미터():
    파라미터들 = []
    for 모듈명 in _헤드리스_모듈목록():
        이유 = 알려진_깨진모듈.get(모듈명)
        표시 = [pytest.mark.xfail(reason=이유, strict=True)] if 이유 else []
        파라미터들.append(pytest.param(모듈명, marks=표시, id=모듈명))
    return 파라미터들


@pytest.mark.parametrize("모듈명", _파라미터())
def test_모듈_import(모듈명):
    importlib.import_module(모듈명)


def test_헤드리스_계층은_kivy에_의존하지_않는다():
    import sys

    for 모듈명 in _헤드리스_모듈목록():
        if 모듈명 not in 알려진_깨진모듈:
            importlib.import_module(모듈명)
    assert not any(m == "kivy" or m.startswith("kivy.") for m in sys.modules)


def test_file_path_레지스트리가_실제_파일과_일치():
    """game/data/file_path.py는 사람이 손으로 채우는 경로표다. 파일을 추가/이동/
    이름변경(리팩터링)하면 여기도 같이 고쳐야 한다 - 빠뜨리면 이 테스트가 잡는다."""
    from game.data.file_path import 파일경로

    실제 = {}
    for 폴더, _, 파일들 in os.walk(os.path.join(ROOT, "game")):
        for 파일 in 파일들:
            if 파일.endswith(".py") and 파일 != "__init__.py":
                상대 = os.path.relpath(os.path.join(폴더, 파일), ROOT)
                실제[파일[:-3]] = 상대[:-3].replace(os.sep, ".")
    assert 파일경로 == 실제
