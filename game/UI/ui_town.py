# =====================
# 마을 화면
# =====================
# town_formet.py 양식의 "마을정보" 하나를 보여주는 화면이다. 던전/다른
# 마을로 이동, 마을 공용 메뉴(NPC/상점/파티구성/창고/휴식)를 다룬다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - NPC/창고는 아직 백엔드가 없어서(quest_system.py/창고 데이터 구조
#   전부 미정) 버튼만 배치하고 항상 비활성 상태다.
# - "상점"은 상점콜백을 주면 활성화되고, 클릭 시 인자 없이 상점콜백을
#   부른다. 실제 상점 팝업(ui_shop.py)은 main_system.py가 연다(ui_town.py가
#   ui_shop.py를 직접 import하지 않는다 - 아래 파티구성과 같은 관례).
#   콜백을 안 주면 버튼이 비활성 상태로 뜬다.
# - "파티 확인"은 이미 만들어진 ui_party.py를 main_system.py가 화면
#   전환으로 연결해줄 것을 전제로, 이 화면은 파티구성콜백만 호출한다
#   (ui_town.py가 ui_party.py를 직접 import하지 않는다 - 화면끼리는
#   서로 부르지 않고 main_system.py를 통해서만 오간다는 기존 관례).
#   콜백을 안 주면 버튼이 비활성 상태로 뜬다.
# - "파티관리"는 ui_party.py(읽기 전용 "파티 확인")와 별개로 캐릭터별
#   [상세보기]/[레벨업] 조작을 다루는 ui_party_management.py를 여는
#   버튼이다(사용자 확인 - 기존 파티화면은 그대로 두고 새로 추가).
#   파티관리콜백을 안 주면 버튼이 비활성 상태로 뜬다.
# - "휴식"은 town_system.휴식_처리()가 실제로 완성되어 있어서 바로
#   동작한다 - 클릭하면 즉시 파티 전원 HP/MP를 회복하고 하단 파티 상태
#   바를 다시 그린다.
# - 던전 이동/다른 마을로 이동 버튼은 map_system.py가 아직 없어서 실제
#   화면 전환 로직은 없다. 이 화면은 "어디로 가려 하는지"만 판단하고
#   (마을 이동은 town_system.마을_이동()으로 개방 여부까지 검증한다),
#   실제 다음 화면 결정은 main_system.py에 맡긴다 - 던전이동콜백/
#   마을이동콜백을 안 주면 각각의 버튼이 비활성 상태로 뜬다.
# - 하단 파티 상태 바는 드래곤 퀘스트 식 박스 UI로 개편했다(ui_battle.py
#   전투 화면의 아군/적 박스와 같은 방식 - 사용자 제공 참고 이미지 기준).
#   캐릭터별로 네모 박스 하나씩 좌우로 늘어놓고, 박스 안에는 이름/HP/MP만
#   숫자로 보여준다 - 마을에서는 전투 중이 아니라 임시생명력/행동자원/
#   상태이상 개념이 없어서 그 셋은 표시하지 않는다. 예전에 쓰던 HP/MP
#   막대(ui_system.py 막대_그리기/HP막대_그리기)는 이번 개편으로 뺐다.
# - ESC를 누르면 설정메뉴콜백(있으면)을 바로 부른다 - 이 화면엔 ESC로
#   취소할 "선택 중" 상태가 따로 없어서다(공통조작키 규칙 - ui_system.py
#   참고).

import tkinter as tk

from game.system import town_system
from game.system import ui_system


class 마을화면(tk.Frame):
    """마을정보        : town_formet.py 마을정보 딕셔너리 (지금 있는 마을).
    파티            : party_system.py 파티 딕셔너리.
    진행도          : town_system.새_진행도() 구조. 마을_이동() 성공 시
                       이 딕셔너리를 직접 바꾼다.
    전체마을목록    : 마을 이동 목록에 띄울 전체 마을정보 리스트. 생략하면
                       town_system.기본_마을목록()을 쓴다.
    던전이동콜백    : 던전 버튼을 클릭하면 던전파일명 하나를 인자로 호출.
                       생략하면 던전 버튼들이 비활성 상태로 뜬다.
    마을이동콜백    : 다른 마을로 이동에 성공하면 그 마을정보를 인자로
                       호출한다(main_system.py가 같은 마을화면을 그
                       마을정보로 다시 여는 데 쓸 수 있다). 생략하면 마을
                       이동 버튼들이 비활성 상태로 뜬다.
    파티구성콜백    : "파티 확인" 버튼 클릭 시 인자 없이 호출. 생략하면
                       버튼이 비활성 상태로 뜬다.
    파티관리콜백    : "파티관리" 버튼 클릭 시 인자 없이 호출. 생략하면
                       버튼이 비활성 상태로 뜬다.
    설정메뉴콜백    : ESC를 누르면 인자 없이 호출한다. 생략하면 ESC를
                       눌러도 아무 일도 없다.
    상점콜백        : "상점" 버튼 클릭 시 인자 없이 호출. 생략하면
                       버튼이 비활성 상태로 뜬다.
    모험가콜백      : "모험가" 버튼 클릭 시 인자 없이 호출(플레이어 화면을
                       여는 용도). 생략하면 버튼이 비활성 상태로 뜬다.
    """

    def __init__(self, master, 마을정보, 파티, 진행도,
                 전체마을목록=None, 던전이동콜백=None, 마을이동콜백=None,
                 파티구성콜백=None, 파티관리콜백=None, 설정메뉴콜백=None,
                 상점콜백=None, 모험가콜백=None):
        super().__init__(master)
        self.마을정보 = 마을정보
        self.파티 = 파티
        self.진행도 = 진행도
        self.전체마을목록 = (
            전체마을목록 if 전체마을목록 is not None else town_system.기본_마을목록()
        )
        self.던전이동콜백 = 던전이동콜백
        self.마을이동콜백 = 마을이동콜백
        self.파티구성콜백 = 파티구성콜백
        self.파티관리콜백 = 파티관리콜백
        self.설정메뉴콜백 = 설정메뉴콜백
        self.상점콜백 = 상점콜백
        self.모험가콜백 = 모험가콜백

        self._위젯_구성()
        ui_system.공통조작키_바인딩(self, esc콜백=self.설정메뉴콜백)

    # -------------------------------------------------
    # 위젯 구성
    # -------------------------------------------------

    def _위젯_구성(self):
        머리 = tk.Frame(self)
        머리.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(
            머리, text=self.마을정보["마을명"], font=("", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            머리, text=" > ".join(self.마을정보.get("상세지역", [])),
        ).pack(anchor="w")

        일러스트틀 = tk.Frame(self, bg="black", height=160)
        일러스트틀.pack(fill="x", padx=10, pady=4)
        일러스트틀.pack_propagate(False)
        tk.Label(
            일러스트틀, text="[마을 배경 일러스트 자리]", fg="white", bg="black",
        ).pack(expand=True)

        본문 = tk.Frame(self)
        본문.pack(fill="both", expand=True, padx=10, pady=4)

        self._공용메뉴_구성(본문)
        self._이동목록_구성(본문)

        self.상태메시지 = tk.Label(self, text="", anchor="w", fg="blue")
        self.상태메시지.pack(fill="x", padx=10)

        self.파티상태틀 = tk.Frame(self, relief="groove", borderwidth=1)
        self.파티상태틀.pack(fill="x", padx=10, pady=(4, 10))
        self._파티상태_갱신()

    def _공용메뉴_구성(self, 부모):
        메뉴틀 = tk.LabelFrame(부모, text="마을 메뉴")
        메뉴틀.pack(side="left", fill="y", padx=(0, 8))

        tk.Button(
            메뉴틀, text="모험가", width=14,
            state="normal" if self.모험가콜백 else "disabled",
            command=self._모험가_클릭,
        ).pack(fill="x", padx=6, pady=3)
        tk.Button(메뉴틀, text="NPC", width=14, state="disabled").pack(
            fill="x", padx=6, pady=3
        )
        tk.Button(
            메뉴틀, text="상점", width=14,
            state="normal" if self.상점콜백 else "disabled",
            command=self._상점_클릭,
        ).pack(fill="x", padx=6, pady=3)
        tk.Button(
            메뉴틀, text="파티 확인", width=14,
            state="normal" if self.파티구성콜백 else "disabled",
            command=self._파티구성_클릭,
        ).pack(fill="x", padx=6, pady=3)
        tk.Button(
            메뉴틀, text="파티관리", width=14,
            state="normal" if self.파티관리콜백 else "disabled",
            command=self._파티관리_클릭,
        ).pack(fill="x", padx=6, pady=3)
        tk.Button(메뉴틀, text="창고", width=14, state="disabled").pack(
            fill="x", padx=6, pady=3
        )
        tk.Button(
            메뉴틀, text="휴식", width=14, command=self._휴식_클릭,
        ).pack(fill="x", padx=6, pady=3)

    def _이동목록_구성(self, 부모):
        오른쪽 = tk.Frame(부모)
        오른쪽.pack(side="left", fill="both", expand=True)

        던전틀 = tk.LabelFrame(오른쪽, text="던전 이동")
        던전틀.pack(fill="x", pady=(0, 8))
        던전목록 = town_system.이동가능던전목록(self.마을정보)
        if not 던전목록:
            tk.Label(던전틀, text="(갈 수 있는 던전 없음)").pack(anchor="w", padx=6, pady=4)
        for 던전파일명 in 던전목록:
            tk.Button(
                던전틀, text=던전파일명, anchor="w",
                state="normal" if self.던전이동콜백 else "disabled",
                command=lambda d=던전파일명: self._던전이동_클릭(d),
            ).pack(fill="x", padx=6, pady=2)

        마을틀 = tk.LabelFrame(오른쪽, text="다른 마을로 이동")
        마을틀.pack(fill="x")
        다른마을목록 = [
            마을 for 마을 in town_system.이동가능마을목록(self.전체마을목록, self.진행도)
            if 마을["마을명"] != self.마을정보["마을명"]
        ]
        if not 다른마을목록:
            tk.Label(마을틀, text="(갈 수 있는 다른 마을 없음)").pack(anchor="w", padx=6, pady=4)
        for 마을 in 다른마을목록:
            tk.Button(
                마을틀, text=마을["마을명"], anchor="w",
                state="normal" if self.마을이동콜백 else "disabled",
                command=lambda m=마을: self._마을이동_클릭(m),
            ).pack(fill="x", padx=6, pady=2)

    # -------------------------------------------------
    # 파티 상태 바 (드래곤 퀘스트 식 박스 - ui_battle.py와 같은 방식)
    # -------------------------------------------------

    def _파티상태_갱신(self):
        for 위젯 in self.파티상태틀.winfo_children():
            위젯.destroy()

        for 캐릭터 in self.파티.get("파티원", []):
            틀 = tk.Frame(self.파티상태틀, relief="groove", borderwidth=1)
            틀.pack(side="left", padx=5, pady=6)
            tk.Label(
                틀, text=캐릭터["캐릭터명"], font=("", 10, "bold"), width=11,
            ).pack(padx=4, pady=(4, 0))
            tk.Label(
                틀, text=f"HP {캐릭터['현재HP']}/{캐릭터['기본최대HP']}",
            ).pack(padx=4)
            tk.Label(
                틀, text=f"MP {캐릭터['현재MP']}/{캐릭터['기본최대MP']}",
            ).pack(padx=4, pady=(0, 4))

    # -------------------------------------------------
    # 버튼 동작
    # -------------------------------------------------

    def _모험가_클릭(self):
        if self.모험가콜백 is not None:
            self.모험가콜백()

    def _상점_클릭(self):
        if self.상점콜백 is not None:
            self.상점콜백()

    def _파티구성_클릭(self):
        if self.파티구성콜백 is not None:
            self.파티구성콜백()

    def _파티관리_클릭(self):
        if self.파티관리콜백 is not None:
            self.파티관리콜백()

    def _휴식_클릭(self):
        town_system.휴식_처리(self.파티)
        self._파티상태_갱신()
        self.상태메시지.config(text="휴식을 취해 파티 전원의 HP/MP를 모두 회복했다.")

    def _던전이동_클릭(self, 던전파일명):
        if self.던전이동콜백 is not None:
            self.던전이동콜백(던전파일명)

    def _마을이동_클릭(self, 목표마을정보):
        try:
            town_system.마을_이동(
                self.진행도, 목표마을정보["마을명"], self.전체마을목록
            )
        except ValueError as e:
            self.상태메시지.config(text=str(e))
            return

        if self.마을이동콜백 is not None:
            self.마을이동콜백(목표마을정보)