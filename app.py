import asyncio
from email.policy import default
from random import randint

import  psycopg2

from aiogram import Bot, Dispatcher, types, F, Router, BaseMiddleware
from aiogram.filters import CommandStart, Command, CommandObject
from  aiogram.enums import ParseMode
from aiogram.utils.formatting import (
    Bold, as_line, as_marked_section, as_key_value, HashTag, as_list
)
from aiogram import html
from aiogram.types import LinkPreviewOptions
from aiogram.types import FSInputFile, URLInputFile, BufferedInputFile
from aiogram.types import  Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.markdown import hide_link
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder
from random import randint
from datetime import datetime
from aiogram.filters import MagicData
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


API_TOKEN = "8096079559:AAFg_Yn4P4RA0RdYw4B9GQJuvdLpZoFi84s"
dp = Dispatcher()
router = Router()

connector = psycopg2.connect(
    host='localhost',
    port=5432,
    database='telegram_bot',
    user='postgres',
    password='1602'
)

class SomeMiddeleware(BaseMiddleware) :
     async def __call__(
             self,
             handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
             event: TelegramObject,
             data: Dict[str, Any]
     ) -> Any:
         print("Before handler")
         result = await handler(event, data)
         print("After handler")
         return result

















@router.message(F.text)
async def stranger_go_away(message: Message):
    if message.from_user.id not in (111, 777):
        await message.answer("Я с тобой не разговариваю!")
# working with link
@dp.message(Command("hidden_link"))
async def hidden_link(message: Message):
    await message.reply(
        f"{hide_link('https://telegra.ph/file/562a512448876923e28c3.png')}"
        f"Документация Telegram: *существует*\n"
        f"Пользователи: *не читают документацию*\n"
        f"Груша:"
    )

# for keyboards
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb =[
        [
            types.KeyboardButton(text="С пюрешкой"),
            types.KeyboardButton(text="Без пюрешки")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True ,
        input_field_placeholder = "Выберите способ подачи"
    )
    await message.answer("Как подавать котлеты?", reply_markup=keyboard)

@dp.message(F.text.lower() == "с пюрешкой")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!")

@dp.message(F.text.lower() == "без пюрешки")
async def without_puree(message: types.Message):
    await message.reply("Так невкусно")

@dp.message(Command("create_keyboard"))
async def create_keyboard(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1,17):
        builder.add(types.KeyboardButton(text = str(i)))
    builder.adjust(4)
    await message.answer(
        "Выберите число:",
        reply_markup=builder.as_markup(resize_keyboard=True)

    )

@dp.message(F.text.lower() == "1")
async def with_puree(message: types.Message):
    await message.reply("Отличный выбор!")


# for special keyboard
@dp.message(Command("special_keyboard"))
async def special_keyboard(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Запросить геолокацию", request_location=True),
        types.KeyboardButton(text="Запросить контакт", request_contact=True)
    )
    builder.row(types.KeyboardButton(
        text="Создать викторину",
        request_poll=types.KeyboardButtonPollType(type="quiz"))
    )
    # ... а третий снова из двух
    builder.row(
        types.KeyboardButton(
            text="Выбрать премиум пользователя",
            request_user=types.KeyboardButtonRequestUser(
                request_id=1,
                user_is_premium=True
            )
        ),
        types.KeyboardButton(
            text="Выбрать супергруппу с форумами",
            request_chat=types.KeyboardButtonRequestChat(
                request_id=2,
                chat_is_channel=False,
                chat_is_forum=True
            )
        )
    )

    await message.answer(
        "Выберите действие:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
@dp.message(F.user_shared)
async def on_user_shared(message: types.Message):
    print(
        f"Request {message.user_shared.request_id}",
        f"UserId {message.user_shared.user_id}",
    )
@dp.message(F.chat_shared)
async def on_chat_shared(message: types.Message):
    print(
        f"Request {message.chat_shared.request_id}",
        f"ChatId {message.chat_shared.chat_id}",
    )

#inline buttons
#Url buttons

@dp.message(Command("inline_url"))
async def cmd_inline_url(message: types.Message, bot: Bot):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="GitHub", url="https://github.com")
    )
    builder.row(types.InlineKeyboardButton(
        text="Оф. канал Telegram",
        url="tg://resolve?domain=telegram")
    )

    # Чтобы иметь возможность показать ID-кнопку,
    # У юзера должен быть False флаг has_private_forwards
    user_id = 5193823381
    chat_info = await bot.get_chat(user_id)
    if not chat_info.has_private_forwards:
        builder.row(types.InlineKeyboardButton(
            text="Какой-то пользователь",
            url=f"tg://user?id={user_id}")
        )

    await message.answer(
        'Выберите ссылку',
        reply_markup=builder.as_markup(),
    )
# for call back
@dp.message(Command("random"))
async def cmd_random(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text = "Нажми меня",
        callback_data="random_value"
    ))
    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=builder.as_markup()
    )
@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: types.CallbackQuery):
    await callback.message.answer(
        str(randint(1,10))
    )
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )

def get_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="-1", callback_data="num_decr"),
            types.InlineKeyboardButton(text="+1", callback_data="num_incr"),
        ],
        [types.InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



# for added and lefted users
@dp.message(F.new_chat_members)
async def somebody_new(message: Message):
    for user in message.new_chat_members:
        await message.reply(
            f"Hello new user {user.full_name}!",
        )
@dp.message(F.left_chat_member)
async def left_group(message: Message):
    user = message.left_chat_member
    await message.reply(
        f"{user.full_name} покинул(а) группу."
    )



# does not work
@dp.message(Command("photo"))
async def photo_dow(message: Message):
    album_builder = MediaGroupBuilder(
        caption = "Общая подпись для будущего альбома"
    )
    album_builder.add(
        type="photo",
        media=FSInputFile("image_from_pc.jpg")
    )
    album_builder.add_photo(
        media="https://picsum.photos/seed/groosha/400/300"
    )
    album_builder.add_photo(
        media="<ваш file_id>"
    )
    await message.answer_media_group(
        # Не забудьте вызвать build()
        media=album_builder.build()
    )


# for download photos but does not work
@dp.message(Command("images"))
async def upload_photo(message: Message):
    file_ids = []
    with open("buffer_emulation.jpg", "rb") as image_from_buffer:
        result = await message.answer_photo(
            BufferedInputFile(
                image_from_buffer.read(),
                filename="image from buffer.jpg"
            ),
            caption="Изображение из буфера"
        )
        file_ids.append(result.photo[-1].file_id)

    # Отправка файла из файловой системы
    image_from_pc = FSInputFile("image_from_pc.jpg")
    result = await message.answer_photo(
        image_from_pc,
        caption="Изображение из файла на компьютере"
    )
    file_ids.append(result.photo[-1].file_id)

    # Отправка файла по ссылке
    image_from_url = URLInputFile("https://picsum.photos/seed/groosha/400/300")
    result = await message.answer_photo(
        image_from_url,
        caption="Изображение по ссылке"
    )
    file_ids.append(result.photo[-1].file_id)
    await message.answer("Отправленные файлы:\n"+"\n".join(file_ids))

@dp.message(Command("gif"))
async def gif(message: Message):
    await message.answer_animation(
        animation="",
        caption="Я сегодня",
        show_caption_above_media=True
    )

@dp.message(F.photo)
async def download_photo(message: Message, bot: Bot):
    await bot.download(
        message.photo[-1],
        destination=f"/tmp/{message.photo[-1].file_id}.jpg"
    )


@dp.message(F.sticker)
async def download_sticker(message: Message, bot: Bot):
    await bot.download(
        message.sticker,
        # для Windows пути надо подправить
        destination=f"/tmp/{message.sticker.file_id}.webp"
    )




# for links
@dp.message(Command("links"))
async def links(message: Message):
    links_text = (
        "https://nplus1.ru/news/2024/05/23/voyager-1-science-data"
        "\n"
        "https://t.me/telegram"
    )
    options_1 = LinkPreviewOptions(is_disabled=True)
    await message.answer(
        f"Нет превью ссылок\n {links_text}",
        link_preview_options=options_1
    )
    options_2 = LinkPreviewOptions(
        url = "https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True
    )
    await message.answer(
        f"Маленькое превью\n{links_text}",
        link_preview_options=options_2
    )
    options_3 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True
    )
    await message.answer(
        f"Большое превью\n{links_text}",
        link_preview_options=options_3
    )
    options_4 = LinkPreviewOptions(
        url="https://nplus1.ru/news/2024/05/23/voyager-1-science-data",
        prefer_small_media=True,
        show_above_text=True
    )
    await message.answer(
        f"Маленькое превью над текстом\n {links_text}",
        link_preview_options=options_4
    )
    options_5 = LinkPreviewOptions(
        url = "https://t.me/telegram"
    )
    await message.answer(
        f"Предпросмотр не первой ссылки\n {links_text}",
        link_preview_options=options_5
    )
@dp.message(F.animation)
async def animation(message: Message):
    await message.reply_animation(message.animation.file_id)


#after sending message to this bot this func separate URL, Email, Password
@dp.message(Command("sms"))
async def extract_data(message: Message):
    data = {
        "url": "<N/A>",
        "email": "<N/A>",
        "code": "<N/A>"
    }
    entities = message.entities or []
    for item in entities:
        if item.type in data.keys():
            data[item.type] = item.extract_from(message.text)
    await message.reply(
        "Вот что я нашёл:\n"
        f"URL: {html.quote(data['url'])}\n"
        f"E-mail: {html.quote(data['email'])}\n"
        f"Пароль: {html.quote(data['code'])}"
    )

#SetTimmer for Alarm
@dp.message(Command("settimer"))
async def set_timer(
        message: Message,
        command: CommandObject
):
    if command.args is None :
        await message.answer("Ошибка: не переданы аргументы")
    try:
        delay_time, text_to_send = command.args.split(" ", maxsplit=1)
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/settimer <time> <message>"
        )
        return
    await message.answer(
        "Таймер добавлен!\n"
        f"Время: {delay_time}\n"
        f"Текст: {text_to_send}"
    )

# this function for new users who click the start this func save her/him info to database
@dp.message(CommandStart())
async def start(message: types.Message):

    cursor = connector.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username) VALUES (%s, %s)""",
                   (message.from_user.id, message.from_user.full_name))
    connector.commit()
    cursor.close()
    await message.answer(text="Hi")

#it is for new bot's users
@dp.message(Command("hello"))
async def cmd_hello(message: types.Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>",
        parse_mode = ParseMode.HTML
    )

#it is for the test
@dp.message(Command("advanced_example"))
async def advanced_example(message: types.Message):
    content = as_list(
        as_marked_section(
            Bold("Succes"),
            "Test1",
            "Test 3",
            "Test 4",
            marker="✅ ",
        ),
        as_marked_section(
            Bold("Failed"),
            "Test 2",
            marker="❌ ",
        ),
        as_marked_section(
            Bold("Summary"),
            as_key_value("Total", 4),
            as_key_value("Succes", 3),
            as_key_value("Failed", 1),
        ),
        HashTag("#Test"),
        sep="\n\n",
    )
    await message.answer(**content.as_kwargs())

# for CRUD operations select and insert
@dp.message(Command("select"))
async def select(message: types.Message):
    cursor = connector.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    await message.answer(text="Data from Database: \n{}".format(result))

# for CRUD operations select and insert
@dp.message(Command("insert"))
async def insert_data(message: types.Message) -> None:
    try:
        spitted_msg = message.text.split(" ")
        user_id = spitted_msg[1]
        username = spitted_msg[2]
    except (ValueError, IndexError):
        await message.answer("Invalid input format")
        return
    cursor = connector.cursor()
    cursor.execute("""
    INSERT INTO users (user_id, username) VALUES (%s, %s)""",
                   (user_id, username))
    connector.commit()
    cursor.close()
    await message.answer(text="Data inserted successfully ")


async def main() -> None:
    bot = Bot(token=API_TOKEN)
    await dp.start_polling(bot)
if __name__ == '__main__':
    print("Bot started")
    asyncio.run(main())