import os
import re
import random
from glob import glob
from telegram import ReplyKeyboardMarkup
from telegram.ext import Filters, MessageHandler, Updater


class TgDialogBot(object):

    def __init__(self, token, project_id, responce_handler, quiz_questions):
        self.updater = Updater(token=token)
        self.project_id = project_id
        handler = MessageHandler(Filters.text | Filters.command, self.send_message)
        self.updater.dispatcher.add_handler(handler)
        self.responce_handler = responce_handler
        self.quiz_questions = quiz_questions

    def start(self):
        self.updater.start_polling()

    def send_message(self, bot, update):
        answer = self.responce_handler(self.project_id, update.message.chat_id, update.message.text, self.quiz_questions)
        if answer:
            custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
            reply_markup = ReplyKeyboardMarkup(custom_keyboard)
            update.message.reply_text(answer, reply_markup=reply_markup)


def get_questions_and_answers(text):
    questions, answers = [], []
    for line in text.split('\n\n'):
        if re.match(r'^Вопрос[\s][0-9][:]', line):
            questions.append(line)
        if re.match(r'^Ответ[:]', line):
            answers.append(line)
    return dict(zip(questions, answers))


def get_answer(project_id, session_id, text, quiz_questions):
    if text == 'Новый вопрос':
        return random.choice(list(quiz_questions.keys()))
    else:
        return text


for file in glob('quiz-questions/*.txt'):
    with open(file, 'r', encoding='KOI8-R') as file_handler:
        text = file_handler.read()
        quiz_questions = get_questions_and_answers(text)
    break

bot = TgDialogBot(
    os.getenv('TG_ACCESS_TOKEN'),
    os.getenv('DIALOGFLOW_PROJECT_ID'),
    get_answer,
    quiz_questions
)
bot.start()
