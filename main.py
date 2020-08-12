import os
import redis
import logging
import argparse
import telegram
import requests
import quiz_tools
import logger_tools
from dotenv import load_dotenv
from tg_quiz import TgQuizBot
from vk_quiz import VkQuizBot
from vk_api import VkApiError, ApiHttpError, AuthError

logger = logging.getLogger('quize_bot')


def create_parser():
    parser = argparse.ArgumentParser(description='Параметры запуска скрипта')
    parser.add_argument('-q', '--quiz', choices=['tg', 'vk'], required=True, help='Викторина в telegram (tg) или ВКонтакте (vk)')
    parser.add_argument('-f', '--quiz_folder', default='quiz-questions', help='Путь к каталогу с текстовыми файлами вопросов для викторины')
    parser.add_argument('-u', '--update_db', action='store_true', help='Обновляет базу данных вопросов викторины с файлов')

    return parser


def launch_tg_bot(redis_conn):
    tg_bot = TgQuizBot(
        os.getenv('TG_ACCESS_TOKEN'),
        redis_conn=redis_conn
    )
    tg_bot.start()


def launch_vk_bot(redis_conn):
    vk_bot = VkQuizBot(
        os.getenv('VK_ACCESS_TOKEN'),
        redis_conn=redis_conn
    )
    vk_bot.start()


def main():

    load_dotenv()
    parser = create_parser()
    args = parser.parse_args()
    logger_tools.initialize_logger(
        logger,
        os.getenv('TG_LOG_TOKEN'),
        os.getenv('TG_CHAT_ID')
    )

    try:
        redis_conn = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            db=0, password=os.getenv('REDIS_PASSWORD')
        )

        if args.update_db:
            quiz_tools.read_questions(args.quiz_folder, redis_conn)

        if args.quiz == 'tg':
            logger.info('telegram quiz bot launched')
            try:
                launch_tg_bot(redis_conn)
            except (
                telegram.TelegramError,
                requests.exceptions.HTTPError
            ) as error:
                logger.exception(f'Ошибка telegram бота: {error}')

        if args.quiz == 'vk':
            logger.info('vk quiz bot launched')
            try:
                launch_vk_bot(redis_conn)
            except (
                requests.exceptions.HTTPError,
                VkApiError, ApiHttpError, AuthError
            ) as error:
                logger.exception(f'Ошибка vk бота: {error}')

    except (
        KeyError, TypeError, ValueError, OSError
    ) as error:
        logger.exception(f'Ошибка бота: {error}')

    except (
        redis.ConnectionError, redis.AuthenticationError, redis.RedisError
    ) as error:
        logger.exception(f'Ошибка работы с базой данных: {error}')


if __name__ == "__main__":
    main()
