# game/system/dungeon_system.py

- 그리드_생성 · function · L36-L39 — def 그리드_생성(맵정보)
- 칸_문자 · function · L42-L49 — def 칸_문자(그리드, 위치)
- _기본_시작좌표 · function · L52-L58 — def _기본_시작좌표(그리드)
- 던전_시작 · function · L61-L86 — def 던전_시작(맵정보, 던전파일명, 시작좌표=None, 진행도=None)
- 해금상태_적용 · function · L89-L112 — def 해금상태_적용(던전상태, 진행도)
- 인카운트_판정 · function · L121-L156 — def 인카운트_판정(던전상태)
- 이동_시도 · function · L159-L202 — def 이동_시도(던전상태, 방향, 인카운트없음=False)
- 오브젝트_클리어_처리 · function · L205-L218 — def 오브젝트_클리어_처리(던전상태, 위치)
