# 🚁 MV Generator — AI 뮤직비디오 메이커

> **스토리 → 가사 → 음악 → 이미지 → 영상** 전 과정 자동화  
> Google Cloud Vertex AI + $300 무료 크레딧으로 동작

---

## ⚠️ 청구 방지 안내 (반드시 읽기)

1. [console.cloud.google.com](https://console.cloud.google.com) 신규가입 → **$300 무료체험 자동 제공**
2. ⛔ **"유료 계정으로 업그레이드" 절대 클릭 금지**  
   → 클릭 시 크레딧 소진 후 자동 청구될 수 있습니다
3. $300 소진 또는 90일 경과 시 **자동 정지** (청구되지 않음)
4. 앱 안전한도 기본 **$250** (`backend/.env`의 `SAFE_LIMIT_USD`로 조정)
5. 앱 내 비용 추적기가 항상 실시간 사용액을 표시합니다

---

## 인증 설정 (JSON 키 대신 ADC 사용)

서비스 계정 JSON 키 없이 `gcloud` CLI 로그인만으로 인증합니다.

```bash
# 1. Google Cloud CLI 설치
#    https://cloud.google.com/sdk/docs/install

# 2. 로그인
gcloud auth application-default login

# 3. 프로젝트 지정 (YOUR_PROJECT_ID를 실제 ID로 교체)
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 4. Vertex AI API 활성화 (처음 한 번)
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

---

## 실행 방법

### 사전 준비
- Python 3.10+
- Node.js 18+
- FFmpeg (시스템에 설치 필요: [ffmpeg.org](https://ffmpeg.org))
- Google Cloud 계정 + gcloud CLI 로그인 (위 인증 설정 참고)

### 백엔드
```bash
cd mv-generator/backend
cp ../.env.example .env
# .env에 API 키 입력
pip install -r requirements.txt
python main.py
# 또는: uvicorn main:app --reload --port 8000
```

### 프론트엔드
```bash
cd mv-generator/frontend
npm install
npm run dev
```

### 접속
- 브라우저에서 `http://localhost:5173` 접속
- API 키 입력 후 제작 시작

---

## 비용 (편당, $300 크레딧에서 차감)

| 단계 | 모델 | 비용 |
|------|------|------|
| 가사 생성 | Gemini 2.5 Flash | **무료** |
| 음악 생성 | Lyria 3 Pro | ~$0.08/곡 |
| 이미지 생성 (10장) | Imagen 3 Fast | ~$0.70 |
| 영상 생성 (80초) | Veo 3.1 Fast | ~$12.00 |
| 최종 편집 | FFmpeg | **무료** |
| **합계** | | **~$12.78/편** |

> $300 무료 크레딧으로 약 **23편** 제작 가능

---

## 기능 개요

### Step 1 — 가사 (FREE)
- 장르/보컬/악기/테마 설정
- Gemini 2.5 Flash로 코러스 훅 강화 가사 자동 생성
- 섹션별 수정 가능

### Step 2 — 음악
- Lyria 3 Pro AI 작곡 또는 파일 업로드
- SSE 실시간 진행 상황 표시
- 비용 게이트 (확인 후 실행)

### Step 3 — 이미지
- 15가지 시각 스타일 선택
- 캐릭터 시트로 일관성 보장
- API 자동생성 또는 수동 업로드

### Step 4 — 영상
- Veo 3.1 Fast로 씬별 영상 생성
- 씬 단위 재생성 가능

### Step 5 — 최종
- FFmpeg 자동 합성 (무료)
- 자막 스타일 5종, 전환 효과 선택
- 코러스 자막 금색 강조

---

## 안전장치

- **세션 비용 추적기**: 모든 API 호출 전 비용 계산 및 누적 표시
- **비용 게이트**: 유료 작업 전 "예상 비용 $X · 진행하시겠습니까?" 확인 모달
- **안전 한도**: $250 초과 시 모든 생성 버튼 비활성화
- **경고 배너**: 한도 90% 도달 시 노랑 → 빨강 색상 변화

---

## 환경변수 (.env)

```env
GEMINI_API_KEY=AIzaSy...
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
SAFE_LIMIT_USD=250
OUTPUT_BASE_PATH=./output
```
