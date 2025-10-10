# CheapBob Backend

## 기술 스택

- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Databases**:
  - PostgreSQL (주 데이터베이스) - SQLAlchemy ORM
  - MongoDB (주문 이력, 탈퇴 예약 데이터) - Beanie ODM
  - Redis (캐싱, 세션 관리)
- **Authentication**: JWT + OAuth 2.0 (Google, Kakao, Naver)
- **Task Scheduler**: APScheduler
- **Database Migration**: Alembic
- **Object Storage**: AWS S3 compatible

## 프로젝트 구조

```
backend/
├── alembic/                    # 데이터베이스 마이그레이션
│   ├── versions/               # 마이그레이션 버전 파일들
│   └── env.py                  # Alembic 환경 설정
│
├── app/                        # 메인 애플리케이션 디렉토리
│   ├── main.py                 # FastAPI 앱 진입점
│   │
│   ├── api/                    # API 엔드포인트
│   │   ├── deps/               # API 의존성 (인증, DB 세션 등)
│   │   └── v1/                 # API 버전 1
│   │       ├── auth/           # 인증 관련 (로그인, OAuth 콜백)
│   │       ├── common/         # 공통 API (인증 불필요)
│   │       ├── customer/       # 고객 전용 API
│   │       ├── seller/         # 판매자 전용 API
│   │       └── test/           # 테스트 API
│   │
│   ├── config/                 # 설정 관련
│   │   ├── settings.py         # 환경변수 설정 (Pydantic Settings)
│   │   └── oauth.py            # OAuth 설정
│   │
│   ├── core/                   # 핵심 유틸리티
│   │   ├── exceptions.py       # 커스텀 예외
│   │   ├── object_storage.py   # S3 스토리지 관리
│   │   ├── portone.py          # 결제 서비스 (PortOne)
│   │   └── redis.py            # Redis 클라이언트
│   │
│   ├── database/               # 데이터베이스 관련
│   │   ├── models/             # SQLAlchemy 모델
│   │   │   ├── customer.py     # 고객 모델
│   │   │   ├── seller.py       # 판매자 모델
│   │   │   ├── store.py        # 가게 모델
│   │   │   ├── product_*.py    # 상품 관련 모델
│   │   │   └── order_*.py      # 주문 관련 모델
│   │   ├── mongodb_models/     # MongoDB 모델 (Beanie)
│   │   │   ├── order_history_item.py      # 오래된 주문 이력
│   │   │   └── *_withdraw_reservation.py   # 탈퇴 예약
│   │   ├── session.py          # PostgreSQL 세션 관리
│   │   └── mongodb_session.py  # MongoDB 세션 관리
│   │
│   ├── middleware/             # 미들웨어
│   │   └── auth.py             # JWT 인증 미들웨어
│   │
│   ├── repositories/           # 데이터 접근 레이어
│   │   ├── base.py             # 기본 Repository (CRUD 제공)
│   │   ├── mongodb_base.py     # MongoDB 기본 Repository
│   │   └── *.py                # 각 모델별 Repository
│   │
│   ├── schemas/                # Pydantic 스키마 (Request/Response)
│   │   ├── auth.py             # 인증 스키마
│   │   ├── customer_*.py       # 고객 관련 스키마
│   │   ├── store*.py           # 가게 관련 스키마
│   │   └── *.py                # 기타 스키마
│   │
│   ├── services/               # 비즈니스 로직 레이어
│   │   ├── auth/               # 인증 서비스
│   │   │   ├── jwt.py          # JWT 토큰 관리
│   │   │   └── oauth_service.py # OAuth 서비스
│   │   ├── oauth/              # OAuth 제공자별 구현
│   │   │   ├── google.py
│   │   │   ├── kakao.py
│   │   │   └── naver.py
│   │   ├── scheduled_tasks/    # 스케줄 작업
│   │   │   ├── auto_cancel_reservation_orders.py  # 예약 자동 취소
│   │   │   ├── auto_complete_orders.py           # 주문 자동 완료
│   │   │   ├── inventory_reset.py                # 재고 리셋
│   │   │   ├── order_migration.py                # 주문 이력 마이그레이션
│   │   │   └── store_operation_status_update.py  # 가게 운영 상태 업데이트
│   │   ├── scheduler.py        # 스케줄러 서비스
│   │   ├── email.py            # 이메일 서비스
│   │   ├── payment.py          # 결제 서비스
│   │   └── redis_cache.py      # Redis 캐시 서비스
│   │
│   └── utils/                  # 유틸리티 함수
│       ├── docs_error.py       # API 문서 에러 예시
│       ├── id_generator.py     # ID 생성기
│       ├── qr_generator.py     # QR 코드 생성
│       └── store_utils.py      # 가게 관련 유틸리티
│
├── pyproject.toml              # 프로젝트 의존성 관리
├── alembic.ini                 # Alembic 설정
└── entrypoint.sh               # Docker 엔트리포인트

```

## 주요 디렉토리 설명

### `/alembic`
- 데이터베이스 스키마 버전 관리
- PostgreSQL 테이블 마이그레이션 스크립트 저장
- 마이그레이션 파일로 변경사항을 명확하게 표시

### `/app/api`
- RESTful API 엔드포인트 정의
- 버전별 API 관리 (현재 v1)
- 사용자 타입별 라우터 분리:
  - `auth/`: OAuth 로그인, JWT 토큰 발급
  - `customer/`: 고객 전용 기능 (주문, 결제, 검색, 프로필 등)
  - `seller/`: 판매자 전용 기능 (가게 관리, 상품 관리, 정산 등)
  - `common/`: 인증 불필요한 공통 API

### `/app/database`
- **models/**: SQLAlchemy ORM 모델 정의
  - 고객, 판매자, 가게, 상품, 주문 등의 엔티티
  - 관계형 데이터베이스 스키마 정의
- **mongodb_models/**: Beanie ODM 모델 정의
  - 주문 이력, 탈퇴 예약 등 NoSQL 데이터

### `/app/repositories`
- Repository 패턴 구현
- `BaseRepository`: 모든 Repository가 상속받는 기본 CRUD 기능
- 각 모델별 커스텀 쿼리 메서드 구현
- 데이터베이스 접근 로직 캡슐화

### `/app/services`
- 비즈니스 로직 구현
- **auth/**: JWT 토큰 생성/검증, OAuth 인증 처리
- **scheduled_tasks/**: 배치 작업 구현
  - 매일 특정 시간에 실행되는 자동화 작업
  - 재고 리셋, 주문 상태 업데이트, 데이터 마이그레이션 등
- 외부 서비스 연동 (이메일, 결제, 객체 스토리지)

### `/app/middleware`
- `JWTAuthMiddleware`: 모든 요청에 대한 JWT 토큰 검증
- 인증이 필요없는 경로 제외 처리

### `/app/schemas`
- Pydantic 모델로 Request/Response 데이터 검증
- API 문서 자동 생성을 위한 스키마 정의
- 타입 안정성 보장

## 아키텍처 패턴

### Layered Architecture
```
API Layer (FastAPI Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Database Layer (PostgreSQL/MongoDB/Redis)
```

### 주요 특징
1. **Repository Pattern**: 데이터 접근 로직을 추상화하여 비즈니스 로직과 분리
2. **Dependency Injection**: FastAPI의 의존성 주입을 활용한 느슨한 결합
3. **Type Safety**: Pydantic과 Python 타입 힌트를 활용한 타입 안정성
4. **Multi-Database**: 용도별 최적화된 데이터베이스 사용
   - PostgreSQL: 트랜잭션이 중요한 주문, 결제 데이터
   - MongoDB: 유연한 스키마가 필요한 이력 데이터
   - Redis: 임시 데이터 캐싱, 세션 관리

## 인증 및 권한

### JWT 기반 인증
- Access Token 기반 인증
- 토큰 자동 갱신 (X-New-Token 헤더)
- Customer/Seller 역할 기반 접근 제어

### OAuth 2.0 지원
- Google, Kakao, Naver 소셜 로그인
- 각 제공자별 전용 구현체
- 통합 OAuth 서비스 레이어

## 배치 작업 (Scheduled Tasks)

APScheduler를 사용한 자동화 작업:
- **재고 리셋**: 매일 상품 재고 초기화
- **주문 자동 취소**: 픽업 시간 경과 시 미수령 주문 자동 취소
- **주문 자동 완료**: 가게 마감 시간에 미처리 주문 자동 완료
- **주문 이력 마이그레이션**: PostgreSQL → MongoDB 이력 이전
- **가게 운영 상태 업데이트**: 운영 시간에 따른 상태 자동 변경
- **사용자 탈퇴 처리**: 예약된 탈퇴 처리

## 환경 설정

`.env` 파일을 통한 환경변수 관리:
```env
# 환경 설정
DEBUG=true
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
FRONTEND_LOCAL_URL=http://localhost:3000

# 데이터베이스
DB_HOST=localhost
DB_PORT=5432
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=cheapbob

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USER=your_user
MONGODB_PASSWORD=your_password
MONGODB_NAME=cheapbob

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_CLIENT_SECRET=your_kakao_client_secret
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# JWT
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-northeast-2
AWS_S3_BUCKET_NAME=cheapbob
AWS_S3_ENDPOINT_URL=https://s3.ap-northeast-2.amazonaws.com

# SMTP
SUPER_ADMIN_SMTP_USER=your_email@example.com
SUPER_ADMIN_SMTP_PASSWORD=your_smtp_password
SUPER_ADMIN_SMTP_EMAIL=your_email@example.com
SUPER_ADMIN_SMTP_HOST=smtp.gmail.com
SUPER_ADMIN_SMTP_PORT=587
SUPER_ADMIN_SMTP_NAME=CheapBob Admin
```

## API 문서
서버 실행 후 다음 URL에서 API 문서 확인 가능:
- Swagger UI: http://localhost:3000/docs