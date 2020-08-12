import re
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
    return (answer if answer else '')


def remove_waste_letters(text):
    return re.sub(r'\n+|\r|\(', ' ', text).strip()


def get_quiz_lib(quiz_text):
    regex_object = re.compile(r'''
        (Вопрос[\s][0-9]+\s?:\n+?)  #начало блока со слова "Вопрос" и до ":" с последующими переносами, если они есть
        (.*?)(Ответ:)               #все символы до слова "Ответ:"
        (.*?[\.|\(])                #все символы до первой точки или открывающейся скобки
    ''', re.DOTALL | re.VERBOSE)
    quiz_questions = regex_object.findall(quiz_text)
    if quiz_questions:
        return {remove_waste_letters(quiz_question[1]): remove_waste_letters(quiz_question[3]) for quiz_question in quiz_questions}


def read_questions(quiz_folder):
    readed_questions = {}
    for file in glob(f'{quiz_folder}/*.txt'):
        with open(file, 'r', encoding='KOI8-R') as file_handler:
            quiz_text = file_handler.read()
            readed_questions.update(get_quiz_lib(quiz_text))
    return readed_questions
