# =====================
# 필드 화면 (노드 이동식 지도)
# =====================
# map_system.py "필드정보"(마을/던전 같은 기존 지점들을 노드로 삼아
# 서로 연결한 지도)를 보여주는 화면이다. 마을과 마을 사이를 오갈 때
# 쓴다 - 사용자 확인 결과 이동 중 몬스터 인카운트는 없다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - "필드정보" 데이터 양식 자체가 이 작업에서 처음 정의된 것이다
#   (map_system.py 모듈 설명 참고) - 실제 필드 데이터 파일은 아직 없다.
# - 노드 위치(원을 그릴 좌표)를 담는 데이터가 필드정보 양식에 없어서,
#   이 화면이 노드 개수만큼 원 모양으로 자동 배치해서 그린다(그냥
#   보여주기 위한 임시 배치이지, 실제 지리적 위치를 반영하지 않는다 -
#   사용자 확인 필요할 수 있음).
# - 노드 색: 빨강 = 현재 위치, 초록 = 지금 이동 가능(인접 + 개방 조건
#   충족), 회색 = 그 외(인접하지 않거나 아직 개방 안 됨). 초록 노드만
#   클릭할 수 있다.
# - "마을" 노드로 이동하면 town_system.마을_이동()을 호출해 진행도까지
#   갱신한다. "던전" 노드는 진행도에 해당하는 개념이 없어서(진행도는
#   "현재마을"만 추적) 이 화면 안에서 현재 위치로만 취급하고 진행도는
#   건드리지 않는다.
# - 실제 화면 전환(마을 화면/던전 화면으로 들어가기)은 이 화면이 하지
#   않는다 - 이동콜백(노드 항목)만 호출하고 나머지는 main_system.py
#   몫이다.
 
import math
import tkinter as tk
 
from game.system import map_system
from game.system import town_system
 
_노드_반지름 = 26
 
 
class 필드화면(tk.Frame):
    """필드정보   : map_system.py "필드정보" 구조.
    현재노드ID : 지금 위치한 노드 ID(필드정보["노드"]의 키).
    진행도     : town_system.새_진행도() 구조 - "마을" 노드의 개방 여부
                  판정과, 이동 성공 시 town_system.마을_이동() 갱신에
                  쓴다.
    이동콜백   : 인접 노드로 이동에 성공하면 그 노드 항목(딕셔너리)을
                  인자로 호출한다. 생략하면 노드를 눌러도 화면 전환
                  요청 없이 이 화면 안의 현재 위치 표시만 바뀐다.
    """
 
    def __init__(self, master, 필드정보, 현재노드ID, 진행도, 이동콜백=None):
        super().__init__(master)
        self.필드정보 = 필드정보
        self.현재노드ID = 현재노드ID
        self.진행도 = 진행도
        self.이동콜백 = 이동콜백
 
        self._좌표 = self._노드_좌표_계산()
        self._위젯_구성()
 
    # -------------------------------------------------
    # 위젯 구성
    # -------------------------------------------------
 
    def _위젯_구성(self):
        tk.Label(
            self, text=self.필드정보["필드명"], font=("", 13, "bold"),
        ).pack(anchor="w", padx=10, pady=(10, 4))
 
        self.캔버스 = tk.Canvas(self, width=440, height=340, bg="#1b1b1b")
        self.캔버스.pack(padx=10, pady=4)
 
        self.상태메시지 = tk.Label(self, text="", anchor="w", fg="blue")
        self.상태메시지.pack(fill="x", padx=10, pady=(0, 10))
 
        self._그리기()
 
    def _노드_좌표_계산(self):
        노드ID목록 = list(self.필드정보["노드"].keys())
        개수 = len(노드ID목록)
        중심 = (220, 170)
        반지름 = 130
        좌표 = {}
        for i, 노드ID in enumerate(노드ID목록):
            각도 = 2 * math.pi * i / max(1, 개수)
            좌표[노드ID] = (
                중심[0] + 반지름 * math.cos(각도),
                중심[1] + 반지름 * math.sin(각도),
            )
        return 좌표
 
    def _그리기(self):
        self.캔버스.delete("all")
 
        for a, b in self.필드정보["연결"]:
            ax, ay = self._좌표[a]
            bx, by = self._좌표[b]
            self.캔버스.create_line(ax, ay, bx, by, fill="#666666")
 
        이동가능 = set(
            map_system.이동가능인접노드목록(self.필드정보, self.현재노드ID, self.진행도)
        )
 
        for 노드ID, (x, y) in self._좌표.items():
            노드 = self.필드정보["노드"][노드ID]
            if 노드ID == self.현재노드ID:
                색 = "#e53935"
            elif 노드ID in 이동가능:
                색 = "#43a047"
            else:
                색 = "#757575"
 
            태그 = f"node_{노드ID}"
            self.캔버스.create_oval(
                x - _노드_반지름, y - _노드_반지름,
                x + _노드_반지름, y + _노드_반지름,
                fill=색, outline="", tags=(태그,),
            )
            self.캔버스.create_text(
                x, y, text=노드["이름"], fill="white", font=("", 9, "bold"),
                tags=(태그,),
            )
 
            if 노드ID in 이동가능:
                self.캔버스.tag_bind(
                    태그, "<Button-1>", lambda e, n=노드ID: self._노드_클릭(n)
                )
 
    # -------------------------------------------------
    # 이동 처리
    # -------------------------------------------------
 
    def _노드_클릭(self, 노드ID):
        노드 = self.필드정보["노드"][노드ID]
 
        if 노드["종류"] == "마을":
            try:
                town_system.마을_이동(self.진행도, 노드["원본"]["마을명"])
            except ValueError as e:
                self.상태메시지.config(text=str(e))
                return
 
        self.현재노드ID = 노드ID
        self.상태메시지.config(text=f"{노드['이름']}(으)로 이동했다.")
        self._그리기()
 
        if self.이동콜백 is not None:
            self.이동콜백(노드)
 