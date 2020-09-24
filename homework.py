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
PRAKTIKUM_API_URL = 'https://praktikum.yandex.ru/api/user_api/{}/'

logging.basicConfig(
    filename='homework.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

bot = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    logger = logging.getLogger('parse_homework_status')
    try:
        homework_name = homework.get('homework_name')
        status = homework['status']
        if status == 'approved':
            verdict = u'Ревьюеру всё понравилось, ' \
                      u'можно приступать к следующему уроку.'
        elif status == 'rejected':
            verdict = u'К сожалению в работе нашлись ошибки.'
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except KeyError as err:
        logger.error(f'Key Error: {err} - no such key in response')
        return "Houston! We've got a problem. " \
               "Status of your homework is not available. Check logs."


def get_homework_statuses(current_timestamp):
    logger = logging.getLogger('get_homework_statuses')
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_API_URL.format('homework_statuses'),
            headers=headers,
            params=params,
            timeout=10
        )
        return homework_statuses.json()
    except requests.exceptions.Timeout as err:
        logger.error(f'Timeout Error: {err}, '
                     f'headers = {headers}, params: {params}')
    except requests.exceptions.HTTPError as err:
        logger.error(f'HTTP Error: {err}, '
                     f'headers = {headers}, params: {params}')
    except requests.exceptions.ConnectionError as err:
        logger.error(f'Connection Error: {err}, '
                     f'headers = {headers}, params: {params}')
    except requests.exceptions.RequestException as err:
        logger.error(f'Some error has happened: {err}, '
                     f'headers = {headers}, params: {params}')
    return


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    tries = 0

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
                logging.info('Homework has not been '
                             'uploaded or reviewed yet.')
            current_timestamp = int(time.time())
            time.sleep(1200)

        except Exception as e:
            tries += 1
            time.sleep(5)
            if tries == 100:
                logging.error(f'Бот упал с ошибкой {tries} раз: {e}')
                send_message('Что-то не так, бот всё время падает. '
                             'Бегом к компьютеру, проверять что за дела. '
                             'А мы запустим его ещё раз через 30 минут.')
                time.sleep(1800)
                continue
            elif tries == 200:
                send_message('Ну так не дело не пойдёт. '
                             'Опять падает. Бот пойдёт отдыхать, '
                             'а ты разбираться с ошибками.')
                return


if __name__ == '__main__':
    main()
