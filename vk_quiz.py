import redis
import random
from quiz_tools import get_answer, get_vk_keyboard
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard


class VkQuizBot(object):
    def __init__(self, token, **kwargs):
        self.vk_session = VkApi(token=token)
        self.vk_api = self.vk_session.get_api()
        self.quiz_questions = kwargs['quiz_questions']
        self.redis_conn = redis.Redis(
            host=kwargs['redis_host'], port=kwargs['redis_port'],
            db=0, password=kwargs['redis_pass']
        )

    def start(self):
        longpoll = VkLongPoll(self.vk_session)
        for event in longpoll.listen():
            self.handle_message(event)

    def handle_message(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Привет':
                message = 'Приветствую!\n Нажмите "Новый вопрос" для начала викторины или "Завершить" для отмены.'
                self.send_message(event.user_id, message, get_vk_keyboard())
                return

            if event.text == 'Завершить':
                empty_keyboard = VkKeyboard.get_empty_keyboard()
                self.send_message(event.user_id, 'Викторина завершена!', empty_keyboard)
                return

            if event.text == 'Новый вопрос':
                question = random.choice(list(self.quiz_questions.keys()))
                self.redis_conn.set(f'vk{event.user_id}', question)
                self.send_message(event.user_id, question)

            elif event.text == 'Сдаться':
                question = self.redis_conn.get(f'vk{event.user_id}')
                correct_answer = get_answer(self.quiz_questions, question.decode())
                message = f'Вот тебе правильный ответ: {correct_answer}\nДля продолжения нажмите "Новый вопрос"'
                self.send_message(event.user_id, message)

            else:
                question = self.redis_conn.get(f'vk{event.user_id}')
                correct_answer = get_answer(self.quiz_questions, question.decode())
                if event.text.upper() in correct_answer.upper():
                    message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
                else:
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
