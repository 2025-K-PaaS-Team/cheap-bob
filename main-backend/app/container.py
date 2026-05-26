from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dependency_injector import containers, providers

from app.domain.seller.service.seller_withdraw import SellerWithdrawService
from app.domain.seller.service.seller_store_sns import SellerStoreSNSService
from app.domain.seller.service.seller_store_settings import SellerStoreSettingsService
from app.domain.seller.service.seller_store_register import SellerStoreRegisterService
from app.domain.seller.service.seller_store_read import SellerStoreReadService
from app.domain.seller.service.seller_store_profile import SellerStoreProfileService
from app.domain.seller.service.seller_store_image import SellerStoreImageService
from app.domain.seller.service.seller_store_close import SellerStoreCloseService
from app.domain.seller.service.seller_settlement import SellerSettlementService
from app.domain.seller.service.seller_registration_status import (
    SellerRegistrationStatusService,
)
from app.domain.seller.service.stock_idempotency import StockIdempotencyService
from app.domain.seller.service.seller_product import SellerProductService
from app.domain.seller.service.seller_account import SellerAccountService
from app.domain.seller.repository.seller_withdraw_reservation import (
    SellerWithdrawReservationRepository,
)
from app.domain.order.service.seller_order import SellerOrderService
from app.domain.order.service.product_stock_reservation import (
    ProductStockReservationService,
)
from app.domain.order.service.order_query import OrderQueryService
from app.domain.order.service.customer_order import CustomerOrderService
from app.domain.order.repository.product_stock_reservation import (
    ProductStockReservationRepository,
)
from app.domain.order.repository.order_history_item import OrderHistoryItemRepository
from app.domain.customer.service.preference_option import PreferenceOptionService
from app.domain.customer.service.customer_withdraw import CustomerWithdrawService
from app.domain.customer.service.customer_search import CustomerSearchService
from app.domain.customer.service.customer_registration_status import (
    CustomerRegistrationStatusService,
)
from app.domain.customer.service.customer_register import CustomerRegisterService
from app.domain.customer.service.customer_profile import CustomerProfileService
from app.domain.customer.service.customer_preference import CustomerPreferenceService
from app.domain.customer.service.customer_history import CustomerHistoryService
from app.domain.customer.service.customer_favorite import CustomerFavoriteService
from app.domain.customer.service.customer_detail import CustomerDetailService
from app.domain.customer.service.customer_account import CustomerAccountService
from app.domain.customer.repository.customer_withdraw_reservation import (
    CustomerWithdrawReservationRepository,
)
from app.domain.auth.service.registration_status import RegistrationStatusService
from app.domain.auth.service.oauth import OAuthService
from app.domain.auth.service.jwt import JwtService
from app.database.session import UnitOfWork
from app.core.internal_client.payment import InternalPaymentClient
from app.config.setting import settings


class Container(containers.DeclarativeContainer):
    """DI 컨테이너. payment 도메인은 MSA 분리되어 InternalPaymentClient 로 호출."""

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

    # ───────── account services (auth 가 사용하므로 auth 위에 둠) ─────────

    customer_account_service = providers.Factory(CustomerAccountService, uow=uow)
    seller_account_service = providers.Factory(SellerAccountService, uow=uow)

    oauth_service = providers.Factory(
        OAuthService,
        jwt_service=jwt_service,
        customer_account_service=customer_account_service,
        seller_account_service=seller_account_service,
    )

    # ───────── internal payment client (MSA 호출) ─────────

    internal_payment_client = providers.Singleton(InternalPaymentClient)

    # ───────── seller ─────────

    seller_withdraw_reservation_repository = providers.Singleton(
        SellerWithdrawReservationRepository,
    )

    seller_store_read_service = providers.Factory(SellerStoreReadService, uow=uow)
    seller_store_register_service = providers.Factory(
        SellerStoreRegisterService, uow=uow,
    )
    seller_store_profile_service = providers.Factory(
        SellerStoreProfileService, uow=uow,
    )
    seller_store_sns_service = providers.Factory(SellerStoreSNSService, uow=uow)
    seller_store_image_service = providers.Factory(SellerStoreImageService, uow=uow)
    seller_registration_status_service = providers.Factory(
        SellerRegistrationStatusService, uow=uow,
    )

    # ───────── order ─────────

    order_history_item_repository = providers.Singleton(OrderHistoryItemRepository)
    product_stock_reservation_repository = providers.Singleton(
        ProductStockReservationRepository,
    )

    order_query_service = providers.Factory(
        OrderQueryService, uow=uow, history_repo=order_history_item_repository,
    )
    product_stock_reservation_service = providers.Factory(
        ProductStockReservationService,
        reservation_repo=product_stock_reservation_repository,
    )
    seller_product_service = providers.Factory(
        SellerProductService,
        uow=uow,
        product_stock_reservation_service=product_stock_reservation_service,
    )

    # ───────── stock idempotency (payment-backend internal call dedupe) ─────────

    stock_idempotency_service = providers.Factory(
        StockIdempotencyService,
        uow=uow,
        seller_product_service=seller_product_service,
    )

    # ───────── seller (settings/withdraw) — payment-backend 호출 ─────────

    seller_store_settings_service = providers.Factory(
        SellerStoreSettingsService,
        uow=uow,
        internal_payment_client=internal_payment_client,
    )
    seller_withdraw_service = providers.Factory(
        SellerWithdrawService,
        uow=uow,
        withdraw_repo=seller_withdraw_reservation_repository,
        seller_account_service=seller_account_service,
        internal_payment_client=internal_payment_client,
    )

    # ───────── order — payment-backend 호출 ─────────

    customer_order_service = providers.Factory(
        CustomerOrderService,
        uow=uow,
        history_repo=order_history_item_repository,
        seller_store_read_service=seller_store_read_service,
        seller_store_image_service=seller_store_image_service,
        seller_product_service=seller_product_service,
        internal_payment_client=internal_payment_client,
    )
    seller_order_service = providers.Factory(
        SellerOrderService,
        uow=uow,
        history_repo=order_history_item_repository,
        seller_store_read_service=seller_store_read_service,
        seller_product_service=seller_product_service,
        order_query_service=order_query_service,
        internal_payment_client=internal_payment_client,
    )

    # ───────── seller — order/payment 의존 서비스 ─────────

    seller_store_close_service = providers.Factory(
        SellerStoreCloseService,
        uow=uow,
        order_query_service=order_query_service,
        seller_product_service=seller_product_service,
        internal_payment_client=internal_payment_client,
    )
    seller_settlement_service = providers.Factory(
        SellerSettlementService,
        uow=uow,
        order_query_service=order_query_service,
    )

    # ───────── customer ─────────

    customer_withdraw_reservation_repository = providers.Singleton(
        CustomerWithdrawReservationRepository,
    )

    customer_register_service = providers.Factory(CustomerRegisterService, uow=uow)
    customer_profile_service = providers.Factory(CustomerProfileService, uow=uow)
    customer_detail_service = providers.Factory(CustomerDetailService, uow=uow)
    customer_preference_service = providers.Factory(CustomerPreferenceService, uow=uow)
    customer_withdraw_service = providers.Factory(
        CustomerWithdrawService,
        uow=uow,
        withdraw_repo=customer_withdraw_reservation_repository,
        order_query_service=order_query_service,
        customer_account_service=customer_account_service,
    )
    customer_history_service = providers.Singleton(CustomerHistoryService)
    customer_favorite_service = providers.Factory(
        CustomerFavoriteService,
        uow=uow,
        seller_store_read_service=seller_store_read_service,
    )
    customer_search_service = providers.Factory(
        CustomerSearchService,
        uow=uow,
        seller_store_read_service=seller_store_read_service,
    )
    customer_registration_status_service = providers.Factory(
        CustomerRegistrationStatusService, uow=uow,
    )
    preference_option_service = providers.Singleton(PreferenceOptionService)

    # ───────── auth.registration_status ─────────

    registration_status_service = providers.Factory(
        RegistrationStatusService,
        customer_registration_status_service=customer_registration_status_service,
        seller_registration_status_service=seller_registration_status_service,
    )


container = Container()
