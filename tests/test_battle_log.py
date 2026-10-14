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
