import json
from datetime import datetime
from src.utils import load_transactions, calculate_cashback, get_greeting
import pandas as pd
import logging

# Настройка логирования для views
logging.basicConfig(
    filename='logs/views.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def generate_json_response(date_str, file_path):
    current_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    greeting = get_greeting(current_time)

    transactions = load_transactions(file_path)
    today = pd.Timestamp(current_time)

    # Фильтруем транзакции по дате
    start_date = today.replace(day=1)
    filtered_transactions = transactions[
        (pd.to_datetime(transactions['Дата операции']) >= start_date) &
        (pd.to_datetime(transactions['Дата операции']) <= today)
        ]

    cards_summary = filtered_transactions.groupby('Номер карты').agg(
        total_spent=('Сумма операции', 'sum'),
        cashback=('Сумма операции', lambda x: calculate_cashback(x.sum()))
    ).reset_index()

    top_transactions = filtered_transactions.nlargest(5, 'Сумма платежа')[
        ['Дата операции', 'Сумма платежа', 'Категория', 'Описание']].to_dict(orient='records')

    currency_rates = [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]
    stock_prices = [{"stock": "AAPL", "price": 150.12}, {"stock": "AMZN", "price": 3173.18}]

    response = {
        "greeting": greeting,
        "cards": [{"last_digits": str(card)[-4:], "total_spent": total, "cashback": cash} for card, total, cash in
                  zip(cards_summary['Номер карты'], cards_summary['total_spent'], cards_summary['cashback'])],
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    logging.info("JSON response generated successfully.")
    return json.dumps(response, ensure_ascii=False)
