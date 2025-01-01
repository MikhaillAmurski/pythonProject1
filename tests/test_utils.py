import pytest
import pandas as pd
import json
from unittest.mock import patch, MagicMock
from src.views import generate_json_response


@pytest.fixture
def mock_transactions():
    """Фикстура с поддельными транзакциями."""
    return pd.DataFrame({
        'Дата операции': pd.to_datetime(['2023-12-01', '2023-12-05', '2023-12-07']),
        'Номер карты': ['1234', '5678', '1234'],
        'Сумма операции': [2000, 3000, 1500],
        'Сумма платежа': [2000, 3000, 1500],
        'Категория': ['Еда', 'Транспорт', 'Еда'],
        'Описание': ['Оплата', 'Перевод', 'Оплата']
    })


@patch('src.views.load_transactions')
@patch('src.views.calculate_cashback')
@patch('src.views.get_greeting')
def test_generate_json_response(mock_get_greeting, mock_calculate_cashback, mock_load_transactions, mock_transactions):
    """Тест функции generate_json_response с использованием mock."""

    # Настройка моков
    mock_load_transactions.return_value = mock_transactions
    mock_calculate_cashback.return_value = 15.0
    mock_get_greeting.return_value = "Добрый день"

    date_input = "2023-12-07 15:30:00"
    path_to_excel = "data/operations.xlsx"

    json_response = generate_json_response(date_input, path_to_excel)

    # Проверяем содержимое JSON-ответа
    response = json.loads(json_response)
    assert response['greeting'] == "Добрый день"
    assert len(response['cards']) == 2
    assert response['cards'][0]['last_digits'] == "1234"
    assert response['cards'][0]['total_spent'] == 3500  # 2000 + 1500
    assert response['cards'][0]['cashback'] == 15.0

    # Проверяем вызовы моков
    mock_load_transactions.assert_called_once_with(path_to_excel)
    mock_calculate_cashback.assert_called_once()
    mock_get_greeting.assert_called_once_with(pd.to_datetime(date_input))
