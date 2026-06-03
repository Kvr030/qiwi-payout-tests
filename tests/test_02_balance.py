"""
Пункт 2: Запрос баланса.

Ключевое условие: баланс всегда больше 0.
"""
import time

import httpx


class TestBalance:

    def test_balance_endpoint_returns_200(self, base_url, headers):
        """
        Проверка что эндпоинт баланса отвечает 200.
        """
        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/balance",
                headers=headers
            )

        assert response.status_code == 200, (
            f"Ожидался 200, получили {response.status_code}"
        )

    def test_balance_response_has_required_fields(self, base_url, headers):
        """
        Проверка структуры ответа согласно документации.
        """
        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/balance",
                headers=headers
            )

        data = response.json()

        assert "balance" in data, (
            "Ответ не содержит поле 'balance' - не по документации"
        )
        assert "currency" in data, (
            "Ответ не содержит поле 'currency' - не по документации"
        )

    def test_balance_greater_than_zero(self, base_url, headers):
        """
        Ключевая проверка: баланс всегда больше 0.
        Если баланс = 0 или меньше - выплаты невозможны.
        """
        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/balance",
                headers=headers
            )

        data = response.json()
        balance = data.get("balance")
        currency = data.get("currency", "RUB")

        assert isinstance(balance, (int, float)), (
            f"Баланс должен быть числом, получен тип {type(balance).__name__}"
        )
        assert balance > 0, (
            f"Баланс равен {balance} {currency}, должен быть больше 0"
        )

    def test_balance_currency_is_rub(self, base_url, headers):
        """
        Проверка что валюта баланса - RUB.
        """
        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/balance",
                headers=headers
            )

        data = response.json()
        currency = data.get("currency")

        assert currency == "RUB", (
            f"Ожидалась валюта RUB, получено {currency}"
        )

    def test_balance_response_time(self, base_url, headers):
        """
        Проверка что баланс отдается не дольше 3 секунд.
        """
        with httpx.Client() as client:
            start = time.time()
            response = client.get(
                f"{base_url}/partner/payout/v1/balance",
                headers=headers
            )
            elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 3.0, (
            f"Ответ получен за {elapsed:.2f}с, ожидалось менее 3с"
        )