import sys
from src.views import generate_json_response


def main():
    """Главная функция для запуска приложения."""
    if len(sys.argv) != 3:
        print("Usage: python main.py <date> <path_to_excel>")
        sys.exit(1)

    date_input = sys.argv[1]  # Дата и время в формате 'YYYY-MM-DD HH:MM:SS'
    path_to_excel = sys.argv[2]  # Путь к Excel файлу с транзакциями

    try:
        json_response = generate_json_response(date_input, path_to_excel)
        print(json_response)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
