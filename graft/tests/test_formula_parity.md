# tests/test_formula_parity.py

- _다이스_치환_이전 · function · L24-L31 — def _다이스_치환_이전(match, 치명타=False)
- 무기공격력_굴림_이전 · function · L34-L42 — def 무기공격력_굴림_이전(무기공격력_수식, 치명타=False)
- 수식_평가_이전 · function · L45-L133 — def 수식_평가_이전(수식, 컨텍스트, 치명타=False)
- _결과 · function · L139-L149 — def _결과(함수, *인자, 시드)
- test_데이터의_모든_수식은_옛_평가기와_같은_값을_낸다 · function · L183-L198 — def test_데이터의_모든_수식은_옛_평가기와_같은_값을_낸다()
- test_무작위_계산식도_옛_평가기와_같다 · function · L234-L250 — def test_무작위_계산식도_옛_평가기와_같다()
- test_지수_버림나눗셈_부호도_같다 · function · L256-L258 — def test_지수_버림나눗셈_부호도_같다(식)
- test_안전_평가는_계산식만_계산한다 · function · L264-L273 — def test_안전_평가는_계산식만_계산한다()
- test_안전_평가는_계산식이_아닌_것을_거부한다 · function · L292-L294 — def test_안전_평가는_계산식이_아닌_것을_거부한다(식)
- test_다이스_개수식에도_같은_제한이_걸린다 · function · L297-L304 — def test_다이스_개수식에도_같은_제한이_걸린다()
- test_평가_결과는_캐시되어도_주사위는_매번_새로_굴린다 · function · L307-L311 — def test_평가_결과는_캐시되어도_주사위는_매번_새로_굴린다()
