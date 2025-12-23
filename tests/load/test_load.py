"""
Нагрузочные тесты телеграм-бота.
Тесты Н1-Н10.

Проверяют производительность и устойчивость под нагрузкой.
"""

import pytest
import asyncio
import time
from decimal import Decimal
from datetime import datetime
from app.services.catalog_service import CatalogService
from app.services.cart_service import CartService
from app.services.search_service import SearchService
from app.services.discount_service import DiscountService
from app.dto import Cart, CartItem


class TestLoadCatalog:
    """Нагрузочные тесты каталога"""

    @pytest.mark.asyncio
    async def test_h01_catalog_100_concurrent_requests(self, mock_product_repo):
        """Н1: 100 параллельных запросов к каталогу, время отклика < 500ms"""
        service = CatalogService(product_repo=mock_product_repo)
        num_requests = 100
        
        start = time.perf_counter()
        tasks = [service.get_categories() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == num_requests
        assert all(len(r) == 5 for r in results)
        avg_ms = total_ms / num_requests
        assert avg_ms < 500, f"Среднее время {avg_ms:.2f}ms превышает 500ms"

    @pytest.mark.asyncio
    async def test_h02_products_by_category_load(self, mock_product_repo):
        """Н2: 100 запросов товаров категорий, проверка RPS"""
        service = CatalogService(product_repo=mock_product_repo)
        num_requests = 100
        categories = [1, 2, 3, 4, 5]
        
        start = time.perf_counter()
        tasks = [service.get_products_by_category(categories[i % 5]) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == num_requests
        rps = num_requests / (total_ms / 1000)
        assert rps > 50, f"RPS {rps:.0f} меньше 50"


class TestLoadCart:
    """Нагрузочные тесты корзины"""

    @pytest.mark.asyncio
    async def test_h03_cart_50_users_concurrent(self, mock_cart_repo, mock_product_repo):
        """Н3: 50 пользователей одновременно добавляют товары"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        num_users = 50
        
        async def user_session(user_id):
            await service.add_item(user_id + 100, product_id=3, qty=1)
            await service.add_item(user_id + 100, product_id=5, qty=1)
            return await service.get_cart(user_id + 100)
        
        start = time.perf_counter()
        tasks = [user_session(i) for i in range(num_users)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == num_users
        non_empty = sum(1 for r in results if not r.is_empty)
        assert non_empty == num_users

    def test_h04_calc_totals_1000_times(self, mock_cart_repo, mock_product_repo):
        """Н4: 1000 расчётов итогов корзины < 1ms каждый"""
        service = CartService(cart_repo=mock_cart_repo, product_repo=mock_product_repo)
        cart = Cart(user_id=1, items=[
            CartItem(product_id=i, product_name=f"Product {i}", price=Decimal(str(10000 + i * 1000)), qty=i % 5 + 1)
            for i in range(10)
        ])
        
        num = 1000
        start = time.perf_counter()
        for _ in range(num):
            service.calc_totals(cart)
        total_ms = (time.perf_counter() - start) * 1000
        
        avg_us = (total_ms * 1000) / num
        assert avg_us < 1000, f"Среднее время {avg_us:.2f}µs превышает 1000µs"


class TestLoadSearch:
    """Нагрузочные тесты поиска"""

    @pytest.mark.asyncio
    async def test_h05_search_100_queries(self, mock_product_repo):
        """Н5: 100 параллельных поисковых запросов"""
        service = SearchService(product_repo=mock_product_repo)
        queries = ["iphone", "samsung", "macbook", "airpods", "ноутбук"]
        num_requests = 100
        
        start = time.perf_counter()
        tasks = [service.search_products(queries[i % len(queries)]) for i in range(num_requests)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == num_requests
        avg_ms = total_ms / num_requests
        assert avg_ms < 500

    @pytest.mark.asyncio
    async def test_h06_fuzzy_search_50_queries(self, mock_product_repo):
        """Н6: 50 нечётких поисковых запросов с опечатками"""
        service = SearchService(product_repo=mock_product_repo)
        queries = ["айфан", "самсунг", "макбк", "эирподс", "ноутбк"]
        
        start = time.perf_counter()
        tasks = [service.search_products(queries[i % len(queries)]) for i in range(50)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == 50
        assert total_ms < 5000


class TestLoadDiscount:
    """Нагрузочные тесты скидок"""

    @pytest.mark.asyncio
    async def test_h07_promo_validation_200_requests(self, mock_promocode_repo):
        """Н7: 200 валидаций промокодов"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        codes = ["SAVE10", "SAVE20", "VIP50", "INVALID", "OLD"]
        
        start = time.perf_counter()
        tasks = [service.validate_promo(codes[i % len(codes)], datetime.utcnow()) for i in range(200)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == 200
        valid_count = sum(1 for r in results if r.valid)
        assert valid_count > 0

    @pytest.mark.asyncio
    async def test_h08_discount_calculation_100_carts(self, mock_promocode_repo):
        """Н8: 100 расчётов скидок для разных корзин"""
        service = DiscountService(promocode_repo=mock_promocode_repo)
        carts = [
            Cart(user_id=i, items=[
                CartItem(product_id=1, product_name="Товар", price=Decimal(str(30000 + i * 1000)), qty=1)
            ])
            for i in range(100)
        ]
        
        start = time.perf_counter()
        tasks = [service.apply_discounts(carts[i], "SAVE10") for i in range(100)]
        results = await asyncio.gather(*tasks)
        total_ms = (time.perf_counter() - start) * 1000
        
        assert len(results) == 100


class TestLoadMixed:
    """Смешанные нагрузочные тесты"""

    @pytest.mark.asyncio
    async def test_h09_mixed_operations_200(self, mock_product_repo, mock_cart_repo, mock_promocode_repo):
        """Н9: 200 смешанных операций (каталог + поиск + скидки)"""
        catalog = CatalogService(product_repo=mock_product_repo)
        search = SearchService(product_repo=mock_product_repo)
        discount = DiscountService(promocode_repo=mock_promocode_repo)
        
        async def operation(i):
            op = i % 3
            if op == 0:
                return await catalog.get_categories()
            elif op == 1:
                return await search.search_products("iphone")
            else:
                return await discount.validate_promo("SAVE10", datetime.utcnow())
        
        start = time.perf_counter()
        tasks = [operation(i) for i in range(200)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_ms = (time.perf_counter() - start) * 1000
        
        successful = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful) / 200 * 100
        
        assert success_rate >= 99, f"Успешность {success_rate:.1f}% < 99%"

    @pytest.mark.asyncio
    async def test_h10_sustained_load_2_seconds(self, mock_product_repo):
        """Н10: Устойчивая нагрузка в течение 2 секунд"""
        service = CatalogService(product_repo=mock_product_repo)
        
        results = []
        errors = []
        duration = 2
        
        start = time.perf_counter()
        end = start + duration
        
        while time.perf_counter() < end:
            try:
                req_start = time.perf_counter()
                await service.get_categories()
                results.append((time.perf_counter() - req_start) * 1000)
            except Exception as e:
                errors.append(str(e))
            await asyncio.sleep(0.01)
        
        assert len(errors) == 0, f"Ошибки: {errors}"
        avg_ms = sum(results) / len(results) if results else 0
        assert avg_ms < 100, f"Среднее время {avg_ms:.2f}ms > 100ms"
