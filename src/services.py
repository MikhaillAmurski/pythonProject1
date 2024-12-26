import pandas as pd
import logging
from typing import Dict


# Настройка логирования для services
logging.basicConfig(
    filename='logs/services.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


def cashback_analysis(data: pd.DataFrame, year: int, month: int) -> Dict[str, float]:
    """Анализ кешбэка по категориям для указанного года и месяца."""
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{pd.Timestamp(start_date).days_in_month}"

    filtered_transactions = data[
        (pd.to_datetime(data['Дата операции']) >= start_date) &
        (pd.to_datetime(data['Дата операции']) <= end_date)
    ]

    cashback_summary = filtered_transactions.groupby('Категория').agg(total_cashback=('Сумма операции', lambda x: (x.sum() * 0.01))).reset_index()
    logging.info(f"Cashback analysis completed for {year}-{month:02d}.")
    return cashback_summary.set_index('Категория')['total_cashback'].to_dict()
