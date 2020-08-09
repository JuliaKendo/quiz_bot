import os
import questions_handlers
from dialog_bot import QuizDialogBot


def main():
    readed_questions = questions_handlers.read_questions()
    bot = QuizDialogBot(
        os.getenv('TG_ACCESS_TOKEN'),
        os.getenv('DIALOGFLOW_PROJECT_ID'),
        quiz_questions=readed_questions,
        redis_host=os.getenv('REDIS_HOST'),
        redis_port=os.getenv('REDIS_PORT'),
        redis_pass=os.getenv('REDIS_PASSWORD')
    )
    bot.start()


if __name__ == "__main__":
    main()
