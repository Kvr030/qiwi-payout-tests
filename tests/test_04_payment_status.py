"""
Пункт 4: Проверка исполнения платежа.

Проверяем что созданный платеж переходит в финальный статус.
"""
import time
import uuid

import httpx
import pytest


class TestPaymentExecution:

    @pytest.fixture
    def claim_id(self):
        return f"test-exec-{uuid.uuid4()}"

    @pytest.fixture
    def payout_data(self, claim_id, test_account):
        return {
            "id": claim_id,
            "sum": {
                "amount": 1.00,
                "currency": "RUB"
            },
            "paymentMethod": {
                "type": "Account",
                "accountId": "643"
            },
            "purpose": "Тестовый платеж AQA на 1 рубль",
            "fields": {
                "account": test_account
            }
        }

    @pytest.fixture(scope="class")
    def created_claim(self, base_url, headers, payout_data):
        """
        Создает выплату и возвращает ответ API.
        Выполняется один раз для всех тестов в классе.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )
        return response.json()

    def test_get_payment_status_by_id(self, base_url, headers, created_claim):
        """
        Проверка получения статуса выплаты по её id.
        """
        claim_id = created_claim["id"]

        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/claims/{claim_id}",
                headers=headers
            )

        assert response.status_code == 200, (
            f"Не удалось получить статус заявки, статус ответа: {response.status_code}"
        )

        data = response.json()
        assert data["id"] == claim_id, (
            f"id в ответе ({data['id']}) не совпадает с запрошенным ({claim_id})"
        )

    def test_payment_status_is_valid(self, base_url, headers, created_claim):
        """
        Проверка что статус заявки принимает допустимые значения.
        """
        claim_id = created_claim["id"]

        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/claims/{claim_id}",
                headers=headers
            )

        data = response.json()
        status = data.get("status")

        valid_statuses = ["NEW", "ACCEPTED", "PROCESSING", "COMPLETED", "REJECTED"]
        assert status in valid_statuses, (
            f"Недопустимый статус '{status}'. Допустимые значения: {valid_statuses}"
        )

    def test_payment_sum_unchanged(self, base_url, headers, created_claim):
        """
        Проверка что сумма выплаты в ответе равна отправленной (1.00 RUB).
        """
        claim_id = created_claim["id"]

        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/claims/{claim_id}",
                headers=headers
            )

        data = response.json()

        if "sum" in data:
            assert data["sum"]["amount"] == 1.00, (
                f"Сумма изменилась: было 1.00, стало {data['sum']['amount']}"
            )
            assert data["sum"]["currency"] == "RUB", (
                f"Валюта изменилась: было RUB, стало {data['sum']['currency']}"
            )

    def test_payment_reaches_final_status(self, base_url, headers, created_claim):
        """
        Проверка что выплата переходит в финальный статус.
        Опрашиваем статус с интервалом 10 секунд, до 5 попыток.
        """
        claim_id = created_claim["id"]
        max_attempts = 5
        delay = 10
        final_status = None

        with httpx.Client() as client:
            for _ in range(max_attempts):
                response = client.get(
                    f"{base_url}/partner/payout/v1/claims/{claim_id}",
                    headers=headers
                )
                status = response.json().get("status")

                if status in ["COMPLETED", "REJECTED"]:
                    final_status = status
                    break

                time.sleep(delay)

        assert final_status is not None, (
            f"Заявка не достигла финального статуса за {max_attempts * delay} секунд"
        )

    def test_nonexistent_claim_returns_404(self, base_url, headers):
        """
        Проверка что запрос несуществующей заявки возвращает 404.
        """
        fake_id = "00000000-0000-0000-0000-000000000000"

        with httpx.Client() as client:
            response = client.get(
                f"{base_url}/partner/payout/v1/claims/{fake_id}",
                headers=headers
            )

        assert response.status_code == 404, (
            f"Ожидался 404, получен {response.status_code}"
        )