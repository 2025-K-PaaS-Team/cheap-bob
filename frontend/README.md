#  CheapBob Frontend


## 🚀 기술 스택

| 분류                   | 사용 기술                                 |
| -------------------- | ------------------------------------- |
| **Framework**        | React 18+, Vite 5, TypeScript         |
| **Styling**          | TailwindCSS, CSS Modules              |
| **State Management** | React Context API                     |
| **Routing**          | React Router v6                       |
| **API 통신**           | Axios                                 |
| **Auth**             | OAuth 2.0 (Naver, Google, Kakao), JWT |
| **Build**            | pnpm, Vite, ESLint, Prettier          |
| **Deploy**           | Vercel / Naver Cloud (Docker 기반 배포)   |

---

## 🧩 프로젝트 구조

```
frontend/
├── src/
│   ├── assets/               # 정적 리소스 및 데이터
│   │   └── information.json
│   │
│   ├── components/           # 재사용 가능한 UI 컴포넌트
│   │   ├── common/           # 공용 컴포넌트
│   │   │   ├── CommonBtn.tsx, CommonModal.tsx, CommonToast.tsx ...
│   │   │   ├── home/         # 홈 화면 전용
│   │   │   └── index.ts
│   │   ├── customer/         # 고객용 UI (회원가입, 주문, 매장리스트 등)
│   │   ├── seller/           # 판매자용 UI (대시보드, 주문관리 등)
│   │   ├── layouts/          # Header, Footer, Wrapper 등 공통 레이아웃
│   │   └── Payment/          # 결제 전용 컴포넌트
│   │
│   ├── constant/             # 상수 및 옵션 정의
│   │   ├── layout.ts, signup.ts, order.ts ...
│   │   └── station.ts, time.ts 등
│   │
│   ├── context/              # 전역 상태 관리 (Toast 등)
│   │   └── ToastContext.tsx
│   │
│   ├── interface/            # TypeScript 인터페이스
│   │   ├── common/           # 공용 타입(auth, store, product 등)
│   │   ├── customer/         # 고객 관련 타입
│   │   ├── seller/           # 판매자 관련 타입
│   │   └── payment/          # 결제 타입
│   │
│   ├── pages/                # 페이지 라우트 구성
│   │   ├── Common/           # 공통 문서/콜백/탈퇴 등
│   │   ├── Customer/         # 고객용 메인, 주문, 마이페이지 등
│   │   ├── Seller/           # 판매자용 대시보드, 정산, 주문 등
│   │   └── index.ts
│   │
│   ├── services/             # API 호출 모듈
│   │   ├── common/auth.ts    # 로그인/토큰
│   │   ├── customer/         # 주문, 결제, 검색, 회원가입 등
│   │   ├── seller/           # 상품, 주문, 정산, 탈퇴 등
│   │   └── client.ts         # Axios 인스턴스 정의
│   │
│   ├── store/                # 프론트엔드 상태 저장소
│   │   ├── seller/           # 판매자 상태 (가입, 대시보드 등)
│   │   └── index.ts
│   │
│   ├── utils/                # 유틸리티 함수
│   │   ├── formatDate.ts, validation.ts, roundCalculater.ts 등
│   │   └── getLayoutByPath.ts, getTitleByKey.ts 등
│   │
│   ├── App.tsx               # 라우트 및 전역 Provider 설정
│   ├── main.tsx              # React 진입점
│   ├── index.css             # 글로벌 스타일
│   └── vite-env.d.ts         # Vite 타입 선언
│
├── .env                      # 환경 변수
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
└── vite.config.ts
```

---

## ⚙️ 주요 기능

| 기능               | 설명                                  |
| ---------------- | ----------------------------------- |
| 🧍‍♀️ **고객 모드**  | 매장 검색, 랜덤팩 구매, 결제, 픽업 QR 인증         |
| 🧑‍🍳 **판매자 모드** | 가게 등록, 영업시간 설정, 주문 관리, 정산 조회        |
| 🔐 **OAuth 로그인** | Naver / Google / Kakao 로그인 후 JWT 발급 |
| 💳 **결제 연동**     | PortOne(아임포트) 기반 카드 결제 및 취소 처리      |
| 🕒 **주문 상태 관리**  | 예약 → 수락 → 완료/취소 실시간 반영              |
| 📢 **알림 시스템**    | 주문/취소/픽업 등 Toast 및 이메일 알림 표시        |
| 📦 **자동화 UI 흐름** | 스케줄러에 따라 상태 변경 시 UI 자동 업데이트         |

---

## 🔑 환경 변수

### `.env`

```env
VITE_API_BASE_URL=_your_api_base_url
VITE_NAVER_CLIENT_ID=your_naver_client_id
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_KAKAO_CLIENT_ID=your_kakao_client_id
VITE_MAP_CLIENT_ID=your_naver_map_key
VITE_PORTONE_KEY=your_portone_key
```

---

## 🧠 라우팅 구조

| 구분             | 주요 페이지    |
| -------------- | --------- |
| `/`            | 홈 화면      |
| `/login`       | 로그인 선택 화면 |
| `/c`           | 고객 홈      |
| `/c/signup`    | 고객 회원가입   |
| `/c/store/:id` | 매장 상세     |
| `/c/order/:id` | 주문 상세     |
| `/c/my`        | 마이페이지     |
| `/s`           | 판매자 홈     |
| `/s/signup`    | 판매자 회원가입  |
| `/s/dashboard` | 판매자 대시보드  |
| `/s/order`     | 판매자 주문 관리 |
| `/s/billing`   | 판매자 정산 관리 |

---

## 🪄 실행 방법

### 1. 의존성 설치

```bash
pnpm install
```

### 2. 개발 서버 실행

```bash
pnpm dev
# https://localhost:5173
```

### 3. 프로덕션 빌드

```bash
pnpm build
pnpm preview
# https://localhost:5173
```

---

## 🧩 상태 관리

* **ToastContext** : 전역 알림 상태 관리
* **store/seller** : 판매자 가입 단계/입력 상태 저장
* **Axios Interceptor** : JWT 자동 첨부 및 만료 시 로그아웃 처리

---

## 🧭 개발 가이드라인

* 컴포넌트 네이밍: `PascalCase`
* 파일 확장자: `.tsx`, `.ts`
* API 호출은 `services/` 내부에서만 수행
* 페이지별 Layout 지정: `getLayoutByPath` 유틸 활용
* 공통 스타일 및 컬러는 `Tailwind config` 기반

---

## 📦 빌드 구조

| 폴더           | 내용          |
| ------------ | ----------- |
| `dist/`      | Vite 빌드 산출물 |
| `assets/`    | 번들링된 정적 파일  |
| `index.html` | SPA 진입점     |

---