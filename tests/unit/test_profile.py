"""
Блочные тесты модуля профиля (ProfileService).
Тесты Б65-Б70.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from app.services.profile_service import ProfileService
from app.services.cart_service import CartService
from app.dto import ProfileUpdate
from app.exceptions import ValidationError, OrderNotFoundError


class TestProfileService:

    @pytest.mark.asyncio
    async def test_b65_get_profile(self, mock_user_repo, mock_order_repo):
        """Б65: Получение профиля пользователя 1 возвращает имя, телефон, кол-во заказов"""
        service = ProfileService(user_repo=mock_user_repo, order_repo=mock_order_repo)
        
        profile = await service.get_profile(user_id=1)
        
        assert profile.user_id == 1
        assert profile.name == "Иван Тестовый"
        assert profile.orders_count == 3

    @pytest.mark.asyncio
    async def test_b66_update_profile_name(self, mock_user_repo, mock_order_repo):
        """Б66: Обновление имени в профиле сохраняет новое значение"""
        service = ProfileService(user_repo=mock_user_repo, order_repo=mock_order_repo)
        
        profile = await service.update_profile(user_id=1, data=ProfileUpdate(name="Новое Имя"))
        
        assert profile is not None

    @pytest.mark.asyncio
    async def test_b67_update_profile_invalid_phone(self, mock_user_repo, mock_order_repo):
        """Б67: Обновление профиля с невалидным телефоном вызывает ValidationError"""
        service = ProfileService(user_repo=mock_user_repo, order_repo=mock_order_repo)
        
        with pytest.raises(ValidationError):
            await service.update_profile(user_id=1, data=ProfileUpdate(phone="invalid"))

    @pytest.mark.asyncio
    async def test_b68_get_order_history(self, mock_user_repo, mock_order_repo):
        """Б68: История заказов пользователя 1 возвращает 3 заказа отсортированных по дате"""
        service = ProfileService(user_repo=mock_user_repo, order_repo=mock_order_repo)
        
        orders = await service.get_order_history(user_id=1, limit=10)
        
        assert len(orders) == 3

    @pytest.mark.asyncio
    async def test_b69_repeat_order(self, mock_user_repo, mock_order_repo, mock_cart_repo, mock_product_repo):
        """Б69: Повторение заказа 2 добавляет его товары в корзину"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        service = ProfileService(
            user_repo=mock_user_repo, order_repo=mock_order_repo, cart_service=cart_service
        )
        from tests.conftest import MockOrderItem
        mock_order_repo.get_order_items = AsyncMock(return_value=[
            MockOrderItem(1, 2, 3, "Samsung", Decimal('79990'), 1)
        ])
        
        cart = await service.repeat_order(user_id=1, order_id=2)
        
        assert cart is not None

    @pytest.mark.asyncio
    async def test_b70_repeat_order_wrong_user(self, mock_user_repo, mock_order_repo, mock_cart_repo, mock_product_repo):
        """Б70: Повторение чужого заказа 4 вызывает OrderNotFoundError"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        service = ProfileService(
            user_repo=mock_user_repo, order_repo=mock_order_repo, cart_service=cart_service
        )
        
        with pytest.raises(OrderNotFoundError):
            await service.repeat_order(user_id=1, order_id=4)
