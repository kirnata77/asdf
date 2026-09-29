# =====================
# 플레이어 화면 (모험가)
# =====================
# 마을의 [모험가] 버튼으로 여는 화면이다. 파티 전체가 공유하는 값(플레이어
# 레벨, 소지금)과 파티원의 이름/직업을 보여주는 읽기 전용 화면이다.
# 마을 화면 전체를 대체해서 띄우고(main_system.py의 _화면래퍼가
# [◀ 메뉴로]를 붙여준다), 나갈 때 마을로 돌아간다.

import tkinter as tk


class 플레이어화면(tk.Frame):
    """플레이어 : player_system.py 플레이어 딕셔너리
                  ("레벨", "소지품"["골드"], "파티"["파티원"]).
    """

    def __init__(self, master, 플레이어):
        super().__init__(master)
        self.플레이어 = 플레이어

        tk.Label(self, text="모험가", font=("", 14, "bold")).pack(
            anchor="w", padx=12, pady=(12, 6)
        )

        정보틀 = tk.LabelFrame(self, text="정보")
        정보틀.pack(fill="x", padx=12, pady=6)
        골드 = self.플레이어.get("소지품", {}).get("골드", 0)
        tk.Label(
            정보틀, text=f"레벨  {self.플레이어.get('레벨', 1)}", anchor="w",
        ).pack(fill="x", padx=8, pady=(6, 2))
        tk.Label(
            정보틀, text=f"소지금  {골드}G", anchor="w",
        ).pack(fill="x", padx=8, pady=(2, 6))

        파티틀 = tk.LabelFrame(self, text="파티원")
        파티틀.pack(fill="x", padx=12, pady=6)
        파티원목록 = self.플레이어.get("파티", {}).get("파티원", [])
        if not 파티원목록:
            tk.Label(파티틀, text="(파티원 없음)", anchor="w").pack(fill="x", padx=8, pady=6)
        for 캐릭터 in 파티원목록:
            tk.Label(
                파티틀,
                text=f"{캐릭터['캐릭터명']}  -  {캐릭터.get('직업') or '무직업'}",
                anchor="w",
            ).pack(fill="x", padx=8, pady=2)