# game/system/combat/flow.py

- 전투_시작 · function · L24-L125 — def 전투_시작( 파티, 몬스터원본목록, 장비데이터모음, 버프정의모음=None, 디버프정의모음=None, 상태이상정의모음=None, 특성정의모음=None, 캐릭터특성정의모음=None, 칭호정의모음=None, 세트정의모음=None, 시작반응_보류=False, 스킬정의모음=None, )
- _참가자_구분 · function · L128-L147 — def _참가자_구분(전투상태)
- _턴순서_정렬 · function · L150-L155 — def _턴순서_정렬(전투상태)
- 이니셔티브_재계산_및_정렬 · function · L158-L165 — def 이니셔티브_재계산_및_정렬(전투상태)
- 턴_시작_처리 · function · L173-L252 — def 턴_시작_처리(전투상태, 참가자)
- 턴_종료_처리 · function · L255-L284 — def 턴_종료_처리(전투상태, 참가자)
- 현재_턴_참가자 · function · L287-L288 — def 현재_턴_참가자(전투상태)
- 다음_턴 · function · L291-L337 — def 다음_턴(전투상태)
- 전투이탈_시도 · function · L340-L388 — def 전투이탈_시도(전투상태, 참가자)
