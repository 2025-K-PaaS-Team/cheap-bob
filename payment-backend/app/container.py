from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dependency_injector import containers, providers

from app.domain.payment.service.store_payment_info import StorePaymentInfoService
from app.domain.payment.service.seller_payment_settings import (
    SellerPaymentSettingsService,
)
from app.domain.payment.service.payment_gateway import PaymentGatewayService
from app.domain.payment.service.customer_payment import CustomerPaymentService
from app.domain.payment.service.cart_item import CartItemService
from app.domain.payment.event.seller_withdrawn import (
    SellerStoreWithdrawnEventHandler,
)
from app.database.session import UnitOfWork
from app.core.portone import PortOnePaymentClient
from app.core.outbox.relay import OutboxRelay
from app.core.kafka.producer import KafkaProducer
from app.core.kafka.consumer import KafkaConsumerRunner
from app.core.internal_client.seller import InternalSellerClient
from app.core.internal_client.order import InternalOrderClient
from app.core.auth import JwtService
from app.config.setting import settings


class Container(containers.DeclarativeContainer):
    """payment-backend DI 컨테이너."""

    # ───────── infra ─────────

    engine = providers.Singleton(
        create_async_engine,
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True,
    )

    session_factory = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    uow = providers.Factory(UnitOfWork, session=session_factory)

    # ───────── auth ─────────

    jwt_service = providers.Singleton(JwtService)

    # ───────── internal HTTP clients ─────────

    internal_seller_client = providers.Singleton(InternalSellerClient)
    internal_order_client = providers.Singleton(InternalOrderClient)

    # ───────── Kafka / Outbox ─────────
    kafka_producer = providers.Singleton(KafkaProducer)
    outbox_relay = providers.Singleton(
        OutboxRelay, uow=uow, producer=kafka_producer,
    )
    kafka_consumer_runner = providers.Singleton(KafkaConsumerRunner)

    # ───────── payment ─────────

    portone_client = providers.Singleton(PortOnePaymentClient)

    store_payment_info_service = providers.Factory(
        StorePaymentInfoService, uow=uow,
    )
    payment_gateway_service = providers.Singleton(
        PaymentGatewayService, portone_client=portone_client,
    )
    seller_payment_settings_service = providers.Factory(
        SellerPaymentSettingsService,
        store_payment_info_service=store_payment_info_service,
    )
    cart_item_service = providers.Factory(CartItemService, uow=uow)

    customer_payment_service = providers.Factory(
        CustomerPaymentService,
        uow=uow,
        store_payment_info_service=store_payment_info_service,
        payment_gateway_service=payment_gateway_service,
        cart_item_service=cart_item_service,
        internal_seller_client=internal_seller_client,
        internal_order_client=internal_order_client,
    )

    # ───────── 이벤트 핸들러 ─────────
    # main.py lifespan 에서 instance().handle 을 KafkaConsumerRunner.register 에 등록.
    seller_store_withdrawn_event_handler = providers.Factory(
        SellerStoreWithdrawnEventHandler,
        uow=uow,
        store_payment_info_service=store_payment_info_service,
    )


container = Container()
