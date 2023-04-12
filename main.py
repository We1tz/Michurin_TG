import logging
import os
import sqlite3

import aiogram
from aiogram import types
import google.cloud.dialogflow
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from config import telegram_token
from keyboards import start_keyboard
from states import Test
from texts import txt

storage = MemoryStorage()

dialogflow = google.cloud.dialogflow

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "michurinbot-350715-99cf31d6b692.json"

session_client = dialogflow.SessionsClient()
project_id = 'michurinbot-350715'
session_id = 'sessions'
language_code = 'ru'
session = session_client.session_path(project_id, session_id)

logging.basicConfig(level=logging.INFO)
bot = aiogram.Bot(token=telegram_token)
dp = aiogram.Dispatcher(bot, storage=storage)


@dp.message_handler(commands="start")
async def cmd_start(message: aiogram.types.Message):
    await message.answer(txt.hello, reply_markup=start_keyboard.keyboard)


@dp.message_handler(commands="find")
async def locate(message: aiogram.types.Message):
    maps = """Здравствуйте, ближайшее к Вам интересное место - Мичуринский краеведческий музей. Высылаю координаты:
     """
    m = 1
    n = 2
    await bot.send_message(message.from_user.id, maps)
    connect = sqlite3.connect('maib_admin/db.sqlite3')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM admin_panel_geo")
    result_geo = cursor.fetchall()
    url_from_base = result_geo[0][3]
    coord_all = (url_from_base.split('search/')[1])
    coord = list(coord_all.split('+'))
    latitude_base = coord[0]
    longitude_base = coord[1][0:9]
    await bot.send_location(message.from_user.id, latitude=latitude_base, longitude=longitude_base)
    #await bot.send_message(f"https://api.telegram.org/bot{telegram_token}/sendlocation?chat_id={message.from_user.id}&latitude={latitude}&longitude={longitude}")


@dp.message_handler(commands='ad')
async def advert(message: aiogram.types.Message):
    connect = sqlite3.connect('maib_admin/db.sqlite3')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM admin_panel_poster")
    results = cursor.fetchall()
    # название result [id][1]
    # описание result [id][2]
    # дополнение к адресу result [id][3]
    # адрес [id][4]
    # дата [id][5]
    # возраст
    # организация
    id = 5  # номер строчки в бд
    await bot.send_message(message.from_user.id, f'Здравствуйте, ожидается мероприятие "{results[id][1]}"\n'
                                                 f'Описание: {results[id][2]}\n'
                                                 f'Мероприятие походит по адресу {results[id][4]}, {results[2][3]}\n'
                                                 f'Дата: {results[id][5]}\n'
                                                 f'Возраст: {results[id][6]}\n'
                           )


@dp.message_handler(commands='quest')
async def enter_quest(message: types.Message):
    hi = (
        """  
        Приветствую, Вы начали квест-викторину
        Я задаю Вам вопросы, а Вы на них отвечаете     
        """)
    await message.answer(hi)
    ask1 = (
        "Вопрос №1. \n\n"
        "В какой области я родился?"
    )
    await message.answer(ask1)
    await Test.Q1.set()


@dp.message_handler(state=Test.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer1 = message.text

    await state.update_data(answer1=answer1)
    ask2 = (
        "Вопрос №2. \n\n"
        "В каком году я родился?"
    )
    await message.answer(ask2)
    await Test.Q2.set()


@dp.message_handler(state=Test.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data.get("answer1")
    answer2 = message.text
    await state.update_data(answer2=answer2)
    ask3 = (
        "Вопрос №3. \n\n"
        "В каком году я переехал в Козлов (Мичуринск)?"
    )
    await message.answer(ask3)
    await Test.Q3.set()


@dp.message_handler(state=Test.Q3)
async def answer_q3(message: types.Message, state: FSMContext):
    answer3 = message.text
    await state.update_data(answer3=answer3)
    ask4 = (
        "Вопрос №4. \n\n"
        "Сколько мне было лет, когда я переехал в Козлов (Мичуринск)?"
    )

    await message.answer(ask4)
    await Test.Q4.set()


@dp.message_handler(state=Test.Q4)
async def answer_q4(message: types.Message, state: FSMContext):
    answer4 = message.text
    await state.update_data(answer4=answer4)
    ask5 = (
        "Вопрос №5. \n\n"
        "Какую смородину я бы рекомендовал Вам посадить? (назвать сорт)"
    )

    await message.answer(ask5)
    await Test.Q5.set()


@dp.message_handler(state=Test.Q5)
async def answer_q5(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = data.get("answer2")
    answer3 = data.get("answer3")
    answer4 = data.get("answer4")
    answer5 = message.text

    def check_answers():
        scores = 0
        if answer1 == "Рязанская" or answer1 == "Рязанская область" or answer1 == "Рязанская губерния" or answer1 == "В Рязанской" or answer1 == "рязанская":
            scores += 1
        if answer2 == "В 1855 году" or answer2 == "1855" or answer2 == "1855 год":
            scores += 1
        if answer3 == "В 1872 году" or answer3 == "1872" or answer3 == "1872 год":
            scores += 1
        if answer4 == "17 лет" or answer4 == "17" or answer4 == "лет 17":
            scores += 1
        if answer5 == "Память Мичурина" or answer5 == "память мичурина":
            scores += 1
        return scores

    score = check_answers()

    await message.answer("Cпасибо за Ваши ответы")
    await message.answer(f"Ваши баллы: {score}")
    await state.reset_state()


# noinspection PyTypeChecker
@dp.message_handler()
async def message_dialogflow(message: aiogram.types.Message):
    text_input = dialogflow.TextInput(
        text=message.text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        session=session, query_input=query_input)
    if response.query_result.fulfillment_text:
        await bot.send_message(message.from_user.id, response.query_result.fulfillment_text)
    else:
        await bot.send_message(message.from_user.id, "Я вас не понял, мне пора в сад")

    log = {
        'Name': message.from_user.username,
        'ID': message.from_user.id,
        'message': message.text,
        'answer': response.query_result.fulfillment_text
    }

    with open('log.txt', 'a', encoding='utf-8') as txt:
        print(log, file=txt)


aiogram.executor.start_polling(dp, skip_updates=True)
