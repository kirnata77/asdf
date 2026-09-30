# =====================
# 전리품 시스템
# =====================
# 전투 승리 후 쓰러뜨린 적마다 "획득골드"와 "드랍표"를 굴린다.
# 데이터 양식은 monster_format.py "몬스터 드랍표 항목 양식"과
# monster_drop.py 머리 설명을 따른다.
#
# "미정"(또는 해석할 수 없는 값)은 골드 0 / 드랍 없음으로 처리한다
# (사용자 결정 2026-09-30) - 발동확률/드랍비율/드랍확률/아이템이름 어느
# 하나라도 "미정"이면 그 항목은 건너뛴다.

import random
from fractions import Fraction

# 드랍표 "아이템조건"의 "카테고리" 키워드 -> 장비 카탈로그의 탭들
조건_카테고리_탭 = {
    "방어구": ["상의", "하의", "어깨", "벨트", "신발"],
}


def _확률값(값):
    """0.3, "1/25" 같은 값을 Fraction으로. "미정" 등 해석 불가면 None."""
    if isinstance(값, bool):
        return None
    if isinstance(값, (int, float)):
        return Fraction(값).limit_denominator()
    if isinstance(값, str):
        try:
            return Fraction(값.strip())
        except (ValueError, ZeroDivisionError):
            return None
    return None


def 골드_굴림(획득골드):
    """ "1~10" -> 1~10 균등, 정수 -> 그 값, "미정"/None/해석 불가 -> 0."""
    if isinstance(획득골드, bool):
        return 0
    if isinstance(획득골드, int):
        return max(0, 획득골드)
    if not isinstance(획득골드, str):
        return 0
    조각 = 획득골드.split("~")
    try:
        숫자들 = [int(x.strip()) for x in 조각]
    except ValueError:
        return 0
    if len(숫자들) == 1:
        return max(0, 숫자들[0])
    if len(숫자들) != 2 or 숫자들[0] > 숫자들[1]:
        return 0
    return max(0, random.randint(숫자들[0], 숫자들[1]))


def _통과(확률):
    return 확률 is not None and random.random() < 확률


def _조건_후보(조건, 장비카탈로그):
    탭들 = 조건_카테고리_탭.get(조건.get("카테고리"), [])
    후보 = []
    for 탭 in 탭들:
        for 이름, 아이템 in 장비카탈로그.get(탭, {}).items():
            if "레어도" in 조건 and 아이템.get("레어도") != 조건["레어도"]:
                continue
            if "티어" in 조건 and 아이템.get("티어") != 조건["티어"]:
                continue
            후보.append(이름)
    return 후보


def _항목_아이템(항목, 장비카탈로그):
    """드랍표 항목 하나에서 아이템 이름 하나를 정한다(없으면 None)."""
    if "아이템이름" in 항목:
        이름 = 항목["아이템이름"]
        return None if 이름 in (None, "미정") else 이름
    조건 = 항목.get("아이템조건")
    if isinstance(조건, dict):
        후보 = _조건_후보(조건, 장비카탈로그)
        return random.choice(후보) if 후보 else None
    return None


def 드랍표_굴림(드랍표, 장비카탈로그):
    """드랍표 본문(monster_drop.py 드랍표_모음의 값) 하나를 굴려 나온
    아이템 이름 리스트를 돌려준다."""
    항목들 = 드랍표.get("아이템", [])
    if 드랍표.get("타입") == "가중형":
        후보 = [(항목, _확률값(항목.get("드랍비율"))) for 항목 in 항목들]
        후보 = [(항목, w) for 항목, w in 후보 if w is not None and w > 0]
        if not 후보:
            return []
        항목 = random.choices(
            [h for h, _ in 후보], weights=[float(w) for _, w in 후보], k=1
        )[0]
        이름 = _항목_아이템(항목, 장비카탈로그)
        return [이름] if 이름 else []
    if 드랍표.get("타입") == "독립형":
        결과 = []
        for 항목 in 항목들:
            if _통과(_확률값(항목.get("드랍확률"))):
                이름 = _항목_아이템(항목, 장비카탈로그)
                if 이름:
                    결과.append(이름)
        return 결과
    return []


def 몬스터_전리품(몬스터원본, 드랍표_모음, 장비카탈로그):
    """몬스터 한 마리의 (골드, [아이템 이름...])."""
    골드 = 골드_굴림(몬스터원본.get("획득골드"))
    아이템들 = []
    for 참조 in 몬스터원본.get("드랍표") or []:
        드랍표 = 드랍표_모음.get(참조.get("이름"))
        if 드랍표 is None:
            continue
        if _통과(_확률값(참조.get("발동확률"))):
            아이템들.extend(드랍표_굴림(드랍표, 장비카탈로그))
    return 골드, 아이템들


def 전리품_판정(몬스터원본목록, 드랍표_모음, 장비카탈로그):
    """쓰러뜨린 몬스터 전부의 전리품. {"골드": 합계, "아이템": [(이름, 개수), ...]}
    - 아이템은 처음 나온 순서대로, 같은 이름은 개수로 묶는다."""
    골드합 = 0
    개수 = {}
    for 원본 in 몬스터원본목록:
        골드, 아이템들 = 몬스터_전리품(원본, 드랍표_모음, 장비카탈로그)
        골드합 += 골드
        for 이름 in 아이템들:
            개수[이름] = 개수.get(이름, 0) + 1
    return {"골드": 골드합, "아이템": list(개수.items())}
