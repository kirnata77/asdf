# 작업 보드 설정 - 조직으로 옮기기

작업 관리를 `MEMORY.md`/`.memory/` 파일에서 GitHub **Project 보드**로 옮긴다.
보드는 새 조직 **`megasunu`** 이 갖고, 저장소도 그 조직으로 옮긴다. kirnata77과 enjay27(Kade)은 둘 다 조직의 **Owner**다.

**진행: 2026-10-16 조직 `megasunu`를 만들고 저장소를 `megasunu/DFzero`로 옮겼다(주인 일 1~3 끝남).**

GitHub 화면의 메뉴 글자는 영어뿐이다(한국어 화면이 없다). 아래에 누를 버튼의 영어 이름을 `이렇게` 적었다.
보드 안의 이름(칸, 상태, 라벨, 이슈)은 모두 한국어로 만든다.

## 저장소 주인(kirnata77)이 할 일 - 3가지, 약 5분

### 시작 전에 - 폰에서 할 때

GitHub 앱(GitHub Mobile)에는 조직 만들기와 저장소 옮기기 메뉴가 없다. 폰 브라우저(삼성 인터넷/크롬)로 한다.

1. 브라우저에서 `github.com`에 kirnata77로 로그인한다.
2. 브라우저 메뉴(⋮ 또는 ≡)에서 **"데스크톱 사이트"(데스크톱 버전 보기)를 켠다.** 켜지 않으면 일부 버튼이 안 보인다.

### 1. 조직 만들기

1. `https://github.com/account/organizations/new?plan=free` 를 연다 (무료 조직).
2. `Organization name`: 조직 이름을 정해 쓴다. 영어 소문자·숫자·`-`만 되고, **모두에게 공개된다.** (이번에 정한 이름: `megasunu`)
3. `Contact email`: kirnata77의 메일 주소.
4. `This organization belongs to`: `My personal account`.
5. 사람 확인(퍼즐)을 풀고 약관에 동의한 뒤 `Next`를 누른다.
6. 다음 화면(`Add organization members`)은 `Skip this step`으로 넘긴다 - 여기서 초대하면 Owner가 아니라 Member가 된다.

### 2. enjay27을 Owner로 초대

1. `https://github.com/orgs/megasunu/people` 을 연다 (조직 화면 -> `People` 탭).
2. `Invite member`를 누르고 **enjay27** 을 찾아 고른다.
3. 역할(`Role in the organization`)을 **`Owner`** 로 고르고 `Send invitation`을 누른다.

enjay27이 수락하면 Kade도 조직의 Owner가 된다. 수락을 기다리지 않고 바로 3번을 해도 된다.

### 3. 저장소를 조직으로 옮기기

1. `https://github.com/kirnata77/asdf/settings` 를 연다 (저장소 -> `Settings` 탭).
2. 맨 아래 빨간 `Danger Zone`에서 `Transfer ownership` 줄의 `Transfer`를 누른다.
3. 새 주인(`New owner`)으로 **`megasunu`** 을 고른다.
4. 확인 칸에 저장소 이름 **`asdf`** 를 그대로 쓴다.
5. `I understand, transfer this repository.`를 누른다.

끝나면 `https://github.com/megasunu/DFzero` 가 열린다(옮기면서 이름을 `DFzero`로 바꿨다). enjay27에게 **조직 이름**과 "옮겼다"를 알려 주면 된다.

- 이슈, PR, 라벨, 릴리스, Secret, 브랜치 보호 설정은 **그대로 같이 옮겨진다.**
- 옛 주소 `github.com/kirnata77/asdf` 는 새 주소 `github.com/megasunu/DFzero`로 자동 연결된다.
  **kirnata77 계정에 `asdf`라는 저장소를 새로 만들지 않는다** - 만들면 이 연결이 끊긴다.

## 보드와 브리지 설정 (2026-10-16, Kade와 Claude)

Kade는 조직 Owner 초대를 수락했다. 나머지는 Kade의 PC에서 `gh`(조직 관리자 권한)로 했고, 웹 클릭은 App 두 번뿐이다.

| 무엇 | 어떻게 | 상태 |
|---|---|---|
| 보드 [던전앤파이터 모바일](https://github.com/orgs/megasunu/projects/1) (#1, 비공개), `DFzero`와 연결 | GraphQL `createProjectV2` | 끝남 |
| 칸: 상태 옵션(백로그/다음/지금/검토 중/완료), 단계, 검증, 우선순위, 시작, 목표 | GraphQL | 끝남 |
| 이슈 31개(#154~#183, #74)와 상태·단계·검증 값 | GraphQL | 끝남 |
| 화면: 보드, 로드맵, 결정 대기(`assignee:kirnata77 is:open`), 실기기 필요(`검증:"실기기 필요"`), 미확인(`검증:미확인`) | REST `POST /orgs/megasunu/projectsV2/1/views` | 끝남 |
| 브리지 App `megasunu-board-bridge`(조직 프로젝트 쓰기, 이슈·PR 읽기, 이 조직에만 설치) | App 매니페스트 흐름 - Kade가 `Create`, `Install` 두 번 클릭 | 끝남 |
| 조직 설정(DFzero에 공유): 변수 `BRIDGE_APP_CLIENT_ID`, `PROJECT_NUMBER`=1, Secret `BRIDGE_APP_PRIVATE_KEY` | `gh variable/secret set --org` | 끝남 |
| 명령 라벨 15개(아래 표) | `gh label create` | 끝남 |
| 워크플로 `project-sync.yml`, `project-snapshot.yml` | PR (워크플로 PR은 사용자가 병합) | PR |

**API로 안 되는 것 - 웹에서 한 번씩 (Kade):**

1. 기본 칸 이름 `Status`를 **상태**로. API는 옵션만 바꾸고 이름은 그대로 둔다(브리지는 두 이름 모두 읽는다).
   보드 -> `⋯` -> `Settings` -> `Status` -> 이름 고치기.
2. 보드를 만들 때 생긴 `View 1` 화면 이름을 **전체**로(또는 지운다). API로 화면 이름을 바꾸거나 지울 수 없다.
3. 보드의 기본 자동화(`Workflows`)는 켜지 않는다 - 새 이슈 -> 백로그, 닫힘 -> 완료, 다시 열림 -> 백로그는
   `project-sync`가 한다(PR이 닫으면 이슈도 닫혀 완료가 된다).
   단, `auto-merge.yml`이 GITHUB_TOKEN으로 닫은 이슈는 `project-sync`를 깨우지 않는다 - 다음 `Project snapshot`
   (하루 3번, 바로 필요하면 직접 실행)이 내보내기 전에 닫혔는데 완료가 아닌 이슈를 완료로 맞춘다(`--reconcile`, #189).

App 키를 잃거나 바꿀 때: App 페이지(`https://github.com/organizations/megasunu/settings/apps/megasunu-board-bridge`)에서
`Generate a private key` -> `gh secret set BRIDGE_APP_PRIVATE_KEY --org megasunu --visibility selected --repos DFzero < 키.pem`
-> 옛 키를 지운다. 키 파일은 저장소에 두지 않는다.

## 세션이 보드를 쓰는 법

- **로컬(Kade의 PC, `gh` 로그인):** `gh project item-list 1 --owner megasunu`, `gh project item-edit`로 직접.
- **클라우드 세션:** 보드 API에 닿지 못한다.
  - 읽기: `git fetch origin status && git show origin/status:STATUS.md` (하루 3번, 최신이 필요하면 `Project snapshot` 워크플로 실행).
  - 쓰기: 이슈에 명령 라벨을 단다. `project-sync`가 칸에 반영하고 라벨을 지운다(쓰기 권한자가 단 것만).

| 명령 라벨 | 칸 = 값 |
|---|---|
| `명령:상태-백로그` / `다음` / `지금` / `검토중` / `완료` | 상태 |
| `명령:단계-1차수` / `2차수` / `레벨12~20` / `품질구조` | 단계 |
| `명령:검증-확인됨` / `미확인` / `실기기필요` | 검증 |
| `명령:우선순위-1` / `2` / `3` | 우선순위 (1순위~3순위) |

- **주인이 정할 일**은 라벨이 아니라 담당자: 이슈 담당자를 kirnata77로 둔다. 담당자가 없는 이슈는 세션이 가져갈 수 있는 일이다.

## 보드 읽는 법 (설정이 끝난 뒤)

- **지금**: 지금 하는 일. **다음**: 다음에 할 일. **백로그**: 언젠가 할 일.
- **담당자가 kirnata77인 이슈 = 주인이 정해 줘야 하는 일.** "결정 대기" 화면에 모인다.
- **검증 = 실기기 필요**: 폰(갤럭시 S24)에서 직접 확인해야 하는 일. "실기기 필요" 화면에 모인다.
  확인했으면 이슈에 결과를 댓글로 남기면 된다.
