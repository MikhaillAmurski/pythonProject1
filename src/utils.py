import logging
import pandas as pd
from datetime import datetime

# Настройка логирования для utils
logging.basicConfig(
    filename='logs/utils.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def load_transactions(file_path):
    """Загрузить транзакции из Excel файла."""
    logging.info(f"Loading transactions from {file_path}")
    try:
        transactions = pd.read_excel(file_path)
        logging.info("Transactions loaded successfully.")
        return transactions
    except Exception as e:
        logging.error(f"Error loading transactions: {e}")
        raise


def calculate_cashback(amount):
    """Вычислить кешбэк на основе суммы."""
    cashback = amount * 0.01  # 1% кешбэк
    logging.debug(f"Calculated cashback: {cashback} for amount: {amount}")
    return cashback


def get_greeting(current_time):
    """Получить приветствие в зависимости от времени суток."""
    hour = current_time.hour
    if hour < 6:
        greeting = "Доброй ночи"
    elif hour < 12:
        greeting = "Доброе утро"
    elif hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    logging.info(f"Greeting generated: {greeting}")
    return greeting
