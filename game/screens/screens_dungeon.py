# =====================
# 던전 화면 - 던전 지도 위젯, 던전 목록, 던전
# =====================
# main.py가 game/screens/ 여섯 파일의 화면을 ScreenManager에 등록한다.

import math
import zlib

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle, Ellipse

import gameflow
from game.screens.screens_common import (
    _캐릭터이미지_경로,
    _에셋_경로,
)


# =====================================================
# 던전 맵 그리드를 그리는 위젯 (칸마다 타일 이미지 또는 색칠한 사각형 +
# 현재 위치를 표시하는 초상화 또는 원)
# =====================================================

_칸_색 = {
    "X": (0.2, 0.2, 0.2, 1),
    "O": (0.78, 0.9, 0.79, 1),
    "@": (1, 0.72, 0.3, 1),
    "#": (0.56, 0.79, 0.98, 1),
}
_기본_칸_색 = (0.4, 0.4, 0.4, 1)

# 던전 화면에 한 번에 보여줄 칸 수(가로/세로 동일) - 플레이어가 항상 이
# 뷰포트 정중앙에 오도록 그린다(아래 던전맵위젯._다시그리기 참고).
_뷰포트_크기 = 9
# 뷰포트가 실제 맵 범위를 벗어난 칸(지도 밖)을 칠하는 색 - "X"(벽)와
# 구분되게 더 어둡게 뒀다.
_맵밖_색 = (0, 0, 0, 1)

# 던전 지도 타일 이미지 (game/assets/dungeon/).
# 풀밭/흙길은 8x8 한 칸, 나무/게이트는 8x16 세로 2칸 - 아래 절반이 그
# 칸에 서고, 위 절반은 바로 윗칸에 겹쳐 그린다. 파일이 없으면 그 칸만
# _칸_색으로 칠한다.
_타일_파일 = {
    "풀밭": "asset_tile_grass.webp",
    "흙길": "asset_tile_dirt.webp",
    "나무": "asset_tile_tree.webp",
    "게이트": "asset_tile_gate.webp",
}
# 세로 2칸짜리 타일을 쓰는 지도 기호 ("X"=나무, "#"=게이트)
_높은타일_기호 = {"X": "나무", "#": "게이트"}
# 흙길 배치 - 좌표 기준으로 항상 같은 자리에 오도록 해시값 노이즈를
# 쓴다(무작위 아님). 덩어리 크기(칸)와 문턱값(클수록 흙길이 적어짐).
_흙길_덩어리크기 = 3
_흙길_문턱값 = 0.66


def _좌표해시(x, y, 시드):
    """(x, y, 시드)마다 항상 같은 0~1 사이 값을 돌려준다(파이썬 내장
    hash()는 실행할 때마다 값이 바뀌어서 쓰지 않는다)."""
    값 = (x * 374761393 + y * 668265263 + 시드 * 2246822519) & 0xFFFFFFFF
    값 = ((값 ^ (값 >> 13)) * 1274126177) & 0xFFFFFFFF
    return (값 ^ (값 >> 16)) / 0xFFFFFFFF


def _흙길_여부(x, y, 시드):
    """ "O" 칸에 흙길을 깔지 정한다. 굵은 격자의 해시값을 부드럽게
    이어서(값 노이즈) 흙길이 낱개로 흩어지지 않고 듬성듬성 덩어리지게
    하고, 칸마다 약간의 흔들림을 더해 경계를 자연스럽게 만든다."""
    크기 = _흙길_덩어리크기
    gx, gy = x / 크기, y / 크기
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = gx - x0, gy - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    위 = _좌표해시(x0, y0, 시드) * (1 - fx) + _좌표해시(x0 + 1, y0, 시드) * fx
    아래 = _좌표해시(x0, y0 + 1, 시드) * (1 - fx) + _좌표해시(x0 + 1, y0 + 1, 시드) * fx
    값 = 위 * (1 - fy) + 아래 * fy
    값 += (_좌표해시(x, y, 시드 + 1) - 0.5) * 0.3
    return 값 > _흙길_문턱값


class 던전맵위젯(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.그리드 = None
        self.위치 = None
        self.초상화코드 = None
        self._텍스처_캐시 = {}
        self._타일_캐시 = {}
        self._흙길시드 = 0
        self.오브젝트 = {}
        self.bind(size=self._다시그리기, pos=self._다시그리기)

    def 갱신(self, 그리드, 위치, 초상화코드=None, 던전파일명=None, 오브젝트=None):
        self.그리드 = 그리드
        self.위치 = 위치
        self.초상화코드 = 초상화코드
        # 던전마다 흙길 무늬가 달라지도록 파일명으로 시드를 정한다.
        self._흙길시드 = zlib.crc32((던전파일명 or "").encode("utf-8")) & 0xFFFF
        # 맵정보["오브젝트"] - "@" 칸에 전용 "타일"이 있는지 찾는 데 쓴다.
        self.오브젝트 = 오브젝트 or {}
        self._다시그리기()

    def _타일(self, 이름):
        """공용 타일(_타일_파일의 이름)의 텍스처를 돌려준다."""
        return self._파일_타일(_타일_파일[이름])

    def _파일_타일(self, 파일명):
        """game/assets/dungeon/의 타일 텍스처를 한 번만 읽어 캐시한다.
        도트를 크게 늘려도 번지지 않게 확대/축소 필터를 nearest로 둔다.
        파일이 없으면 None."""
        if 파일명 not in self._타일_캐시:
            텍스처 = None
            경로 = _에셋_경로("dungeon", 파일명)
            if 경로:
                try:
                    텍스처 = CoreImage(경로).texture
                    텍스처.mag_filter = "nearest"
                    텍스처.min_filter = "nearest"
                except Exception:
                    텍스처 = None
            self._타일_캐시[파일명] = 텍스처
        return self._타일_캐시[파일명]

    def _오브젝트_타일(self, 맵x, 맵y):
        """(맵x, 맵y) 오브젝트에 "타일"이 지정돼 있으면 그 텍스처를,
        없거나 파일이 없으면 None을 돌려준다."""
        정보 = self.오브젝트.get((맵x, 맵y))
        if not 정보 or not 정보.get("타일"):
            return None
        return self._파일_타일(정보["타일"])

    def _높은타일_반쪽(self, 이름):
        """세로 2칸 타일을 (아래 절반, 위 절반) 텍스처로 나눠 돌려준다.
        Kivy 텍스처는 왼쪽 아래가 원점이라 y=0 쪽이 아래 절반이다."""
        텍스처 = self._타일(이름)
        if 텍스처 is None:
            return None, None
        폭, 높이 = 텍스처.size
        반 = 높이 // 2
        return 텍스처.get_region(0, 0, 폭, 반), 텍스처.get_region(0, 반, 폭, 반)

    def _플레이어_텍스처(self):
        """선택된 모험단 프로필 이미지의 텍스처를 돌려준다. 아직 실제
        webp 파일이 없거나(개발 중), 코드가 없으면 None을 돌려주고,
        _다시그리기는 그 경우 원(Ellipse)으로 대신 그린다."""
        코드 = self.초상화코드
        if 코드 is None:
            return None
        if 코드 not in self._텍스처_캐시:
            try:
                self._텍스처_캐시[코드] = CoreImage(_캐릭터이미지_경로(코드)).texture
            except Exception:
                self._텍스처_캐시[코드] = None
        return self._텍스처_캐시[코드]

    def _칸_문자(self, x, y):
        """(x, y)가 그리드 범위를 벗어나면 None(맵 밖)을 돌려준다."""
        if self.그리드 is None or y < 0 or y >= len(self.그리드):
            return None
        행 = self.그리드[y]
        if x < 0 or x >= len(행):
            return None
        return 행[x]

    def _다시그리기(self, *args):
        self.canvas.clear()
        if (
            self.그리드 is None
            or self.위치 is None
            or self.width <= 0
            or self.height <= 0
        ):
            return

        # 맵 전체를 위젯 크기에 맞춰 축소하는 대신, 플레이어를 중심으로
        # _뷰포트_크기 x _뷰포트_크기 칸만 고정 크기로 그린다 - 맵이
        # 커져도 칸 크기는 그대로고, 플레이어가 움직이면 그 칸 창이
        # 함께 움직이는 방식(카메라가 플레이어를 따라간다).
        칸폭 = self.width / _뷰포트_크기
        칸높이 = self.height / _뷰포트_크기
        중심x, 중심y = self.위치
        반칸 = _뷰포트_크기 // 2

        def 칸위치(화면x, 화면y):
            # 지도 데이터는 y=0이 맨 윗줄이지만, Kivy 좌표는
            # 왼쪽 아래가 원점이라 아래에서부터 그려 올라간다.
            return (self.x + 화면x * 칸폭, self.y + self.height - (화면y + 1) * 칸높이)

        칸크기 = (칸폭, 칸높이)
        풀밭 = self._타일("풀밭")
        흙길 = self._타일("흙길")

        with self.canvas:
            # 1단계 - 바닥. "O"는 풀밭(좌표에 따라 흙길), "X"/"#"은 그 위에
            # 나무/게이트를 올릴 풀밭, "@"는 오브젝트에 "타일"이 있으면
            # 풀밭 위에 그 타일, 없으면 기존 색 그대로, 지도 밖은 검정.
            for 화면y in range(_뷰포트_크기):
                for 화면x in range(_뷰포트_크기):
                    맵x = 중심x - 반칸 + 화면x
                    맵y = 중심y - 반칸 + 화면y
                    문자 = self._칸_문자(맵x, 맵y)
                    바닥 = None
                    if 문자 == "O":
                        바닥 = (
                            흙길
                            if (
                                흙길 is not None
                                and _흙길_여부(맵x, 맵y, self._흙길시드)
                            )
                            else 풀밭
                        )
                    elif (
                        문자 in _높은타일_기호
                        and self._타일(_높은타일_기호[문자]) is not None
                    ):
                        바닥 = 풀밭
                    오브젝트타일 = (
                        self._오브젝트_타일(맵x, 맵y) if 문자 == "@" else None
                    )
                    if 오브젝트타일 is not None and 풀밭 is not None:
                        바닥 = 풀밭
                    if 바닥 is not None:
                        Color(1, 1, 1, 1)
                        Rectangle(texture=바닥, pos=칸위치(화면x, 화면y), size=칸크기)
                        if 오브젝트타일 is not None:
                            Rectangle(
                                texture=오브젝트타일,
                                pos=칸위치(화면x, 화면y),
                                size=칸크기,
                            )
                    else:
                        Color(
                            *(
                                _맵밖_색
                                if 문자 is None
                                else _칸_색.get(문자, _기본_칸_색)
                            )
                        )
                        Rectangle(pos=칸위치(화면x, 화면y), size=칸크기)

            # 2단계 - 나무/게이트(세로 2칸). 윗줄부터 차례로 그려서 아래쪽
            # 나무의 위 절반이 윗칸 위에 겹치게 한다. 뷰포트 바로 아래 줄에
            # 서 있는 것도 위 절반만은 맨 아랫줄에 보이므로 한 줄 더 돈다.
            Color(1, 1, 1, 1)
            for 화면y in range(_뷰포트_크기 + 1):
                for 화면x in range(_뷰포트_크기):
                    문자 = self._칸_문자(중심x - 반칸 + 화면x, 중심y - 반칸 + 화면y)
                    if 문자 not in _높은타일_기호:
                        continue
                    아래절반, 위절반 = self._높은타일_반쪽(_높은타일_기호[문자])
                    if 아래절반 is None:
                        continue
                    if 화면y < _뷰포트_크기:
                        Rectangle(
                            texture=아래절반, pos=칸위치(화면x, 화면y), size=칸크기
                        )
                    if 화면y >= 1:
                        Rectangle(
                            texture=위절반, pos=칸위치(화면x, 화면y - 1), size=칸크기
                        )

            # 플레이어는 항상 뷰포트 정중앙 칸(반칸, 반칸)에 그린다.
            # 모험단 프로필 이미지가 있으면 그 이미지를, 없으면(파일이
            # 아직 없거나 코드 미설정) 빨간 원을 그린다.
            여백폭 = 칸폭 * 0.2
            여백높이 = 칸높이 * 0.2
            플레이어위치 = (
                self.x + 반칸 * 칸폭 + 여백폭,
                self.y + self.height - (반칸 + 1) * 칸높이 + 여백높이,
            )
            플레이어크기 = (칸폭 - 여백폭 * 2, 칸높이 - 여백높이 * 2)
            텍스처 = self._플레이어_텍스처()
            if 텍스처 is not None:
                Color(1, 1, 1, 1)
                Rectangle(texture=텍스처, pos=플레이어위치, size=플레이어크기)
            else:
                Color(1, 0.15, 0.15, 1)
                Ellipse(pos=플레이어위치, size=플레이어크기)


# =====================================================
# 4-1. 던전 목록 화면 (마을 -> 던전 사이에 들어가는 선택 화면)
# =====================================================


class 던전목록화면(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        루트 = BoxLayout(orientation="vertical", padding=16, spacing=10)
        루트.add_widget(Label(text="던전 이동", font_size=40, size_hint=(1, 0.12)))

        self.목록틀 = BoxLayout(orientation="vertical", size_hint=(1, 0.68), spacing=8)
        루트.add_widget(self.목록틀)

        self.안내라벨 = Label(text="", size_hint=(1, 0.1))
        루트.add_widget(self.안내라벨)

        뒤로버튼 = Button(text="뒤로", size_hint=(1, 0.1))
        뒤로버튼.bind(on_release=lambda *_: setattr(self.manager, "current", "마을"))
        루트.add_widget(뒤로버튼)

        self.add_widget(루트)

    def on_pre_enter(self, *args):
        self.갱신()

    def 갱신(self):
        self.목록틀.clear_widgets()
        앱 = App.get_running_app()
        던전목록 = gameflow.이동가능던전목록(앱.게임상태)

        if not 던전목록:
            self.안내라벨.text = "이 마을에서 갈 수 있는 던전이 없습니다."
            return
        self.안내라벨.text = ""

        for 파일명 in 던전목록:
            맵정보 = gameflow.던전_레지스트리.get(파일명, {})
            표시이름 = 맵정보.get("지도명", 파일명)
            버튼 = Button(text=표시이름, size_hint=(1, None), height=56)
            버튼.bind(on_release=lambda inst, f=파일명: self._선택(f))
            self.목록틀.add_widget(버튼)

    def _선택(self, 파일명):
        앱 = App.get_running_app()
        gameflow.던전_진입(앱.게임상태, 파일명)
        self.manager.get_screen("던전").갱신()
        self.manager.current = "던전"


# =====================================================
# 5. 던전 이동 화면
# =====================================================


class 던전화면(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._대기중오브젝트 = None

        루트 = BoxLayout(orientation="vertical", padding=16, spacing=8)

        self.상태라벨 = Label(
            text="",
            size_hint=(1, 0.14),
            halign="left",
            valign="top",
            font_size=26,
        )
        self.상태라벨.bind(
            size=lambda *_: setattr(
                self.상태라벨,
                "text_size",
                self.상태라벨.size,
            )
        )
        루트.add_widget(self.상태라벨)

        self.지도위젯 = 던전맵위젯(size_hint=(1, 0.36))
        루트.add_widget(self.지도위젯)

        방향틀 = GridLayout(cols=3, size_hint=(1, 0.28), spacing=6)

        파티버튼 = Button(text="파티")
        파티버튼.bind(on_release=self._파티_클릭)
        방향틀.add_widget(파티버튼)

        위버튼 = Button(text="▲")
        위버튼.bind(on_release=lambda *_: self._이동("위"))
        방향틀.add_widget(위버튼)

        메뉴버튼 = Button(text="메뉴")
        메뉴버튼.bind(on_release=self._메뉴_클릭)
        방향틀.add_widget(메뉴버튼)

        왼쪽버튼 = Button(text="◀")
        왼쪽버튼.bind(on_release=lambda *_: self._이동("왼쪽"))
        방향틀.add_widget(왼쪽버튼)

        self.상호작용버튼 = Button(text="상호작용", disabled=True)
        self.상호작용버튼.bind(on_release=self._상호작용)
        방향틀.add_widget(self.상호작용버튼)

        오른쪽버튼 = Button(text="▶")
        오른쪽버튼.bind(on_release=lambda *_: self._이동("오른쪽"))
        방향틀.add_widget(오른쪽버튼)

        방향틀.add_widget(Label())
        아래버튼 = Button(text="▼")
        아래버튼.bind(on_release=lambda *_: self._이동("아래"))
        방향틀.add_widget(아래버튼)
        방향틀.add_widget(Label())

        루트.add_widget(방향틀)

        self.메시지라벨 = Label(text="", size_hint=(1, 0.22))
        루트.add_widget(self.메시지라벨)

        self.add_widget(루트)

    def 갱신(self):
        앱 = App.get_running_app()
        게임상태 = 앱.게임상태
        던전상태 = 게임상태["던전상태"]

        줄들 = [
            f"{캐릭터['캐릭터명']} Lv.{캐릭터['레벨']}  "
            f"HP {캐릭터['현재HP']}/{gameflow.캐릭터_최대HP(게임상태, 캐릭터)}  "
            f"MP {캐릭터['현재MP']}/{gameflow.캐릭터_최대MP(게임상태, 캐릭터)}"
            for 캐릭터 in 게임상태["파티"]["파티원"]
        ]
        줄들.append(f"위치 {던전상태['위치']}  걸음수 {던전상태['걸음수']}")
        self.상태라벨.text = "\n".join(줄들)
        self.지도위젯.갱신(
            던전상태["그리드"],
            던전상태["위치"],
            게임상태.get("선택된초상화"),
            던전상태.get("던전파일명"),
            던전상태["맵정보"].get("오브젝트"),
        )
        self.메시지라벨.text = ""
        self.상호작용버튼.disabled = True
        self._대기중오브젝트 = None

    def _이동(self, 방향):
        앱 = App.get_running_app()
        결과 = gameflow.던전_이동(앱.게임상태, 방향)

        if 결과["결과"] == "이동불가":
            self.메시지라벨.text = "그 쪽으로는 갈 수 없습니다."

        elif 결과["결과"] == "오브젝트":
            self._대기중오브젝트 = (결과["위치"], 결과["오브젝트"])
            self.상호작용버튼.disabled = False
            self.메시지라벨.text = "무언가 있습니다. '말 걸기'를 눌러보세요."

        elif 결과["결과"] == "전투시작":
            self.manager.get_screen("전투").갱신(신규=True)
            self.manager.current = "전투"
            return

        elif 결과["결과"] == "이동":
            self.갱신()
            연결지역 = 결과.get("연결지역")
            if 연결지역 is not None:
                처리 = gameflow.연결지역_처리(앱.게임상태, 연결지역)
                if 처리["타입"] == "마을":
                    self.manager.get_screen("마을").갱신()
                    self.manager.current = "마을"
                    return
                elif 처리["타입"] == "던전":
                    # 다른 던전으로 이어지는 연결점 - 새 던전 지도로 바로
                    # 갱신한다.
                    self.갱신()
                    self.메시지라벨.text = f"{처리['지도명']}(으)로 이동했습니다."
                    return
                else:
                    self.메시지라벨.text = (
                        "이 앞은 다른 지역으로 이어지지만, 이번 프로토타입에는 "
                        "아직 구현돼 있지 않습니다."
                    )

    def _상호작용(self, *args):
        if self._대기중오브젝트 is None:
            return
        위치, 오브젝트 = self._대기중오브젝트
        앱 = App.get_running_app()
        결과 = gameflow.오브젝트_상호작용(앱.게임상태, 위치, 오브젝트)

        if 결과["결과"] == "전투시작":
            self.manager.get_screen("전투").갱신(신규=True)
            self.manager.current = "전투"
            return
        elif 결과["결과"] == "미지원":
            self.메시지라벨.text = (
                결과.get("설명") or "여긴 아직 아무 일도 일어나지 않습니다."
            )
        else:
            self.메시지라벨.text = "몬스터 데이터가 없어 전투를 시작할 수 없습니다."

        self.상호작용버튼.disabled = True
        self._대기중오브젝트 = None

    def _메뉴_클릭(self, *args):
        self.메시지라벨.text = "메뉴는 아직 구현되지 않았습니다."

    def _파티_클릭(self, *args):
        self.manager.get_screen("파티관리").복귀화면 = "던전"
        self.manager.current = "파티관리"
