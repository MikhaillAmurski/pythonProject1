import pandas as pd
import logging
from datetime import datetime

# Настройка логирования для reports
logging.basicConfig(
    filename='logs/reports.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def spending_by_category(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние три месяца."""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)

    filtered_transactions = transactions[
        (pd.to_datetime(transactions['Дата операции']) >= start_date) &
        (pd.to_datetime(transactions['Дата операции']) <= end_date) &
        (transactions['Категория'] == category)
    ]

    logging.info(f"Spending calculated for category: {category} from {start_date} to {end_date}.")
    return filtered_transactions.groupby('Дата операции').agg(total_spent=('Сумма операции', 'sum')).reset_index()
