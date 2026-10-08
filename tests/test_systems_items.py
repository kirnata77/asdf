"""상점/장비/세이브/레벨업 시스템 단위 테스트."""

import json
import random

import pytest

import gameflow as gf
from game.data.equipment.eq_02_armor_set import 방어구세트목록
from game.data.monster.monster_drop import 드랍표_모음
from game.system import (
    character_data_system as 데이터,
    dice_utils,
    character_levelup_system as 레벨업,
    equipment_system as 장비,
    loot_system as 전리품,
    player_system,
    potion_system as 포션시스템,
    save_system,
    shop_system as 상점,
)


@pytest.fixture
def 카탈로그():
    return gf._상점_카탈로그_생성()


def _플레이어(골드=0, 파티원=None):
    p = player_system.빈_플레이어()
    p["소지품"]["골드"] = 골드
    p["파티"]["파티원"] = 파티원 or []
    return p


# ------------------------------------------------------------------- shop


def test_카탈로그_구조(카탈로그):
    assert list(카탈로그) == 상점.대분류_목록
    assert list(카탈로그["장비"]) == 상점.장비_탭순서
    assert list(카탈로그["소모품"]) == 상점.소모품_탭순서
    assert {탭: len(v) for 탭, v in 카탈로그["재료"].items()} == {
        "큐브 조각": 6,
        "큐브": 6,
        "소울": 6,
        "잡템": 1,
    }
    assert {탭: len(v) for 탭, v in 카탈로그["장비"].items()} == {
        "무기": 51,
        "상의": 10,
        "하의": 10,
        "어깨": 5,
        "벨트": 5,
        "신발": 10,
        "목걸이": 3,
        "반지": 3,
        "팔찌": 3,
        "보조장비": 1,
        "마법석": 2,
        "귀걸이": 1,
    }
    assert {탭: len(v) for 탭, v in 카탈로그["소모품"].items()} == {
        "포션": 9,
        "투척 아이템": 2,
        "음식": 28,
    }
    assert 상점.탭_목록("장비") == 상점.장비_탭순서 and 상점.탭_목록("재료") == []
    assert 상점.탭_목록("소모품") is not 상점.소모품_탭순서  # 사본을 준다


def test_구매목록_가격0과_판매목록필터(카탈로그):
    전체 = [i["이름"] for i in 상점.구매목록(카탈로그, "장비", "무기")]
    assert "치트용 소검" not in 전체 and "녹슨 소검" in 전체  # 가격 0은 기본 제외
    엘븐 = gf.마을파일_레지스트리["town_01A_T01_Elvengard"]["상점판매목록"]
    마을 = [i["이름"] for i in 상점.구매목록(카탈로그, "장비", "무기", 엘븐)]
    assert "치트용 소검" in 마을  # 판매목록에 있으면 가격 0도 판다
    assert "강철 소검" not in 마을 and set(마을) <= set(엘븐)
    assert 상점.구매목록(카탈로그, "없는분류", "탭") == []


def test_구매_성공과_오류(카탈로그):
    p = _플레이어(골드=35)
    assert 상점.구매_처리(p, 카탈로그, "소모품", "포션", "초보자용 HP 포션", 3) == 30
    assert p["소지품"]["골드"] == 5 and p["소지품"]["포션"] == {"초보자용 HP 포션": 3}
    assert 상점.구매_처리(p, 카탈로그, "소모품", "투척 아이템", "돌맹이", 5) == 5
    assert p["소지품"]["소모품"] == {"돌맹이": 5} and 상점.보유_골드(p) == 0
    for 수량, 메시지 in [
        (0, "1 이상"),
        (1.5, "1 이상"),
        (100, "99개"),
        (1, "골드가 부족"),
    ]:
        with pytest.raises(ValueError, match=메시지):
            상점.구매_처리(p, 카탈로그, "소모품", "포션", "초보자용 HP 포션", 수량)
    with pytest.raises(ValueError, match="팔지 않는다"):
        상점.구매_처리(p, 카탈로그, "장비", "무기", "강철 소검", 1, ["녹슨 소검"])
    assert 상점.보유_골드({}) == 0  # 소지품이 없으면 만들어서 0


def test_재료는_재료칸에_들어가고_팔수만_있다(카탈로그):
    from game.controller import ctl_rewards

    assert (
        ctl_rewards._아이템_소지품_카테고리({"상점카탈로그": 카탈로그}, "고블린의 팬티")
        == "재료"
    )
    assert 상점.소지품_카테고리("재료", "소울") == "재료"
    assert 상점.구매목록(카탈로그, "재료", "잡템") == []  # 상점은 재료를 팔지 않는다
    assert 상점.구매목록(카탈로그, "재료", "잡템", ["고블린의 팬티"]) == []
    p = _플레이어()
    p["소지품"]["재료"] = {"고블린의 팬티": 3, "레어 소울": 1}
    assert [(i["이름"], n) for i, n in 상점.판매목록(p, 카탈로그, "재료", "잡템")] == [
        ("고블린의 팬티", 3)
    ]
    상점.판매_처리(p, 카탈로그, "재료", "잡템", "고블린의 팬티", 2)
    assert p["소지품"]["골드"] == 2 and p["소지품"]["재료"]["고블린의 팬티"] == 1
    상점.판매_처리(p, 카탈로그, "재료", "소울", "레어 소울", 1)
    assert p["소지품"]["골드"] == 7  # 25 * 20% = 5


def test_판매_장착중은_못판다(카탈로그):
    c = 데이터.빈_캐릭터()
    c["장착장비"]["무기"] = "녹슨 소검"
    p = _플레이어(파티원=[c])
    p["소지품"]["장비"] = {"녹슨 소검": 2, "없는아이템": 1}
    assert [(i["이름"], n) for i, n in 상점.판매목록(p, 카탈로그, "장비", "무기")] == [
        ("녹슨 소검", 1)
    ]
    assert 상점.장착중_개수(p, "녹슨 소검") == 1
    with pytest.raises(ValueError, match="1개까지"):
        상점.판매_처리(p, 카탈로그, "장비", "무기", "녹슨 소검", 2)
    assert 상점.판매_처리(p, 카탈로그, "장비", "무기", "녹슨 소검", 1) == 50 // 5
    assert p["소지품"]["장비"]["녹슨 소검"] == 1 and p["소지품"]["골드"] == 10
    with pytest.raises(ValueError, match="팔 수 없다"):
        상점.판매_처리(p, 카탈로그, "장비", "무기", "녹슨 소검", 1)  # 남은 건 장착중
    with pytest.raises(ValueError, match="1 이상"):
        상점.판매_처리(p, 카탈로그, "장비", "무기", "녹슨 소검", 0)
    p["소지품"]["포션"] = {"초보자용 HP 포션": 1}
    상점.판매_처리(p, 카탈로그, "소모품", "포션", "초보자용 HP 포션", 1)
    assert "초보자용 HP 포션" not in p["소지품"]["포션"]  # 0개가 되면 항목 삭제
    assert 상점.판매가({"가격": 9}) == 2 and 상점.판매가({}) == 0
    assert 상점.판매가({"가격": 1}) == 1 and 상점.판매가({"가격": 10}) == 2
    assert 상점.소지품_카테고리("소모품", "음식") == "소모품"


# -------------------------------------------------------------- equipment


def _캐릭터(**덮어쓰기):
    c = 데이터.빈_캐릭터()
    c.update(덮어쓰기)
    return c


def test_장착_가능여부_분기(카탈로그):
    c = _캐릭터(가용무기=["소검"])
    무기, 경갑, 중갑 = (
        카탈로그["장비"]["무기"]["녹슨 소검"],
        카탈로그["장비"]["상의"]["허름한 경갑 상의"],
        카탈로그["장비"]["상의"]["녹슨 중갑 상의"],
    )
    assert 장비.장착_가능여부(c, "무기", 무기) == (True, None)
    assert 장비.장착_가능여부(c, "상의", 경갑) == (True, None)
    assert not 장비.장착_가능여부(c, "날개", 무기)[0]
    assert "맞지 않는다" in 장비.장착_가능여부(c, "하의", 경갑)[1]
    assert 장비.장착_가능여부(c, "상의", 중갑) == (True, None)  # 방어구 제한 없음
    assert (
        "무기는 아직"
        in 장비.장착_가능여부(c, "무기", 카탈로그["장비"]["무기"]["이빠진 카타나"])[1]
    )
    assert 장비.장착_가능여부(c, "목걸이", 카탈로그["장비"]["목걸이"]["조잡한 목걸이"])[
        0
    ]
    장비.장비_장착(c, "상의", 경갑)
    with pytest.raises(ValueError):
        장비.장비_장착(c, "무기", 카탈로그["장비"]["무기"]["이빠진 카타나"])
    장비.장비_해제(c, "상의")
    assert c["장착장비"]["상의"] is None
    with pytest.raises(ValueError, match="존재하지 않는 슬롯"):
        장비.장비_해제(c, "날개")


def test_실데이터_세트는_같은_재질_5부위에서_발동(카탈로그):
    """eq_02_armor_set.py 머리말: "재질 5부위를 전부 갖추면 발동" - 세트 정의엔 "구성품"이 없고
    "타입"(재질)만 있다. 이름(마리아의 천 등)과 무관하게 재질만 본다."""
    assert all("구성품" not in 정의 for 정의 in 방어구세트목록.values())
    탭 = 카탈로그["장비"]

    def 첫(슬롯, 재질):
        return next(i for i in 탭[슬롯].values() if i["재질"] == 재질)

    for 세트명, 정의 in 방어구세트목록.items():
        전부 = {슬롯: 첫(슬롯, 정의["타입"]) for 슬롯 in 장비.방어구_슬롯}
        assert [s["세트명"] for s in 장비.세트효과_목록(전부, 방어구세트목록)] == [
            세트명
        ]
        assert (
            장비.장비_보너스_합산(전부, 방어구세트목록)["AC보너스"]
            == sum(i["AC보너스"] for i in 전부.values()) + 1
        )
        네부위 = dict(전부, 벨트=None)
        assert 장비.세트효과_목록(네부위, 방어구세트목록) == []
    섞임 = {슬롯: 첫(슬롯, "경갑") for 슬롯 in 장비.방어구_슬롯}
    섞임["신발"] = 첫("신발", "천갑")
    assert 장비.세트효과_목록(섞임, 방어구세트목록) == []
    마리아 = {
        슬롯: 탭[슬롯][f"마리아의 천 {슬롯}"] for 슬롯 in ("상의", "하의", "신발")
    }
    assert 장비.세트효과_목록(마리아, 방어구세트목록) == []  # 3부위만으로는 안 된다


def test_세트_보너스_합산_합성데이터():
    세트 = {
        "s": {
            "세트명": "s",
            "구성품": ["a", "b"],
            "효과": {"AC보너스": 2, "스탯보너스": {"민첩": 2}},
        },
        "빈": {"구성품": []},
    }
    장착 = {
        "상의": {"이름": "a", "AC보너스": 1, "스탯보너스": {"근력": 1, "힘": "x"}},
        "하의": {"이름": "b", "속도보너스": 1, "데미지보너스": "1d4"},
        "신발": None,
    }
    assert [s["세트명"] for s in 장비.세트효과_목록(장착, 세트)] == ["s"]
    assert 장비.세트효과_목록(장착, None) == []
    합 = 장비.장비_보너스_합산(장착, 세트)
    assert (합["AC보너스"], 합["속도보너스"], 합["데미지보너스"]) == (3, 1, 0)
    assert (
        합["스탯보너스"]["근력"] == 1
        and 합["스탯보너스"]["민첩"] == 2
        and "힘" not in 합["스탯보너스"]
    )


def test_민첩상한과_AC():
    c = _캐릭터(민첩=18)  # 보정치 +4
    장착 = {
        "상의": {"재질": "경갑", "민첩상한": 2, "AC보너스": 1},
        "하의": {"재질": "천갑", "민첩상한": None},
    }
    assert 장비.민첩상한_계산(c, 장착) == 2
    assert 장비.최종AC_계산(c, 장착) == 10 + 1 + 2
    assert 장비.최종AC_계산(c, 장착, 추가민첩=-8) == 10 + 1 + 0  # 상한 아래면 그대로
    c["민첩상한해제"].append("경갑")  # 경갑숙련 - 5부위가 모두 경갑일 때만 발동
    c["보유특성"].append("경갑숙련")
    assert 장비.민첩상한_계산(c, 장착) == 2
    전부경갑 = {슬롯: {"재질": "경갑", "민첩상한": 2} for 슬롯 in 장비.방어구_슬롯}
    assert 장비.민첩상한_계산(c, 전부경갑) is None
    assert (
        장비.민첩상한_계산(c, {"상의": {"재질": "중갑", "민첩상한": 0}, "a": None}) == 0
    )


def test_장비반영_능력치_HP_MP():
    c = _캐릭터(
        건강=12, 지능=13, 기본최대HP=20, 기본최대MP=50, 레벨=3, 주문시전능력치="지능"
    )
    장착 = {"목걸이": {"스탯보너스": {"건강": 2, "지능": 1}}}
    assert 장비.장비반영_능력치(c, 장착)["건강"] == 14
    assert 장비.장비반영_최대HP(c, 장착) == 20  # 레벨당체력증가가 없으면 건강 미반영
    c["레벨당체력증가"] = 6
    # 건강보정치 1 -> 2: 공식(3,6,2)=8+12, 공식(3,6,1)=7+올림(10.5)=18 -> +2
    assert 장비.장비반영_최대HP(c, 장착) == 20 + 2
    # 지능 13->14: 보정치 +1 -> +2, 레벨 3이라 (3-1)배
    assert 장비.장비반영_최대MP(c, 장착) == 50 + (2 - 1) * 2
    장착["목걸이"]["스탯보너스"]["지능"] = 3
    assert 장비.장비반영_최대MP(c, 장착) == 54  # 13->16: +1 -> +3
    c["주문시전능력치"] = None  # 미지정 -> 지능
    assert 장비.장비반영_최대MP(c, 장착) == 54
    assert (
        장비.장비반영_최대HP(
            _캐릭터(기본최대HP=0, 건강=10), {"a": {"스탯보너스": {"건강": -10}}}
        )
        == 1
    )


def test_소지품_동기화와_교체(카탈로그):
    a, b = _캐릭터(가용무기=["소검"]), _캐릭터(가용무기=["소검"])
    a["장착장비"]["무기"] = b["장착장비"]["무기"] = "녹슨 소검"
    p = _플레이어(파티원=[a, b])
    p["소지품"]["장비"] = {"녹슨 소검": 1}
    장비.장착품_소지품_동기화(p)
    assert p["소지품"]["장비"]["녹슨 소검"] == 2  # 장착 수만큼 보충
    장비.장착품_소지품_동기화(p)
    assert p["소지품"]["장비"]["녹슨 소검"] == 2  # 다시 불러도 그대로
    무기탭 = 카탈로그["장비"]["무기"]
    p["소지품"]["장비"].update({"강철 소검": 1, "이빠진 카타나": 1, "없는칼": 1})
    후보 = {
        i["이름"]: (n, ok) for i, n, ok, _ in 장비.교체_후보목록(p, a, "무기", 무기탭)
    }
    assert 후보 == {"강철 소검": (1, True), "이빠진 카타나": (1, False)}
    장비.장비_교체(p, a, "무기", 무기탭["강철 소검"])
    assert a["장착장비"]["무기"] == "강철 소검"
    with pytest.raises(ValueError, match="남은 것이 없다"):
        장비.장비_교체(p, b, "무기", 무기탭["강철 소검"])


# ------------------------------------------------------------------- save


def _핵심캐릭터(이름, **추가):
    """세이브 불러오기 검사(state_schema.캐릭터_핵심)를 통과하는 최소 캐릭터."""
    return {
        "캐릭터명": 이름,
        "직업": "귀검사",
        "레벨": 1,
        "현재HP": 10,
        "현재MP": 5,
        **추가,
    }


def test_세이브_구버전_형식과_요약(임시_세이브폴더):
    구버전 = {
        "파티": {"파티원": [_핵심캐릭터("철수")], "골드": 77},
        "진행도": {"현재마을": "엘븐가드", "클리어한오브젝트": [["d", [1, 2]]]},
    }
    (임시_세이브폴더 / "slot_2.json").write_text(
        json.dumps(구버전, ensure_ascii=False), encoding="utf-8"
    )
    플레이어, 진행도 = save_system.게임_불러오기(2)
    assert 플레이어["소지품"]["골드"] == 77 and 플레이어["선택된초상화"] == "001m"
    assert 진행도["클리어한던전"] == set() and 진행도["클리어한오브젝트"] == {
        ("d", (1, 2))
    }
    assert save_system.세이브_요약(2) == {
        "슬롯번호": 2,
        "저장시각": None,
        "현재마을": "엘븐가드",
        "대표캐릭터명": "철수",
        "파티인원수": 1,
    }
    요약 = save_system.전체_세이브_요약()
    assert [s.get("비어있음", False) for s in 요약] == [True, False, True]
    with pytest.raises(FileNotFoundError):
        save_system.게임_불러오기(1)
    save_system.세이브_삭제(1)  # 없는 슬롯 삭제는 조용히 넘어간다
    assert save_system.세이브_요약(3) is None


def test_세이브_map_던전파일명은_dungeon으로_바꿔_불러온다(임시_세이브폴더):
    구버전 = {
        "플레이어": player_system.빈_플레이어(),
        "진행도": {
            "클리어한던전": ["map_01A_D01_Lorien"],
            "클리어한오브젝트": [["map_01A_D02_Hollow_Lorien", [15, 3]]],
        },
    }
    (임시_세이브폴더 / "slot_1.json").write_text(
        json.dumps(구버전, ensure_ascii=False), encoding="utf-8"
    )
    _, 진행도 = save_system.게임_불러오기(1)
    assert 진행도["클리어한던전"] == {"dungeon_01A_D01_Lorien"}
    assert 진행도["클리어한오브젝트"] == {("dungeon_01A_D02_Hollow_Lorien", (15, 3))}


def test_세이브_신버전_기본값_채움(임시_세이브폴더):
    (임시_세이브폴더 / "slot_1.json").write_text(
        json.dumps(
            {"플레이어": {"파티": {"파티원": []}}, "진행도": {"클리어한던전": ["a"]}}
        ),
        encoding="utf-8",
    )
    플레이어, 진행도 = save_system.게임_불러오기(1)
    assert 플레이어["레벨"] == 1 and 플레이어["선택된초상화"] == "001m"
    assert 플레이어["소지품"] == player_system.빈_소지품()
    assert 진행도["클리어한던전"] == {"a"}
    assert save_system.세이브_요약(1)["대표캐릭터명"] == "-"


def test_세이브_폴더는_game_saves(monkeypatch):
    monkeypatch.undo()  # 자동 픽스처의 바꿔치기를 풀고 실제 경로 계산만 확인
    assert save_system._세이브_폴더().replace("\\", "/").endswith("game/saves")


# 세이브 안정화(N1a) - 원자적 쓰기, 백업(.bak), 손상 슬롯. 구조 점검 W-1.


def _저장(슬롯번호, 마을="엘븐가드", 이름="철수"):
    플레이어 = player_system.빈_플레이어()
    플레이어["파티"]["파티원"] = [_핵심캐릭터(이름)]
    save_system.게임_저장(슬롯번호, 플레이어, {"현재마을": 마을})


def test_세이브_원자적_쓰기는_임시파일을_남기지_않고_이전_세이브를_백업한다(
    임시_세이브폴더,
):
    _저장(1, 마을="엘븐가드")
    assert not (
        임시_세이브폴더 / "slot_1.json.bak"
    ).exists()  # 처음엔 백업할 이전 세이브가 없다
    첫내용 = (임시_세이브폴더 / "slot_1.json").read_text(encoding="utf-8")

    _저장(1, 마을="헨돈마이어")
    assert sorted(p.name for p in 임시_세이브폴더.iterdir()) == [
        "slot_1.json",
        "slot_1.json.bak",
    ]  # .tmp 같은 찌꺼기가 없다
    assert (임시_세이브폴더 / "slot_1.json.bak").read_text(encoding="utf-8") == 첫내용
    assert save_system.세이브_요약(1)["현재마을"] == "헨돈마이어"


def test_세이브_저장이_중간에_실패하면_이전_세이브가_그대로다(
    임시_세이브폴더, monkeypatch
):
    _저장(1, 마을="엘븐가드")
    이전 = (임시_세이브폴더 / "slot_1.json").read_text(encoding="utf-8")

    def 실패(*args, **kwargs):
        raise OSError("디스크가 가득 찼다")

    # 임시 파일에 쓴 뒤 바꿔치기 직전(fsync)에 실패하는 경우
    with monkeypatch.context() as m:
        m.setattr(save_system.os, "fsync", 실패)
        with pytest.raises(OSError):
            _저장(1, 마을="헨돈마이어")
    assert (임시_세이브폴더 / "slot_1.json").read_text(encoding="utf-8") == 이전
    assert [p.name for p in 임시_세이브폴더.iterdir()] == [
        "slot_1.json"
    ]  # 임시 파일 정리

    # 직렬화 단계에서 실패해도 본 파일은 그대로다(파일을 열기 전에 끝낸다)
    with monkeypatch.context() as m:
        m.setattr(save_system.json, "dumps", 실패)
        with pytest.raises(OSError):
            _저장(1, 마을="헨돈마이어")
    assert (임시_세이브폴더 / "slot_1.json").read_text(encoding="utf-8") == 이전


def test_세이브_본파일이_잘리면_백업으로_불러오고_요약에_복구본이_뜬다(임시_세이브폴더):
    _저장(2, 마을="엘븐가드", 이름="철수")
    _저장(2, 마을="헨돈마이어", 이름="영희")  # .bak = 앞의 세이브
    잘린 = (임시_세이브폴더 / "slot_2.json").read_text(encoding="utf-8")[:30]
    (임시_세이브폴더 / "slot_2.json").write_text(
        잘린, encoding="utf-8"
    )  # 쓰다 끊긴 파일

    플레이어, 진행도 = save_system.게임_불러오기(2)
    assert 플레이어["파티"]["파티원"][0]["캐릭터명"] == "철수"
    assert 진행도["현재마을"] == "엘븐가드"
    assert save_system.세이브_요약(2)["복구본"] is True
    assert save_system.세이브_요약(2)["대표캐릭터명"] == "철수"


def test_세이브_본파일도_백업도_못_읽으면_손상오류_요약은_예외없이_손상(
    임시_세이브폴더,
):
    _저장(1, 이름="온전")
    (임시_세이브폴더 / "slot_2.json").write_text(
        '{"플레이어": {"파티": {"파', encoding="utf-8"
    )

    with pytest.raises(save_system.세이브_손상오류) as 오류:
        save_system.게임_불러오기(2)
    assert 오류.value.슬롯번호 == 2 and "손상" in str(오류.value)
    assert save_system.세이브_요약(2) == {"슬롯번호": 2, "손상": True}

    # 슬롯 하나가 망가져도 목록은 만들어지고 다른 슬롯은 그대로다(메인 메뉴가 막히지 않는다)
    요약 = save_system.전체_세이브_요약()
    assert 요약[0]["대표캐릭터명"] == "온전"
    assert 요약[1] == {"슬롯번호": 2, "손상": True}
    assert 요약[2] == {"슬롯번호": 3, "비어있음": True}

    # 형태가 틀린 JSON(리스트, 진행도 없음)도 손상으로 본다
    (임시_세이브폴더 / "slot_3.json").write_text("[1, 2]", encoding="utf-8")
    assert save_system.세이브_요약(3) == {"슬롯번호": 3, "손상": True}
    (임시_세이브폴더 / "slot_3.json").write_text('{"플레이어": {}}', encoding="utf-8")
    assert save_system.세이브_요약(3) == {"슬롯번호": 3, "손상": True}


def test_세이브_망가진_본파일을_덮어써도_좋은_백업은_지켜진다(임시_세이브폴더):
    _저장(1, 이름="첫째")
    _저장(1, 이름="둘째")  # .bak = 첫째
    (임시_세이브폴더 / "slot_1.json").write_text("{끊김", encoding="utf-8")
    _저장(1, 이름="셋째")  # 망가진 본 파일은 백업하지 않는다
    assert (임시_세이브폴더 / "slot_1.json.bak").read_text(encoding="utf-8").count(
        "첫째"
    ) == 1
    assert save_system.게임_불러오기(1)[0]["파티"]["파티원"][0]["캐릭터명"] == "셋째"


def test_세이브_삭제는_백업과_임시파일도_지운다(임시_세이브폴더):
    _저장(1)
    _저장(1)
    (임시_세이브폴더 / "slot_1.json.tmp").write_text("x", encoding="utf-8")
    save_system.세이브_삭제(1)
    assert list(임시_세이브폴더.iterdir()) == []
    assert save_system.세이브_요약(1) is None


def test_gameflow는_손상오류를_그대로_올린다(임시_세이브폴더):
    (임시_세이브폴더 / "slot_1.json").write_text("{", encoding="utf-8")
    assert gf.세이브_손상오류 is save_system.세이브_손상오류
    with pytest.raises(gf.세이브_손상오류):
        gf.게임_불러오기(1)
    assert gf.전체_세이브_요약()[0] == {"슬롯번호": 1, "손상": True}


# 세이브 버전과 마이그레이션(N1b)


def test_세이브에는_버전이_들어_있다(임시_세이브폴더):
    _저장(1)
    저장 = json.loads((임시_세이브폴더 / "slot_1.json").read_text(encoding="utf-8"))
    assert 저장["버전"] == save_system.세이브_버전 == 1


def test_버전_없는_세이브는_0으로_보고_현재_형태로_변환한다(임시_세이브폴더):
    옛 = {
        "파티": {
            "파티원": [
                _핵심캐릭터("철수", 보유특성=["웨펀마스터", "엘레멘탈 번", "공용"])
            ],
            "골드": 40,
        },
        "진행도": {
            "클리어한던전": ["map_01A_D01_Lorien"],
            "클리어한오브젝트": [["map_01A_D01_Lorien", [3, 4]]],
        },
    }
    (임시_세이브폴더 / "slot_1.json").write_text(
        json.dumps(옛, ensure_ascii=False), encoding="utf-8"
    )
    플레이어, 진행도 = save_system.게임_불러오기(1)
    철수 = 플레이어["파티"]["파티원"][0]
    assert 철수["보유특성"] == [
        "무기의 극의",
        "공용",
    ]  # 바뀐 이름은 바꾸고 없어진 특성은 뺀다
    assert (철수["성별"], 철수["전직"], 철수["치명타주사위"]) == ("m", None, 1)
    assert 철수["횟수제한스킬"] == {"휴식제한스킬": {}}
    assert 플레이어["소지품"]["골드"] == 40 and 플레이어["숙소"] == []
    assert 진행도["플레이어레벨"] == 플레이어["레벨"] == 1
    assert 진행도["클리어한던전"] == {"dungeon_01A_D01_Lorien"}
    assert 진행도["클리어한오브젝트"] == {("dungeon_01A_D01_Lorien", (3, 4))}


def test_현재_버전_세이브는_변환을_다시_거치지_않는다(임시_세이브폴더):
    _저장(1)
    경로 = 임시_세이브폴더 / "slot_1.json"
    저장 = json.loads(경로.read_text(encoding="utf-8"))
    저장["플레이어"]["파티"]["파티원"][0].pop("성별", None)
    경로.write_text(json.dumps(저장, ensure_ascii=False), encoding="utf-8")
    # 버전 1이면 "성별이 없다"는 형식 오류가 아니라 그냥 값이다 - 변환이 덮어쓰지 않는다
    assert "성별" not in save_system.게임_불러오기(1)[0]["파티"]["파티원"][0]


def test_마이그레이션은_저장된_버전보다_높은_것만_순서대로_적용한다(
    임시_세이브폴더, monkeypatch
):
    순서 = []

    def 변환2(데이터):
        순서.append(2)
        데이터["플레이어"]["표시"] = 데이터["플레이어"].get("표시", "") + "2"

    def 변환3(데이터):
        순서.append(3)
        데이터["플레이어"]["표시"] += "3"

    _저장(1)  # 버전 1로 저장
    monkeypatch.setattr(save_system, "세이브_버전", 3)
    monkeypatch.setattr(
        save_system,
        "_마이그레이션",
        save_system._마이그레이션 + [(2, 변환2), (3, 변환3)],
    )
    플레이어, _ = save_system.게임_불러오기(1)
    assert 순서 == [2, 3] and 플레이어["표시"] == "23"
    # 이미 3으로 저장된 세이브는 건너뛴다
    _저장(2)
    순서.clear()
    save_system.게임_불러오기(2)
    assert 순서 == []


def test_더_새로운_버전_세이브는_막고_백업으로_돌아가지_않는다(임시_세이브폴더):
    _저장(1)
    _저장(1)  # .bak은 현재 버전
    경로 = 임시_세이브폴더 / "slot_1.json"
    저장 = json.loads(경로.read_text(encoding="utf-8"))
    저장["버전"] = save_system.세이브_버전 + 1
    경로.write_text(json.dumps(저장, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(save_system.세이브_버전오류) as 오류:
        save_system.게임_불러오기(1)
    assert 오류.value.버전 == save_system.세이브_버전 + 1 and "새로운 버전" in str(
        오류.value
    )
    assert isinstance(
        오류.value, save_system.세이브_손상오류
    )  # 화면은 하나만 잡아도 된다
    assert save_system.세이브_요약(1) == {"슬롯번호": 1, "손상": True, "새버전": True}


def test_세이브_버전이나_구조가_이상하면_손상으로_본다(임시_세이브폴더):
    경로 = 임시_세이브폴더 / "slot_1.json"
    for 내용 in (
        {"버전": "1", "진행도": {}},  # 버전이 정수가 아님
        {"버전": -1, "진행도": {}},
        {"버전": True, "진행도": {}},
        {"플레이어": [], "진행도": {}},  # 변환하다 실패하는 구조
        {"플레이어": {"파티": {"파티원": [1]}}, "진행도": {}},
    ):
        경로.write_text(json.dumps(내용), encoding="utf-8")
        assert save_system.세이브_요약(1) == {"슬롯번호": 1, "손상": True}, 내용
        with pytest.raises(save_system.세이브_손상오류):
            save_system.게임_불러오기(1)

    # 본 파일의 구조만 이상하면 백업으로 돌아간다
    _저장(1, 이름="온전")
    _저장(1, 이름="새것")
    경로.write_text(json.dumps({"플레이어": [], "진행도": {}}), encoding="utf-8")
    assert save_system.게임_불러오기(1)[0]["파티"]["파티원"][0]["캐릭터명"] == "온전"


# 세이브 폴더를 앱 데이터 폴더로 옮기기(N1c) - 옛 위치(game/saves)의 세이브는 한 번만 복사한다.

_원래_세이브_폴더 = (
    save_system._세이브_폴더
)  # conftest의 자동 픽스처가 바꿔치기하기 전 함수


@pytest.fixture
def 폴더_설정(tmp_path, monkeypatch):
    """옛 폴더(= 기본 위치)와 새 폴더를 tmp에 두고 실제 폴더 계산 함수를 되살린다."""
    옛 = tmp_path / "옛"
    옛.mkdir()
    새 = tmp_path / "새" / "saves"  # 아직 없는 폴더 - 설정이 만든다
    monkeypatch.setattr(save_system, "_세이브_폴더", _원래_세이브_폴더)
    monkeypatch.setattr(save_system, "_기본_세이브_폴더", lambda: str(옛))
    monkeypatch.setattr(save_system, "_폴더_재정의", None)
    return 옛, 새


def test_세이브_폴더_설정은_옛_세이브를_한번_복사하고_옛_파일은_남긴다(폴더_설정):
    옛, 새 = 폴더_설정
    (옛 / "slot_1.json").write_text("{옛1}", encoding="utf-8")
    (옛 / "slot_1.json.bak").write_text("{옛1백업}", encoding="utf-8")
    (옛 / "slot_3.json").write_text("{옛3}", encoding="utf-8")
    (옛 / "slot_9.json").write_text("{범위 밖}", encoding="utf-8")

    복사 = save_system.세이브_폴더_설정(str(새))
    assert 복사 == ["slot_1.json", "slot_1.json.bak", "slot_3.json"]
    assert save_system._세이브_폴더() == str(새)
    assert (새 / "slot_1.json").read_text(encoding="utf-8") == "{옛1}"
    assert (새 / "slot_1.json.bak").read_text(encoding="utf-8") == "{옛1백업}"
    assert not (새 / "slot_9.json").exists()
    assert (옛 / "slot_1.json").exists() and (
        옛 / "slot_3.json"
    ).exists()  # 옛 파일은 지우지 않는다
    assert not list(새.glob("*.tmp"))


def test_세이브_폴더_설정_후_저장은_새_폴더에_된다(폴더_설정):
    옛, 새 = 폴더_설정
    save_system.세이브_폴더_설정(str(새))
    _저장(1)
    assert (새 / "slot_1.json").exists() and not (옛 / "slot_1.json").exists()
    assert save_system.세이브_요약(1)["대표캐릭터명"] == "철수"


def test_옛_세이브는_두번_가져오지_않아_지운_슬롯이_되살아나지_않는다(폴더_설정):
    옛, 새 = 폴더_설정
    (옛 / "slot_1.json").write_text("{옛}", encoding="utf-8")
    save_system.세이브_폴더_설정(str(새))
    save_system.세이브_삭제(1)  # 사용자가 슬롯을 지웠다
    assert save_system.세이브_폴더_설정(str(새)) == []  # 다음 실행
    assert not (새 / "slot_1.json").exists()


def test_새_폴더에_이미_있는_슬롯은_덮어쓰지_않는다(폴더_설정):
    옛, 새 = 폴더_설정
    새.mkdir(parents=True)
    (새 / "slot_1.json").write_text("{새}", encoding="utf-8")
    (옛 / "slot_1.json").write_text("{옛}", encoding="utf-8")
    (옛 / "slot_2.json").write_text("{옛2}", encoding="utf-8")
    assert save_system.세이브_폴더_설정(str(새)) == ["slot_2.json"]
    assert (새 / "slot_1.json").read_text(encoding="utf-8") == "{새}"


def test_옛_폴더가_없거나_같은_폴더면_복사하지_않고_표시만_남긴다(
    폴더_설정, tmp_path, monkeypatch
):
    옛, 새 = 폴더_설정
    monkeypatch.setattr(
        save_system, "_기본_세이브_폴더", lambda: str(tmp_path / "없음")
    )
    assert save_system.세이브_폴더_설정(str(새)) == []
    assert (새 / save_system._가져옴_표시파일).exists()

    같은 = tmp_path / "같은"
    같은.mkdir()
    (같은 / "slot_1.json").write_text("{x}", encoding="utf-8")
    monkeypatch.setattr(save_system, "_기본_세이브_폴더", lambda: str(같은))
    assert save_system.세이브_폴더_설정(str(같은)) == []


def test_복사에_실패해도_앱은_계속되고_다음_실행에_다시_시도한다(
    폴더_설정, monkeypatch
):
    옛, 새 = 폴더_설정
    (옛 / "slot_1.json").write_text("{옛}", encoding="utf-8")

    def 실패(*args, **kwargs):
        raise OSError("읽기 실패")

    with monkeypatch.context() as m:
        m.setattr(save_system.shutil, "copy2", 실패)
        assert save_system.세이브_폴더_설정(str(새)) == []
    assert not (새 / save_system._가져옴_표시파일).exists()  # 표시가 없어 다시 시도한다
    assert save_system.세이브_폴더_설정(str(새)) == ["slot_1.json"]
    assert (새 / save_system._가져옴_표시파일).exists()


def test_gameflow는_세이브_폴더_설정을_내보낸다(폴더_설정):
    옛, 새 = 폴더_설정
    assert gf.세이브_폴더_설정(str(새)) == []
    assert save_system._세이브_폴더() == str(새)


# ---------------------------------------------------------------- levelup


def _레벨업캐릭터():
    c = _캐릭터(레벨=1, 약점스탯="지능", 건강=12, 기본최대HP=12)
    return c


def test_레벨업_타입별():
    c = _레벨업캐릭터()
    레벨업.캐릭터_레벨업(
        c,
        {"타입": "특성획득", "획득": {"획득특성": ["힘", "재주"]}},
        6,
        특성정의모음={"힘": {"효과": {"변동대상": "근력", "변동값": 1}}, "재주": {}},
    )
    assert c["레벨"] == 2 and c["보유특성"] == ["힘", "재주"] and c["근력"] == 9
    assert c["기본최대HP"] == 2 * (6 + 1)
    레벨업.캐릭터_레벨업(
        c,
        {"타입": "스탯획득", "획득": {"배분점수": 2}},
        6,
        배분={"근력": 1, "민첩": 1},
    )
    레벨업.캐릭터_레벨업(c, {"타입": "미정", "획득": {"설명": "미정"}}, 6)
    레벨업.캐릭터_레벨업(c, {"타입": "행동획득", "획득": {"추가횟수": 1}}, 6)
    레벨업.캐릭터_레벨업(c, {"타입": "스킬획득", "획득": {"획득스킬": ["강권"]}}, 6)
    assert (c["근력"], c["민첩"], c["보유스킬"], c["추가공격"], c["레벨"]) == (
        10,
        9,
        ["강권"],
        1,
        6,
    )
    with pytest.raises(ValueError, match="알 수 없는"):
        레벨업.캐릭터_레벨업(c, {"타입": "이상함"}, 6)


def test_스킬강화_레벨업():
    """레벨 12 스킬강화 - 선택지 안의 스킬 하나와 배율을 기록, 다시 고르면 교체."""
    c = _레벨업캐릭터()
    항목 = {
        "타입": "스킬강화",
        "획득": {"최대차수": 3, "최종피해배율": 1.5, "MP소모배율": 2},
    }
    with pytest.raises(ValueError, match="강화할 스킬"):
        레벨업.캐릭터_레벨업(c, 항목, 6, 강화스킬="없음", 스킬강화선택지=["귀참"])
    assert c["레벨"] == 1 and "스킬강화" not in c
    레벨업.캐릭터_레벨업(c, 항목, 6, 강화스킬="귀참", 스킬강화선택지=["귀참", "가드"])
    assert c["스킬강화"] == {"스킬": "귀참", "최종피해배율": 1.5, "MP소모배율": 2}
    레벨업.캐릭터_레벨업(c, 항목, 6, 강화스킬="가드", 스킬강화선택지=["귀참", "가드"])
    assert c["스킬강화"]["스킬"] == "가드" and c["레벨"] == 3
    # 고를 스킬이 하나도 없으면 레벨만 오른다
    d = _레벨업캐릭터()
    레벨업.캐릭터_레벨업(d, 항목, 6, 스킬강화선택지=[])
    assert d["레벨"] == 2 and "스킬강화" not in d


def test_배분_오류와_약점제거():
    c = _레벨업캐릭터()
    항목 = {"타입": "스탯획득", "획득": {"배분점수": 2}}
    with pytest.raises(ValueError, match="필요합계"):
        레벨업.캐릭터_레벨업(c, 항목, 6, 배분={"근력": 1})
    with pytest.raises(ValueError, match="약점스탯"):
        레벨업.캐릭터_레벨업(c, 항목, 6, 배분={"지능": 2})
    assert c["레벨"] == 1  # 실패한 레벨업은 레벨도 올리지 않는다(B5)
    assert 레벨업.약점스탯_투자가능(c, "근력") and not 레벨업.약점스탯_투자가능(
        c, "지능"
    )
    c["보유특성"].append("약점제거")
    assert 레벨업.약점스탯_투자가능(c, "지능")


def test_퍽_분류별():
    c = _레벨업캐릭터()
    퍽 = {"타입": "퍽획득"}
    레벨업.캐릭터_레벨업(
        c, 퍽, 6, 퍽이름="a", 퍽정의={"분류": "특성획득", "획득특성": "오토가드"}
    )
    레벨업.캐릭터_레벨업(
        c,
        퍽,
        6,
        퍽이름="b",
        퍽정의={"분류": "스탯획득", "획득스탯포인트": 2},
        배분={"매력": 2},
    )
    레벨업.캐릭터_레벨업(
        c, 퍽, 6, 퍽이름="c", 퍽정의={"분류": "스탯획득", "획득특성": "약점제거"}
    )
    레벨업.캐릭터_레벨업(
        c, 퍽, 6, 퍽이름="d", 퍽정의={"분류": "스탯획득"}
    )  # 둘 다 없음 -> 변화 없음
    레벨업.캐릭터_레벨업(
        c, 퍽, 6, 퍽이름="e", 퍽정의={"분류": "스킬획득", "획득스킬": "가드"}
    )
    레벨업.캐릭터_레벨업(
        c,
        퍽,
        6,
        퍽이름="f",
        퍽정의={"분류": "스킬획득", "획득스킬": None},
        선택스킬="큐어",
    )
    assert c["보유특성"] == ["오토가드", "약점제거"] and c["매력"] == 10
    assert c["보유스킬"] == ["가드", "큐어"]
    with pytest.raises(NotImplementedError):
        레벨업.캐릭터_레벨업(c, 퍽, 6, 퍽이름="g", 퍽정의={"분류": "일반퍽"})


# ------------------------------------------------------------------- loot


@pytest.mark.parametrize(
    "값,기대",
    [("미정", 0), (None, 0), ("abc", 0), ("10~1", 0), (7, 7), ("3", 3), (True, 0)],
)
def test_골드_굴림_고정값과_미정(값, 기대):
    assert 전리품.골드_굴림(값) == 기대


def test_골드_굴림_범위(monkeypatch):
    monkeypatch.setattr(전리품.random, "randint", lambda a, b: a * 100 + b)
    assert 전리품.골드_굴림("1~10") == 110


def test_미정_드랍표와_확률은_아무것도_주지_않는다(카탈로그):
    미정 = {"획득골드": "미정", "드랍표": [{"이름": "미정", "발동확률": "미정"}]}
    확률미정 = {"드랍표": [{"이름": "커먼장비군", "발동확률": "미정"}]}
    for 몬스터 in (미정, 확률미정, {}):
        assert 전리품.몬스터_전리품(몬스터, 드랍표_모음, 카탈로그["장비"]) == (0, [])
    # 잡템군은 아이템이름/드랍확률이 전부 "미정"
    assert 전리품.드랍표_굴림(드랍표_모음["잡템군"], 카탈로그["장비"]) == []
    assert 전리품.드랍표_굴림({"타입": "모름"}, 카탈로그["장비"]) == []
    assert 전리품.드랍표_굴림({"타입": "가중형", "아이템": []}, 카탈로그["장비"]) == []


def test_가중형은_하나_독립형은_통과한_것_전부(카탈로그, monkeypatch):
    monkeypatch.setattr(전리품.random, "random", lambda: 0.0)  # 모든 확률 통과
    가중 = 전리품.드랍표_굴림(드랍표_모음["커먼장비군"], 카탈로그["장비"])
    assert len(가중) == 1 and 가중[0] in [
        i["아이템이름"] for i in 드랍표_모음["커먼장비군"]["아이템"]
    ]
    독립 = {
        "타입": "독립형",
        "아이템": [
            {"아이템이름": "조잡한 반지", "드랍확률": 0.5},
            {"아이템이름": "미정", "드랍확률": 1},
            {"아이템이름": "조잡한 팔찌", "드랍확률": "1/2"},
        ],
    }
    assert 전리품.드랍표_굴림(독립, 카탈로그["장비"]) == ["조잡한 반지", "조잡한 팔찌"]
    monkeypatch.setattr(전리품.random, "random", lambda: 0.99)
    assert 전리품.드랍표_굴림(독립, 카탈로그["장비"]) == []


def test_아이템조건은_카탈로그에서_맞는_것을_고른다(카탈로그):
    조건 = {"카테고리": "방어구", "레어도": "커먼", "티어": 1}
    후보 = 전리품._조건_후보(조건, 카탈로그["장비"])
    방어구 = {
        이름: 아이템
        for 탭 in ("상의", "하의", "어깨", "벨트", "신발")
        for 이름, 아이템 in 카탈로그["장비"][탭].items()
    }
    assert "허름한 경갑 상의" in 후보 and set(후보) <= set(방어구)
    assert all((방어구[i]["레어도"], 방어구[i]["티어"]) == ("커먼", 1) for i in 후보)
    assert len(후보) == sum(
        (a["레어도"], a["티어"]) == ("커먼", 1) for a in 방어구.values()
    )
    assert 전리품._조건_후보({"카테고리": "모름"}, 카탈로그["장비"]) == []
    표 = {"타입": "가중형", "아이템": [{"아이템조건": 조건, "드랍비율": 1}]}
    assert 전리품.드랍표_굴림(표, 카탈로그["장비"])[0] in 후보
    assert 전리품._항목_아이템({}, 카탈로그["장비"]) is None


def test_전리품_판정은_골드를_더하고_같은_아이템을_묶는다(monkeypatch):
    결과들 = iter([(3, ["A", "B"]), (4, ["A"]), (0, [])])
    monkeypatch.setattr(전리품, "몬스터_전리품", lambda *_: next(결과들))
    assert 전리품.전리품_판정([{}, {}, {}], {}, {}) == {
        "골드": 7,
        "아이템": [("A", 2), ("B", 1)],
    }


def test_드랍표에_적힌_아이템은_전부_카탈로그에_있다(카탈로그):
    # 장비뿐 아니라 포션 등 상점 카탈로그 전체(포션군)
    전체 = {
        이름 for 탭모음 in 카탈로그.values() for 탭 in 탭모음.values() for 이름 in 탭
    }
    for 표이름, 표 in 드랍표_모음.items():
        표들 = list(표["차수표"].values()) if 표["타입"] == "차수별" else [표]
        for 항목 in [항목 for t in 표들 for 항목 in t["아이템"]]:
            이름 = 항목.get("아이템이름")
            if 이름 not in (None, "미정"):
                assert 이름 in 전체, (표이름, 이름)


def test_보상_후보는_몬스터마다_넣고_발동확률은_보지_않는다(카탈로그):
    고블린 = {"드랍표": [{"이름": "커먼특장군", "발동확률": 0.01}]}
    미정 = {"드랍표": [{"이름": "미정", "발동확률": "미정"}]}
    후보 = 전리품.보상_후보목록([고블린, 고블린, 미정], 드랍표_모음, 카탈로그["장비"])
    이름들 = [이름 for 이름, _ in 후보]
    assert 이름들 == ["망가진 암밴드", "망가진 증진석", "망가진 귀걸이"] * 2
    assert all(abs(w - 1 / 3) < 1e-9 for _, w in 후보)
    assert 전리품.보상_후보목록([미정, {}], 드랍표_모음, 카탈로그["장비"]) == []


def test_보상_후보_독립형과_아이템조건과_미정(카탈로그):
    표모음 = {
        "독립": {
            "타입": "독립형",
            "아이템": [
                {"아이템이름": "조잡한 반지", "드랍확률": 0.5},
                {"아이템이름": "미정", "드랍확률": 1},
                {"아이템이름": "조잡한 팔찌", "드랍확률": "미정"},
            ],
        },
        "조건": {
            "타입": "가중형",
            "아이템": [
                {
                    "아이템조건": {"카테고리": "방어구", "레어도": "커먼", "티어": 1},
                    "드랍비율": 1,
                }
            ],
        },
    }
    몬스터 = {"드랍표": [{"이름": "독립"}, {"이름": "조건"}]}
    후보 = 전리품.보상_후보목록([몬스터], 표모음, 카탈로그["장비"])
    assert 후보[0] == ("조잡한 반지", 0.5)
    조건후보 = 후보[1:]
    assert len(조건후보) == len(
        전리품._조건_후보(표모음["조건"]["아이템"][0]["아이템조건"], 카탈로그["장비"])
    )
    assert abs(sum(w for _, w in 조건후보) - 1) < 1e-9  # 가중치를 똑같이 나눈다


def test_보상_뽑기는_가중치로_뽑고_뽑힌_항목은_다시_안_뽑는다(monkeypatch):
    assert 전리품.보상_뽑기([]) == [None, None, None]
    assert 전리품.보상_뽑기([("A", 1)]) == ["A", None, None]
    # 같은 아이템이 두 항목이면 두 칸에 나올 수 있다
    assert sorted(전리품.보상_뽑기([("A", 1), ("A", 1)]), key=str) == ["A", "A", None]
    받은가중치 = []

    def 가짜(범위, weights, k):
        받은가중치.append(list(weights))
        return [len(weights) - 1]  # 매번 마지막 항목

    monkeypatch.setattr(전리품.random, "choices", 가짜)
    assert 전리품.보상_뽑기([("A", 1), ("B", 2), ("C", 3), ("D", 4)]) == ["D", "C", "B"]
    assert 받은가중치 == [[1, 2, 3, 4], [1, 2, 3], [1, 2]]


def test_골드_수식과_차수별_드랍표와_장비_카테고리(카탈로그):
    assert 전리품.골드_굴림("레벨×100", {"레벨": 3, "차수": 1}) == 300
    assert 전리품.골드_굴림("레벨×100") == 100  # 레벨이 없으면 1
    assert 전리품.골드_굴림("알수없는수식") == 0
    표 = 드랍표_모음["황금고블린군"]
    언커먼 = 전리품._조건_후보(
        {"카테고리": "장비", "레어도": "언커먼"}, 카탈로그["장비"]
    )
    assert len(언커먼) == sum(
        d.get("레어도") == "언커먼"
        for 탭 in 카탈로그["장비"].values()
        for d in 탭.values()
    )
    (이름,) = 전리품.드랍표_굴림(표, 카탈로그["장비"], 차수=1)
    assert 이름 in 언커먼
    assert 전리품.드랍표_굴림(표, 카탈로그["장비"], 차수=2) == []  # 2차수는 아직 없음
    황금 = {"차수": 1, "드랍표": [{"이름": "황금고블린군", "발동확률": 1}]}
    assert sorted(
        n for n, _ in 전리품.보상_후보목록([황금], 드랍표_모음, 카탈로그["장비"])
    ) == sorted(언커먼)


def test_드랍그룹_이름과_포션군은_차수_티어의_HP06_MP04(카탈로그):
    for 이름 in (
        "커먼장비군",
        "커먼악세군",
        "커먼특장군",
        "커먼무기군",
        "언커먼무기군",
        "언커먼장비군",
        "언커먼악세군",
        "언커먼특장군",
        "포션군",
    ):
        assert 이름 in 드랍표_모음, 이름
    for 옛이름 in ("커먼장비A군", "커먼장비B군", "커먼장비C군"):
        assert 옛이름 not in 드랍표_모음
    레어도 = {
        n: d.get("레어도") for 탭 in 카탈로그["장비"].values() for n, d in 탭.items()
    }
    for 표이름, 등급 in (
        ("커먼무기군", "커먼"),
        ("언커먼무기군", "언커먼"),
        ("언커먼악세군", "언커먼"),
    ):
        assert {레어도[i["아이템이름"]] for i in 드랍표_모음[표이름]["아이템"]} == {
            등급
        }
    포션 = 드랍표_모음["포션군"]["차수표"]
    assert sorted(포션) == [1, 2, 3, 4]
    assert [(i["아이템이름"], i["드랍비율"]) for i in 포션[1]["아이템"]] == [
        ("초보자용 HP 포션", 0.6),
        ("초보자용 MP 포션", 0.4),
    ]
    random.seed(2)
    나온것 = [
        전리품.드랍표_굴림(드랍표_모음["포션군"], 카탈로그["장비"], 차수=2)[0]
        for _ in range(500)
    ]
    assert set(나온것) == {"입문자용 HP 포션", "입문자용 MP 포션"}
    assert 0.53 < 나온것.count("입문자용 HP 포션") / 500 < 0.67


# ------------------------------------------------------------------- potion
def test_회복포션_굴림_최소값과_최대치(monkeypatch):
    포션 = {
        "티어": 3,
        "회복대상": "HP",
        "회복값": "(차수)d10+건강보정치",
        "최소회복값": 1,
        "레벨제한": 11,
    }
    monkeypatch.setattr(dice_utils, "주사위_합", lambda 개수, 면수: 개수 * 100 + 면수)
    assert 포션시스템.회복량_굴림(포션, 2) == 310 + 2  # 3d10 -> 개수/면수 확인
    monkeypatch.setattr(dice_utils, "주사위_합", lambda 개수, 면수: 3)
    assert 포션시스템.회복량_굴림(포션, -1) == 2
    assert 포션시스템.회복량_굴림(포션, -5) == 1  # 3-5 -> 최소 1
    mp포션 = dict(포션, 회복대상="MP", 회복값="(차수)d6+주문시전보정치")
    assert 포션시스템.회복량_굴림(mp포션, 1) == 4
    대상 = {"현재HP": 8}
    assert 포션시스템.포션_적용(대상, 포션, 0, 10) == 2 and 대상["현재HP"] == 10


def test_회복포션_사용불가_사유와_소지품_차감():
    포션 = {"티어": 1, "회복대상": "MP", "레벨제한": 6}
    사유 = 포션시스템.사용불가_사유
    assert 사유(포션, 6, 5, 3, 10, 1) is None
    assert "소지품" in 사유(포션, 6, 5, 3, 10, 0)
    assert "레벨 6" in 사유(포션, 5, 5, 3, 10, 1)
    assert "쓰러진" in 사유(포션, 6, 0, 3, 10, 1)
    assert "가득" in 사유(포션, 6, 5, 10, 10, 1)
    소지품 = {"포션": {"a": 2}}
    포션시스템.소지품_차감(소지품, "a")
    포션시스템.소지품_차감(소지품, "a")
    assert 소지품["포션"] == {}
    with pytest.raises(ValueError):
        포션시스템.소지품_차감(소지품, "a")
