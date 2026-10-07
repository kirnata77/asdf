# =====================
# 세피로타 상층 (소형지도)
# =====================
# dungeon_format.py 양식을 따른다.
#
# 하늘성(2차수) 탑 던전의 지도 틀이다. 마을에서 바로 올 수 없고,
# 세피로타 하층(dungeon_02A_D13_sephiroth_lower)의 천장 포탈(19,0)로 올라온다. 하층에 이어
# 탑의 북쪽을 동쪽에서 서쪽으로 돈다(반시계 방향).
# 23x20, 사용자가 그린 워크시트 그대로다. 고리 바깥은 하늘 "Y", 발판 바로 둘레와
# 가운데 아래(탑)는 하늘성 벽 "X".
# - 하층에서 올라오면 오른쪽 아래(19,18)에 나타난다. 바로 밑 바닥(19,19)은
#   하층으로 내려가는 길이다(내려가면 하층 보스 앞 (19,2)).
# - 왼쪽 아래 바닥(3,19)은 웨스트코스트(마을)로 돌아가는 포탈이다.
# - 마을 포탈 바로 앞(3,18)에 보스전투 이벤트가 있다. 이겨야 마을 포탈로 갈 수
#   있다("통행가능화" - 던전을 나갔다 들어오면 다시 막힌다).
#
# 타일: 발판 에메랄드, 이동불가 하늘성 벽, 하늘 노을, 포탈은 벽 위에 하늘성 게이트("타일" - dungeon_format.py).
#
# 몬스터: 아직 정하지 않았다(다음 단계). 그때까지 인카운트가 없고, 보스의
# "전투몬스터"가 비어 있어 보스는 막힌 채로 있다.

맵정보 = {
    "지도명": "세피로타 상층",
    "상세지역": ["아라드", "벨마이어 공국 남부"],
    "지도": [
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYYYYYYYYYYYYYYY",
        "YYYYYYYYYXXXXXYYYYYYYYY",
        "YYYYYYYXXXOOOXXXYYYYYYY",
        "YYYYYYXXOOOOOOOXXYYYYYY",
        "YYYYYXXOOOOOOOOOXXYYYYY",
        "YYYYXXOOOOOOOOOOOXXXYYY",
        "YYYXXOOOOOXXXOOOOOXXYYY",
        "YYXXOOOOXXXXXXXOOOOXXYY",
        "YXXOOOOXXXXXXXXXOOOOXXY",
        "YXOOOOXXXXXXXXXXXOOOOXY",
        "YXOOOOXXXXXXXXXXXOOOOXY",
        "YXOOOXXXXXXXXXXXXXOOOXY",
        "YXO@OXXXXXXXXXXXXXOOOXY",
        "YXX#XXXXXXXXXXXXXXX#XXY",
    ],
    "타일": {
        "O": "asset_tile_emerald.webp",
        "X": "asset_tile_skycastlewall.webp",
        "Y": "asset_tile_skyyellow.webp",
        "#": [
            "asset_tile_skycastlewall.webp",
            "asset_tile_gate_skycastle.webp",
        ],
    },
    "입장좌표": (19, 18),
    "오브젝트": {
        (3, 18): {
            "분류": "이벤트",
            "타입": "보스전투",
            "이름": "세피로타 상층 보스",  # 미정 - 몬스터를 정할 때 바꾼다
            "설명": "마을로 가는 포탈을 지키는 보스. 이겨야 포탈로 갈 수 있다.",
            "발동방식": "말걸기",
            "전투몬스터": [],  # 미정 - 몬스터를 정할 때 채운다(레벨/차수도)
            "클리어시": "통행가능화",
        },
    },
    "연결지역": {
        (3, 19): {
            "연결맵": "town_02A_T03_westcoast",
            "진입좌표": None,  # 마을은 화면(선택지) 형태라 좌표 개념이 없음
        },
        (19, 19): {
            "연결맵": "dungeon_02A_D13_sephiroth_lower",
            "진입좌표": (19, 2),
        },
    },
}
