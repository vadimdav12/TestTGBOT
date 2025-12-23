"""
Конфигурация pytest и фикстуры для тестирования телеграм-бота.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from typing import List

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ==================== MOCK КЛАССЫ ====================

class MockProduct:
    def __init__(self, id, name, price, stock=10, category_id=1, is_active=True):
        self.id = id
        self.name = name
        self.price = Decimal(str(price))
        self.stock = stock
        self.category_id = category_id
        self.is_active = is_active
        self.description = ''
        self.created_at = datetime.utcnow()


class MockCategory:
    def __init__(self, id, name, sort_order=0, is_active=True):
        self.id = id
        self.name = name
        self.sort_order = sort_order
        self.is_active = is_active


class MockUser:
    def __init__(self, id, telegram_id, name='', phone='', address='', is_admin=False):
        self.id = id
        self.telegram_id = telegram_id
        self.name = name
        self.phone = phone
        self.address = address
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()


class MockOrder:
    def __init__(self, id, user_id, order_number, total, status='created',
                 discount=0, contact_name='', contact_phone='', contact_address='',
                 payment_method='card'):
        self.id = id
        self.user_id = user_id
        self.order_number = order_number
        self.total = Decimal(str(total))
        self.status = status
        self.discount = Decimal(str(discount))
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_address = contact_address
        self.payment_method = payment_method
        self.created_at = datetime.utcnow()


class MockOrderItem:
    def __init__(self, id, order_id, product_id, product_name, price, qty):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.product_name = product_name
        self.price = Decimal(str(price))
        self.qty = qty


class MockPromocode:
    def __init__(self, id, code, discount_type, discount_value,
                 valid_from=None, valid_to=None, is_used=False):
        self.id = id
        self.code = code
        self.discount_type = discount_type
        self.discount_value = Decimal(str(discount_value))
        self.valid_from = valid_from or (datetime.utcnow() - timedelta(days=30))
        self.valid_to = valid_to or (datetime.utcnow() + timedelta(days=30))
        self.is_used = is_used


class MockFavorite:
    def __init__(self, id, user_id, product_id):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id


class MockBot:
    def __init__(self):
        self.sent_messages = []
        self.sent_documents = []
    
    async def send_message(self, chat_id, text, **kwargs):
        self.sent_messages.append({'chat_id': chat_id, 'text': text, **kwargs})
        return MagicMock()
    
    async def send_document(self, chat_id, document, caption='', **kwargs):
        self.sent_documents.append({'chat_id': chat_id, 'document': document, 'caption': caption})
        return MagicMock()


# ==================== ТЕСТОВЫЕ ДАННЫЕ ====================

@pytest.fixture
def test_categories():
    return [
        MockCategory(1, "Смартфоны", 1),
        MockCategory(2, "Ноутбуки", 2),
        MockCategory(3, "Аксессуары", 3),
        MockCategory(4, "Телевизоры", 4),
        MockCategory(5, "Аудио", 5),
    ]


@pytest.fixture
def test_products():
    return [
        MockProduct(1, "iPhone 15 Pro", 129990, stock=0, category_id=1),
        MockProduct(2, "iPhone 15", 89990, stock=5, category_id=1),
        MockProduct(3, "Samsung Galaxy S24", 79990, stock=10, category_id=1),
        MockProduct(4, "Xiaomi 14", 49990, stock=3, category_id=1),
        MockProduct(5, "MacBook Pro 14", 199990, stock=2, category_id=2),
        MockProduct(6, "ASUS ROG Strix", 159990, stock=7, category_id=2),
        MockProduct(7, "Чехол iPhone", 1990, stock=100, category_id=3),
        MockProduct(8, "Зарядка USB-C", 2490, stock=50, category_id=3),
        MockProduct(9, "AirPods Pro 2", 24990, stock=15, category_id=5),
        MockProduct(10, "Sony WH-1000XM5", 34990, stock=8, category_id=5),
        MockProduct(50, "Тестовый товар", 9990, stock=1, category_id=1),
        MockProduct(99, "Архивный товар", 999, stock=0, category_id=1, is_active=False),
    ]


@pytest.fixture
def test_users():
    return [
        MockUser(1, 100001, "Иван Тестовый", "+7 999 111-11-11", "ул. Тестовая, 1"),
        MockUser(2, 100002, "Мария Тестовая", "+7 999 222-22-22", "ул. Тестовая, 2"),
        MockUser(3, 100003, "Пётр Тестовый", "+7 999 333-33-33", "ул. Тестовая, 3"),
        MockUser(4, 100004, "Новый Пользователь", "", ""),
        MockUser(8, 100008, "Админ Первый", "+7 999 888-88-88", "", is_admin=True),
        MockUser(9, 100009, "Админ Второй", "+7 999 999-99-99", "", is_admin=True),
    ]


@pytest.fixture
def test_promocodes():
    now = datetime.utcnow()
    return [
        MockPromocode(1, "SAVE10", "percent", 10),
        MockPromocode(2, "SAVE20", "percent", 20),
        MockPromocode(3, "OLD", "percent", 15,
                     now - timedelta(days=730), now - timedelta(days=365)),
        MockPromocode(4, "USED", "percent", 10, is_used=True),
        MockPromocode(5, "VIP50", "percent", 50),
        MockPromocode(6, "FIXED5000", "fixed", 5000),
    ]


@pytest.fixture
def test_orders():
    return [
        MockOrder(1, 1, "ORD-20241201-0001", 89990, status='created'),
        MockOrder(2, 1, "ORD-20241201-0002", 129990, status='paid'),
        MockOrder(3, 1, "ORD-20241202-0001", 49990, status='shipped'),
        MockOrder(4, 2, "ORD-20241202-0002", 79990, status='paid'),
        MockOrder(5, 3, "ORD-20241203-0001", 24990, status='cancelled'),
    ]


# ==================== MOCK РЕПОЗИТОРИИ ====================

@pytest.fixture
def mock_product_repo(test_products, test_categories):
    repo = AsyncMock()
    
    async def fetch_categories():
        return [c for c in test_categories if c.is_active]
    
    async def fetch_category_by_id(category_id):
        return next((c for c in test_categories if c.id == category_id), None)
    
    async def fetch_category_by_name(name):
        return next((c for c in test_categories if c.name == name), None)
    
    async def fetch_products_by_category(category_id):
        return [p for p in test_products if p.category_id == category_id and p.is_active]
    
    async def fetch_product_by_id(product_id):
        return next((p for p in test_products if p.id == product_id and p.is_active), None)
    
    async def fetch_all_products():
        return [p for p in test_products if p.is_active]
    
    async def insert_product(data):
        new_id = max(p.id for p in test_products) + 1
        new_product = MockProduct(new_id, data.name, data.price, data.stock, data.category_id)
        test_products.append(new_product)
        return new_product
    
    async def update_product(product_id, data):
        for p in test_products:
            if p.id == product_id:
                if hasattr(data, 'price') and data.price is not None:
                    p.price = Decimal(str(data.price))
                if hasattr(data, 'stock') and data.stock is not None:
                    p.stock = data.stock
                if hasattr(data, 'name') and data.name is not None:
                    p.name = data.name
                return p
        return None
    
    async def delete_product(product_id):
        for p in test_products:
            if p.id == product_id:
                p.is_active = False
                return True
        return False
    
    async def insert_category(name):
        new_id = max(c.id for c in test_categories) + 1
        new_cat = MockCategory(new_id, name, new_id)
        test_categories.append(new_cat)
        return new_cat
    
    async def delete_category(category_id):
        for c in test_categories:
            if c.id == category_id:
                c.is_active = False
                return True
        return False
    
    async def count_products_in_category(category_id):
        return len([p for p in test_products if p.category_id == category_id and p.is_active])
    
    repo.fetch_categories = fetch_categories
    repo.fetch_category_by_id = fetch_category_by_id
    repo.fetch_category_by_name = fetch_category_by_name
    repo.fetch_products_by_category = fetch_products_by_category
    repo.fetch_product_by_id = fetch_product_by_id
    repo.fetch_all_products = fetch_all_products
    repo.insert_product = insert_product
    repo.update_product = update_product
    repo.delete_product = delete_product
    repo.insert_category = insert_category
    repo.delete_category = delete_category
    repo.count_products_in_category = count_products_in_category
    
    return repo


@pytest.fixture
def mock_cart_repo():
    repo = AsyncMock()
    cart_data = {}
    
    async def get_cart_items(user_id):
        return cart_data.get(user_id, [])
    
    async def upsert_cart_item(user_id, product_id, qty):
        if user_id not in cart_data:
            cart_data[user_id] = []
        for item in cart_data[user_id]:
            if item['product_id'] == product_id:
                item['qty'] = qty
                return
        cart_data[user_id].append({
            'product_id': product_id, 'qty': qty,
            'name': f'Product {product_id}', 'price': Decimal('9990'),
            'stock': 10, 'is_active': True
        })
    
    async def delete_cart_item(user_id, product_id):
        if user_id in cart_data:
            cart_data[user_id] = [i for i in cart_data[user_id] if i['product_id'] != product_id]
    
    async def clear_cart(user_id):
        cart_data[user_id] = []
    
    repo.get_cart_items = get_cart_items
    repo.upsert_cart_item = upsert_cart_item
    repo.delete_cart_item = delete_cart_item
    repo.clear_cart = clear_cart
    repo._data = cart_data
    
    return repo


@pytest.fixture
def mock_order_repo(test_orders):
    repo = AsyncMock()
    
    async def get_order_by_id(order_id):
        return next((o for o in test_orders if o.id == order_id), None)
    
    async def list_orders_by_user(user_id):
        return [o for o in test_orders if o.user_id == user_id]
    
    async def update_order_status(order_id, status):
        for o in test_orders:
            if o.id == order_id:
                o.status = status
    
    repo.get_order_by_id = get_order_by_id
    repo.list_orders_by_user = list_orders_by_user
    repo.update_order_status = update_order_status
    
    return repo


@pytest.fixture
def mock_user_repo(test_users):
    repo = AsyncMock()
    
    async def get_user_by_id(user_id):
        return next((u for u in test_users if u.id == user_id), None)
    
    async def is_admin(user_id):
        user = next((u for u in test_users if u.id == user_id), None)
        return user.is_admin if user else False
    
    repo.get_user_by_id = get_user_by_id
    repo.is_admin = is_admin
    
    return repo


@pytest.fixture
def mock_favorites_repo():
    repo = AsyncMock()
    favorites = {}
    
    async def get_favorites(user_id):
        return [MockFavorite(i, user_id, pid) for i, pid in enumerate(favorites.get(user_id, []))]
    
    async def add_favorite(user_id, product_id):
        if user_id not in favorites:
            favorites[user_id] = []
        if product_id not in favorites[user_id]:
            favorites[user_id].append(product_id)
    
    async def remove_favorite(user_id, product_id):
        if user_id in favorites and product_id in favorites[user_id]:
            favorites[user_id].remove(product_id)
    
    async def exists_favorite(user_id, product_id):
        return user_id in favorites and product_id in favorites[user_id]
    
    repo.get_favorites = get_favorites
    repo.add_favorite = add_favorite
    repo.remove_favorite = remove_favorite
    repo.exists_favorite = exists_favorite
    repo._data = favorites
    
    return repo


@pytest.fixture
def mock_promocode_repo(test_promocodes):
    repo = AsyncMock()
    usage = {}
    
    async def get_promocode_by_code(code):
        return next((p for p in test_promocodes if p.code.upper() == code.upper()), None)
    
    async def check_user_usage(code, user_id):
        return (code.upper(), user_id) in usage
    
    async def record_usage(code, user_id, order_id):
        usage[(code.upper(), user_id)] = True
    
    repo.get_promocode_by_code = get_promocode_by_code
    repo.check_user_usage = check_user_usage
    repo.record_usage = record_usage
    
    return repo


@pytest.fixture
def mock_bot():
    return MockBot()
