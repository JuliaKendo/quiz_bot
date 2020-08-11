import os
import telegram
import quiz_tools
import requests
from dotenv import load_dotenv
from tg_quiz_dialogs import TgQuizBot
from vk_quiz_dialogs import VkQuizBot
from vk_api import VkApiError, ApiHttpError, AuthError


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

    try:
        quiz_questions = quiz_tools.read_questions()

        try:
            launch_tg_bot(quiz_questions)
        except (
            telegram.TelegramError,
            requests.exceptions.HTTPError
        ) as error:
            print(f'{error}')

        try:
            launch_vk_bot(quiz_questions)
        except (
            requests.exceptions.HTTPError,
            VkApiError, ApiHttpError, AuthError
        ) as error:
            print(f'{error}')

    except (
        KeyError, TypeError, ValueError, OSError
    ) as error:
        print(f'{error}')


if __name__ == "__main__":
    main()
