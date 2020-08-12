# Бот для проведения викторины

Данный бот предназначен для организации викторины в telegram и в группе ВКонтакте. Бот берет вопросы и ответы для викторины из текстовых файлов и сохраняет их в базе данных [Redis](https://redislabs.com).

![Alt text](demo_tg.gif) | ![Alt text](demo_vk.gif)
------------------------ | ----------------------------

## Установка и запуск

Python3 должен быть уже установлен. Затем используйте pip (или pip3, если есть конфликт с Python2) для установки зависимостей:

```
pip install -r requirements.txt
```

Создайте базу данных на [Redislabs](https://redislabs.com)

Для установки отредактируйте файл .env, в котором заполните следующие переменные окружения:
- `TG_ACCESS_TOKEN` - Секретный ключ бота telegram для викторины.
- `TG_LOG_TOKEN` - Секретный ключ бота для информации об ошибках.
- `TG_CHAT_ID` - ID чата текущего пользователя telegram.
- `VK_ACCESS_TOKEN` - Секретный токен для подключения к api сайта [vk.com](http://www.vk.com).
- `REDIS_HOST` - Адрес базы данных [Redislabs](https://redislabs.com).
- `REDIS_PORT` - Порт для подключения к базе данных [Redislabs](https://redislabs.com).
- `REDIS_PASSWORD` - Пароль для подключения к базе данных [Redislabs](https://redislabs.com).


Запускают скрипт с одним обязательным параметром:
- `-q, --quiz {tg, vk}`  Запуск викторины в telegram (tg) или ВКонтакте (vk).

Также доступны следующие необязательные параметры:
- `-u, --update_db`    Обновляет базу данных вопросов викторины с файлов.
- `-f, --quiz_folder`  Путь к каталогу с текстовыми файлами вопросов для викторины.

```
python.exe main.py --quiz tg
```	

Информацию о ходе выполнения скрипт отправляют отдельному боту telegram. Токен его должен быть указан в соответствующей переменной окружения.
В составе скрипта присутствует файл `Procfile`, необходимый для деплоя на сервер [HEROKU](https://heroku.com). Файл уже настроен должным образом, поэтому перенос скрипта на сервер выполняется в соответствии с документацией сервера [HEROKU](https://devcenter.heroku.com/articles/git).


## Цель проекта

Код написан в образовательных целях, для изучения возможностей чат-ботов, на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org).
