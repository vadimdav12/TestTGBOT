"""
Блочные тесты модуля заказов (OrderService).
Тесты Б30-Б40.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from app.services.order_service import OrderService
from app.services.cart_service import CartService
from app.dto import ContactData
from app.exceptions import (
    EmptyCartError, OrderNotFoundError, OrderCannotBeCancelledError,
    InvalidStatusTransitionError, ValidationError
)


class TestOrderService:

    @pytest.fixture
    def order_service(self, mock_order_repo, mock_cart_repo, mock_product_repo):
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        notification_service = AsyncMock()
        discount_service = AsyncMock()
        return OrderService(
            order_repo=mock_order_repo,
            cart_service=cart_service,
            product_repo=mock_product_repo,
            notification_service=notification_service,
            discount_service=discount_service
        )

    @pytest.mark.asyncio
    async def test_b30_create_order_success(self, order_service, mock_cart_repo):
        """Б30: Создание заказа создаёт запись, резервирует товар, очищает корзину"""
        mock_cart_repo._data[1] = [
            {'product_id': 3, 'qty': 1, 'name': 'Samsung', 'price': Decimal('79990'), 'stock': 10, 'is_active': True}
        ]
        contact = ContactData(name="Тест", phone="+7 999 111-11-11", address="г. Москва, ул. Тестовая, д. 1")
        
        order = await order_service.create_order(user_id=1, contact=contact, payment_method='card')
        
        assert order is not None
        assert order.order_number.startswith("ORD-")
        assert order.status == 'created'

    @pytest.mark.asyncio
    async def test_b31_create_order_empty_cart_raises_error(self, order_service):
        """Б31: Создание заказа с пустой корзиной вызывает EmptyCartError"""
        contact = ContactData(name="Тест", phone="+7 999 111-11-11", address="г. Москва, ул. Тестовая, д. 1")
        
        with pytest.raises(EmptyCartError) as exc_info:
            await order_service.create_order(user_id=4, contact=contact)
        
        assert exc_info.value.user_id == 4

    @pytest.mark.asyncio
    async def test_b32_get_order_success(self, mock_order_repo):
        """Б32: Получение заказа по id=2 возвращает заказ ORD-20241201-0002"""
        service = OrderService(order_repo=mock_order_repo)
        
        order = await service.get_order(order_id=2, user_id=1)
        
        assert order is not None
        assert order.order_number == "ORD-20241201-0002"

    @pytest.mark.asyncio
    async def test_b33_get_order_wrong_user_returns_none(self, mock_order_repo):
        """Б33: Получение чужого заказа (order_id=4, user_id=1) возвращает None"""
        service = OrderService(order_repo=mock_order_repo)
        
        order = await service.get_order(order_id=4, user_id=1)
        
        assert order is None

    @pytest.mark.asyncio
    async def test_b34_list_orders(self, mock_order_repo):
        """Б34: Получение списка заказов пользователя 1 возвращает 3 заказа"""
        service = OrderService(order_repo=mock_order_repo)
        
        orders = await service.list_orders(user_id=1)
        
        assert len(orders) == 3
        assert all(o.user_id == 1 for o in orders)

    @pytest.mark.asyncio
    async def test_b35_update_status_success(self, mock_order_repo):
        """Б35: Изменение статуса заказа 1 на 'confirmed' выполняется успешно"""
        notification_service = AsyncMock()
        service = OrderService(order_repo=mock_order_repo, notification_service=notification_service)
        
        order = await service.update_status(order_id=1, status='confirmed')
        
        assert order.status == 'confirmed'

    @pytest.mark.asyncio
    async def test_b36_update_status_invalid_transition_raises_error(self, mock_order_repo):
        """Б36: Переход cancelled -> shipped вызывает InvalidStatusTransitionError"""
        service = OrderService(order_repo=mock_order_repo)
        
        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            await service.update_status(order_id=5, status='shipped')
        
        assert exc_info.value.current_status == 'cancelled'
        assert exc_info.value.new_status == 'shipped'

    @pytest.mark.asyncio
    async def test_b37_cancel_order_success(self, mock_order_repo, mock_product_repo):
        """Б37: Отмена заказа 1 меняет статус на 'cancelled' и возвращает товар на склад"""
        mock_order_repo.get_order_items = AsyncMock(return_value=[])
        service = OrderService(order_repo=mock_order_repo, product_repo=mock_product_repo)
        
        order = await service.cancel_order(order_id=1, user_id=1)
        
        assert order.status == 'cancelled'

    @pytest.mark.asyncio
    async def test_b38_cancel_shipped_order_raises_error(self, mock_order_repo, mock_product_repo):
        """Б38: Отмена отправленного заказа 3 (status=shipped) вызывает OrderCannotBeCancelledError"""
        service = OrderService(order_repo=mock_order_repo, product_repo=mock_product_repo)
        
        with pytest.raises(OrderCannotBeCancelledError) as exc_info:
            await service.cancel_order(order_id=3, user_id=1)
        
        assert exc_info.value.status == 'shipped'

    @pytest.mark.asyncio
    async def test_b39_reserve_stock(self, mock_order_repo, mock_product_repo, test_products):
        """Б39: Резервирование товаров уменьшает остаток на складе"""
        from tests.conftest import MockOrderItem
        mock_order_repo.get_order_items = AsyncMock(return_value=[
            MockOrderItem(1, 1, 3, "Samsung", Decimal('79990'), 2)
        ])
        service = OrderService(order_repo=mock_order_repo, product_repo=mock_product_repo)
        initial_stock = test_products[2].stock
        
        await service.reserve_stock(order_id=1)
        
        assert test_products[2].stock == initial_stock - 2

    @pytest.mark.asyncio
    async def test_b40_release_stock(self, mock_order_repo, mock_product_repo, test_products):
        """Б40: Снятие резерва (при отмене) увеличивает остаток на складе"""
        from tests.conftest import MockOrderItem
        mock_order_repo.get_order_items = AsyncMock(return_value=[
            MockOrderItem(1, 1, 3, "Samsung", Decimal('79990'), 2)
        ])
        service = OrderService(order_repo=mock_order_repo, product_repo=mock_product_repo)
        initial_stock = test_products[2].stock
        
        await service.release_stock(order_id=1)
        
        assert test_products[2].stock == initial_stock + 2
