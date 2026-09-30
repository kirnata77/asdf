# =====================
# 공용 부품 - 초상화 경로/초상화 선택 팝업, 버튼·입력칸 크기, 기기 설정 파일,
# 카드 디자인 색상과 둥근상자·게이지·평면버튼
# =====================
# main.py가 game/screens/ 여섯 파일의 화면을 ScreenManager에 등록한다.

import os
import json

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

import gameflow


# =====================================================
# 초상화 시스템 - 서로 완전히 별개인 두 가지
# =====================================================
# 1) "플레이어 초상화" - 던전 지도(던전화면.지도위젯)에 "내 위치"로
#    표시할 이미지. 직업과 무관하게 마을 [모험단] 화면에서 65장 그리드
#    (아래 _초상화_행목록/_초상화선택팝업)에서 직접 골라서 정하고,
#    게임상태 최상위 "선택된초상화" 키 하나에 저장된다(gameflow.
#    초상화_설정/게임상태["선택된초상화"] 참고). 파티원이 여러 명이어도
#    공용 값 하나뿐이다.
# 2) "캐릭터 초상화" - 모험단화면의 파티원 목록, 전투화면의 아군 그래픽
#    박스에 쓰는, 캐릭터 개인별 초상화. 직업으로 앞자리가 자동 정해지고
#    (gameflow.초상화_코드 참고) 성별만 캐릭터별로 토글한다 - 65장
#    그리드에서 고르지 않는다.
#
# 둘 다 파일명 규칙(asset_sd_character_{코드}.webp)과 아래
# _캐릭터이미지_경로()를 함께 쓴다.
_초상화_접두사 = "asset_sd_character_"

# "플레이어 초상화" 그리드용 - 실제 파일 목록(game/assets/character/
# 전체 65장) 그대로 파일명 순서대로
# 5칸씩 끊은 것뿐이다. 직업과는 아무 관계가 없다(그래서 63장이 아니라
# 65장이 정확히 13행으로 나눠떨어져 빈 칸이 없다).
_초상화_행목록 = [
    ("001f", "001m", "011f", "011m", "012f"),
    ("012m", "013f", "013m", "014f", "014m"),
    ("015f", "015m", "021f", "021m", "022f"),
    ("022m", "023f", "023m", "024f", "024m"),
    ("031f", "031m", "032f", "032m", "033f"),
    ("033m", "034f", "034m", "035m", "041f"),
    ("041m", "042f", "042m", "043f", "043m"),
    ("044f", "044m", "045f", "045m", "051f"),
    ("051m", "052f", "052m", "053f", "053m"),
    ("054f", "054m", "061f", "062f", "063f"),
    ("064f", "071m", "072m", "073m", "074m"),
    ("081f", "082f", "083f", "084f", "091m"),
    ("092m", "093m", "094m", "101f", "102f"),
]

_기본_초상화_코드 = "001m"


def _이미지_원경로(코드):
    파일명 = f"{_초상화_접두사}{코드}.webp"
    # 이 파일은 game/screens/ 안에 있으므로 한 단계 위(game/)의 assets를 쓴다.
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets",
        "character",
        파일명,
    )


def _이미지_존재(코드):
    return os.path.isfile(_이미지_원경로(코드))


def _캐릭터이미지_경로(코드):
    """코드(예: "020f")에 대응하는 SD 캐릭터 이미지의 전체 경로를
    돌려준다. 그 코드의 실제 파일이 아직 없으면(예: 직업 기반 비전직
    코드는 "분류번호"만 정해져 있고 원화가 없는 경우가 있음) 같은
    계열(앞 2자리)·같은 성별로 실제 존재하는 파일 중 가장 앞 순번으로
    대신 보여주고, 그마저 없으면 공용 기본 초상화(001)로 대체한다."""
    if _이미지_존재(코드):
        return _이미지_원경로(코드)
    계열, 성별 = 코드[:2], 코드[-1]
    for 순번 in "123456789":
        대체코드 = f"{계열}{순번}{성별}"
        if _이미지_존재(대체코드):
            return _이미지_원경로(대체코드)
    return _이미지_원경로(f"{_기본_초상화_코드[:-1]}{성별}")


def _에셋_경로(폴더, 파일명):
    """game/assets/{폴더}/{파일명}의 전체 경로를 돌려준다. 파일명이 없거나
    "미정"이거나 실제 파일이 없으면 None. 던전 타일(dungeon), 몬스터
    이미지(monster), 마을 배경(town)에 쓴다."""
    if not 파일명 or 파일명 == "미정":
        return None
    경로 = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets",
        폴더,
        파일명,
    )
    return 경로 if os.path.isfile(경로) else None


def _도트_필터(이미지위젯):
    """도트 이미지를 크게 늘려도 번지지 않게 텍스처 확대 필터를
    nearest로 둔다(텍스처가 나중에 로드돼도 적용되게 bind까지 건다)."""

    def 적용(inst, 텍스처):
        if 텍스처 is not None:
            텍스처.mag_filter = "nearest"

    이미지위젯.bind(texture=적용)
    적용(이미지위젯, 이미지위젯.texture)


class _이미지버튼(ButtonBehavior, Image):
    """터치 가능한 이미지 - "플레이어 초상화" 그리드 팝업 썸네일,
    모험단 프로필의 캐릭터별 성별 토글, 전투화면 그래픽 박스에 쓴다."""

    pass


class _초상화선택팝업(Popup):
    """ "플레이어 초상화"(던전 지도 표시용, 직업과 무관)를 65장 그리드
    에서 고르는 팝업."""

    def __init__(self, 현재선택, 선택콜백, **kwargs):
        super().__init__(title="플레이어 초상화 선택", size_hint=(0.95, 0.9), **kwargs)
        self._선택콜백 = 선택콜백

        스크롤 = ScrollView()
        격자 = GridLayout(cols=5, size_hint_y=None, spacing=4, padding=4)
        격자.bind(minimum_height=격자.setter("height"))

        for 행 in _초상화_행목록:
            for 코드 in 행:
                if 코드 is None:
                    격자.add_widget(Widget(size_hint_y=None, height=dp(90)))
                    continue
                버튼 = _이미지버튼(
                    source=_캐릭터이미지_경로(코드),
                    size_hint_y=None,
                    height=dp(90),
                    allow_stretch=True,
                )
                버튼.bind(on_release=lambda inst, c=코드: self._선택(c))
                격자.add_widget(버튼)

        스크롤.add_widget(격자)
        self.content = 스크롤

    def _선택(self, 코드):
        self._선택콜백(코드)
        self.dismiss()


# =====================================================
# 메인메뉴/파티생성 화면에서 쓰는 버튼·입력칸 크기를 여기 상수로 모아둔다.
# (사용자 요청 - 상자는 세로로 작게, 글자는 상자에 맞게 크게, 두 화면의
# 버튼/입력칸이 서로 다른 크기로 따로 놀지 않게 하나로 통일) 값만 바꾸면
# 아래에서 이 상수를 쓰는 모든 버튼/입력칸에 그대로 반영된다.
_버튼_높이 = dp(56)
_버튼_폰트크기 = 44
_입력_높이 = dp(52)
_입력_폰트크기 = 36

# -----------------------------------------------------
# 기기 설정 파일 - 세이브와 별개인 앱 설정. 지금은 "반응자동"
# (반응 자동 사용) 하나. 앱 데이터 폴더의 설정.json에 저장한다.
# -----------------------------------------------------


def _설정_경로():
    앱 = App.get_running_app()
    폴더 = getattr(앱, "user_data_dir", None) or os.path.dirname(
        os.path.abspath(__file__)
    )
    return os.path.join(폴더, "설정.json")


def 설정_불러오기():
    try:
        with open(_설정_경로(), encoding="utf-8") as 파일:
            설정 = json.load(파일)
    except Exception:
        설정 = {}
    gameflow.반응_자동_설정(설정.get("반응자동", False))
    return 설정


def 설정_저장(키, 값):
    설정 = {}
    try:
        with open(_설정_경로(), encoding="utf-8") as 파일:
            설정 = json.load(파일)
    except Exception:
        pass
    설정[키] = 값
    try:
        with open(_설정_경로(), "w", encoding="utf-8") as 파일:
            json.dump(설정, 파일, ensure_ascii=False)
    except Exception:
        pass


# 파티 화면 디자인: 파티원마다 넓은 카드 한 장 - 왼쪽 초상화,
# 가운데 이름·직업·레벨 / HP·MP 게이지 / 능력치 3×2, 오른쪽 [레벨업][상세보기].
_카드_배경색 = (0.13, 0.14, 0.17, 1)
_카드_쓰러짐색 = (0.18, 0.11, 0.11, 1)
_강조색 = (0.22, 0.56, 0.86, 1)
_흐린글자색 = (0.62, 0.65, 0.7, 1)
_HP색 = (0.85, 0.27, 0.27, 1)
_MP색 = (0.27, 0.5, 0.9, 1)
_게이지_바탕색 = (0.24, 0.25, 0.29, 1)


class _둥근상자(BoxLayout):
    """둥근 모서리 배경을 칠한 BoxLayout."""

    def __init__(self, 배경색, 반지름=12, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._색 = Color(*배경색)
            self._배경 = RoundedRectangle(radius=[dp(반지름)])
        self.bind(pos=self._다시그리기, size=self._다시그리기)

    def _다시그리기(self, *args):
        self._배경.pos = self.pos
        self._배경.size = self.size


class _게이지(Widget):
    """HP/MP 막대 - 바탕 막대 위에 현재/최대 비율만큼 색을 채우고 글자를 얹는다."""

    def __init__(self, 이름, 현재, 최대, 색, **kwargs):
        super().__init__(**kwargs)
        self._비율 = max(0.0, min(1.0, 현재 / 최대)) if 최대 else 0.0
        with self.canvas.before:
            Color(*_게이지_바탕색)
            self._바탕 = RoundedRectangle(radius=[dp(4)])
            Color(*색)
            self._채움 = RoundedRectangle(radius=[dp(4)])
        self._글 = Label(text=f"{이름}  {현재} / {최대}", font_size="12sp", bold=True)
        self.add_widget(self._글)
        self.bind(pos=self._다시그리기, size=self._다시그리기)

    def _다시그리기(self, *args):
        self._바탕.pos = self.pos
        self._바탕.size = self.size
        self._채움.pos = self.pos
        self._채움.size = (self.width * self._비율, self.height)
        self._글.pos = self.pos
        self._글.size = self.size


def _평면버튼(글, 색, **kwargs):
    """기본 회색 입체 배경 대신 단색 배경 버튼."""
    return Button(
        text=글,
        background_normal="",
        background_disabled_normal="",
        background_color=색,
        **kwargs,
    )


# =====================================================
# 핸드폰 [뒤로] 키
# =====================================================
# 안드로이드 [뒤로] 키는 Kivy에 키코드 27로 들어오고, 그대로 두면 앱이
# 최소화된다. 대신 화면/팝업의 취소·닫기·뒤로 버튼을 누른 것과 같게
# 동작시키고, 그런 버튼이 없는 곳(메인메뉴, 마을, 던전, 전투, 꼭 골라야
# 하는 팝업)에서는 아무 일도 하지 않는다. 대상 버튼은 만들 때
# 뒤로키_버튼()으로 표시해 둔다. main.py가 창의 on_keyboard에 연결한다.


def 뒤로키_버튼(버튼):
    """[뒤로] 키를 누르면 이 버튼을 누른 것과 같게 동작하도록 표시한다."""
    버튼.뒤로키 = True
    return 버튼


def _뒤로키_버튼_찾기(위젯):
    for 자식 in 위젯.walk(restrict=True):
        if getattr(자식, "뒤로키", False) and not 자식.disabled:
            return 자식
    return None


def 뒤로키_처리(창, 키, *args):
    if 키 != 27:
        return False
    맨위 = 창.children[0] if 창.children else None
    if isinstance(맨위, DropDown):
        맨위.dismiss()
    elif isinstance(맨위, ModalView):
        # 표시된 버튼이 없는 팝업은, 바깥을 눌러 닫을 수 있는 것만 닫는다
        # (auto_dismiss=False이면서 취소 버튼도 없는 팝업은 꼭 골라야 하는 창).
        버튼 = _뒤로키_버튼_찾기(맨위)
        if 버튼 is not None:
            버튼.trigger_action(duration=0)
        elif 맨위.auto_dismiss:
            맨위.dismiss()
    else:
        버튼 = _뒤로키_버튼_찾기(App.get_running_app().root.current_screen)
        if 버튼 is not None:
            버튼.trigger_action(duration=0)
    return True
