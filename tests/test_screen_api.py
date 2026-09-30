"""화면용 gameflow 창구 테스트 + 계층 규칙(화면은 game.system을 직접 쓰지 않는다).

화면(kivy) 자체는 CI에서 돌지 않는다. 대신 화면이 부르는 gameflow 함수를 여기서
검사하고, 화면 소스가 game.system을 직접 import하거나 gameflow.xxx_system으로
우회하지 않는지 정적으로 검사한다. 화면 실행 확인은 tools/ui_smoke.py(kivy+Xvfb).
"""

import os
import random
import re

import pytest

import gameflow as gf
from game.system.combat import flow
from game.system import skill_system as ss
from tests import support

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_화면은_game_system을_직접_쓰지_않는다():
    위반 = []
    for 폴더 in ("game/screens",):
        for 파일 in sorted(os.listdir(os.path.join(ROOT, 폴더))):
            if not 파일.endswith(".py"):
                continue
            경로 = os.path.join(ROOT, 폴더, 파일)
            for 줄번호, 줄 in enumerate(open(경로, encoding="utf-8"), 1):
                if re.search(
                    r"(from|import)\s+game\.system|gameflow\.\w+_system\b", 줄
                ):
                    위반.append(f"{폴더}/{파일}:{줄번호}: {줄.strip()}")
    for 줄번호, 줄 in enumerate(
        open(os.path.join(ROOT, "main.py"), encoding="utf-8"), 1
    ):
        if re.search(r"(from|import)\s+game\.system", 줄):
            위반.append(f"main.py:{줄번호}: {줄.strip()}")
    assert not 위반, "화면 -> gameflow -> system 계층 위반:\n" + "\n".join(위반)


def _전투(
    구성=(("", "귀검사"), ("", "거너"), ("", "마법사"), ("", "프리스트")), 레벨=10
):
    random.seed(3)
    상태 = support.새게임(list(구성))
    전직 = {
        "귀검사": "웨펀마스터",
        "거너": "레인저",
        "마법사": "엘리멘탈마스터",
        "프리스트": "크루세이더",
    }
    for c in 상태["파티"]["파티원"]:
        support.성장(상태, c, 레벨, 전직=전직[c["직업"]] if 레벨 >= 6 else None)
    gf.파티_최대치로_회복(상태)
    gf._전투_시작(상태, ["타우 아미", "고블린", "고블린"], 레벨=6, 차수=2)
    support.반응_처리(상태)
    return 상태


def _차례(상태, 이름):
    전투상태 = 상태["전투상태"]
    p = next(x for x in 전투상태["참가자"] if x["이름"] == 이름)
    전투상태["현재턴"] = 전투상태["참가자"].index(p)
    flow._턴_시작_처리(전투상태, p)
    return p


def test_상점_창구():
    assert gf.상점_대분류목록 == ["장비", "소모품", "재료"]
    assert gf.상점_최대구매수량 == 99
    assert gf.상점_판매가({"가격": 50}) == 10


def test_약점스탯_투자가능():
    c = support.새게임([("", "귀검사")])["파티"]["파티원"][0]
    assert gf.약점스탯_투자가능(c, "근력") and not gf.약점스탯_투자가능(c, "지능")


def test_스킬_사용가능과_휴식횟수():
    상태 = _전투()
    프리스트 = _차례(상태, "프리스트")
    assert gf.스킬_사용_가능여부(상태, 프리스트, "치유의 기도") == (True, None)
    최대 = gf.스킬_휴식_남은횟수(상태, 프리스트, "치유의 기도")[1]
    assert gf.스킬_휴식_남은횟수(상태, 프리스트, "치유의 기도") == (최대, 최대)
    assert gf.스킬_휴식_남은횟수(상태, 프리스트, "홀리 스매쉬") is None
    프리스트["현재MP"] = 0
    가능, 사유 = gf.스킬_사용_가능여부(상태, 프리스트, "치유의 기도")
    assert not 가능 and "MP" in 사유


def test_스킬_실제_타겟():
    상태 = _전투()
    거너 = _차례(상태, "거너")
    모음 = 상태["스킬데이터모음"]
    assert gf.스킬_실제_타겟(상태, 모음["헤드샷"]) == 모음["헤드샷"]["타겟"]
    assert gf.스킬_실제_타겟(상태, 모음["은탄"]) == "자신"
    거너["원본"]["보유특성"].append("장탄공급")  # 조건부효과 타겟 오버라이드
    assert gf.스킬_실제_타겟(상태, 모음["은탄"]) == "아군단일"
    _차례(상태, "마법사")
    assert gf.스킬_실제_타겟(상태, 모음["보이드"]) == 모음["보이드"]["지속공격"]["타겟"]
    분할 = next(d for d in 모음.values() if "공격단계1" in d and not d.get("타겟"))
    assert gf.스킬_실제_타겟(상태, 분할) == 분할["공격단계1"]["타겟"]


def test_현재참가자_수치와_지정불가():
    상태 = _전투()
    마법사 = _차례(상태, "마법사")
    공격횟수 = 상태["스킬데이터모음"]["썬더콜링"]["공격횟수"]
    assert gf.현재참가자_수치(상태, 공격횟수) == ss._정수_평가(
        공격횟수, 상태["전투상태"], 마법사
    )
    assert (
        gf.현재참가자_수치(상태, None) == 1
        and gf.현재참가자_수치(상태, None, 기본값=0) == 0
    )
    assert gf.현재참가자_수치(상태, "2+차수") == 4  # 레벨 10 = 2차수
    적 = next(x for x in 상태["전투상태"]["참가자"] if x["진영"] == "적")
    assert gf.지정불가_상태인가(상태, 적) is False
    ss._상태이상_부여(상태["전투상태"], 적, "은신", 2, None)
    assert gf.지정불가_상태인가(상태, 적) is True


def test_몬스터_크기_분류와_표시_배율():
    크기 = {n: d.get("크기") for n, d in gf.몬스터목록.items()}
    for n, d in gf.몬스터목록.items():
        기대 = {"고블린": "소형", "루가루": "소형", "좀비": "중형", "인간": "중형"}.get(
            d["분류"]
        )
        if d["분류"] == "타우":
            기대 = "대형" if n in ("타우 비스트", "타우킹 샤우타") else "중형"
        assert 크기[n] == 기대, (n, d["분류"], 크기[n])
    p = lambda 원본, 이름="x": {"이름": 이름, "원본": 원본}  # noqa: E731
    assert [gf.적_표시_배율(p({"크기": k})) for k in ("소형", "중형", "대형")] == [
        0.75,
        1.0,
        1.25,
    ]
    assert gf.적_표시_배율(p({})) == 1.0  # 없으면 중형
    with pytest.raises(ValueError, match="크기"):
        gf.적_표시_배율(p({"크기": "거대"}))


def test_적_그리기_순서는_대형이_뒤_같은_크기는_왼쪽이_앞():
    적 = [
        {"이름": n, "원본": {"크기": k}}
        for n, k in (
            ("A", "소형"),
            ("B", "대형"),
            ("C", "중형"),
            ("D", "소형"),
            ("E", "대형"),
        )
    ]
    순서 = [p["이름"] for _, p in gf.적_그리기_순서(적)]
    # 먼저 그린 것이 뒤: 대형(오른쪽부터) -> 중형 -> 소형(오른쪽부터) - 왼쪽이 마지막(앞)
    assert 순서 == ["E", "B", "C", "D", "A"]
    assert [i for i, _ in gf.적_그리기_순서(적)] == [4, 1, 2, 3, 0]
