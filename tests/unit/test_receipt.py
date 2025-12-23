"""
Блочные тесты модуля чеков (ReceiptService).
Тесты Б71-Б75.
"""

import pytest
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock
from app.services.receipt_service import ReceiptService
from app.exceptions import OrderNotFoundError, OrderNotPaidError
from tests.conftest import MockOrderItem


class TestReceiptService:

    @pytest.fixture
    def receipt_service(self, mock_order_repo, mock_bot, tmp_path):
        mock_order_repo.get_order_items = AsyncMock(return_value=[
            MockOrderItem(1, 2, 3, "Samsung Galaxy S24", Decimal('79990'), 1),
            MockOrderItem(2, 2, 9, "AirPods Pro 2", Decimal('24990'), 2)
        ])
        return ReceiptService(
            order_repo=mock_order_repo, bot=mock_bot, receipts_dir=str(tmp_path / "receipts")
        )

    @pytest.mark.asyncio
    async def test_b71_generate_receipt_pdf(self, receipt_service):
        """Б71: Генерация PDF-чека для заказа 2 создаёт файл размером 1KB-500KB"""
        filepath = await receipt_service.generate_receipt_pdf(order_id=2)
        
        assert Path(filepath).exists()
        size = Path(filepath).stat().st_size
        assert 1000 <= size <= 500000

    @pytest.mark.asyncio
    async def test_b72_generate_receipt_nonexistent_order(self, mock_order_repo, tmp_path):
        """Б72: Генерация чека для несуществующего заказа 99999 вызывает OrderNotFoundError"""
        service = ReceiptService(order_repo=mock_order_repo, receipts_dir=str(tmp_path))
        
        with pytest.raises(OrderNotFoundError) as exc_info:
            await service.generate_receipt_pdf(order_id=99999)
        
        assert exc_info.value.order_id == 99999

    @pytest.mark.asyncio
    async def test_b73_generate_receipt_unpaid_order(self, mock_order_repo, tmp_path):
        """Б73: Генерация чека для неоплаченного заказа 1 вызывает OrderNotPaidError"""
        service = ReceiptService(order_repo=mock_order_repo, receipts_dir=str(tmp_path))
        
        with pytest.raises(OrderNotPaidError) as exc_info:
            await service.generate_receipt_pdf(order_id=1)
        
        assert exc_info.value.order_id == 1

    @pytest.mark.asyncio
    async def test_b74_get_receipt_data(self, receipt_service):
        """Б74: Получение данных чека возвращает номер заказа, позиции и итог"""
        data = await receipt_service.get_receipt_data(order_id=2)
        
        assert data.order_number == "ORD-20241201-0002"
        assert len(data.items) == 2
        assert data.total == Decimal('129990')

    @pytest.mark.asyncio
    async def test_b75_send_receipt(self, receipt_service, mock_bot, tmp_path):
        """Б75: Отправка чека пользователю вызывает bot.send_document"""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test")
        
        result = await receipt_service.send_receipt(user_id=100001, receipt_path=str(test_file))
        
        assert result == True
        assert len(mock_bot.sent_documents) == 1
