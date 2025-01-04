from src.views import main
from unittest.mock import patch, Mock


def test_main_success():
    mock_get_greeting = Mock(return_value="Доброе утро")
    mock_filter_transactions_by_date = Mock(return_value=[{"amount": 100}])
    mock_get_card_expenses = Mock(return_value=[{"card": 1234, "amount": 500}])
    mock_get_top_transactions = Mock(return_value=[{"amount": 200}])
    mock_get_currency_rates = Mock(return_value=[{"currency": "USD", "rate": 100}])
    mock_get_stock_price = Mock(return_value=[{"stock": "AAPL", "price": 150}])

    df_transactions = [1,2,3]
    date = "2024-01-01"
    user_currencies = ["USD"]
    user_stocks = ["AAPL"]

    with patch('src.views.get_greeting', mock_get_greeting), \
         patch('src.views.filter_transactions_by_date', mock_filter_transactions_by_date), \
         patch('src.views.get_card_expenses', mock_get_card_expenses), \
         patch('src.views.get_top_transactions', mock_get_top_transactions), \
         patch('src.views.get_currency_rates', mock_get_currency_rates), \
         patch('src.views.get_stock_price', mock_get_stock_price):
         result = main(df_transactions, date, user_currencies, user_stocks)
         expected_result = """{
    "greeting": "Доброе утро",
    "cards": [
        {
            "card": 1234,
            "amount": 500
        }
    ],
    "top_transactions": [
        {
            "amount": 200
        }
    ],
    "currency_rates": [
        {
            "currency": "USD",
            "rate": 100
        }
    ],
    "stock_prices": [
        {
            "stock": "AAPL",
            "price": 150
        }
    ]
}"""
         assert result == expected_result
