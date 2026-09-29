# =====================
# 스킬 화면
# =====================
# 파티원이 보유한 스킬 목록과 각 스킬의 세부 내용(job_skill_XX.py
# "스킬목록" 데이터 그대로)을 확인하는, 전투 밖에서 쓰는 화면이다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 읽기 전용이다. 스킬 사용은 ui_battle.py(전투 중)에서만 하고, 여기서는
#   설명을 확인만 한다. "훔쳐배우기"처럼 스킬을 즉시 골라야 하는 퍽은
#   character_levelup_system.py 쪽 흐름(레벨업/퍽 선택 화면)에서 다뤄야
#   할 내용이라 여기 넣지 않았다.
# - 캐릭터의 직업에 맞는 job_skill_XX.py "스킬목록"을 찾아서
#   "스킬데이터모음전체"를 만드는 건 호출하는 쪽(main_system.py)의 몫이다
#   - ui_battle.py와 같은 관례다. 캐릭터가 "보유스킬"로 갖고 있는데
#   이 딕셔너리에 없는 이름은 "데이터 없음"으로 표시한다.

import tkinter as tk

_표시할_키 = [
    ("분류", "분류"), ("행동", "행동"), ("타겟", "타겟"), ("속성", "속성"),
    ("데미지", "데미지"), ("데미지보너스", "데미지보너스"),
    ("명중률", "명중률"), ("명중보너스", "명중보너스"),
    ("공격횟수", "공격횟수"), ("MP소모", "MP소모"),
    ("턴당사용제한", "턴당사용제한"), ("휴식당횟수", "휴식당횟수"),
    ("전투당횟수", "전투당횟수"), ("일반공격취급", "일반공격취급"),
]


class 스킬화면(tk.Frame):
    """파티원목록        : character_data_system.py 캐릭터 딕셔너리 리스트.
    스킬데이터모음전체  : {캐릭터명: {스킬이름: 스킬데이터, ...}, ...}.
    """

    def __init__(self, master, 파티원목록, 스킬데이터모음전체=None):
        super().__init__(master)
        self.파티원목록 = 파티원목록
        self.스킬데이터모음전체 = 스킬데이터모음전체 or {}
        self.선택된캐릭터 = 파티원목록[0] if 파티원목록 else None

        self._위젯_구성()
        if self.선택된캐릭터 is not None:
            self._캐릭터_갱신()

    def _위젯_구성(self):
        좌측 = tk.Frame(self)
        좌측.pack(side="left", fill="y", padx=8, pady=8)
        tk.Label(좌측, text="파티원", font=("", 10, "bold")).pack(anchor="w")
        for 캐릭터 in self.파티원목록:
            tk.Button(
                좌측, text=캐릭터["캐릭터명"], width=12, anchor="w",
                command=lambda c=캐릭터: self._캐릭터_선택(c),
            ).pack(fill="x", pady=1)

        중앙 = tk.Frame(self)
        중앙.pack(side="left", fill="y", padx=8, pady=8)
        tk.Label(중앙, text="보유 스킬", font=("", 10, "bold")).pack(anchor="w")
        self.스킬목록틀 = tk.Frame(중앙)
        self.스킬목록틀.pack(fill="y")

        self.상세틀 = tk.Frame(self, relief="groove", borderwidth=1)
        self.상세틀.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    def _캐릭터_선택(self, 캐릭터):
        self.선택된캐릭터 = 캐릭터
        self._캐릭터_갱신()

    def _캐릭터_갱신(self):
        for 위젯 in self.스킬목록틀.winfo_children():
            위젯.destroy()
        for 위젯 in self.상세틀.winfo_children():
            위젯.destroy()

        캐릭터 = self.선택된캐릭터
        스킬데이터모음 = self.스킬데이터모음전체.get(캐릭터["캐릭터명"], {})
        보유스킬 = 캐릭터.get("보유스킬", [])

        if not 보유스킬:
            tk.Label(self.스킬목록틀, text="(보유한 스킬 없음)").pack(anchor="w")
            return

        for 이름 in 보유스킬:
            존재함 = 이름 in 스킬데이터모음
            표시 = 이름 if 존재함 else f"{이름} (데이터 없음)"
            tk.Button(
                self.스킬목록틀, text=표시, width=16, anchor="w",
                state=("normal" if 존재함 else "disabled"),
                command=lambda n=이름, d=스킬데이터모음.get(이름): self._스킬_표시(n, d),
            ).pack(fill="x", pady=1)

        self._스킬_표시(보유스킬[0], 스킬데이터모음.get(보유스킬[0]))

    def _스킬_표시(self, 이름, 스킬데이터):
        for 위젯 in self.상세틀.winfo_children():
            위젯.destroy()

        if 스킬데이터 is None:
            tk.Label(self.상세틀, text=f"'{이름}'의 스킬 데이터가 없습니다.").pack(
                anchor="w", padx=10, pady=10
            )
            return

        tk.Label(self.상세틀, text=이름, font=("", 12, "bold")).pack(
            anchor="w", padx=10, pady=(10, 4)
        )

        정보틀 = tk.Frame(self.상세틀)
        정보틀.pack(fill="x", padx=10, pady=4)
        row = 0
        for 표시이름, 키 in _표시할_키:
            if 키 not in 스킬데이터:
                continue
            tk.Label(정보틀, text=f"{표시이름}: {스킬데이터[키]}", anchor="w").grid(
                row=row // 2, column=row % 2, sticky="w", padx=6, pady=1
            )
            row += 1

        설명 = 스킬데이터.get("설명")
        if 설명:
            tk.Label(
                self.상세틀, text=설명, anchor="w", justify="left",
                wraplength=380,
            ).pack(fill="x", padx=10, pady=(8, 10))