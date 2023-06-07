import math
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import math
import os
import re
import sqlite3
from pathlib import Path
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, InputFile

import aiogram
import google.cloud.dialogflow
import google.cloud.dialogflow
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv

import config
import keyboards.locate
from keyboards import start_keyboard
from states import Test
from stt import STT
from texts import txt
from tts import TTS
import asyncio

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=config.telegram_token)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
tts = TTS()
stt = STT()
dialogflow = google.cloud.dialogflow

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "michurinbot-350715-99cf31d6b692.json"

session_client = dialogflow.SessionsClient()
project_id = 'michurinbot-350715'
session_id = 'sessions'
language_code = 'ru'
session = session_client.session_path(project_id, session_id)


@dp.message_handler(commands="start")
async def cmd_start(message: aiogram.types.Message):
    await message.answer(txt.hello, reply_markup=start_keyboard.keyboard)
    # Отправка текста спустя 3 часа
    await asyncio.sleep(3 * 60 * 60)
    await message.answer("Прошло уже 3 часа, а ты не проявляешь активность, я уже яблону посадил")

    # Отправка текста спустя день
    await asyncio.sleep(24 * 60 * 60)
    await message.answer("Привет, ты давно не задаешь мне вопросы, не хочешь узнать что-то новое?")

    # Отправка текста спустя неделю
    await asyncio.sleep(7 * 24 * 60 * 60)
    await message.answer("Прошла целая неделя, я успел уже вывести новый сорт, а от тебя еще нет активности")
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    username = message.from_user.username
    message_id = message.from_user.id

    # Проверяем существование пользователя в базе данных
    cursor.execute('SELECT * FROM users WHERE message_id = ?', (message_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        print('Пользователь существует')
    else:
        cursor.execute('INSERT INTO users (username, message_id) VALUES (?, ?)', (username, message_id))
        connection.commit()
        print('Пользователь добавлен в базу данных')

    connection.close()

    buttons = [
        types.InlineKeyboardButton(text="Telegram", url="https://t.me/+HFKvzFZaOvdkNDVi "),
        types.InlineKeyboardButton(text="VK", url="https://vk.com/club217810823")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer(txt.hello, reply_markup=start_keyboard.keyboard)
    await message.answer("Ещё подпишитесь на наши каналы, чтобы узнавать об обновлениях раньше других :) \n",
                         reply_markup=keyboard)


@dp.message_handler(commands="mail")
async def mail_to_user(message: Message, state: FSMContext):
    print(message.from_user.id)
    right_user = ['1922232899', '129991831']
    if str(message.from_user.id) == str(right_user[0]) or str(message.from_user.id) == str(right_user[1]):
        await message.answer('Здравствуйте, вы авторизованы. \n'
                             'Какое сообщение или медиа-файл необходимо отправить? \n')
        await Test.Q20.set()
        await state.update_data(command="mail")
    else:
        await message.answer('Ошибка доступа')


@dp.message_handler(content_types=types.ContentTypes.ANY, state=Test.Q20)
async def send_mail_message(message: Message, state: FSMContext):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('SELECT message_id FROM users')
    message_ids = cursor.fetchall()
    data = await state.get_data()

    media_types = ["photo", "audio", "video"]
    if message.content_type in media_types:
        for message_id in message_ids:
            chat_id = int(message_id[0])
            if message.content_type == "photo":
                media = message.photo[-1].file_id
                await bot.send_photo(chat_id, media)
            elif message.content_type == "audio":
                media = message.audio.file_id
                await bot.send_audio(chat_id, media)
            elif message.content_type == "video":
                media = message.video.file_id
                await bot.send_video(chat_id, media, supports_streaming=True)
    else:
        message_from_users = message.text
        for message_id in message_ids:
            chat_id = int(message_id[0])
            await bot.send_message(chat_id, text=message_from_users)

    await state.finish()
    connection.close()



@dp.message_handler(content_types=[
    types.ContentType.VOICE,
    types.ContentType.AUDIO,
    types.ContentType.DOCUMENT
]
)
async def voice_message_handler(message: types.Message, state: FSMContext):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if message.content_type == types.ContentType.VOICE:
        file_id = message.voice.file_id
    elif message.content_type == types.ContentType.AUDIO:
        file_id = message.audio.file_id
    elif message.content_type == types.ContentType.DOCUMENT:
        file_id = message.document.file_id
    else:
        await message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.tmp")
    await bot.download_file(file_path, destination=file_on_disk)
    await message.reply("Аудио получено")

    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"

    os.remove(file_on_disk)

    text_input = dialogflow.TextInput(
        text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        session=session, query_input=query_input)
    if response.query_result.fulfillment_text:
        await bot.send_message(message.from_user.id, response.query_result.fulfillment_text)
    else:
        await bot.send_message(message.from_user.id, "Я вас не понял, мне пора в сад")



@dp.message_handler(commands="find")
async def locate(message: aiogram.types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Здравствуйте, нажмите на кнопку, чтобы отправить своё местоположение',
                           reply_markup=keyboards.locate.keyboard_location)
    await Test.Q9.set()
    await state.update_data(command="find")


@dp.message_handler(state=Test.Q9, content_types=types.ContentTypes.LOCATION)
async def answer_q1(message: types.Message, state: FSMContext):
    # получение локации и координат пользователя
    data = await state.get_data()
    command = data.get("command")
    latitude_1 = message.location.latitude
    longitude_2 = message.location.longitude
    await state.finish()

    # функция для расчета расстояния между двумя координатами
    def distance(lat1, lon1, lat2, lon2):
        R = 6371  # радиус Земли в км
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # получение списка координат из базы данных
    connect = sqlite3.connect('maib_admin/db.sqlite3')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM admin_panel_geo")
    result_geo = cursor.fetchall()

    latitude_user = latitude_1
    longitude_user = longitude_2

    min_distance = None
    closest_coordinate = None
    closest_name = None
    all_coordinates = []
    # обработка google map url
    for row in result_geo:
        url = row[3]
        name = row[1]
        match = re.search(r"@([\d\.]+),([\d\.]+)", url)
        latitudes = float(match.group(1))
        longitudes = float(match.group(2))
        dist = distance(latitudes, longitudes, latitude_user, longitude_user)
        if min_distance is None or dist < min_distance:
            min_distance = dist
            closest_coordinate = (latitudes, longitudes)
            closest_name = name
        all_coordinates.append((name, (latitudes, longitudes), dist))

    # создаем инлайн клавиатуру с более далекими достопримечательностями
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    for name, coordinate, dist in sorted(all_coordinates, key=lambda x: x[2])[1:3]:
        inline_keyboard.add(types.InlineKeyboardButton(
            text=f"{name} ({dist:.2f} км)",
            callback_data=f"location_{coordinate[0]}_{coordinate[1]}"
        ))

    # отправляем пользователю ближайшую координату и инлайн клавиатуру с более далекими достопримечательностями
    await bot.send_message(message.from_user.id, f"Ближайшая к вам достопримечательность: {closest_name}",
                           reply_markup=start_keyboard.keyboard)
    await bot.send_location(message.from_user.id, latitude=closest_coordinate[0], longitude=closest_coordinate[1],
                            reply_markup=inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('location_'))
async def process_location_callback(callback_query: types.CallbackQuery):
    _, latitude, longitude = callback_query.data.split('_')
    await bot.send_location(callback_query.from_user.id, latitude=float(latitude), longitude=float(longitude))
    await bot.answer_callback_query(callback_query.id)


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_button(callback_query: types.CallbackQuery):
    # Разбиваем строку callback_data на параметры с помощью символа "="
    callback_data = callback_query.data
    event_id = int(callback_data.split("=")[1])

    # Получаем информацию о мероприятии из базы данных
    connect = sqlite3.connect('maib_admin/db.sqlite3')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM admin_panel_poster WHERE id = ?", (event_id,))
    event_info = cursor.fetchone()

    # Отправляем сообщение с информацией о мероприятии
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=f'Здравствуйте, ожидается мероприятие "{event_info[1]}"\n'
             f'Описание: {event_info[2]}\n'
             f'Мероприятие походит по адресу {event_info[4]}, ({event_info[3]})\n'
             f'Дата: {event_info[5]}\n'
             f'Возраст: {event_info[6]}\n'
    )

    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(commands='ad')
async def advert(message: aiogram.types.Message):
    connect = sqlite3.connect('maib_admin/db.sqlite3')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM admin_panel_poster")
    results = cursor.fetchall()

    buttons = []
    for i, event in enumerate(results):
        button = InlineKeyboardButton(text=event[1], callback_data=f"event_id={event[0]}")
        buttons.append([button])

    # создаем inline клавиатуру с кнопками
    reply_markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_message(
        chat_id=message.from_user.id,
        text="Выберите мероприятие:",
        reply_markup=reply_markup
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
