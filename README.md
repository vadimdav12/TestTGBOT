# Тестирование Telegram-бота интернет-магазина

## Структура

```
tests/
├── conftest.py                    # Фикстуры и моки
├── unit/                          # Блочные тесты (Б1-Б82)
│   ├── test_catalog.py            # Б1-Б14
│   ├── test_cart.py               # Б15-Б29
│   ├── test_order.py              # Б30-Б40
│   ├── test_discount.py           # Б41-Б48
│   ├── test_search.py             # Б49-Б56
│   ├── test_favorites.py          # Б57-Б64
│   ├── test_profile.py            # Б65-Б70
│   ├── test_receipt.py            # Б71-Б75
│   ├── test_notification.py       # Б76-Б79
│   └── test_utils.py              # Б80-Б82
├── integration/                   # Интеграционные тесты (И1-И12)
│   └── test_integration.py
└── load/                          # Нагрузочные тесты (Н1-Н10)
    └── test_load.py
```

---

## Блочные тесты (Б1-Б82)

### Каталог (Б1-Б14) — `test_catalog.py`

| № | Тест | Описание |
|---|------|----------|
| Б1 | `test_b01_get_categories_returns_active` | Получение списка категорий возвращает 5 активных |
| Б2 | `test_b02_get_products_by_category_smartphones` | Получение товаров категории 1 возвращает 4 смартфона |
| Б3 | `test_b03_get_products_nonexistent_category` | Несуществующая категория 999 возвращает [] |
| Б4 | `test_b04_get_product_by_id` | Товар id=3: Samsung Galaxy S24, цена=79990, остаток=10 |
| Б5 | `test_b05_get_product_nonexistent` | Несуществующий товар id=99999 возвращает None |
| Б6 | `test_b06_get_product_stock` | Остаток товара id=3 равен 10 |
| Б7 | `test_b07_create_product_success` | Создание товара присваивает id |
| Б8 | `test_b08_create_product_invalid_data_raises_error` | Невалидные данные вызывают ValidationError |
| Б9 | `test_b09_update_product` | Обновление товара id=3 меняет цену и остаток |
| Б10 | `test_b10_delete_product` | Удаление товара id=50 ставит is_active=False |
| Б11 | `test_b11_create_category` | Создание категории "Новая" |
| Б12 | `test_b12_create_duplicate_category_raises_error` | Дубликат "Смартфоны" вызывает DuplicateCategoryError |
| Б13 | `test_b13_delete_empty_category` | Удаление пустой категории успешно |
| Б14 | `test_b14_delete_nonempty_category_raises_error` | Категория с товарами вызывает CategoryNotEmptyError |

### Корзина (Б15-Б29) — `test_cart.py`

| № | Тест | Описание |
|---|------|----------|
| Б15 | `test_b15_get_cart_with_items` | Корзина пользователя 1 содержит 2 позиции |
| Б16 | `test_b16_get_empty_cart` | Корзина нового пользователя пуста |
| Б17 | `test_b17_add_item_new_user` | Добавление товара создаёт запись |
| Б18 | `test_b18_add_item_existing_increases_qty` | Повторное добавление увеличивает qty |
| Б19 | `test_b19_add_item_exceeds_stock_raises_error` | Превышение остатка вызывает InsufficientStockError |
| Б20 | `test_b20_add_item_zero_stock_raises_error` | Товар с остатком 0 вызывает ошибку |
| Б21 | `test_b21_update_item_qty` | Изменение qty обновляет запись |
| Б22 | `test_b22_update_item_qty_zero_removes` | qty=0 удаляет товар из корзины |
| Б23 | `test_b23_update_nonexistent_item_raises_error` | Несуществующий товар вызывает CartItemNotFoundError |
| Б24 | `test_b24_remove_item` | Удаление товара из корзины |
| Б25 | `test_b25_remove_nonexistent_item_idempotent` | Удаление несуществующего — идемпотентно |
| Б26 | `test_b26_clear_cart` | Очистка корзины удаляет все записи |
| Б27 | `test_b27_calc_totals` | Расчёт итогов: subtotal, items_count, positions_count |
| Б28 | `test_b28_check_stock_available` | Проверка остатка: stock=10, qty=5 → True |
| Б29 | `test_b29_check_stock_not_available` | Проверка остатка: stock=3, qty=5 → False |

### Заказы (Б30-Б40) — `test_order.py`

| № | Тест | Описание |
|---|------|----------|
| Б30 | `test_b30_create_order_success` | Создание заказа: запись + резерв + очистка корзины |
| Б31 | `test_b31_create_order_empty_cart_raises_error` | Пустая корзина вызывает EmptyCartError |
| Б32 | `test_b32_get_order_success` | Получение заказа по id |
| Б33 | `test_b33_get_order_wrong_user_returns_none` | Чужой заказ возвращает None |
| Б34 | `test_b34_list_orders` | Список заказов пользователя |
| Б35 | `test_b35_update_status_success` | Изменение статуса заказа |
| Б36 | `test_b36_update_status_invalid_transition_raises_error` | cancelled→shipped вызывает InvalidStatusTransitionError |
| Б37 | `test_b37_cancel_order_success` | Отмена заказа меняет статус и возвращает товар |
| Б38 | `test_b38_cancel_shipped_order_raises_error` | Отмена shipped вызывает OrderCannotBeCancelledError |
| Б39 | `test_b39_reserve_stock` | Резервирование уменьшает остаток |
| Б40 | `test_b40_release_stock` | Снятие резерва увеличивает остаток |

### Скидки (Б41-Б48) — `test_discount.py`

| № | Тест | Описание |
|---|------|----------|
| Б41 | `test_b41_validate_promo_active` | SAVE10: valid=True, 10% |
| Б42 | `test_b42_validate_promo_expired` | OLD: valid=False, "истёк" |
| Б43 | `test_b43_validate_promo_already_used` | USED: valid=False, "использован" |
| Б44 | `test_b44_validate_promo_not_found` | Несуществующий: valid=False |
| Б45 | `test_b45_apply_percent_discount` | SAVE10 к 100000₽ = скидка 10000₽ |
| Б46 | `test_b46_apply_fixed_discount` | FIXED5000 = скидка 5000₽ |
| Б47 | `test_b47_auto_discount_50k` | Автоскидка 5% при 50000₽ |
| Б48 | `test_b48_check_promo_usage` | Проверка использования промокода |

### Поиск (Б49-Б56) — `test_search.py`

| № | Тест | Описание |
|---|------|----------|
| Б49 | `test_b49_normalize_query` | Нормализация: пробелы, регистр |
| Б50 | `test_b50_levenshtein_distance` | Расстояние Левенштейна |
| Б51 | `test_b51_fuzzy_match_high_similarity` | Нечёткое сопоставление score>=0.8 |
| Б52 | `test_b52_search_exact_match` | Точный поиск "iPhone 15" |
| Б53 | `test_b53_search_fuzzy_match` | Нечёткий поиск с опечатками |
| Б54 | `test_b54_search_cyrillic_transliteration` | Поиск на кириллице |
| Б55 | `test_b55_search_empty_query` | Пустой запрос → [] |
| Б56 | `test_b56_search_no_results` | Несуществующий товар → [] |

### Избранное (Б57-Б64) — `test_favorites.py`

| № | Тест | Описание |
|---|------|----------|
| Б57 | `test_b57_add_favorite` | Добавление в избранное |
| Б58 | `test_b58_add_favorite_idempotent` | Повторное добавление — идемпотентно |
| Б59 | `test_b59_add_favorite_nonexistent_product` | Несуществующий товар → ProductNotFoundError |
| Б60 | `test_b60_remove_favorite` | Удаление из избранного |
| Б61 | `test_b61_remove_favorite_idempotent` | Удаление несуществующего — идемпотентно |
| Б62 | `test_b62_list_favorites` | Список избранного |
| Б63 | `test_b63_is_favorite_true` | Проверка наличия → True |
| Б64 | `test_b64_is_favorite_false` | Проверка отсутствия → False |

### Профиль (Б65-Б70) — `test_profile.py`

| № | Тест | Описание |
|---|------|----------|
| Б65 | `test_b65_get_profile` | Получение профиля с количеством заказов |
| Б66 | `test_b66_update_profile_name` | Обновление имени |
| Б67 | `test_b67_update_profile_invalid_phone` | Невалидный телефон → ValidationError |
| Б68 | `test_b68_get_order_history` | История заказов |
| Б69 | `test_b69_repeat_order` | Повторение заказа |
| Б70 | `test_b70_repeat_order_wrong_user` | Чужой заказ → OrderNotFoundError |

### Чеки (Б71-Б75) — `test_receipt.py`

| № | Тест | Описание |
|---|------|----------|
| Б71 | `test_b71_generate_receipt_pdf` | Генерация PDF размером 1KB-500KB |
| Б72 | `test_b72_generate_receipt_nonexistent_order` | Несуществующий заказ → OrderNotFoundError |
| Б73 | `test_b73_generate_receipt_unpaid_order` | Неоплаченный заказ → OrderNotPaidError |
| Б74 | `test_b74_get_receipt_data` | Получение данных чека |
| Б75 | `test_b75_send_receipt` | Отправка чека пользователю |

### Уведомления (Б76-Б79) — `test_notification.py`

| № | Тест | Описание |
|---|------|----------|
| Б76 | `test_b76_notify_order_created` | Уведомление о создании заказа |
| Б77 | `test_b77_notify_status_changed` | Уведомление об изменении статуса |
| Б78 | `test_b78_notify_payment_success` | Уведомление об оплате |
| Б79 | `test_b79_notify_admin_new_order` | Уведомление админам |

### Утилиты (Б80-Б82) — `test_utils.py`

| № | Тест | Описание |
|---|------|----------|
| Б80 | `test_b80_format_price` | Форматирование цены: 15000 → "15 000 ₽" |
| Б81 | `test_b81_validate_phone_valid` | Валидация корректного телефона |
| Б82 | `test_b82_validate_phone_invalid` | Валидация некорректного телефона |

---

## Интеграционные тесты (И1-И12) — `test_integration.py`

| № | Тест | Описание |
|---|------|----------|
| И1 | `test_i01_catalog_navigation` | Навигация: категории → товары категории |
| И2 | `test_i02_catalog_product_details` | Просмотр товара: список → детали с остатком |
| И3 | `test_i03_add_to_cart_with_stock_check` | Добавление в корзину с проверкой остатка |
| И4 | `test_i04_add_to_cart_insufficient_stock` | Добавление при недостатке товара → ошибка |
| И5 | `test_i05_checkout_flow` | Полное оформление: корзина → скидки → заказ → уведомление |
| И6 | `test_i06_checkout_with_invalid_phone` | Оформление с невалидным телефоном → валидация |
| И7 | `test_i07_payment_creates_session` | Инициализация оплаты создаёт платёжную сессию |
| И8 | `test_i08_payment_webhook_updates_order` | Webhook оплаты: статус → чек → отправка |
| И9 | `test_i09_search_cyrillic_finds_product` | Поиск на кириллице → добавление в корзину |
| И10 | `test_i10_favorites_workflow` | Избранное → просмотр → в корзину |
| И11 | `test_i11_promocode_applies_to_cart` | Применение промокода к корзине |
| И12 | `test_i12_admin_creates_product` | Админ создаёт товар через админ-панель |

---

## Нагрузочные тесты (Н1-Н10) — `test_load.py`

| № | Тест | Описание |
|---|------|----------|
| Н1 | `test_h01_catalog_100_concurrent_requests` | 100 параллельных запросов к каталогу, время < 500ms |
| Н2 | `test_h02_products_by_category_load` | 100 запросов к товарам категорий, RPS > 50 |
| Н3 | `test_h03_cart_50_concurrent_users` | 50 пользователей добавляют товары одновременно |
| Н4 | `test_h04_calc_totals_1000_times` | 1000 расчётов итогов корзины, среднее < 1ms |
| Н5 | `test_h05_search_100_queries` | 100 параллельных поисковых запросов |
| Н6 | `test_h06_fuzzy_search_50_queries` | 50 нечётких запросов с опечатками |
| Н7 | `test_h07_promo_validation_200_requests` | 200 проверок промокодов |
| Н8 | `test_h08_discount_calculation_100_carts` | 100 расчётов скидок для разных корзин |
| Н9 | `test_h09_mixed_operations_200` | 200 смешанных операций, успешность ≥ 99% |
| Н10 | `test_h10_sustained_load_2_seconds` | Устойчивая нагрузка 2 секунды, > 100 запросов |

---

## Запуск тестов

```bash
# Все тесты
pytest

# Только блочные
pytest tests/unit/

# Только интеграционные
pytest tests/integration/

# Только нагрузочные
pytest tests/load/

# Конкретный файл
pytest tests/unit/test_cart.py

# Конкретный тест
pytest tests/unit/test_cart.py::TestCartService::test_b15_get_cart_with_items
```

## Зависимости

```
pytest>=7.0.0
pytest-asyncio>=0.21.0
```
