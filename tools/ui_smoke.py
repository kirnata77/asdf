"""화면 스모크 테스트 - 실제 Kivy 앱을 띄워 주요 화면 동작을 호출하고 스크린샷을 남긴다.

    pip install kivy                       # 한 번
    xvfb-run -a -s "-screen 0 720x1280x24" python tools/ui_smoke.py [스크린샷폴더]   # 리눅스(화면 없음)
    python tools/ui_smoke.py [스크린샷폴더]                                        # Windows/맥(창이 뜬다)

tests/는 kivy 없이 gameflow 이하만 검사한다. 화면(game/screens) 코드를 바꿨다면 이것을
돌려 확인한다(CLAUDE.md 완료 기준 3). 레벨 10 파티를 만들어 다음을 실제로 호출한다:
파티 구성 이름칸(6자 제한), 상점 구매/판매 목록, 능력치 배분 팝업, 장비 교체 팝업/상세보기, 뒤로 키, 전투 화면 스킬 팝업과 스킬별 실제 타겟(4직업 전 스킬),
적반복지정(썬더콜링) 선택 - 은신 대상 거부 포함, 도망(구속이면 막힘 팝업, 실패하면 턴 종료),
전투 종료 팝업(승리 전리품/없음, 도망, 패배).
예외가 나면 종료코드 1.
스크린샷 기본 폴더: ui_smoke_shots/ (.gitignore에 들어 있다).
"""

import json
import os
import random
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("KIVY_NO_ARGS", "1")

import main  # noqa: E402 - 크래시 로그 훅/폰트 등록 등 앱 초기화를 그대로 쓴다
from kivy.clock import Clock  # noqa: E402
from kivy.core.window import Window  # noqa: E402

import gameflow as gf  # noqa: E402
from game.screens import screens_party  # noqa: E402
from game.system import dice_utils  # noqa: E402
from game.system.combat import flow  # noqa: E402
from tests import support  # noqa: E402

스크린샷폴더 = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "ui_smoke_shots")
결과 = {"단계": [], "오류": None}
전직 = {
    "귀검사": "웨펀마스터",
    "거너": "레인저",
    "마법사": "엘리멘탈마스터",
    "프리스트": "크루세이더",
}


def _찍기(이름):
    os.makedirs(스크린샷폴더, exist_ok=True)
    Window.screenshot(name=os.path.join(스크린샷폴더, 이름 + ".png"))


def _팝업_닫기():
    for 위젯 in list(Window.children)[:-1]:
        if hasattr(위젯, "dismiss"):
            위젯.dismiss()


class 스모크앱(main.DnfMobileApp):
    def on_start(self):
        self._단계 = self._단계들()
        Clock.schedule_once(self._다음, 1)

    def _다음(self, _dt):
        try:
            Clock.schedule_once(
                self._다음, next(self._단계)
            )  # 단계 사이에 화면을 그리게 기다린다
        except StopIteration:
            self.stop()
        except Exception:  # noqa: BLE001
            결과["오류"] = traceback.format_exc()
            self.stop()

    def _단계들(self):
        random.seed(3)
        상태 = support.새게임(
            [("", "귀검사"), ("", "거너"), ("", "마법사"), ("", "프리스트")]
        )
        for c in 상태["파티"]["파티원"]:
            support.성장(상태, c, 10, 전직=전직[c["직업"]])
        gf.파티_최대치로_회복(상태)
        self.게임상태 = 상태
        매니저 = self.root

        매니저.current = "파티생성"
        이름칸 = 매니저.get_screen("파티생성").슬롯목록[0]["이름입력"]
        assert 이름칸.hint_text == f"이름최대{gf.캐릭터명_최대길이}자", 이름칸.hint_text
        yield 0.5
        _찍기("party_create_hint")
        이름칸.text = "가나다라마바사아"
        assert 이름칸.text == "가나다라마바", 이름칸.text
        yield 0.3
        _찍기("party_create_name6")
        결과["단계"].append("파티 구성 이름칸(안내 문구, 6자 제한)")

        # 이름이 겹치면 시작하지 않고 안내 줄에 알린다(B4)
        파티생성 = 매니저.get_screen("파티생성")
        파티생성.슬롯목록[1]["참여토글"].state = "down"
        파티생성.슬롯목록[0]["이름입력"].text = "철수"
        파티생성.슬롯목록[1]["이름입력"].text = "철수"
        이전상태 = self.게임상태
        파티생성._시작()
        assert 매니저.current == "파티생성", 매니저.current
        assert "겹칩니다" in 파티생성.안내라벨.text, 파티생성.안내라벨.text
        assert self.게임상태 is 이전상태
        yield 0.3
        _찍기("party_create_duplicate")
        결과["단계"].append("파티 구성 이름 중복 -> 시작 안 함")

        매니저.current = "상점"
        상점 = 매니저.get_screen("상점")
        상점._대분류_그리기("구매")
        상점._탭목록_그리기("구매", "장비")
        yield 0.5
        _찍기("shop_buy")
        상점._탭목록_그리기("판매", "장비")
        yield 0.5
        _찍기("shop_sell")
        결과["단계"].append("상점 구매/판매 목록")

        매니저.current = "파티관리"
        매니저.get_screen("파티관리")._능력치배분_팝업(
            상태["파티"]["파티원"][0], 2, lambda 배분: None
        )
        yield 0.5
        _찍기("stat_popup")
        _팝업_닫기()
        결과["단계"].append("능력치 배분 팝업")

        # 장비 교체 팝업: 칸마다 이름 + 간단요약(무기 공격력/AC) + [상세보기]
        for 슬롯 in ("무기", "상의"):
            for 이름 in list(상태["상점카탈로그"]["장비"][슬롯])[:3]:
                상태["소지품"]["장비"][이름] = 상태["소지품"]["장비"].get(이름, 0) + 1
        귀검사 = 상태["파티"]["파티원"][0]
        매니저.current = "파티원"
        for 슬롯, 요약 in (("무기", "무기 공격력 "), ("상의", "AC ")):
            screens_party._장비교체_팝업(귀검사, 슬롯, lambda: None)
            yield 0.5
            _찍기(f"equip_swap_{슬롯}")
            팝업 = Window.children[0]
            글들 = [w.text for w in 팝업.walk(restrict=True) if hasattr(w, "text")]
            assert any(요약 in 글 for 글 in 글들), 글들
            assert 글들.count("상세보기") >= 2, 글들
            _팝업_닫기()
            yield 0.3
        무기 = next(iter(상태["상점카탈로그"]["장비"]["무기"].values()))
        screens_party._아이템_상세_팝업(무기)
        yield 0.5
        _찍기("equip_detail")
        _팝업_닫기()
        결과["단계"].append("장비 교체 팝업(무기/상의) + 상세보기")
        yield 0.3

        # 핸드폰 [뒤로] 키(27): 맨 위 팝업의 취소/닫기 -> 화면의 뒤로/나가기 순
        def 뒤로():
            Window.dispatch("on_keyboard", 27, 0, None, [])

        def 팝업수():
            return sum(hasattr(w, "dismiss") for w in Window.children)

        screens_party._장비교체_팝업(귀검사, "무기", lambda: None)
        screens_party._아이템_상세_팝업(무기)
        yield 0.5
        assert 팝업수() == 2, 팝업수()
        뒤로()
        yield 0.5
        assert 팝업수() == 1, "상세보기만 닫혀야 한다"
        뒤로()
        yield 0.5
        assert 팝업수() == 0 and 매니저.current == "파티원", 매니저.current
        매니저.get_screen("파티원").복귀화면 = "파티관리"
        매니저.get_screen("파티관리").복귀화면 = "마을"
        뒤로()
        assert 매니저.current == "파티관리", 매니저.current
        뒤로()
        assert 매니저.current == "마을", 매니저.current
        뒤로()
        assert 매니저.current == "마을", "마을에서는 아무 일도 없어야 한다"
        상점 = 매니저.get_screen("상점")
        상점.복귀화면 = "마을"
        매니저.current = "상점"
        상점._대분류_그리기("구매")
        뒤로()
        글들 = [w.text for w in 상점.내용틀.walk(restrict=True) if hasattr(w, "text")]
        assert "나가기" in 글들 and 매니저.current == "상점", 글들
        뒤로()
        assert 매니저.current == "마을", 매니저.current
        매니저.current = "메인메뉴"
        뒤로()
        assert 매니저.current == "메인메뉴", 매니저.current
        결과["단계"].append("뒤로 키(팝업 겹침/파티원/파티관리/마을/상점/메인메뉴)")

        gf._전투_시작(상태, ["타우 아미", "고블린", "고블린"], 레벨=6, 차수=2)
        support.반응_처리(상태)
        전투 = 매니저.get_screen("전투")
        전투.갱신(신규=True)
        매니저.current = "전투"
        전투상태 = 상태["전투상태"]

        def 차례(이름):
            p = next(x for x in 전투상태["참가자"] if x["이름"] == 이름)
            전투상태["현재턴"] = 전투상태["참가자"].index(p)
            flow._턴_시작_처리(전투상태, p)
            return p

        for 이름 in ("마법사", "거너", "귀검사", "프리스트"):
            p = 차례(이름)
            _팝업_닫기()
            전투._스킬_버튼_클릭(p)
            for 스킬 in p["원본"]["보유스킬"]:
                데이터 = 상태["스킬데이터모음"][스킬]
                assert 전투._실제_타겟(데이터) == gf.스킬_실제_타겟(상태, 데이터), 스킬
            결과["단계"].append(
                f"{이름} 스킬 팝업/실제 타겟 {len(p['원본']['보유스킬'])}개"
            )
        yield 0.5
        _찍기("battle_skill_popup")
        _팝업_닫기()

        차례("마법사")
        yield 0.3
        전투._스킬_클릭("썬더콜링", 상태["스킬데이터모음"]["썬더콜링"])
        assert 전투.선택모드[0] == "반복지정", 전투.선택모드
        적 = [x for x in 전투상태["참가자"] if x["진영"] == "적" and x["생존"]]
        gf.skill_system._상태이상_부여(전투상태, 적[1], "은신", 3, None)
        전투._반복지정_선택(적[1])
        assert "지정할 수 없는" in 전투.안내라벨.text, 전투.안내라벨.text
        while 전투.선택모드 and 전투.선택모드[0] == "반복지정":
            전투._반복지정_선택(적[0])
        결과["단계"].append("썬더콜링 반복지정(은신 대상 거부 포함)")
        yield 0.5
        _찍기("battle_after_thundercalling")

        # 도망: 파티 중 한 명이라도 구속이면 [도망]이 판정 없이 막힘 팝업을 띄운다
        현재 = 차례("귀검사")
        거너 = next(x for x in 전투상태["참가자"] if x["이름"] == "거너")
        gf.skill_system._상태이상_부여(전투상태, 거너, "구속", 3, None)
        로그수 = len(전투상태["로그"])
        전투._도망_클릭()
        yield 0.5
        글들 = [
            w.text
            for 팝업 in list(Window.children)[:-1]
            for w in 팝업.walk(restrict=True)
            if hasattr(w, "text")
        ]
        assert "도망 칠 수 없습니다.\n대상 : 거너\n상태이상 : 구속" in 글들, 글들
        assert "확인" in 글들, 글들
        _찍기("battle_flee_blocked")
        뒤로()
        yield 0.3
        assert 팝업수() == 0, "확인(뒤로 키)으로 닫혀야 한다"
        assert (
            len(전투상태["로그"]) == 로그수
            and 전투상태["참가자"][전투상태["현재턴"]] is 현재
        ), "막히면 굴림도 턴 변화도 없다"
        결과["단계"].append("구속이면 도망 불가 팝업(대상/상태이상/확인)")

        # 구속이 풀리면 확인 팝업 -> 실패 시 현재 캐릭터의 턴이 끝난다
        거너["상태이상"] = [i for i in 거너["상태이상"] if i["이름"] != "구속"]
        전투._도망_클릭()
        yield 0.3
        예버튼 = next(
            w
            for 팝업 in list(Window.children)[:-1]
            for w in 팝업.walk(restrict=True)
            if getattr(w, "text", None) == "예"
        )
        원래 = dice_utils.random.randint
        dice_utils.random.randint = lambda a, b: 1
        try:
            예버튼.dispatch("on_release")
            yield 1.0
        finally:
            dice_utils.random.randint = 원래
        assert (
            전투상태["종료"] is not None
            or 전투상태["참가자"][전투상태["현재턴"]] is not 현재
        ), "도망에 실패하면 턴이 넘어가야 한다"
        결과["단계"].append("도망 실패 -> 현재 캐릭터 턴 종료")
        _찍기("battle_after_flee_fail")

        # 전투 종료 팝업: 승리(전리품) -> 던전, 도망 -> 던전, 패배 -> 마을
        def 팝업글():
            return [
                w.text
                for 팝업 in list(Window.children)[:-1]
                for w in 팝업.walk(restrict=True)
                if hasattr(w, "text")
            ]

        def 확인_누르기():
            버튼 = next(
                w
                for 팝업 in list(Window.children)[:-1]
                for w in 팝업.walk(restrict=True)
                if getattr(w, "text", None) == "확인"
            )
            버튼.dispatch("on_release")

        _팝업_닫기()
        gf.던전_진입(상태, "map_01A_D01_Lorien")
        for 몬스터들, 끝내기, 첫줄, 전리품줄, 도착, 사진 in (
            (
                ["고블린", "겁쟁이 고블린"],
                support.강제_승리,
                "전투 승리!",
                True,
                "던전",
                "battle_end_win",
            ),
            (["힐가브"], support.강제_승리, "전투 승리!", False, "던전", None),
            (
                ["타우 아미"],
                lambda s: flow.전투이탈_시도(s["전투상태"], gf.아군_목록(s)[0]),
                "도망쳤다!",
                None,
                "던전",
                None,
            ),
            (
                ["타우 아미"],
                support.강제_패배,
                "전투 패배!",
                None,
                "마을",
                "battle_end_lose",
            ),
        ):
            gf._전투_시작(상태, 몬스터들, 레벨=6, 차수=2)  # 시작 반응에 안 쓰러지게
            support.반응_처리(상태)
            매니저.current = "전투"
            전투.갱신(신규=True)
            yield 0.3
            # 체력 1 몬스터(힐가브)는 전투시작 반응에 쓰러져 이미 팝업이 떠 있을 수 있다
            if 상태["전투상태"] is not None:
                if 첫줄 == "도망쳤다!":
                    원래 = dice_utils.random.randint
                    dice_utils.random.randint = lambda a, b: 20
                    try:
                        끝내기(상태)
                    finally:
                        dice_utils.random.randint = 원래
                else:
                    끝내기(상태)
                전투.갱신()
            yield 0.5
            글 = next(
                t
                for t in 팝업글()
                if t.split("\n")[0] in ("전투 승리!", "도망쳤다!", "전투 패배!")
            )
            줄들 = 글.split("\n")
            assert 줄들[0] == 첫줄, 글
            if 전리품줄 is True:
                assert 줄들[1] == "전리품" and len(줄들) >= 3 and "없음" not in 줄들, 글
            elif 전리품줄 is False:
                assert 줄들[1:3] == ["전리품", "없음"], 글
            else:
                assert "전리품" not in 줄들, 글
            if 사진:
                _찍기(사진)
            확인_누르기()
            yield 0.5
            assert 매니저.current == 도착, 매니저.current
            if 도착 == "마을":
                gf.던전_진입(상태, "map_01A_D01_Lorien")
        결과["단계"].append("전투 종료 팝업(승리 전리품/없음, 도망, 패배)")


if __name__ == "__main__":
    스모크앱().run()
    for 단계 in 결과["단계"]:
        print("OK  ", 단계)
    if 결과["오류"]:
        print(결과["오류"])
    print(
        json.dumps(
            {"스크린샷": 스크린샷폴더, "성공": 결과["오류"] is None}, ensure_ascii=False
        )
    )
    sys.exit(1 if 결과["오류"] else 0)
