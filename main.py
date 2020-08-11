import os
import logging
import telegram
import requests
import quiz_tools
from dotenv import load_dotenv
from tg_quiz_dialogs import TgQuizBot
from vk_quiz_dialogs import VkQuizBot
from vk_api import VkApiError, ApiHttpError, AuthError

logger = logging.getLogger('quize_bot')


def initialize_logger(log_path=None):
    if log_path:
        output_dir = log_path
    else:
        output_dir = os.path.dirname(os.path.realpath(__file__))
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.path.join(output_dir, 'log.txt'), "a")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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
    initialize_logger()

    try:
        quiz_questions = quiz_tools.read_questions()

        try:
            launch_tg_bot(quiz_questions)
        except (
            telegram.TelegramError,
            requests.exceptions.HTTPError
        ) as error:
            logger.exception(f'Ошибка telegram бота: {error}')

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
