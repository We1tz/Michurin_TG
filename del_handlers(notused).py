@dp.message_handler(commands='предложить')
async def offer_update(message: types.Message):
    message_for_user = (f"""Здравствуй, путник {message.from_user.username} \n
Коли ты забрел в мою усадьбу, считай своим долгом внести свою лепту в ее процветание.  \n

Чтобы помочь развитию проекта, пришли одним сообщением вопрос, который хочешь добавить в бота, а также ответ, пример ниже:  \n

"Какой ваш родной город?" - "Я родился в Рязани, однако судьба привела меня в город Козлов, который позже был назван моим именем" \n
После модерации ваш вопрос будет добавлен в бота""")
    await bot.send_message(message.from_user.id, message_for_user)

    # временно отключенная команда из-за доработки другого и данную команду не используют




class User:
    def __init__(self, name, id, offer):
        self.name = name
        self.id = id
        self.offer = offer


        # неиспользуемый класс на данный момент относится к предложить, пока неактуален