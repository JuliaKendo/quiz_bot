from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType
from quiz_tools import get_vk_keyboard
from quiz_tools import save_scoring, get_scoring_string, delete_scoring
from quiz_tools import get_random_question, save_asked_question, get_answer


class VkQuizBot(object):
    def __init__(self, token, redis_conn):
        self.vk_session = VkApi(token=token)
        self.vk_api = self.vk_session.get_api()
        self.redis_conn = redis_conn

    def start(self):
        longpoll = VkLongPoll(self.vk_session)
        for event in longpoll.listen():
            self.handle_message(event)

    def handle_message(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Привет':
                user_ident = f'user_vk_{event.user_id}'
                message = 'Приветствую!\n Нажмите "Новый вопрос" для начала викторины или "Завершить" для отмены.'
                self.send_message(event.user_id, message, get_vk_keyboard())
                delete_scoring(self.redis_conn, user_ident)
                return

            if event.text == 'Завершить':
                empty_keyboard = VkKeyboard.get_empty_keyboard()
                self.send_message(event.user_id, 'Викторина завершена!', empty_keyboard)
                return

            if event.text == 'Новый вопрос':
                user_ident = f'user_vk_{event.user_id}'
                question_key, question = get_random_question(self.redis_conn)
                save_asked_question(self.redis_conn, user_ident, question_key)
                self.send_message(event.user_id, question)

            elif event.text == 'Сдаться':
                user_ident = f'user_vk_{event.user_id}'
                correct_answer = get_answer(self.redis_conn, user_ident)
                save_scoring(self.redis_conn, user_ident)
                message = f'Вот тебе правильный ответ: {correct_answer}\nДля продолжения нажмите "Новый вопрос"'
                self.send_message(event.user_id, message)

            elif event.text == 'Мой счет':
                user_ident = f'user_vk_{event.user_id}'
                scoring_string = get_scoring_string(self.redis_conn, user_ident)
                message = f'{scoring_string}\nНажмите "Новый вопрос" для продолжения или "Завершить" для отмены.'
                self.send_message(event.user_id, message)

            else:
                user_ident = f'user_vk_{event.user_id}'
                correct_answer = get_answer(self.redis_conn, user_ident)
                if event.text.upper() in correct_answer.upper():
                    save_scoring(self.redis_conn, user_ident, True)
                    message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
                else:
                    save_scoring(self.redis_conn, user_ident)
                    message = 'Неправильно... Попробуешь ещё раз?'
                self.send_message(event.user_id, message)

    def send_message(self, user_id, message, keyboard=None):
        if message:
            self.vk_api.messages.send(
                user_id=user_id,
                message=message,
                keyboard=keyboard,
                random_id=get_random_id()
            )
