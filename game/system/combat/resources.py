# 전투 시스템 - 효과 정의 조회와 자원(보유/소모/장전).
# (combat 패키지에서 분리 - R4. 전체 설계 설명은 game/system/combat/__init__.py)

from game.data.buff import buff
from game.data.buff import debuff
from game.data.buff import skill_effects
from game.system.combat import formula, stats

# =====================================================
# 효과 정의 조회 / 자원 (원래 skill_system.py에 있던 함수들)
# =====================================================
# skill_system.py의 동명 함수들이 이 함수들을 그대로 위임 호출한다.

def 효과정의_조회(이름):
    """이름을 기술효과목록 → 버프목록 → 디버프목록 순으로 찾아
    (정의, 출처) 튜플을 반환한다. 출처는 "기술효과"/"버프"/"디버프" 중
    하나. 없으면 (None, None)."""
    if 이름 in skill_effects.기술효과목록:
        return skill_effects.기술효과목록[이름], "기술효과"
    if 이름 in buff.버프목록:
        return buff.버프목록[이름], "버프"
    if 이름 in debuff.디버프목록:
        return debuff.디버프목록[이름], "디버프"
    return None, None


def 자원_보유량(전투상태, 참가자, 이름):
    정의, 출처 = 효과정의_조회(이름)
    if 출처 == "기술효과":
        for 항목 in 참가자["버프"]:
            if 항목["이름"] == 이름:
                return 항목.get("중첩", 1)
        return 0
    return 참가자.get("보유자원", {}).get(이름, 0)


def 자원_소모(전투상태, 참가자, 이름, 개수=1):
    """자원이 부족해도 에러를 내지 않고 (성공여부, 실제소모량)을 반환한다
    - 소모 가능 여부 자체는 skill_system.사용_가능여부()가 미리 검사한다."""
    정의, 출처 = 효과정의_조회(이름)
    if 출처 == "기술효과":
        for 항목 in list(참가자["버프"]):
            if 항목["이름"] == 이름:
                보유 = 항목.get("중첩", 1)
                if 보유 <= 개수:
                    참가자["버프"].remove(항목)
                else:
                    항목["중첩"] = 보유 - 개수
                return True, min(보유, 개수)
        return False, 0

    보유자원 = 참가자.setdefault("보유자원", {})
    보유 = 보유자원.get(이름, 0)
    if 보유 <= 0:
        return False, 0
    실제소모 = min(보유, 개수)
    보유자원[이름] = 보유 - 실제소모
    return True, 실제소모


def 장전소모_처리(전투상태, 참가자):
    """"장전 : OO"(은탄 등) 버프가 있으면 1개 소모하고 (이름, 속성변환,
    추가피해값, 추가피해속성) 튜플을 반환한다. "추가피해"는 공격당 한 번만
    굴려 모든 타격에 동일하게 더한다. "추가피해속성"이 있으면(은탄 - 명)
    추가피해는 공격 속성과 따로 그 속성으로 저항/취약을 적용한다
    (피해_적용의 추가피해목록). 소모할 장전 버프가 없으면
    (None, None, 0, None). 일반공격_실행/skill_system.공격스킬_실행이 함께 쓴다."""
    for 항목 in list(참가자["버프"]):
        if 항목["이름"].startswith("장전 : "):
            자원_소모(전투상태, 참가자, 항목["이름"], 1)
            정의, _ = 효과정의_조회(항목["이름"])
            효과 = (정의 or {}).get("효과", {})
            추가피해식 = 효과.get("추가피해")
            추가피해 = formula.수식_평가(추가피해식, stats.기본_컨텍스트(전투상태, 참가자)) if 추가피해식 else 0
            return 항목["이름"], 효과.get("속성변환"), 추가피해, 효과.get("추가피해속성")
    return None, None, 0, None
