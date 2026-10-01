"""화면 스모크 테스트 - 실제 Kivy 앱을 띄워 주요 화면 동작을 호출하고 스크린샷을 남긴다.

    pip install kivy                       # 한 번
    xvfb-run -a -s "-screen 0 720x1280x24" python tools/ui_smoke.py [스크린샷폴더]   # 리눅스(화면 없음)
    python tools/ui_smoke.py [스크린샷폴더]                                        # Windows/맥(창이 뜬다)

tests/는 kivy 없이 gameflow 이하만 검사한다. 화면(game/screens) 코드를 바꿨다면 이것을
돌려 확인한다(CLAUDE.md 완료 기준 3). 레벨 10 파티를 만들어 다음을 실제로 호출한다:
파티 구성 이름칸(6자 제한), 상점 구매/판매 목록, 능력치 배분 팝업, 장비 교체 팝업/상세보기, 뒤로 키, 전투 화면 스킬 팝업과 스킬별 실제 타겟(4직업 전 스킬),
적 대상 선택 팝업(일반공격, 취소), 적반복지정(썬더콜링) 선택 - 은신 대상 거부 포함, 도망(구속이면 막힘 팝업, 실패하면 턴 종료),
전투 종료 팝업(승리 전리품/없음, 도망, 패배)과 전투 보상(3칸 선택/빈칸 포기), 자동전투(켜기/중지/끝까지), 몬스터 크기 배율, 적 도망(황금 고블린).
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
from kivy.uix.button import Button  # noqa: E402

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
        assert 이름칸.hint_text == gf.캐릭터명_안내, 이름칸.hint_text
        yield 0.5
        _찍기("party_create_hint")
        이름칸.text = "가나다라마바사아"
        assert 이름칸.text == "가나다라마바", 이름칸.text
        이름칸.text = "abcdefghijklmnop"
        assert 이름칸.text == "abcdefghijkl", 이름칸.text
        이름칸.text = "가나다라마바"
        yield 0.3
        _찍기("party_create_name6")
        결과["단계"].append("파티 구성 이름칸(안내 문구, 한글 6자/영문 12자 제한)")

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

        # [스킬습득] 팝업: 직업 계열 스킬 목록 + 비용, 골드가 모자라면 버튼 잠금, 누르면 배운다
        파티관리 = 매니저.get_screen("파티관리")
        파티관리.갱신()
        assert any(
            getattr(w, "text", "") == "스킬습득" for w in 파티관리.walk(restrict=True)
        ), "스킬습득 버튼 없음"
        yield 0.3
        _찍기("party_manage")
        귀검사 = 상태["파티"]["파티원"][0]
        상태["소지품"]["골드"] = 50
        파티관리._스킬습득_팝업(귀검사)
        yield 0.5
        _찍기("skill_learn_popup")
        팝업 = list(Window.children)[0]
        스킬버튼 = [
            w
            for w in 팝업.walk(restrict=True)
            if isinstance(w, Button) and w.text.endswith("골드")
        ]
        # 골드 50: 50골드(1차 계열) 스킬만 누를 수 있고 100골드(전직) 스킬은 잠김
        assert 스킬버튼 and all(
            b.disabled == (b.text == "100골드") for b in 스킬버튼
        ), [(b.text, b.disabled) for b in 스킬버튼]
        보유전 = list(귀검사["보유스킬"])
        스킬버튼[0].dispatch("on_release")
        yield 0.3
        새스킬 = [n for n in 귀검사["보유스킬"] if n not in 보유전]
        assert len(새스킬) == 1 and 상태["소지품"]["골드"] == 0, 새스킬
        남은버튼 = [
            w
            for w in 팝업.walk(restrict=True)
            if isinstance(w, Button) and w.text.endswith("골드")
        ]
        assert 남은버튼 and all(b.disabled for b in 남은버튼)  # 골드 0 -> 잠김
        _찍기("skill_learn_after")
        상세 = next(
            w
            for w in 팝업.walk(restrict=True)
            if isinstance(w, Button) and w.text == "상세보기"
        )
        상세.dispatch("on_release")
        yield 0.5
        assert list(Window.children)[0].title == "스킬 상세보기"
        _찍기("skill_learn_detail")
        _팝업_닫기()
        결과["단계"].append(
            "스킬습득 팝업(한 줄: 이름/가격/상세보기, 가격 누르면 배움, 모자라면 잠금, 상세 팝업)"
        )

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
            # 이름 없이 만든 캐릭터는 전직명이 되므로 1차 직업으로도 찾는다
            p = next(
                x
                for x in 전투상태["참가자"]
                if 이름 in (x["이름"], (x.get("원본") or {}).get("직업"))
            )
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

        # 적 대상은 이름 목록 팝업에서 고른다 - 살아 있는 적 버튼 + 맨 아래 [취소]
        def 대상버튼들():
            assert 팝업수() == 1, 팝업수()
            return [
                w
                for w in Window.children[0].walk(restrict=True)
                if isinstance(w, Button)
            ]

        적 = [x for x in 전투상태["참가자"] if x["진영"] == "적" and x["생존"]]
        차례("귀검사")
        전투._일반공격_클릭()
        yield 0.3
        글들 = [b.text for b in 대상버튼들()]
        assert len(글들) == len(적) + 1 and 글들[-1] == "취소", 글들
        assert 글들[:-1] == [p["이름"] for p in 적], 글들
        _찍기("battle_target_popup")
        뒤로()
        yield 0.3
        assert 팝업수() == 0 and 전투.선택모드 is None, (
            "취소(뒤로 키)면 행동 없이 닫힌다"
        )
        로그수 = len(전투상태["로그"])
        전투._일반공격_클릭()
        yield 0.3
        대상버튼들()[0].trigger_action(duration=0)
        yield 0.5
        assert 팝업수() == 0 and len(전투상태["로그"]) > 로그수, "고르면 바로 공격한다"
        결과["단계"].append("일반공격 대상 팝업(적 목록 + 취소/뒤로 키, 고르면 공격)")

        차례("마법사")
        yield 0.3
        전투._스킬_클릭("썬더콜링", 상태["스킬데이터모음"]["썬더콜링"])
        assert 전투.선택모드[0] == "반복지정", 전투.선택모드
        적 = [x for x in 전투상태["참가자"] if x["진영"] == "적" and x["생존"]]
        gf.skill_system._상태이상_부여(전투상태, 적[1], "은신", 3, None)
        yield 0.3
        _찍기("battle_target_popup_repeat")
        대상버튼들()[1].trigger_action(duration=0)
        assert "지정할 수 없는" in 전투.안내라벨.text, 전투.안내라벨.text
        while 전투.선택모드 and 전투.선택모드[0] == "반복지정":
            대상버튼들()[0].trigger_action(duration=0)
        assert 팝업수() == 0, 팝업수()
        결과["단계"].append(
            "썬더콜링 반복지정 - 대상 팝업을 다시 열며 선택(은신 대상 거부 포함)"
        )
        yield 0.5
        _찍기("battle_after_thundercalling")

        # 도망: 파티 중 한 명이라도 구속이면 [도망]이 판정 없이 막힘 팝업을 띄운다
        현재 = 차례("귀검사")
        거너 = next(
            x for x in 전투상태["참가자"] if (x.get("원본") or {}).get("직업") == "거너"
        )
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
        assert (
            f"도망 칠 수 없습니다.\n대상 : {거너['이름']}\n상태이상 : 구속" in 글들
        ), 글들
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

        def 팝업_버튼(글):
            return next(
                w
                for 팝업 in list(Window.children)[:-1]
                for w in 팝업.walk(restrict=True)
                if getattr(w, "text", None) == 글
            )

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
            if 첫줄 == "전투 승리!":
                # [확인]은 전투 보상을 받거나 포기하기 전까지 잠겨 있다
                assert (
                    팝업_버튼("확인").disabled and not 팝업_버튼("전투 보상").disabled
                )
                팝업_버튼("전투 보상").dispatch("on_release")
                yield 0.5
                칸 = gf.전투_보상_칸(상태)
                assert 팝업_버튼("선택").disabled  # 박스를 누르기 전
                if 전리품줄 is True:  # 고블린들 - 후보가 있다
                    assert all(칸), 칸
                    보유 = 상태["소지품"]["장비"].get(칸[1], 0)
                    박스 = next(
                        w
                        for 팝업 in list(Window.children)[:-1]
                        for w in 팝업.walk(restrict=True)
                        if getattr(w, "text", None) == 칸[1]
                    ).parent
                    박스.dispatch("on_release")
                    yield 0.3
                    _찍기("battle_reward")
                    팝업_버튼("선택").dispatch("on_release")
                    yield 0.3
                    assert 상태["소지품"]["장비"][칸[1]] == 보유 + 1
                else:  # 힐가브 - 후보 없음, 세 칸 모두 빈칸
                    assert 칸 == [None, None, None], 칸
                    _찍기("battle_reward_empty")
                    골드 = 상태["소지품"]["골드"]
                    팝업_버튼("포기하기(10골드)").dispatch("on_release")
                    yield 0.3
                    assert 상태["소지품"]["골드"] == 골드 + 10
                assert not gf.전투_보상_대기중(상태)
                assert (
                    not 팝업_버튼("확인").disabled and 팝업_버튼("전투 보상").disabled
                )
            확인_누르기()
            yield 0.5
            assert 매니저.current == 도착, 매니저.current
            if 도착 == "마을":
                gf.던전_진입(상태, "map_01A_D01_Lorien")
        결과["단계"].append(
            "전투 종료 팝업(승리 전리품/없음, 도망, 패배) + 전투 보상 선택/포기"
        )

        # 자동전투: 켜면 [자동전투 중지]로 바뀌고 다른 행동 버튼은 잠긴다. 중지하면 풀린다.
        def 버튼(글):
            return next(
                w
                for w in 전투.액션틀.walk(restrict=True)
                if getattr(w, "text", None) == 글
            )

        def 아군_차례로_맞추기():
            p = next(x for x in gf.아군_목록(상태) if x["생존"])
            상태["전투상태"]["현재턴"] = 상태["전투상태"]["참가자"].index(p)
            flow._턴_시작_처리(상태["전투상태"], p)

        gf._전투_시작(상태, ["타우 아미", "타우 아미"], 레벨=6, 차수=2)
        support.반응_처리(상태)
        매니저.current = "전투"
        아군_차례로_맞추기()
        전투.갱신(신규=True)
        yield 0.3
        버튼("자동전투").dispatch("on_release")
        assert 전투.자동전투
        중지 = 버튼("자동전투 중지")
        assert all(
            버튼(글).disabled
            for 글 in ("일반공격", "스킬", "아이템", "도망", "턴 넘기기")
        )
        중지.dispatch("on_release")  # 첫 턴이 돌기 전에(0초 예약) 중지
        yield 0.3
        assert not 전투.자동전투 and 버튼("자동전투")
        if not gf.전투_종료됨(상태) and 상태["전투상태"] is not None:
            assert not 버튼("일반공격").disabled or not gf.아군_차례인가(상태)
        결과["단계"].append("자동전투 켜기 -> 버튼 잠금 -> 중지")

        # 다시 켜면 전투가 끝날 때까지 스스로 진행한다(결과 팝업이 뜬다)
        if 상태["전투상태"] is not None:
            버튼("자동전투").dispatch("on_release")
            for _ in range(100):
                if 상태["전투상태"] is None:
                    break
                yield 0.2
            assert 상태["전투상태"] is None, "자동전투가 전투를 끝내지 못했다"
            assert not 전투.자동전투
            _찍기("battle_auto_end")
            _팝업_닫기()
        결과["단계"].append("자동전투로 전투 끝까지 진행 -> 결과 팝업")

        # 몬스터 크기: 소형 0.75 / 중형 1 / 대형 1.25배, 칸 바닥(발바닥) 맞춤, 대형이 뒤(먼저 그림)
        from kivy.graphics import Rectangle

        gf._전투_시작(상태, ["고블린", "타우 비스트", "타우 아미"], 레벨=6, 차수=2)
        support.반응_처리(상태)
        매니저.current = "전투"
        전투.갱신(신규=True)
        yield 0.6
        적 = gf.적_목록(상태)
        사각형 = [
            c for c in 전투.적그래픽행.canvas.after.children if isinstance(c, Rectangle)
        ]
        assert len(사각형) == 3, len(사각형)
        칸들 = [칸 for 칸, _, _ in 전투._적그림목록]
        for 사각, (칸, 경로, 배율), (_, p) in zip(
            사각형, 전투._적그림목록, gf.적_그리기_순서(적)
        ):
            tw, th = 사각.texture.size
            맞춤 = min(칸.width / tw, 칸.height / th)
            assert abs(사각.size[1] - th * 맞춤 * 배율) < 1, (p["이름"], 사각.size)
            assert abs(사각.pos[1] - 칸.y) < 1  # 발바닥 = 칸 바닥
            assert abs(사각.pos[0] + 사각.size[0] / 2 - 칸.center_x) < 1
        assert [p["원본"]["몬스터명"] for _, p in gf.적_그리기_순서(적)][
            0
        ] == "타우 비스트"
        assert len(set(칸들)) == 3
        _찍기("battle_monster_size")
        결과["단계"].append("몬스터 크기 배율(소/중/대) + 발바닥 맞춤 + 대형이 뒤")

        # 황금 고블린(도망턴 5): 자기 턴이 5번 끝나면 도망 -> 이름표 "(도망)", 그림 없음,
        # 적이 모두 도망쳤으면 "적이 도망쳤다!" 팝업 -> [확인] -> 던전
        _팝업_닫기()
        gf._전투_시작(상태, ["황금 고블린"], 레벨=3, 차수=1)
        support.반응_처리(상태)
        매니저.current = "전투"
        황금 = gf.적_목록(상태)[0]
        황금["끝난턴수"] = 4
        상태["전투상태"]["현재턴"] = 상태["전투상태"]["참가자"].index(황금)
        상태["전투상태"]["현재턴_행동완료"] = True
        gf.턴_넘기기(상태)
        assert 황금["도망"] and 상태["전투상태"]["종료"] == "적도망"
        전투.갱신(신규=True)
        yield 0.6
        이름표 = [
            w.text for w in 전투.적상태틀.walk(restrict=True) if hasattr(w, "text")
        ]
        assert any("(도망)" in t for t in 이름표), 이름표
        assert all(경로 is None for _, 경로, _ in 전투._적그림목록)
        글 = next(t for t in 팝업글() if t.startswith("적이 도망쳤다!"))
        assert 글 == "적이 도망쳤다!", 글
        _찍기("battle_enemy_fled")
        확인_누르기()
        yield 0.5
        assert 매니저.current == "던전", 매니저.current
        결과["단계"].append(
            "황금 고블린 도망 -> (도망) 표시, 그림 없음, 적이 도망쳤다! -> 던전"
        )


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
