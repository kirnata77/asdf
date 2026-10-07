"""화면 스모크 테스트 - 실제 Kivy 앱을 띄워 주요 화면 동작을 호출하고 스크린샷을 남긴다.

    pip install kivy                       # 한 번
    xvfb-run -a -s "-screen 0 1080x2340x24" python tools/ui_smoke.py [스크린샷폴더]  # 리눅스(화면 없음)
    python tools/ui_smoke.py [스크린샷폴더]                                        # Windows/맥(창이 뜬다)

tests/는 kivy 없이 gameflow 이하만 검사한다. 화면(game/screens) 코드를 바꿨다면 이것을
돌려 확인한다(CLAUDE.md 완료 기준 3). 레벨 10 파티를 만들어 다음을 실제로 호출한다:
파티 구성 이름칸(6자 제한), 상점 구매/판매 목록, 능력치 배분 팝업, 장비 교체 팝업/상세보기, 파티원 포션 사용, 뒤로 키, 전투 화면 스킬 팝업과 스킬별 실제 타겟(4직업 전 스킬),
적 대상 선택 팝업(일반공격, 취소), 전투 [아이템] 포션(보조행동), 적반복지정(썬더콜링) 선택 - 은신 대상 거부 포함, 행동 선택 팝업(메모라이즈), 도망(구속이면 막힘 팝업, 실패하면 턴 종료),
전투 종료 팝업(승리 전리품/없음, 도망, 패배)과 전투 보상(3칸 선택/빈칸 포기), 자동전투(켜기/중지/끝까지), 몬스터 크기 배율, 적 도망(황금 고블린),
기준 화면 틀(비율이 다른 창에서 검정 여백/터치/팝업 크기).
예외가 나면 종료코드 1.
스크린샷 기본 폴더: ui_smoke_shots/ (.gitignore에 들어 있다).
"""

import json
import os
import random
import shutil
import sys
import tempfile
import traceback
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ.setdefault("KIVY_NO_ARGS", "1")

# 창 크기는 사용자 휴대폰(갤럭시 S24, 세로 1080x2340)에 맞춘다 - 창을 만들기 전에 정해야 한다.
# 화면 밀도도 S24 기본값(450dpi = 2.8125, 가로 384dp)으로 - dp/sp 크기가 폰과 같게 보인다
# (데스크톱 기본 밀도 1이면 글자가 폰보다 훨씬 작게 찍힌다).
os.environ.setdefault("KIVY_METRICS_DENSITY", "2.8125")
from kivy.config import Config  # noqa: E402

Config.set("graphics", "width", "1080")
Config.set("graphics", "height", "2340")
Config.set("graphics", "resizable", "0")

import main  # noqa: E402 - 크래시 로그 훅/폰트 등록 등 앱 초기화를 그대로 쓴다
from kivy.clock import Clock  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.uix.button import Button  # noqa: E402
from kivy.uix.scrollview import ScrollView  # noqa: E402

import gameflow as gf  # noqa: E402
from game.screens import screens_common, screens_party  # noqa: E402
from game.system import dice_utils, save_system, skill_system  # noqa: E402
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


def _스크롤_확인(스크롤, 이름):
    """목록이 화면보다 길고, 손가락으로 끌어 올리면 내려가며, 맨 아래 항목까지 보이는지.
    제너레이터 - 단계 안에서 yield from 으로 부른다."""
    from kivy.tests.common import UnitTestTouch

    내용 = 스크롤.children[0]
    assert 내용.height > 스크롤.height + 10, (이름, 내용.height, 스크롤.height)
    스크롤.scroll_y = 1
    yield 0.2
    x, y = 스크롤.to_window(스크롤.center_x, 스크롤.center_y)
    손 = UnitTestTouch(x, y - 스크롤.height * 0.3)
    손.touch_down()
    for i in range(1, 13):
        손.touch_move(x, y - 스크롤.height * 0.3 + i * 25)
    손.touch_up()
    yield 0.6
    assert 스크롤.scroll_y < 0.99, (이름, "끌어도 안 내려감", 스크롤.scroll_y)
    # 맨 아래로 옮긴다. scroll_y만 바꾸면 스크롤 효과(effect_y)가 들고 있는 위치값은 그대로
    # 남아, 효과가 다음에 갱신될 때 scroll_y를 그 값으로 되돌린다(관성이 남아 있을 때 실패가
    # 실행마다 달랐던 원인). 효과의 위치값을 맨 아래로 옮기면 scroll_y도 따라간다 - kivy는
    # scroll_y = -위치값 / (내용 높이 - 창 높이)라 맨 아래는 위치값 0이다.
    yield 1.5  # 끌고 난 뒤 관성 스크롤이 멈출 때까지
    스크롤.effect_y.velocity = 0  # 남은 관성 버리기(cancel은 남은 속도로 계속 움직인다)
    스크롤.effect_y.cancel()
    스크롤.effect_y.value = 0
    yield 0.8
    assert 스크롤.scroll_y == 0, (이름, "맨 아래로 못 옮김", 스크롤.scroll_y)
    마지막 = 내용.children[0]  # BoxLayout은 마지막에 넣은 위젯이 children[0]
    _, 아래 = 마지막.to_window(*마지막.pos)
    _, 바닥 = 스크롤.to_window(*스크롤.pos)
    assert 바닥 - 4 <= 아래 <= 바닥 + 스크롤.height, (이름, 아래, 바닥)


def _팝업_닫기():
    for 위젯 in list(Window.children)[:-1]:
        if hasattr(위젯, "dismiss"):
            위젯.dismiss()


class 스모크앱(main.DnfMobileApp):
    def _세이브_폴더_준비(self):
        pass  # 이 스모크는 세이브를 임시 폴더로 바꿔서 쓴다(실제 앱 데이터 폴더를 건드리지 않는다)

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
        매니저 = self.매니저

        yield from self._단계_파티생성(상태, 매니저)
        yield from self._단계_상점(상태, 매니저)
        yield from self._단계_파티관리_팝업(상태, 매니저)
        전투 = yield from self._단계_장비_포션_뒤로키_전투팝업(상태, 매니저)
        yield from self._단계_전투종료_자동전투_주점(상태, 매니저, 전투)
        yield from self._단계_맵_타일(상태, 매니저)
        yield from self._단계_목록_스크롤(상태, 매니저)
        yield from self._단계_세이브(상태, 매니저)
        yield from self._단계_설정(매니저)
        yield from self._단계_화면_틀(매니저)

    def _단계_파티생성(self, 상태, 매니저):
        """파티 구성 화면 - 이름칸(안내/글자 수 제한)과 이름 중복"""
        매니저.current = "파티생성"
        # 처음엔 네 칸 모두 참여, 직업은 귀검사/격투가/거너/마법사
        슬롯들 = 매니저.get_screen("파티생성").슬롯목록
        assert [s["직업스피너"].text for s in 슬롯들] == [
            "귀검사",
            "격투가",
            "거너",
            "마법사",
        ]
        assert all(s["참여토글"].state == "down" for s in 슬롯들[1:])
        assert all(not s["이름입력"].disabled for s in 슬롯들)
        이름칸 = 슬롯들[0]["이름입력"]
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
        결과["단계"].append(
            "파티 구성 기본값(4명 참여, 귀검사/격투가/거너/마법사) + 이름칸(안내 문구, 한글 6자/영문 12자 제한)"
        )

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

    def _단계_상점(self, 상태, 매니저):
        """상점 - 구매/판매 목록과 해체(일괄해체 확인 팝업)"""
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

        # 해체: 메인에 [해체], 장비 목록에서 해체하면 소울/큐브 조각이 재료로
        상점._메인_그리기()
        assert any(
            getattr(w, "text", "") == "해체" for w in 상점.내용틀.walk(restrict=True)
        ), "상점에 해체 버튼 없음"
        상태["소지품"]["장비"]["찢어진 천갑 상의"] = (
            상태["소지품"]["장비"].get("찢어진 천갑 상의", 0) + 1
        )
        상점._탭목록_그리기("해체", "장비")
        탭 = next(
            w
            for w in 상점.내용틀.walk(restrict=True)
            if isinstance(w, Button) and w.text == "상의"
        )
        탭.dispatch("on_release")
        yield 0.3
        _찍기("shop_dismantle")
        해체버튼 = next(
            w
            for w in 상점.내용틀.walk(restrict=True)
            if isinstance(w, Button) and w.text == "해체"
        )
        소울전 = 상태["소지품"]["재료"].get("커먼 소울", 0)
        해체버튼.dispatch("on_release")
        yield 0.3
        assert "해체" in 상점.안내라벨.text and "커먼 소울" in 상점.안내라벨.text, (
            상점.안내라벨.text
        )
        assert 상태["소지품"]["재료"]["커먼 소울"] == 소울전 + 1
        _찍기("shop_dismantle_after")

        # [전체] 탭이 맨 앞, 일괄해체 기본 범위는 커먼 / 전체
        탭글 = [
            w.text
            for w in 상점.내용틀.walk(restrict=True)
            if isinstance(w, Button) and w.text in gf.상점_해체_탭목록
        ]
        assert 탭글[0] == "전체", 탭글
        assert (상점.일괄등급.text, 상점.일괄부위.text) == ("커먼", "전체")
        for 이름 in ("찢어진 천갑 하의", "조잡한 반지"):
            상태["소지품"]["장비"][이름] = 상태["소지품"]["장비"].get(이름, 0) + 1
        일괄 = next(
            w
            for w in 상점.내용틀.walk(restrict=True)
            if isinstance(w, Button) and w.text == "일괄해체"
        )
        일괄.dispatch("on_release")
        yield 0.5
        팝업 = list(Window.children)[0]
        assert 팝업.title == "일괄해체", 팝업
        _찍기("shop_dismantle_batch_confirm")
        next(
            w
            for w in 팝업.walk(restrict=True)
            if isinstance(w, Button) and w.text == "해체"
        ).dispatch("on_release")
        yield 0.3
        assert "해체:" in 상점.안내라벨.text and "커먼 소울" in 상점.안내라벨.text, (
            상점.안내라벨.text
        )
        assert not gf.상점_일괄해체_대상(상태, "커먼", "전체")
        _찍기("shop_dismantle_batch_after")
        결과["단계"].append(
            "상점 해체(장비 -> 소울 + 큐브 조각, [전체] 탭, 일괄해체 커먼/전체 확인 팝업)"
        )

    def _단계_파티관리_팝업(self, 상태, 매니저):
        """파티관리 - 능력치 배분, 스킬강화, 스킬습득 팝업"""
        매니저.current = "파티관리"
        매니저.get_screen("파티관리")._능력치배분_팝업(
            상태["파티"]["파티원"][0], 2, lambda 배분: None
        )
        yield 0.5
        _찍기("stat_popup")
        _팝업_닫기()
        결과["단계"].append("능력치 배분 팝업")

        # 레벨 12 [스킬강화] 팝업: 보유 스킬마다 버튼, 누르면 그 스킬로 확정
        고른 = []
        강화항목 = gf.전직_레지스트리["귀검사"]["웨펀마스터"]["레벨업테이블"][12]
        매니저.get_screen("파티관리")._스킬강화_팝업(
            상태["파티"]["파티원"][0], 강화항목, 고른.append
        )
        yield 0.5
        _찍기("skill_enhance_popup")
        팝업 = list(Window.children)[0]
        버튼들 = [
            w
            for w in 팝업.walk(restrict=True)
            if isinstance(w, Button) and w.text.startswith("귀참")
        ]
        assert len(버튼들) == 1, [getattr(w, "text", "") for w in 팝업.walk()]
        버튼들[0].dispatch("on_release")
        yield 0.6  # 팝업 닫힘 애니메이션이 끝날 때까지(0.3이면 가끔 아직 창에 남아 있었다)
        assert 고른 == ["귀참"] and len(Window.children) == 1, 고른
        결과["단계"].append("스킬강화 팝업(보유 스킬 버튼 -> 그 스킬로 확정)")

        # [스킬습득] 팝업: 직업 계열 스킬 목록 + 비용, 골드가 모자라면 버튼 잠금, 누르면 배운다
        파티관리 = 매니저.get_screen("파티관리")
        파티관리.갱신()
        assert any(
            getattr(w, "text", "") == "스킬습득" for w in 파티관리.walk(restrict=True)
        ), "스킬습득 버튼 없음"
        yield 0.3
        # 카드 오른쪽 버튼 셋은 위에서 아래로 쌓이고, 능력치 칸은 "이름 값"이 한 줄에 다 들어간다
        from kivy.core.text.markup import MarkupLabel

        버튼y = {
            w.text: w.y
            for w in 파티관리.walk(restrict=True)
            if getattr(w, "text", "") in ("레벨업", "스킬습득", "상세보기")
        }
        assert 버튼y["레벨업"] > 버튼y["스킬습득"] > 버튼y["상세보기"], 버튼y
        능력치칸 = [
            w
            for w in 파티관리.walk(restrict=True)
            if isinstance(w, main.Label) and "[color=9ea6b3]" in w.text
        ]
        assert len(능력치칸) == 6 * len(상태["파티"]["파티원"]), len(능력치칸)
        for 칸 in 능력치칸:
            글 = MarkupLabel(text=칸.text, font_size=칸.font_size, markup=True)
            글.refresh()
            assert 글.texture.width <= 칸.width, (칸.text, 글.texture.width, 칸.width)
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

    def _단계_장비_포션_뒤로키_전투팝업(self, 상태, 매니저):
        """장비 교체/파티원 포션/뒤로 키, 전투 화면 팝업(스킬/대상/포션/행동 선택/도망)"""
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

        # 파티원 화면 [포션 사용]: 목록(가득 찬 MP 포션은 사유와 함께 비활성) -> 마시면 HP가 오른다
        상태["소지품"]["포션"] = {"초보자용 HP 포션": 2, "초보자용 MP 포션": 1}
        귀검사["현재HP"] = 1
        파티원 = 매니저.get_screen("파티원")
        파티원.캐릭터 = 귀검사
        파티원.갱신()
        파티원._포션_팝업(상태, 귀검사)
        yield 0.5
        버튼 = [
            w for w in Window.children[0].walk(restrict=True) if isinstance(w, Button)
        ]
        hp버튼 = next(b for b in 버튼 if b.text.startswith("초보자용 HP 포션 x2"))
        mp버튼 = next(b for b in 버튼 if b.text.startswith("초보자용 MP 포션"))
        assert mp버튼.disabled and "가득" in mp버튼.text, mp버튼.text
        hp버튼.trigger_action(duration=0)
        yield 0.5
        assert 귀검사["현재HP"] > 1, 귀검사["현재HP"]
        assert 상태["소지품"]["포션"]["초보자용 HP 포션"] == 1
        _찍기("party_potion_popup")
        _팝업_닫기()
        gf.파티_최대치로_회복(상태)
        결과["단계"].append(
            "파티원 포션 사용 팝업(가득 차면 비활성, 마시면 회복/개수 감소)"
        )
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

        gf.전투_시작(상태, ["타우 아미", "고블린", "고블린"], 레벨=6, 차수=2)
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
            flow.턴_시작_처리(전투상태, p)
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
        # 버튼마다 "이름\nHP 현재/최대", 상단 적 칸에도 같은 HP 줄
        assert 글들[:-1] == [f"{p['이름']}\n{gf.적_HP표시(상태, p)}" for p in 적], 글들
        assert all("/" in g.split("\n")[1] for g in 글들[:-1]), 글들
        적칸글 = [
            w.text
            for w in 전투.적상태틀.walk(restrict=True)
            if isinstance(w, main.Label)
        ]
        assert all(any(gf.적_HP표시(상태, p) in t for t in 적칸글) for p in 적), 적칸글
        # 팝업 폭은 기준 화면의 0.7(전에는 0.35) - 긴 이름이 버튼 안에 들어간다
        assert abs(Window.children[0].width - 0.7 * Window.width) < 2
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

        # [아이템]: 회복포션 팝업 -> 보조행동 1개로 자신만 회복, 로그에 남는다
        p = 차례("귀검사")
        p["현재HP"] = 1
        보조 = p["행동자원"]["보조행동"]
        전투._아이템_클릭()
        yield 0.3
        포션버튼 = [b for b in 대상버튼들() if b.text.startswith("초보자용 HP 포션")]
        assert 포션버튼 and not 포션버튼[0].disabled, [b.text for b in 대상버튼들()]
        _찍기("battle_potion_popup")
        포션버튼[0].trigger_action(duration=0)
        yield 0.5
        assert p["현재HP"] > 1 and p["행동자원"]["보조행동"] == 보조 - 1
        assert "초보자용 HP 포션 사용" in 전투상태["로그"][-1].get("행동", "")
        결과["단계"].append("전투 [아이템] 포션 팝업(보조행동 1, 자신 회복, 로그)")

        차례("마법사")
        yield 0.3
        전투._스킬_클릭("썬더콜링", 상태["스킬데이터모음"]["썬더콜링"])
        assert 전투.선택모드[0] == "반복지정", 전투.선택모드
        적 = [x for x in 전투상태["참가자"] if x["진영"] == "적" and x["생존"]]
        skill_system.상태이상_부여(전투상태, 적[1], "은신", 3, None)
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

        # 메모라이즈: 하급마법을 일반행동/보조행동 중 골라 쓴다 - 행동 선택 팝업
        p = 차례("마법사")
        하급 = next(
            n
            for n, d in 상태["스킬데이터모음"].items()
            if "하급마법" in d.get("타입", []) and d.get("타겟") == "적단일"
        )
        if 하급 not in p["원본"]["보유스킬"]:
            p["원본"]["보유스킬"].append(하급)
        p["행동자원"].update(일반행동=1, 보조행동=1)
        p["현재MP"] = 999
        전투._스킬_클릭(하급, 상태["스킬데이터모음"][하급])
        yield 0.3
        글들 = [b.text for b in 대상버튼들()]
        assert 글들 == ["일반행동 (남은 1)", "보조행동 (남은 1)", "취소"], 글들
        _찍기("battle_action_choice_popup")
        대상버튼들()[1].trigger_action(duration=0)  # 보조행동
        yield 0.3
        대상버튼들()[0].trigger_action(duration=0)  # 첫 번째 적
        yield 0.5
        assert 팝업수() == 0, 팝업수()
        assert (p["행동자원"]["일반행동"], p["행동자원"]["보조행동"]) == (1, 0)
        # 수단이 하나뿐이면 팝업 없이 바로 대상 선택으로 간다
        전투._스킬_클릭(하급, 상태["스킬데이터모음"][하급])
        yield 0.3
        assert 전투.선택모드 == ("스킬", 하급), 전투.선택모드
        _팝업_닫기()
        전투._대상선택_취소()
        결과["단계"].append(
            "행동 선택 팝업(메모라이즈 하급마법 - 일반행동/보조행동, 하나면 생략)"
        )

        # 도망: 파티 중 한 명이라도 구속이면 [도망]이 판정 없이 막힘 팝업을 띄운다
        현재 = 차례("귀검사")
        거너 = next(
            x for x in 전투상태["참가자"] if (x.get("원본") or {}).get("직업") == "거너"
        )
        skill_system.상태이상_부여(전투상태, 거너, "구속", 3, None)
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
        return 전투  # 다음 단계(전투 종료/자동전투)가 이어서 쓴다

    def _단계_전투종료_자동전투_주점(self, 상태, 매니저, 전투):
        """전투 종료/보상, 자동전투, 몬스터 크기, 황금 고블린 도망, 주점"""
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
        gf.던전_진입(상태, "dungeon_01A_D01_Lorien")
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
            원래맵 = 상태["던전상태"]["맵정보"]
            if 전리품줄 is False:
                # "전리품 없음": 던전 공용 드랍도, 골드도 없는 전투로 만든다
                상태["던전상태"]["맵정보"] = {**원래맵, "드랍표": []}
            gf.전투_시작(상태, 몬스터들, 레벨=6, 차수=2)  # 시작 반응에 안 쓰러지게
            if 전리품줄 is False:
                for 적 in gf.적_목록(상태):
                    적["원본"]["획득골드"] = "미정"
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
            if 상태.get("던전상태"):
                상태["던전상태"]["맵정보"] = 원래맵
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
                    # 받은 아이템이 전투 종료 팝업의 전리품 줄에 더해진다
                    새글 = next(t for t in 팝업글() if t.startswith("전투 승리!"))
                    assert 새글 == "\n".join(
                        gf.전투_종료_문구(상태, "아군승리")
                    ) and any(줄.startswith(칸[1]) for 줄 in 새글.split("\n")[2:]), 새글
                    _찍기("battle_end_win_reward")
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
                gf.던전_진입(상태, "dungeon_01A_D01_Lorien")
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
            flow.턴_시작_처리(상태["전투상태"], p)

        gf.전투_시작(상태, ["타우 아미", "타우 아미"], 레벨=6, 차수=2)
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

        # 몬스터 크기: 소형 1/2 / 중형 3/4 / 대형 1배(칸 전체), 칸 바닥(발바닥) 맞춤, 대형이 뒤(먼저 그림)
        from kivy.graphics import Rectangle

        gf.전투_시작(상태, ["고블린", "타우 비스트", "타우 아미"], 레벨=6, 차수=2)
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
        # 아군 그림: 칸에 꽉 맞춘 크기의 2/3, 칸 바닥 가운데
        from kivy.uix.image import Image as 그림

        아군그림 = [
            w for w in 전투.아군그래픽행.walk(restrict=True) if isinstance(w, 그림)
        ]
        assert 아군그림, "아군 그림 없음"
        for 이미지 in 아군그림:
            틀 = 이미지.parent
            tw, th = 이미지.texture_size
            맞춤 = min(틀.width / tw, 틀.height / th) * 2 / 3
            assert abs(이미지.height - th * 맞춤) < 1, (이미지.size, 틀.size)
            assert abs(이미지.y - 틀.y) < 1 and abs(이미지.center_x - 틀.center_x) < 1
        _찍기("battle_monster_size")
        결과["단계"].append(
            "몬스터 크기 배율(소 1/2, 중 3/4, 대 1) + 발바닥 맞춤 + 대형이 뒤, 아군 그림 2/3 바닥 맞춤"
        )

        # 황금 고블린(도망턴 5): 자기 턴이 5번 끝나면 도망 -> 이름표 "(도망)", 그림 없음,
        # 적이 모두 도망쳤으면 "적이 도망쳤다!" 팝업 -> [확인] -> 던전
        _팝업_닫기()
        gf.전투_시작(상태, ["황금 고블린"], 레벨=3, 차수=1)
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
        _팝업_닫기()
        yield 0.3
        _찍기(
            "dungeon_map"
        )  # 던전 지도(바닥/나무·게이트/플레이어) - 그리기 변경 전후 비교용
        결과["단계"].append(
            "황금 고블린 도망 -> (도망) 표시, 그림 없음, 적이 도망쳤다! -> 던전"
        )

        # 주점: 영입(파티가 꽉 차 있으면 숙소로) -> 대기 -> 합류 -> 추방(확인 팝업)
        _팝업_닫기()
        매니저.current = "마을"
        yield 0.3
        assert any(
            getattr(w, "text", "") == "주점"
            for w in 매니저.get_screen("마을").walk(restrict=True)
        ), "마을에 주점 버튼 없음"
        매니저.current = "주점"
        주점 = 매니저.get_screen("주점")
        상태 = self.게임상태
        상태["소지품"]["골드"] = 1000
        주점.갱신()
        yield 0.3
        _찍기("tavern")

        def 팝업버튼(글):
            팝업 = list(Window.children)[0]
            return next(
                w
                for w in 팝업.walk(restrict=True)
                if isinstance(w, Button) and w.text.startswith(글)
            )

        주점._영입_팝업()
        yield 0.5
        _찍기("tavern_recruit")
        이름칸 = next(
            w
            for w in list(Window.children)[0].walk(restrict=True)
            if w.__class__.__name__ == "TextInput"
        )
        이름칸.text = "새동료"
        팝업버튼("영입").dispatch("on_release")
        yield 0.3
        숙소 = gf.숙소_목록(상태)
        assert [c["캐릭터명"] for c in 숙소] == ["새동료"], 주점.안내라벨.text
        assert 상태["소지품"]["골드"] == 1000 - gf.영입_비용

        파티 = 상태["파티"]["파티원"]
        첫째 = 파티[0]
        주점._대기_팝업()
        yield 0.3
        팝업버튼(첫째["캐릭터명"]).dispatch("on_release")
        yield 0.3
        assert 첫째 in 숙소 and 첫째 not in 파티 and len(Window.children) == 1

        주점._합류_팝업()
        yield 0.3
        _찍기("tavern_join")
        팝업버튼(첫째["캐릭터명"]).dispatch("on_release")
        yield 0.3
        assert 첫째 in 파티 and 첫째 not in 숙소

        새동료 = 숙소[0]
        주점._추방_팝업()
        yield 0.3
        팝업버튼("새동료").dispatch("on_release")
        yield 0.3
        assert list(Window.children)[0].title == "파티원 추방"
        _찍기("tavern_expel_confirm")
        팝업버튼("추방").dispatch("on_release")
        yield 0.3
        assert 새동료 not in 숙소 and len(Window.children) == 1
        assert "추방했습니다" in 주점.안내라벨.text, 주점.안내라벨.text
        _찍기("tavern_after")
        결과["단계"].append("주점(영입 -> 숙소, 대기, 합류, 추방 확인 팝업)")

    def _단계_맵_타일(self, 상태, 매니저):
        """하늘성 탑(아몬 상층)이 맵정보 "타일"의 그림(발판/벽/하늘, 포탈은 벽 위 하늘성
        게이트)으로, 로리엔 보스의 세리아 감옥이 2x2칸 크기로 그려지는지"""
        from kivy.graphics import Rectangle

        def 그린_사각형(지도):
            return [c for c in 지도.canvas.children if isinstance(c, Rectangle)]

        _팝업_닫기()
        gf.던전_진입(상태, "dungeon_02A_D12_amon_upper")
        상태["던전상태"]["위치"] = (
            4,
            16,
        )  # 왼쪽 아래 - 발판/벽/하늘/마을 포탈이 보인다
        매니저.current = "던전"
        던전 = 매니저.get_screen("던전")
        던전.갱신()
        yield 0.5
        지도 = 던전.지도위젯
        그린것 = {id(c.texture) for c in 그린_사각형(지도) if c.texture is not None}
        for 기호 in ("O", "X", "Y", "#"):
            텍스처들 = 지도._맵_타일(기호)
            assert 텍스처들, (기호, "타일 그림을 못 읽음")
            for 텍스처 in 텍스처들:
                assert id(텍스처) in 그린것, (기호, "맵 타일이 그려지지 않음")
        assert len(지도._맵_타일("#")) == 2  # 벽 위에 게이트
        # 칸은 정사각형, 짧은 쪽(세로)에 9칸, 가로로 긴 위젯이면 가로 칸이 더 많다
        칸폭, 칸높이 = 지도._칸_크기()
        assert abs(칸폭 - 칸높이) < 0.01, (칸폭, 칸높이)
        assert 지도._행수 == 9 and 지도._열수 >= 지도._행수, (지도._열수, 지도._행수)
        assert 지도._열수 * 칸폭 >= 지도.width, "가로 끝까지 칸을 그리지 않음"
        assert 지도._타일("풀밭") is None or id(지도._타일("풀밭")) not in 그린것
        _찍기("dungeon_map_tiles")

        # 로리엔 보스(15,3) - 세리아 감옥은 한 칸이지만 2x2칸 크기로, 바닥 위/플레이어 아래
        gf.던전_진입(상태, "dungeon_01A_D01_Lorien")
        상태["던전상태"]["위치"] = (14, 3)
        던전.갱신()
        yield 0.5
        칸폭, 칸높이 = 지도._칸_크기()
        사각형들 = 그린_사각형(지도)
        감옥 = [
            i
            for i, c in enumerate(사각형들)
            if abs(c.size[0] - 칸폭 * 2) < 1 and abs(c.size[1] - 칸높이 * 2) < 1
        ]
        assert 감옥, "감옥이 2x2칸 크기로 그려지지 않음"
        칸들 = [
            i
            for i, c in enumerate(사각형들)
            if abs(c.size[0] - 칸폭) < 1 and abs(c.size[1] - 칸높이) < 1
        ]
        assert max(칸들) < 감옥[0], "감옥이 바닥보다 먼저 그려짐"
        assert 지도.canvas.children[-1] is not 사각형들[감옥[0]]  # 플레이어가 맨 위
        _찍기("dungeon_prison_2x2")
        gf.던전_진입(상태, "dungeon_02A_D11_amon_lower")
        상태["던전상태"]["위치"] = (19, 3)  # 아몬 하층 보스(19,1) 아래 - 로리안 감옥
        던전.갱신()
        yield 0.5
        로리안 = 지도._오브젝트_타일(19, 1)
        assert 로리안 is not None, "로리안 감옥 그림을 못 읽음"
        assert any(
            c.texture is not None
            and c.texture.size != (0, 0)
            and abs(c.size[0] - 칸폭 * 2) < 1
            for c in 그린_사각형(지도)
        ), "로리안 감옥이 2x2칸으로 그려지지 않음"
        _찍기("dungeon_prison_lorien")
        # 포탈로 이어진 맵을 함께 그린다 - 아몬 하층 천장 포탈(19,0) 위로 상층이
        # 이어진다(상층 (19,18) 발판이 하층 좌표 (19,-1)), 이웃 맵의 "@"는 감춘다
        assert 지도._칸_문자(19, -1) == "O", 지도._칸_문자(19, -1)
        assert 지도._칸_문자(3, -1) == "O"  # 상층 마을 포탈 앞 보스 -> 발판으로
        assert 지도._칸_문자(19, 0) == "#"  # 겹친 포탈 칸은 지금 맵
        gf.던전_진입(상태, "dungeon_01A_D01_Lorien")
        상태["던전상태"]["위치"] = (14, 3)  # 보스(감옥) 왼쪽 - 오른쪽에 로리엔 안쪽
        던전.갱신()
        yield 0.5
        assert 지도._칸_문자(17, 3) == "O", "로리엔 오른쪽에 로리엔 안쪽이 안 이어짐"
        _찍기("dungeon_neighbor_maps")
        상태["던전상태"] = None
        매니저.current = "마을"
        yield 0.3
        결과["단계"].append(
            "맵 타일(하늘성 발판/벽/노을 하늘/게이트 겹침), 정사각형 칸, 감옥 2x2칸(바닥 위, 플레이어 아래), 이어진 맵 함께 보이기"
        )

    def _단계_목록_스크롤(self, 상태, 매니저):
        """상점/장비 교체 목록 스크롤(끌어서 내림)"""
        # 목록 스크롤: 상점 구매/판매/해체[전체], 장비 교체 팝업(소지품) - 항목이 많을 때
        카탈로그 = 상태["상점카탈로그"]["장비"]
        for 이름 in 카탈로그["무기"]:
            if 카탈로그["무기"][이름].get("레어도") != "치트":
                상태["소지품"]["장비"][이름] = 상태["소지품"]["장비"].get(이름, 0) + 1
        for 탭 in ("상의", "하의", "어깨", "벨트", "신발"):
            for 이름 in 카탈로그[탭]:
                상태["소지품"]["장비"][이름] = 상태["소지품"]["장비"].get(이름, 0) + 1
        매니저.current = "상점"
        상점 = 매니저.get_screen("상점")

        def 목록스크롤():
            return next(
                w
                for w in 상점.내용틀.walk(restrict=True)
                if isinstance(w, ScrollView) and w.do_scroll_y
            )

        # S24 세로 화면(1080x2340)에서는 마을 판매 목록이 한 화면에 다 들어간다 -
        # 스크롤을 보려고 이 단계에서만 카탈로그 장비(치트 제외)를 판매 목록에 잠시 더한다.
        판매목록 = gf.현재_마을정보(상태)["상점판매목록"]
        원래_판매목록 = list(판매목록)
        판매목록.extend(
            이름
            for 탭 in 카탈로그.values()
            for 이름, 데이터 in 탭.items()
            if 데이터.get("레어도") != "치트" and 이름 not in 원래_판매목록
        )
        try:
            for 모드, 이름 in (
                ("구매", "shop_scroll_buy"),
                ("판매", "shop_scroll_sell"),
                ("해체", "shop_scroll_dismantle"),
            ):
                상점._탭목록_그리기(모드, "장비")
                yield 0.4
                yield from _스크롤_확인(목록스크롤(), f"상점 {모드}")
                _찍기(이름)
        finally:
            판매목록[:] = 원래_판매목록
        매니저.current = "파티원"
        screens_party._장비교체_팝업(상태["파티"]["파티원"][0], "무기", lambda: None)
        yield 0.5
        팝업스크롤 = next(
            w
            for w in list(Window.children)[0].walk(restrict=True)
            if isinstance(w, ScrollView)
        )
        yield from _스크롤_확인(팝업스크롤, "장비 교체 팝업")
        _찍기("equip_swap_scroll")
        _팝업_닫기()
        결과["단계"].append(
            "목록 스크롤(상점 구매/판매/해체, 장비 교체 팝업 - 끌어서 내림, 맨 아래 보임)"
        )

    def _단계_세이브(self, 상태, 매니저):
        """세이브 슬롯(새버전/손상/복구본)과 앱 시작 때 세이브 폴더 이전"""
        # 세이브 슬롯: 슬롯 하나가 망가져도 메인 메뉴/슬롯 목록이 열린다(구조 점검 W-1).
        # 실제 game/saves/ 대신 임시 폴더를 쓴다.
        세이브폴더 = tempfile.mkdtemp(prefix="ui_smoke_saves_")
        원래폴더 = save_system._세이브_폴더
        save_system._세이브_폴더 = lambda: 세이브폴더
        try:
            self.게임상태 = 상태
            gf.게임_저장(상태, 1)
            경로1 = os.path.join(세이브폴더, "slot_1.json")
            with open(경로1, encoding="utf-8") as f:
                저장1 = json.load(f)
            저장1["버전"] = save_system.세이브_버전 + 1  # 더 새로운 앱이 저장한 세이브
            with open(경로1, "w", encoding="utf-8") as f:
                json.dump(저장1, f, ensure_ascii=False)
            gf.게임_저장(상태, 3)
            gf.게임_저장(상태, 3)  # 두 번째 저장이 .bak을 만든다
            with open(
                os.path.join(세이브폴더, "slot_2.json"), "w", encoding="utf-8"
            ) as f:
                f.write('{"플레이어": {"파')  # 쓰다 끊긴 파일, 백업 없음 -> 손상
            with open(
                os.path.join(세이브폴더, "slot_3.json"), "w", encoding="utf-8"
            ) as f:
                f.write('{"플레이어": {"파')  # 본 파일만 끊김, .bak이 있음 -> 복구본
            매니저.current = "메인메뉴"
            yield 0.3
            assert not 매니저.get_screen("메인메뉴").불러오기버튼.disabled
            매니저.current = "불러오기목록"
            yield 0.4
            _찍기("save_slots_corrupt")
            불러오기 = 매니저.get_screen("불러오기목록")
            줄들 = list(reversed(불러오기.목록틀.children))  # 위에서 아래(슬롯 1, 2, 3)

            def 줄_글(줄):
                return next(
                    w.text for w in 줄.children if w.__class__.__name__ == "Label"
                )

            def 줄_버튼(줄):
                return next(w for w in 줄.children if isinstance(w, Button))

            assert "(손상됨" in 줄_글(줄들[1]), 줄_글(줄들[1])
            assert "[백업]" in 줄_글(줄들[2]), 줄_글(줄들[2])
            assert "더 새로운 버전" in 줄_글(줄들[0]), 줄_글(줄들[0])
            assert 줄_버튼(줄들[0]).disabled and not 줄_버튼(줄들[2]).disabled
            assert 줄_버튼(줄들[1]).disabled, "손상 슬롯은 불러올 수 없다"

            불러오기._선택(2)  # 막혀 있어도 호출되면 앱이 죽지 않고 안내만 한다
            assert 매니저.current == "불러오기목록" and "손상" in 불러오기.안내라벨.text
            불러오기._선택(3)  # 백업으로 불러온다
            assert 매니저.current == "마을"

            self.게임상태 = 상태
            매니저.current = "저장목록"
            yield 0.3
            매니저.get_screen("저장목록")._선택(2)  # 손상 슬롯 덮어쓰기
            yield 0.2
            assert save_system.세이브_요약(2).get("손상") is None
            assert "저장했습니다" in 매니저.get_screen("저장목록").안내라벨.text
            결과["단계"].append(
                "세이브 슬롯(새버전/손상/복구본 표시, 메인 메뉴 정상, 손상 슬롯 덮어쓰기)"
            )

            # 앱 시작 때 세이브 폴더를 앱 데이터 폴더로 옮기고 옛 세이브를 한 번 가져온다(임시 폴더만 씀)
            앱데이터 = tempfile.mkdtemp(prefix="ui_smoke_appdata_")
            옛위치 = tempfile.mkdtemp(prefix="ui_smoke_legacy_")
            with open(os.path.join(옛위치, "slot_2.json"), "w", encoding="utf-8") as f:
                f.write("{}")

            # App을 하나 더 만들면 App.get_running_app()이 바뀌므로 자리표시 객체로 부른다
            임시앱 = types.SimpleNamespace(user_data_dir=앱데이터)

            save_system._세이브_폴더 = 원래폴더  # 임시 폴더 바꿔치기를 잠깐 푼다
            기본폴더 = save_system._기본_세이브_폴더
            save_system._기본_세이브_폴더 = lambda: 옛위치
            try:
                main.DnfMobileApp._세이브_폴더_준비(임시앱)
                assert save_system._세이브_폴더() == os.path.join(앱데이터, "saves")
                assert os.path.isfile(os.path.join(앱데이터, "saves", "slot_2.json"))
                assert os.path.isfile(os.path.join(옛위치, "slot_2.json")), (
                    "옛 파일은 남는다"
                )
            finally:
                save_system._기본_세이브_폴더 = 기본폴더
                save_system._폴더_재정의 = None
                save_system._세이브_폴더 = lambda: 세이브폴더
                shutil.rmtree(앱데이터, ignore_errors=True)
                shutil.rmtree(옛위치, ignore_errors=True)
            결과["단계"].append(
                "앱 시작 시 세이브 폴더를 앱 데이터 폴더로(옛 세이브 한 번 복사)"
            )
        finally:
            save_system._세이브_폴더 = 원래폴더
            shutil.rmtree(세이브폴더, ignore_errors=True)
            매니저.current = "마을"

    def _단계_설정(self, 매니저):
        """설정 파일이 없거나 깨졌거나 쓸 수 없어도 옵션 화면/설정 저장이 죽지 않는다"""
        폴더 = tempfile.mkdtemp(prefix="ui_smoke_settings_")
        경로 = os.path.join(폴더, "설정.json")
        원래경로 = screens_common._설정_경로
        원래반응 = gf.반응_자동_여부()
        screens_common._설정_경로 = lambda: 경로
        try:
            assert screens_common.설정_불러오기() == {}  # 파일 없음
            for 내용 in (
                '{"반응자',
                "[1, 2]",
                "\udcff",
            ):  # 끊긴 JSON, 딕셔너리 아님, 깨진 글자
                with open(경로, "w", encoding="utf-8", errors="surrogateescape") as f:
                    f.write(내용)
                assert screens_common.설정_불러오기() == {}, 내용
            screens_common.설정_저장(
                "반응자동", True
            )  # 깨진 파일을 새 설정으로 덮어쓴다
            with open(경로, encoding="utf-8") as f:
                assert json.load(f) == {"반응자동": True}
            assert screens_common.설정_불러오기() == {"반응자동": True}
            assert gf.반응_자동_여부()
            screens_common._설정_경로 = lambda: (
                폴더
            )  # 폴더라 쓸 수 없다 -> 조용히 넘어간다
            screens_common.설정_저장("반응자동", False)
            screens_common._설정_경로 = lambda: 경로
            매니저.current = "옵션"
            yield 0.3
            _찍기("settings")
            결과["단계"].append(
                "설정 파일(없음/깨짐/딕셔너리 아님/쓰기 실패) - 기본값으로 계속"
            )
        finally:
            screens_common._설정_경로 = 원래경로
            gf.반응_자동_설정(원래반응)
            shutil.rmtree(폴더, ignore_errors=True)
            매니저.current = "마을"

    def _단계_화면_틀(self, 매니저):
        """기준 화면 틀 - 비율이 다른 창에서 검정 여백, 터치 위치, 팝업 크기"""
        from kivy.tests.common import UnitTestTouch
        from kivy.uix.popup import Popup

        틀 = self.root
        원래크기 = tuple(Window.size)
        assert 틀.배율 == 1 and tuple(틀.틀.pos) == (0, 0), (틀.배율, 틀.틀.pos)
        try:
            # 기준보다 길쭉한 창(위아래 여백)과 넓적한 창(좌우 여백)
            for 이름, 크기 in (("tall", (900, 2340)), ("wide", (1080, 1440))):
                Window.size = 크기
                yield 0.5
                assert tuple(Window.size) == 크기, (이름, Window.size)
                배율 = screens_common.기준화면_배율(*크기)
                assert abs(틀.배율 - 배율) < 1e-6, (이름, 틀.배율, 배율)
                보이는폭 = screens_common.기준화면_폭 * 배율
                보이는높이 = screens_common.기준화면_높이 * 배율
                x, y = 틀.틀.pos
                assert abs(x - (크기[0] - 보이는폭) / 2) < 1, (이름, 틀.틀.pos)
                assert abs(y - (크기[1] - 보이는높이) / 2) < 1, (이름, 틀.틀.pos)

                # 줄어든 화면에서 손가락으로 누른 곳이 그 버튼에 닿는다
                매니저.current = "옵션"
                yield 0.3
                _찍기("frame_" + 이름)
                뒤로 = next(
                    w
                    for w in 매니저.current_screen.walk(restrict=True)
                    if isinstance(w, Button) and w.text == "뒤로"
                )
                손 = UnitTestTouch(*뒤로.to_window(*뒤로.center))
                손.touch_down()
                손.touch_up()
                yield 0.3
                assert 매니저.current == "메인메뉴", (이름, 매니저.current)

                # 팝업은 가운데에, 크기 비율은 기준 화면에 대해
                팝업 = Popup(title="틀 점검", size_hint=(0.9, 0.5))
                팝업.open(animation=False)
                yield 0.3
                assert abs(팝업.width - 0.9 * 보이는폭) < 1, (이름, 팝업.size)
                assert abs(팝업.height - 0.5 * 보이는높이) < 1, (이름, 팝업.size)
                assert abs(팝업.center_x - Window.width / 2) < 1, (이름, 팝업.center)
                assert abs(팝업.center_y - Window.height / 2) < 1, (이름, 팝업.center)
                _찍기("frame_" + 이름 + "_popup")
                팝업.dismiss(animation=False)
                yield 0.3
            결과["단계"].append(
                "기준 화면 틀(1080x2340) - 길쭉/넓적한 창에서 검정 여백, 가운데 배치, 터치, 팝업 크기"
            )
        finally:
            Window.size = 원래크기
        yield 0.5
        assert abs(틀.배율 - 1) < 1e-6, 틀.배율
        매니저.current = "마을"


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
