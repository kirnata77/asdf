"""화면 스모크 테스트 - 실제 Kivy 앱을 띄워 주요 화면 동작을 호출하고 스크린샷을 남긴다.

    pip install kivy                       # 한 번
    xvfb-run -a -s "-screen 0 720x1280x24" python tools/ui_smoke.py [스크린샷폴더]   # 리눅스(화면 없음)
    python tools/ui_smoke.py [스크린샷폴더]                                        # Windows/맥(창이 뜬다)

tests/는 kivy 없이 gameflow 이하만 검사한다. 화면(game/screens) 코드를 바꿨다면 이것을
돌려 확인한다(CLAUDE.md 완료 기준 3). 레벨 10 파티를 만들어 다음을 실제로 호출한다:
상점 구매/판매 목록, 능력치 배분 팝업, 전투 화면 스킬 팝업과 스킬별 실제 타겟(4직업 전 스킬),
적반복지정(썬더콜링) 선택 - 은신 대상 거부 포함. 예외가 나면 종료코드 1.
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
