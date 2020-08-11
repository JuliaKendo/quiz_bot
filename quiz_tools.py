import re
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


def get_answer(quiz_lib, question):
    answer = quiz_lib.get(question)
    return re.sub(r'[\.|\(].*$', '', answer).strip()


def remove_waste_letters(text):
    return re.sub(r'\n+|\r', ' ', text).strip()


def get_quiz_lib(quiz_text):
    quiz_lib = {}
    for quiz_question in re.split(r'Вопрос[\s][0-9]+\s?:\n', quiz_text):
        regex_object = re.compile(r'''
            (.*)(\nОтвет:\n?)           #все символы с начала строки до слова "Ответ:", ограниченным одним или несколькими переносами строк
            (.*)(\nКомментарий:.*\n+)?  #все символы после предыдущей группы, до и после слова "Комментарий:", если оно присутствует в тексте
            (\nИсточник:.*\n+)          #все символы после слова "Источник:", включая один или несколько переносов строки
            (\nАвтор:.*\n+)             #все символы после слова "Автор:", включая один или несколько переносов строки
        ''', re.DOTALL | re.VERBOSE)
        question_and_answer = regex_object.findall(quiz_question)
        if question_and_answer:
            quiz_lib.update({remove_waste_letters(question[0]): remove_waste_letters(question[2]) for question in question_and_answer})

    return quiz_lib


def read_questions(quiz_folder):
    readed_questions = {}
    for file in tqdm(glob(f'{quiz_folder}/*.txt'), desc="Прочитано", unit=" файлов с вопросами"):
        with open(file, 'r', encoding='KOI8-R') as file_handler:
            quiz_text = file_handler.read()
            readed_questions.update(get_quiz_lib(quiz_text))
            break
    return readed_questions
