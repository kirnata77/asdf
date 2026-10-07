# =====================
# 미들오션 심해 (소형지도)
# =====================
# dungeon_format.py 양식을 따른다.
#
# 하늘성(2차수) 던전의 지도 틀이다. 마을에서 바로 올 수 없고,
# 미들오션 천해(dungeon_02A_D15_middleocean_shallow)의 동쪽 포탈(16,3)을 클리어해야 들어온다.
# 같은 좌우 2구역(각 5x5) 구조.
# - 서쪽 벽(0,3)은 미들오션 천해으로 돌아가는 길이다(포탈 바로 앞 (15,3)에 나타난다).
# - 동쪽 방 끝은 막다른 길이다.
# - 나무(X) 배치는 랜덤 텍스처이며 의미는 없다.
#
# 몬스터: 아직 정하지 않았다(다음 단계). 그때까지 인카운트가 없다.

맵정보 = {
    "지도명": "미들오션 심해",
    "상세지역": ["아라드", "벨마이어 공국 남부"],
    "지도": [
        "XXXXXXXXXXXXXXXXX",
        "XOOOXOXXXXXOOOOOX",
        "XOXOOOXXXXXXXOOOX",
        "#OOOOOOOOOOOOOOOX",
        "XOOOOXXXXXXOOOOOX",
        "XOXXOOXXXXXXOXOXX",
        "XXXXXXXXXXXXXXXXX",
    ],
    "입장좌표": (1, 3),
    "오브젝트": {},
    "연결지역": {
        (0, 3): {
            "연결맵": "dungeon_02A_D15_middleocean_shallow",
            "진입좌표": (15, 3),
        },
    },
}
