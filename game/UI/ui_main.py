# =====================
# 메인 화면 (타이틀)
# =====================
# 실행 파일을 켜면 가장 먼저 뜨는 화면이다. 다른 화면들(ui_party.py 등)과
# 마찬가지로, 이 화면은 버튼을 눌렀을 때 다음에 어느 화면으로 넘어갈지
# 스스로 정하지 않는다 - 각 버튼의 동작은 콜백으로 받아서 main_system.py
# (화면 전환 뼈대)가 정하게 한다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 메인 일러스트는 아직 실제 이미지 파일이 없어서(에셋 미정) 자리만
#   Label로 잡아뒀다. 나중에 이미지 파일이 생기면 tk.PhotoImage 등으로
#   바꿔 끼우면 된다.
# - "불러오기" 버튼은 save_system.전체_세이브_요약()을 확인해서 저장된
#   슬롯이 하나도 없으면 자동으로 비활성화한다 - 빈 슬롯 목록 화면으로
#   넘어가는 것을 막기 위함이다.
# - "게임 종료" 버튼은 종료콜백을 안 주면 이 창(root) 자체를 닫는다.
# - Z(확인)는 이 화면도 ui_system.공통조작키_바인딩()으로 켜뒀다 - 확인
#   콜백을 따로 안 줘서, Tab으로 버튼 사이를 옮겨 다니다 Z를 누르면 그
#   버튼을 누른 것과 같다. 타이틀 화면엔 "취소"할 것이 없어 X는 그냥
#   아무 일도 하지 않는다.

import tkinter as tk

from game.system import save_system
from game.system import ui_system


class 메인화면(tk.Frame):
    """새로운시작콜백, 불러오기콜백, 옵션콜백, 종료콜백 : 각 버튼을 눌렀을
    때 인자 없이 호출할 함수. 생략하면 해당 버튼을 눌러도 아무 일도
    일어나지 않는다 (단, 종료콜백은 생략하면 창을 직접 닫는다)."""

    def __init__(self, master, 새로운시작콜백=None, 불러오기콜백=None,
                 옵션콜백=None, 종료콜백=None):
        super().__init__(master)
        self.새로운시작콜백 = 새로운시작콜백
        self.불러오기콜백 = 불러오기콜백
        self.옵션콜백 = 옵션콜백
        self.종료콜백 = 종료콜백

        일러스트틀 = tk.Frame(self, bg="black", height=360)
        일러스트틀.pack(fill="both", expand=True)
        일러스트틀.pack_propagate(False)
        tk.Label(일러스트틀, text="[메인 일러스트 자리]", fg="white", bg="black",
                 font=("", 12)).pack(expand=True)

        버튼틀 = tk.Frame(self)
        버튼틀.pack(pady=20)

        저장된_슬롯_있음 = any(
            not 요약.get("비어있음") for 요약 in save_system.전체_세이브_요약()
        )

        tk.Button(버튼틀, text="새로운 시작", width=18,
                  command=self._새로운_시작).pack(pady=4)
        tk.Button(버튼틀, text="불러오기", width=18,
                  state="normal" if 저장된_슬롯_있음 else "disabled",
                  command=self._불러오기).pack(pady=4)
        tk.Button(버튼틀, text="옵션", width=18,
                  command=self._옵션).pack(pady=4)
        tk.Button(버튼틀, text="게임 종료", width=18,
                  command=self._게임_종료).pack(pady=4)

        ui_system.공통조작키_바인딩(self)

    def _새로운_시작(self):
        if self.새로운시작콜백 is not None:
            self.새로운시작콜백()

    def _불러오기(self):
        if self.불러오기콜백 is not None:
            self.불러오기콜백()

    def _옵션(self):
        if self.옵션콜백 is not None:
            self.옵션콜백()

    def _게임_종료(self):
        if self.종료콜백 is not None:
            self.종료콜백()
        else:
            self.winfo_toplevel().destroy()