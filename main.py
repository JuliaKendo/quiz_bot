import os
from dotenv import load_dotenv
import quiz_tools
from tg_quiz_dialogs import TgQuizBot
from vk_quiz_dialogs import VkQuizBot


def main():

    load_dotenv()

    bot = TgQuizBot(
        os.getenv('TG_ACCESS_TOKEN'),
        os.getenv('DIALOGFLOW_PROJECT_ID'),
        quiz_questions=quiz_tools.read_questions(),
        redis_host=os.getenv('REDIS_HOST'),
        redis_port=os.getenv('REDIS_PORT'),
        redis_pass=os.getenv('REDIS_PASSWORD')
    )
    bot.start()

    vk_bot = VkQuizBot(
        os.getenv('VK_ACCESS_TOKEN'),
        quiz_questions=quiz_tools.read_questions(),
        redis_host=os.getenv('REDIS_HOST'),
        redis_port=os.getenv('REDIS_PORT'),
        redis_pass=os.getenv('REDIS_PASSWORD')
    )
    vk_bot.start()


if __name__ == "__main__":
    main()
