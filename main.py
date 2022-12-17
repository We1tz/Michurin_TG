import logging
import os
import sqlite3
import aiogram
import google.cloud.dialogflow
from texts import txt
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from keyboards import start_keyboard, locate
from config import telegram_token
from states import Test

storage = MemoryStorage()


class User:
    def __init__(self, name, id, offer):
        self.name = name
        self.id = id
        self.offer = offer


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
    await bot.send_message(message.from_user.id, maps)
    await bot.send_message(message.from_user.id, "https://www.google.ru/maps/place/Мичуринский+краеведческий+музей/@52.8942197,40.5054534,17z/data=!3m1!4b1!4m5!3m4!1s0x413991162386f7e7:0x98f2e38b89522c6d!8m2!3d52.8942197!4d40.5076421")

@dp.message_handler(commands='афиша')
async def advert(message: types.Message):
    await bot.send_message(message.from_user.id, txt.ad)

@dp.message_handler(commands='предложить')
async def offer_update(message: types.Message):
    message_for_user = (f"""Здравствуй, путник {message.from_user.username} \n
Коли ты забрел в мою усадьбу, считай своим долгом внести свою лепту в ее процветание.  \n

Чтобы помочь развитию проекта, пришли одним сообщением вопрос, который хочешь добавить в бота, а также ответ, пример ниже:  \n

"Какой ваш родной город?" - "Я родился в Рязани, однако судьба привела меня в город Козлов, который позже был назван моим именем" \n
После модерации ваш вопрос будет добавлен в бота""")

    await message.answer(message_for_user)
    user = User(message.from_user.username, message.from_user.id, '')
    print('Пользователь создан')
    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                        name TEXT,
                        id TEXT,
                        offer TEXT
                    )""")
    cursor.execute(f"SELECT id FROM users WHERE id = {user.id}")
    data = cursor.fetchone()
    if data is None:
        information = (user.name, user.id, user.offer)
        cursor.execute('INSERT INTO users VALUES(?, ?, ?);', information)
        connect.commit()
    else:
        print('Пропуск создания пользователь уже существует')
    await Test.Q9.set()


@dp.message_handler(state=Test.Q9)
async def offer_update_1(message: types.Message, state: FSMContext):
    new_offers = message.text

    await state.update_data(new_offers=new_offers)

    connect = sqlite3.connect('users.db')
    cursor = connect.cursor()
    user = User(message.from_user.first_name, message.from_user.id, new_offers)
    cursor.execute('UPDATE users SET offer=? WHERE id=?', (user.offer, user.id))
    connect.commit()

    await message.answer('Ответ принят, спасибо!')
    await state.reset_state()


@dp.message_handler(commands='quest')
async def enter_quest(message: types.Message):
    hi = (
        """  
        Приветствую, Вы начали квест-викторину
        Я задаю Вам вопросы, а Вы на них отвечаете     
        """
    )
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
