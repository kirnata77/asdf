# tests/test_gameflow.py

- test_직업_레지스트리 · function · L18-L19 — def test_직업_레지스트리()
- test_직업은_데이터파일표_한_줄로_등록된다 · function · L22-L41 — def test_직업은_데이터파일표_한_줄로_등록된다()
- test_새_게임_캐릭터_스냅샷 · function · L45-L58 — def test_새_게임_캐릭터_스냅샷(직업, golden)
- test_이름없는_같은직업은_알파벳으로_구분 · function · L61-L66 — def test_이름없는_같은직업은_알파벳으로_구분()
- test_이름이_겹치면_새_게임을_시작하지_않는다 · function · L79-L83 — def test_이름이_겹치면_새_게임을_시작하지_않는다(파티구성): # B4: 이름이 겹치면 장비데이터모음({캐릭터명: ...})이 덮어써져 장비가 섞이고, # 이름/직업까지 같으면 파티원_추가가 같은 캐릭터로 보고 ValueError(앱 크래시).
- test_캐릭터명은_한글6자_영문12자로_자른다 · function · L86-L101 — def test_캐릭터명은_한글6자_영문12자로_자른다()
- test_겹침방지_알파벳은_글자제한과_별개다 · function · L104-L106 — def test_겹침방지_알파벳은_글자제한과_별개다()
- test_시작_진행도_소지품 · function · L109-L120 — def test_시작_진행도_소지품(golden)
- test_세이브_불러오기_왕복 · function · L123-L137 — def test_세이브_불러오기_왕복(임시_세이브폴더)
- _보스전_자동진행 · function · L140-L175 — def _보스전_자동진행(파티구성, 시드, 최대반복=500)
- test_보스전_4인파티 · function · L179-L181 — def test_보스전_4인파티(시드, golden)
- test_보스전_단독 · function · L185-L187 — def test_보스전_단독(직업, golden)
- test_같은_시드는_같은_전투 · function · L190-L192 — def test_같은_시드는_같은_전투()
