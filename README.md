# QIWI Payout API Tests

Тестовое задание AQA Python

## Описание

Тесты для API выплат QIWI на основе документации:
https://developer.qiwi.com/ru/payout/v1/

> **Важно:** Тесты работают с неработающим сервисом. Используем документацию
> как эталон для проверки форматов ответов.

## Структура проекта
├── tests/
│ ├── test_01_health_check.py # Доступность сервиса
│ ├── test_02_balance.py # Баланс (balance > 0)
│ ├── test_03_create_payment.py # Создание выплаты на 1 рубль
│ └── test_04_payment_status.py # Исполнение платежа
├── postman/
│ └── qiwi_payout_collection.json # Коллекция Postman
├── conftest.py # Фикстуры
└── README.md

## Установка

```bash
pip install httpx pytest pytest-playwright pytest-asyncio playwright
playwright install

# Все тесты
pytest tests/ -v

# По пунктам
pytest tests/test_01_health_check.py -v
pytest tests/test_02_balance.py -v
pytest tests/test_03_create_payment.py -v
pytest tests/test_04_payment_status.py -v

Коллекция Postman
Открыть Postman

Import → postman/qiwi_payout_collection.json

Установить переменные: token, test_account

Запустить коллекцию