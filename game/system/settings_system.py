# =====================
# 기기 설정 시스템
# =====================
# 세이브와 별개인 앱 설정 파일(설정.json)을 읽고 쓴다. 키는 "반응자동",
# "자동전투방식", "전투로그방식"(값의 뜻과 기본값은 controller의 ctl_battle).
# 경로는 화면이 앱 데이터 폴더(kivy user_data_dir)로 정해 넘긴다 - 이 모듈은
# kivy를 모른다. 파일이 없거나 깨져도 게임은 기본값으로 계속한다.

import json
import os

__all__ = ["설정_읽기", "설정_쓰기"]


def 설정_읽기(경로):
    """설정 파일을 딕셔너리로 읽는다. 없거나(OSError) 깨졌거나(ValueError - JSON 오류,
    잘못된 인코딩) 딕셔너리가 아니면 빈 설정으로 시작한다."""
    try:
        with open(경로, encoding="utf-8") as 파일:
            설정 = json.load(파일)
    except (OSError, ValueError):
        return {}
    return 설정 if isinstance(설정, dict) else {}


def 설정_쓰기(경로, 설정):
    """설정 딕셔너리를 파일에 쓴다. 임시 파일에 다 쓴 뒤 바꿔치기해서 도중에 실패해도 옛 파일은
    그대로다(세이브의 원자적 쓰기와 같은 방식, .bak은 없다). 쓰지 못하면(OSError) 임시 파일을
    지우고 False - 이번 실행의 값은 이미 컨트롤러에 들어가 있으니 부르는 쪽은 그냥 넘어간다."""
    임시 = 경로 + ".tmp"
    try:
        with open(임시, "w", encoding="utf-8") as 파일:
            json.dump(설정, 파일, ensure_ascii=False)
            파일.flush()
            os.fsync(파일.fileno())
        os.replace(임시, 경로)
    except OSError:
        if os.path.isfile(임시):
            os.remove(임시)
        return False
    return True
