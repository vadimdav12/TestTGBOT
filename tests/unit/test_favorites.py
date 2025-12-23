"""
Блочные тесты модуля избранного (FavoritesService).
Тесты Б57-Б64.
"""

import pytest
from app.services.favorites_service import FavoritesService
from app.exceptions import ProductNotFoundError


class TestFavoritesService:

    @pytest.mark.asyncio
    async def test_b57_add_favorite(self, mock_favorites_repo, mock_product_repo):
        """Б57: Добавление товара 5 в избранное пользователя 4 создаёт запись"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        
        await service.add_favorite(user_id=4, product_id=5)
        
        assert 5 in mock_favorites_repo._data.get(4, [])

    @pytest.mark.asyncio
    async def test_b58_add_favorite_idempotent(self, mock_favorites_repo, mock_product_repo):
        """Б58: Повторное добавление товара 5 не создаёт дубликат (идемпотентность)"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        
        await service.add_favorite(user_id=4, product_id=5)
        await service.add_favorite(user_id=4, product_id=5)
        
        count = mock_favorites_repo._data.get(4, []).count(5)
        assert count == 1

    @pytest.mark.asyncio
    async def test_b59_add_favorite_nonexistent_product(self, mock_favorites_repo, mock_product_repo):
        """Б59: Добавление несуществующего товара 99999 вызывает ProductNotFoundError"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        
        with pytest.raises(ProductNotFoundError) as exc_info:
            await service.add_favorite(user_id=4, product_id=99999)
        
        assert exc_info.value.product_id == 99999

    @pytest.mark.asyncio
    async def test_b60_remove_favorite(self, mock_favorites_repo, mock_product_repo):
        """Б60: Удаление товара 5 из избранного удаляет запись"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        mock_favorites_repo._data[1] = [5]
        
        await service.remove_favorite(user_id=1, product_id=5)
        
        assert 5 not in mock_favorites_repo._data.get(1, [])

    @pytest.mark.asyncio
    async def test_b61_remove_favorite_idempotent(self, mock_favorites_repo, mock_product_repo):
        """Б61: Удаление несуществующей записи выполняется без ошибки (идемпотентность)"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        
        await service.remove_favorite(user_id=4, product_id=999)
        # Не должно быть исключения

    @pytest.mark.asyncio
    async def test_b62_list_favorites(self, mock_favorites_repo, mock_product_repo):
        """Б62: Получение избранного пользователя 1 возвращает список товаров"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        mock_favorites_repo._data[1] = [2, 3, 5]
        
        products = await service.list_favorites(user_id=1)
        
        assert len(products) == 3

    @pytest.mark.asyncio
    async def test_b63_is_favorite_true(self, mock_favorites_repo, mock_product_repo):
        """Б63: Проверка наличия товара 5 в избранном возвращает True"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        mock_favorites_repo._data[1] = [5]
        
        result = await service.is_favorite(user_id=1, product_id=5)
        
        assert result == True

    @pytest.mark.asyncio
    async def test_b64_is_favorite_false(self, mock_favorites_repo, mock_product_repo):
        """Б64: Проверка отсутствия товара 5 в избранном возвращает False"""
        service = FavoritesService(favorites_repo=mock_favorites_repo, product_repo=mock_product_repo)
        
        result = await service.is_favorite(user_id=4, product_id=5)
        
        assert result == False
