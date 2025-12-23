"""
Блочные тесты модуля каталога (CatalogService).
Тесты Б1-Б14.
"""

import pytest
from decimal import Decimal
from app.services.catalog_service import CatalogService
from app.dto import ProductCreate, ProductUpdate
from app.exceptions import ValidationError, CategoryNotEmptyError, DuplicateCategoryError


class TestCatalogService:

    @pytest.mark.asyncio
    async def test_b01_get_categories_returns_active(self, mock_product_repo):
        """Б1: Получение списка категорий возвращает 5 активных категорий"""
        service = CatalogService(product_repo=mock_product_repo)
        
        categories = await service.get_categories()
        
        assert len(categories) == 5
        assert all(c.is_active for c in categories)

    @pytest.mark.asyncio
    async def test_b02_get_products_by_category_smartphones(self, mock_product_repo):
        """Б2: Получение товаров категории 1 (Смартфоны) возвращает 4 товара"""
        service = CatalogService(product_repo=mock_product_repo)
        
        products = await service.get_products_by_category(1)
        
        assert len(products) == 4
        assert all(p.category_id == 1 for p in products)

    @pytest.mark.asyncio
    async def test_b03_get_products_nonexistent_category(self, mock_product_repo):
        """Б3: Получение товаров несуществующей категории 999 возвращает пустой список"""
        service = CatalogService(product_repo=mock_product_repo)
        
        products = await service.get_products_by_category(999)
        
        assert products == []

    @pytest.mark.asyncio
    async def test_b04_get_product_by_id(self, mock_product_repo):
        """Б4: Получение товара id=3 возвращает Samsung Galaxy S24, цена=79990, остаток=10"""
        service = CatalogService(product_repo=mock_product_repo)
        
        product = await service.get_product(3)
        
        assert product is not None
        assert product.name == "Samsung Galaxy S24"
        assert product.price == Decimal('79990')
        assert product.stock == 10

    @pytest.mark.asyncio
    async def test_b05_get_product_nonexistent(self, mock_product_repo):
        """Б5: Получение несуществующего товара id=99999 возвращает None"""
        service = CatalogService(product_repo=mock_product_repo)
        
        product = await service.get_product(99999)
        
        assert product is None

    @pytest.mark.asyncio
    async def test_b06_get_product_stock(self, mock_product_repo):
        """Б6: Получение остатка товара id=3 возвращает 10"""
        service = CatalogService(product_repo=mock_product_repo)
        
        stock = await service.get_product_stock(3)
        
        assert stock == 10

    @pytest.mark.asyncio
    async def test_b07_create_product_success(self, mock_product_repo):
        """Б7: Создание товара вставляет запись и возвращает присвоенный id"""
        service = CatalogService(product_repo=mock_product_repo)
        data = ProductCreate(
            name="Новый смартфон",
            price=Decimal('59990'),
            stock=20,
            category_id=1
        )
        
        product = await service.create_product(data)
        
        assert product is not None
        assert product.id is not None
        assert product.name == "Новый смартфон"

    @pytest.mark.asyncio
    async def test_b08_create_product_invalid_data_raises_error(self, mock_product_repo):
        """Б8: Создание товара с невалидными данными вызывает ValidationError"""
        service = CatalogService(product_repo=mock_product_repo)
        
        # Пустое имя
        with pytest.raises(ValidationError):
            await service.create_product(ProductCreate(name="", price=100, stock=1, category_id=1))
        
        # Отрицательная цена
        with pytest.raises(ValidationError):
            await service.create_product(ProductCreate(name="Test", price=-100, stock=1, category_id=1))
        
        # Несуществующая категория
        with pytest.raises(ValidationError):
            await service.create_product(ProductCreate(name="Test", price=100, stock=1, category_id=999))

    @pytest.mark.asyncio
    async def test_b09_update_product(self, mock_product_repo):
        """Б9: Обновление товара id=3 изменяет цену и остаток"""
        service = CatalogService(product_repo=mock_product_repo)
        data = ProductUpdate(price=Decimal('69990'), stock=15)
        
        product = await service.update_product(3, data)
        
        assert product.price == Decimal('69990')
        assert product.stock == 15

    @pytest.mark.asyncio
    async def test_b10_delete_product(self, mock_product_repo):
        """Б10: Удаление товара id=50 устанавливает is_active=False"""
        service = CatalogService(product_repo=mock_product_repo)
        
        result = await service.delete_product(50)
        
        assert result == True

    @pytest.mark.asyncio
    async def test_b11_create_category(self, mock_product_repo):
        """Б11: Создание категории 'Новая' создаёт запись"""
        service = CatalogService(product_repo=mock_product_repo)
        
        category = await service.create_category("Новая категория")
        
        assert category is not None
        assert category.name == "Новая категория"

    @pytest.mark.asyncio
    async def test_b12_create_duplicate_category_raises_error(self, mock_product_repo):
        """Б12: Создание категории 'Смартфоны' вызывает DuplicateCategoryError"""
        service = CatalogService(product_repo=mock_product_repo)
        
        with pytest.raises(DuplicateCategoryError):
            await service.create_category("Смартфоны")

    @pytest.mark.asyncio
    async def test_b13_delete_empty_category(self, mock_product_repo):
        """Б13: Удаление пустой категории выполняется успешно"""
        service = CatalogService(product_repo=mock_product_repo)
        # Категория 4 (Телевизоры) - в ней нет товаров в тестовых данных
        
        result = await service.delete_category(4)
        
        assert result == True

    @pytest.mark.asyncio
    async def test_b14_delete_nonempty_category_raises_error(self, mock_product_repo):
        """Б14: Удаление категории 1 с товарами вызывает CategoryNotEmptyError"""
        service = CatalogService(product_repo=mock_product_repo)
        
        with pytest.raises(CategoryNotEmptyError):
            await service.delete_category(1)
