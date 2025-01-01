import logging
from pathlib import Path
import json
from src.utils import (
    get_data,
    reader_transaction_excel,
    get_top_transactions,
    filter_transactions_by_date,
    get_card_expenses,
    get_currency_rates,
    get_stock_price,
    get_greeting,
)

ROOT_PATH = Path(__file__).resolve().parent.parent


logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("..\\logs\\views.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def main(df_transactions, date, user_currencies, user_stocks):
    "Главная функция, делающая вывод на главную страницу"
    greeting = get_greeting()
    transactions = filter_transactions_by_date(df_transactions, date)
    cards = get_card_expenses(df_transactions)
    top_trans = get_top_transactions(df_transactions)
    currency_rates = get_currency_rates(user_currencies)
    stock_prices = get_stock_price(user_stocks)

    date_json = json.dumps(
        {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_trans,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        },
        indent=4,
        ensure_ascii=False,
    )
    return date_json
