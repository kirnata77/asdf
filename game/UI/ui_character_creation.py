# =====================
# 정식 캐릭터 생성 화면
# =====================
# "새로운 시작"에서 파티원 한 명(총 4번 반복)을 만드는 화면이다. 다른
# ui_*.py들과 같은 관례로, 이 화면은 실제로 완성된 캐릭터를 만들지
# 않는다 - 이름과 직업만 고르게 하고, 그 두 값을 확인콜백으로 넘기면
# main_system.py가 job_level_XX.py/job_ability_XX.py/eq_weapon_XX.py
# 데이터를 찾아 character_creation_system.캐릭터_생성()으로 실제
# 캐릭터를 완성한다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 능력치(근력~매력) 배분은 더 이상 이 화면에서 플레이어가 직접
#   고르지 않는다 - 직업을 고르면 character_creation_system.py의
#   직업별_주보조약점스탯/초기능력치_생성()이 자동으로 정해준다
#   (사용자 확정 규칙). 이 화면은 그 결과를 미리보기로 보여주기만 한다.
# - 직업 목록은 character_creation_system.직업별_주보조약점스탯의 키를
#   그대로 쓴다 - 새 직업이 그 레지스트리에 추가되면 이 화면도 자동으로
#   따라간다.
# - 이름을 비워두고 확인을 누르면 고른 직업 이름을 그대로 캐릭터명으로
#   쓴다(사용자 확인 필요할 수 있음 - 최소한 빈 이름으로 진행이 막히지는
#   않게 하기 위한 임시 처리).
# - Z(확인)/X(취소)는 ui_system.공통조작키_바인딩()으로 "확인"/"취소"
#   버튼과 그대로 연결했다 - 취소콜백을 안 받은 경우(취소 버튼 자체가
#   없는 경우)는 X를 눌러도 아무 일도 없다.

import tkinter as tk

from game.system import character_creation_system as 캐릭터생성
from game.system import ui_system

_능력치_목록 = ["근력", "민첩", "건강", "지능", "지혜", "매력"]


class 캐릭터생성화면(tk.Frame):
    """순번     : 지금 몇 번째 파티원을 만드는 중인지(1~4) - 화면 제목에만 쓴다.
    확인콜백  : "확인" 버튼을 누르면 (캐릭터명, 직업)을 인자로 호출한다.
    취소콜백  : "취소" 버튼을 누르면 인자 없이 호출한다. 생략하면
                취소 버튼 자체가 뜨지 않는다.
    """

    직업목록 = list(캐릭터생성.직업별_주보조약점스탯.keys())

    def __init__(self, master, 순번=1, 확인콜백=None, 취소콜백=None):
        super().__init__(master)
        self.확인콜백 = 확인콜백
        self.취소콜백 = 취소콜백
        self.선택직업 = tk.StringVar(value=self.직업목록[0])

        tk.Label(
            self, text=f"파티원 {순번}번 캐릭터 생성", font=("", 14, "bold"),
        ).pack(pady=(16, 8))

        이름틀 = tk.Frame(self)
        이름틀.pack(pady=6)
        tk.Label(이름틀, text="이름 : ").pack(side="left")
        self.이름입력 = tk.Entry(이름틀, width=20)
        self.이름입력.pack(side="left")

        직업틀 = tk.LabelFrame(self, text="직업 선택")
        직업틀.pack(pady=8, padx=16, fill="x")
        for 직업 in self.직업목록:
            tk.Radiobutton(
                직업틀, text=직업, variable=self.선택직업, value=직업,
                command=self._미리보기_갱신,
            ).pack(side="left", padx=6, pady=4)

        self.미리보기라벨 = tk.Label(
            self, justify="left", font=("", 11), anchor="w",
        )
        self.미리보기라벨.pack(pady=12, padx=16, fill="x")
        self._미리보기_갱신()

        버튼틀 = tk.Frame(self)
        버튼틀.pack(pady=16)
        tk.Button(버튼틀, text="확인", width=12, command=self._확인).pack(
            side="left", padx=4
        )
        if self.취소콜백 is not None:
            tk.Button(버튼틀, text="취소", width=12, command=self.취소콜백).pack(
                side="left", padx=4
            )

        ui_system.공통조작키_바인딩(
            self, 확인콜백=self._확인, 취소콜백=self.취소콜백,
        )

    def _미리보기_갱신(self):
        직업 = self.선택직업.get()
        능력치, 주스탯, 보조스탯, 약점스탯 = 캐릭터생성.초기능력치_생성(직업)

        줄들 = [
            f"[{직업}] 주스탯 {주스탯} / 보조스탯 {보조스탯} / 약점스탯 {약점스탯}",
            "",
        ]
        for 스탯이름 in _능력치_목록:
            표기 = 스탯이름
            if 스탯이름 == 주스탯:
                표기 += " (주)"
            elif 스탯이름 == 보조스탯:
                표기 += " (보조)"
            elif 스탯이름 == 약점스탯:
                표기 += " (약점)"
            줄들.append(f"  {표기} : {능력치[스탯이름]}")

        self.미리보기라벨.config(text="\n".join(줄들))

    def _확인(self):
        캐릭터명 = self.이름입력.get().strip() or self.선택직업.get()
        if self.확인콜백 is not None:
            self.확인콜백(캐릭터명, self.선택직업.get())