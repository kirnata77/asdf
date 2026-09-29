# =====================
# 전투 화면
# =====================
# main_system.py의 "앱.화면_전환()"이 이 파일의 "전투화면" 클래스를
# 컨테이너 프레임 위에 얹어서 띄운다. 이 파일은 combat_system.py/
# skill_system.py가 만들어둔 "전투상태"를 그대로 화면에 그리고, 버튼
# 클릭을 그 두 모듈의 함수 호출로 옮기는 역할만 한다 - 명중/피해/자원
# 소모 등 실제 계산은 전부 combat_system.py/skill_system.py에 있다.
#
# -----------------------------------------------------
# 이번 버전 범위 (중요 - 검토 시 참고)
# -----------------------------------------------------
# - 파티원/몬스터 박스는 드래곤 퀘스트 식 UI로 개편했다(사용자 확인) -
#   박스 안에는 이름/HP/MP만 표시한다. HP는 임시생명력(참가자
#   "임시생명력" - skill_system.버프자원소환_스킬_실행이 "임시생명력" 키가
#   있는 버프/자원스킬에서 채워준다, 예: 크루세이더 "신성한 빛")이 있으면
#   "(임시HP)/(현재HP)/(최대HP)", 없으면 "(현재HP)/(최대HP)"로 보여준다.
#   행동자원(일반행동 ○ / 보조행동 △ / 반응행동 □ / 쇼타임 등 기타행동 ★)은
#   보유 개수만큼 도형을 반복해 박스 맨 아래에 표시하고, 상태이상은 박스
#   밖(그 캐릭터 칸의 맨 위 - 적 박스가 화면 위쪽에 있고 아군 박스가
#   아래쪽에 있는 배치를 고려해 아군 박스 위)에 별도 라벨로 표시한다.
#   추가공격 사용가능 횟수는 이번 개편 범위에 없어 표시하지 않는다(사용자가
#   준 도형 목록에 없었음 - 필요하면 추가).
#   일반공격과 스킬 사용, 턴 넘기기를 지원한다. 몬스터 턴은
#   combat_system.몬스터_턴_실행()으로 자동 처리한다.
# - 방어 버튼은 없앴다(사용자 확인). 아이템 버튼은 소지품 시스템 자체가
#   아직 없어 자리만 만들어두고 항상 비활성화 상태다. 도망 버튼은
#   "전투이탈" 로직에 연결할 예정인데, combat_system.py/skill_system.py
#   어디에도 그런 이름의 로직이 아직 없어(상태이상 "구속"의 "도망불가"
#   플래그만 있고 실제 도망 처리는 없음) 우선 버튼만 만들어두고
#   비활성화해뒀다 - 사용자에게 확인 후 연결한다.
# - "일반공격"은 combat_system.일반공격_실행()을 그대로 부르는데, 그
#   함수 자체는 행동자원을 소모하지 않는다(무기 명중/피해 계산만 한다).
#   그래서 이 화면이 직접 참가자["행동자원"]["일반행동"]을 1 깎는다 -
#   job_skill_format.py 스킬처럼 "행동" 키가 데이터로 정의돼 있지 않아
#   여기서 프로젝트 [밸런스 기준]의 "일반행동 소모 일반공격" 그대로
#   가정했다(사용자 확인 필요할 수 있음).
# - 추가공격(일반공격/일반공격취급 스킬 사용 후 발동 가능한 추가 공격)은
#   이번 버전에 아직 없다 - 참가자["추가공격_사용가능"] 값은 이제 화면에
#   표시조차 하지 않는다(위 박스 개편 범위 참고). 실제 사용 처리는
#   다음 단계로 미룬다.
# - 스킬 목록은 시전자["원본"]["보유스킬"] 중, 이 화면을 띄울 때 넘겨준
#   "스킬데이터모음"(이름 -> job_skill_XX.py 스킬데이터)에 실제로 있는
#   것만 보여준다 - 캐릭터의 직업에 맞는 job_skill_XX.py를 찾아 이
#   딕셔너리를 만들어 넘기는 건 호출하는 쪽(main_system.py)의 몫이다.
# - "적반복지정"(타격마다 대상을 따로 지정) 타겟은 아직 지원하지 않는다 -
#   그런 스킬은 중심대상 하나로만 실행되어 skill_system.타겟_확장이
#   같은 대상을 반복 재사용한다(사용자 확인 필요할 수 있음).
# - HP/MP 막대(ui_system.py 막대_그리기/HP막대_그리기)는 위 박스 개편과
#   함께 뺐다 - 드래곤 퀘스트 참고 화면처럼 막대 없이 숫자만 보여주는
#   형태로 바꿨다(사용자 제공 참고 이미지 기준 - 막대가 다시 필요하면
#   알려달라).
# - Z(확인)/X(취소)/ESC는 ui_system.공통조작키_바인딩()으로 묶는다. Z는
#   확인콜백을 안 줘서 그 순간 포커스된 버튼을 그냥 눌러준다. X/ESC는
#   "선택모드"(일반공격/스킬 대상을 고르는 중인 상태)를 취소하는 데만
#   쓴다 - 설정메뉴는 마을/던전에서만 열게 했으므로(사용자 확인) 전투
#   중에는 열지 않는다.

import tkinter as tk

from game.system import combat_system
from game.system import skill_system
from game.system import ui_system

_대상_필요_타겟 = ("적단일", "아군단일", "적3체")


class 전투화면(tk.Frame):
    """전투상태 하나를 받아 화면에 그리고, 버튼 조작을 combat_system.py/
    skill_system.py 호출로 옮긴다.

    전투상태      : combat_system.전투_시작()이 만든 전투상태 딕셔너리.
    스킬데이터모음 : {스킬이름: 스킬데이터, ...} - 이 전투에 참가한
                     아군들의 job_skill_XX.py "스킬목록"을 전부 합친 것.
                     생략하면 스킬 버튼이 항상 "사용 가능한 스킬 없음"으로
                     뜬다.
    종료시콜백     : 전투가 끝났을 때(승리/패배) 호출할 함수. 인자로
                     전투상태["종료"]("아군승리"/"적승리") 값을 받는다.
                     생략하면 화면 안에 결과만 표시하고 아무 데도 넘어가지
                     않는다(town_system.py 등 다음 화면이 아직 없다).
    """

    def __init__(self, master, 전투상태, 스킬데이터모음=None, 종료시콜백=None):
        super().__init__(master)
        self.전투상태 = 전투상태
        self.스킬데이터모음 = 스킬데이터모음 or {}
        self.종료시콜백 = 종료시콜백

        # None이거나 ("일반공격",) 또는 ("스킬", 스킬이름, 스킬데이터).
        # None이 아니면 몬스터/파티원 행을 클릭했을 때 그 대상으로 행동을
        # 실행하는 "대상 선택 대기" 상태라는 뜻이다.
        self.선택모드 = None

        self._몬스터행 = {}   # 참가자["이름"] -> 위젯 모음 딕셔너리
        self._파티행 = {}

        self._위젯_구성()
        ui_system.공통조작키_바인딩(self, 취소콜백=self._취소)
        self.after(100, self._턴_진행)

    # -------------------------------------------------
    # 위젯 구성
    # -------------------------------------------------

    def _위젯_구성(self):
        self.상태라벨 = tk.Label(self, text="", anchor="w", font=("", 11, "bold"))
        self.상태라벨.pack(fill="x", padx=8, pady=(8, 4))

        몬스터틀 = tk.LabelFrame(self, text="적")
        몬스터틀.pack(fill="x", padx=8, pady=4)
        self.몬스터목록틀 = tk.Frame(몬스터틀)
        self.몬스터목록틀.pack(padx=6, pady=6)
        for 참가자 in self.전투상태["참가자"]:
            if 참가자["진영"] == "적":
                self._몬스터_행_생성(참가자)

        파티틀 = tk.LabelFrame(self, text="파티")
        파티틀.pack(fill="x", padx=8, pady=4)
        self.파티목록틀 = tk.Frame(파티틀)
        self.파티목록틀.pack(padx=6, pady=6)
        for 참가자 in self.전투상태["참가자"]:
            if 참가자["진영"] == "아군":
                self._파티원_행_생성(참가자)

        로그틀 = tk.LabelFrame(self, text="전투 로그")
        로그틀.pack(fill="both", expand=True, padx=8, pady=4)
        스크롤 = tk.Scrollbar(로그틀)
        스크롤.pack(side="right", fill="y")
        self.로그텍스트 = tk.Text(로그틀, height=8, state="disabled",
                                yscrollcommand=스크롤.set, wrap="word")
        self.로그텍스트.pack(fill="both", expand=True)
        스크롤.config(command=self.로그텍스트.yview)

        버튼틀 = tk.Frame(self)
        버튼틀.pack(fill="x", padx=8, pady=(4, 8))
        self.일반공격버튼 = tk.Button(버튼틀, text="일반공격", width=10,
                                   command=self._일반공격_버튼_클릭)
        self.일반공격버튼.pack(side="left", padx=2)
        self.스킬버튼 = tk.Button(버튼틀, text="스킬", width=10,
                               command=self._스킬_버튼_클릭)
        self.스킬버튼.pack(side="left", padx=2)
        tk.Button(버튼틀, text="아이템", width=10, state="disabled").pack(side="left", padx=2)
        self.도망버튼 = tk.Button(버튼틀, text="도망", width=10,
                               command=self._도망_버튼_클릭)
        self.도망버튼.pack(side="left", padx=2)
        self.턴넘기기버튼 = tk.Button(버튼틀, text="턴 넘기기", width=10,
                                   command=self._턴넘기기_버튼_클릭)
        self.턴넘기기버튼.pack(side="right", padx=2)

    def _몬스터_행_생성(self, 참가자):
        """적 박스는 아군 박스보다 조금 더 작게 만든다(최대 5마리까지
        늘어설 수 있어서 - 사용자 확인). 이름/HP/MP만 보여준다."""
        틀 = tk.Frame(self.몬스터목록틀, relief="groove", borderwidth=1)
        틀.pack(side="left", padx=3, pady=2)
        이름라벨 = tk.Label(틀, text=참가자["이름"], font=("", 9, "bold"), width=9)
        이름라벨.pack(padx=3, pady=(3, 0))
        HP텍스트 = tk.Label(틀, text="", font=("", 8))
        HP텍스트.pack(padx=3)
        MP텍스트 = tk.Label(틀, text="", font=("", 8))
        MP텍스트.pack(padx=3, pady=(0, 3))

        for 위젯 in (틀, 이름라벨, HP텍스트, MP텍스트):
            위젯.bind("<Button-1>", lambda e, p=참가자: self._대상_클릭(p))

        self._몬스터행[참가자["이름"]] = {
            "틀": 틀, "이름라벨": 이름라벨, "HP텍스트": HP텍스트, "MP텍스트": MP텍스트,
        }

    def _파티원_행_생성(self, 참가자):
        """아군은 4개 칸으로 좌우에 늘어놓는다(사용자 확인). 상태이상은
        박스 밖 - 그 캐릭터 칸의 맨 위에 별도 라벨로 둔다. 행동자원은
        박스 맨 아래에 도형으로 표시한다(_행동자원_도형 참고)."""
        칸 = tk.Frame(self.파티목록틀)
        칸.pack(side="left", padx=5, pady=2, anchor="n")

        상태이상라벨 = tk.Label(
            칸, text="", font=("", 8), fg="#b71c1c", wraplength=110, justify="left",
        )
        상태이상라벨.pack(side="top", fill="x")

        틀 = tk.Frame(칸, relief="groove", borderwidth=1)
        틀.pack(side="top")
        이름라벨 = tk.Label(틀, text=참가자["이름"], font=("", 10, "bold"), width=11)
        이름라벨.pack(padx=4, pady=(4, 0))
        HP텍스트 = tk.Label(틀, text="")
        HP텍스트.pack(padx=4)
        MP텍스트 = tk.Label(틀, text="")
        MP텍스트.pack(padx=4)
        행동자원라벨 = tk.Label(틀, text="", font=("", 11))
        행동자원라벨.pack(padx=4, pady=(0, 4))

        for 위젯 in (틀, 이름라벨):
            위젯.bind("<Button-1>", lambda e, p=참가자: self._대상_클릭(p))

        self._파티행[참가자["이름"]] = {
            "칸": 칸, "틀": 틀, "이름라벨": 이름라벨,
            "HP텍스트": HP텍스트, "MP텍스트": MP텍스트,
            "행동자원라벨": 행동자원라벨, "상태이상라벨": 상태이상라벨,
        }

    # -------------------------------------------------
    # 화면 갱신
    # -------------------------------------------------

    def _HP_문자열(self, 참가자):
        """참가자["임시생명력"](skill_system.버프자원소환_스킬_실행이
        "임시생명력" 키가 있는 스킬에서 채워준다 - 예: 크루세이더 "신성한
        빛")이 있으면 "(임시)/(현재)/(최대)", 없으면 "(현재)/(최대)"로
        표시한다(사용자 확인)."""
        최대HP = combat_system.유효_최대HP(self.전투상태, 참가자)
        임시 = 참가자.get("임시생명력", 0)
        if 임시:
            return f"HP {임시}/{참가자['현재HP']}/{최대HP}"
        return f"HP {참가자['현재HP']}/{최대HP}"

    def _MP_문자열(self, 참가자):
        if 참가자["진영"] == "아군":
            최대MP = 참가자["원본"].get("기본최대MP", 참가자["현재MP"])
        else:
            최대MP = 참가자["원본"].get("최대MP", 참가자["현재MP"])
        return f"MP {참가자['현재MP']}/{최대MP}"

    def _상태이상_문자열(self, 참가자):
        항목들 = 참가자.get("상태이상", [])
        if not 항목들:
            return ""
        return ", ".join(f"{i['이름']}({i.get('지속턴', '?')})" for i in 항목들)

    def _행동자원_도형(self, 참가자):
        """일반행동 ○ / 보조행동 △ / 반응행동 □ / 쇼타임 등 기타행동 ★을
        보유 개수만큼 반복해서 이어붙인다(사용자 확인)."""
        자원 = 참가자.get("행동자원", {})
        기타행동 = 참가자.get("기타행동", {})
        return (
            "○" * max(0, 자원.get("일반행동", 0))
            + "△" * max(0, 자원.get("보조행동", 0))
            + "□" * max(0, 자원.get("반응행동", 0))
            + "★" * max(0, 기타행동.get("쇼타임행동", 0))
        )

    def _갱신(self):
        현재참가자 = combat_system.현재_턴_참가자(self.전투상태)

        for 참가자 in self.전투상태["참가자"]:
            if 참가자["진영"] == "적":
                위젯 = self._몬스터행.get(참가자["이름"])
                if 위젯 is None:
                    continue
                위젯["HP텍스트"].config(text=self._HP_문자열(참가자))
                위젯["MP텍스트"].config(text=self._MP_문자열(참가자))
                생존여부 = "" if 참가자["생존"] else " (쓰러짐)"
                강조 = "#fff3cd" if 참가자 is 현재참가자 else self.cget("bg")
                위젯["틀"].config(bg=강조)
                위젯["이름라벨"].config(text=참가자["이름"] + 생존여부, bg=강조)
            else:
                위젯 = self._파티행.get(참가자["이름"])
                if 위젯 is None:
                    continue
                위젯["HP텍스트"].config(text=self._HP_문자열(참가자))
                위젯["MP텍스트"].config(text=self._MP_문자열(참가자))
                위젯["행동자원라벨"].config(text=self._행동자원_도형(참가자))
                위젯["상태이상라벨"].config(text=self._상태이상_문자열(참가자))

                생존여부 = "" if 참가자["생존"] else " (쓰러짐)"
                강조 = "#fff3cd" if 참가자 is 현재참가자 else self.cget("bg")
                위젯["틀"].config(bg=강조)
                위젯["이름라벨"].config(text=참가자["이름"] + 생존여부, bg=강조)

        self._로그_갱신()

    def _로그_문자열(self, 항목):
        if "비고" in 항목 and "판정" not in 항목 and "타격" not in 항목:
            대상표시 = f" -> {항목['대상']}" if "대상" in 항목 else ""
            return f"{항목.get('공격자', 항목.get('대상', ''))}{대상표시}: {항목['비고']}"
        if "행동" in 항목:
            return f"{항목.get('공격자', '')}: {항목['행동']}"
        if "타격" in 항목:
            # 몬스터 다중 타격 패턴 결과
            명중수 = sum(1 for t in 항목["타격"] if t["판정"].get("성공"))
            return (
                f"{항목['공격자']} -> {항목['대상']} [{항목.get('패턴', '?')}] "
                f"{명중수}/{len(항목['타격'])}회 명중, 총 {항목.get('총피해', 0)} 피해"
            )
        if "판정" in 항목:
            판정 = 항목["판정"]
            if not 판정.get("성공"):
                return f"{항목['공격자']} -> {항목['대상']}: 빗나감"
            치명 = " (치명타!)" if 판정.get("치명타") else ""
            return f"{항목['공격자']} -> {항목['대상']}: {항목.get('피해', 0)} 피해{치명}"
        return str(항목)

    def _로그_갱신(self):
        self.로그텍스트.config(state="normal")
        self.로그텍스트.delete("1.0", "end")
        for 항목 in self.전투상태["로그"]:
            self.로그텍스트.insert("end", self._로그_문자열(항목) + "\n")
        self.로그텍스트.config(state="disabled")
        self.로그텍스트.see("end")

    def _상태메시지(self, 문자열):
        self.상태라벨.config(text=문자열)

    # -------------------------------------------------
    # 턴 진행
    # -------------------------------------------------

    def _턴_진행(self):
        self._갱신()

        if self.전투상태.get("종료"):
            self._전투종료_처리()
            return

        참가자 = combat_system.현재_턴_참가자(self.전투상태)
        if 참가자["진영"] == "적":
            self._상태메시지(f"{참가자['이름']}의 턴 (자동 진행)")
            self.일반공격버튼.config(state="disabled")
            self.스킬버튼.config(state="disabled")
            self.도망버튼.config(state="disabled")
            self.턴넘기기버튼.config(state="disabled")
            combat_system.몬스터_턴_실행(self.전투상태, 참가자)
            combat_system.다음_턴(self.전투상태)
            self.after(500, self._턴_진행)
        else:
            self._상태메시지(f"{참가자['이름']}의 턴입니다. 행동을 선택하세요.")
            self._행동버튼_갱신(참가자)

    def _행동버튼_갱신(self, 참가자):
        self.턴넘기기버튼.config(state="normal")
        무기있음 = 참가자.get("장비데이터", {}).get("무기") is not None
        일반행동있음 = 참가자["행동자원"].get("일반행동", 0) > 0
        self.일반공격버튼.config(
            state="normal" if (무기있음 and 일반행동있음) else "disabled"
        )
        보유스킬있음 = any(
            이름 in self.스킬데이터모음 for 이름 in 참가자["원본"].get("보유스킬", [])
        )
        self.스킬버튼.config(state="normal" if 보유스킬있음 else "disabled")
        # "도망"도 일반공격과 같은 자원(일반행동 1개)을 쓴다고 가정했다 -
        # combat_system.전투이탈_시도()와 마찬가지로 아직 프로젝트에 정해진
        # 비용이 없어 임시로 정한 값이다(사용자 확인 필요할 수 있음).
        self.도망버튼.config(state="normal" if 일반행동있음 else "disabled")

    def _전투종료_처리(self):
        self.일반공격버튼.config(state="disabled")
        self.스킬버튼.config(state="disabled")
        self.도망버튼.config(state="disabled")
        self.턴넘기기버튼.config(state="disabled")
        결과 = self.전투상태["종료"]
        if 결과 == "전투이탈":
            self._상태메시지("파티가 전투에서 도망쳤습니다.")
        else:
            self._상태메시지(f"전투 종료: {결과}")
        if self.종료시콜백 is not None:
            self.종료시콜백(결과)

    # -------------------------------------------------
    # 버튼 / 대상 선택 처리
    # -------------------------------------------------

    def _취소(self):
        """X 또는 ESC로 부른다 - 대상 선택 대기 중(선택모드가 있음)일 때만
        선택을 취소하고, 아니면 아무 일도 하지 않는다(공통조작키 규칙 -
        ui_system.py 참고)."""
        if self.선택모드 is None:
            return
        self.선택모드 = None
        참가자 = combat_system.현재_턴_참가자(self.전투상태)
        self._상태메시지(f"{참가자['이름']}의 턴입니다. 행동을 선택하세요.")

    def _일반공격_버튼_클릭(self):
        self.선택모드 = ("일반공격",)
        self._상태메시지("일반공격할 적을 클릭하세요.")

    def _스킬_버튼_클릭(self):
        참가자 = combat_system.현재_턴_참가자(self.전투상태)
        후보 = [이름 for 이름 in 참가자["원본"].get("보유스킬", [])
                if 이름 in self.스킬데이터모음]
        if not 후보:
            self._상태메시지("사용할 수 있는 스킬 데이터가 없습니다.")
            return

        팝업 = tk.Toplevel(self)
        팝업.title(f"{참가자['이름']}의 스킬")
        for 이름 in 후보:
            스킬데이터 = self.스킬데이터모음[이름]
            가능, 사유 = skill_system.사용_가능여부(self.전투상태, 참가자, 스킬데이터)
            표시 = 이름 if 가능 else f"{이름}  (사용 불가: {사유})"
            tk.Button(
                팝업, text=표시, anchor="w",
                state=("normal" if 가능 else "disabled"),
                command=lambda n=이름, d=스킬데이터, w=팝업: self._스킬_선택됨(n, d, w),
            ).pack(fill="x", padx=4, pady=2)

    def _스킬_선택됨(self, 이름, 스킬데이터, 팝업):
        팝업.destroy()
        if 스킬데이터.get("타겟") in _대상_필요_타겟:
            self.선택모드 = ("스킬", 이름, 스킬데이터)
            self._상태메시지(f"'{이름}' 사용 대상을 클릭하세요.")
        else:
            self._스킬_실행(이름, 스킬데이터, None)

    def _도망_버튼_클릭(self):
        self.선택모드 = None
        참가자 = combat_system.현재_턴_참가자(self.전투상태)
        if 참가자["행동자원"].get("일반행동", 0) <= 0:
            self._상태메시지("일반행동이 남아있지 않습니다.")
            return
        참가자["행동자원"]["일반행동"] -= 1
        성공, 굴림값, 난이도 = combat_system.전투이탈_시도(self.전투상태, 참가자)
        if 성공:
            self._턴_진행()  # 전투상태["종료"]="전투이탈"을 감지해 종료 처리로 넘어간다
        else:
            self._갱신()
            self._상태메시지(f"도망 실패 ({굴림값} vs DC{난이도})" if 굴림값 is not None
                          else "도망 실패 (도망불가 상태)")
            self._행동버튼_갱신(참가자)

    def _턴넘기기_버튼_클릭(self):
        self.선택모드 = None
        combat_system.다음_턴(self.전투상태)
        self._턴_진행()

    def _대상_클릭(self, 대상):
        if self.선택모드 is None:
            return
        if not 대상["생존"]:
            self._상태메시지("이미 쓰러진 대상입니다.")
            return

        종류 = self.선택모드[0]
        if 종류 == "일반공격":
            if 대상["진영"] != "적":
                self._상태메시지("일반공격은 적을 대상으로 선택해야 합니다.")
                return
            self.선택모드 = None
            self._일반공격_실행(대상)
        elif 종류 == "스킬":
            _, 이름, 스킬데이터 = self.선택모드
            필요진영 = "적" if 스킬데이터.get("타겟") in ("적단일", "적3체") else "아군"
            if 대상["진영"] != 필요진영:
                self._상태메시지(f"'{이름}'은(는) {필요진영} 쪽 대상을 선택해야 합니다.")
                return
            self.선택모드 = None
            self._스킬_실행(이름, 스킬데이터, 대상)

    def _일반공격_실행(self, 대상):
        참가자 = combat_system.현재_턴_참가자(self.전투상태)
        if 참가자["행동자원"].get("일반행동", 0) <= 0:
            self._상태메시지("일반행동이 남아있지 않습니다.")
            return
        참가자["행동자원"]["일반행동"] -= 1
        combat_system.일반공격_실행(self.전투상태, 참가자, 대상)
        self._갱신()
        self._행동버튼_갱신(참가자)

    def _스킬_실행(self, 이름, 스킬데이터, 중심대상):
        참가자 = combat_system.현재_턴_참가자(self.전투상태)
        try:
            skill_system.스킬_실행(self.전투상태, 참가자, 이름, 스킬데이터, 중심대상=중심대상)
        except ValueError as 오류:
            self._상태메시지(str(오류))
            return
        self._갱신()
        self._행동버튼_갱신(참가자)