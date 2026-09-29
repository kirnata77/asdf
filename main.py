# =====================
# Kivy 앱 진입점 (main_system.py의 "앱" 클래스 대응)
# =====================
import os
import sys
import traceback
import datetime

# -----------------------------------------------------
# 임시 디버그용: 화면(Loading...)이 뜨자마자 바로 꺼지는 건, 앱이 아직
# Kivy 화면을 띄우기도 전 - 즉 아래 import/초기화 단계에서 예외가 나서
# 죽는 경우다. 이 시점의 예외는 Kivy의 ExceptionManager(이 파일 아래쪽)로는
#못 잡는다(그건 화면이 뜬 다음, 이벤트 루프 안에서 난 예외만 잡음).
# 대신 파이썬이 처리 못 한 예외를 마지막에 항상 거치는 sys.excepthook을
# 덮어써서, 어떤 단계에서 죽든 오류 내용을 폰 Download 폴더에 파일로
# 남긴다. USB/adb 없이(회사 PC라 연결 불가) 원인을 확인하기 위한
# 안전장치이며, 원인이 확인되면 이 블록은 제거해도 된다.
def _크래시로그_저장(exc_type, exc_value, exc_tb):
    오류내용 = (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        + "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    )
    print(오류내용)
    try:
        저장경로 = "/storage/emulated/0/Download/dnf_crash_log.txt"
        with open(저장경로, "w", encoding="utf-8") as f:
            f.write(오류내용)
    except Exception:
        pass


sys.excepthook = _크래시로그_저장

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, NoTransition

# Kivy 기본 폰트(Roboto)에는 한글 글자가 없어서 화면에 네모(□)로 깨져
# 보이는 문제가 있다. 한때는 이 파일 용량을 아예 없애려고 기기에 이미
# 깔려 있는 시스템 한글 폰트를 쓰는 방식(경로 후보를 순서대로 탐색)을
# 썼었는데, 기기마다 경로가 달라 일부 기기에서는 다시 깨질 위험이 있어서
# 폐기했다. 대신 나눔고딕을 fontTools로 다이어트(힌팅/GSUB/GPOS/DSIG 등
# 렌더링에 불필요한 테이블만 제거, 글자 커버리지는 원본과 동일하게 유지)
# 시킨 단일 폰트 파일 하나(game/assets/font/NanumGothic-Diet.ttf, 약
# 1.3MB - 원본 나눔고딕 Regular 약 2.0MB 대비 축소)를 앱에 직접 담아
# "Roboto" 별칭을 덮어쓰는 방식으로 되돌아갔다(2026-09-22).
#
# 볼드체 파일은 따로 안 담았다 - fn_bold를 생략하면 Kivy가 볼드 스타일
# 텍스트에도 자동으로 fn_regular를 대신 쓴다(볼드 느낌은 안 나지만 글자는
# 정상 표시된다).
_폰트_경로 = os.path.join(
    os.path.dirname(__file__), "game", "assets", "font", "NanumGothic-Diet.ttf",
)
LabelBase.register(name="Roboto", fn_regular=_폰트_경로)

# -----------------------------------------------------
# 임시 디버그용: 버튼 클릭 등 이벤트 처리 중 예외가 나도 앱이 그냥
# 종료되지 않고, 오류 내용을 화면에 팝업으로 띄운다. USB/adb 없이도
# (회사 PC라 USB 연결이 안 되는 환경) 크래시 원인을 스크린샷으로
# 공유받기 위한 안전장치다 - 원인이 확인되면 이 블록은 제거해도 된다.
from kivy.base import ExceptionHandler, ExceptionManager
from kivy.core.clipboard import Clipboard
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button


def _오류_팝업_띄우기(내용):
    라벨 = Label(
        text=내용, size_hint_y=None, halign="left", valign="top", font_size=12,
    )
    라벨.bind(
        texture_size=lambda inst, size: setattr(inst, "height", size[1]),
        width=lambda inst, w: setattr(inst, "text_size", (w, None)),
    )
    스크롤 = ScrollView()
    스크롤.add_widget(라벨)

    복사버튼 = Button(text="오류 내용 복사하기", size_hint=(1, 0.12))

    def _복사(*args):
        Clipboard.copy(내용)
        복사버튼.text = "복사됨! (대화창에 붙여넣기)"

    복사버튼.bind(on_release=_복사)

    본문 = BoxLayout(orientation="vertical", spacing=8)
    본문.add_widget(스크롤)
    본문.add_widget(복사버튼)

    Popup(
        title="오류 발생 - 아래 버튼으로 복사해서 공유해 주세요",
        content=본문, size_hint=(0.95, 0.9),
    ).open()


class _오류처리기(ExceptionHandler):
    def handle_exception(self, inst):
        내용 = "".join(traceback.format_exception(type(inst), inst, inst.__traceback__))
        print(내용)
        try:
            _오류_팝업_띄우기(내용)
        except Exception:
            pass
        return ExceptionManager.PASS


ExceptionManager.add_handler(_오류처리기())

# 화면은 game/screens/ 아래 6개 파일로 나뉘어 있다(2026-09-29, 예전 screens.py).
from game.screens.screens_menu import (
    메인메뉴화면, 파티생성화면, 불러오기목록화면, 저장목록화면, 옵션화면,
)
from game.screens.screens_town import 마을화면, 마을이동목록화면, 상점화면, 모험단화면
from game.screens.screens_dungeon import 던전목록화면, 던전화면
from game.screens.screens_battle import 전투화면
from game.screens.screens_party import 파티관리화면, 파티원화면


class DnfMobileApp(App):
    title = "던전앤파이터 모바일 프로토타입"

    def build(self):
        self.게임상태 = None

        매니저 = ScreenManager(transition=NoTransition())
        매니저.add_widget(메인메뉴화면(name="메인메뉴"))
        매니저.add_widget(파티생성화면(name="파티생성"))
        매니저.add_widget(불러오기목록화면(name="불러오기목록"))
        매니저.add_widget(저장목록화면(name="저장목록"))
        매니저.add_widget(옵션화면(name="옵션"))
        매니저.add_widget(마을화면(name="마을"))
        매니저.add_widget(마을이동목록화면(name="마을이동목록"))
        매니저.add_widget(파티관리화면(name="파티관리"))
        매니저.add_widget(파티원화면(name="파티원"))
        매니저.add_widget(던전목록화면(name="던전목록"))
        매니저.add_widget(던전화면(name="던전"))
        매니저.add_widget(상점화면(name="상점"))
        매니저.add_widget(전투화면(name="전투"))
        매니저.add_widget(모험단화면(name="모험단"))
        매니저.current = "메인메뉴"
        return 매니저


if __name__ == "__main__":
    DnfMobileApp().run()