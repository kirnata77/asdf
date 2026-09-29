# =====================
# 캐릭터 화면
# =====================
# 파티 화면에서 캐릭터 한 명을 누르면 열리는 화면이다. 위쪽 탭이 두 개다.
#   [장비] 던전앤파이터 장비 창을 참고한 배치 - 가운데 캐릭터, 왼쪽에
#          방어구, 오른쪽에 무기/칭호/악세/특수장비. 칸을 누르면 팝업이
#          떠서 착용 중인 장비 이름과 [교체] [닫기]가 나온다.
#          [교체]를 누르면 소지품 중 그 부위에 맞는 아이템 리스트가 나오고,
#          착용할 수 없는 아이템도 회색으로 사유와 함께 나온다.
#   [상태] 능력치/파생 스탯/보유 특성. ui_status.py를 그대로 쓰되, 이
#          파일이 ui_status.py를 직접 import하지 않고 main_system.py가
#          넘겨주는 상태탭생성 함수로 만든다(화면끼리는 서로 부르지 않고
#          main_system.py를 통해서만 오간다는 기존 관례).
#
# 칸 배치 (왼쪽 2열 / 오른쪽 2열)
#     어깨    상의   [캐릭터]   무기      칭호
#     벨트    하의              팔찌      목걸이
#     신발                      보조장비  반지
#                               마법석    귀걸이
#
# 칭호 칸은 아직 미구현이다(데이터/슬롯이 없음) - 눌러도 "미구현" 팝업만 뜬다.
#
# 소지품 규칙: 소지품["장비"]에는 장착 중인 아이템도 개수에 포함되어 있고
# (equipment_system.장착품_소지품_동기화 참고), 교체 리스트에는 장착 중인
# 것(이 캐릭터든 다른 파티원이든)을 뺀 나머지만 나온다. 그래서 교체 자체는
# 소지품 개수를 바꾸지 않고 장착 슬롯의 이름만 바꾼다.

import tkinter as tk
from tkinter import ttk

from game.system import equipment_system

_왼쪽_배치 = [
    ["어깨", "상의"],
    ["벨트", "하의"],
    ["신발", None],
]
_오른쪽_배치 = [
    ["무기", "칭호"],
    ["팔찌", "목걸이"],
    ["보조장비", "반지"],
    ["마법석", "귀걸이"],
]
_미구현_슬롯 = {"칭호"}


class 캐릭터화면(tk.Frame):
    """플레이어      : player_system.py 플레이어 딕셔너리 ("소지품"/"파티").
    캐릭터        : 보여줄 파티원(character_data_system.py 캐릭터 딕셔너리).
    카탈로그      : shop_system.카탈로그_생성() 결과 - 카탈로그["장비"][슬롯]
                    으로 그 부위 아이템 데이터({이름: 데이터})를 찾는다.
    상태탭생성    : (부모위젯, 캐릭터) -> 상태 탭 안에 채울 위젯. 생략하면
                    상태 탭에 "(미연결)"만 뜬다. 탭을 열 때마다 새로 만든다
                    (장비를 바꾼 뒤 AC 등이 다시 계산되도록).
    장비변경콜백  : 장비를 교체하는 데 성공하면 인자 없이 호출(생략 가능).
                    main_system.py가 장비데이터모음을 다시 만드는 데 쓴다.
    """

    def __init__(self, master, 플레이어, 캐릭터, 카탈로그,
                 상태탭생성=None, 장비변경콜백=None):
        super().__init__(master)
        self.플레이어 = 플레이어
        self.캐릭터 = 캐릭터
        self.카탈로그 = 카탈로그
        self.상태탭생성 = 상태탭생성
        self.장비변경콜백 = 장비변경콜백
        self._슬롯버튼 = {}

        self.노트북 = ttk.Notebook(self)
        self.노트북.pack(fill="both", expand=True, padx=8, pady=8)

        self.장비탭 = tk.Frame(self.노트북)
        self.상태탭 = tk.Frame(self.노트북)
        self.노트북.add(self.장비탭, text="장비")
        self.노트북.add(self.상태탭, text="상태")

        self._장비탭_구성()
        self.노트북.bind("<<NotebookTabChanged>>", self._탭_바뀜)

    # -------------------------------------------------
    # 장비 탭
    # -------------------------------------------------

    def _장비탭_구성(self):
        틀 = tk.Frame(self.장비탭)
        틀.pack(expand=True, pady=10)

        self._칸_격자_만들기(틀, _왼쪽_배치).grid(row=0, column=0, padx=8)

        중앙 = tk.Frame(틀, bg="black", width=190, height=300)
        중앙.grid(row=0, column=1, padx=8)
        중앙.grid_propagate(False)
        중앙.pack_propagate(False)
        tk.Label(
            중앙, text="[캐릭터 일러스트 자리]", fg="white", bg="black",
        ).pack(expand=True)
        tk.Label(
            중앙, text=self.캐릭터["캐릭터명"], fg="white", bg="black",
            font=("", 11, "bold"),
        ).pack()
        tk.Label(
            중앙,
            text=f"Lv.{self.캐릭터['레벨']}  {self.캐릭터.get('직업') or '무직업'}",
            fg="white", bg="black",
        ).pack(pady=(0, 12))

        self._칸_격자_만들기(틀, _오른쪽_배치).grid(row=0, column=2, padx=8)

    def _칸_격자_만들기(self, 부모, 배치):
        격자 = tk.Frame(부모)
        for 행번호, 행 in enumerate(배치):
            for 열번호, 슬롯 in enumerate(행):
                if 슬롯 is None:
                    continue
                버튼 = tk.Button(
                    격자, width=12, height=3, wraplength=90, justify="center",
                    command=lambda s=슬롯: self._슬롯_클릭(s),
                )
                버튼.grid(row=행번호, column=열번호, padx=3, pady=3)
                self._슬롯버튼[슬롯] = 버튼
        self._슬롯_갱신()
        return 격자

    def _슬롯_갱신(self):
        for 슬롯, 버튼 in self._슬롯버튼.items():
            if 슬롯 in _미구현_슬롯:
                이름 = "(미구현)"
            else:
                이름 = self.캐릭터.get("장착장비", {}).get(슬롯) or "(비어 있음)"
            버튼.config(text=f"[{슬롯}]\n{이름}")

    def _슬롯_클릭(self, 슬롯):
        _장비팝업(self, 슬롯)

    # -------------------------------------------------
    # 상태 탭
    # -------------------------------------------------

    def _탭_바뀜(self, _event=None):
        선택된탭 = self.노트북.tab(self.노트북.select(), "text")
        if 선택된탭 != "상태":
            return
        for 위젯 in self.상태탭.winfo_children():
            위젯.destroy()
        if self.상태탭생성 is None:
            tk.Label(self.상태탭, text="(상태 화면이 연결되지 않았다)").pack(pady=20)
            return
        내용 = self.상태탭생성(self.상태탭, self.캐릭터)
        내용.pack(fill="both", expand=True)

    # -------------------------------------------------
    # 장비 교체
    # -------------------------------------------------

    def 장비_교체(self, 슬롯, 아이템데이터):
        """팝업이 부르는 교체 실행. 실패하면 ValueError(사유)."""
        equipment_system.장비_교체(self.플레이어, self.캐릭터, 슬롯, 아이템데이터)
        self._슬롯_갱신()
        if self.장비변경콜백 is not None:
            self.장비변경콜백()


class _장비팝업(tk.Toplevel):
    """칸을 눌렀을 때 뜨는 팝업. 처음엔 착용 중인 장비 이름과 [교체] [닫기],
    [교체]를 누르면 소지품에서 그 부위에 맞는 아이템 리스트로 바뀐다."""

    def __init__(self, 화면, 슬롯):
        super().__init__(화면)
        self.화면 = 화면
        self.슬롯 = 슬롯
        self.title(슬롯)
        self.resizable(False, False)
        self.transient(화면.winfo_toplevel())
        self.grab_set()

        self.본문틀 = tk.Frame(self)
        self.본문틀.pack(padx=20, pady=16)
        self._기본_화면()

    def _본문_비우기(self):
        for 위젯 in self.본문틀.winfo_children():
            위젯.destroy()

    # ---- 화면 1 : 착용 중인 장비 + 교체/닫기 ----

    def _기본_화면(self):
        self._본문_비우기()
        tk.Label(self.본문틀, text=self.슬롯, font=("", 12, "bold")).pack(pady=(0, 8))

        if self.슬롯 in _미구현_슬롯:
            tk.Label(self.본문틀, text="아직 미구현이다.").pack(pady=8)
            tk.Button(self.본문틀, text="닫기", width=10, command=self.destroy).pack(pady=(8, 0))
            return

        이름 = self.화면.캐릭터.get("장착장비", {}).get(self.슬롯)
        tk.Label(self.본문틀, text=이름 or "(착용 중인 장비 없음)").pack(pady=8)

        버튼틀 = tk.Frame(self.본문틀)
        버튼틀.pack(pady=(8, 0))
        tk.Button(버튼틀, text="교체", width=10, command=self._교체_화면).pack(side="left", padx=4)
        tk.Button(버튼틀, text="닫기", width=10, command=self.destroy).pack(side="left", padx=4)

    # ---- 화면 2 : 소지품 후보 리스트 ----

    def _교체_화면(self):
        self._본문_비우기()
        tk.Label(self.본문틀, text=f"{self.슬롯} 교체", font=("", 12, "bold")).pack(pady=(0, 8))

        슬롯아이템들 = self.화면.카탈로그.get("장비", {}).get(self.슬롯, {})
        후보목록 = equipment_system.교체_후보목록(
            self.화면.플레이어, self.화면.캐릭터, self.슬롯, 슬롯아이템들,
        )

        목록틀 = self._스크롤틀_만들기(self.본문틀)
        if not 후보목록:
            tk.Label(목록틀, text="(교체할 수 있는 아이템이 소지품에 없다)", fg="gray").pack(
                anchor="w", padx=6, pady=8
            )
        for 아이템, 가능수량, 착용가능, 사유 in 후보목록:
            self._후보행_만들기(목록틀, 아이템, 가능수량, 착용가능, 사유)

        self.상태메시지 = tk.Label(self.본문틀, text="", fg="red", wraplength=380)
        self.상태메시지.pack(pady=(6, 0))

        버튼틀 = tk.Frame(self.본문틀)
        버튼틀.pack(pady=(8, 0))
        tk.Button(버튼틀, text="뒤로", width=10, command=self._기본_화면).pack(side="left", padx=4)
        tk.Button(버튼틀, text="닫기", width=10, command=self.destroy).pack(side="left", padx=4)

    def _스크롤틀_만들기(self, 부모):
        틀 = tk.Frame(부모, width=400, height=220)
        틀.pack()
        틀.pack_propagate(False)
        캔버스 = tk.Canvas(틀, highlightthickness=0)
        스크롤 = tk.Scrollbar(틀, orient="vertical", command=캔버스.yview)
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

    def _후보행_만들기(self, 부모, 아이템, 가능수량, 착용가능, 사유):
        행 = tk.Frame(부모)
        행.pack(fill="x", padx=4, pady=2)

        색 = "black" if 착용가능 else "gray"
        tk.Label(
            행, text=f"{아이템['이름']}  x{가능수량}", width=24, anchor="w", fg=색,
        ).pack(side="left")

        if 착용가능:
            tk.Button(
                행, text="장착",
                command=lambda a=아이템: self._장착(a),
            ).pack(side="left", padx=4)
        else:
            tk.Label(
                행, text=f"착용 불가 - {사유}", fg="gray", wraplength=200, justify="left",
            ).pack(side="left", padx=4)

    def _장착(self, 아이템):
        try:
            self.화면.장비_교체(self.슬롯, 아이템)
        except ValueError as e:
            self.상태메시지.config(text=str(e))
            return
        self.destroy()