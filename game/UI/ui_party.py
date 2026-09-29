# =====================
# 파티 화면
# =====================
# 파티원 전체를 한 화면에서 훑어보는 목록이다. 전투 밖(마을 등)에서
# "우리 파티가 지금 어떤 상태인지" 확인하는 용도로 만들었다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 읽기 전용 목록이다. 장비 교체나 파티원 교체(party_system.파티원_추가/
#   파티원_제거)는 아직 넣지 않았다 - 장비 교체는 아이템/소지품 시스템이
#   없어 "어떤 장비 중에서 고를지" 자체가 없고, 파티원 교체는 마을에서
#   대기 중인 캐릭터 목록(예비 인원) 개념이 아직 정해지지 않았다.
# - 캐릭터 하나를 클릭하면 "상세보기콜백"(있으면)을 그 캐릭터로 호출한다
#   - main_system.py가 이걸 ui_status.상태화면으로 화면 전환하는 데
#     쓸 수 있다. ui_party.py는 ui_status.py를 직접 import하지 않는다
#     (화면끼리는 서로 부르지 않고 main_system.py를 통해서만 오간다).

import tkinter as tk

from game.system import equipment_system


class 파티화면(tk.Frame):
    """파티            : party_system.py 파티 딕셔너리({"파티원": [...]}).
    장비데이터모음  : {캐릭터명: {슬롯: 아이템데이터, ...}, ...}.
    상세보기콜백    : 목록의 캐릭터 행을 클릭했을 때 그 캐릭터 데이터를
                       인자로 호출할 함수. 생략하면 클릭해도 아무 일도
                       일어나지 않는다.
    """

    def __init__(self, master, 파티, 장비데이터모음=None, 상세보기콜백=None):
        super().__init__(master)
        self.파티 = 파티
        self.장비데이터모음 = 장비데이터모음 or {}
        self.상세보기콜백 = 상세보기콜백

        tk.Label(self, text="파티", font=("", 13, "bold")).pack(anchor="w", padx=10, pady=(10, 4))

        목록틀 = tk.Frame(self)
        목록틀.pack(fill="both", expand=True, padx=10, pady=4)

        머리행 = tk.Frame(목록틀)
        머리행.pack(fill="x")
        for 제목, 폭 in (("이름", 10), ("직업", 10), ("레벨", 6), ("HP", 12), ("MP", 12), ("무기", 14), ("AC", 6)):
            tk.Label(머리행, text=제목, width=폭, anchor="w", font=("", 9, "bold")).pack(side="left")

        for 캐릭터 in self.파티.get("파티원", []):
            self._행_생성(목록틀, 캐릭터)

    def _행_생성(self, 부모, 캐릭터):
        장비데이터 = self.장비데이터모음.get(캐릭터["캐릭터명"], {})
        try:
            AC = equipment_system.최종AC_계산(캐릭터, 장비데이터)
        except Exception:
            AC = 캐릭터.get("기본AC", "-")

        생존 = 캐릭터["현재HP"] > 0
        행 = tk.Frame(부모, cursor="hand2" if self.상세보기콜백 else "")
        행.pack(fill="x", pady=1)

        칸들 = [
            (캐릭터["캐릭터명"] + ("" if 생존 else " (쓰러짐)"), 10),
            (캐릭터.get("직업") or "-", 10),
            (str(캐릭터["레벨"]), 6),
            (f"{캐릭터['현재HP']}/{캐릭터['기본최대HP']}", 12),
            (f"{캐릭터['현재MP']}/{캐릭터['기본최대MP']}", 12),
            (캐릭터.get("장착장비", {}).get("무기") or "-", 14),
            (str(AC), 6),
        ]
        위젯들 = [행]
        for 텍스트, 폭 in 칸들:
            라벨 = tk.Label(행, text=텍스트, width=폭, anchor="w")
            라벨.pack(side="left")
            위젯들.append(라벨)

        if self.상세보기콜백 is not None:
            for 위젯 in 위젯들:
                위젯.bind("<Button-1>", lambda e, c=캐릭터: self.상세보기콜백(c))