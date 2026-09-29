# =====================
# 메인 시스템 (진입점)
# =====================
# tkinter 루트 창 하나를 만들고 그 위에서 화면(ui_*.py의 tk.Frame
# 서브클래스)들을 갈아 끼우는 진입점. 화면의 실제 로직은 각 ui_*.py가
# 갖고 있다.
#
# 주의(아직 미해결):
# - 몬스터 "칭호" 효과(HP/AC 보정)와 "최대HP"/"AC"의 문자열 수식은
#   combat_system이 아직 평가하지 않는다 - 문자열이면 HP/AC가 1/10으로
#   대체된다.
# - "옵션" 메뉴는 콜백이 연결되어 있지 않다(미구현).
# - ui_fild.py(필드화면)는 현재 게임 흐름에 연결되어 있지 않다.

import tkinter as tk
from tkinter import messagebox

from game.system import character_creation_system as 캐릭터생성
from game.system import character_levelup_system
from game.system import combat_system
from game.system import equipment_system
from game.system import map_system
from game.system import party_system
from game.system import player_system
from game.system import save_system
from game.system import shop_system
from game.system import town_system
from game.system import ui_system

from game.UI import ui_main
from game.UI import ui_town
from game.UI import ui_dungeon
from game.UI import ui_party
from game.UI import ui_party_management
from game.UI import ui_character
from game.UI import ui_player
from game.UI import ui_shop
from game.UI import ui_status
from game.UI import ui_battle
from game.UI import ui_character_creation

from game.data.buff import buff, debuff
from game.data import status_effects
from game.data.monster.monster_tier_01 import 몬스터목록

from game.data.town.town_01A_T01_Elvengard import 마을정보 as _엘븐가드
from game.data.MAP.map_01A_D01_Lorien import 맵정보 as _로리엔
from game.data.MAP.map_01A_D02_Hollow_Lorien import 맵정보 as _로리엔안쪽

from game.data.job_level.job_level_010m_ghost_swordsman import 레벨업테이블 as _귀검사레벨업
from game.data.job_level.job_level_020f_fighter import 레벨업테이블 as _격투가레벨업
from game.data.job_level.job_level_030f_gunner import 레벨업테이블 as _거너레벨업
from game.data.job_level.job_level_040f_mage import 레벨업테이블 as _마법사레벨업
from game.data.job_level.job_level_050f_priest import 레벨업테이블 as _프리스트레벨업

from game.data.ability.job_ability_010m import 특성목록 as _귀검사특성
from game.data.ability.job_ability_020f import 특성목록 as _격투가특성
from game.data.ability.job_ability_030f import 특성목록 as _거너특성
from game.data.ability.job_ability_040f import 특성목록 as _마법사특성
from game.data.ability.job_ability_050f import 특성목록 as _프리스트특성
from game.data.ability.job_ability_0000 import 특성목록 as _공용특성

from game.data.equipment.eq_01_weapon_010 import 귀검사무기목록
from game.data.equipment.eq_01_weapon_020 import 격투가무기목록
from game.data.equipment.eq_01_weapon_030 import 거너무기목록
from game.data.equipment.eq_01_weapon_040 import 마법사무기목록
from game.data.equipment.eq_01_weapon_050 import 프리스트무기목록

from game.data.equipment.eq_02_armor_01_top import 상의목록
from game.data.equipment.eq_02_armor_02_bottom import 하의목록
from game.data.equipment.eq_02_armor_03_shoulder import 어깨목록
from game.data.equipment.eq_02_armor_04_belt import 벨트목록
from game.data.equipment.eq_02_armor_05_shoes import 신발목록
from game.data.equipment.eq_03_accesery_06_necklace import 목걸이목록
from game.data.equipment.eq_03_accesery_07_ring import 반지목록
from game.data.equipment.eq_03_accesery_08_bracelet import 팔찌목록
from game.data.equipment.eq_04_special_09_subequipment import 보조장비목록
from game.data.equipment.eq_04_special_10_magicstone import 마법석목록
from game.data.equipment.eq_04_special_11_earring import 귀걸이목록

from game.data.item.item_potion import 포션_데이터
from game.data.item.item_consumable import 소모품_데이터

from game.data.job_skill.job_skill_0000 import 스킬목록 as _공용스킬
from game.data.job_skill.job_skill_010m_ghost_swordsman import 스킬목록 as _귀검사스킬
from game.data.job_skill.job_skill_020f_fighter import 스킬목록 as _격투가스킬
from game.data.job_skill.job_skill_030f_gunner import 스킬목록 as _거너스킬
from game.data.job_skill.job_skill_040f_mage import 스킬목록 as _마법사스킬
from game.data.job_skill.job_skill_050f_priest import 스킬목록 as _프리스트스킬

from game.data.perks.perks_class_0000 import 퍽목록 as _공용퍽
from game.data.perks.perks_class_010m import 퍽목록 as _귀검사퍽
from game.data.perks.perks_class_020f import 퍽목록 as _격투가퍽
from game.data.perks.perks_class_030f import 퍽목록 as _거너퍽
from game.data.perks.perks_class_040f import 퍽목록 as _마법사퍽
from game.data.perks.perks_class_050f import 퍽목록 as _프리스트퍽


# =====================================================
# 직업별 데이터 레지스트리 (수동 등록)
# =====================================================

_직업_데이터 = {
    "귀검사": {
        "레벨업테이블": _귀검사레벨업,
        "특성모음": _귀검사특성,
        "무기목록": 귀검사무기목록,
        "스킬목록": _귀검사스킬,
        "퍽목록": _귀검사퍽,
    },
    "격투가": {
        "레벨업테이블": _격투가레벨업,
        "특성모음": _격투가특성,
        "무기목록": 격투가무기목록,
        "스킬목록": _격투가스킬,
        "퍽목록": _격투가퍽,
    },
    "거너": {
        "레벨업테이블": _거너레벨업,
        "특성모음": _거너특성,
        "무기목록": 거너무기목록,
        "스킬목록": _거너스킬,
        "퍽목록": _거너퍽,
    },
    "마법사": {
        "레벨업테이블": _마법사레벨업,
        "특성모음": _마법사특성,
        "무기목록": 마법사무기목록,
        "스킬목록": _마법사스킬,
        "퍽목록": _마법사퍽,
    },
    "프리스트": {
        "레벨업테이블": _프리스트레벨업,
        "특성모음": _프리스트특성,
        "무기목록": 프리스트무기목록,
        "스킬목록": _프리스트스킬,
        "퍽목록": _프리스트퍽,
    },
}

_마을_레지스트리 = {
    "town_01A_T01_Elvengard": _엘븐가드,
}
_던전_레지스트리 = {
    "map_01A_D01_Lorien": _로리엔,
    "map_01A_D02_Hollow_Lorien": _로리엔안쪽,
}

# =====================================================
# 플레이어 레벨업 트리거
# =====================================================
# (던전파일명, 좌표) -> 처음 클리어 시 플레이어 레벨을 이 값으로 올린다
# (max() 처리). 레벨 4+ 조건은 미정 - 정해지면 항목만 추가.
_플레이어레벨업_트리거 = {
    ("map_01A_D01_Lorien", (15, 3)): 2,
    ("map_01A_D02_Hollow_Lorien", (15, 3)): 3,
}


def _캐릭터_완성(캐릭터명, 직업):
    """이름/직업으로 _직업_데이터를 찾아
    character_creation_system.캐릭터_생성()으로 레벨 1 캐릭터를
    완성한다."""
    데이터 = _직업_데이터[직업]
    레벨1_항목 = 데이터["레벨업테이블"][1]

    획득특성 = 레벨1_항목["획득"]["획득특성"]
    특성이름들 = [획득특성] if isinstance(획득특성, str) else 획득특성
    특성정의모음 = {이름: 데이터["특성모음"][이름] for 이름 in 특성이름들}

    시작무기데이터 = 데이터["무기목록"][레벨1_항목["시작장비"]]
    주문시전능력치 = 레벨1_항목.get("주문시전능력치")

    return 캐릭터생성.캐릭터_생성(
        캐릭터명, 직업, 레벨1_항목, 특성정의모음,
        시작무기데이터, 주문시전능력치=주문시전능력치,
    )


def _장비데이터모음_생성(파티, 상점카탈로그):
    """캐릭터별 장비 데이터({캐릭터명: {슬롯: 아이템데이터}}). 파티 딕셔너리와
    _상점_카탈로그_생성()으로 만든 상점카탈로그를 받는다(카탈로그는 정적
    데이터라 매번 새로 만들지 않고, _게임흐름이 한 번 만들어 캐싱해둔 것을
    넘겨받는다). 캐릭터 "장착장비"의 이름을 상점 카탈로그(무기는 모든 직업
    무기 합본 - 다른 직업 무기도 착용할 수 있으므로)에서 찾아 실제 데이터로
    바꾼다. 방어구/악세/특수장비도 들어가므로 최종AC_계산 등에 장비 보너스가
    반영된다. 빈 슬롯이나 데이터가 없는 이름은 뺀다."""
    장비카탈로그 = 상점카탈로그["장비"]
    결과 = {}
    for 캐릭터 in 파티["파티원"]:
        슬롯데이터 = {}
        for 슬롯, 이름 in 캐릭터["장착장비"].items():
            if not 이름:
                continue
            아이템 = 장비카탈로그.get(슬롯, {}).get(이름)
            if 아이템 is not None:
                슬롯데이터[슬롯] = 아이템
        결과[캐릭터["캐릭터명"]] = 슬롯데이터
    return 결과


def _상점_카탈로그_생성():
    """상점(shop_system.py)이 쓰는 카탈로그. 무기 탭은 모든 직업 무기를
    합치고, 나머지 부위는 eq_02~04 목록을 그대로 쓴다. 포션/음식/투척
    아이템은 item_potion.py / item_consumable.py 데이터를 쓴다."""
    무기탭 = {}
    for 직업데이터 in _직업_데이터.values():
        무기탭.update(직업데이터["무기목록"])

    장비탭모음 = {
        "무기": 무기탭,
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
    return shop_system.카탈로그_생성(장비탭모음, 포션_데이터, 소모품_데이터)


def _전투용_스킬데이터모음_생성(파티):
    """참가 파티원 직업들의 스킬목록 + 공용스킬(job_skill_0000)을 합쳐
    반환한다."""
    합침 = dict(_공용스킬)
    직업집합 = {캐릭터["직업"] for 캐릭터 in 파티["파티원"]}
    for 직업 in 직업집합:
        합침.update(_직업_데이터[직업]["스킬목록"])
    return 합침


def _마을명으로_마을정보_찾기(마을명):
    for 마을 in town_system.기본_마을목록():
        if 마을["마을명"] == 마을명:
            return 마을
    return None


def _선행조건_만족(캐릭터, 선행조건):
    """선행조건 만족 여부. None=항상 만족, str=해당 특성 보유,
    dict={"특성보유"|"최소능력치": ...}."""
    if 선행조건 is None:
        return True
    if isinstance(선행조건, str):
        return 선행조건 in 캐릭터["보유특성"]
    if isinstance(선행조건, dict):
        if "특성보유" in 선행조건:
            return 선행조건["특성보유"] in 캐릭터["보유특성"]
        if "최소능력치" in 선행조건:
            return all(
                캐릭터.get(스탯, 0) >= 값
                for 스탯, 값 in 선행조건["최소능력치"].items()
            )
    return True


# =====================================================
# 화면 전환 뼈대
# =====================================================

class 앱:
    """Tk 루트 창 + 컨테이너 프레임. 요청 시 현재 화면을 지우고 새
    화면(ui_*.py의 tk.Frame)으로 갈아 끼운다."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("던전앤파이터 텍스트 RPG")
        self.root.geometry("880x640")
        self.컨테이너 = tk.Frame(self.root)
        self.컨테이너.pack(fill="both", expand=True)
        self.현재화면 = None

    def 화면_전환(self, 화면클래스, **kwargs):
        """현재 화면을 없애고 새 화면을 그 자리에 채운다. 화면클래스는
        tk.Frame(부모, **kwargs) 형태로 생성 가능한 클래스여야 한다."""
        if self.현재화면 is not None:
            self.현재화면.destroy()
        self.현재화면 = 화면클래스(self.컨테이너, **kwargs)
        self.현재화면.pack(fill="both", expand=True)

    def 실행(self):
        self.root.mainloop()


class _화면래퍼(tk.Frame):
    """"◀ 메뉴로" 버튼 + 실제 화면(ui_*.py Frame)을 감싸는 래퍼.
    X(취소)/ESC도 메뉴콜백과 같은 동작으로 묶는다."""

    def __init__(self, master, 내부화면클래스, 메뉴콜백, **kwargs):
        super().__init__(master)
        상단 = tk.Frame(self)
        상단.pack(fill="x")
        tk.Button(상단, text="◀ 메뉴로", command=메뉴콜백).pack(side="left", padx=6, pady=6)
        내부 = 내부화면클래스(self, **kwargs)
        내부.pack(fill="both", expand=True)
        ui_system.공통조작키_바인딩(self, 취소콜백=메뉴콜백)


class _불러오기메뉴(tk.Frame):
    """세이브 슬롯을 골라 불러오는 화면."""

    def __init__(self, master, 확인콜백=None, 취소콜백=None):
        super().__init__(master)
        self.확인콜백 = 확인콜백

        tk.Label(self, text="불러오기", font=("", 14, "bold")).pack(pady=16)

        슬롯있음 = False
        for 요약 in save_system.전체_세이브_요약():
            if 요약.get("비어있음"):
                continue
            슬롯있음 = True
            텍스트 = (
                f"{요약['슬롯번호']}번 - {요약['현재마을']} - "
                f"{요약['대표캐릭터명']} 외 {요약['파티인원수']}명 "
                f"({요약['저장시각']})"
            )
            tk.Button(
                self, text=텍스트, width=48,
                command=lambda s=요약["슬롯번호"]: self._선택(s),
            ).pack(pady=4)

        if not 슬롯있음:
            tk.Label(self, text="저장된 게임이 없다.").pack(pady=8)

        if 취소콜백 is not None:
            tk.Button(self, text="취소", command=취소콜백).pack(pady=12)

        ui_system.공통조작키_바인딩(self, 취소콜백=취소콜백)

    def _선택(self, 슬롯번호):
        if self.확인콜백 is not None:
            self.확인콜백(슬롯번호)


class _슬롯목록(tk.Frame):
    """설정메뉴의 저장하기/불러오기 슬롯 목록. 저장 모드는 빈 슬롯도
    선택 가능, 불러오기 모드는 빈 슬롯을 비활성 처리한다."""

    def __init__(self, master, 모드, 확인콜백=None, 취소콜백=None):
        super().__init__(master)
        self.확인콜백 = 확인콜백

        tk.Label(
            self, text=("저장하기" if 모드 == "저장" else "불러오기"),
            font=("", 13, "bold"),
        ).pack(pady=(0, 8))

        슬롯있음 = False
        for 요약 in save_system.전체_세이브_요약():
            비어있음 = 요약.get("비어있음", False)
            if 비어있음:
                텍스트 = f"{요약['슬롯번호']}번 - (비어있음)"
                활성 = (모드 == "저장")
            else:
                슬롯있음 = True
                텍스트 = (
                    f"{요약['슬롯번호']}번 - {요약['현재마을']} - "
                    f"{요약['대표캐릭터명']} 외 {요약['파티인원수']}명 "
                    f"({요약['저장시각']})"
                )
                활성 = True
            tk.Button(
                self, text=텍스트, width=44,
                state="normal" if 활성 else "disabled",
                command=lambda s=요약["슬롯번호"]: self._선택(s),
            ).pack(pady=2)

        if 모드 == "불러오기" and not 슬롯있음:
            tk.Label(self, text="저장된 게임이 없다.").pack(pady=8)

        if 취소콜백 is not None:
            tk.Button(self, text="취소", command=취소콜백).pack(pady=(12, 0))

        ui_system.공통조작키_바인딩(self, 취소콜백=취소콜백)

    def _선택(self, 슬롯번호):
        if self.확인콜백 is not None:
            self.확인콜백(슬롯번호)


class _설정메뉴(tk.Toplevel):
    """ESC로 여는 설정 팝업(계속하기/저장하기/불러오기/메인메뉴). 마을/던전
    화면을 유지한 채 Toplevel로 띄운다(진행 중이던 위치 보존).

    불러오기콜백(슬롯번호), 메인메뉴콜백() 은 확정 시 팝업을 닫고 호출된다.
    """

    def __init__(self, master, 플레이어, 진행도, 불러오기콜백=None, 메인메뉴콜백=None):
        super().__init__(master)
        self.title("설정")
        self.resizable(False, False)
        self.플레이어 = 플레이어
        self.진행도 = 진행도
        self.불러오기콜백 = 불러오기콜백
        self.메인메뉴콜백 = 메인메뉴콜백

        # 모달로 만들어 뒤 화면(마을/던전) 조작을 막는다.
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self._본문틀 = tk.Frame(self)
        self._본문틀.pack(padx=20, pady=16)
        self._메인_화면_구성()

    def _본문_비우기(self):
        for 위젯 in self._본문틀.winfo_children():
            위젯.destroy()

    def _메인_화면_구성(self):
        self._본문_비우기()
        tk.Label(self._본문틀, text="설정", font=("", 14, "bold")).pack(pady=(0, 12))
        tk.Button(
            self._본문틀, text="계속하기", width=16, command=self.destroy,
        ).pack(pady=4)
        tk.Button(
            self._본문틀, text="저장하기", width=16, command=self._저장하기_화면,
        ).pack(pady=4)
        tk.Button(
            self._본문틀, text="불러오기", width=16, command=self._불러오기_화면,
        ).pack(pady=4)
        tk.Button(
            self._본문틀, text="메인메뉴", width=16, command=self._메인메뉴_확인,
        ).pack(pady=4)
        # X/ESC도 계속하기와 동일하게 팝업만 닫는다.
        ui_system.공통조작키_바인딩(self, 취소콜백=self.destroy)

    def _저장하기_화면(self):
        self._본문_비우기()
        _슬롯목록(
            self._본문틀, 모드="저장",
            확인콜백=self._저장_확정, 취소콜백=self._메인_화면_구성,
        ).pack()

    def _저장_확정(self, 슬롯번호):
        save_system.게임_저장(슬롯번호, self.플레이어, self.진행도)
        self._메인_화면_구성()
        tk.Label(
            self._본문틀, text=f"{슬롯번호}번 슬롯에 저장했다.", fg="blue",
        ).pack(pady=(0, 4))

    def _불러오기_화면(self):
        self._본문_비우기()
        _슬롯목록(
            self._본문틀, 모드="불러오기",
            확인콜백=self._불러오기_확정, 취소콜백=self._메인_화면_구성,
        ).pack()

    def _불러오기_확정(self, 슬롯번호):
        self.destroy()
        if self.불러오기콜백 is not None:
            self.불러오기콜백(슬롯번호)

    def _메인메뉴_확인(self):
        나가기확인됨 = messagebox.askyesno(
            "메인메뉴로",
            "저장하지 않은 진행상황은 사라진다. 메인메뉴로 나가겠는가?",
            parent=self,
        )
        if not 나가기확인됨:
            return
        self.destroy()
        if self.메인메뉴콜백 is not None:
            self.메인메뉴콜백()


class _능력치배분_팝업(tk.Toplevel):
    """스탯획득 레벨업/퍽의 능력치 배분 팝업. 약점스탯은 투자 불가
    (character_levelup_system.약점스탯_투자가능). 배분점수를 다 써야
    확인 가능하며, 확인 시 확인콜백({"근력": 1, ...})을 부르고 닫는다.
    """

    _능력치_목록 = ["근력", "민첩", "건강", "지능", "지혜", "매력"]

    def __init__(self, master, 캐릭터, 배분점수, 확인콜백):
        super().__init__(master)
        self.title("능력치 배분")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.캐릭터 = 캐릭터
        self.배분점수 = 배분점수
        self.확인콜백 = 확인콜백
        self.배분 = {이름: 0 for 이름 in self._능력치_목록}
        self.투자가능 = {
            이름: character_levelup_system.약점스탯_투자가능(캐릭터, 이름)
            for 이름 in self._능력치_목록
        }

        tk.Label(self, text=f"능력치 {배분점수}점을 배분한다.").pack(padx=16, pady=(14, 4))
        self.남은점수_라벨 = tk.Label(self, text="")
        self.남은점수_라벨.pack(pady=(0, 8))

        self._행위젯 = {}
        for 이름 in self._능력치_목록:
            행 = tk.Frame(self)
            행.pack(fill="x", padx=16, pady=2)
            tk.Label(행, text=이름, width=6, anchor="w").pack(side="left")
            감소버튼 = tk.Button(행, text="-", width=2, command=lambda n=이름: self._증감(n, -1))
            감소버튼.pack(side="left")
            값라벨 = tk.Label(행, text="0", width=3)
            값라벨.pack(side="left")
            증가버튼 = tk.Button(행, text="+", width=2, command=lambda n=이름: self._증감(n, 1))
            증가버튼.pack(side="left")
            if not self.투자가능[이름]:
                tk.Label(행, text="(약점스탯 - 투자 불가)", fg="gray").pack(side="left", padx=6)
            self._행위젯[이름] = (감소버튼, 값라벨, 증가버튼)

        self.확인_버튼 = tk.Button(self, text="확인", command=self._확인_클릭)
        self.확인_버튼.pack(pady=(8, 14))

        self._갱신()

    def _남은점수(self):
        return self.배분점수 - sum(self.배분.values())

    def _증감(self, 이름, 증감):
        if 증감 > 0:
            if not self.투자가능[이름] or self._남은점수() <= 0:
                return
        else:
            if self.배분[이름] <= 0:
                return
        self.배분[이름] += 증감
        self._갱신()

    def _갱신(self):
        남은점수 = self._남은점수()
        self.남은점수_라벨.config(text=f"남은 점수: {남은점수}")
        for 이름, (감소버튼, 값라벨, 증가버튼) in self._행위젯.items():
            값라벨.config(text=str(self.배분[이름]))
            감소버튼.config(state="normal" if self.배분[이름] > 0 else "disabled")
            증가버튼.config(
                state="normal" if (self.투자가능[이름] and 남은점수 > 0) else "disabled"
            )
        self.확인_버튼.config(state="normal" if 남은점수 == 0 else "disabled")

    def _확인_클릭(self):
        배분결과 = {이름: 값 for 이름, 값 in self.배분.items() if 값 > 0}
        self.destroy()
        self.확인콜백(배분결과)


class _퍽선택_팝업(tk.Toplevel):
    """퍽획득 레벨업 팝업. 공용퍽+클래스퍽 중 선행조건 미충족/이미 보유
    항목은 제외한다. "일반퍽" 분류와 획득스킬=None(훔쳐배우기)은 미지원이라
    제외(character_levelup_system.py 참고, 레벨 4+에서 채울 것).

    확인콜백은 캐릭터_레벨업()의 "퍽획득" 분기 인자(퍽이름/퍽정의/특성정의/
    배분)를 딕셔너리로 받는다.
    """

    def __init__(self, master, 캐릭터, 공용퍽목록, 클래스퍽목록, 확인콜백):
        super().__init__(master)
        self.title("퍽 선택")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.master_창 = master
        self.캐릭터 = 캐릭터
        self.확인콜백 = 확인콜백

        tk.Label(self, text="퍽을 하나 선택한다.", font=("", 11, "bold")).pack(
            padx=16, pady=(14, 8)
        )

        목록틀 = tk.Frame(self)
        목록틀.pack(padx=16, pady=(0, 14))

        전체목록 = list(공용퍽목록.items()) + list(클래스퍽목록.items())
        표시함 = False
        for 퍽이름, 퍽정의 in 전체목록:
            if not self._선택가능(퍽이름, 퍽정의):
                continue
            표시함 = True
            행 = tk.Frame(목록틀)
            행.pack(fill="x", pady=2)
            tk.Button(
                행, text=퍽이름, width=14, anchor="w",
                command=lambda n=퍽이름, d=퍽정의: self._퍽_클릭(n, d),
            ).pack(side="left")
            tk.Label(
                행, text=퍽정의.get("설명", ""), anchor="w", wraplength=320, justify="left",
            ).pack(side="left", padx=6)

        if not 표시함:
            tk.Label(목록틀, text="(지금 고를 수 있는 퍽이 없다)").pack()

    def _선택가능(self, 퍽이름, 퍽정의):
        분류 = 퍽정의.get("분류")
        if 분류 == "일반퍽":
            return False
        if not _선행조건_만족(self.캐릭터, 퍽정의.get("선행조건")):
            return False
        if "획득특성" in 퍽정의:
            return 퍽정의["획득특성"] not in self.캐릭터["보유특성"]
        if 분류 == "스킬획득":
            획득스킬 = 퍽정의.get("획득스킬")
            if 획득스킬 is None:
                return False  # 훔쳐배우기 - 미지원
            return 획득스킬 not in self.캐릭터["보유스킬"]
        return True

    def _퍽_클릭(self, 퍽이름, 퍽정의):
        if 퍽정의.get("분류") == "스탯획득" and "획득스탯포인트" in 퍽정의:
            self.destroy()
            _능력치배분_팝업(
                self.master_창, self.캐릭터, 퍽정의["획득스탯포인트"],
                확인콜백=lambda 배분: self.확인콜백(
                    {"퍽이름": 퍽이름, "퍽정의": 퍽정의, "배분": 배분}
                ),
            )
            return

        특성정의 = None
        if "획득특성" in 퍽정의:
            직업데이터 = _직업_데이터.get(self.캐릭터["직업"], {})
            특성정의 = 직업데이터.get("특성모음", {}).get(퍽정의["획득특성"])
            if 특성정의 is None:
                특성정의 = _공용특성.get(퍽정의["획득특성"])

        self.destroy()
        self.확인콜백({"퍽이름": 퍽이름, "퍽정의": 퍽정의, "특성정의": 특성정의})


# =====================================================
# 메인화면 -> 새로운 시작 / 불러오기
# =====================================================

class _시작흐름:
    """메인화면에서 "새로운 시작"/"불러오기"를 눌렀을 때부터 파티가
    갖춰져 마을 화면으로 들어가기 전까지를 담당한다."""

    def __init__(self, 앱인스턴스):
        self.앱인스턴스 = 앱인스턴스
        self._생성된_캐릭터목록 = []

    def 메인_화면(self):
        self.앱인스턴스.화면_전환(
            ui_main.메인화면,
            새로운시작콜백=self._새로운_시작,
            불러오기콜백=self._불러오기_화면,
        )

    # ---- 새로운 시작: 캐릭터 생성 x4 ----

    def _새로운_시작(self):
        self._생성된_캐릭터목록 = []
        self._다음_캐릭터_생성_화면()

    def _다음_캐릭터_생성_화면(self):
        순번 = len(self._생성된_캐릭터목록) + 1
        self.앱인스턴스.화면_전환(
            ui_character_creation.캐릭터생성화면, 순번=순번,
            확인콜백=self._캐릭터_생성_확인,
            취소콜백=self.메인_화면,
        )

    def _캐릭터_생성_확인(self, 캐릭터명, 직업):
        self._생성된_캐릭터목록.append(_캐릭터_완성(캐릭터명, 직업))

        if len(self._생성된_캐릭터목록) < party_system.파티_최대인원:
            self._다음_캐릭터_생성_화면()
            return

        플레이어 = player_system.빈_플레이어()
        for 캐릭터 in self._생성된_캐릭터목록:
            party_system.파티원_추가(플레이어["파티"], 캐릭터)

        self._게임_시작(플레이어, town_system.새_진행도())

    # ---- 불러오기 ----

    def _불러오기_화면(self):
        self.앱인스턴스.화면_전환(
            _불러오기메뉴, 확인콜백=self._불러오기_확인, 취소콜백=self.메인_화면,
        )

    def _불러오기_확인(self, 슬롯번호):
        플레이어, 진행도 = save_system.게임_불러오기(슬롯번호)
        self._게임_시작(플레이어, 진행도)

    def _게임_시작(self, 플레이어, 진행도):
        게임흐름 = _게임흐름(self.앱인스턴스, 플레이어, 진행도)
        게임흐름.마을_화면()


# =====================================================
# 마을 / 던전 / 전투
# =====================================================

class _게임흐름:
    """파티가 갖춰진 뒤(새로운 시작 또는 불러오기 이후) 실제 게임 진행 -
    마을 ↔ 던전 ↔ 전투, 파티/상태 확인, 파티관리(레벨업)를 담당한다."""

    def __init__(self, 앱인스턴스, 플레이어, 진행도):
        self.앱인스턴스 = 앱인스턴스
        self.플레이어 = 플레이어
        self.진행도 = 진행도
        self.상점카탈로그 = _상점_카탈로그_생성()
        self.장비데이터모음 = _장비데이터모음_생성(플레이어["파티"], self.상점카탈로그)
        equipment_system.장착품_소지품_동기화(플레이어)
        self.던전상태 = None

    # ---------------- 마을 ----------------

    def 마을_화면(self, 마을정보=None):
        if 마을정보 is None:
            마을정보 = _마을명으로_마을정보_찾기(self.진행도["현재마을"])
        self.앱인스턴스.화면_전환(
            ui_town.마을화면, 마을정보=마을정보, 파티=self.플레이어["파티"],
            진행도=self.진행도,
            던전이동콜백=self._던전_이동,
            마을이동콜백=self.마을_화면,
            파티구성콜백=self._파티_화면,
            파티관리콜백=lambda: self._파티관리_화면(self.마을_화면),
            설정메뉴콜백=self._설정메뉴_열기,
            상점콜백=lambda: self._상점_열기(마을정보),
            모험가콜백=self._모험가_화면,
        )

    # ---------------- 상점 ----------------

    def _상점_열기(self, 마을정보):
        """마을의 [상점] 버튼 - 상점 팝업(Toplevel)을 띄운다. 마을 화면은
        그대로 두고, 상점의 판매 목록은 그 마을 정보의 "상점판매목록"
        (아이템 이름 리스트, 없으면 None)을 쓴다."""
        ui_shop.상점팝업(
            self.앱인스턴스.root, self.플레이어, self.상점카탈로그,
            상점판매목록=마을정보.get("상점판매목록"),
        )

    def _파티_화면(self):
        self.앱인스턴스.화면_전환(
            _화면래퍼, 내부화면클래스=ui_party.파티화면,
            메뉴콜백=lambda: self.마을_화면(),
            파티=self.플레이어["파티"], 장비데이터모음=self.장비데이터모음,
            상세보기콜백=self._캐릭터_화면,
        )

    def _캐릭터_화면(self, 캐릭터):
        """파티 화면에서 캐릭터를 누르면 여는 [장비]/[상태] 탭 화면."""
        self.앱인스턴스.화면_전환(
            _화면래퍼, 내부화면클래스=ui_character.캐릭터화면,
            메뉴콜백=self._파티_화면,
            플레이어=self.플레이어, 캐릭터=캐릭터, 카탈로그=self.상점카탈로그,
            상태탭생성=lambda 부모, 대상: ui_status.상태화면(
                부모, 파티원목록=[대상], 장비데이터모음=self.장비데이터모음,
                초기선택=대상,
            ),
            장비변경콜백=self._장비_변경됨,
        )

    def _장비_변경됨(self):
        self.장비데이터모음 = _장비데이터모음_생성(self.플레이어["파티"], self.상점카탈로그)

    def _모험가_화면(self):
        """마을의 [모험가] 버튼 - 마을 화면을 통째로 대체해서 띄운다."""
        self.앱인스턴스.화면_전환(
            _화면래퍼, 내부화면클래스=ui_player.플레이어화면,
            메뉴콜백=lambda: self.마을_화면(),
            플레이어=self.플레이어,
        )

    def _상태_화면(self, 캐릭터=None, 복귀콜백=None):
        # 복귀콜백이 없으면(ui_party.py에서 온 경우) 파티화면으로 복귀.
        self.앱인스턴스.화면_전환(
            _화면래퍼, 내부화면클래스=ui_status.상태화면,
            메뉴콜백=복귀콜백 or self._파티_화면,
            파티원목록=self.플레이어["파티"]["파티원"], 장비데이터모음=self.장비데이터모음,
            초기선택=캐릭터,
        )

    # ---------------- 파티관리(레벨업) ----------------

    def _파티관리_화면(self, 복귀콜백):
        """[파티관리] 화면. 복귀콜백은 나갈 때 돌아갈 곳(마을_화면/
        _던전_화면_열기)."""
        self.앱인스턴스.화면_전환(
            _화면래퍼, 내부화면클래스=ui_party_management.파티관리화면,
            메뉴콜백=복귀콜백,
            파티=self.플레이어["파티"], 플레이어레벨=self.플레이어["레벨"],
            상세보기콜백=lambda 캐릭터: self._상태_화면(
                캐릭터, lambda: self._파티관리_화면(복귀콜백)
            ),
            레벨업콜백=lambda 캐릭터: self._레벨업_시도(캐릭터, 복귀콜백),
        )

    def _레벨업_시도(self, 캐릭터, 복귀콜백):
        """캐릭터를 한 레벨 올린다. 타입이 특성획득/스킬획득/행동획득이면
        바로 적용하고, 스탯획득/퍽획득이면 팝업으로 선택받아 적용한다."""
        직업데이터 = _직업_데이터[캐릭터["직업"]]
        다음레벨 = 캐릭터["레벨"] + 1
        레벨업항목 = 직업데이터["레벨업테이블"].get(다음레벨)
        if 레벨업항목 is None:
            # 아직 그 레벨의 레벨업테이블이 없다 - 무시.
            return

        레벨1_항목 = 직업데이터["레벨업테이블"][1]
        기본체력 = 레벨1_항목["기본체력"]
        레벨당체력증가 = 레벨1_항목["레벨당체력증가"]
        타입 = 레벨업항목["타입"]

        if 타입 == "특성획득":
            character_levelup_system.캐릭터_레벨업(
                캐릭터, 레벨업항목, 기본체력, 레벨당체력증가,
                특성정의모음=직업데이터["특성모음"],
            )
            self._파티관리_화면(복귀콜백)
        elif 타입 in ("스킬획득", "행동획득"):
            character_levelup_system.캐릭터_레벨업(
                캐릭터, 레벨업항목, 기본체력, 레벨당체력증가,
            )
            self._파티관리_화면(복귀콜백)
        elif 타입 == "스탯획득":
            배분점수 = 레벨업항목["획득"]["배분점수"]
            _능력치배분_팝업(
                self.앱인스턴스.root, 캐릭터, 배분점수,
                확인콜백=lambda 배분: self._레벨업_스탯확정(
                    캐릭터, 레벨업항목, 기본체력, 레벨당체력증가, 배분, 복귀콜백,
                ),
            )
        elif 타입 == "퍽획득":
            _퍽선택_팝업(
                self.앱인스턴스.root, 캐릭터,
                _공용퍽, 직업데이터["퍽목록"],
                확인콜백=lambda 선택결과: self._레벨업_퍽확정(
                    캐릭터, 레벨업항목, 기본체력, 레벨당체력증가, 선택결과, 복귀콜백,
                ),
            )

    def _레벨업_스탯확정(self, 캐릭터, 레벨업항목, 기본체력, 레벨당체력증가, 배분, 복귀콜백):
        character_levelup_system.캐릭터_레벨업(
            캐릭터, 레벨업항목, 기본체력, 레벨당체력증가, 배분=배분,
        )
        self._파티관리_화면(복귀콜백)

    def _레벨업_퍽확정(self, 캐릭터, 레벨업항목, 기본체력, 레벨당체력증가, 선택결과, 복귀콜백):
        character_levelup_system.캐릭터_레벨업(
            캐릭터, 레벨업항목, 기본체력, 레벨당체력증가, **선택결과,
        )
        self._파티관리_화면(복귀콜백)

    # ---------------- 설정메뉴 (ESC) ----------------

    def _설정메뉴_열기(self):
        _설정메뉴(
            self.앱인스턴스.root, self.플레이어, self.진행도,
            불러오기콜백=self._설정메뉴_불러오기,
            메인메뉴콜백=self._설정메뉴_메인메뉴,
        )

    def _설정메뉴_불러오기(self, 슬롯번호):
        self.플레이어, self.진행도 = save_system.게임_불러오기(슬롯번호)
        self.장비데이터모음 = _장비데이터모음_생성(self.플레이어["파티"], self.상점카탈로그)
        equipment_system.장착품_소지품_동기화(self.플레이어)
        self.던전상태 = None
        self.마을_화면()

    def _설정메뉴_메인메뉴(self):
        _시작흐름(self.앱인스턴스).메인_화면()

    # ---------------- 던전 ----------------

    def _던전_이동(self, 던전파일명, 시작좌표=None):
        맵정보 = _던전_레지스트리.get(던전파일명)
        if 맵정보 is None:
            # 데이터 없는 맵 - 이동하지 않음.
            if self.던전상태 is not None:
                self._던전_화면_열기()
            else:
                self.마을_화면()
            return

        self.던전상태 = map_system.던전_시작(
            맵정보, 던전파일명, 시작좌표=시작좌표, 진행도=self.진행도,
        )
        self._던전_화면_열기()

    def _던전_화면_열기(self):
        self.앱인스턴스.화면_전환(
            ui_dungeon.던전화면, 던전상태=self.던전상태,
            몬스터조우콜백=self._몬스터_조우,
            오브젝트상호작용콜백=self._오브젝트_상호작용,
            맵이동콜백=self._맵_이동,
            파티관리콜백=lambda: self._파티관리_화면(self._던전_화면_열기),
            설정메뉴콜백=self._설정메뉴_열기,
        )

    def _맵_이동(self, 연결지역):
        연결맵 = 연결지역["연결맵"]
        if 연결맵 in _마을_레지스트리:
            self.마을_화면(_마을_레지스트리[연결맵])
            return
        self._던전_이동(연결맵, 시작좌표=연결지역.get("진입좌표"))

    def _오브젝트_상호작용(self, 위치, 오브젝트):
        """말걸기 오브젝트(보스전투 제외, 현재는 "상자"만) 상호작용. 반환값이
        던전 화면 상태 메시지로 뜬다. 상자 외 타입은 이름/설명만 보여준다."""
        if 오브젝트.get("타입") == "상자":
            return self._상자_상호작용(위치, 오브젝트)
        return f"{오브젝트.get('이름', '알 수 없음')} - {오브젝트.get('설명', '')}"

    def _상자_상호작용(self, 위치, 오브젝트):
        """보물상자를 연다. 이미 열었으면(진행도["클리어한오브젝트"]) 보상을
        다시 주지 않는다. 보상은 현재 골드만 지원."""
        던전파일명 = self.던전상태["던전파일명"]
        if town_system.오브젝트_클리어됨(self.진행도, 던전파일명, 위치):
            return "이미 열어본 상자다."

        보상 = 오브젝트.get("보상", {})
        골드 = 보상.get("골드", 0)
        if 골드:
            player_system.골드_추가(self.플레이어, 골드)
        town_system.오브젝트_클리어_기록(self.진행도, 던전파일명, 위치)

        if 골드:
            return f"보물상자를 열어 {골드}골드를 얻었다!"
        return "보물상자를 열었다."

    # ---------------- 전투 ----------------

    def _몬스터_조우(self, 몬스터항목목록, 위치):
        """몬스터항목목록 원소는 {"이름":.., "칭호":..}. "칭호"가 있으면
        원본 몬스터 데이터를 얕은 복사해 "칭호" 필드만 덮어쓴다(효과 계산은
        아직 미구현 - 모듈 상단 주의 참고)."""
        몬스터원본목록 = []
        for 항목 in 몬스터항목목록:
            원본 = 몬스터목록.get(항목["이름"])
            if 원본 is None:
                # 실제 데이터 없는 몬스터 - 전투로 이어가지 않음.
                self._던전_화면_열기()
                return
            칭호 = 항목.get("칭호")
            if 칭호 is not None:
                원본 = dict(원본, 칭호=칭호)
            몬스터원본목록.append(원본)

        전투상태 = combat_system.전투_시작(
            self.플레이어["파티"], 몬스터원본목록, self.장비데이터모음,
            버프정의모음=buff.버프목록, 디버프정의모음=debuff.디버프목록,
            상태이상정의모음=status_effects.상태이상목록,
        )

        def 종료시콜백(결과):
            if 결과 == "아군승리" and 위치 is not None:
                던전파일명 = self.던전상태["던전파일명"]
                처음클리어 = not town_system.오브젝트_클리어됨(
                    self.진행도, 던전파일명, 위치,
                )

                map_system.오브젝트_클리어_처리(self.던전상태, 위치)
                town_system.오브젝트_클리어_기록(self.진행도, 던전파일명, 위치)
                map_system.해금상태_적용(self.던전상태, self.진행도)

                # 보스 첫 클리어 시 플레이어 레벨 상승(_플레이어레벨업_트리거).
                # 캐릭터 개별 레벨은 [레벨업]으로 직접 올려야 함.
                목표레벨 = _플레이어레벨업_트리거.get((던전파일명, 위치))
                if 처음클리어 and 목표레벨 is not None:
                    self.플레이어["레벨"] = max(self.플레이어["레벨"], 목표레벨)

            self._던전_화면_열기()

        self.앱인스턴스.화면_전환(
            ui_battle.전투화면, 전투상태=전투상태,
            스킬데이터모음=_전투용_스킬데이터모음_생성(self.플레이어["파티"]),
            종료시콜백=종료시콜백,
        )


if __name__ == "__main__":
    앱인스턴스 = 앱()
    _시작흐름(앱인스턴스).메인_화면()
    앱인스턴스.실행()