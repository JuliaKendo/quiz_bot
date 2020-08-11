import os
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

    return parser


def launch_tg_bot(quiz_questions):
    tg_bot = TgQuizBot(
        os.getenv('TG_ACCESS_TOKEN'),
        quiz_questions=quiz_questions,
        redis_host=os.getenv('REDIS_HOST'),
        redis_port=os.getenv('REDIS_PORT'),
        redis_pass=os.getenv('REDIS_PASSWORD')
    )
    tg_bot.start()


def launch_vk_bot(quiz_questions):
    vk_bot = VkQuizBot(
        os.getenv('VK_ACCESS_TOKEN'),
        quiz_questions=quiz_questions,
        redis_host=os.getenv('REDIS_HOST'),
        redis_port=os.getenv('REDIS_PORT'),
        redis_pass=os.getenv('REDIS_PASSWORD')
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
        quiz_questions = quiz_tools.read_questions(args.quiz_folder)

        if args.quiz == 'tg':
            logger.info('telegram quiz bot launched')
            try:
                launch_tg_bot(quiz_questions)
            except (
                telegram.TelegramError,
                requests.exceptions.HTTPError
            ) as error:
                logger.exception(f'Ошибка telegram бота: {error}')

        if args.quiz == 'vk':
            logger.info('vk quiz bot launched')
            try:
                launch_vk_bot(quiz_questions)
            except (
                requests.exceptions.HTTPError,
                VkApiError, ApiHttpError, AuthError
            ) as error:
                logger.exception(f'Ошибка vk бота: {error}')

    except (
        KeyError, TypeError, ValueError, OSError
    ) as error:
        logger.exception(f'Ошибка бота: {error}')


if __name__ == "__main__":
    main()
