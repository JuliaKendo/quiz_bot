import re
import json
import random
from tqdm import tqdm
from glob import glob
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_vk_keyboard():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.DEFAULT)

    return keyboard.get_keyboard()


def add_scoring(redis_conn, redis_key):
    scoring = redis_conn.get(redis_key)
    scoring = int(scoring.decode()) + 1 if scoring else 1
    redis_conn.set(redis_key, scoring)


def save_scoring(redis_conn, user_ident, success=False):
    add_scoring(redis_conn, f'attempts_{user_ident}')
    if success:
        add_scoring(redis_conn, f'success_{user_ident}')


def delete_scoring(redis_conn, user_ident):
    redis_conn.delete(f'attempts_{user_ident}')
    redis_conn.delete(f'success_{user_ident}')


def get_scoring_string(redis_conn, user_ident):
    total_scoring = redis_conn.get(f'attempts_{user_ident}')
    success_scoring = redis_conn.get(f'success_{user_ident}')
    return 'Всего попыток: %s, из них успешных: %s' % (
        total_scoring.decode() if total_scoring else '0',
        success_scoring.decode() if success_scoring else '0'
    )


def get_answer(redis_conn, user_ident):
    question_key = json.loads(redis_conn.get(user_ident))['last_asked_question']
    question = json.loads(redis_conn.get(question_key))
    if question:
        return question['answer']


def get_random_question(redis_conn):
    max_question_number = len(redis_conn.keys(pattern=u'question_*'))
    question_key = f'question_{random.randint(0, max_question_number)}'
    question = json.loads(redis_conn.get(question_key))
    if question:
        return question_key, question['question']


def save_asked_question(redis_conn, user_ident, question_key):
    redis_conn.set(
        user_ident,
        json.dumps({'last_asked_question': question_key})
    )


def remove_waste_letters(text):
    return re.sub(r'\n+|\r|\(', ' ', text).strip()


def load_quiz_lib(quiz_text, redis_conn):
    regex_object = re.compile(r'''
        (Вопрос[\s][0-9]+\s?:\n+?)  #начало блока со слова "Вопрос" и до ":" с последующими переносами, если они есть
        (.*?)(Ответ:)               #все символы до слова "Ответ:"
        (.*?[\.|\(])                #все символы до первой точки или открывающейся скобки
    ''', re.DOTALL | re.VERBOSE)
    quiz_questions = regex_object.findall(quiz_text)
    for question_number, quiz_question in enumerate(quiz_questions):
        redis_conn.set(
            f'question_{question_number}',
            json.dumps(
                {
                    'question': remove_waste_letters(quiz_question[1]),
                    'answer': remove_waste_letters(quiz_question[3])
                }
            )
        )


def read_questions(quiz_folder, redis_conn):
    for file in tqdm(glob(f'{quiz_folder}/*.txt'), desc="Прочитано", unit=" файлов с вопросами"):
        with open(file, 'r', encoding='KOI8-R') as file_handler:
            load_quiz_lib(file_handler.read(), redis_conn)
