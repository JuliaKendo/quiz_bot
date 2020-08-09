import os
import quiz_tools
from quiz_dialogs import QuizDialogsBot


def main():

    bot = QuizDialogsBot(
        os.getenv('TG_ACCESS_TOKEN'),
        os.getenv('DIALOGFLOW_PROJECT_ID'),
        quiz_questions=quiz_tools.read_questions(),
        redis_host=os.getenv('REDIS_HOST'),
        redis_port=os.getenv('REDIS_PORT'),
        redis_pass=os.getenv('REDIS_PASSWORD')
    )
    bot.start()


if __name__ == "__main__":
    main()
