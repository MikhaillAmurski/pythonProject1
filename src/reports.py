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
    """Возвращает траты по заданной категории за последние три месяца.

    Args:
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        category (str): Название категории для анализа.
        date (str, optional): Дата, относительно которой идет анализ (формат 'YYYY-MM-DD'). Если не указана, берется текущая дата.

    Returns:
        pd.DataFrame: Датафрейм с суммами расходов по указанной категории.
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)

    filtered_transactions = transactions[
        (pd.to_datetime(transactions['Дата операции']) >= start_date) &
        (pd.to_datetime(transactions['Дата операции']) <= end_date) &
        (transactions['Категория'] == category)
        ]

    logging.info(f"Spending calculated for category: {category} from {start_date.date()} to {end_date.date()}.")
    return filtered_transactions.groupby('Дата операции').agg(total_spent=('Сумма операции', 'sum')).reset_index()


def spending_by_weekday(transactions: pd.DataFrame, date: str = None) -> pd.DataFrame:
    """Возвращает средние траты в каждый день недели за последние три месяца.

    Args:
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        date (str, optional): Дата, относительно которой идет анализ (формат 'YYYY-MM-DD'). Если не указана, берется текущая дата.

    Returns:
        pd.DataFrame: Датафрейм со средними расходами по дням недели.
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)

    filtered_transactions = transactions[
        (pd.to_datetime(transactions['Дата операции']) >= start_date) &
        (pd.to_datetime(transactions['Дата операции']) <= end_date)
        ]

    filtered_transactions['weekday'] = filtered_transactions['Дата операции'].dt.day_name()
    weekly_spending = filtered_transactions.groupby('weekday').agg(total_spent=('Сумма операции', 'mean')).reset_index()

    logging.info(f"Weekly spending calculated from {start_date.date()} to {end_date.date()}.")
    return weekly_spending


def spending_by_workday(transactions: pd.DataFrame, date: str = None) -> pd.DataFrame:
    """Возвращает средние траты в рабочий и выходной день за последние три месяца.

    Args:
        transactions (pd.DataFrame): Датафрейм с транзакциями.
        date (str, optional): Дата, относительно которой идет анализ (формат 'YYYY-MM-DD'). Если не указана, берется текущая дата.

    Returns:
        pd.DataFrame: Датафрейм со средними расходами в рабочие и выходные дни.
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)

    filtered_transactions = transactions[
        (pd.to_datetime(transactions['Дата операции']) >= start_date) &
        (pd.to_datetime(transactions['Дата операции']) <= end_date)
        ]

    filtered_transactions['is_weekend'] = filtered_transactions['Дата операции'].dt.dayofweek >= 5
    workday_spending = filtered_transactions.groupby('is_weekend').agg(
        total_spent=('Сумма операции', 'mean')).reset_index()

    workday_spending['Day Type'] = workday_spending['is_weekend'].map({True: 'Выходной', False: 'Рабочий'})
    result = workday_spending[['Day Type', 'total_spent']]

    logging.info(f"Spending by workdays and weekends calculated from {start_date.date()} to {end_date.date()}.")
    return result
