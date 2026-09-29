# =====================
# 상태 화면
# =====================
# 파티원 한 명을 골라 능력치/파생 스탯/보유특성을 확인하는, 전투 밖에서
# 쓰는 화면이다. combat_system.py의 "참가자" 인스턴스가 아니라
# character_data_system.py의 캐릭터 데이터(그리고 equipment_system.py의
# 장비 계산)를 직접 읽는다 - 전투 중이 아니라서 버프/디버프/상태이상은
# 없다는 전제다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 읽기 전용이다. 능력치 재분배나 특성 변경 같은 조작은 없다 - 그런
#   조작은 character_levelup_system.py 쪽 흐름(파티관리 화면의 [레벨업] -
#   main_system.py 참고)에서 다룬다.
# - "그때그때 계산" 보너스(effect_engine.py 참고) 중 AC/방어력/보호률/
#   명중률보너스/최대HP·MP/행동자원에 붙는 "특성"발 보너스는 아직
#   effect_engine.py 자체에 계산 함수가 없어서 반영되지 않는다 - 즉 이
#   화면의 AC/방어력/보호률 값은 장비 보너스까지만 반영되고, 특성이
#   주는 추가 보너스는 능력치 자체를 올리는 종류("근력" 등 직접 수치
#   변경)만 이미 캐릭터 값에 녹아 있다.
# - 초기선택을 받으면(파티관리 화면에서 특정 캐릭터의 [상세보기]를 눌러
#   들어온 경우 등) 처음부터 그 캐릭터를 보여준다 - 생략하면 예전처럼
#   파티원목록의 첫 번째 캐릭터를 기본으로 보여준다.

import tkinter as tk

from game.system import character_data_system as 캐릭터데이터
from game.system import equipment_system

_능력치_목록 = ["근력", "민첩", "건강", "지능", "지혜", "매력"]


class 상태화면(tk.Frame):
    """파티원목록      : character_data_system.py 캐릭터 딕셔너리 리스트.
    장비데이터모음  : {캐릭터명: {슬롯: 아이템데이터, ...}, ...} -
                       equipment_system.py 계산에 필요한 실제 장비 데이터.
    초기선택        : 처음에 보여줄 캐릭터 데이터(선택). 생략하면
                       파티원목록의 첫 번째 캐릭터를 보여준다.
    """

    def __init__(self, master, 파티원목록, 장비데이터모음=None, 초기선택=None):
        super().__init__(master)
        self.파티원목록 = 파티원목록
        self.장비데이터모음 = 장비데이터모음 or {}
        self.선택된캐릭터 = (
            초기선택 if 초기선택 is not None
            else (파티원목록[0] if 파티원목록 else None)
        )

        self._위젯_구성()
        if self.선택된캐릭터 is not None:
            self._갱신()

    def _위젯_구성(self):
        좌측 = tk.Frame(self)
        좌측.pack(side="left", fill="y", padx=8, pady=8)
        tk.Label(좌측, text="파티원", font=("", 10, "bold")).pack(anchor="w")
        for 캐릭터 in self.파티원목록:
            tk.Button(
                좌측, text=캐릭터["캐릭터명"], width=12, anchor="w",
                command=lambda c=캐릭터: self._캐릭터_선택(c),
            ).pack(fill="x", pady=1)

        self.우측 = tk.Frame(self, relief="groove", borderwidth=1)
        self.우측.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    def _캐릭터_선택(self, 캐릭터):
        self.선택된캐릭터 = 캐릭터
        self._갱신()

    def _갱신(self):
        for 위젯 in self.우측.winfo_children():
            위젯.destroy()

        캐릭터 = self.선택된캐릭터
        장비데이터 = self.장비데이터모음.get(캐릭터["캐릭터명"], {})

        머리 = tk.Frame(self.우측)
        머리.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(
            머리, text=f"{캐릭터['캐릭터명']}  ({캐릭터.get('직업') or '무직업'})",
            font=("", 13, "bold"),
        ).pack(anchor="w")
        차수 = 캐릭터데이터.차수_계산(캐릭터)
        tk.Label(머리, text=f"레벨 {캐릭터['레벨']}  ·  {차수}차수").pack(anchor="w")

        자원틀 = tk.Frame(self.우측)
        자원틀.pack(fill="x", padx=10, pady=4)
        tk.Label(자원틀, text=f"HP  {캐릭터['현재HP']} / {캐릭터['기본최대HP']}").grid(row=0, column=0, sticky="w", padx=(0, 20))
        tk.Label(자원틀, text=f"MP  {캐릭터['현재MP']} / {캐릭터['기본최대MP']}").grid(row=0, column=1, sticky="w")

        능력치틀 = tk.LabelFrame(self.우측, text="능력치")
        능력치틀.pack(fill="x", padx=10, pady=4)
        for i, 이름 in enumerate(_능력치_목록):
            값 = 캐릭터[이름]
            보정치 = 캐릭터데이터.능력치_보정치(캐릭터, 이름)
            부호 = "+" if 보정치 >= 0 else ""
            tk.Label(능력치틀, text=f"{이름} {값} ({부호}{보정치})", width=14, anchor="w").grid(
                row=i // 3, column=i % 3, sticky="w", padx=6, pady=2
            )

        파생틀 = tk.LabelFrame(self.우측, text="파생 스탯")
        파생틀.pack(fill="x", padx=10, pady=4)
        try:
            AC = equipment_system.최종AC_계산(캐릭터, 장비데이터)
        except Exception:
            AC = 캐릭터.get("기본AC", "-")
        tk.Label(파생틀, text=f"AC {AC}", width=14, anchor="w").grid(row=0, column=0, sticky="w", padx=6, pady=2)
        tk.Label(파생틀, text=f"방어력 {캐릭터.get('기본방어력', 0)}", width=14, anchor="w").grid(row=0, column=1, sticky="w", padx=6, pady=2)
        tk.Label(파생틀, text=f"보호률 {캐릭터.get('기본보호률', 0)}", width=14, anchor="w").grid(row=0, column=2, sticky="w", padx=6, pady=2)
        tk.Label(파생틀, text=f"속도 {캐릭터.get('기본속도', 0)}", width=14, anchor="w").grid(row=1, column=0, sticky="w", padx=6, pady=2)
        tk.Label(파생틀, text=f"어그로 {캐릭터.get('어그로', 10)} x{캐릭터.get('어그로배율', 1.0)}", width=14, anchor="w").grid(row=1, column=1, sticky="w", padx=6, pady=2)
        tk.Label(파생틀, text=f"추가공격 {캐릭터.get('추가공격', 0)}회", width=14, anchor="w").grid(row=1, column=2, sticky="w", padx=6, pady=2)

        장비틀 = tk.LabelFrame(self.우측, text="장착 장비")
        장비틀.pack(fill="x", padx=10, pady=4)
        for i, (슬롯, 아이템이름) in enumerate(캐릭터.get("장착장비", {}).items()):
            tk.Label(장비틀, text=f"{슬롯}: {아이템이름 or '-'}", width=18, anchor="w").grid(
                row=i // 3, column=i % 3, sticky="w", padx=6, pady=1
            )

        특성틀 = tk.LabelFrame(self.우측, text="보유 특성")
        특성틀.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        보유특성 = 캐릭터.get("보유특성", [])
        if 보유특성:
            tk.Label(특성틀, text=", ".join(보유특성), anchor="w", justify="left", wraplength=380).pack(
                fill="x", padx=6, pady=4
            )
        else:
            tk.Label(특성틀, text="(없음)", anchor="w").pack(fill="x", padx=6, pady=4)