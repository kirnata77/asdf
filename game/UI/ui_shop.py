# =====================
# 상점 화면
# =====================
# 마을의 [상점] 버튼을 누르면 main_system.py가 여는 팝업(Toplevel)이다.
# 구매/판매 로직은 전부 shop_system.py가 처리하고, 이 파일은 화면만 그린다.
#
# 화면 흐름
#   메인 : [구매] [판매] [나가기]           (나가기 = 팝업 닫기)
#   구매/판매 : [장비] [소모품] [재료]      (재료는 아직 미구현)
#   장비   : 부위 탭(무기/상의/하의/어깨/벨트/신발/목걸이/반지/팔찌/
#            보조장비/마법석/귀걸이) - 무기 탭에는 모든 직업 무기가 있다.
#   소모품 : 포션/투척 아이템/음식 탭
#   각 탭의 리스트 한 줄 : 이름 / [자세히보기] / 단가 / 수량(스핀박스) /
#            합계 가격 / [구매] 또는 [판매]
#            (판매 리스트는 소지품에 있는 아이템만, 장착 장비 제외)
#
# X/ESC는 한 단계 뒤로 가고, 메인 화면에서는 팝업을 닫는다
# (ui_system.공통조작키_바인딩 규칙).

import tkinter as tk
from tkinter import ttk

from game.system import shop_system
from game.system import ui_system

_상세_제외키 = {"이름"}


def _값_문자열(값):
    if isinstance(값, dict):
        return ", ".join(f"{k} {v:+d}" if isinstance(v, int) else f"{k} {v}"
                         for k, v in 값.items())
    if isinstance(값, (list, tuple)):
        return ", ".join(str(v) for v in 값)
    return str(값)


class 상점팝업(tk.Toplevel):
    """플레이어      : player_system.py 플레이어 딕셔너리("소지품"/"파티").
    카탈로그      : shop_system.카탈로그_생성() 결과.
    상점판매목록  : 이 마을 상점이 파는 아이템 이름 리스트(town 파일의
                    "상점판매목록"). None이면 shop_system 임시 동작.
    종료콜백      : 팝업이 닫힐 때 인자 없이 호출한다(생략 가능).
    """

    def __init__(self, master, 플레이어, 카탈로그, 상점판매목록=None, 종료콜백=None):
        super().__init__(master)
        self.title("상점")
        self.geometry("640x460")
        self.플레이어 = 플레이어
        self.카탈로그 = 카탈로그
        self.상점판매목록 = 상점판매목록
        self.종료콜백 = 종료콜백
        self._뒤로동작 = self._닫기
        self._탭프레임 = {}

        # 모달 - 뒤 화면(마을) 조작을 막는다(_설정메뉴와 같은 방식).
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._닫기)

        self.골드라벨 = tk.Label(self, text="", anchor="e", font=("", 10, "bold"))
        self.골드라벨.pack(fill="x", padx=12, pady=(8, 0))
        self._골드_갱신()

        self.본문틀 = tk.Frame(self)
        self.본문틀.pack(fill="both", expand=True, padx=12, pady=8)

        self.상태메시지 = tk.Label(self, text="", anchor="w", fg="blue")
        self.상태메시지.pack(fill="x", padx=12, pady=(0, 8))

        self._메인_화면()
        ui_system.공통조작키_바인딩(self, 취소콜백=self._뒤로)

    # -------------------------------------------------
    # 공통
    # -------------------------------------------------

    def _닫기(self):
        self.destroy()
        if self.종료콜백 is not None:
            self.종료콜백()

    def _뒤로(self):
        self._뒤로동작()

    def _골드_갱신(self):
        self.골드라벨.config(
            text=f"보유 골드: {shop_system.보유_골드(self.플레이어)}G"
        )

    def _메시지(self, 글, 오류=False):
        self.상태메시지.config(text=글, fg="red" if 오류 else "blue")

    def _본문_비우기(self):
        for 위젯 in self.본문틀.winfo_children():
            위젯.destroy()
        self._탭프레임 = {}

    # -------------------------------------------------
    # 화면 1 : 구매 / 판매 / 나가기
    # -------------------------------------------------

    def _메인_화면(self):
        self._본문_비우기()
        self._뒤로동작 = self._닫기
        tk.Label(self.본문틀, text="상점", font=("", 14, "bold")).pack(pady=(30, 16))
        tk.Button(
            self.본문틀, text="구매", width=16,
            command=lambda: self._대분류_화면("구매"),
        ).pack(pady=4)
        tk.Button(
            self.본문틀, text="판매", width=16,
            command=lambda: self._대분류_화면("판매"),
        ).pack(pady=4)
        tk.Button(
            self.본문틀, text="나가기", width=16, command=self._닫기,
        ).pack(pady=4)

    # -------------------------------------------------
    # 화면 2 : 장비 / 소모품 / 재료
    # -------------------------------------------------

    def _대분류_화면(self, 모드):
        self._본문_비우기()
        self._뒤로동작 = self._메인_화면
        self._메시지("")
        tk.Label(self.본문틀, text=모드, font=("", 14, "bold")).pack(pady=(30, 16))
        tk.Button(
            self.본문틀, text="장비", width=16,
            command=lambda: self._목록_화면(모드, "장비"),
        ).pack(pady=4)
        tk.Button(
            self.본문틀, text="소모품", width=16,
            command=lambda: self._목록_화면(모드, "소모품"),
        ).pack(pady=4)
        tk.Button(
            self.본문틀, text="재료", width=16,
            command=lambda: self._재료_화면(모드),
        ).pack(pady=4)
        tk.Button(
            self.본문틀, text="뒤로", width=16, command=self._메인_화면,
        ).pack(pady=(12, 4))

    def _재료_화면(self, 모드):
        # 재료 상점은 아직 미구현.
        self._본문_비우기()
        self._뒤로동작 = lambda: self._대분류_화면(모드)
        tk.Label(self.본문틀, text=f"{모드} - 재료", font=("", 14, "bold")).pack(pady=(30, 8))
        tk.Label(self.본문틀, text="아직 미구현이다.").pack(pady=8)
        tk.Button(
            self.본문틀, text="뒤로", width=16,
            command=lambda: self._대분류_화면(모드),
        ).pack(pady=8)

    # -------------------------------------------------
    # 화면 3 : 부위/종류 탭 + 리스트
    # -------------------------------------------------

    def _목록_화면(self, 모드, 대분류):
        self._본문_비우기()
        self._뒤로동작 = lambda: self._대분류_화면(모드)
        self._메시지("")

        상단 = tk.Frame(self.본문틀)
        상단.pack(fill="x")
        tk.Button(
            상단, text="◀ 뒤로", command=lambda: self._대분류_화면(모드),
        ).pack(side="left")
        tk.Label(상단, text=f"{모드} - {대분류}", font=("", 12, "bold")).pack(
            side="left", padx=10
        )

        노트북 = ttk.Notebook(self.본문틀)
        노트북.pack(fill="both", expand=True, pady=(6, 0))

        for 탭 in shop_system.탭_목록(대분류):
            탭틀 = tk.Frame(노트북)
            노트북.add(탭틀, text=탭)
            안쪽 = self._스크롤틀_만들기(탭틀)
            self._탭프레임[탭] = 안쪽
            self._행_채우기(안쪽, 모드, 대분류, 탭)

    def _스크롤틀_만들기(self, 부모):
        캔버스 = tk.Canvas(부모, highlightthickness=0)
        스크롤 = tk.Scrollbar(부모, orient="vertical", command=캔버스.yview)
        안쪽 = tk.Frame(캔버스)
        안쪽.bind(
            "<Configure>",
            lambda e: 캔버스.configure(scrollregion=캔버스.bbox("all")),
        )
        캔버스.create_window((0, 0), window=안쪽, anchor="nw")
        캔버스.configure(yscrollcommand=스크롤.set)
        캔버스.pack(side="left", fill="both", expand=True)
        스크롤.pack(side="right", fill="y")
        return 안쪽

    def _행_채우기(self, 안쪽, 모드, 대분류, 탭):
        for 위젯 in 안쪽.winfo_children():
            위젯.destroy()

        if 모드 == "구매":
            항목목록 = [
                (아이템, shop_system.최대_구매수량)
                for 아이템 in shop_system.구매목록(
                    self.카탈로그, 대분류, 탭, self.상점판매목록
                )
            ]
            빈문구 = "(팔고 있는 물건이 없다)"
        else:
            항목목록 = shop_system.판매목록(self.플레이어, self.카탈로그, 대분류, 탭)
            빈문구 = "(팔 수 있는 물건이 없다)"

        if not 항목목록:
            tk.Label(안쪽, text=빈문구, fg="gray").pack(anchor="w", padx=6, pady=8)
            return

        for 아이템, 최대수량 in 항목목록:
            self._행_만들기(안쪽, 모드, 대분류, 탭, 아이템, 최대수량)

    def _행_만들기(self, 안쪽, 모드, 대분류, 탭, 아이템, 최대수량):
        이름 = 아이템["이름"]
        단가 = 아이템["가격"] if 모드 == "구매" else shop_system.판매가(아이템)

        행 = tk.Frame(안쪽)
        행.pack(fill="x", padx=4, pady=2)

        tk.Label(행, text=이름, width=20, anchor="w").pack(side="left")
        tk.Button(
            행, text="자세히보기",
            command=lambda a=아이템: self._자세히보기(a),
        ).pack(side="left", padx=2)
        tk.Label(행, text=f"{단가}G", width=6, anchor="e").pack(side="left")
        if 모드 == "판매":
            tk.Label(행, text=f"보유 {최대수량}", width=7).pack(side="left")

        수량변수 = tk.IntVar(value=1)
        tk.Spinbox(
            행, from_=1, to=최대수량, width=4, textvariable=수량변수,
        ).pack(side="left", padx=4)

        합계라벨 = tk.Label(행, text=f"{단가}G", width=8, anchor="e")
        합계라벨.pack(side="left")

        def 합계_갱신(*_):
            try:
                수 = 수량변수.get()
            except tk.TclError:
                수 = 0
            합계라벨.config(text=f"{단가 * 수}G")

        수량변수.trace_add("write", 합계_갱신)

        tk.Button(
            행, text=모드, width=5,
            command=lambda: self._거래_클릭(모드, 대분류, 탭, 이름, 수량변수),
        ).pack(side="left", padx=4)

    # -------------------------------------------------
    # 거래
    # -------------------------------------------------

    def _거래_클릭(self, 모드, 대분류, 탭, 이름, 수량변수):
        try:
            수량 = 수량변수.get()
        except tk.TclError:
            self._메시지("수량이 올바르지 않다.", 오류=True)
            return

        try:
            if 모드 == "구매":
                금액 = shop_system.구매_처리(
                    self.플레이어, self.카탈로그, 대분류, 탭, 이름, 수량,
                    self.상점판매목록,
                )
                self._메시지(f"{이름} {수량}개를 {금액}G에 샀다.")
            else:
                금액 = shop_system.판매_처리(
                    self.플레이어, self.카탈로그, 대분류, 탭, 이름, 수량,
                )
                self._메시지(f"{이름} {수량}개를 {금액}G에 팔았다.")
        except ValueError as e:
            self._메시지(str(e), 오류=True)
            return

        self._골드_갱신()
        if 모드 == "판매":
            # 보유 수량이 바뀌므로 그 탭의 리스트를 다시 그린다.
            self._행_채우기(self._탭프레임[탭], 모드, 대분류, 탭)

    # -------------------------------------------------
    # 자세히보기
    # -------------------------------------------------

    def _자세히보기(self, 아이템):
        창 = tk.Toplevel(self)
        창.title(아이템["이름"])
        창.resizable(False, False)
        창.transient(self)

        tk.Label(창, text=아이템["이름"], font=("", 12, "bold")).pack(
            padx=16, pady=(12, 6)
        )
        내용 = tk.Frame(창)
        내용.pack(padx=16, pady=(0, 8))
        for 키, 값 in 아이템.items():
            if 키 in _상세_제외키 or 값 in (None, 0, "", {}, []):
                continue
            tk.Label(내용, text=f"{키}: {_값_문자열(값)}", anchor="w",
                     justify="left", wraplength=320).pack(fill="x", pady=1)

        tk.Button(창, text="닫기", command=창.destroy).pack(pady=(0, 12))