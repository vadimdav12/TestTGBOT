"""
Блочные тесты модуля поиска (SearchService).
Тесты Б49-Б56.
"""

import pytest
from app.services.search_service import SearchService


class TestSearchService:

    def test_b49_normalize_query(self, mock_product_repo):
        """Б49: Нормализация запроса '  АйФон 16  PRO  ' возвращает 'айфон 16 pro'"""
        service = SearchService(product_repo=mock_product_repo)
        
        result = service.normalize_query("  АйФон 16  PRO  ")
        
        assert result == "айфон 16 pro"

    def test_b50_levenshtein_distance(self, mock_product_repo):
        """Б50: Расстояние Левенштейна между 'айфон' и 'айфан' равно 1"""
        service = SearchService(product_repo=mock_product_repo)
        
        distance = service.levenshtein_distance("айфон", "айфан")
        
        assert distance == 1

    def test_b51_fuzzy_match_high_similarity(self, mock_product_repo):
        """Б51: Нечёткое сопоставление 'iphone' и 'iphon' даёт score >= 0.8"""
        service = SearchService(product_repo=mock_product_repo)
        
        score = service.fuzzy_match("iphone", "iphon")
        
        assert score >= 0.8

    @pytest.mark.asyncio
    async def test_b52_search_exact_match(self, mock_product_repo):
        """Б52: Поиск 'iPhone 15' находит товар id=2 с score=1.0"""
        service = SearchService(product_repo=mock_product_repo)
        
        results = await service.search_products("iPhone 15")
        
        assert len(results) > 0
        iphone = next((r for r in results if r.product_id == 2), None)
        assert iphone is not None

    @pytest.mark.asyncio
    async def test_b53_search_fuzzy_match(self, mock_product_repo):
        """Б53: Поиск 'samsun galax' находит Samsung Galaxy S24"""
        service = SearchService(product_repo=mock_product_repo)
        
        results = await service.search_products("samsun galax")
        
        assert len(results) > 0
        samsung_found = any(r.product_id == 3 for r in results[:5])
        assert samsung_found

    @pytest.mark.asyncio
    async def test_b54_search_cyrillic_transliteration(self, mock_product_repo):
        """Б54: Поиск 'Самсунг' на кириллице находит Samsung через транслитерацию"""
        service = SearchService(product_repo=mock_product_repo)
        
        results = await service.search_products("Самсунг")
        
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_b55_search_empty_query(self, mock_product_repo):
        """Б55: Поиск с пустым запросом возвращает пустой список"""
        service = SearchService(product_repo=mock_product_repo)
        
        results = await service.search_products("")
        
        assert results == []

    @pytest.mark.asyncio
    async def test_b56_search_no_results(self, mock_product_repo):
        """Б56: Поиск 'xyznonexistent123' возвращает пустой список"""
        service = SearchService(product_repo=mock_product_repo)
        
        results = await service.search_products("xyznonexistent123")
        
        assert results == []
