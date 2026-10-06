# tests/test_scenario_s6.py

- _패배 · class · L37-L38 — class _패배(Exception)
- _캠페인 · class · L41-L114 — class _캠페인
- __init__ · method · L42-L48 — def __init__(self, 시드)
- _전투 · method · L51-L60 — def _전투(self, 상태)
- 보스 · method · L62-L64 — def 보스(self)
- 나가기 · method · L66-L67 — def 나가기(self, 연결맵)
- 진입 · method · L69-L70 — def 진입(self, 번호)
- 원정 · method · L72-L85 — def 원정(self, 이름, 진행)
- 키우기 · method · L88-L114 — def 키우기(self)
- 캠페인 · function · L117-L193 — def 캠페인(시드)
- 로리엔 · function · L123-L128 — def 로리엔()
- 머크우드 · function · L135-L140 — def 머크우드()
- 선더랜드 · function · L146-L153 — def 선더랜드()
- 프로스트 · function · L159-L165 — def 프로스트(): # 머크우드 숏컷(포이즌 선더랜드 보스 필요)이 열렸다
- 그락카락 · function · L169-L175 — def 그락카락()
- 어둠의_선더랜드 · function · L181-L186 — def 어둠의_선더랜드(): # 선더랜드 북쪽 숏컷(불타는 그락카락 보스 필요)이 열렸다
- test_S6_캠페인_실전 · function · L198-L202 — def test_S6_캠페인_실전(시드, golden)
