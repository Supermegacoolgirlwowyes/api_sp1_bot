# This Python file uses the following encoding: utf-8
import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework.get('status') != 'approved':
        verdict = u'К сожалению в работе нашлись ошибки.'
    else:
        verdict = u'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            headers=headers,
            params=params,
            timeout=10
        )
    except requests.exceptions.Timeout as err:
        print(f'Timeout Error: {err}')
    except requests.exceptions.HTTPError as err:
        print(f'HTTP Error: {err}')
    except requests.exceptions.ConnectionError as err:
        print(f'Connection Error: {err}')
    except requests.exceptions.RequestException as err:
        print(f'Some error has happened: {err}')
    return homework_statuses.json()


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            else:
                send_message('Вы не загрузили работу на проверку.')
            current_timestamp = new_homework.get('current_date')  # обновить timestamp
            time.sleep(1200)  # опрашивать раз в двадцать минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
