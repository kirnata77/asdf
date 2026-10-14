"""전투 로그 항목의 "종류" 칸과 화면 문장(gameflow.로그_문장들)을 지킨다 (품질 계획 P4, Q-2).

- 문장 기준: 골든 파일에 든 전투 로그 항목 전부를 로그_문장들로 바꾼 결과를 골든
  `battle_log_sentences`에 고정한다. 로그 항목의 모양이 바뀌어도(칸 추가) 화면 문장은 그대로여야 한다.
- 종류 규칙: 엔진이 쌓는 dict 항목은 전부 로그_문장들이 아는 "종류"를 갖는다(conftest의
  `전투_로그_종류_검사`가 모든 테스트에서 core.로그를 지켜보고, 여기서는 골든에 든 항목을 본다).
"""

import glob
import json
import os

import gameflow as gf
from game.system.combat import core

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "golden")
문장_골든 = "battle_log_sentences"


def _골든_로그들():
    """골든 파일마다 그 안의 "로그" 목록에 든 항목들(파일 순서, 항목 순서 그대로)."""
    모음 = {}
    for 경로 in sorted(glob.glob(os.path.join(GOLDEN_DIR, "*.json"))):
        이름 = os.path.splitext(os.path.basename(경로))[0]
        if 이름 == 문장_골든:
            continue
        with open(경로, encoding="utf-8") as f:
            값 = json.load(f)
        항목들 = []

        def 훑기(x):
            if isinstance(x, dict):
                for 키 in sorted(x):
                    if 키 == "로그" and isinstance(x[키], list):
                        # 로그 항목 안의 "로그"(효과 문장 목록)까지는 내려가지 않는다
                        항목들.extend(x[키])
                    else:
                        훑기(x[키])
            elif isinstance(x, list):
                for 원소 in x:
                    훑기(원소)

        훑기(값)
        if 항목들:
            모음[이름] = 항목들
    return 모음


def test_골든_로그의_화면_문장이_기준과_같다(golden):
    문장들 = {
        이름: [gf.로그_문장들(항목) for 항목 in 항목들]
        for 이름, 항목들 in _골든_로그들().items()
    }
    assert sum(len(v) for v in 문장들.values()) > 1000  # 골든에서 로그를 실제로 찾았나
    golden(문장_골든, 문장들)


def test_골든_로그의_dict_항목은_전부_아는_종류를_갖는다():
    모름 = [
        (이름, 항목)
        for 이름, 항목들 in _골든_로그들().items()
        for 항목 in 항목들
        if isinstance(항목, dict) and 항목.get("종류") not in gf.로그_종류_목록
    ]
    assert not 모름[:5], f"종류 없는/모르는 로그 항목 {len(모름)}개"


def test_문장_처리표는_엔진의_로그_종류를_빠짐없이_안다():
    assert set(gf.로그_종류_목록) == set(core.로그_종류)


def test_거대화로_쉬는_차례는_은는을_맞춰_쉬고있다로_보인다():
    """사용자 지정 2026-10-14 - 받침에 맞춰 "은/는"을 붙인다."""
    import random

    from game.system.combat import flow, monster_actions
    from tests import support

    random.seed(3)
    상태 = support.새게임([("", "귀검사")])
    gf.전투_시작(상태, ["타우 비스트"], 레벨=2, 차수=1)
    support.반응_처리(상태)
    전투상태 = 상태["전투상태"]
    비스트 = next(p for p in 전투상태["참가자"] if p["진영"] == "적")
    flow.턴_시작_처리(전투상태, 비스트)
    monster_actions.몬스터_턴_실행(전투상태, 비스트)  # 첫 차례는 쉰다
    assert gf.로그_문장들(전투상태["로그"][-1]) == ["타우 비스트는 쉬고있다."]
    # 받침이 있는 이름은 "은"
    assert gf.로그_문장들(전투상태["로그"][-1] | {"공격자": "타우 비스트 B"}) == [
        "타우 비스트 B는 쉬고있다."
    ]
    assert gf.로그_문장들(전투상태["로그"][-1] | {"공격자": "거대 루가루 L"}) == [
        "거대 루가루 L은 쉬고있다."
    ]
