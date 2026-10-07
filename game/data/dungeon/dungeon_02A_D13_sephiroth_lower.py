# =====================
# 세피로타 하층 (소형지도)
# =====================
# dungeon_format.py 양식을 따른다.
#
# 하늘성(2차수) 탑 던전의 지도 틀이다. 웨스트코스트(마을)에서 [던전이동]으로
# 바로 들어온다. 가운데의 둥근 탑을 반시계 방향으로 도는 구조 - 하층은 탑의
# 남쪽을 서쪽에서 동쪽으로 돈다(상층 세피로타 상층이 북쪽을 이어서 돈다).
# 23x20, 사용자가 그린 상층 워크시트를 위아래로 뒤집고, 바깥 하늘을 하늘성 벽으로
# 바꾼 모양이다(양옆 한 줄은 하늘 "Y" 그대로). 이동불가는 가운데 위(탑)와 고리 바깥.
# - 왼쪽 위 천장(3,0)은 웨스트코스트(마을)로 나가는 길이다. 마을에서 들어오면 (3,1).
# - 오른쪽 위 천장(19,0)은 세피로타 상층(dungeon_02A_D14_sephiroth_upper)으로 올라가는 포탈이고,
#   올라가면 상층의 오른쪽 아래(19,18)에 나타난다.
# - 포탈 바로 앞(19,1)에 보스전투 이벤트가 있다. 이겨야 포탈로 갈 수 있다
#   ("통행가능화" - 던전을 나갔다 들어오면 다시 막힌다).
#
# 타일: 발판 에메랄드, 이동불가 하늘성 벽, 하늘 노을("타일" - dungeon_format.py).
#
# 몬스터: 아직 정하지 않았다(다음 단계). 그때까지 인카운트가 없어 걸어도
# 전투가 일어나지 않고, 보스의 "전투몬스터"가 비어 있어 보스는 막힌 채로
# 있다(오브젝트_상호작용이 "몬스터데이터없음"을 돌려준다).

맵정보 = {
    "지도명": "세피로타 하층",
    "상세지역": ["아라드", "벨마이어 공국 남부"],
    "지도": [
        "YXX#XXXXXXXXXXXXXXX#XXY",
        "YXOOOXXXXXXXXXXXXXO@OXY",
        "YXOOOXXXXXXXXXXXXXOOOXY",
        "YXOOOOXXXXXXXXXXXOOOOXY",
        "YXOOOOXXXXXXXXXXXOOOOXY",
        "YXXOOOOXXXXXXXXXOOOOXXY",
        "YXXXOOOOXXXXXXXOOOOXXXY",
        "YXXXXOOOOOXXXOOOOOXXXXY",
        "YXXXXXOOOOOOOOOOOXXXXXY",
        "YXXXXXXOOOOOOOOOXXXXXXY",
        "YXXXXXXXOOOOOOOXXXXXXXY",
        "YXXXXXXXXXOOOXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
        "YXXXXXXXXXXXXXXXXXXXXXY",
    ],
    "타일": {
        "O": "asset_tile_emerald.webp",
        "X": "asset_tile_skycastlewall.webp",
        "Y": "asset_tile_skyyellow.webp",
    },
    "입장좌표": (3, 1),
    "오브젝트": {
        (19, 1): {
            "분류": "이벤트",
            "타입": "보스전투",
            "이름": "세피로타 하층 보스",  # 미정 - 몬스터를 정할 때 바꾼다
            "설명": "세피로타 상층으로 가는 포탈을 지키는 보스. 이겨야 포탈로 갈 수 있다.",
            "발동방식": "말걸기",
            "전투몬스터": [],  # 미정 - 몬스터를 정할 때 채운다(레벨/차수도)
            "클리어시": "통행가능화",
        },
    },
    "연결지역": {
        (3, 0): {
            "연결맵": "town_02A_T03_westcoast",
            "진입좌표": None,  # 마을은 화면(선택지) 형태라 좌표 개념이 없음
        },
        (19, 0): {
            "연결맵": "dungeon_02A_D14_sephiroth_upper",
            "진입좌표": (19, 18),
        },
    },
}
