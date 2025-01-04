import json
import logging
from pathlib import Path

import pytest
import re
from src.utils import get_dict_transaction


logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
log_dir = Path("./logs")
log_dir.mkdir(exist_ok=True, parents=True)
file_handler = logging.FileHandler(log_dir.joinpath("services.log"), encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_transactions_fizlicam(dict_transaction: list[dict], pattern):
    """Функция возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам"""
    logger.info("Вызвана функция get_transactions_fizlicam")
    list_transactions_fl = []
    for trans in dict_transaction:
        if "Описание" in trans and re.match(pattern, trans["Описание"]):
            list_transactions_fl.append(trans)
    logger.info(f"Найдено {len(list_transactions_fl)} транзакций, соответствующих паттерну")
    if list_transactions_fl:
        list_transactions_fl_json = json.dumps(list_transactions_fl, ensure_ascii=False)
        logger.info(f"Возвращен JSON со {len(list_transactions_fl)} транзакциями")
        return list_transactions_fl_json
    else:
        logger.info("Возвращен пустой список")
        return "[]"


if __name__ == "__main__":
    list_transactions_fl_json = get_transactions_fizlicam(
        get_dict_transaction("..\\data\\operations.xlsx"), pattern=r"\b[А-Я][а-я]+\s[А-Я]\."
    )
    print(list_transactions_fl_json)
