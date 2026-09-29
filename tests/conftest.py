"""공용 픽스처.

tests/는 kivy 없이 돈다 - gameflow.py 이하(game/system, game/data)는 kivy를
import하지 않기 때문이다. game/screens/와 main.py는 여기서 다루지 않는다.
"""

import json
import os

import pytest

from game.system import save_system

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")


@pytest.fixture(autouse=True)
def 임시_세이브폴더(tmp_path, monkeypatch):
    """테스트가 실제 game/saves/를 건드리지 않게 세이브 폴더를 바꿔치기한다."""
    monkeypatch.setattr(save_system, "_세이브_폴더", lambda: str(tmp_path))
    return tmp_path


def _정규화(값):
    """JSON 왕복으로 튜플/키 타입 차이를 없앤다(골든 파일과 비교할 모양)."""
    return json.loads(json.dumps(값, ensure_ascii=False, default=str))


@pytest.fixture
def golden():
    """golden(이름, 실제값): tests/golden/<이름>.json과 비교한다.

    동작을 일부러 바꿨다면 UPDATE_GOLDEN=1 로 실행해 골든 파일을 다시 쓰고,
    그 diff를 커밋에서 설명한다. 리팩터링(동작 불변)이라면 골든이 바뀌면 안 된다.
    """

    def _비교(이름, 실제값):
        경로 = os.path.join(GOLDEN_DIR, f"{이름}.json")
        실제값 = _정규화(실제값)
        if os.environ.get("UPDATE_GOLDEN") == "1" or not os.path.exists(경로):
            with open(경로, "w", encoding="utf-8", newline="\r\n") as f:  # CRLF 규칙
                json.dump(실제값, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.write("\n")
            if os.environ.get("UPDATE_GOLDEN") != "1":
                pytest.fail(f"골든 파일이 없어 새로 만들었다: {경로} - 내용을 확인하고 커밋할 것")
            return
        with open(경로, encoding="utf-8") as f:
            기대값 = json.load(f)
        assert 실제값 == 기대값, f"{이름}: 골든과 다르다 (의도한 변경이면 UPDATE_GOLDEN=1)"

    return _비교
