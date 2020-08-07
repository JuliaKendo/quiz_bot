import os
import re
import redis
import random
from glob import glob
from telegram import ReplyKeyboardMarkup
from telegram.ext import Filters, MessageHandler, Updater


class TgDialogBot(object):

    def __init__(self, token, project_id, responce_handler):
        self.updater = Updater(token=token)
        self.project_id = project_id
        handler = MessageHandler(Filters.text | Filters.command, self.send_message)
        self.updater.dispatcher.add_handler(handler)
        self.responce_handler = responce_handler

    def start(self):
        self.updater.start_polling()

    def send_message(self, bot, update):
        answer = self.responce_handler(self.project_id, update.message.chat_id, update.message.text)
        if answer:
            update.message.reply_text(answer)


class QuizDialogBot(TgDialogBot):
    def __init__(self, token, project_id, responce_handler, **kwargs):
        super().__init__(token, project_id, responce_handler)
        self.quiz_questions = kwargs['quiz_questions']
        self.redis_conn = redis.Redis(
            host=kwargs['redis_host'],
            port=kwargs['redis_port'],
            db=0,
            password=kwargs['redis_pass']
        )

    def send_message(self, bot, update):
        answer = self.responce_handler(self.project_id, update.message.chat_id, update.message.text, self.quiz_questions, self.redis_conn)
        if answer:
            custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
            reply_markup = ReplyKeyboardMarkup(custom_keyboard)
            update.message.reply_text(answer, reply_markup=reply_markup)


def get_questions_and_answers(text):
    questions_and_answers = {}
    for quiz_question in re.split(r'Вопрос[\s][0-9]+\s?:\n', text):
        regex_object = re.compile(r'''(.*)(\nОтвет:\n?)(.*)(\nКомментарий:.*\n+)?(\nИсточник:.*\n+)(\nАвтор:.*\n+)''', re.DOTALL)
        question_and_answer = regex_object.findall(quiz_question)
        if question_and_answer:
            questions_and_answers.update({question[0]: question[2] for question in question_and_answer})

    return questions_and_answers


def get_answer(project_id, session_id, text, quiz_questions, redis_conn):
    if text == 'Новый вопрос':
        select_question = random.choice(list(quiz_questions.keys()))
        redis_conn.set(session_id, select_question)
        return select_question
    else:
        select_question = redis_conn.get(session_id)
        if select_question:
            return quiz_questions[select_question.decode()]


for file in glob('quiz-questions/*.txt'):
    with open(file, 'r', encoding='KOI8-R') as file_handler:
        text = file_handler.read()
        quiz_questions_and_answers = get_questions_and_answers(text)
    break


bot = QuizDialogBot(
    os.getenv('TG_ACCESS_TOKEN'),
    os.getenv('DIALOGFLOW_PROJECT_ID'),
    get_answer,
    quiz_questions=quiz_questions_and_answers,
    redis_host=os.getenv('REDIS_HOST'),
    redis_port=os.getenv('REDIS_PORT'),
    redis_pass=os.getenv('REDIS_PASSWORD')
)
bot.start()
