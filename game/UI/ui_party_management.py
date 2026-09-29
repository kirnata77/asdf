# =====================
# 파티관리 화면
# =====================
# 마을/던전에서 [파티관리]로 들어오는 화면이다. ui_party.py("파티 확인" -
# 전투 밖에서 파티 상태를 훑어보기만 하는 읽기 전용 목록)와는 별개로,
# 캐릭터별 [상세보기]/[레벨업] 조작이 필요해서 새로 만들었다(사용자 확인 -
# 기존 파티화면은 그대로 두고 새 화면을 만들기로 함).
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 캐릭터 레벨은 더 이상 몬스터 처치 경험치로 오르지 않는다(사용자 확인 -
#   기존 경험치 시스템은 실제로 동작한 적이 없었다). 대신 플레이어 레벨
#   (던전 보스 클리어 등으로 오른다 - main_system.py 참고)까지, 캐릭터별로
#   [레벨업] 버튼을 직접 눌러야 한 레벨씩 오른다. 그래서 [레벨업] 버튼은
#   "캐릭터 레벨 < 플레이어 레벨"일 때만 활성화된다.
# - [레벨업]을 눌렀을 때 실제로 일어나는 일(능력치 배분/퍽 선택 팝업 등)은
#   이 화면이 모른다 - 레벨업콜백(캐릭터)만 부른다. 그 결과로 파티 데이터가
#   바뀌면 main_system.py가 이 화면을 다시 열어(화면_전환) 새로 그리게
#   한다(화면끼리 서로 안 부르고 main_system.py를 통해서만 오간다는 기존
#   관례 - ui_party.py와 동일).
# - [상세보기]도 마찬가지로 상세보기콜백(캐릭터)만 부른다 -
#   ui_status.상태화면으로 화면 전환하는 건 main_system.py 몫이다.

import tkinter as tk


class 파티관리화면(tk.Frame):
    """파티          : party_system.py 파티 딕셔너리({"파티원": [...]}).
    플레이어레벨  : 정수. 캐릭터 레벨업 가능 상한(캐릭터 레벨이 이보다
                    낮아야 [레벨업] 버튼이 활성화된다).
    상세보기콜백  : [상세보기] 클릭 시 그 캐릭터 데이터를 인자로 호출.
                    생략하면 버튼이 비활성 상태로 뜬다.
    레벨업콜백    : [레벨업] 클릭 시 그 캐릭터 데이터를 인자로 호출.
                    생략하면 버튼이 비활성 상태로 뜬다.
    """

    def __init__(self, master, 파티, 플레이어레벨, 상세보기콜백=None, 레벨업콜백=None):
        super().__init__(master)
        self.파티 = 파티
        self.플레이어레벨 = 플레이어레벨
        self.상세보기콜백 = 상세보기콜백
        self.레벨업콜백 = 레벨업콜백

        머리 = tk.Frame(self)
        머리.pack(fill="x", padx=10, pady=(10, 4))
        tk.Label(머리, text="파티관리", font=("", 13, "bold")).pack(side="left")
        tk.Label(머리, text=f"플레이어 레벨 {self.플레이어레벨}").pack(side="right")

        목록틀 = tk.Frame(self)
        목록틀.pack(fill="both", expand=True, padx=10, pady=4)

        머리행 = tk.Frame(목록틀)
        머리행.pack(fill="x")
        for 제목, 폭 in (("이름", 10), ("직업", 10), ("레벨", 6)):
            tk.Label(머리행, text=제목, width=폭, anchor="w", font=("", 9, "bold")).pack(
                side="left"
            )

        for 캐릭터 in self.파티.get("파티원", []):
            self._행_생성(목록틀, 캐릭터)

    def _행_생성(self, 부모, 캐릭터):
        행 = tk.Frame(부모)
        행.pack(fill="x", pady=2)

        생존 = 캐릭터["현재HP"] > 0
        tk.Label(
            행, text=캐릭터["캐릭터명"] + ("" if 생존 else " (쓰러짐)"),
            width=10, anchor="w",
        ).pack(side="left")
        tk.Label(행, text=캐릭터.get("직업") or "-", width=10, anchor="w").pack(side="left")
        tk.Label(행, text=str(캐릭터["레벨"]), width=6, anchor="w").pack(side="left")

        tk.Button(
            행, text="상세보기", width=10,
            state="normal" if self.상세보기콜백 else "disabled",
            command=lambda c=캐릭터: self._상세보기_클릭(c),
        ).pack(side="left", padx=2)

        레벨업가능 = 캐릭터["레벨"] < self.플레이어레벨
        tk.Button(
            행, text="레벨업", width=10,
            state="normal" if (self.레벨업콜백 and 레벨업가능) else "disabled",
            command=lambda c=캐릭터: self._레벨업_클릭(c),
        ).pack(side="left", padx=2)

    def _상세보기_클릭(self, 캐릭터):
        if self.상세보기콜백 is not None:
            self.상세보기콜백(캐릭터)

    def _레벨업_클릭(self, 캐릭터):
        if self.레벨업콜백 is not None:
            self.레벨업콜백(캐릭터)