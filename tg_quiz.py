import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from quiz_tools import get_random_question, save_asked_question, get_answer
from quiz_tools import save_scoring, get_scoring_string, delete_scoring
from telegram.ext import Filters, MessageHandler, CommandHandler, Updater, ConversationHandler

logger = logging.getLogger('quize_bot')


class TgQuizBot(object):
    def __init__(self, token, redis_conn):
        self.updater = Updater(token=token)
        handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start_quiz)],
            states={
                'new_question': [
                    MessageHandler(Filters.regex('Новый вопрос'), self.handle_new_question_request),
                    MessageHandler(Filters.regex('Сдаться'), self.handle_correct_answer),
                    MessageHandler(Filters.regex('Мой счет'), self.handle_my_scoring),
                ],
                'check_reply': [
                    MessageHandler(Filters.regex('Новый вопрос'), self.handle_new_question_request),
                    MessageHandler(Filters.regex('Сдаться'), self.handle_correct_answer),
                    MessageHandler(Filters.regex('Мой счет'), self.handle_my_scoring),
                    MessageHandler(
                        Filters.text & (~Filters.regex('Новый вопрос') | ~Filters.regex('Сдаться') | ~Filters.regex('Мой счет')),
                        self.handle_solution_attempt
                    ),
                    MessageHandler(~Filters.text, self.handle_uncorrect_input)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.end_quiz)]
        )
        self.updater.dispatcher.add_handler(handler)
        self.updater.dispatcher.add_error_handler(self.error)
        self.redis_conn = redis_conn

    def start(self):
        self.updater.start_polling()

    def error(self, bot, update, error):
        logger.exception(f'Ошибка tg бота: {error}')
        return ConversationHandler.END

    def start_quiz(self, bot, update):
        user_ident = f'user_tg_{update.message.chat_id}'
        text = 'Приветствую!\n Нажмите "Новый вопрос" для начала викторины или "/cancel" для отмены.'
        custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
        reply_markup = ReplyKeyboardMarkup(custom_keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)
        delete_scoring(self.redis_conn, user_ident)
        return 'new_question'

    def handle_new_question_request(self, bot, update):
        user_ident = f'user_tg_{update.message.chat_id}'
        question_key, question = get_random_question(self.redis_conn)
        save_asked_question(self.redis_conn, user_ident, question_key)
        update.message.reply_text(question)
        return 'check_reply'

    def handle_solution_attempt(self, bot, update):
        user_ident = f'user_tg_{update.message.chat_id}'
        correct_answer = get_answer(self.redis_conn, user_ident)
        if update.message.text.upper() in correct_answer.upper():
            save_scoring(self.redis_conn, user_ident, True)
            update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
            return 'new_question'
        else:
            save_scoring(self.redis_conn, user_ident)
            update.message.reply_text('Неправильно... Попробуешь ещё раз?')
            return 'check_reply'

    def handle_correct_answer(self, bot, update):
        user_ident = f'user_tg_{update.message.chat_id}'
        save_scoring(self.redis_conn, user_ident)
        correct_answer = get_answer(self.redis_conn, user_ident)
        update.message.reply_text(f'Вот тебе правильный ответ: {correct_answer}\nДля продолжения нажмите "Новый вопрос"')
        return 'new_question'

    def handle_uncorrect_input(self, bot, update):
        update.message.reply_text('Непонимаю.\nНажмите "Новый вопрос" для продолжения или "/cancel" для отмены.')
        return 'new_question'

    def handle_my_scoring(self, bot, update):
        user_ident = f'user_tg_{update.message.chat_id}'
        scoring_string = get_scoring_string(self.redis_conn, user_ident)
        update.message.reply_text(f'{scoring_string}\nНажмите "Новый вопрос" для продолжения или "/cancel" для отмены.')
        return 'new_question'

    def end_quiz(self, bot, update):
        text = 'Викторина завершена!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
