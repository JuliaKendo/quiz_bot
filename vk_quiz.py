from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from quiz_tools import check_answer
from quiz_tools import get_vk_keyboard
from quiz_tools import save_scoring, get_scoring_string, delete_scoring
from quiz_tools import get_random_question, save_asked_question, get_answer


class VkQuizBot(object):
    def __init__(self, token, group_id, redis_conn):
        self.vk_session = VkApi(token=token)
        self.group_id = group_id
        self.vk_api = self.vk_session.get_api()
        self.redis_conn = redis_conn

    def start(self):
        longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        for event in longpoll.listen():
            self.handle_message(event)

    def handle_message(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW and event.object.text:
            if event.object.text == 'Привет':
                self.start_quiz(event)
                return

            if event.object.text == 'Завершить':
                self.end_quiz(event)
                return

            if 'Новый вопрос' in event.object.text:
                self.handle_new_question_request(event)

            elif 'Сдаться' in event.object.text:
                self.handle_correct_answer(event)

            elif 'Мой счет' in event.object.text:
                self.handle_my_scoring(event)

            else:
                self.handle_solution_attempt(event)

    def start_quiz(self, event):
        user_ident = f'user_vk_{event.object.from_id}'
        message = 'Приветствую!\n Нажмите "Новый вопрос" для начала викторины или "Завершить" для отмены.'
        self.send_message(event.object.peer_id, message, get_vk_keyboard())
        delete_scoring(self.redis_conn, user_ident)

    def handle_new_question_request(self, event):
        user_ident = f'user_vk_{event.object.from_id}'
        question_key, question = get_random_question(self.redis_conn)
        save_asked_question(self.redis_conn, user_ident, question_key)
        self.send_message(event.object.peer_id, question)

    def handle_solution_attempt(self, event):
        user_ident = f'user_vk_{event.object.from_id}'
        correct_answer = get_answer(self.redis_conn, user_ident)
        if check_answer(event.object.text, correct_answer):
            save_scoring(self.redis_conn, user_ident, True)
            message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
        else:
            save_scoring(self.redis_conn, user_ident)
            message = 'Неправильно... Попробуешь ещё раз?'

        self.send_message(event.object.peer_id, message)

    def handle_correct_answer(self, event):
        user_ident = f'user_vk_{event.object.from_id}'
        correct_answer = get_answer(self.redis_conn, user_ident)
        save_scoring(self.redis_conn, user_ident)
        message = f'Вот тебе правильный ответ: {correct_answer}\nДля продолжения нажмите "Новый вопрос"'
        self.send_message(event.object.peer_id, message)

    def handle_my_scoring(self, event):
        user_ident = f'user_vk_{event.object.from_id}'
        scoring_string = get_scoring_string(self.redis_conn, user_ident)
        message = f'{scoring_string}\nНажмите "Новый вопрос" для продолжения или "Завершить" для отмены.'
        self.send_message(event.object.peer_id, message)

    def end_quiz(self, event):
        empty_keyboard = VkKeyboard.get_empty_keyboard()
        self.send_message(event.object.peer_id, 'Викторина завершена!', empty_keyboard)

    def send_message(self, send_id, message, keyboard=None):
        if message:
            self.vk_api.messages.send(
                peer_id=send_id,
                message=message,
                keyboard=keyboard,
                random_id=get_random_id()
            )
