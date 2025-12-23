"""
Блочные тесты модуля уведомлений (NotificationService).
Тесты Б76-Б79.
"""

import pytest
from decimal import Decimal
from app.services.notification_service import NotificationService
from tests.conftest import MockOrder


class TestNotificationService:

    @pytest.fixture
    def notification_service(self, mock_bot, mock_user_repo):
        return NotificationService(
            bot=mock_bot, user_repo=mock_user_repo, config={'admin_ids': [100008, 100009]}
        )

    @pytest.fixture
    def sample_order(self):
        return MockOrder(
            id=1, user_id=1, order_number="ORD-20241201-0001", total=89990,
            contact_name="Иван Тестовый", contact_phone="+7 999 111-11-11",
            contact_address="г. Москва, ул. Тестовая, д. 1"
        )

    @pytest.mark.asyncio
    async def test_b76_notify_order_created(self, notification_service, sample_order, mock_bot):
        """Б76: Уведомление о создании заказа отправляет сообщение пользователю"""
        await notification_service.notify_order_created(sample_order)
        
        assert len(mock_bot.sent_messages) == 1
        assert mock_bot.sent_messages[0]['chat_id'] == 100001
        assert "ORD-20241201-0001" in mock_bot.sent_messages[0]['text']

    @pytest.mark.asyncio
    async def test_b77_notify_status_changed(self, notification_service, mock_bot):
        """Б77: Уведомление об изменении статуса на 'shipped' содержит текст об отправке"""
        order = MockOrder(id=3, user_id=1, order_number="ORD-20241202-0001", total=49990, status='shipped')
        
        await notification_service.notify_status_changed(order)
        
        assert len(mock_bot.sent_messages) == 1
        text = mock_bot.sent_messages[0]['text'].lower()
        assert "отправлен" in text or "🚚" in mock_bot.sent_messages[0]['text']

    @pytest.mark.asyncio
    async def test_b78_notify_payment_success(self, notification_service, mock_bot):
        """Б78: Уведомление об успешной оплате содержит сумму и упоминание чека"""
        order = MockOrder(id=2, user_id=1, order_number="ORD-20241201-0002", total=129990, status='paid')
        
        await notification_service.notify_payment_success(order)
        
        assert len(mock_bot.sent_messages) == 1
        text = mock_bot.sent_messages[0]['text'].lower()
        assert "оплат" in text
        assert "чек" in text

    @pytest.mark.asyncio
    async def test_b79_notify_admin_new_order(self, notification_service, sample_order, mock_bot):
        """Б79: Уведомление админам о новом заказе отправляется всем админам (2 сообщения)"""
        await notification_service.notify_admin_new_order(sample_order)
        
        assert len(mock_bot.sent_messages) == 2
        admin_ids = {msg['chat_id'] for msg in mock_bot.sent_messages}
        assert 100008 in admin_ids
        assert 100009 in admin_ids
