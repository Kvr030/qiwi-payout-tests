"""
Пункт 1: Проверка доступности сервиса.

Вызываем публичный метод API (GET /rates) и проверяем формат ответа.
Если формат отличается от документации - с сервисом проблемы.
"""
import time

import httpx


class TestServiceAvailability:

    def test_server_responds(self, base_url):
        """
        Проверка что сервер отвечает на запрос.
        Сервис считается доступным если вернул 200, 401 или 404.
        """
        with httpx.Client() as client:
            response = client.get(f"{base_url}/api/v2/rates")

        assert response.status_code in [200, 401, 404], (
            f"Сервис недоступен, статус ответа: {response.status_code}"
        )

    def test_response_is_json(self, base_url):
        """
        Проверка что ответ в формате JSON (если статус не 404).
        Для 404 допускается пустое тело.
        """
        with httpx.Client() as client:
            response = client.get(f"{base_url}/api/v2/rates")

        if response.status_code == 404:
            return

        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type, (
            f"Ответ не в JSON формате, content-type: {content_type}"
        )

        data = response.json()
        assert isinstance(data, dict), (
            f"Формат ответа не соответствует документации, "
            f"ожидался объект, получен {type(data).__name__}"
        )

    def test_response_time(self, base_url):
        """
        Проверка что сервер отвечает быстрее 10 секунд.
        """
        with httpx.Client(timeout=15.0) as client:
            start = time.time()
            response = client.get(f"{base_url}/api/v2/rates")
            elapsed = time.time() - start

        assert response.status_code in [200, 401, 404]
        assert elapsed < 10.0, (
            f"Слишком долгий ответ: {elapsed:.2f}с при лимите 10с"
        )