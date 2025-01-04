import os

import pytest
import datetime
import pandas as pd
import json
from unittest.mock import patch, mock_open
from pathlib import Path
from datetime import datetime

import requests

# Импортируем функции из тестируемого модуля
from src.utils import (
    get_data,
    reader_transaction_excel,
    get_dict_transaction,
    get_user_settings,
    get_currency_rates,
    get_stock_price,
    get_top_transactions,
    get_card_expenses,
    filter_transactions_by_date,
    get_greeting,
)


def test_get_data_valid():
    date_str = "01.01.2024 10:00:00"
    expected_date = datetime(2024, 1, 1, 10, 0, 0)
    assert get_data(date_str) == expected_date


def test_get_data_invalid_format():
    with pytest.raises(ValueError):
        get_data("invalid date format")


@pytest.fixture
def sample_excel_data():
    df = pd.DataFrame(
        {
            "Дата операции": ["01.01.2024 10:00:00", "02.01.2024 12:00:00"],
            "Сумма платежа": [100, -50],
            "Номер карты": [1234, 5678],
        }
    )
    return df


@patch("pandas.read_excel")
def test_reader_transaction_excel_success(mock_read_excel, sample_excel_data):
    mock_read_excel.return_value = sample_excel_data
    df = reader_transaction_excel("test.xlsx")
    assert df.equals(sample_excel_data)


@patch("pandas.read_excel", side_effect=FileNotFoundError)
def test_reader_transaction_excel_file_not_found(mock_read_excel):
    with pytest.raises(FileNotFoundError):
        reader_transaction_excel("nonexistent_file.xlsx")


@patch("pandas.read_excel", side_effect=pd.errors.EmptyDataError)
def test_reader_transaction_excel_empty(mock_read_excel):
    with pytest.raises(pd.errors.EmptyDataError):
        reader_transaction_excel("empty_file.xlsx")


@patch("src.utils.pd.read_excel", side_effect=FileNotFoundError)
def test_get_dict_transaction_file_not_found(mock_read_excel):
    with pytest.raises(FileNotFoundError):
        get_dict_transaction("test.xlsx")


# Тесты для функции get_user_settings

def test_get_user_settings_success(tmp_path):
    settings_file = tmp_path / "settings.json"
    settings_data = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "MSFT"]}
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f)
    currencies, stocks = get_user_settings(str(settings_file))
    assert currencies == ["USD", "EUR"]
    assert stocks == ["AAPL", "MSFT"]


def test_get_user_settings_file_not_found():
    currencies, stocks = get_user_settings("nonexistent_file.json")
    assert currencies == []
    assert stocks == []


def test_get_user_settings_invalid_json(tmp_path):
    settings_file = tmp_path / "settings.json"
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write("invalid json")
    currencies, stocks = get_user_settings(str(settings_file))
    assert currencies == []
    assert stocks == []


def test_get_user_settings_missing_key(tmp_path):
    settings_file = tmp_path / "settings.json"
    settings_data = {"user_currencies": ["USD", "EUR"]}
    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f)
    currencies, stocks = get_user_settings(str(settings_file))
    assert currencies == []
    assert stocks == []


# Тесты для функции get_currency_rates

@patch.dict(os.environ, {"API_KEY": "test_api_key"})  # Заменяем API_KEY
@patch("requests.get")
def test_get_currency_rates_success(mock_get):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"quotes": {"USDRUB": 100, "USDEUR": 0.9}}'
    mock_response.json = lambda: {"quotes": {"USDRUB": 100, "USDEUR": 0.9}}
    mock_get.return_value = mock_response
    rates = get_currency_rates(["USD", "EUR"])
    assert rates == [{"currency": "USD", "rate": 100.0}, {"currency": "EUR", "rate": 111.11}]


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch("requests.get")
def test_get_currency_rates_api_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Test error")
    rates = get_currency_rates(["USD", "EUR"])
    assert rates is None


@patch.dict(os.environ, {"API_KEY": "test_api_key"})
@patch("requests.get")
def test_get_currency_rates_missing_data(mock_get):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"quotes": {"USDEUR": 0.9}}'
    mock_response.json = lambda: {"quotes": {"USDEUR": 0.9}}
    mock_get.return_value = mock_response
    rates = get_currency_rates(["USD", "EUR"])
    assert rates is None


@patch.dict(os.environ, {}, clear=True) #Проверка отсутствия API ключа
def test_get_currency_rates_no_api_key():
    rates = get_currency_rates(["USD", "EUR"])
    assert rates is None


# Тесты для функции get_stock_price (аналогично предыдущим, используя mock)
@patch.dict(os.environ, {"API_KEY_STOCK": "test_api_key"})
@patch("requests.get")
def test_get_stock_price_success(mock_get):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"Global Quote": {"05. price": "150.00"}}'
    mock_response.json = lambda: {"Global Quote": {"05. price": "150.00"}}
    mock_get.return_value = mock_response
    prices = get_stock_price(["AAPL"])
    assert prices == [{"stock": "AAPL", "price": 150.0}]


@patch.dict(os.environ, {"API_KEY_STOCK": "test_api_key"})
@patch("requests.get")
def test_get_stock_price_api_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Test error")
    prices = get_stock_price(["AAPL"])
    assert prices == []


@patch.dict(os.environ, {"API_KEY_STOCK": "test_api_key"})
@patch("requests.get")
def test_get_stock_price_invalid_data(mock_get):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"Global Quote": {}}'
    mock_response.json = lambda: {"Global Quote": {}}
    mock_get.return_value = mock_response
    prices = get_stock_price(["AAPL"])
    assert prices == []


@patch.dict(os.environ, {}, clear=True)
def test_get_stock_price_no_api_key():
    prices = get_stock_price(["AAPL"])
    assert prices == []


#Тесты для функции get_top_transactions
@pytest.fixture
def sample_transactions_df():
    data = {
        "Дата операции": ["01.01.2024 10:00:00", "02.01.2024 10:00:00", "03.01.2024 10:00:00", "04.01.2024 10:00:00", "05.01.2024 10:00:00", "06.01.2024 10:00:00"],
        "Сумма платежа": [100, 50, 200, 150, 250, 300],
        "Категория": ["Продукты", "Транспорт", "Развлечения", "Продукты", "Транспорт", "Развлечения"],
        "Описание": ["Магазин", "Такси", "Кино", "Кафе", "Метро", "Концерт"],
    }
    df = pd.DataFrame(data)
    return df


def test_get_top_transactions_success(sample_transactions_df):
    top_transactions = get_top_transactions(sample_transactions_df)
    assert len(top_transactions) == 5
    assert top_transactions[0]["amount"] == 50


def test_get_top_transactions_empty_df():
    top_transactions = get_top_transactions(pd.DataFrame())
    assert top_transactions == []


#Тесты для функции get_card_expenses
@pytest.fixture
def sample_card_expenses_df():
    data = {
        "Номер карты": [1234, 1234, 5678, 5678, 1234],
        "Сумма платежа": [-100, -50, -200, -100, -30],
    }
    df = pd.DataFrame(data)
    return df


def test_get_card_expenses_success(sample_card_expenses_df):
    expenses = get_card_expenses(sample_card_expenses_df)
    assert len(expenses) == 2
    assert expenses[0]["total_spent"] == 180
    assert expenses[0]["cashback"] == 1.8


def test_get_card_expenses_empty_df():
    expenses = get_card_expenses(pd.DataFrame())
    assert expenses == []


#Тесты для функции filter_transactions_by_date
@pytest.fixture
def sample_filter_transactions_df():
    data = {
        "Дата операции": ["01.01.2024 10:00:00", "15.01.2024 10:00:00", "01.02.2024 10:00:00", "18.02.2024 10:00:00"],
        "Сумма платежа": [100, 50, 200, 150],
    }
    df = pd.DataFrame(data)
    return df


def test_filter_transactions_by_date_success(sample_filter_transactions_df):
    filtered_df = filter_transactions_by_date(sample_filter_transactions_df, "15.01.2024 10:00:00")
    assert len(filtered_df) == 2


def test_filter_transactions_by_date_empty_df():
    filtered_df = filter_transactions_by_date(pd.DataFrame(), "15.01.2024 10:00:00")
    assert filtered_df is None


def test_get_greeting_morning():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0)
        assert get_greeting() == "Доброе утро"


def test_get_greeting_afternoon():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 14, 0, 0)
        assert get_greeting() == "Добрый день"


def test_get_greeting_evening():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 19, 0, 0)
        assert get_greeting() == "Добрый вечер"


def test_get_greeting_night():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 23, 0, 0)
        assert get_greeting() == "Доброй ночи"


def test_get_greeting_midnight():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 1, 1, 0, 0, 0)
        assert get_greeting() == "Доброй ночи"


def test_get_greeting_early_morning():
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2024,1,1,4,0,0)
        assert get_greeting() == "Доброе утро"

