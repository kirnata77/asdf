# 컨트롤러 - 마을 - 이동, 휴식
# (gameflow.py에서 분리 - N5. 화면은 gameflow.py 창구만 부른다. 설명은 gameflow.py 머리말)

from game.system import town_system
from game.controller.ctl_party import 파티_최대치로_회복

__all__ = [
    "현재_마을정보",
    "이동가능마을목록",
    "마을_이동",
    "이동가능던전목록",
    "휴식",
]


def 현재_마을정보(게임상태):
    마을명 = 게임상태["진행도"]["현재마을"]
    for 마을 in town_system.기본_마을목록():
        if 마을["마을명"] == 마을명:
            return 마을
    return town_system.기본_마을목록()[0]


def 이동가능마을목록(게임상태):
    return town_system.이동가능마을목록(
        town_system.기본_마을목록(),
        게임상태["진행도"],
    )


def 마을_이동(게임상태, 목표마을명):
    town_system.마을_이동(게임상태["진행도"], 목표마을명)


def 이동가능던전목록(게임상태):
    return town_system.이동가능던전목록(현재_마을정보(게임상태))


def 휴식(게임상태):
    town_system.휴식_처리(게임상태["파티"])
    # town_system은 장비를 모르므로 장비 반영 최대치로 다시 채운다.
    파티_최대치로_회복(게임상태)
