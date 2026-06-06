# MV Generator — 수업용 실행 가이드

> 처음 실행하는 학생을 위한 단계별 안내서입니다.

---

## 준비물 체크리스트

설치 전, 아래 항목을 먼저 확인하세요.

- [ ] **Python 3.10 이상** — `python --version` 으로 확인
- [ ] **Node.js 18 이상** — `node --version` 으로 확인
- [ ] **FFmpeg** — `ffmpeg -version` 으로 확인
- [ ] **Google Cloud CLI** — `gcloud --version` 으로 확인
- [ ] **Google 계정** — Gmail 계정 있으면 됩니다

---

## 처음 1회만 하는 작업

### Step A. 패키지 설치

**Windows**
```
INSTALL.bat 더블클릭
```

**Mac / Linux**
```bash
bash install.sh
```

완료 메시지가 나오면 창을 닫습니다.

---

### Step B. Google Cloud 계정 만들기 + 무료 크레딧 받기

1. [console.cloud.google.com](https://console.cloud.google.com) 접속
2. Google 계정으로 로그인
3. **새 프로젝트 만들기** → 이름 아무거나 입력 → 만들기
4. 프로젝트 ID 복사해두기 (예: `my-project-123456`)

> **중요**: "$300 무료 크레딧" 팝업이 뜨면 **"무료로 시작하기"** 클릭  
> **"유료 계정으로 업그레이드"는 절대 클릭 금지** — 청구될 수 있습니다

---

### Step C. Google 로그인 (AUTH 실행)

**Windows**
```
AUTH.bat 더블클릭
```

**Mac / Linux**
```bash
bash auth.sh
```

실행하면:
1. 브라우저가 열립니다 → Google 계정으로 로그인 → "허용" 클릭
2. 터미널로 돌아와서 Project ID 입력 (Step B에서 복사한 것)
3. Enter

완료 메시지가 나오면 닫습니다.

---

## 매번 앱 실행할 때

**Windows**
```
RUN.bat 더블클릭
```

**Mac / Linux**
```bash
bash run.sh
```

- 검은 창이 2개 뜹니다 (백엔드 서버, 프론트엔드 서버)
- 잠시 후 브라우저가 자동으로 열립니다
- 열리지 않으면 직접 `http://localhost:5173` 접속

> **두 검은 창을 사용 중에는 닫지 마세요.** 닫으면 앱이 꺼집니다.

---

## 앱 사용 순서 (5단계)

브라우저가 열리면 Google Cloud Project ID를 입력하고 시작합니다.

```
[1단계] 가사 만들기
  장르, 테마 선택 → "가사 생성" 클릭
  마음에 들지 않으면 전체 재생성 또는 섹션별 수정 가능

[2단계] 음악 + 스토리
  "Lyria로 생성" 클릭 → AI가 90~120초 노래 자동 제작 (5~10분 소요)
  또는 직접 음악 파일 업로드 가능
  스토리 생성 → 10개 씬 자동 구성 (코러스는 재사용으로 비용 절약)

[3단계] 이미지
  스타일 선택 (한국웹툰시트 / 시네마틱판타지 / 지브리 등 17종)
  "캐릭터 시트 생성" → "씬 이미지 생성" 순서로 클릭
  (각각 3~10분 소요)

[4단계] 영상 클립
  "영상 생성 시작" 클릭
  씬당 약 3~5분 소요, 총 7개 신규 클립 생성 (코러스 3개는 복사 재사용)
  가장 오래 걸리는 단계입니다 (30~50분)

[5단계] 최종 편집
  자막 스타일, 전환 효과 선택
  "최종 영상 합성" 클릭 → 1~2분 후 MP4 완성
  "다운로드" 클릭
```

---

## 비용 안내 (편당)

| 단계 | 예상 비용 |
|------|-----------|
| 가사 · 스토리 | 무료 |
| 음악 생성 | ~$0.08 |
| 이미지 생성 | ~$1.00 |
| 영상 클립 생성 | ~$8.40 |
| 최종 편집 | 무료 |
| **합계** | **약 $10/편** |

> $300 크레딧으로 약 **29편** 제작 가능  
> 앱 우측 상단의 비용 표시기를 항상 확인하세요

---

## 앱 종료할 때

**Windows**
```
STOP.bat 더블클릭
```

또는 MV-Backend, MV-Frontend 창을 직접 닫아도 됩니다.

**Mac / Linux**
```bash
bash stop.sh
```

---

## 자주 묻는 문제

### 브라우저가 자동으로 안 열려요
`http://localhost:5173` 을 직접 브라우저 주소창에 입력하세요.

### "gcloud를 찾을 수 없습니다" 오류
Google Cloud CLI가 설치되지 않았습니다.  
→ [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install) 에서 설치 후 터미널 재시작

### "ffmpeg을 찾을 수 없습니다" 오류
FFmpeg이 PATH에 등록되지 않았습니다.  
→ [ffmpeg.org/download.html](https://ffmpeg.org/download.html) 에서 다운로드 후 설치

### 로그인 창이 다시 뜨면서 "인증 필요" 오류
ADC 인증이 만료됐습니다. `AUTH.bat` 을 다시 실행하세요.

### 영상 생성 중 "안전 필터" 오류
해당 씬만 재생성 버튼을 누르면 자동으로 순화해서 재시도합니다.

### npm 설치 중 창이 꺼짐
`INSTALL.bat` 을 다시 더블클릭하세요. (이미 설치된 것은 건너뜀)

---

## 출력 파일 위치

완성된 영상은 다음 경로에 저장됩니다:

```
mv-generator/
└── output/
    └── proj_날짜_시간_xxxx/
        └── 07_final/
            └── mv.mp4   ← 완성 영상
```

---

## 폴더 구조 요약

```
mv-generator/
├── RUN.bat          ← 앱 실행 (매번)
├── AUTH.bat         ← 구글 로그인 (최초 1회)
├── INSTALL.bat      ← 패키지 설치 (최초 1회)
├── STOP.bat         ← 앱 종료
├── backend/         ← Python FastAPI 서버
├── frontend/        ← React 웹 앱
└── output/          ← 생성된 영상 저장소
```
