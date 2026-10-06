# tests/test_scenario_s5.py

- _패배 · class · L24-L25 — class _패배(Exception)
- _진행도_스냅샷 · function · L28-L34 — def _진행도_스냅샷(상태)
- _패배_처리 · function · L37-L52 — def _패배_처리(상태, 기록, 시도, 골드전, 진행도전)
- test_S5_패배_휴식_재도전 · function · L56-L92 — def test_S5_패배_휴식_재도전(golden)
- 전투처리 · function · L65-L75 — def 전투처리(s, 시도=시도): # 이 전투 직전의 골드/진행도 - 앞선 인카운트에서 이긴 전리품은 이미 들어왔다
- _도망_성공까지 · function · L95-L120 — def _도망_성공까지(상태, 기록, 라벨)
- test_S5_도망 · function · L124-L194 — def test_S5_도망(golden)
- 인카운트_이기기 · function · L170-L173 — def 인카운트_이기기(s)
