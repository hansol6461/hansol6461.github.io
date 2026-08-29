# 이한솔 개인 홈페이지

영문판과 국문판을 함께 제공하는 정적 사이트입니다. GitHub Pages에서 Jekyll이
자동으로 빌드하므로 컴퓨터에 아무것도 설치하지 않아도 됩니다.

---

## 1. 처음 올리기 (약 10분)

**1) GitHub 가입**
[github.com](https://github.com)에서 계정을 만듭니다. 아이디가 곧 사이트 주소가
됩니다. 아이디가 `hansol6461`이므로 주소는 `hansol6461.github.io`가 됩니다.

**2) 저장소 만들기**
오른쪽 위 `+` → `New repository`

- Repository name: `hansol6461.github.io`
- Public 선택
- 나머지는 그대로 두고 `Create repository`

**3) 파일 올리기**
저장소 첫 화면의 `uploading an existing file` 링크를 누르고, 이 폴더 안의 파일과
폴더를 전부 끌어다 놓습니다. 아래쪽 `Commit changes` 버튼을 누르면 끝입니다.

**4) Pages 켜기**
`Settings` → 왼쪽 메뉴 `Pages` → Source를 `Deploy from a branch`,
Branch를 `main` / `/ (root)`로 두고 `Save`.

1~2분 뒤 `https://hansol6461.github.io`로 접속됩니다.

`_config.yml`의 주소는 이미 `hansol6461`로 채워져 있습니다.

---

## 2. 프로필 사진

`assets/img/profile.jpg` 에 이미 넣어두었습니다.

바꾸시려면 같은 이름으로 덮어쓰면 됩니다. 세로로 긴 비율(4:5 정도)에
가로 600px 이상을 권합니다. 얼굴이 화면에서 작게 나오므로 머리와 어깨
위주로 잘라야 알아보기 좋습니다.

화면에서는 채도를 조금 낮춰 표시합니다. 원본은 그대로 두고 CSS에서만
처리하므로, 색감이 마음에 안 드시면 `assets/css/style.css` 의 `.portrait`
안에 있는 `filter` 줄을 지우면 원본 색으로 나옵니다.

---

## 3. 내용 고치기

모든 내용은 `_data/` 폴더의 네 파일에 들어 있습니다. HTML을 건드릴 일은 없습니다.

| 파일 | 내용 | 갱신 방식 |
|---|---|---|
| `_data/publications.yml` | 학술논문 (표시용) | **자동** — 직접 고치지 마십시오 |
| `_data/publications_manual.yml` | 학술논문 (원본) | 수기 |
| `_data/cv.yml` | 경력, 학력, 연구과제, 번역, 연구 분야 | 수기 |
| `_data/press.yml` | 언론 보도 | 수기 |
| `_data/i18n.yml` | 화면 문구와 소개글 | 수기 |

### 논문 목록은 자동으로 갱신됩니다

Google Scholar는 공개 API가 없어 직접 가져올 수 없습니다. 대신 **OpenAlex**를
씁니다. Crossref를 실시간으로 받아오는 공개 데이터베이스라, 논문이 출판되면
대개 며칠 안에 잡힙니다. 행님 ORCID(`0000-0002-6912-7128`)로 조회합니다.

`.github/workflows/sync-publications.yml`이 **매주 월요일 새벽 3시**에 돌면서

1. OpenAlex에서 ORCID로 걸린 논문을 전부 받고
2. `_data/publications_manual.yml`의 수기 목록과 합친 뒤
3. `_data/publications.yml`에 씁니다

새 논문이 있을 때만 커밋하므로 이력이 지저분해지지 않습니다.
지금 바로 돌려보려면 저장소 `Actions` 탭 → `Sync publications` →
`Run workflow` 버튼을 누르십시오.

**수기 목록이 항상 이깁니다.** 서지 표기를 직접 다듬어 두었거나,
OpenAlex에 없는 KCI 논문(군사과학논집, 영어평가 등)도 그대로 유지됩니다.
OpenAlex 조회가 실패해도 수기 목록을 그대로 쓰므로 목록이 비는 일은 없습니다.

### 논문을 수기로 고치거나 추가하기

`_data/publications_manual.yml`을 고칩니다. `_data/publications.yml`이 아닙니다.

```yaml
- id: J55
  year: 2026
  date: '2026-09-15'
  authors: <strong>Lee, H.</strong>, & Kim, S.
  title: 'Title of the paper: With a subtitle'
  venue: Journal Name
  detail: 30(2), 1–20
  doi: https://doi.org/10.xxxx/xxxxx
  index: SSCI
```

- 본인 이름은 `<strong>`으로 감싸면 굵게 나옵니다.
- 제목에 콜론(`:`)이 들어가면 반드시 작은따옴표로 감싸야 합니다.
- `date`는 정렬에 쓰입니다. 월을 모르면 `'2026-01-01'`처럼 적어도 됩니다.
- `index`는 `SSCI`, `Scopus`, `KCI` 중 하나거나 빈 문자열입니다.
- `id`는 자동으로 다시 매겨지니 대충 넣어도 됩니다.

자동 수집분의 저자 표기가 마음에 안 들면(예: `Tabari, M. A.`를
`Abdi Tabari, M.`으로 고치고 싶을 때) 같은 DOI로 수기 목록에 항목을 만드십시오.
DOI가 일치하면 수기 쪽 표기로 덮어씁니다.

### 연구과제는 수기입니다

`_data/cv.yml`의 `projects:` 아래에 같은 형식으로 넣습니다. 연구과제는
공개 데이터베이스에 없으므로 자동화할 수 없습니다. 영문과 국문을 나란히
적어야 두 페이지에 모두 나옵니다. `translations:`(번역 실적)도 같습니다.

---

## 3-1. 숨겨둔 섹션 다시 켜기

학회 활동과 수상 이력은 데이터는 남아 있고 화면에만 안 나옵니다.
다시 보이게 하려면 `_config.yml`의 다음 부분에서 `false`를 `true`로 바꾸십시오.

```yaml
show:
  service: false      # 학회 활동
  awards: false       # 수상 이력
```

---

## 4. 검색 노출 (해두면 좋은 것)

사이트를 올린 다음 순서대로 하시면 됩니다.

1. **ORCID 프로필**의 Websites 항목에 사이트 주소 추가
2. **Google Scholar 프로필**의 Homepage 칸에 주소 추가
   (`_config.yml`에 이미 넣어두었고 구조화 데이터에도 들어가 있습니다)
3. **육사 교수 소개 페이지**에 주소 추가 — 기관 도메인이라 가중치가 큽니다
4. **한국연구재단 KRI** 연구자 정보에 주소 추가
5. **구글 서치 콘솔**([search.google.com/search-console](https://search.google.com/search-console))에
   사이트 등록 후 `https://hansol6461.github.io/sitemap.xml` 제출

### 네이버는 따로 등록해야 합니다

구글에 잡힌다고 네이버에 자동으로 나오지 않습니다. 네이버는 자체 크롤러를
쓰기 때문에 **서치어드바이저**에 등록하지 않으면 검색에 아예 안 잡힙니다.

1. [searchadvisor.naver.com](https://searchadvisor.naver.com) 접속 후 네이버
   계정으로 로그인
2. 웹마스터 도구 → 사이트 관리 → `https://hansol6461.github.io` 등록
3. 소유 확인 단계에서 **HTML 태그** 방식을 고르면 `content` 값을 줍니다.
   그 값을 `_config.yml` 의 `verify.naver` 에 넣으십시오.

   ```yaml
   verify:
     google: ""
     naver: "여기에 붙여넣기"
   ```

   커밋하면 `<head>` 에 자동으로 들어갑니다. 다시 확인 버튼을 누르면 됩니다.
4. 등록 후 왼쪽 메뉴 요청 → 사이트맵 제출에서 `sitemap.xml` 입력
5. 요청 → 웹페이지 수집에서 주소를 직접 넣으면 수집이 빨라집니다

구글 서치 콘솔도 같은 방식입니다. HTML 태그 방식으로 받은 값을
`verify.google` 에 넣으면 됩니다. 네이버 크롤러가 사이트를 수집하기까지는
보통 1주에서 4주 걸립니다.

### 네이버 인물정보에 홈페이지 주소 넣기

이게 사실 위의 모든 작업보다 효과가 큽니다. 네이버 인물정보는 도메인
신뢰도가 높아서, 거기서 홈페이지로 링크가 걸리면 구글과 네이버 양쪽에서
가중치를 받습니다. 인물정보 페이지의 정보 수정 요청으로 홈페이지 항목을
추가하십시오.

### ORCID 레코드도 채워두기

`_config.yml` 의 ORCID는 세 곳에 쓰입니다.

- 화면 표시 (공식 iD 마크와 함께)
- 구조화 데이터의 `identifier` 와 `sameAs`
- 논문 자동 갱신의 조회 키

그런데 반대 방향도 걸어두어야 효과가 납니다. [orcid.org](https://orcid.org)에
로그인해서 **Websites & social links** 항목에 홈페이지 주소를 넣고, 공개
범위를 Everyone으로 두십시오. Employment 항목에 육군사관학교도 채워두면
동명이인 구분에 도움이 됩니다.

사이트에는 schema.org의 Person 구조화 데이터가 이미 들어 있습니다. 구글이
ORCID와 Scholar 계정을 같은 사람으로 묶는 데 쓰이며, 동명이인과 구분하는 데
가장 직접적으로 작용하는 부분입니다.

---

## 5. 사용자 도메인 붙이기 (나중에)

도메인을 사시면 그때 다음만 하면 됩니다. 사이트를 다시 만들 필요는 없습니다.

1. GitHub 저장소 `Settings` → `Pages` → Custom domain에 도메인 입력 후 저장
2. 도메인 산 곳의 DNS 설정에서
   - A 레코드 4개: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - CNAME 레코드: 호스트 `www`, 값 `hansol6461.github.io`
3. DNS가 반영되면 `Enforce HTTPS` 체크
4. `_config.yml`의 `url`을 새 도메인으로 변경

---

## 6. 로컬에서 미리보기 (선택)

굳이 안 하셔도 됩니다. GitHub에 올리면 바로 확인할 수 있습니다.
그래도 하시려면 Ruby 설치 후:

```bash
bundle install
bundle exec jekyll serve
```

`http://localhost:4000`에서 열립니다.

---

## 파일 구조

```
├── _config.yml          사이트 설정 (주소, 이메일, ORCID, Scholar)
├── .github/workflows/   논문 목록 주간 자동 갱신
├── scripts/
│   └── sync_publications.py   OpenAlex 동기화
├── _data/               내용 데이터 — 여기만 고치면 됩니다
├── _includes/
│   ├── head.html        메타 태그와 구조화 데이터
│   └── body.html        본문 구조
├── _layouts/default.html 전체 틀
├── assets/
│   ├── css/style.css    디자인
│   ├── js/site.js       연도 필터, 현재 위치 표시
│   └── img/             프로필 사진 위치
├── index.html           영문판
└── ko/index.html        국문판
```
