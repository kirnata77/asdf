# =====================
# 전투 화면 - 전투화면(반응 선택 팝업 포함), 스킬 선택 팝업, 상태 박스
# =====================
# main.py가 game/screens/ 여섯 파일의 화면을 ScreenManager에 등록한다.

import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from kivy.graphics import Color, Line

import gameflow
from game.screens.screens_common import (
    _캐릭터이미지_경로,
    _에셋_경로,
    _도트_필터,
    뒤로키_버튼,
)


# =====================================================
# 6. 전투 화면
# =====================================================

# 적/아군 상태·그래픽 박스를 몇 칸까지 고정으로 그릴지. 실제 참가자가 이보다 적으면 남는 칸은 빈 칸으로
# 둔다 - 모험단 프로필 그리드(_초상화_행목록)와 같은 방식.
_적슬롯_최대 = 5
_아군슬롯_최대 = 4
# 적이 5마리보다 적을 때 칸 사이 간격을 넓혀 가운데로 모으는 비율
# - 칸 자체는 _박스_비율, 칸 사이 빈 공간은
# _간격_비율만큼의 상대 폭을 차지한다. 적이 적을수록 칸 개수가 줄어
# 빈 공간(간격) 비중이 커지고, 자연히 전체가 중앙에 모인 것처럼 보인다.
_박스_비율 = 2
_간격_비율 = 1


def _가운데정렬_채우기(틀, 위젯목록):
    """가로 BoxLayout인 틀을 비우고, 위젯목록을 앞뒤/사이에 동일한
    간격(스페이서)을 두고 채운다. 위젯 개수가 적을수록 간격이 상대적으로
    넓어져 전체가 화면 중앙으로 모인다."""
    틀.clear_widgets()
    틀.add_widget(Widget(size_hint_x=_간격_비율))
    for 위젯 in 위젯목록:
        틀.add_widget(위젯)
        틀.add_widget(Widget(size_hint_x=_간격_비율))


# 상태/그래픽/배경 박스 테두리 색 - 전부 흰색 테두리로 통일한다.
_박스_테두리색 = (1, 1, 1, 1)


class _테두리박스(ButtonBehavior, BoxLayout):
    """테두리를 그리는 상자. 전투화면의 적/아군 상태 박스, 그래픽 박스,
    배경 틀(전투 배경 이미지는 아직 없어 빈 채로 둔다)에 공용으로 쓴다.
    현재턴_표시()로 테두리를 굵게 만들어 누구 턴인지 표시한다."""

    def __init__(self, 테두리색, 기본두께=1.5, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        super().__init__(**kwargs)
        self._기본두께 = 기본두께
        with self.canvas.before:
            Color(*테두리색)
            self._테두리 = Line(width=기본두께)
        self.bind(pos=self._다시그리기, size=self._다시그리기)

    def _다시그리기(self, *args):
        self._테두리.rectangle = (
            self.x + 1,
            self.y + 1,
            max(self.width - 2, 0),
            max(self.height - 2, 0),
        )

    def 현재턴_표시(self, 켜짐):
        self._테두리.width = self._기본두께 * 2.5 if 켜짐 else self._기본두께


class _스킬선택팝업(Popup):
    """ "스킬" 버튼을 누르면 뜨는 목록 팝업(액션 버튼 5칸 고정 레이아웃이라
    화면에 스킬 목록을 펼칠 자리가 없다)."""

    def __init__(self, 항목목록, 선택콜백, **kwargs):
        super().__init__(title="스킬 선택", size_hint=(0.85, 0.75), **kwargs)
        self.선택콜백 = 선택콜백

        스크롤 = ScrollView()
        목록틀 = BoxLayout(
            orientation="vertical", spacing=6, padding=6, size_hint_y=None
        )
        목록틀.bind(minimum_height=목록틀.setter("height"))

        for 이름, 스킬데이터, 가능, *나머지 in 항목목록:
            표시 = 나머지[0] if 나머지 else 이름
            버튼 = Button(text=표시, size_hint_y=None, height=dp(56), disabled=not 가능)
            버튼.bind(on_release=lambda inst, n=이름, d=스킬데이터: self._선택(n, d))
            목록틀.add_widget(버튼)

        스크롤.add_widget(목록틀)
        self.content = 스크롤

    def _선택(self, 이름, 스킬데이터):
        self.선택콜백(이름, 스킬데이터)
        self.dismiss()


class 전투화면(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.선택모드 = None
        self._엔진중 = False

        루트 = BoxLayout(orientation="vertical", padding=10, spacing=6)

        # 적 상태 박스(최대 5칸) - 이름/HP/MP. 현재 턴이면 테두리가
        # 굵어진다. 5마리보다 적으면 칸 사이 간격이 넓어져 가운데로 모인다
        # (GridLayout 대신 스페이서를 둔 BoxLayout).
        self.적상태틀 = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.13), spacing=4
        )
        루트.add_widget(self.적상태틀)

        # 전투 배경(배경 이미지는 아직 없어 비워둠) + 그래픽 - 위 칸(5)엔
        # 적 그래픽, 아래 칸(4)엔 아군 그래픽.
        self.배경틀 = _테두리박스(
            _박스_테두리색,
            기본두께=1,
            size_hint=(1, 0.33),
            spacing=4,
            padding=4,
        )
        self.적그래픽행 = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.55), spacing=4
        )
        self.배경틀.add_widget(self.적그래픽행)
        self.아군그래픽행 = GridLayout(
            cols=_아군슬롯_최대, size_hint=(1, 0.45), spacing=4
        )
        self.배경틀.add_widget(self.아군그래픽행)
        루트.add_widget(self.배경틀)

        # 아군 상태 박스(최대 4칸).
        self.아군상태틀 = GridLayout(
            cols=_아군슬롯_최대, size_hint=(1, 0.13), spacing=4
        )
        루트.add_widget(self.아군상태틀)

        # 전투 로그 - 아군 상태 박스와 액션 버튼 사이에 배치.
        로그스크롤 = ScrollView(size_hint=(1, 0.17))
        self.로그라벨 = Label(
            text="",
            size_hint_y=None,
            halign="left",
            valign="top",
            font_size=20,
        )
        self.로그라벨.bind(
            texture_size=lambda inst, size: setattr(inst, "height", size[1]),
            width=lambda inst, w: setattr(inst, "text_size", (w, None)),
        )
        로그스크롤.add_widget(self.로그라벨)
        루트.add_widget(로그스크롤)

        self.안내라벨 = Label(text="", size_hint=(1, 0.05), font_size=20)
        루트.add_widget(self.안내라벨)

        # 액션 버튼 - 왼쪽위 일반공격/오른쪽위
        # 스킬/중간왼쪽 아이템/중간오른쪽 도망/아래 전체 턴 넘기기.
        self.액션틀 = BoxLayout(orientation="vertical", size_hint=(1, 0.19), spacing=4)
        루트.add_widget(self.액션틀)

        self.add_widget(루트)

    # -------------------------------------------------
    # 상태/그래픽 박스 - 공용 라벨 생성 헬퍼
    # -------------------------------------------------

    def _중앙정렬_라벨(self, 문자열):
        라벨 = Label(text=문자열, font_size=16, halign="center", valign="middle")
        라벨.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        return 라벨

    # -------------------------------------------------
    # 화면 갱신
    # -------------------------------------------------

    def 갱신(self, 신규=False):
        앱 = App.get_running_app()
        게임상태 = 앱.게임상태
        self.선택모드 = None

        if 신규:
            self.로그라벨.text = ""

        if 게임상태 is None or 게임상태["전투상태"] is None:
            return

        참가자 = self._표시_갱신(게임상태)

        # 던전에서 전투가 시작되며 미뤄 둔 전투시작 반응(패스티스트 건)을 먼저
        # 처리한다(반응 선택 팝업을 띄워야 하므로 전투 화면에서 처리).
        if gameflow.전투시작_반응_대기중(게임상태):
            self._엔진_실행(
                lambda: gameflow.전투시작_반응_처리(게임상태), lambda _: self.갱신()
            )
            return

        if gameflow.전투_종료됨(게임상태):
            self._전투종료_처리()
            return

        아군차례 = gameflow.아군_차례인가(게임상태)
        self._행동버튼_갱신(아군차례, 참가자)

        if 아군차례:
            self.안내라벨.text = f"{참가자['이름']}의 턴 - 행동을 선택하세요."
        else:
            self.안내라벨.text = f"{참가자['이름']}의 턴 (자동 진행 중...)"
            Clock.schedule_once(self._자동진행, 0.4)

    def _표시_갱신(self, 게임상태):
        """상태 박스와 새 로그만 다시 그린다(반응 팝업 직전에도 쓴다)."""
        참가자 = gameflow.현재_턴_참가자(게임상태)
        self._적_박스_갱신(게임상태, 참가자)
        self._아군_박스_갱신(게임상태, 참가자)
        for 로그항목 in gameflow.새_로그_가져오기(게임상태):
            self.로그라벨.text += self._로그_문자열(로그항목) + "\n"
        return 참가자

    # -------------------------------------------------
    # 반응 선택
    # -------------------------------------------------
    # 반응 자동 사용이 꺼져 있으면 전투 동작(공격/스킬/턴 넘기기/적 턴/도망/
    # 전투시작 반응)을 작업 스레드에서 실행한다. 엔진이 반응 후보를 만나면
    # 전투상태["반응선택"](= _반응_묻기)을 부르고, 이 함수가 화면 스레드에
    # 팝업을 띄운 뒤 고를 때까지 작업 스레드를 기다리게 한다. 작업 중에는
    # 화면 입력을 막는다. 켜져 있으면 화면 스레드에서 바로 실행하고 자동으로 쓴다.

    def _엔진_실행(self, 작업, 완료=None):
        if self._엔진중:
            return
        게임상태 = App.get_running_app().게임상태
        전투상태 = 게임상태["전투상태"]
        if gameflow.반응_자동_여부():
            전투상태["반응선택"] = None
            결과 = 작업()
            if 완료:
                완료(결과)
            return
        전투상태["반응선택"] = self._반응_묻기
        self._엔진중 = True
        self.disabled = True

        def 끝(결과, 오류):
            self._엔진중 = False
            self.disabled = False
            전투상태["반응선택"] = None
            if isinstance(오류, ValueError):
                self.안내라벨.text = str(오류)
                self.갱신()
                return
            if 오류 is not None:
                raise 오류
            if 완료:
                완료(결과)

        def 일():
            try:
                결과, 오류 = 작업(), None
            except Exception as 예외:
                결과, 오류 = None, 예외
            Clock.schedule_once(lambda dt: 끝(결과, 오류))

        threading.Thread(target=일, daemon=True).start()

    def _반응_묻기(self, 참가자, 후보, 상황):
        """작업 스레드에서 불린다 - 팝업 결과(후보 번호 또는 None)를 기다렸다 돌려준다."""
        이벤트 = threading.Event()
        결과 = {}

        def 열기(dt):
            게임상태 = App.get_running_app().게임상태
            self._표시_갱신(게임상태)
            self._반응_팝업(
                참가자, 후보, 상황, lambda 번호: (결과.update(값=번호), 이벤트.set())
            )

        Clock.schedule_once(열기)
        이벤트.wait()
        return 결과.get("값")

    def _반응_팝업(self, 참가자, 후보, 상황, 끝):
        본문 = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(12))
        상황라벨 = Label(text=상황, halign="left", valign="middle", size_hint=(1, 0.3))
        상황라벨.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        본문.add_widget(상황라벨)
        반응행동 = 참가자.get("행동자원", {}).get("반응행동", 0)
        팝업 = Popup(
            title=f"반응 - {참가자['이름']} (반응행동 {반응행동})",
            content=본문,
            size_hint=(0.92, None),
            height=dp(200 + 64 * len(후보)),
            auto_dismiss=False,
        )

        def 선택(번호):
            팝업.dismiss(animation=False)
            끝(번호)

        목록 = BoxLayout(orientation="vertical", spacing=dp(6))
        for 번호, (이름, 설명) in enumerate(후보):
            버튼 = Button(
                text=f"{이름}  -  {설명}",
                halign="center",
                valign="middle",
                background_normal="",
                background_color=(0.22, 0.56, 0.86, 1),
            )
            버튼.bind(
                size=lambda inst, size: setattr(
                    inst, "text_size", (size[0] - dp(12), None)
                )
            )
            버튼.bind(on_release=lambda inst, n=번호: 선택(n))
            목록.add_widget(버튼)
        안함 = Button(
            text="사용 안 함",
            background_normal="",
            background_color=(0.3, 0.31, 0.35, 1),
        )
        안함.bind(on_release=lambda *_: 선택(None))
        목록.add_widget(안함)
        본문.add_widget(목록)
        팝업.open()

    def _적_박스_갱신(self, 게임상태, 현재참가자):
        적목록 = gameflow.적_목록(게임상태)[:_적슬롯_최대]

        상태박스목록 = []
        그래픽박스목록 = []
        for 적 in 적목록:
            상태박스 = _테두리박스(_박스_테두리색, size_hint_x=_박스_비율)
            상태박스.add_widget(
                self._중앙정렬_라벨(
                    f"{적['이름']}\nHP {적['현재HP']}  MP {적['현재MP']}"
                    + ("" if 적["생존"] else "\n(쓰러짐)")
                )
            )
            상태박스.disabled = not 적["생존"]
            상태박스.bind(on_release=lambda inst, p=적: self._대상_선택(p))
            상태박스.현재턴_표시(적 is 현재참가자)
            상태박스목록.append(상태박스)

            그래픽박스 = _테두리박스(_박스_테두리색, size_hint_x=_박스_비율)
            # 몬스터 데이터의 "이미지"(game/assets/monster/)를 띄운다.
            # 지정이 없거나 파일이 없으면 빈 이미지로 자리만 둔다.
            경로 = _에셋_경로("monster", 적["원본"].get("이미지"))
            if 경로:
                이미지 = Image(allow_stretch=True, source=경로)
                _도트_필터(이미지)
            else:
                이미지 = Image(allow_stretch=True)
            그래픽박스.add_widget(이미지)
            그래픽박스목록.append(그래픽박스)

        # 적이 5마리보다 적으면 칸 사이 간격이 넓어져 가운데로 모인다.
        _가운데정렬_채우기(self.적상태틀, 상태박스목록)
        _가운데정렬_채우기(self.적그래픽행, 그래픽박스목록)

    def _아군_박스_갱신(self, 게임상태, 현재참가자):
        self.아군상태틀.clear_widgets()
        self.아군그래픽행.clear_widgets()

        아군목록 = gameflow.아군_목록(게임상태)
        for i in range(_아군슬롯_최대):
            if i >= len(아군목록):
                self.아군상태틀.add_widget(Widget())
                self.아군그래픽행.add_widget(Widget())
                continue

            아군 = 아군목록[i]
            상태박스 = _테두리박스(_박스_테두리색)
            상태 = "" if 아군["생존"] else "\n(쓰러짐)"
            상태박스.add_widget(
                self._중앙정렬_라벨(
                    f"{아군['이름']}\n"
                    f"HP {아군['현재HP']}/{gameflow.캐릭터_최대HP(게임상태, 아군['원본'])}\n"
                    f"MP {아군['현재MP']}/{gameflow.캐릭터_최대MP(게임상태, 아군['원본'])}{상태}"
                )
            )
            # 아군단일 스킬 대상 선택용.
            상태박스.bind(on_release=lambda inst, p=아군: self._아군_선택(p))
            상태박스.현재턴_표시(아군 is 현재참가자)
            self.아군상태틀.add_widget(상태박스)

            그래픽박스 = _테두리박스(_박스_테두리색)
            # 캐릭터별 직업 기반 초상화(gameflow.초상화_코드) - 던전
            # 지도용 "플레이어 초상화"와는 별개다.
            이미지 = Image(
                allow_stretch=True,
                source=_캐릭터이미지_경로(gameflow.초상화_코드(아군["원본"])),
            )
            그래픽박스.add_widget(이미지)
            self.아군그래픽행.add_widget(그래픽박스)

    def _자동진행(self, *args):
        앱 = App.get_running_app()
        게임상태 = 앱.게임상태
        if 게임상태 is None or 게임상태["전투상태"] is None or self._엔진중:
            return
        self._엔진_실행(lambda: gameflow.턴_넘기기(게임상태), lambda _: self.갱신())

    def _로그_문자열(self, 항목):
        # 반응특성 로그: 반격 공격은 아래 "판정" 형식 앞에
        # [반응:이름]을 붙이고, 회피/피해감소 등은 설명 문구만 보여준다.
        if "반응" in 항목 and "판정" not in 항목:
            return f"[반응] {항목.get('공격자', '?')} '{항목['반응']}': {항목.get('비고', '')}"
        if "반응" in 항목:
            판정 = 항목["판정"]
            if not 판정.get("성공"):
                return f"[반응:{항목['반응']}] {항목.get('공격자', '?')} -> {항목.get('대상', '?')}: 빗나감"
            치명 = " (치명타!)" if 판정.get("치명타") else ""
            return (
                f"[반응:{항목['반응']}] {항목.get('공격자', '?')} -> "
                f"{항목.get('대상', '?')}: {항목.get('피해', 0)} 피해{치명}"
            )
        if "타격" in 항목 and "총피해" in 항목:
            명중수 = sum(1 for t in 항목["타격"] if t.get("판정", {}).get("성공"))
            return (
                f"{항목.get('공격자', '?')} [{항목.get('스킬', '')}] "
                f"{명중수}/{len(항목['타격'])}회 명중, 총 {항목.get('총피해', 0)} 피해"
            )
        if "판정" in 항목:
            판정 = 항목["판정"]
            if not 판정.get("성공"):
                return f"{항목.get('공격자', '?')} -> {항목.get('대상', '?')}: 빗나감"
            치명 = " (치명타!)" if 판정.get("치명타") else ""
            return (
                f"{항목.get('공격자', '?')} -> {항목.get('대상', '?')}: "
                f"{항목.get('피해', 0)} 피해{치명}"
            )
        if "총피해" in 항목:
            이름표 = 항목.get("패턴") or 항목.get("스킬") or ""
            return f"{항목.get('공격자', '?')} [{이름표}] 총 {항목['총피해']} 피해"
        if "행동" in 항목:
            return f"{항목.get('공격자', '?')}: {항목['행동']}"
        if "버프" in 항목:
            return f"{항목.get('공격자', '?')}: '{항목.get('스킬')}' 사용 -> {항목.get('버프')}"
        return str(항목)

    # -------------------------------------------------
    # 행동 버튼 (좌상 일반공격/우상 스킬/중좌 아이템/
    # 중우 도망/하단 전체 턴 넘기기)
    # -------------------------------------------------

    def _행동버튼_갱신(self, 아군차례, 참가자):
        self.액션틀.clear_widgets()

        행1 = BoxLayout(orientation="horizontal", spacing=4)
        일반공격버튼 = Button(text="일반공격")
        일반공격버튼.disabled = not (
            아군차례 and 참가자["행동자원"].get("일반행동", 0) > 0
        )
        일반공격버튼.bind(on_release=lambda *_: self._일반공격_클릭())
        행1.add_widget(일반공격버튼)

        스킬버튼 = Button(text="스킬")
        스킬버튼.disabled = not 아군차례
        스킬버튼.bind(on_release=lambda *_: self._스킬_버튼_클릭(참가자))
        행1.add_widget(스킬버튼)
        self.액션틀.add_widget(행1)

        행2 = BoxLayout(orientation="horizontal", spacing=4)
        아이템버튼 = Button(text="아이템")
        아이템버튼.disabled = not 아군차례
        아이템버튼.bind(on_release=lambda *_: self._아이템_클릭())
        행2.add_widget(아이템버튼)

        도망버튼 = Button(text="도망")
        도망버튼.disabled = not 아군차례
        도망버튼.bind(on_release=lambda *_: self._도망_클릭())
        행2.add_widget(도망버튼)
        self.액션틀.add_widget(행2)

        턴넘기기버튼 = Button(text="턴 넘기기")
        턴넘기기버튼.disabled = not 아군차례
        턴넘기기버튼.bind(on_release=lambda *_: self._턴넘기기_클릭())
        self.액션틀.add_widget(턴넘기기버튼)

    def _스킬_버튼_클릭(self, 참가자):
        """ "스킬" 버튼 - 보유 스킬 목록을 팝업(_스킬선택팝업)으로 띄운다."""
        앱 = App.get_running_app()
        게임상태 = 앱.게임상태
        스킬데이터모음 = 게임상태["스킬데이터모음"]

        항목목록 = []
        for 이름 in 참가자["원본"].get("보유스킬", []):
            스킬데이터 = 스킬데이터모음.get(이름)
            if 스킬데이터 is None:
                continue
            가능, _ = gameflow.스킬_사용_가능여부(게임상태, 참가자, 이름)
            # 휴식당횟수가 있는 스킬은 남은 횟수를 붙여 보여준다.
            남은정보 = gameflow.스킬_휴식_남은횟수(게임상태, 참가자, 이름)
            표시 = f"{이름} ({남은정보[0]}/{남은정보[1]})" if 남은정보 else 이름
            항목목록.append((이름, 스킬데이터, 가능, 표시))

        if not 항목목록:
            self.안내라벨.text = "사용할 수 있는 스킬이 없습니다."
            return

        _스킬선택팝업(항목목록, self._스킬_클릭).open()

    def _일반공격_클릭(self):
        self.선택모드 = ("일반공격",)
        self.안내라벨.text = "일반공격할 대상을 선택하세요."

    def _실제_타겟(self, 스킬데이터):
        """스킬의 실제 타겟 종류(gameflow.스킬_실제_타겟 참고)."""
        return gameflow.스킬_실제_타겟(App.get_running_app().게임상태, 스킬데이터)

    def _스킬_클릭(self, 이름, 스킬데이터):
        타겟 = self._실제_타겟(스킬데이터)
        if 타겟 == "적단일":
            self.선택모드 = ("스킬", 이름)
            self.안내라벨.text = f"'{이름}' 사용 대상을 선택하세요."
        elif 타겟 == "적3체":
            self.선택모드 = ("스킬", 이름)
            self.안내라벨.text = (
                f"'{이름}' 중심 대상을 선택하세요 (양옆 1체씩 함께 맞습니다)."
            )
        elif 타겟 == "아군단일":
            self.선택모드 = ("스킬아군", 이름)
            self.안내라벨.text = f"'{이름}'을(를) 사용할 아군을 선택하세요."
        elif 타겟 == "적반복지정":
            # 타격 횟수만큼 적을 차례로 누른다. 다 고르면 실행.
            앱 = App.get_running_app()
            횟수 = max(
                1, gameflow.현재참가자_수치(앱.게임상태, 스킬데이터.get("공격횟수", 1))
            )
            self.선택모드 = ("반복지정", 이름, 횟수, [])
            self.안내라벨.text = f"'{이름}' 대상을 {횟수}번 선택하세요 (1/{횟수})."
        else:
            self._스킬_실행(이름, None)

    def _아군_선택(self, 아군참가자):
        if self.선택모드 is None or self.선택모드[0] != "스킬아군":
            return
        if not 아군참가자["생존"]:
            self.안내라벨.text = "쓰러진 아군은 대상으로 고를 수 없습니다."
            return
        _, 이름 = self.선택모드
        self.선택모드 = None
        self._스킬_실행(이름, 아군참가자)

    def _대상_선택(self, 적참가자):
        if self.선택모드 is None or not 적참가자["생존"]:
            return
        종류 = self.선택모드[0]
        if 종류 == "스킬아군":
            return  # 아군 대상 선택 중에는 적 칸을 눌러도 무시한다.
        if 종류 == "반복지정":
            self._반복지정_선택(적참가자)
            return
        if 종류 == "일반공격":
            self.선택모드 = None
            self._일반공격_실행(적참가자)
        elif 종류 == "스킬":
            _, 이름 = self.선택모드
            self.선택모드 = None
            self._스킬_실행(이름, 적참가자)

    def _반복지정_선택(self, 적참가자):
        """ "적반복지정" 스킬의 대상을 한 번 추가한다. 은신(지정불가) 대상은
        고를 수 없고, "중복지정가능"이 False면 같은 적을 두 번 고를 수 없으며,
        "대상당피격제한"이 있으면 그 횟수를 넘길 수 없다."""
        _, 이름, 횟수, 목록 = self.선택모드
        앱 = App.get_running_app()
        스킬데이터 = 앱.게임상태["스킬데이터모음"][이름]
        if gameflow.지정불가_상태인가(앱.게임상태, 적참가자):
            self.안내라벨.text = f"{적참가자['이름']}은(는) 지정할 수 없는 상태입니다."
            return
        이미 = sum(1 for p in 목록 if p is 적참가자)
        if 이미 and not 스킬데이터.get("중복지정가능", True):
            self.안내라벨.text = "같은 적을 두 번 고를 수 없습니다."
            return
        제한 = 스킬데이터.get("대상당피격제한")
        if 제한 is not None:
            제한 = gameflow.현재참가자_수치(앱.게임상태, 제한)
            if 이미 >= 제한:
                self.안내라벨.text = f"한 적은 최대 {제한}번까지 고를 수 있습니다."
                return
        목록.append(적참가자)
        if len(목록) < 횟수:
            self.안내라벨.text = (
                f"'{이름}' 대상을 선택하세요 ({len(목록) + 1}/{횟수}) - "
                f"고른 대상: {', '.join(p['이름'] for p in 목록)}"
            )
            return
        self.선택모드 = None
        self._스킬_실행(이름, 목록[0], 지정대상목록=list(목록))

    def _일반공격_실행(self, 대상):
        앱 = App.get_running_app()
        self._오류표시_실행(lambda: gameflow.아군_일반공격(앱.게임상태, 대상))

    def _스킬_실행(self, 이름, 대상, 지정대상목록=None):
        앱 = App.get_running_app()
        self._오류표시_실행(
            lambda: gameflow.아군_스킬사용(
                앱.게임상태, 이름, 대상, 지정대상목록=지정대상목록
            )
        )

    def _오류표시_실행(self, 작업):
        """ValueError(자원 부족 등)는 안내 문구로 보여주고 화면은 그대로 둔다."""

        def 감싼작업():
            try:
                return 작업(), None
            except ValueError as 오류:
                return None, 오류

        def 완료(결과):
            _, 오류 = 결과
            if 오류 is not None:
                self.안내라벨.text = str(오류)
                return
            self.갱신()

        self._엔진_실행(감싼작업, 완료)

    def _턴넘기기_클릭(self):
        앱 = App.get_running_app()
        self._엔진_실행(lambda: gameflow.턴_넘기기(앱.게임상태), lambda _: self.갱신())

    def _아이템_클릭(self):
        # 아직 아이템/인벤토리 시스템 자체가 없어(게임 데이터에 아이템
        # 목록이 없음) 자리만 만들어 둔 버튼이다.
        self.안내라벨.text = "아이템은 아직 구현되지 않았습니다."

    # -------------------------------------------------
    # 도망
    # -------------------------------------------------

    def _도망_클릭(self):
        확인라벨 = Label(text="도망치시겠습니까?")

        버튼틀 = BoxLayout(orientation="horizontal", size_hint=(1, 0.3), spacing=8)
        예버튼 = Button(text="예")
        아니오버튼 = Button(text="아니오")
        뒤로키_버튼(아니오버튼)
        버튼틀.add_widget(예버튼)
        버튼틀.add_widget(아니오버튼)

        본문 = BoxLayout(orientation="vertical", spacing=12, padding=12)
        본문.add_widget(확인라벨)
        본문.add_widget(버튼틀)

        팝업 = Popup(
            title="도망", content=본문, size_hint=(0.7, 0.35), auto_dismiss=False
        )
        예버튼.bind(on_release=lambda *_: self._도망_확인(팝업))
        아니오버튼.bind(on_release=lambda *_: 팝업.dismiss())
        팝업.open()

    def _도망_확인(self, 팝업):
        팝업.dismiss()
        앱 = App.get_running_app()
        self._엔진_실행(
            lambda: gameflow.아군_도망시도(앱.게임상태), lambda _: self.갱신()
        )

    # -------------------------------------------------
    # 전투 종료
    # -------------------------------------------------

    def _전투종료_처리(self):
        앱 = App.get_running_app()
        결과 = 앱.게임상태["전투상태"]["종료"]
        self.안내라벨.text = f"전투 종료: {결과}"
        self.액션틀.clear_widgets()

        확인버튼 = Button(text="확인")
        확인버튼.bind(on_release=self._전투종료_확인)
        self.액션틀.add_widget(확인버튼)

    def _전투종료_확인(self, *args):
        앱 = App.get_running_app()
        결과 = gameflow.전투_결과_정리(앱.게임상태)

        if 결과 == "적승리":
            # 이번 프로토타입에는 별도의 부활/페널티 시스템이 없다
            # (town_system.휴식_처리의 주석 참고 - "마을에 도착한 것
            # 자체를 무사히 돌아왔다로 취급"하는 임시 가정). 그래서 파티가
            # 전멸하면 HP/MP를 전부 회복시켜 마을로 돌려보낸다.
            gameflow.휴식(앱.게임상태)
            self.manager.get_screen("마을").갱신()
            self.manager.current = "마을"
        else:
            self.manager.get_screen("던전").갱신()
            self.manager.current = "던전"
