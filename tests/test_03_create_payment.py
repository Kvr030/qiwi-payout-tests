"""
Пункт 3: Создание платежа на 1 рубль.
"""
import uuid

import httpx
import pytest


class TestCreatePayment:

    @pytest.fixture
    def claim_id(self):
        return f"test-{uuid.uuid4()}"

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

    def test_create_payment_returns_success(self, base_url, headers, payout_data):
        """
        Проверка что выплата создается (статус 200 или 201).
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )

        assert response.status_code in [200, 201], (
            f"Ожидался 200 или 201, получен {response.status_code}"
        )

    def test_create_payment_response_has_id(self, base_url, headers, payout_data):
        """
        Проверка что ответ содержит id заявки.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )

        data = response.json()

        assert "id" in data, (
            "Ответ не содержит поле 'id' - не по документации"
        )
        assert data["id"] == payout_data["id"], (
            f"id в ответе ({data['id']}) не совпадает с отправленным ({payout_data['id']})"
        )

    def test_create_payment_response_has_status(self, base_url, headers, payout_data):
        """
        Проверка что ответ содержит статус заявки.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )

        data = response.json()

        assert "status" in data, (
            "Ответ не содержит поле 'status' - не по документации"
        )

        valid_statuses = ["NEW", "ACCEPTED", "PROCESSING"]
        assert data["status"] in valid_statuses, (
            f"Статус '{data['status']}' не входит в допустимые: {valid_statuses}"
        )

    def test_create_payment_sum_is_correct(self, base_url, headers, payout_data):
        """
        Проверка что сумма выплаты в ответе равна 1.00 RUB.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )

        data = response.json()

        if "sum" in data:
            assert data["sum"]["amount"] == 1.00, (
                f"Сумма в ответе {data['sum']['amount']}, ожидалось 1.00"
            )
            assert data["sum"]["currency"] == "RUB", (
                f"Валюта в ответе {data['sum']['currency']}, ожидалось RUB"
            )

    def test_create_payment_without_token_fails(self, base_url, payout_data):
        """
        Проверка что запрос без токена возвращает 401 или 403.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                json=payout_data
            )

        assert response.status_code in [401, 403], (
            f"Без токена ожидался 401 или 403, получен {response.status_code}"
        )

    def test_create_payment_duplicate_id_fails(self, base_url, headers, payout_data):
        """
        Проверка что повторный запрос с тем же id возвращает 409 Conflict.
        """
        with httpx.Client() as client:
            first_response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )

            second_response = client.post(
                f"{base_url}/partner/payout/v1/claims",
                headers=headers,
                json=payout_data
            )

        assert first_response.status_code in [200, 201], (
            f"Первый запрос: ожидался 200 или 201, получен {first_response.status_code}"
        )
        assert second_response.status_code == 409, (
            f"Повторный запрос: ожидался 409 Conflict, получен {second_response.status_code}"
        )