"""
Блочные тесты модуля корзины (CartService).
Тесты Б15-Б29.
"""

import pytest
from decimal import Decimal
from app.services.cart_service import CartService
from app.dto import Cart, CartItem
from app.exceptions import InsufficientStockError, CartItemNotFoundError


class TestCartService:

    @pytest.mark.asyncio
    async def test_b15_get_cart_with_items(self, mock_cart_repo, mock_product_repo):
        """Б15: Получение корзины пользователя 1 возвращает 2 позиции с актуальными ценами"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        mock_cart_repo._data[1] = [
            {'product_id': 2, 'qty': 1, 'name': 'iPhone 15', 'price': Decimal('89990'), 'stock': 5, 'is_active': True},
            {'product_id': 7, 'qty': 2, 'name': 'Чехол iPhone', 'price': Decimal('1990'), 'stock': 100, 'is_active': True}
        ]
        
        cart = await service.get_cart(1)
        
        assert len(cart.items) == 2
        assert cart.items[0].price == Decimal('89990')

    @pytest.mark.asyncio
    async def test_b16_get_empty_cart(self, mock_cart_repo, mock_product_repo):
        """Б16: Получение корзины нового пользователя 4 возвращает пустую корзину"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        cart = await service.get_cart(4)
        
        assert cart.is_empty == True
        assert len(cart.items) == 0

    @pytest.mark.asyncio
    async def test_b17_add_item_new_user(self, mock_cart_repo, mock_product_repo):
        """Б17: Добавление товара 3 в количестве 2 пользователю 4 создаёт запись в корзине"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        cart = await service.add_item(user_id=4, product_id=3, qty=2)
        
        assert len(mock_cart_repo._data.get(4, [])) == 1
        assert mock_cart_repo._data[4][0]['product_id'] == 3

    @pytest.mark.asyncio
    async def test_b18_add_item_existing_increases_qty(self, mock_cart_repo, mock_product_repo):
        """Б18: Добавление товара 2 (qty=2) при существующем qty=1 увеличивает количество до 3"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        mock_cart_repo._data[1] = [
            {'product_id': 2, 'qty': 1, 'name': 'iPhone 15', 'price': Decimal('89990'), 'stock': 5, 'is_active': True}
        ]
        
        await service.add_item(user_id=1, product_id=2, qty=2)
        
        assert mock_cart_repo._data[1][0]['qty'] == 3

    @pytest.mark.asyncio
    async def test_b19_add_item_exceeds_stock_raises_error(self, mock_cart_repo, mock_product_repo):
        """Б19: Добавление товара 4 (stock=3) в количестве 5 вызывает InsufficientStockError"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        with pytest.raises(InsufficientStockError) as exc_info:
            await service.add_item(user_id=4, product_id=4, qty=5)
        
        assert exc_info.value.available == 3
        assert exc_info.value.requested == 5

    @pytest.mark.asyncio
    async def test_b20_add_item_zero_stock_raises_error(self, mock_cart_repo, mock_product_repo):
        """Б20: Добавление товара 1 (stock=0) вызывает InsufficientStockError"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        with pytest.raises(InsufficientStockError):
            await service.add_item(user_id=4, product_id=1, qty=1)

    @pytest.mark.asyncio
    async def test_b21_update_item_qty(self, mock_cart_repo, mock_product_repo):
        """Б21: Изменение количества товара 2 на 3 обновляет запись"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        mock_cart_repo._data[1] = [
            {'product_id': 2, 'qty': 1, 'name': 'iPhone 15', 'price': Decimal('89990'), 'stock': 5, 'is_active': True}
        ]
        
        await service.update_item(user_id=1, product_id=2, qty=3)
        
        assert mock_cart_repo._data[1][0]['qty'] == 3

    @pytest.mark.asyncio
    async def test_b22_update_item_qty_zero_removes(self, mock_cart_repo, mock_product_repo):
        """Б22: Установка количества 0 для товара 7 удаляет его из корзины"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        mock_cart_repo._data[1] = [
            {'product_id': 7, 'qty': 2, 'name': 'Чехол', 'price': Decimal('1990'), 'stock': 100, 'is_active': True}
        ]
        
        await service.update_item(user_id=1, product_id=7, qty=0)
        
        assert len(mock_cart_repo._data[1]) == 0

    @pytest.mark.asyncio
    async def test_b23_update_nonexistent_item_raises_error(self, mock_cart_repo, mock_product_repo):
        """Б23: Изменение несуществующего товара 999 вызывает CartItemNotFoundError"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        with pytest.raises(CartItemNotFoundError):
            await service.update_item(user_id=4, product_id=999, qty=1)

    @pytest.mark.asyncio
    async def test_b24_remove_item(self, mock_cart_repo, mock_product_repo):
        """Б24: Удаление товара 7 из корзины удаляет запись"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        mock_cart_repo._data[1] = [
            {'product_id': 7, 'qty': 2, 'name': 'Чехол', 'price': Decimal('1990'), 'stock': 100, 'is_active': True}
        ]
        
        await service.remove_item(user_id=1, product_id=7)
        
        assert 7 not in [i['product_id'] for i in mock_cart_repo._data.get(1, [])]

    @pytest.mark.asyncio
    async def test_b25_remove_nonexistent_item_idempotent(self, mock_cart_repo, mock_product_repo):
        """Б25: Удаление несуществующего товара 999 выполняется без ошибки (идемпотентность)"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        await service.remove_item(user_id=4, product_id=999)
        # Не должно быть исключения

    @pytest.mark.asyncio
    async def test_b26_clear_cart(self, mock_cart_repo, mock_product_repo):
        """Б26: Очистка корзины пользователя 1 удаляет все записи"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        mock_cart_repo._data[1] = [
            {'product_id': 2, 'qty': 1, 'name': 'iPhone', 'price': Decimal('89990'), 'stock': 5, 'is_active': True},
            {'product_id': 7, 'qty': 2, 'name': 'Чехол', 'price': Decimal('1990'), 'stock': 100, 'is_active': True}
        ]
        
        await service.clear_cart(user_id=1)
        
        assert mock_cart_repo._data[1] == []

    def test_b27_calc_totals(self, mock_cart_repo, mock_product_repo):
        """Б27: Расчёт итогов корзины: subtotal=93970, items_count=3, positions_count=2"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        cart = Cart(user_id=1, items=[
            CartItem(product_id=2, product_name='iPhone', price=Decimal('89990'), qty=1),
            CartItem(product_id=7, product_name='Чехол', price=Decimal('1990'), qty=2)
        ])
        
        totals = service.calc_totals(cart)
        
        assert totals.subtotal == Decimal('93970')
        assert totals.items_count == 3
        assert totals.positions_count == 2

    @pytest.mark.asyncio
    async def test_b28_check_stock_available(self, mock_cart_repo, mock_product_repo):
        """Б28: Проверка остатка товара 3 (stock=10) для qty=5 возвращает True"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        result = await service.check_stock(product_id=3, qty=5)
        
        assert result == True

    @pytest.mark.asyncio
    async def test_b29_check_stock_not_available(self, mock_cart_repo, mock_product_repo):
        """Б29: Проверка остатка товара 4 (stock=3) для qty=5 возвращает False"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        result = await service.check_stock(product_id=4, qty=5)
        
        assert result == False
