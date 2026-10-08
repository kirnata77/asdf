# =====================
# 메뉴 화면 - 메인메뉴, 파티 생성, 불러오기/저장 목록, 옵션
# =====================
# main.py가 game/screens/ 여섯 파일의 화면을 ScreenManager에 등록한다.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.metrics import dp

import gameflow
from game.screens.screens_common import (
    _강조색,
    _둥근상자,
    _버튼_높이,
    _버튼_폰트크기,
    _카드_배경색,
    _캐릭터이미지_경로,
    _평면버튼,
    _흐린글자색,
    설정_불러오기,
    설정_저장,
    뒤로키_버튼,
)


# =====================================================
# 0. 메인 메뉴


class 메인메뉴화면(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        레이아웃 = BoxLayout(orientation="vertical", padding=24, spacing=14)

        레이아웃.add_widget(
            Label(
                text="던전앤파이터 모바일 프로토타입",
                font_size="28sp",
                size_hint=(1, 0.3),
            )
        )

        버튼틀 = BoxLayout(orientation="vertical", size_hint=(1, 0.7), spacing=10)

        새시작버튼 = Button(
            text="새로운 시작",
            font_size=_버튼_폰트크기,
            size_hint_y=None,
            height=_버튼_높이,
        )
        새시작버튼.bind(
            on_release=lambda *_: setattr(self.manager, "current", "파티생성")
        )
        버튼틀.add_widget(새시작버튼)

        self.불러오기버튼 = Button(
            text="불러오기",
            font_size=_버튼_폰트크기,
            size_hint_y=None,
            height=_버튼_높이,
        )
        self.불러오기버튼.bind(on_release=self._불러오기)
        버튼틀.add_widget(self.불러오기버튼)

        옵션버튼 = Button(
            text="옵션",
            font_size=_버튼_폰트크기,
            size_hint_y=None,
            height=_버튼_높이,
        )
        옵션버튼.bind(on_release=lambda *_: setattr(self.manager, "current", "옵션"))
        버튼틀.add_widget(옵션버튼)

        종료버튼 = Button(
            text="게임 종료",
            font_size=_버튼_폰트크기,
            size_hint_y=None,
            height=_버튼_높이,
        )
        종료버튼.bind(on_release=lambda *_: App.get_running_app().stop())
        버튼틀.add_widget(종료버튼)

        레이아웃.add_widget(버튼틀)
        self.add_widget(레이아웃)

    def on_pre_enter(self, *args):
        # 손상된 슬롯(백업도 못 읽음)은 불러올 수 없으므로 세지 않는다
        저장된_슬롯_있음 = any(
            not 요약.get("비어있음") and not 요약.get("손상")
            for 요약 in gameflow.전체_세이브_요약()
        )
        self.불러오기버튼.disabled = not 저장된_슬롯_있음

    def _불러오기(self, *args):
        self.manager.current = "불러오기목록"


# =====================================================
# 1. 파티 생성 화면 (최대 4인)
# =====================================================

# 파티 화면(파티관리화면)과 같은 카드 디자인: 파티원 칸마다 둥근
# 카드 - 왼쪽 직업 초상화, 가운데 이름 입력·직업 선택·그 직업의 시작
# HP/MP/능력치 미리보기, 오른쪽 참여 토글(1번은 필수). 참여하지 않는 칸은
# 흐리게 표시하고 입력을 막는다.


class 파티생성화면(Screen):
    _능력치_목록 = ["근력", "민첩", "건강", "지능", "지혜", "매력"]
    # 처음 열었을 때 칸마다 고른 직업 - 네 칸 모두 참여 상태로 시작한다
    _기본_직업 = ["귀검사", "격투가", "거너", "마법사"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.슬롯목록 = []
        self._미리보기_캐시 = {}

        루트 = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        머리 = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(64))
        제목 = Label(
            text="파티 구성",
            font_size="26sp",
            bold=True,
            halign="left",
            valign="bottom",
        )
        제목.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        머리.add_widget(제목)
        부제 = Label(
            text="1~4명 · 이름을 비워두면 직업 이름으로 시작합니다",
            font_size="13sp",
            color=_흐린글자색,
            halign="left",
            valign="top",
        )
        부제.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        머리.add_widget(부제)
        루트.add_widget(머리)

        목록틀 = BoxLayout(orientation="vertical", spacing=dp(10))
        for i in range(4):
            목록틀.add_widget(self._카드_생성(i))
        루트.add_widget(목록틀)

        self.안내라벨 = Label(
            text="",
            size_hint=(1, None),
            height=dp(28),
            font_size="13sp",
            color=_흐린글자색,
        )
        루트.add_widget(self.안내라벨)

        버튼줄 = BoxLayout(
            orientation="horizontal", spacing=dp(10), size_hint=(1, None), height=dp(56)
        )
        뒤로버튼 = _평면버튼(
            "뒤로", (0.3, 0.31, 0.35, 1), font_size="16sp", size_hint=(0.35, 1)
        )
        뒤로키_버튼(뒤로버튼)
        뒤로버튼.bind(
            on_release=lambda *_: setattr(self.manager, "current", "메인메뉴")
        )
        버튼줄.add_widget(뒤로버튼)
        시작버튼 = _평면버튼(
            "모험 시작", _강조색, font_size="16sp", bold=True, size_hint=(0.65, 1)
        )
        시작버튼.bind(on_release=self._시작)
        버튼줄.add_widget(시작버튼)
        루트.add_widget(버튼줄)
        self.add_widget(루트)

        for 슬롯 in self.슬롯목록:
            self._카드_갱신(슬롯)

    def _미리보기(self, 직업):
        """그 직업으로 새로 만든 캐릭터(시작 HP/MP/능력치 미리보기용)."""
        if 직업 not in self._미리보기_캐시:
            self._미리보기_캐시[직업] = gameflow.캐릭터_생성("", 직업)
        return self._미리보기_캐시[직업]

    def _카드_생성(self, i):
        카드 = _둥근상자(
            _카드_배경색, orientation="horizontal", padding=dp(10), spacing=dp(10)
        )
        슬롯 = {"번호": i, "카드": 카드}

        초상틀 = _둥근상자(
            (0.2, 0.21, 0.25, 1), 반지름=10, size_hint=(0.24, 1), padding=dp(4)
        )
        슬롯["초상"] = Image(allow_stretch=True, keep_ratio=True)
        초상틀.add_widget(슬롯["초상"])
        카드.add_widget(초상틀)

        가운데 = BoxLayout(orientation="vertical", size_hint=(0.54, 1), spacing=dp(5))
        슬롯["가운데"] = 가운데
        번호라벨 = Label(
            text=f"[b]{i + 1}번 파티원[/b]"
            + ("  [size=12sp][color=9ea6b3]필수[/color][/size]" if i == 0 else ""),
            markup=True,
            font_size="15sp",
            halign="left",
            valign="middle",
            size_hint=(1, 0.2),
        )
        번호라벨.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        가운데.add_widget(번호라벨)

        입력줄 = BoxLayout(orientation="horizontal", spacing=dp(6), size_hint=(1, 0.3))
        슬롯["이름입력"] = TextInput(
            text="",
            hint_text=gameflow.캐릭터명_안내,
            multiline=False,
            font_size="15sp",
            background_normal="",
            background_active="",
            background_disabled_normal="",
            background_color=(0.2, 0.21, 0.25, 1),
            foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.5, 0.52, 0.57, 1),
            cursor_color=(1, 1, 1, 1),
            padding=(dp(6), 0),
            size_hint=(0.6, 1),
        )
        # 칸 높이가 글자 한 줄보다 크게 남지 않아서, 위아래 여백을 고정값으로
        # 주면 글자가 잘린다. 남는 높이를 위아래로 나눠 글자를 가운데 둔다.
        슬롯["이름입력"].bind(
            height=lambda inst, h: setattr(
                inst, "padding", (dp(6), max(0, (h - inst.line_height) / 2), dp(6), 0)
            ),
            # 한글 6자 / 영문 12자(섞으면 영문 2자 = 한글 1자)를 넘으면 자른다
            text=lambda inst, 값: (
                setattr(inst, "text", gameflow.이름_자르기(값))
                if gameflow.이름_폭(값) > gameflow.캐릭터명_최대폭
                else None
            ),
        )
        입력줄.add_widget(슬롯["이름입력"])
        슬롯["직업스피너"] = Spinner(
            text=self._기본_직업[i],
            values=gameflow.직업목록,
            font_size="15sp",
            background_normal="",
            background_disabled_normal="",
            background_color=(0.3, 0.31, 0.35, 1),
            size_hint=(0.4, 1),
        )
        슬롯["직업스피너"].bind(text=lambda inst, 값, 슬=슬롯: self._카드_갱신(슬))
        입력줄.add_widget(슬롯["직업스피너"])
        가운데.add_widget(입력줄)

        슬롯["자원라벨"] = Label(
            text="",
            markup=True,
            font_size="12sp",
            halign="left",
            valign="middle",
            size_hint=(1, 0.14),
        )
        슬롯["자원라벨"].bind(size=lambda inst, size: setattr(inst, "text_size", size))
        가운데.add_widget(슬롯["자원라벨"])

        능력치판 = GridLayout(cols=3, size_hint=(1, 0.36))
        슬롯["능력치칸"] = {}
        for 이름 in self._능력치_목록:
            칸 = Label(
                text="", markup=True, font_size="12sp", halign="left", valign="middle"
            )
            칸.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            능력치판.add_widget(칸)
            슬롯["능력치칸"][이름] = 칸
        가운데.add_widget(능력치판)
        카드.add_widget(가운데)

        오른쪽 = BoxLayout(orientation="vertical", size_hint=(0.22, 1))
        if i == 0:
            슬롯["참여토글"] = None
            오른쪽.add_widget(
                _평면버튼(
                    "참여",
                    _강조색,
                    font_size="14sp",
                    bold=True,
                    disabled=True,
                    disabled_color=(1, 1, 1, 1),
                )
            )
        else:
            토글 = ToggleButton(
                text="참여",
                state="down",
                font_size="14sp",
                background_normal="",
                background_down="",
                background_color=(0.2, 0.21, 0.25, 1),
            )
            토글.bind(state=lambda inst, 값, 슬=슬롯: self._카드_갱신(슬))
            슬롯["참여토글"] = 토글
            오른쪽.add_widget(토글)
        카드.add_widget(오른쪽)

        self.슬롯목록.append(슬롯)
        return 카드

    def _카드_갱신(self, 슬롯):
        """직업 미리보기와 참여 여부(흐림/입력 막기)를 카드에 반영한다."""
        토글 = 슬롯.get("참여토글")
        if "능력치칸" not in 슬롯:
            return  # 카드 생성 도중(아직 위젯이 다 없음)
        참여 = 토글 is None or 토글.state == "down"
        if 토글 is not None:
            토글.text = "참여" if 참여 else "미참여"
            토글.background_color = _강조색 if 참여 else (0.2, 0.21, 0.25, 1)
            토글.bold = 참여
        직업 = 슬롯["직업스피너"].text
        미리 = self._미리보기(직업)
        슬롯["초상"].source = _캐릭터이미지_경로(gameflow.초상화_코드(미리))
        슬롯["초상"].color = (1, 1, 1, 1) if 참여 else (0.35, 0.35, 0.35, 1)
        슬롯["자원라벨"].text = (
            f"[color=e05555]HP {미리['기본최대HP']}[/color]    "
            f"[color=6fa0ff]MP {미리['기본최대MP']}[/color]"
        )
        for 이름, 칸 in 슬롯["능력치칸"].items():
            칸.text = f"[color=9ea6b3]{이름}[/color] {미리[이름]}"
        슬롯["이름입력"].disabled = not 참여
        슬롯["직업스피너"].disabled = not 참여
        슬롯["가운데"].opacity = 1 if 참여 else 0.45

    def _시작(self, *args):
        파티구성 = []
        for i, 슬롯 in enumerate(self.슬롯목록):
            if i > 0 and 슬롯["참여토글"].state != "down":
                continue
            파티구성.append((슬롯["이름입력"].text, 슬롯["직업스피너"].text))

        앱 = App.get_running_app()
        try:
            앱.게임상태 = gameflow.새_게임_시작(파티구성)
        except ValueError as 오류:  # 이름 중복 - 시작하지 않고 알려 준다
            self.안내라벨.text = str(오류)
            return
        self.manager.get_screen("마을").갱신()
        self.manager.current = "마을"


# =====================================================
# 2. 불러오기 / 저장 슬롯 목록 (공용 레이아웃, 동작만 다름)
# =====================================================


class _슬롯목록화면(Screen):
    """세이브 슬롯 목록을 보여주는 화면의 공용 뼈대. 불러오기목록화면
    (선택 시 게임을 불러온다)과 저장목록화면(선택 시 현재 게임을
    저장한다)이 이 클래스를 상속해 버튼 동작만 다르게 정의한다."""

    제목 = "세이브 슬롯"
    버튼글자 = "선택"
    돌아갈화면 = "메인메뉴"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.슬롯행목록 = []

        루트 = BoxLayout(orientation="vertical", padding=16, spacing=10)
        루트.add_widget(Label(text=self.제목, font_size="24sp", size_hint=(1, 0.12)))

        self.목록틀 = BoxLayout(orientation="vertical", size_hint=(1, 0.68), spacing=8)
        루트.add_widget(self.목록틀)

        self.안내라벨 = Label(text="", size_hint=(1, 0.1))
        루트.add_widget(self.안내라벨)

        뒤로버튼 = Button(text="뒤로", size_hint=(1, 0.1))
        뒤로키_버튼(뒤로버튼)
        뒤로버튼.bind(
            on_release=lambda *_: setattr(self.manager, "current", self.돌아갈화면)
        )
        루트.add_widget(뒤로버튼)

        self.add_widget(루트)

    def on_pre_enter(self, *args):
        self.갱신()

    def 갱신(self):
        self.목록틀.clear_widgets()
        for 요약 in gameflow.전체_세이브_요약():
            줄 = BoxLayout(
                orientation="horizontal", size_hint=(1, None), height=dp(56), spacing=8
            )

            if 요약.get("비어있음"):
                설명 = f"{요약['슬롯번호']}번 슬롯 - (비어 있음)"
            elif 요약.get("새버전"):
                설명 = f"{요약['슬롯번호']}번 슬롯 - (더 새로운 버전의 세이브)"
            elif 요약.get("손상"):
                설명 = f"{요약['슬롯번호']}번 슬롯 - (손상됨, 불러올 수 없음)"
            else:
                표시 = (
                    " [백업]" if 요약.get("복구본") else ""
                )  # 길어서 잘리는 줄 끝 말고 앞에 둔다
                설명 = (
                    f"{요약['슬롯번호']}번 슬롯{표시} - {요약['대표캐릭터명']} 외 "
                    f"{요약['파티인원수']}명 / {요약['현재마을']} / {요약['저장시각']}"
                )
            줄.add_widget(Label(text=설명, font_size="16sp", halign="left"))

            버튼 = Button(text=self.버튼글자, size_hint=(0.28, 1))
            버튼.disabled = self._비활성(요약)
            버튼.bind(on_release=lambda inst, s=요약["슬롯번호"]: self._선택(s))
            줄.add_widget(버튼)

            self.목록틀.add_widget(줄)

    def _비활성(self, 요약):
        return False

    def _선택(self, 슬롯번호):
        raise NotImplementedError


class 불러오기목록화면(_슬롯목록화면):
    제목 = "불러오기"
    버튼글자 = "불러오기"
    돌아갈화면 = "메인메뉴"

    def _비활성(self, 요약):
        return bool(요약.get("비어있음") or 요약.get("손상"))

    def _선택(self, 슬롯번호):
        앱 = App.get_running_app()
        try:
            앱.게임상태 = gameflow.게임_불러오기(슬롯번호)
        except (FileNotFoundError, gameflow.세이브_손상오류) as 오류:
            self.안내라벨.text = str(오류)
            return
        self.manager.get_screen("마을").갱신()
        self.manager.current = "마을"


class 저장목록화면(_슬롯목록화면):
    제목 = "저장하기"
    버튼글자 = "저장"
    돌아갈화면 = "마을"

    def _선택(self, 슬롯번호):
        앱 = App.get_running_app()
        if 앱.게임상태 is None:
            return
        gameflow.게임_저장(앱.게임상태, 슬롯번호)
        self.안내라벨.text = f"{슬롯번호}번 슬롯에 저장했습니다."
        self.갱신()


# =====================================================
# 3. 옵션 (반응 자동 사용 - 설정 저장은 screens_common)
# =====================================================


class 옵션화면(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        설정 = 설정_불러오기()
        루트 = BoxLayout(orientation="vertical", padding=24, spacing=14)
        루트.add_widget(
            Label(
                text="옵션",
                font_size="26sp",
                size_hint=(1, 0.2),
            )
        )
        설정틀 = BoxLayout(orientation="vertical", size_hint=(1, 0.6), spacing=8)
        self.반응자동버튼 = ToggleButton(
            size_hint=(1, None),
            height=dp(56),
            state="down" if 설정.get("반응자동") else "normal",
        )
        self.반응자동버튼.bind(state=self._반응자동_변경)
        설정틀.add_widget(self.반응자동버튼)
        설명 = Label(
            text="끄면 전투 중 반응행동을 쓰는 반응(회피/반격/피해감소 등)마다 "
            "사용할지 묻는 창이 뜹니다. 켜면 묻지 않고 자동으로 사용합니다.",
            font_size="13sp",
            size_hint=(1, None),
            height=dp(64),
            halign="left",
            valign="top",
        )
        설명.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        설정틀.add_widget(설명)
        설정틀.add_widget(Widget())
        루트.add_widget(설정틀)
        self._반응자동_변경(self.반응자동버튼, self.반응자동버튼.state)
        뒤로버튼 = Button(text="뒤로", size_hint=(1, 0.2))
        뒤로키_버튼(뒤로버튼)
        뒤로버튼.bind(
            on_release=lambda *_: setattr(self.manager, "current", "메인메뉴")
        )
        루트.add_widget(뒤로버튼)
        self.add_widget(루트)

    def _반응자동_변경(self, 버튼, 상태):
        켜짐 = 상태 == "down"
        버튼.text = f"반응 자동 사용: {'켜짐' if 켜짐 else '꺼짐'}"
        if 켜짐 != gameflow.반응_자동_여부():
            gameflow.반응_자동_설정(켜짐)
            설정_저장("반응자동", 켜짐)
