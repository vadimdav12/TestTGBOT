"""
Интеграционные тесты телеграм-бота.
Тесты И1-И12.

Проверяют взаимодействие нескольких компонентов системы.
"""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock
from app.services.catalog_service import CatalogService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.discount_service import DiscountService
from app.services.search_service import SearchService
from app.services.favorites_service import FavoritesService
from app.services.notification_service import NotificationService
from app.services.payment_service import PaymentService
from app.services.receipt_service import ReceiptService
from app.dto import ContactData
from app.exceptions import InsufficientStockError
from tests.conftest import MockOrder, MockOrderItem


class TestIntegration:

    @pytest.mark.asyncio
    async def test_i01_catalog_navigation(self, mock_product_repo, mock_bot):
        """И1: Навигация по каталогу: категории → товары категории"""
        catalog_service = CatalogService(product_repo=mock_product_repo)
        
        # 1. Получаем категории
        categories = await catalog_service.get_categories()
        assert len(categories) == 5
        
        # 2. Выбираем категорию "Смартфоны" (id=1)
        smartphones_category = next(c for c in categories if c.name == "Смартфоны")
        
        # 3. Получаем товары категории
        products = await catalog_service.get_products_by_category(smartphones_category.id)
        assert len(products) == 4
        assert all(p.category_id == 1 for p in products)

    @pytest.mark.asyncio
    async def test_i02_catalog_product_details(self, mock_product_repo):
        """И2: Просмотр товара: список → детали товара с остатком"""
        catalog_service = CatalogService(product_repo=mock_product_repo)
        
        # 1. Получаем список товаров
        products = await catalog_service.get_products_by_category(1)
        
        # 2. Выбираем товар
        product_id = products[0].id
        
        # 3. Получаем детали
        product = await catalog_service.get_product(product_id)
        stock = await catalog_service.get_product_stock(product_id)
        
        assert product is not None
        assert stock >= 0

    @pytest.mark.asyncio
    async def test_i03_add_to_cart_with_stock_check(self, mock_cart_repo, mock_product_repo):
        """И3: Добавление в корзину с проверкой остатка"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        # 1. Проверяем остаток
        available = await cart_service.check_stock(product_id=3, qty=2)
        assert available == True
        
        # 2. Добавляем в корзину
        cart = await cart_service.add_item(user_id=1, product_id=3, qty=2)
        
        # 3. Проверяем корзину
        assert not cart.is_empty

    @pytest.mark.asyncio
    async def test_i04_add_to_cart_insufficient_stock(self, mock_cart_repo, mock_product_repo):
        """И4: Добавление в корзину при недостатке товара → ошибка"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        # Товар id=1 имеет stock=0
        with pytest.raises(InsufficientStockError) as exc_info:
            await cart_service.add_item(user_id=1, product_id=1, qty=1)
        
        assert exc_info.value.available == 0

    @pytest.mark.asyncio
    async def test_i05_checkout_flow(self, mock_cart_repo, mock_product_repo, mock_order_repo, mock_promocode_repo, mock_user_repo, mock_bot):
        """И5: Полный процесс оформления: корзина → скидки → заказ → уведомление"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        discount_service = DiscountService(promocode_repo=mock_promocode_repo)
        notification_service = NotificationService(bot=mock_bot, user_repo=mock_user_repo, config={'admin_ids': [100008]})
        order_service = OrderService(
            order_repo=mock_order_repo, cart_service=cart_service,
            product_repo=mock_product_repo, discount_service=discount_service,
            notification_service=notification_service
        )
        
        # 1. Добавляем товар в корзину
        await cart_service.add_item(user_id=1, product_id=3, qty=1)
        
        # 2. Получаем корзину и считаем скидки
        cart = await cart_service.get_cart(1)
        discount_result = await discount_service.apply_discounts(cart, "SAVE10")
        
        # 3. Оформляем заказ
        contact = ContactData(name="Тест", phone="+7 999 111-11-11", address="г. Москва, ул. Тестовая, д. 1")
        order = await order_service.create_order(user_id=1, contact=contact)
        
        assert order is not None
        assert order.status == 'created'

    @pytest.mark.asyncio
    async def test_i06_checkout_with_invalid_phone(self, mock_cart_repo, mock_product_repo, mock_order_repo):
        """И6: Оформление с невалидным телефоном → валидация FSM"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        order_service = OrderService(order_repo=mock_order_repo, cart_service=cart_service)
        
        # Добавляем товар
        mock_cart_repo._data[1] = [
            {'product_id': 3, 'qty': 1, 'name': 'Samsung', 'price': Decimal('79990'), 'stock': 10, 'is_active': True}
        ]
        
        # Невалидный телефон должен быть отклонён на уровне валидации
        from app.utils.helpers import validate_phone
        assert validate_phone("invalid") == False
        assert validate_phone("+7 999 111-11-11") == True

    @pytest.mark.asyncio
    async def test_i07_payment_creates_session(self, mock_order_repo, mock_user_repo, mock_bot, tmp_path):
        """И7: Инициализация оплаты создаёт платёжную сессию"""
        payment_gateway = AsyncMock()
        payment_gateway.create_session = AsyncMock(return_value=AsyncMock(
            session_id="sess_123", payment_url="https://pay.example.com/sess_123"
        ))
        
        receipt_service = ReceiptService(order_repo=mock_order_repo, bot=mock_bot, receipts_dir=str(tmp_path))
        notification_service = NotificationService(bot=mock_bot, user_repo=mock_user_repo, config={})
        payment_service = PaymentService(
            order_repo=mock_order_repo, payment_gateway=payment_gateway,
            receipt_service=receipt_service, notification_service=notification_service
        )
        
        # Создаём платёжную сессию
        session = await payment_service.create_payment_session(order_id=2)
        
        assert session.session_id == "sess_123"
        assert "pay.example.com" in session.payment_url

    @pytest.mark.asyncio
    async def test_i08_payment_webhook_updates_order(self, mock_order_repo, mock_user_repo, mock_bot, tmp_path):
        """И8: Webhook оплаты обновляет статус → генерирует чек → отправляет"""
        mock_order_repo.get_order_items = AsyncMock(return_value=[
            MockOrderItem(1, 2, 3, "Samsung", Decimal('79990'), 1)
        ])
        
        receipt_service = ReceiptService(order_repo=mock_order_repo, bot=mock_bot, receipts_dir=str(tmp_path))
        notification_service = NotificationService(bot=mock_bot, user_repo=mock_user_repo, config={})
        payment_service = PaymentService(
            order_repo=mock_order_repo, payment_gateway=AsyncMock(),
            receipt_service=receipt_service, notification_service=notification_service
        )
        
        # Симулируем webhook
        result = await payment_service.process_webhook(order_id=2, status='paid')
        
        assert result == True

    @pytest.mark.asyncio
    async def test_i09_search_cyrillic_finds_product(self, mock_product_repo, mock_cart_repo):
        """И9: Поиск на кириллице находит товар и добавляет в корзину"""
        search_service = SearchService(product_repo=mock_product_repo)
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        # 1. Поиск "самсунг"
        results = await search_service.search_products("самсунг")
        assert len(results) > 0
        
        # 2. Добавляем найденный товар
        product_id = results[0].product_id
        await cart_service.add_item(user_id=1, product_id=product_id, qty=1)
        
        # 3. Проверяем корзину
        cart = await cart_service.get_cart(1)
        assert not cart.is_empty

    @pytest.mark.asyncio
    async def test_i10_favorites_workflow(self, mock_favorites_repo, mock_product_repo, mock_cart_repo):
        """И10: Добавление в избранное → просмотр → в корзину"""
        favorites_service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        
        # 1. Добавляем в избранное
        await favorites_service.add_favorite(user_id=1, product_id=3)
        
        # 2. Получаем список
        favorites = await favorites_service.list_favorites(user_id=1)
        assert len(favorites) == 1
        
        # 3. Добавляем в корзину
        for product in favorites:
            await cart_service.add_item(user_id=1, product_id=product.id, qty=1)
        
        cart = await cart_service.get_cart(1)
        assert len(cart.items) == 1

    @pytest.mark.asyncio
    async def test_i11_promocode_applies_to_cart(self, mock_cart_repo, mock_product_repo, mock_promocode_repo):
        """И11: Применение промокода к корзине рассчитывает скидку"""
        cart_service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        discount_service = DiscountService(promocode_repo=mock_promocode_repo)
        
        # 1. Добавляем товар
        mock_cart_repo._data[1] = [
            {'product_id': 5, 'qty': 1, 'name': 'MacBook', 'price': Decimal('199990'), 'stock': 2, 'is_active': True}
        ]
        
        # 2. Получаем корзину
        cart = await cart_service.get_cart(1)
        
        # 3. Применяем промокод
        result = await discount_service.apply_discounts(cart, "SAVE10")
        
        # 10% от 199990 = 19999
        assert result.promo_discount == Decimal('19999')

    @pytest.mark.asyncio
    async def test_i12_admin_creates_product(self, mock_product_repo, mock_user_repo):
        """И12: Админ создаёт товар через админ-панель"""
        catalog_service = CatalogService(product_repo=mock_product_repo)
        
        # 1. Проверяем права админа
        is_admin = await mock_user_repo.is_admin(8)
        assert is_admin == True
        
        # 2. Создаём товар
        from app.dto import ProductCreate
        data = ProductCreate(name="Новый товар", price=Decimal('99990'), stock=50, category_id=1)
        product = await catalog_service.create_product(data)
        
        assert product is not None
        assert product.name == "Новый товар"
