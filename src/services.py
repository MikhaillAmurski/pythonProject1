import pandas as pd
import logging
from typing import Dict, List

# Настройка логирования для services
logging.basicConfig(
    filename='logs/services.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def cashback_analysis(data: pd.DataFrame, year: int, month: int) -> Dict[str, float]:
    """Анализ кешбэка по категориям для указанного года и месяца.

    Args:
        data (pd.DataFrame): Датафрейм с транзакциями.
        year (int): Год для анализа.
        month (int): Месяц для анализа.

    Returns:
        Dict[str, float]: Словарь, где ключи — категории, а значения — соответствующий кешбэк.
    """
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{pd.Timestamp(start_date).days_in_month}"

    filtered_transactions = data[
        (pd.to_datetime(data['Дата операции']) >= start_date) &
        (pd.to_datetime(data['Дата операции']) <= end_date)
        ]

    cashback_summary = filtered_transactions.groupby('Категория').agg(
        total_cashback=('Сумма операции', lambda x: (x.sum() * 0.01))
    ).reset_index()

    logging.info(f"Cashback analysis completed for {year}-{month:02d}.")
    return cashback_summary.set_index('Категория')['total_cashback'].to_dict()


def investment_bank(month: str, transactions: List[Dict[str, float]], limit: int) -> float:
    """Рассчитывает сумму, отложенную в «Инвесткопилку».

    Args:
        month (str): Месяц, для которого рассчитывается отложенная сумма (формат 'YYYY-MM').
        transactions (List[Dict[str, float]]): Список транзакций с информацией о сумме.
        limit (int): Предел, до которого необходимо округлять суммы.

    Returns:
        float: Сумма, отложенная в «Инвесткопилку».
    """
    total_invest = 0
    for transaction in transactions:
        amount = transaction['Сумма операции']
        rounded_amount = ((amount // limit) + 1) * limit
        total_invest += (rounded_amount - amount)

    logging.info(f"Total investment for {month}: {total_invest} RUB")
    return total_invest
