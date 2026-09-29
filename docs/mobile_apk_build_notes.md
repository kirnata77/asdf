# 모바일 APK 빌드 노트

> **주의: 2026-09-16 기준 기록이고 일부 낡았으며 끝이 잘려 있다.** 지금은 GitHub
> Actions(`.github/workflows/build-apk.yml`)가 APK를 빌드한다. 낡은 부분 목록은
> `.memory/active-issues/known-bugs.md`의 "문서" 절. (원래 위치: `game/`)

작업 위치(클라우드 프로토타입): `/home/claude/dnf_mobile` (Kivy 이식판).
실제 프로젝트 경로: `Z:\백업\코딩연습\game` (파일 배치는 `file_path.py` 참고).

## 1. 왜 APK 빌드를 이 세션(클라우드 샌드박스)에서 못 하는가

buildozer(python-for-android)는 빌드 중 Android SDK/NDK, Apache Ant 등을
`dl.google.com`/`archive.apache.org`에서 내려받아야 하는데, 이 클라우드
세션의 네트워크는 pypi/npm/github(git 프로토콜) 등으로만 제한돼 있어
403/터널 실패가 난다. 이건 특정 회사 컴퓨터의 보안 정책이 아니라, 이
클라우드 샌드박스 자체의 고정된 속성이다 - 어떤 기기로 접속해도 동일하다.

**해결책: Google Colab**에서 빌드한다. Colab은 인터넷 제한이 없어서
buildozer가 SDK/NDK/Ant를 정상적으로 받아 빌드를 끝까지 마칠 수 있다.
(대안으로 GitHub Actions도 있으나, 이번엔 Colab을 선택해 진행했다.)

## 2. Colab에서 빌드하는 순서 (실제로 성공한 명령)

1. `dnf_mobile.zip`을 Colab 세션에 업로드한다.
2. 압축 해제(재실행 시 덮어쓰기 프롬프트를 피하려면 `-o` 사용):
   ```
   !unzip -o -q dnf_mobile.zip
   ```
3. buildozer 설치:
   ```
   !pip install buildozer cython
   ```
4. `dnf_mobile/buildozer.spec`에서 `[buildozer]` 섹션에
   `warn_on_root = 0`을 넣어야 한다 - `[app]` 섹션에 넣으면 인식하지 못하고
   "Buildozer is running as root!" 프롬프트에서 `EOFError`로 멈춘다
   (Colab은 항상 root로 실행되기 때문에 반드시 필요).
5. 빌드 실행:
   ```
   %cd dnf_mobile
   !buildozer android debug
   ```
6. Android SDK 라이선스 동의 프롬프트(`Accept? (y/N):`)가 뜨면 모바일에서는
   응답하기 어려우므로, 셀을 중단하고 아래로 한 번에 전체 동의시킨 뒤
   다시 `buildozer android debug`를 실행한다:
   ```
   !yes | ~/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager --sdk_root=~/.buildozer/android/platform/android-sdk --licenses
   ```
7. 빌드가 끝나면 `dnf_mobile/bin/dnfmobile-0.1-arm64-v8a-debug.apk`가
   생성된다. Colab 파일 브라우저(모바일에서는 "파일 브라우저 표시" 메뉴)
   에서 다운로드해 폰에 설치하면 된다.

## 3. 한글이 네모(□)로 깨지는 문제와 수정

**원인**: Kivy 기본 폰트 별칭 "Roboto"에는 한글 글리프가 없다.

**수정**: `main.py`에서 `screens.py`를 import하기 **전에**
`kivy.core.text.LabelBase.register(name="Roboto", fn_regular=..., fn_bold=...)`
로 "Roboto" 별칭 자체를 나눔고딕(NanumGothic) TTF로 덮어썼다. 이러면
위젯마다 `font_name`을 따로 지정하지 않아도 모든 Label/Button 등에
자동 적용된다.

- 폰트 파일 위치: `game/assets/font/NanumGothic-Regular.ttf`,
  `NanumGothic-Bold.ttf` (실제 프로젝트 기준 - `file_path.py` 참고).
- **buildozer.spec에 `source.include_exts`로 `ttf`/`otf`가 포함돼 있어야
  APK 안에 폰트 파일이 실제로 패키징된다** - 빠지면 로컬에서는 되는데
  APK에서는 다시 깨진다.
- import 순서 중요: `LabelBase.register(...)`가 `from screens import ...`
  보다 먼저 실행돼야 화면들이 만들어지는 시점에 이미 "Roboto" 별칭이
  덮어써진 상태다.

검증은 실제 Kivy `App` 컨텍스트 안에서 해야 한다 - `Window`/`App` 없이
`CoreLabel(...).refresh()`만 단독으로 부르면 이 환경에서는 세그폴트가
나는데, 이건 폰트 수정과 무관한 헤드리스 테스트 환경 자체의 특이 동작이다
(전체 `App` 컨텍스트 안에서 테스트하면 정상 동작 확인됨).

## 4. 이번 빌드에 포함된 범위 (2026-09-16 확장판)

첫 APK는 귀검사 1명 + 로리엔 던전 + 세이브/마을 없음으로 최소 범위였고,
이후 사용자 요청으로 아래 4가지를 전부 추가했다:

1. **메인 메뉴 + 세이브/불러오기** - `main.py`가 이제 "메인메뉴" 화면으로
   시작한다(새로운 시작/불러오기/옵션/게임 종료). 원본 프로젝트의
   `save_system.py`를 그대로 포팅(`game/system/save_system.py`) - JSON
   기반, 3슬롯, `game/saves/slot_N.json`에 저장된다.
2. **4인 파티** - 파티 생성 화면에서 최대 4명까지 이름+직업을 정해 시작할
   수 있다(`party_system.py`의 `파티_최대인원 = 4`를 그대로 사용 -
   combat 패키지/skill_system.py는 원래부터 다인원에 일반적으로
   동작해서 전투 엔진 자체는 손댈 필요가 없었다).
3. **5직업 전부** - 귀검사 외 격투가/거너/마법사/프리스트의 1차수 데이터
   (job_skill/job_level/job_ability/무기 목록)를 전부 이식했다. 레벨
   3까지만 자동 성장시키므로(2차전직은 레벨 6부터라 이번 범위 밖) 2차전직
   직업 파일(웨폰마스터 등)은 옮기지 않았다.
4. **마을 시스템** - `town_system.py`(원본의 실제 구현판, 스텁이 아님)와
   시작 마을 "엘븐가드" 데이터를 이식했다. 마을에서 휴식(파티 전원
   HP/MP 전량 회복), 던전 이동(로리엔), 저장하기를 할 수 있다. 로리엔
   던전의 서쪽 끝 "#" 칸으로 나가면 다시 마을로 돌아온다.
   **상점/NPC/창고는 버튼만 있고 비활성 상태다** - 원본 프로젝트에도
   `shop_system.py`가 `"test"`라는 문자열뿐인 자리표시자이고
   `item_potion.py`/`item_consumable.py`도 빈 `{}`라, 포팅할 실제
   백엔드 자체가 없다(원본 tkinter판 `ui_town.py`도 동일하게 비활성
   처리돼 있음 - 이번 프로토타입만의 임의 축소가 아니다).

파티 전멸 시에는 부활/페널티 시스템이 아직 없어서, HP/MP를 전부 회복시켜
마을로 돌려보내는 것으로 임시 처리했다(`town_system.휴식_처리`의 주석에
남긴 가정과 같은 맥락 - 추후 확인/조정 필요할 수 있음).

빌드/설치 절차 자체(2절)는 이전과 동일하다 - `dnf_mobile.zip`만
새 버전으로 교체해서 같은 순서를 따르면 된다.