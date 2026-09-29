# 던전앤파이터 모바일 프로토타입

Kivy로 만든 턴제 RPG 프로토타입이다. buildozer로 안드로이드 APK를 빌드한다.

- `main.py` - Kivy 앱 진입점, 화면 등록
- `gameflow.py` - 화면과 게임 로직/데이터 사이를 잇는 컨트롤러. 화면은 이 파일의 함수만 부른다
- `game/screens/` - Kivy 화면
- `game/system/` - 전투, 스킬, 장비, 세이브 등 게임 로직
- `game/data/` - 직업, 몬스터, 맵, 아이템 데이터(파이썬 딕셔너리)
- `game/assets/` - 폰트, 이미지

원격 저장소: https://github.com/kirnata77/asdf (브랜치 `main`)

## Git 작업 규칙

**커밋하면 그 커밋을 바로 원격 저장소(origin)에 push한다.** 커밋만 하고 로컬에 쌓아 두지 않는다.

이 과정은 `.githooks/post-commit` 훅이 자동으로 한다. 커밋이 끝나면 훅이 현재 브랜치를 `origin`에 push하고, 처음 올리는 브랜치면 upstream도 설정한다. 리베이스나 체리픽 중에는 건너뛴다.

### 훅 켜기 (저장소마다 한 번)

```
git config core.hooksPath .githooks
```

`git config core.hooksPath`가 `.githooks`를 출력하면 켜진 상태다. 커밋할 때 `[post-commit] origin/<브랜치> 에 push합니다...`가 출력되면 정상이다.

### 커밋할 때 확인할 것

1. 커밋한 뒤 출력에서 push 성공 여부를 확인한다.
2. `[post-commit] push에 실패했습니다`가 나오면 커밋은 로컬에 남아 있다. 원인(네트워크, 인증, 원격이 앞서 있음 등)을 해결하고 `git push`로 직접 올린다.
3. 훅이 켜져 있지 않은 환경이면 커밋 직후 `git push`를 직접 실행한다.
4. 원격에 이미 올라간 커밋은 `--amend`나 `rebase`로 고치지 말고 새 커밋으로 수정한다(강제 push가 필요해지기 때문).
