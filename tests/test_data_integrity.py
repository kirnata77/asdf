"""데이터 무결성 - 데이터(game/data) 안의 수식과 이름 참조가 실제로 읽히는지 검사한다.

런타임은 일부러 관대하다: 평가할 수 없는 수식은 0/기본값으로 바뀌고(combat.participants/monster_actions/
traits, loot_system), 정의 없는 특성 이름은 건너뛴다(traits._특성_목록). "아직 미정인 데이터"를 견디려는
설계지만, 그래서 데이터 오타가 오류 없이 효과 없음이 된다(구조 점검 W-3). 이 파일이 그 안전망이다 - 런타임은
그대로 두고, 데이터가 읽히는지를 테스트에서 엄격하게 확인한다. 의도된 예외는 허용 목록에 이유와 함께 적는다.
허용 목록의 항목이 더는 필요 없어지면(데이터가 고쳐지면) 테스트가 목록에서 지우라고 알려 준다.
"""

import collections
import importlib
import os
import pathlib
import pkgutil
import random
import re
import sys

import pytest

import game.data as 데이터패키지
import gameflow as gf
from game.data.equipment.eq_04_special_11_earring import 귀걸이목록
from game.data.buff.debuff import 디버프목록
from game.data.equipment.eq_04_special_10_magicstone import 마법석목록
from game.data.equipment.eq_03_accessory_06_necklace import 목걸이목록
from game.data.equipment.eq_03_accessory_07_ring import 반지목록
from game.data.buff.buff import 버프목록
from game.data.equipment.eq_02_armor_04_belt import 벨트목록
from game.data.equipment.eq_04_special_09_subequipment import 보조장비목록
from game.data.equipment.eq_02_armor_01_top import 상의목록
from game.data.buff.status_effects import 상태이상목록
from game.data.equipment.eq_02_armor_05_shoes import 신발목록
from game.data.equipment.eq_02_armor_03_shoulder import 어깨목록
from game.data.monster.monster_title import 칭호목록
from game.data.equipment.eq_03_accessory_08_bracelet import 팔찌목록
from game.data.equipment.eq_02_armor_02_bottom import 하의목록
from game.system.combat import formula, resources

루트 = pathlib.Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------- 수식


# 수식이 들어 있는 데이터 키. 키 이름을 목록으로 둔 이유: 문자열 값 중 무엇이 수식인지는
# 키로만 알 수 있다(설명 문구에도 숫자가 있다). 새 수식 키가 생기면 여기에 더한다.
수식_키 = {
    "데미지",
    "무기공격력",
    "난이도",
    "속도",
    "수식",
    "변동값",
    "회복량",
    "최대값",
    "최대HP",
    "AC",
    "공격횟수",
    "회피보너스",
    "임시생명력",
    "이니셔티브보너스",
    "실패시데미지",
    "명중보너스",
    "중첩량",
    "추가피해",
    "휴식당횟수",
    "해제개수",
    "획득골드",
    "최대MP",
    "지속턴",
    "수치",
    "분신수",
    "근력",
    "재굴림",
    "변경",
    "기존",
    "데미지보너스",
    "명중률보너스",
    "속도보너스",
}

# 수식_평가가 모르는 변수지만 호출하는 쪽이 먼저 숫자로 바꿔서 넘기는 것들.
# 새 변수를 여기 더하려면 그 호출 쪽이 실제로 치환하는지 확인한다.
호출쪽_치환 = {
    "중첩수": "2",  # combat/stats.py 버프디버프_수치 - 상태이상 중첩량
    "고블린수": "3",  # combat/traits.py - "집계조건"으로 센 필드의 몬스터 수
}

수식_컨텍스트 = {
    "차수": 2,
    "레벨": 5,
    "보정치": 1,
    "주문시전보정치": 3,
    "스타일성장횟수": 1,
    "귀신보유수": 2,
    "무기공격력": "1d8",
    "추가공격": 1,
    "능력치": {이름: 14 for 이름 in ("근력", "민첩", "건강", "지능", "지혜", "매력")},
}


def _데이터_모듈들():
    for 정보 in pkgutil.walk_packages(데이터패키지.__path__, "game.data."):
        yield importlib.import_module(정보.name)


def _수식_모으기():
    """{(키, 문자열): [모듈이름, ...]} - 수식 키 아래의 숫자/변수가 든 문자열 값."""
    찾음 = collections.defaultdict(set)

    def 걷기(값, 키, 모듈):
        if isinstance(값, dict):
            for k, v in 값.items():
                걷기(v, k if isinstance(k, str) else 키, 모듈)
        elif isinstance(값, (list, tuple)):
            for v in 값:
                걷기(v, 키, 모듈)
        elif (
            isinstance(값, str)
            and 키 in 수식_키
            and re.search(r"\d|차수|보정치|레벨", 값)
        ):
            찾음[(키, 값)].add(모듈)

    for 모듈 in _데이터_모듈들():
        for 이름, 값 in vars(모듈).items():
            if 이름.startswith("__") or isinstance(값, type) or callable(값):
                continue
            if isinstance(값, type(sys)):  # 다른 모듈 참조
                continue
            걷기(값, 이름, 모듈.__name__)
    return 찾음


def test_데이터의_모든_수식이_엄격하게_평가된다():
    수식들 = _수식_모으기()
    # 수집이 깨지면(키 이름이 바뀌는 등) 검사가 조용히 비는 일을 막는다
    assert len(수식들) >= 90, f"수식을 {len(수식들)}개만 찾았다 - 수집 로직을 확인한다"

    실패 = []
    for (키, 값), 모듈들 in sorted(수식들.items()):
        식 = 값
        for 변수, 숫자 in 호출쪽_치환.items():
            식 = 식.replace(변수, 숫자)
        try:
            random.seed(0)
            결과 = formula.수식_평가(식, dict(수식_컨텍스트))
        except Exception as 오류:  # noqa: BLE001 - 어떤 실패든 데이터 문제로 보고한다
            실패.append(
                f"{키}: {값!r} -> {type(오류).__name__}: {오류} ({sorted(모듈들)[0]})"
            )
            continue
        assert isinstance(결과, (int, float)), (키, 값, 결과)
    assert not 실패, (
        "런타임이 조용히 0/기본값으로 바꿀 수식이 있다 - 데이터를 고치거나, 호출 쪽이 먼저 치환하는 "
        "변수라면 호출쪽_치환에 더한다:\n" + "\n".join(실패)
    )


def test_호출쪽_치환_변수는_실제_데이터에서_쓰인다():
    """쓰이지 않는 변수가 목록에 남아 있으면 나중에 오타를 가릴 수 있다."""
    수식들 = _수식_모으기()
    for 변수 in 호출쪽_치환:
        assert any(변수 in 값 for (_, 값) in 수식들), (
            f"{변수}는 데이터에 없다 - 목록에서 지운다"
        )


# ---------------------------------------------------------------- 몬스터

몬스터_필수키 = {
    "몬스터명",
    "이미지",
    "크기",
    "분류",
    "타입",
    "칭호",
    "특성",
    "출현장소",
    "적등급",
    "레벨",
    "차수",
    "역할군",
    "최대HP",
    "AC",
    "근력",
    "민첩",
    "건강",
    "지능",
    "지혜",
    "매력",
    "속도",
    "속도보너스",
    "데미지보너스",
    "명중률보너스",
    "치명타주사위",
    "취약",
    "저항",
    "내성",
    "면역",
    "버프",
    "디버프",
    "상태이상",
    "패턴",
    "획득골드",
    "드랍표",
}
몬스터_선택키 = {"AC보너스"}  # 없으면 0(combat/stats.py가 .get으로 읽는다)
패턴_필수키 = {"이름", "타입", "타겟", "명중률", "효과", "조건부효과", "설명"}

# 몬스터 데이터가 이름은 쓰는데 특성 정의가 아직 없는 종족 특성. 정의가 없으면 그 특성은
# 조용히 건너뛰어진다(traits._특성_목록). 주석(monster_ability.py/gameflow.py)은 공용 특성
# (job_ability_0000.py)에 있다고 하지만 정의한 적이 없다 - known-bugs.md. 정의를 만들면 지운다.
정의_없는_몬스터_특성 = {
    "종족:루가루": {"루가루", "시로가루", "쿠로가루", "정원사 랄", "펜릴"},
    "종족:인간": {"결빙의 케라하", "화염의 비노슈"},
}
# 칭호 칸의 자리표시자(아직 안 정한 값). 칭호목록에 있거나 이 값이면 정상이다.
칭호_자리표시자 = {None, "미정"}


def test_몬스터_데이터는_필수_키와_허용값을_지킨다():
    문제 = []
    for 키, 몬스터 in gf.몬스터목록.items():
        모자람 = 몬스터_필수키 - set(몬스터)
        남음 = set(몬스터) - 몬스터_필수키 - 몬스터_선택키
        if 모자람 or 남음:
            문제.append(f"{키}: 없는 키 {sorted(모자람)} 모르는 키 {sorted(남음)}")
        if 몬스터.get("몬스터명") != 키:
            문제.append(f"{키}: 몬스터명 {몬스터.get('몬스터명')!r}이 목록 키와 다르다")
        if 몬스터.get("크기") not in gf.몬스터_크기_배율:
            문제.append(f"{키}: 크기 {몬스터.get('크기')!r}")
        if 몬스터.get("적등급") not in ("일반", "네임드", "엘리트"):
            문제.append(f"{키}: 적등급 {몬스터.get('적등급')!r}")
        if 몬스터.get("역할군") not in ("딜러", "탱커", "메이지"):
            문제.append(f"{키}: 역할군 {몬스터.get('역할군')!r}")
        이미지 = 몬스터.get("이미지")
        if 이미지 and not (루트 / "game" / "assets" / "monster" / 이미지).is_file():
            문제.append(f"{키}: 그림 파일이 없다 {이미지}")
        if not 몬스터.get("패턴"):
            문제.append(f"{키}: 패턴이 비었다")
        for 번호, 패턴 in (몬스터.get("패턴") or {}).items():
            빠짐 = 패턴_필수키 - set(패턴)
            if 빠짐:
                문제.append(f"{키} 패턴 {번호}: 없는 키 {sorted(빠짐)}")
        칭호 = 몬스터.get("칭호")
        if 칭호 not in 칭호_자리표시자 and 칭호 not in 칭호목록:
            문제.append(f"{키}: 칭호 {칭호!r}의 정의가 없다")
    assert not 문제, "\n".join(문제)


def test_몬스터_특성_이름은_정의가_있다():
    정의 = gf.전투용_몬스터특성정의
    없는 = collections.defaultdict(set)
    for 키, 몬스터 in gf.몬스터목록.items():
        for 이름 in 몬스터.get("특성") or []:
            if 이름 not in 정의:
                없는[이름].add(키)
    assert dict(없는) == 정의_없는_몬스터_특성, (
        "정의 없는 몬스터 특성이 허용 목록과 다르다. 새로 생겼으면 정의를 만들거나 오타를 고치고, "
        "허용 목록의 특성에 정의가 생겼으면 목록에서 지운다:\n" + repr(dict(없는))
    )


def _이름_참조_모으기(값, 결과):
    """데이터에서 버프/상태이상/자원을 이름으로 가리키는 곳을 모은다."""
    if isinstance(값, dict):
        종류 = 값.get("종류")
        if 종류 in (
            "상태이상",
            "자동상태",
            "지속피해",
            "아군버프",
            "버프해제",
            "디버프해제",
        ) and isinstance(값.get("이름"), str):
            결과.append(값["이름"])
        획득 = 값.get("버프획득")
        if isinstance(획득, str):
            결과.append(획득)
        elif isinstance(획득, list):
            결과.extend(이름 for 이름 in 획득 if isinstance(이름, str))
        for v in 값.values():
            _이름_참조_모으기(v, 결과)
    elif isinstance(값, (list, tuple)):
        for v in 값:
            _이름_참조_모으기(v, 결과)


def _이름_풀림(이름):
    """런타임이 이 이름을 풀 수 있는가: 상태이상/버프/디버프/기술효과, 또는 "소환:<이름>"
    (combat.monster_actions._몬스터_소환수_목록이 접두어를 떼어 소환수 목록에서 찾는다)."""
    if 이름 in 상태이상목록 or resources.효과정의_조회(이름)[0] is not None:
        return True
    from game.data.buff import summon_00

    return 이름.startswith("소환:") and 이름[len("소환:") :] in summon_00.소환수목록


def test_스킬과_몬스터_패턴의_버프_이름은_풀린다():
    참조 = []
    for 직업, 정보 in gf.직업_레지스트리.items():
        for 이름, 스킬 in 정보["스킬목록"].items():
            목록 = []
            _이름_참조_모으기(스킬, 목록)
            참조 += [(f"스킬 {직업}/{이름}", n) for n in 목록]
    for 키, 몬스터 in gf.몬스터목록.items():
        목록 = []
        _이름_참조_모으기(몬스터["패턴"], 목록)
        참조 += [(f"몬스터 {키}", n) for n in 목록]
    assert len(참조) >= 60, f"참조를 {len(참조)}개만 찾았다 - 수집 로직을 확인한다"
    못푼 = [f"{곳}: {이름!r}" for 곳, 이름 in 참조 if not _이름_풀림(이름)]
    assert not 못푼, "런타임이 풀지 못하는 버프/상태이상 이름:\n" + "\n".join(못푼)


# ---------------------------------------------------------------- 스킬

스킬_필수키 = {"분류", "타입", "습득방법", "행동", "MP소모", "설명"}


def test_스킬_데이터는_필수_키를_가진다():
    문제 = []
    for 직업, 정보 in gf.직업_레지스트리.items():
        for 이름, 스킬 in 정보["스킬목록"].items():
            빠짐 = 스킬_필수키 - set(스킬)
            if 빠짐:
                문제.append(f"{직업}/{이름}: 없는 키 {sorted(빠짐)}")
    assert not 문제, "\n".join(문제)


@pytest.mark.parametrize(
    "이름,레지스트리",
    [
        ("버프", lambda: 버프목록),
        ("디버프", lambda: 디버프목록),
        ("상태이상", lambda: 상태이상목록),
    ],
)
def test_버프_디버프_상태이상은_필수_키를_가진다(이름, 레지스트리):
    필수 = {"분류", "중첩", "효과", "설명"} | (
        {"타입"} if 이름 != "상태이상" else set()
    )
    문제 = [
        f"{키}: {sorted(필수 - set(값))}"
        for 키, 값 in 레지스트리().items()
        if 필수 - set(값)
    ]
    assert not 문제, "\n".join(문제)


# ---------------------------------------------------------------- 던전/마을/상점


def test_던전_데이터의_좌표와_참조가_맞는다():
    문제 = []
    for 이름, 던전 in gf.던전_레지스트리.items():
        격자 = 던전["지도"]
        너비, 높이 = len(격자[0]), len(격자)

        def 안(좌표):
            return 0 <= 좌표[0] < 너비 and 0 <= 좌표[1] < 높이

        if 던전.get("입장좌표") and not 안(던전["입장좌표"]):
            문제.append(f"{이름}: 입장좌표 {던전['입장좌표']}가 지도 밖")
        for 좌표, 오브젝트 in 던전["오브젝트"].items():
            if not 안(좌표):
                문제.append(f"{이름}: 오브젝트 {좌표}가 지도 밖")
            for 몹 in 오브젝트.get("전투몬스터") or []:
                if 몹["이름"] not in gf.몬스터목록:
                    문제.append(f"{이름}: 보스전 몬스터 {몹['이름']!r} 없음")
        for 좌표, 연결 in 던전["연결지역"].items():
            if not 안(좌표):
                문제.append(f"{이름}: 연결 {좌표}가 지도 밖")
            대상 = 연결["연결맵"]
            if 대상 not in gf.던전_레지스트리 and 대상 not in gf.마을파일_레지스트리:
                문제.append(f"{이름}: 연결맵 {대상!r} 없음")
            elif 연결.get("진입좌표") and 대상 in gf.던전_레지스트리:
                격자2 = gf.던전_레지스트리[대상]["지도"]
                x, y = 연결["진입좌표"]
                if not (0 <= x < len(격자2[0]) and 0 <= y < len(격자2)):
                    문제.append(
                        f"{이름}: {대상}의 진입좌표 {연결['진입좌표']}가 지도 밖"
                    )
        for 그룹 in 던전["인카운트"]["출현그룹"]:
            for 몹, 가중치 in 그룹[
                "출현몬스터"
            ].items():  # 가중치는 상대값(random.choices)이라 합이 1일 필요는 없다
                if 몹 not in gf.몬스터목록:
                    문제.append(f"{이름}: 인카운트 몬스터 {몹!r} 없음")
                if not 가중치 > 0:
                    문제.append(f"{이름}: {몹!r}의 가중치 {가중치}")
    assert not 문제, "\n".join(문제)


def test_마을_데이터와_상점_품목이_맞는다():
    카탈로그 = gf._상점_카탈로그_생성()
    품목 = set()

    def 모으기(값):
        if isinstance(값, dict):
            for 키, v in 값.items():
                품목.add(키)
                모으기(v)

    모으기(카탈로그)
    문제 = []
    for 이름, 마을 in gf.마을파일_레지스트리.items():
        for 던전 in 마을["던전목록"]:
            if 던전 not in gf.던전_레지스트리:
                문제.append(f"{이름}: 던전 {던전!r} 없음")
        조건 = 마을.get("개방조건")
        if 조건 and 조건.get("대상") not in gf.던전_레지스트리:
            문제.append(f"{이름}: 개방조건 대상 {조건.get('대상')!r} 없음")
        if not (루트 / "game" / "assets" / "town" / 마을["배경이미지"]).is_file():
            문제.append(f"{이름}: 배경이미지 {마을['배경이미지']} 없음")
        for 품 in 마을["상점판매목록"]:
            if 품 not in 품목:
                문제.append(f"{이름}: 상점 품목 {품!r}이 카탈로그에 없다")
    assert not 문제, "\n".join(문제)


def test_장비_이름은_목록을_가로질러_겹치지_않는다():
    """같은 이름이 두 목록에 있으면 소지품/상점이 어느 쪽인지 가를 수 없다."""
    목록들 = {
        "상의": 상의목록,
        "하의": 하의목록,
        "어깨": 어깨목록,
        "벨트": 벨트목록,
        "신발": 신발목록,
        "목걸이": 목걸이목록,
        "반지": 반지목록,
        "팔찌": 팔찌목록,
        "보조장비": 보조장비목록,
        "마법석": 마법석목록,
        "귀걸이": 귀걸이목록,
    }
    주인 = collections.defaultdict(list)
    for 이름, 목록 in 목록들.items():
        for 키, 항목 in 목록.items():
            주인[키].append(이름)
            assert 항목.get("이름") == 키, f"{이름}/{키}: 이름 칸 {항목.get('이름')!r}"
    겹침 = {키: v for 키, v in 주인.items() if len(v) > 1}
    assert not 겹침, 겹침


def test_루트_경로는_저장소_최상위다():
    assert os.path.isfile(루트 / "gameflow.py")
