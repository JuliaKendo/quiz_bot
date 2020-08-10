import redis
import random
from quiz_tools import get_answer
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Filters, MessageHandler, CommandHandler, Updater, ConversationHandler


class TgQuizBot():
    def __init__(self, token, project_id, **kwargs):
        self.updater = Updater(token=token)
        self.project_id = project_id
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_quiz)],
            states={
                'new_question': [
                    MessageHandler(Filters.regex('Новый вопрос'), self.handle_new_question_request),
                    MessageHandler(Filters.regex('Сдаться'), self.handle_correct_answer)
                ],
                'check_reply': [
                    MessageHandler(Filters.text & (~Filters.regex('Сдаться')), self.handle_solution_attempt),
                    MessageHandler(Filters.regex('Сдаться'), self.handle_correct_answer)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.end_quiz)]
        )
        self.updater.dispatcher.add_handler(handler)
        self.updater.dispatcher.add_error_handler(self.error)
        self.quiz_questions = kwargs['quiz_questions']
        self.redis_conn = redis.Redis(
            host=kwargs['redis_host'], port=kwargs['redis_port'],
            db=0, password=kwargs['redis_pass']
        )

    def start(self):
        self.updater.start_polling()

    def error(self, bot, update, error):
        return ConversationHandler.END

    def start_quiz(self, bot, update):
        text = 'Приветствую!\n Нажмите "Новый вопрос" для начала викторины или "/cancel" для отмены.'
        custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)
        return 'new_question'

    def handle_new_question_request(self, bot, update):
        session_id = update.message.chat_id
        question = random.choice(list(self.quiz_questions.keys()))
        self.redis_conn.set(session_id, question)
        update.message.reply_text(question)
        return 'check_reply'

    def handle_solution_attempt(self, bot, update):
        session_id = update.message.chat_id
        question = self.redis_conn.get(session_id)
        correct_answer = get_answer(self.quiz_questions, question.decode())
        if update.message.text.upper() in correct_answer.upper():
            update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        else:
            update.message.reply_text('Неправильно... Попробуешь ещё раз?')
        return 'new_question'

    def handle_correct_answer(self, bot, update):
        session_id = update.message.chat_id
        question = self.redis_conn.get(session_id)
        correct_answer = get_answer(self.quiz_questions, question.decode())
        update.message.reply_text(f'Вот тебе правильный ответ: {correct_answer}.\nДля продолжения нажмите "Новый вопрос"')
        return 'new_question'

    def end_quiz(self, bot, update):
        text = 'Викторина завершена!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
