"""
Блочные тесты модуля скидок (DiscountService).
Тесты Б41-Б48.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from app.services.discount_service import DiscountService
from app.dto import Cart, CartItem


class TestDiscountService:

    @pytest.mark.asyncio
    async def test_b41_validate_promo_active(self, mock_promocode_repo):
        """Б41: Валидация активного промокода SAVE10 возвращает valid=True, discount=10%"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        
        result = await service.validate_promo("SAVE10", datetime.utcnow())
        
        assert result.valid == True
        assert result.discount_type == "percent"
        assert result.discount_value == Decimal('10')

    @pytest.mark.asyncio
    async def test_b42_validate_promo_expired(self, mock_promocode_repo):
        """Б42: Валидация истёкшего промокода OLD возвращает valid=False, error='Промокод истёк'"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        
        result = await service.validate_promo("OLD", datetime.utcnow())
        
        assert result.valid == False
        assert "истёк" in result.error_message

    @pytest.mark.asyncio
    async def test_b43_validate_promo_already_used(self, mock_promocode_repo):
        """Б43: Валидация использованного промокода USED возвращает valid=False"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        
        result = await service.validate_promo("USED", datetime.utcnow())
        
        assert result.valid == False
        assert "использован" in result.error_message

    @pytest.mark.asyncio
    async def test_b44_validate_promo_not_found(self, mock_promocode_repo):
        """Б44: Валидация несуществующего промокода возвращает valid=False"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        
        result = await service.validate_promo("INVALID123", datetime.utcnow())
        
        assert result.valid == False
        assert "не найден" in result.error_message

    @pytest.mark.asyncio
    async def test_b45_apply_percent_discount(self, mock_promocode_repo):
        """Б45: Применение промокода SAVE10 к корзине 100000₽ даёт скидку 10000₽"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        cart = Cart(user_id=1, items=[
            CartItem(product_id=1, product_name="Товар", price=Decimal('100000'), qty=1)
        ])
        
        result = await service.apply_discounts(cart, "SAVE10")
        
        assert result.promo_discount == Decimal('10000')

    @pytest.mark.asyncio
    async def test_b46_apply_fixed_discount(self, mock_promocode_repo):
        """Б46: Применение промокода FIXED5000 даёт фиксированную скидку 5000₽"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        cart = Cart(user_id=1, items=[
            CartItem(product_id=1, product_name="Товар", price=Decimal('50000'), qty=1)
        ])
        
        result = await service.apply_discounts(cart, "FIXED5000")
        
        assert result.promo_discount == Decimal('5000')

    def test_b47_auto_discount_50k(self, mock_promocode_repo):
        """Б47: Автоскидка при сумме 50000₽ составляет 5% = 2500₽"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        
        discount = service.calculate_auto_discount(Decimal('50000'))
        
        assert discount == Decimal('2500')

    @pytest.mark.asyncio
    async def test_b48_check_promo_usage(self, mock_promocode_repo):
        """Б48: Проверка использования промокода SAVE10 пользователем 1 возвращает False"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        
        result = await service.check_promo_usage("SAVE10", user_id=1)
        
        assert result == False
