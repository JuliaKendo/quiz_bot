import re
from glob import glob


def get_questions_and_answers(text):
    questions_and_answers = {}
    for quiz_question in re.split(r'Вопрос[\s][0-9]+\s?:\n', text):
        regex_object = re.compile(r'''(.*)(\nОтвет:\n?)(.*)(\nКомментарий:.*\n+)?(\nИсточник:.*\n+)(\nАвтор:.*\n+)''', re.DOTALL)
        question_and_answer = regex_object.findall(quiz_question)
        if question_and_answer:
            questions_and_answers.update({question[0]: question[2] for question in question_and_answer})

    return questions_and_answers


def read_questions():
    readed_questions = {}
    for file in glob('quiz-questions/*.txt'):
        with open(file, 'r', encoding='KOI8-R') as file_handler:
            text = file_handler.read()
            readed_questions.update(get_questions_and_answers(text))
        break
    return readed_questions
