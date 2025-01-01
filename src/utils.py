import datetime
import datetime as dt
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Literal

import pandas as pd
from src.config import file_path
import os
import requests
from dotenv import load_dotenv

load_dotenv("..\\.env")

ROOT_PATH = Path(__file__).resolve().parent.parent

logger = logging.getLogger("logs")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("..\\logs\\utils.log", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_data(data_string: str) -> datetime.datetime:
    """Преобразует строку в объект datetime.

    Args:
        data_string: Строка даты в формате "DD.MM.YYYY HH:MM:SS".

    Returns:
        Объект datetime.datetime, соответствующий переданной строке.

    Raises:
        ValueError: Если строка не соответствует указанному формату.
    """
    logger.info(f"Получена строка даты: {data_string}")
    try:
        data_obj = datetime.datetime.strptime(data_string, "%d.%m.%Y %H:%M:%S")
        logger.info(f"Преобразована в объект datetime: {data_obj}")
        return data_obj
    except ValueError as e:
        logger.error(f"Ошибка преобразования даты: %s.  Передана строка: %s", e, data_string)
        raise


logger = logging.getLogger(__name__)


def reader_transaction_excel(file_path: str) -> pd.DataFrame:
    """Читает данные транзакций из файла Excel.

    Args:
        file_path: Путь к файлу Excel.

    Returns:
        pandas.DataFrame с данными о транзакциях.

    Raises:
        FileNotFoundError: Если файл не найден.
        pd.errors.EmptyDataError: Если файл пустой.
        pd.errors.ParserError: Если возникла ошибка при парсинге файла.
        Exception: Для любых других исключений, возникающих при чтении файла.

    """
    logger.info(f"Чтение транзакций из файла: {file_path}")
    try:
        df_transactions = pd.read_excel(file_path)
        if df_transactions.empty:
            logger.warning(f"Файл {file_path} пустой.")
            raise pd.errors.EmptyDataError(f"Файл {file_path} пустой.")
        logger.info(f"Данные из файла {file_path} успешно считаны.")
        return df_transactions
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден.")
        raise
    except pd.errors.ParserError as e:
        logger.exception(f"Ошибка при парсинге файла {file_path}: {e}")
        raise
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при чтении файла {file_path}: {e}")
        raise


def get_dict_transaction(file_path: str) -> list[dict]:
    """Преобразует данные из файла Excel в список словарей.

    Args:
        file_path: Путь к файлу Excel.

    Returns:
        Список словарей, где каждый словарь представляет строку из файла Excel.
        Возвращает пустой список, если произошла ошибка.

    Raises:
        FileNotFoundError: Если файл не найден.
        pd.errors.EmptyDataError: если файл пустой
        pd.errors.ParserError: Если возникла ошибка при парсинге файла.
        Exception: Для любых других исключений.
    """
    logger.info(f"Начало преобразования данных из файла: {file_path}")
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            logger.warning(f"Файл {file_path} пустой.")
            return []
        transactions = df.to_dict(orient="records")
        logger.info(f"Данные из файла {file_path} преобразованы в список словарей.")
        return transactions
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден.")
        raise
    except pd.errors.ParserError as e:
        logger.exception(f"Ошибка парсинга файла {file_path}: {e}")
        return []
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка: {e}")
        return []


def get_user_settings(file_path: str) -> Tuple[List[str], List[str]]:
    """Загружает настройки пользователя (валюты и акции) из JSON-файла.

    Args:
        file_path: Путь к JSON-файлу с настройками пользователя.

    Returns:
        Кортеж, содержащий два списка: список валют и список акций.  Возвращает ([], []) в случае ошибки.

    Raises:
        FileNotFoundError: Если файл не найден.
        json.JSONDecodeError: Если файл не является корректным JSON.
        KeyError: Если в JSON-файле отсутствуют ключи "user_currencies" или "user_stocks".
        Exception: Для любых других исключений.
    """
    logger.info(f"Загрузка настроек пользователя из файла: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
        currencies = user_settings["user_currencies"]
        stocks = user_settings["user_stocks"]
        logger.info("Настройки пользователя успешно загружены.")
        return currencies, stocks
    except FileNotFoundError:
        logger.error(f"Файл настроек {file_path} не найден.")
        return [], []
    except json.JSONDecodeError:
        logger.error(f"Ошибка разбора JSON-файла {file_path}.")
        return [], []
    except KeyError as e:
        logger.error(f"Отсутствует ключ в файле настроек {file_path}: {e}")
        return [], []
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при загрузке настроек: {e}")
        return [], []


def get_currency_rates(currencies: List[str]) -> Optional[List[Dict]]:
    """Получает курсы валют с помощью API apilayer.

    Args:
        currencies: Список кодов валют (например, ["USD", "EUR"]).

    Returns:
        Список словарей с курсами валют.  Каждый словарь имеет ключи "currency" и "rate".
        Возвращает None, если произошла ошибка.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        logger.error("API_KEY не найден в переменных окружения.")
        return None

    symbols = ",".join(currencies)
    url = f"https://api.apilayer.com/currency_data/live?symbols={symbols}"
    headers = {"apikey": api_key}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем код ответа (200 OK)

        data = response.json()
        quotes = data.get("quotes", {})
        usd = quotes.get("USDRUB")
        eur_usd = quotes.get("USDEUR")

        if usd is None or eur_usd is None:
            logger.warning("Данные по USDRUB или USDEUR не найдены в ответе API.")
            return None
        eur = usd / eur_usd

        rates = [
            {"currency": "USD", "rate": round(usd, 2)},
            {"currency": "EUR", "rate": round(eur, 2)},
        ]
        logger.info("Курсы валют успешно получены.")
        return rates

    except requests.exceptions.RequestException as e:
        logger.exception(f"Ошибка запроса к API apilayer: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.exception(f"Ошибка обработки данных от API apilayer: {e}")
        return None


def get_stock_price(stocks: List[str]) -> List[Dict]:
    """
    Получает цены акций с помощью API Alpha Vantage.

    Args:
        stocks: Список тикеров акций (например, ["AAPL", "MSFT"]).

    Returns:
        Список словарей, каждый содержащий тикер и цену акции.
        Возвращает пустой список, если произошла ошибка.
    """
    api_key = os.environ.get("API_KEY_STOCK")
    if not api_key:
        print("Ошибка: API_KEY_STOCK не найден в переменных окружения.")
        return []

    stock_prices = []
    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            price = round(float(data["Global Quote"]["05. price"]), 2)
            stock_prices.append({"stock": stock, "price": price})

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса к API для {stock}: {e}")
        except (KeyError, ValueError) as e:
            print(f"Ошибка обработки данных для {stock}: {e}")

    return stock_prices


def get_top_transactions(transactions: pd.DataFrame, top_n: int = 5) -> List[Dict]:
    """Возвращает список из top_n транзакций с наименьшей суммой платежа.

    Args:
        transactions: pandas.DataFrame с данными о транзакциях.  Должен содержать столбцы "Дата операции" и "Сумма платежа".
        top_n: Количество транзакций для возврата (по умолчанию 5).

    Returns:
        Список словарей, где каждый словарь представляет транзакцию с полями "date", "amount", "category", "description".
        Возвращает пустой список, если DataFrame пуст или возникла ошибка.
    """
    logger.info(f"Получение топ {top_n} транзакций.")
    try:
        if transactions.empty:
            logger.warning("DataFrame транзакций пуст.")
            return []

        top_transactions = transactions.sort_values(by="Сумма платежа", ascending=True).head(top_n)
        top_transactions_list = []
        for transaction in top_transactions.to_dict(orient="records"):
            try:
                date_str = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S").strftime("%d.%m.%Y")
                top_transactions_list.append(
                    {
                        "date": date_str,
                        "amount": transaction["Сумма платежа"],
                        "category": transaction["Категория"],
                        "description": transaction["Описание"],
                    }
                )
            except (KeyError, ValueError) as e:
                logger.error(f"Ошибка обработки транзакции: {e}. Данные транзакции: {transaction}")

        logger.info(f"Получен список топ {top_n} транзакций.")
        return top_transactions_list
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при получении топ транзакций: {e}")
        return []


def get_card_expenses(transactions: pd.DataFrame) -> List[Dict]:
    """Вычисляет общие расходы и кэшбэк по каждой карте.

    Args:
        transactions: pandas.DataFrame с данными о транзакциях. Должен содержать столбцы "Номер карты" и "Сумма платежа".

    Returns:
        Список словарей, где каждый словарь содержит информацию о расходах по одной карте:
        - last_digits: Номер карты (предполагается, что это последние цифры номера).
        - total_spent: Общая сумма расходов по карте.
        - cashback: Сумма кэшбэка (рассчитывается как 1% от суммы расходов).
        Возвращает пустой список, если DataFrame пустой или произошла ошибка.

    """
    logger.info("Начало вычисления расходов по картам.")
    try:
        if transactions.empty:
            logger.warning("DataFrame транзакций пустой.")
            return []

        card_expenses = (
            transactions[transactions["Сумма платежа"] < 0]
            .groupby("Номер карты")["Сумма платежа"]
            .sum()
            .to_dict()
        )

        logger.debug(f"Получен словарь расходов по картам: {card_expenses}")

        expenses_list = []
        for card_number, total_spent in card_expenses.items():
            cashback = abs(round(total_spent / 100, 2))
            expenses_list.append(
                {
                    "last_digits": card_number,
                    "total_spent": abs(total_spent),
                    "cashback": cashback,
                }
            )
            logger.info(f"Расходы по карте {card_number}: {abs(total_spent)}, кэшбэк: {cashback}")

        logger.info("Вычисление расходов по картам завершено.")
        return expenses_list

    except KeyError as e:
        logger.error(f"Отсутствует необходимый столбец в DataFrame: {e}")
        return []
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка: {e}")
        return []


def filter_transactions_by_date(transactions: pd.DataFrame, date_string: str) -> Optional[pd.DataFrame]:
    """Фильтрует транзакции по заданному месяцу.

    Args:
        transactions: pandas.DataFrame с данными о транзакциях.  Должен содержать столбец "Дата операции" с датами в формате DD.MM.YYYY HH:MM:SS.
        date_string: Строка с датой в формате DD.MM.YYYY HH:MM:SS, которая определяет месяц для фильтрации.

    Returns:
        pandas.DataFrame, содержащий транзакции за указанный месяц. Возвращает None, если произошла ошибка.
    """
    logger.info(f"Фильтрация транзакций по дате: {date_string}")
    try:
        end_date = pd.to_datetime(date_string, format="%d.%m.%Y %H:%M:%S")
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0) + pd.Timedelta(days=1)

        filtered_transactions = transactions[
            (pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S") >= start_date)
            & (pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S") < end_date)
        ]

        logger.info(f"Отфильтровано транзакций: {len(filtered_transactions)}")
        return filtered_transactions

    except (KeyError, ValueError) as e:
        logger.error(f"Ошибка фильтрации транзакций: {e}")
        return None
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка при фильтрации транзакций: {e}")
        return None


def get_greeting() -> Literal["Доброе утро", "Добрый день", "Добрый вечер", "Доброй ночи"]:
    """Возвращает приветствие в зависимости от времени суток.

    Returns:
        Приветствие ("Доброе утро", "Добрый день", "Добрый вечер" или "Доброй ночи").
    """
    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
