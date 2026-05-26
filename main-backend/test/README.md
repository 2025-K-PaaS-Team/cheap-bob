# 백엔드 테스트 가이드

CheapBob 백엔드의 비즈니스 로직을 **단위 테스트 + 통합 테스트** 2계층으로 검증한다.

| 계층 | 대상 | 의존성 | 실행 속도 |
|---|---|---|---|
| **unit** | Service 로직 | Repository · Session Mock | < 1s |
| **integration** | Service → Repository → PostgreSQL | 실 DB 필요 | 수 초 |

## 실행 방법

`main-backend/` 디렉토리에서:

```bash
# 단위만 (가장 빠름, 외부 의존 없음)
uv run pytest test/unit

# 통합까지
POSTGRES_TEST_URL='postgresql+asyncpg://cheap_bob_user:password@localhost:5432/cheap_bob_test' \
  uv run pytest

# 특정 도메인 / 서비스
uv run pytest test/unit/domain/order/customer_order_service/

# 마커 기반
uv run pytest -m unit
uv run pytest -m integration
```

## 디렉토리 구조

```
main-backend/test/
├── unit/                                # 단위 테스트
│   ├── conftest.py                     # app.database.model 선 import
│   ├── middleware/test_jwt_auth.py
│   └── domain/
│       ├── auth/{jwt,oauth,account}_service/
│       ├── order/{customer_order,seller_order,product_stock_reservation}_service/
│       └── payment/{customer_payment,payment_gateway,seller_payment_settings,store_payment_info}_service/
└── integration/                         # 통합 테스트 (실 DB)
    ├── conftest.py                     # NullPool engine + seed fixtures
    └── domain/
        ├── order/test_order_flow.py
        └── payment/test_payment_flow.py
```

각 서비스 단위 디렉토리는 다음 네 파일로 구성:

- `__init__.py`
- `model_factory.py` — `SimpleNamespace` 기반 도메인 객체 팩토리
- `mock_factory.py` — `UnitOfWork` / `AsyncSession` / Repository Mock 팩토리
- `conftest.py` — 서비스 fixture (`monkeypatch` 로 Repository 클래스 치환) + autouse 카운터 reset
- `test_<service>.py`

## 컨벤션

### 테스트 클래스 네이밍

```python
@pytest.mark.unit
class TestSendRequest:
    """Tests for FriendshipService.send_request."""
```

### 테스트 메서드 네이밍

```python
async def test_{action}_{condition_or_result}(self): ...
```

### AAA 패턴 + Factory + Mock

```python
async def test_accept_updates_status(self, service, order_repo_mock):
    # Arrange
    order = OrderFactory.create(status=OrderStatus.reservation)
    order_repo_mock.get_order_with_relations.return_value = order

    # Act
    result = await service.accept_order(...)

    # Assert
    assert result.status == OrderStatus.accept
    order_repo_mock.update.assert_awaited()
```

### SimpleNamespace 팩토리

SQLAlchemy 모델을 직접 인스턴스화하면 backref 이벤트가 `_sa_instance_state` 를 요구해 에러
가 난다. 단위 테스트에선 `SimpleNamespace` 로 속성만 흉내내는 팩토리를 쓴다.

```python
class OrderFactory:
    _counter = 0
    @classmethod
    def create(cls, *, status=OrderStatus.reservation, ...) -> SimpleNamespace:
        cls._counter += 1
        return SimpleNamespace(payment_id=f"PAY_{cls._counter:04d}", status=status, ...)
```

### `@transactional` 우회

서비스가 `@transactional` 데코레이터를 쓰는 경우, `FakeUnitOfWork` 가 `async with self.uow`
를 만족시키고 `self._session` 에 Mock session 을 채워준다. `monkeypatch.setattr` 로
서비스 모듈 안의 Repository 클래스 를 *lambda session: repo_mock* 로 치환한다.

## 주의사항

1. **SQLAlchemy 매퍼 등록**: `test/unit/conftest.py` 가 `app.database.model` 을 import 해
   모든 ORM 모델을 미리 로드한다. 그렇지 않으면 relationship 문자열 해석 시점에 실패한다.
2. **SimpleNamespace 팩토리**: 단위 테스트에서 SQLAlchemy 모델 인스턴스를 직접 만들지 말
   것. backref 이벤트가 `_sa_instance_state` 를 요구한다.
3. **Mock session 메서드**: 서비스가 `self._session.flush / refresh / begin_nested` 를
   호출하면 Mock 에 세 메서드를 모두 등록해둔다.
4. **Counter reset**: `autouse=True` fixture 로 테스트 간 ID 충돌 방지.
5. **비동기**: `asyncio_mode="auto"` 라 `@pytest.mark.asyncio` 자동 적용.
6. **통합 DB 격리**: 매 테스트마다 drop/create. `NullPool` 사용.
