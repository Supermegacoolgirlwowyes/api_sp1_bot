# This Python file uses the following encoding: utf-8
import logging
import os
import time
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger('Homework_bot')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('homework_bot.log')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

bot = telegram.Bot(token=TELEGRAM_TOKEN)


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
        return homework_statuses.json()
    except requests.exceptions.Timeout as err:
        logger.error(f'Timeout Error: {err}')
    except requests.exceptions.HTTPError as err:
        logger.error(f'HTTP Error: {err}')
    except requests.exceptions.ConnectionError as err:
        logger.error(f'Connection Error: {err}')
    except requests.exceptions.RequestException as err:
        logger.error(f'Some error has happened: {err}')


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')
                        [0]
                    )
                )
                return
            else:
                logger.info('Homework not been reviewed yet.')
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
