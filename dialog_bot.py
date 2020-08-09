import redis
import random
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Filters, MessageHandler, CommandHandler, Updater, ConversationHandler


class QuizDialogBot():
    def __init__(self, token, project_id, **kwargs):
        self.updater = Updater(token=token)
        self.project_id = project_id
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_quiz)],
            states={
                'user_massage': [MessageHandler(Filters.text, self.send_message)]
            },
            fallbacks=[MessageHandler(Filters.text, self.end_quiz)]
        )
        self.updater.dispatcher.add_handler(handler)
        self.quiz_questions = kwargs['quiz_questions']
        self.redis_conn = redis.Redis(
            host=kwargs['redis_host'],
            port=kwargs['redis_port'],
            db=0,
            password=kwargs['redis_pass']
        )

    def start(self):
        self.updater.start_polling()

    def start_quiz(self, bot, update):
        text = 'Приветствую!\n Нажмите "" для начала викторины или "/cancel" для отмены.'
        custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)
        return 'user_massage'

    def end_quiz(self, bot, update):
        text = 'Викторина завершена!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove)
        return ConversationHandler.END

    def send_message(self, bot, update):
        reply_text = self.get_tg_message(self.project_id, update.message.chat_id, update.message.text, self.quiz_questions, self.redis_conn)
        update.message.reply_text(reply_text)

    def check_answer(self, questions, question, answer):
        right_answer = questions.get(question)
        if not right_answer:
            return ''
        shot_answer = right_answer.split('.')[0]
        if answer.upper() in shot_answer.upper():
            return 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        else:
            return 'Неправильно... Попробуешь ещё раз?'

    def get_tg_message(self, project_id, session_id, user_response, quiz_questions, redis_conn):
        if user_response == 'Новый вопрос':
            question = random.choice(list(quiz_questions.keys()))
            redis_conn.set(session_id, question)
            return question
        else:
            question = redis_conn.get(session_id)
            return self.check_answer(quiz_questions, question.decode(), user_response)
