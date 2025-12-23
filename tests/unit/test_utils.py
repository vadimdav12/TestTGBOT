"""
Блочные тесты вспомогательных функций (Utils).
Тесты Б80-Б82.
"""

import pytest
from decimal import Decimal
from app.utils.helpers import format_price, validate_phone, plural_form


class TestUtils:

    def test_b80_format_price(self):
        """Б80: Форматирование цены 15000 возвращает '15 000 ₽'"""
        result = format_price(15000)
        
        assert result == "15 000 ₽"

    def test_b81_validate_phone_valid(self):
        """Б81: Валидация телефона '+7 999 123-45-67' возвращает True"""
        assert validate_phone("+7 999 123-45-67") == True
        assert validate_phone("+79991234567") == True
        assert validate_phone("8 999 123-45-67") == True
        assert validate_phone("89991234567") == True

    def test_b82_validate_phone_invalid(self):
        """Б82: Валидация невалидного телефона '59991234567' возвращает False"""
        assert validate_phone("59991234567") == False
        assert validate_phone("123456") == False
        assert validate_phone("abcdefghij") == False


class TestUtilsAdditional:
    """Дополнительные тесты утилит"""

    def test_format_price_decimal(self):
        """Форматирование Decimal корректно работает"""
        result = format_price(Decimal('129990'))
        assert result == "129 990 ₽"

    def test_format_price_zero(self):
        """Форматирование нуля"""
        result = format_price(0)
        assert result == "0 ₽"

    def test_plural_form_one(self):
        """Склонение для 1: 'товар'"""
        result = plural_form(1, ('товар', 'товара', 'товаров'))
        assert result == 'товар'

    def test_plural_form_two(self):
        """Склонение для 2: 'товара'"""
        result = plural_form(2, ('товар', 'товара', 'товаров'))
        assert result == 'товара'

    def test_plural_form_five(self):
        """Склонение для 5: 'товаров'"""
        result = plural_form(5, ('товар', 'товара', 'товаров'))
        assert result == 'товаров'

    def test_plural_form_eleven(self):
        """Склонение для 11: 'товаров' (исключение)"""
        result = plural_form(11, ('товар', 'товара', 'товаров'))
        assert result == 'товаров'

    def test_plural_form_twenty_one(self):
        """Склонение для 21: 'товар'"""
        result = plural_form(21, ('товар', 'товара', 'товаров'))
        assert result == 'товар'
