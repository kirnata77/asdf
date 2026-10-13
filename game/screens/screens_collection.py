# =====================
# 도감 / 업적 화면 (게임 중 [메뉴] -> [도감] / [업적])
# =====================
# 도감: 대분류(몬스터/장비/소모품/재료) -> 소분류 탭 -> 목록. 장비는 소지품 화면과 같은 부위 탭과 하위 필터
# (무기 직업군/종류, 방어구 재질)에 레어도 필터 한 줄이 더 붙는다. 등록하지 않은 항목도 이름은 보이지만
# 어둡게 보이고 [상세보기]를 누를 수 없다. 아이템 [상세보기]는 소지품 화면 것을 그대로 쓴다.
# 업적: 왼쪽에 분류(레벨/도감/전투/특수), 오른쪽에 그 분류의 업적과 줄마다 [보상받기], 오른쪽 아래 [보상 전부 받기].
# 달성하지 않았거나 이미 받은 업적의 [보상받기]는 눌리지 않는다. 로직은 전부 gameflow.도감_*/업적_*.

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.utils import escape_markup

import gameflow
from game.screens.screens_common import (
    _에셋_경로,
    _버튼_폰트크기,
    뒤로키_버튼,
    닫기_버튼,
    스크롤_목록,
    탭_줄,
    글자_높이,
    아이템_이름_글,
)
from game.screens.screens_town import 소지품화면

_미등록_색 = "5c6068"  # 등록하지 않은 항목 이름 - 어둡게


class 도감화면(소지품화면):
    제목 = "도감"
    모드 = "도감"

    def on_pre_enter(self, *args):
        self.복귀화면 = getattr(self, "돌아갈화면", None) or "마을"
        super().on_pre_enter(*args)

    def _골드_갱신(self):
        게임상태 = App.get_running_app().게임상태
        등록 = 전체 = 0
        for 대분류 in gameflow.도감_대분류목록:
            n, m = gameflow.도감_등록현황(게임상태, 대분류)
            등록, 전체 = 등록 + n, 전체 + m
        self.골드라벨.text = f"등록 {등록}/{전체}"

    def _대분류_그리기(self, 모드):
        self._비우기()
        게임상태 = App.get_running_app().게임상태
        상단 = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=글자_높이()
        )
        나가기버튼 = Button(text="◀ 나가기", size_hint=(0.32, 1))
        뒤로키_버튼(나가기버튼)
        나가기버튼.bind(on_release=self._나가기)
        상단.add_widget(나가기버튼)
        상단.add_widget(Label(text=모드, size_hint=(0.68, 1)))
        self.내용틀.add_widget(상단)
        for 대분류 in gameflow.도감_대분류목록:
            등록, 전체 = gameflow.도감_등록현황(게임상태, 대분류)
            버튼 = Button(text=f"{대분류} ({등록}/{전체})", font_size=_버튼_폰트크기)
            버튼.bind(on_release=lambda *_, d=대분류: self._탭목록_그리기(모드, d))
            self.내용틀.add_widget(버튼)

    def _탭줄(self, 모드, 대분류):
        return gameflow.도감_탭줄(App.get_running_app().게임상태, 대분류)

    def _부위_고르기(self, 모드, 대분류, 탭):
        self._필터 = {"직업군": None, "분류": None, "레어도": None}
        self._하위탭_그리기(모드, 대분류, 탭)
        self._아이템목록_그리기(모드, 대분류, 탭, self._목록틀)

    def _하위탭_그리기(self, 모드, 대분류, 탭):
        """소지품/상점과 같은 하위 탭(무기 직업군/종류, 방어구 재질) 아래에 레어도 탭 한 줄."""
        super()._하위탭_그리기(모드, 대분류, 탭)
        레어도탭 = gameflow.도감_레어도탭(App.get_running_app().게임상태, 대분류, 탭)
        if not 레어도탭:
            return
        높이 = 글자_높이("13sp")
        틀 = self._하위탭틀
        틀.add_widget(
            탭_줄(
                레어도탭,
                lambda 값, m=모드, d=대분류, t=탭: self._하위_고르기(
                    m, d, t, "레어도", 값
                ),
                self._필터.get("레어도") or 레어도탭[0],
                높이=높이,
                font_size="13sp",
            )
        )
        줄수 = len(틀.children)
        틀.height = 줄수 * 높이 + (줄수 - 1) * dp(4)

    def _아이템목록_그리기(self, 모드, 대분류, 탭, 목록틀):
        목록틀.clear_widgets()
        self._현재 = (대분류, 탭, 목록틀)
        게임상태 = App.get_running_app().게임상태
        필터 = getattr(self, "_필터", None) or {}
        항목목록 = [
            (항목, 등록)
            for 항목, 등록 in gameflow.도감_목록(게임상태, 대분류, 탭)
            if 대분류 != "장비"
            or (
                gameflow.상점_분류_일치(탭, 항목, 필터.get("직업군"), 필터.get("분류"))
                and gameflow.도감_레어도_일치(항목, 필터.get("레어도"))
            )
        ]
        if not 항목목록:
            목록틀.add_widget(
                Label(
                    text="해당하는 항목이 없습니다.", size_hint=(1, None), height=dp(40)
                )
            )
            return
        for 항목, 등록 in 항목목록:
            목록틀.add_widget(self._도감_행(대분류, 항목, 등록))

    def _도감_행(self, 대분류, 항목, 등록):
        몬스터 = 대분류 == "몬스터"
        이름 = 항목["몬스터명"] if 몬스터 else 항목["이름"]
        if not 등록:
            글 = f"[color={_미등록_색}]{escape_markup(이름)}[/color]"
        elif 몬스터:
            글 = escape_markup(이름)
        else:
            글 = 아이템_이름_글(항목)
        행 = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=56, spacing=4
        )
        이름라벨 = Label(
            text=글,
            markup=True,
            size_hint=(0.56, 1),
            halign="left",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        이름라벨.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        행.add_widget(이름라벨)
        행.add_widget(
            Label(
                text="등록" if 등록 else f"[color={_미등록_색}]미등록[/color]",
                markup=True,
                size_hint=(0.2, 1),
            )
        )
        상세버튼 = Button(text="상세보기", size_hint=(0.24, 1), disabled=not 등록)
        if 몬스터:
            상세버튼.bind(on_release=lambda *_: self._몬스터_상세(항목))
        else:
            상세버튼.bind(on_release=lambda *_: self._상세보기(항목))
        행.add_widget(상세버튼)
        return 행

    def _몬스터_상세(self, 몬스터):
        본문 = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        그림 = _에셋_경로("monster", 몬스터.get("이미지"))
        if 그림:
            본문.add_widget(
                Image(
                    source=그림,
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint=(1, 0.55),
                )
            )
        문구 = Label(
            text="\n".join(gameflow.도감_몬스터_상세(몬스터["몬스터명"])),
            halign="center",
            valign="middle",
        )
        문구.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        본문.add_widget(문구)
        팝업 = Popup(
            title=몬스터["몬스터명"],
            content=본문,
            size_hint=(0.85, None),
            height=dp(460),
        )
        본문.add_widget(닫기_버튼(팝업, size_hint=(1, None), height=dp(52)))
        팝업.open()
        return 팝업


class 업적화면(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.돌아갈화면 = "마을"
        self._분류 = gameflow.업적_분류목록[0]

        루트 = BoxLayout(orientation="vertical", padding=12, spacing=6)
        머리 = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=글자_높이("20sp")
        )
        머리.add_widget(Label(text="업적", font_size="20sp"))
        self.골드라벨 = Label(text="")
        머리.add_widget(self.골드라벨)
        루트.add_widget(머리)

        상단 = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=글자_높이()
        )
        나가기버튼 = Button(text="◀ 나가기", size_hint=(0.32, 1))
        뒤로키_버튼(나가기버튼)
        나가기버튼.bind(on_release=self._나가기)
        상단.add_widget(나가기버튼)
        상단.add_widget(Widget(size_hint=(0.68, 1)))
        루트.add_widget(상단)

        몸 = BoxLayout(orientation="horizontal", spacing=dp(6))
        # 왼쪽: 분류 버튼(위에서부터 쌓고 남는 칸은 비운다)
        왼쪽 = BoxLayout(orientation="vertical", size_hint=(0.3, 1), spacing=dp(4))
        self._분류버튼 = {}
        for 분류 in gameflow.업적_분류목록:
            버튼 = ToggleButton(
                text=분류,
                group=f"업적분류{id(self)}",
                allow_no_selection=False,
                state="down" if 분류 == self._분류 else "normal",
                size_hint=(1, None),
                height=dp(56),
            )
            버튼.bind(on_release=lambda *_, b=분류: self._분류_고르기(b))
            왼쪽.add_widget(버튼)
            self._분류버튼[분류] = 버튼
        왼쪽.add_widget(Widget())
        몸.add_widget(왼쪽)

        # 오른쪽: 업적 목록 + 오른쪽 아래 [보상 전부 받기]
        오른쪽 = BoxLayout(orientation="vertical", size_hint=(0.7, 1), spacing=dp(6))
        스크롤, self._목록틀 = 스크롤_목록(1)
        self._목록스크롤 = 스크롤
        오른쪽.add_widget(스크롤)
        아래줄 = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(56))
        아래줄.add_widget(Widget(size_hint=(0.4, 1)))
        self.전부받기버튼 = Button(text="보상 전부 받기", size_hint=(0.6, 1))
        self.전부받기버튼.bind(on_release=self._전부_받기)
        아래줄.add_widget(self.전부받기버튼)
        오른쪽.add_widget(아래줄)
        몸.add_widget(오른쪽)
        루트.add_widget(몸)

        self.안내라벨 = Label(text="", size_hint=(1, None), height=글자_높이())
        루트.add_widget(self.안내라벨)
        self.add_widget(루트)

    def on_pre_enter(self, *args):
        self.안내라벨.text = ""
        self.갱신()

    def _나가기(self, *args):
        self.manager.current = self.돌아갈화면 or "마을"

    def _분류_고르기(self, 분류):
        self._분류 = 분류
        self.갱신()

    def 갱신(self):
        게임상태 = App.get_running_app().게임상태
        self.골드라벨.text = f"보유 골드: {gameflow.상점_보유골드(게임상태)}G"
        for 분류, 버튼 in self._분류버튼.items():
            버튼.state = "down" if 분류 == self._분류 else "normal"
        self._목록틀.clear_widgets()
        for 줄 in gameflow.업적_목록(게임상태, self._분류):
            self._목록틀.add_widget(self._업적_행(줄))
        self.전부받기버튼.disabled = gameflow.업적_받을_보상_수(게임상태) == 0

    def _업적_행(self, 줄):
        행 = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=dp(84), spacing=4
        )
        색 = "ffffff" if 줄["달성"] else _미등록_색
        글 = (
            f"[color={색}][b]{escape_markup(줄['이름'])}[/b][/color]\n"
            f"[size=12sp]{escape_markup(줄['설명'])}[/size]\n"
            f"[size=12sp]진행 {줄['진행']}/{줄['목표']}  보상 {줄['보상골드']}G[/size]"
        )
        라벨 = Label(
            text=글, markup=True, size_hint=(0.66, 1), halign="left", valign="middle"
        )
        라벨.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        행.add_widget(라벨)
        버튼 = Button(
            text="받음" if 줄["받음"] else "보상받기",
            size_hint=(0.34, 1),
            disabled=줄["받음"] or not 줄["달성"],
        )
        버튼.업적ID = 줄["ID"]
        버튼.bind(on_release=lambda *_: self._받기(줄["ID"]))
        행.add_widget(버튼)
        return 행

    def _받기(self, 업적ID):
        게임상태 = App.get_running_app().게임상태
        try:
            골드 = gameflow.업적_보상_받기(게임상태, 업적ID)
        except ValueError as 오류:
            self.안내라벨.text = str(오류)
            return
        self.갱신()
        self.안내라벨.text = f"보상 {골드}G를 받았습니다."

    def _전부_받기(self, *args):
        수, 골드 = gameflow.업적_보상_전부_받기(App.get_running_app().게임상태)
        self.갱신()
        self.안내라벨.text = (
            f"업적 {수}개의 보상 {골드}G를 받았습니다."
            if 수
            else "받을 보상이 없습니다."
        )
