# MV Generator — AI 뮤직비디오 메이커

> 스토리 → 가사 → 음악 → 이미지 → 영상 전 과정 자동화  
> Google Cloud Vertex AI + $300 무료 크레딧으로 동작

---

## 목차

1. [사전 준비물](#1-사전-준비물)
2. [빠른 시작 (3단계)](#2-빠른-시작-3단계)
3. [환경 설정 (.env)](#3-환경-설정-env)
4. [앱 사용법 (5단계 워크플로)](#4-앱-사용법-5단계-워크플로)
5. [비용 안내](#5-비용-안내)
6. [청구 방지 안내](#6-청구-방지-안내)
7. [기술 스택](#7-기술-스택)
8. [프로젝트 구조](#8-프로젝트-구조)
9. [문제 해결](#9-문제-해결)

---

## 1. 사전 준비물

| 항목 | 버전 | 비고 |
|------|------|------|
| Python | 3.10 이상 | [python.org](https://www.python.org/downloads/) |
| Node.js | 18 이상 | [nodejs.org](https://nodejs.org/) |
| FFmpeg | 최신 | [ffmpeg.org](https://ffmpeg.org/download.html) — 시스템 PATH에 등록 필수 |
| Google Cloud CLI | 최신 | [설치 가이드](https://cloud.google.com/sdk/docs/install) |
| Google Cloud 계정 | — | [console.cloud.google.com](https://console.cloud.google.com) 무료 가입 |

> **FFmpeg PATH 등록**: Windows의 경우 시스템 환경변수 PATH에 FFmpeg bin 폴더를 추가해야 합니다.  
> 터미널에서 `ffmpeg -version` 이 출력되면 정상입니다.

---

## 2. 빠른 시작 (3단계)

### Windows

```
INSTALL.bat   ← 1회만: Python/Node 패키지 설치
AUTH.bat      ← 1회만: Google 계정 로그인
RUN.bat       ← 매번: 앱 실행 (백엔드 + 프론트엔드 + 브라우저 자동 실행)
```

### Mac / Linux

```bash
bash install.sh   # 1회만: 패키지 설치
bash auth.sh      # 1회만: Google 계정 로그인
bash run.sh       # 매번: 앱 실행
```

### 수동 실행

```bash
# 백엔드 (포트 8000)
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000

# 프론트엔드 (포트 5173, 새 터미널)
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173` 접속 → Google Cloud Project ID 입력 → 시작

---

## 3. 환경 설정 (.env)

`backend/` 폴더에 `.env` 파일 생성 (없으면 기본값으로 동작):

```env
# 선택사항 — 앱 UI에서 입력해도 됩니다
GOOGLE_CLOUD_PROJECT_ID=your-project-id

# 안전 한도: 이 금액 초과 시 생성 버튼 비활성화 (기본 $250)
SAFE_LIMIT_USD=250

# Vertex AI 리전 (기본값 그대로 두세요)
GOOGLE_CLOUD_LOCATION=us-central1

# 출력 폴더 경로 (기본값 권장)
OUTPUT_BASE_PATH=./output
```

> **API 키 없음**: 이 프로젝트는 서비스 계정 JSON 키 대신  
> `gcloud auth application-default login` (ADC) 방식으로 인증합니다.  
> AUTH.bat / auth.sh 실행 한 번으로 설정 완료됩니다.

---

## 4. 앱 사용법 (5단계 워크플로)

```
[Step 1] 가사       무료  Gemini 2.5 Flash — 장르/테마 입력 → 가사 자동 생성
[Step 2] 음악 + 스토리   Lyria 3 Pro — 90~120초 AI 작곡 / 스토리보드 생성
[Step 3] 이미지          Nano Banana Pro/2 — 캐릭터 시트 + 씬 이미지 (17가지 스타일)
[Step 4] 영상            Veo 3.1 Fast — 씬별 8초 클립 생성 (코러스 재사용으로 비용 절감)
[Step 5] 최종 편집  무료  FFmpeg — 클립 합성 + 음악 + 자막 자동 합성
```

### 각 단계 상세

**Step 1 — 가사 (무료)**
- 장르 (트롯트·K-POP·발라드 등), 보컬, 악기, 테마 선택
- Gemini 2.5 Flash가 코러스 훅이 강한 가사를 자동 생성
- 섹션(인트로/벌스/코러스/아웃트로)별 개별 수정 가능

**Step 2 — 음악 + 스토리**
- Lyria 3 Pro로 90~120초 분량의 AI 음악 생성 (또는 직접 파일 업로드)
- Gemini가 가사를 분석해 기승전결 스토리보드 10개 씬 자동 구성
- 코러스 씬은 첫 번째만 생성 후 재사용 → 비용 절감

**Step 3 — 이미지 (17가지 스타일)**
- 한국웹툰시트, 시네마틱판타지, 지브리, 픽사3D, 일본애니 등
- 아트디렉터급 상세 프롬프트로 표정 6종 + 4방향 + 의상 3~4종 캐릭터 시트 생성
- 씬 이미지는 캐릭터 시트를 레퍼런스로 일관성 유지

**Step 4 — 영상**
- Veo 3.1 Fast로 씬당 8초 클립 생성
- 코러스 반복 등장 시 첫 클립을 복사 (Veo 호출 없음, 비용 $0)
- 안전 필터 차단 시 자동 순화 3단계 재시도

**Step 5 — 최종 편집 (무료)**
- FFmpeg으로 클립 자동 concat
- 영상 길이를 음악 길이에 정확히 맞춤 (패딩 또는 속도 미세 조정)
- 자막 스타일 5종 선택, 코러스 구간 금색 자막 강조
- MP4 다운로드 또는 CapCut 프로젝트 내보내기

---

## 5. 비용 안내

뮤직비디오 1편 기준 (10개 씬, 90~120초 음악):

| 단계 | 모델 | 예상 비용 |
|------|------|-----------|
| 가사 · 스토리 생성 | Gemini 2.5 Flash | **무료** |
| 음악 생성 (90~120초) | Lyria 3 Pro | ~$0.08 |
| 캐릭터 시트 3종 (4K) | Nano Banana Pro | ~$0.40 |
| 씬 이미지 10장 | Nano Banana Pro/2 | ~$0.70~$1.34 |
| 영상 클립 (7개 신규 × 8초) | Veo 3.1 Fast | ~$8.40 |
| 최종 편집 (FFmpeg) | — | **무료** |
| **합계** | | **약 $9.6~$10.2/편** |

> - 코러스 씬 3개는 복사 재사용으로 Veo 비용 $0  
> - $300 무료 크레딧으로 약 **29~31편** 제작 가능  
> - 앱 안전 한도 기본 $250 (`SAFE_LIMIT_USD`로 조정 가능)

---

## 6. 청구 방지 안내

**반드시 읽어주세요**

1. [console.cloud.google.com](https://console.cloud.google.com) 신규 가입 시 **$300 무료 크레딧 자동 제공**
2. **"유료 계정으로 업그레이드" 절대 클릭 금지**  
   클릭 시 크레딧 소진 후 자동 청구될 수 있습니다
3. $300 소진 또는 90일 경과 시 **자동 정지** (미업그레이드 시 청구 없음)
4. 앱 내 실시간 비용 추적기가 모든 호출 비용을 표시합니다
5. 안전 한도($250) 초과 시 모든 생성 버튼이 자동 비활성화됩니다

---

## 7. 기술 스택

| 영역 | 기술 |
|------|------|
| 백엔드 | Python 3.10 + FastAPI + SSE 스트리밍 |
| 프론트엔드 | React 18 + Vite + Tailwind CSS + Zustand |
| AI — 텍스트/스토리 | Google Vertex AI Gemini 2.5 Flash |
| AI — 음악 | Lyria 3 Pro (Vertex AI v1beta1) |
| AI — 이미지 | Nano Banana Pro (`gemini-3-pro-image-preview`) |
| AI — 영상 | Veo 3.1 Fast (`veo-3.1-fast-generate-001`) |
| 미디어 처리 | FFmpeg (concat · 자막 · 길이 맞춤) |
| 인증 | Google ADC (Application Default Credentials) |

---

## 8. 프로젝트 구조

```
mv-generator/
├── RUN.bat / run.sh          # 원클릭 실행
├── AUTH.bat / auth.sh        # 구글 로그인 (최초 1회)
├── INSTALL.bat / install.sh  # 패키지 설치 (최초 1회)
├── STOP.bat / stop.sh        # 서버 종료
│
├── backend/
│   ├── main.py               # FastAPI 앱 진입점
│   ├── config.py             # 프로젝트 설정 + 경로 헬퍼
│   ├── requirements.txt
│   ├── routes/
│   │   ├── setup.py          # Google Cloud 연결 검증
│   │   ├── lyrics.py         # 가사 생성/수정
│   │   ├── story.py          # 스토리보드 생성
│   │   ├── music.py          # Lyria 음악 생성
│   │   ├── images.py         # 이미지 생성 (캐릭터 시트 + 씬)
│   │   ├── video.py          # Veo 영상 클립 생성
│   │   └── final.py          # 최종 합성 (concat + 음악 + 자막)
│   ├── services/
│   │   ├── image_service.py  # Nano Banana Pro/2 이미지 생성
│   │   ├── lyria_service.py  # Lyria 3 Pro 음악 생성
│   │   ├── gemini_service.py # Gemini 텍스트 생성
│   │   └── capcut_service.py # CapCut 프로젝트 내보내기
│   └── utils/
│       ├── prompt_builder.py # 아트디렉터급 스타일별 프롬프트
│       ├── subtitle.py       # SRT/ASS 자막 생성 + 음악 동기화
│       ├── audio.py          # 오디오 길이/BPM 분석
│       └── cost_guard.py     # 비용 추적 + 안전 한도
│
├── frontend/
│   └── src/
│       ├── components/steps/ # Step1~Step5 UI
│       ├── components/ui/    # 공통 UI 컴포넌트
│       └── store/            # Zustand 상태 관리
│
└── output/                   # 생성물 저장 (자동 생성)
    └── proj_YYYYMMDD_HHMMSS_xxxx/
        ├── 01_lyrics/        # 가사 · 스토리
        ├── 02_music/         # 음악 파일 + 메타
        ├── 03_characters/    # 캐릭터 시트
        ├── 04_images/        # 씬 이미지
        ├── 05_clips/         # 영상 클립
        ├── 06_subtitles/     # SRT · ASS 자막
        └── 07_final/         # 최종 MV + CapCut 패키지
```

---

## 9. 문제 해결

### `gcloud: command not found`
Google Cloud CLI가 설치되지 않았거나 PATH에 없습니다.  
→ [설치 가이드](https://cloud.google.com/sdk/docs/install) 참고 후 터미널 재시작

### `ffmpeg: command not found`
FFmpeg이 PATH에 등록되지 않았습니다.  
→ [ffmpeg.org](https://ffmpeg.org/download.html) 에서 다운로드 후 시스템 PATH 추가

### `Could not automatically determine credentials` (인증 오류)
ADC 인증이 만료됐거나 설정되지 않았습니다.  
→ `AUTH.bat` (Windows) 또는 `bash auth.sh` (Mac/Linux) 재실행

### `SERVICE_DISABLED: Vertex AI API has not been used`
Vertex AI API가 비활성화 상태입니다.  
→ AUTH.bat 마지막 단계에서 자동 활성화됩니다. 또는:
```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

### `npm` 실행 후 배치 파일이 종료됨 (Windows)
`call npm` 형태로 호출해야 합니다. RUN.bat / INSTALL.bat 은 이미 수정되어 있습니다.

### 영상 생성이 안전 필터에 차단됨
폭력·선정적 표현이 포함된 가사나 스토리를 수정하거나,  
Step 4에서 해당 씬만 재생성하면 자동 순화 3단계를 거쳐 재시도합니다.

### 최종 영상 길이가 음악보다 짧음
이미 자동 보정됩니다. Step 5에서 FFmpeg이 마지막 프레임을 정지 연장(tpad)하거나  
속도를 미세 조정해 음악 길이에 맞춥니다.
