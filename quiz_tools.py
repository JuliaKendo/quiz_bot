import re
import random
from tqdm import tqdm
from glob import glob
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def check_answer(answer, correct_answer):
    regex_object = re.compile(r'[\n+|\r|\(|\)|\.|\,|\:|\;|\"|\[|\]|\s]')
    answer_seq = [word for word in regex_object.split(answer.upper()) if len(word) > 2]
    correct_answer_seq = [word for word in regex_object.split(correct_answer.upper()) if len(word) > 2]
    return len(answer_seq) == len(set(answer_seq) & set(correct_answer_seq)) and len(answer_seq) > 0


def get_vk_keyboard():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)

    return keyboard.get_keyboard()


def save_scoring(redis_conn, user_ident, successful_attempt=False):
    attempts, success = redis_conn.hmget(f'scoring_of_{user_ident}', ('attempts', 'success'))
    attempts = int(attempts.decode()) + 1 if attempts else 1
    added_number = 1 if successful_attempt else 0
    success = int(success.decode()) + added_number if success else added_number
    redis_conn.hmset(f'scoring_of_{user_ident}', {'attempts': attempts, 'success': success})


def delete_scoring(redis_conn, user_ident):
    redis_conn.hdel(f'scoring_of_{user_ident}', 'attempts', 'success')


def get_scoring_string(redis_conn, user_ident):
    attempts, success = redis_conn.hmget(f'scoring_of_{user_ident}', ('attempts', 'success'))
    return 'Всего попыток: %s, из них успешных: %s' % (
        attempts.decode() if attempts else '0',
        success.decode() if success else '0'
    )


def get_answer(redis_conn, user_ident):
    question_key = redis_conn.hget(user_ident, 'last_asked_question')
    question = redis_conn.hget(question_key, 'answer')
    return question.decode() if question else ''


def get_random_question(redis_conn):
    max_question_number = len(redis_conn.keys(pattern=u'question_*'))
    question_key = f'question_{random.randint(0, max_question_number)}'
    question = redis_conn.hget(question_key, 'question')
    return question_key, question.decode() if question else None


def save_asked_question(redis_conn, user_ident, question_key):
    redis_conn.hset(user_ident, 'last_asked_question', question_key)


def remove_waste_letters(phrases):
    return (re.sub(r'\n+|\r|\(', ' ', phrase).strip() for phrase in phrases)


def load_quiz_lib(quiz_folder, redis_conn):
    for question_number, quiz_question in enumerate(get_questions(quiz_folder)):
        phrases = dict(zip(('question', 'answer'), remove_waste_letters(quiz_question[1::2])))
        redis_conn.hmset(f'question_{question_number}', phrases)


def get_questions(quiz_folder):
    regex_object = re.compile(r'''
        (Вопрос[\s][0-9]+\s?:\n+?)  #начало блока со слова "Вопрос" и до ":" с последующими переносами, если они есть
        (.*?)(Ответ:)               #все символы до слова "Ответ:"
        (.*?[\.|\(])                #все символы до первой точки или открывающейся скобки
    ''', re.DOTALL | re.VERBOSE)
    for file in tqdm(glob(f'{quiz_folder}/*.txt'), desc="Прочитано", unit=" файлов с вопросами"):
        with open(file, 'r', encoding='KOI8-R') as file_handler:
            yield from regex_object.findall(file_handler.read())
