# 컨트롤러 - 업적 - 메뉴 [업적] 화면용 목록/보상 받기
# (화면은 gameflow.py 창구만 부른다. 설명은 gameflow.py 머리말)
#
# 판정과 보상은 achievement_system.py, 업적 목록은 game/data/achievement/achievement_list.py.
# 전투 승리 횟수는 ctl_rewards.전투_결과_정리가 센다.

from game.data.achievement.achievement_list import 업적_목록 as _업적데이터
from game.data.achievement.achievement_list import 업적_분류
from game.system import achievement_system
from game.controller.ctl_party import 플레이어뷰

__all__ = [
    "업적_분류목록",
    "업적_목록",
    "업적_받을_보상_수",
    "업적_보상_받기",
    "업적_보상_전부_받기",
    "업적_보상_문구",
]

업적_분류목록 = list(업적_분류)


def 업적_목록(게임상태, 분류):
    """그 분류의 업적 줄들 - {"ID", "이름", "설명", "진행", "목표", "달성", "받음", "보상"(보이는 글)}."""
    진행도 = 게임상태["진행도"]
    줄들 = []
    for 업적 in _업적데이터:
        if 업적["분류"] != 분류:
            continue
        진행, 목표 = achievement_system.진행값(진행도, 업적)
        줄들.append(
            {
                "ID": 업적["ID"],
                "이름": 업적["이름"],
                "설명": 업적.get("설명", ""),
                "진행": 진행,
                "목표": 목표,
                "달성": 진행 >= 목표,
                "받음": achievement_system.받음(진행도, 업적),
                "보상": achievement_system.보상_이름(업적),
            }
        )
    return 줄들


def 업적_받을_보상_수(게임상태):
    진행도 = 게임상태["진행도"]
    return sum(
        1 for 업적 in _업적데이터 if achievement_system.받을_수_있음(진행도, 업적)
    )


def 업적_보상_받기(게임상태, 업적ID):
    """그 업적의 보상을 받고 {"골드", "아이템"}을 돌려준다. 없는 업적/달성 전/이미 받음/줄 수 없는 보상이면 ValueError."""
    업적 = next((u for u in _업적데이터 if u["ID"] == 업적ID), None)
    if 업적 is None:
        raise ValueError(f"'{업적ID}' 업적은 없다.")
    return achievement_system.보상_받기(
        게임상태["진행도"], 플레이어뷰(게임상태), 업적, 게임상태["상점카탈로그"]
    )


def 업적_보상_전부_받기(게임상태):
    """받을 수 있는 보상을 전부 받는다. (받은 업적 수, {"골드": 합, "아이템": [...]})."""
    return achievement_system.전부_받기(
        게임상태["진행도"], 플레이어뷰(게임상태), _업적데이터, 게임상태["상점카탈로그"]
    )


def 업적_보상_문구(받음):
    """받은 보상을 화면 글로 - "10G, 마법으로 봉인된 소검"."""
    return achievement_system.보상_문구(받음)
