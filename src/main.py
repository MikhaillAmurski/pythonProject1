from pathlib import Path
from src.config import file_path
from src.utils import reader_transaction_excel, get_user_settings
from src.views import main

ROOT_PATH = Path(__file__).resolve().parent.parent


if __name__ == "__main__":
    df_transactions = reader_transaction_excel(file_path)
    date = "29.07.2019 22:06:27"

    user_currencies, user_stocks = get_user_settings(str(ROOT_PATH) + "/user_setting.json")

    date_json = main(df_transactions, date, user_currencies, user_stocks)

    print(date_json)
    print(file_path)
