# game/system/combat/formula.py

- _노드_평가 · function · L33-L54 — def _노드_평가(노드)
- _계산 · function · L58-L60 — def _계산(식): # eval처럼 앞뒤 공백은 무시한다. 순수 함수라(같은 문자열 -> 같은 값) 결과를 캐시한다.
- 안전_평가 · function · L63-L69 — def 안전_평가(식)
- _다이스_치환 · function · L72-L79 — def _다이스_치환(match, 치명타=False)
- 무기공격력_굴림 · function · L82-L90 — def 무기공격력_굴림(무기공격력_수식, 치명타=False)
- 수식_평가 · function · L93-L179 — def 수식_평가(수식, 컨텍스트, 치명타=False)
