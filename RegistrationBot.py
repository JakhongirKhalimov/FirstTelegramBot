import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, ContentType, InputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime
import psycopg2

logging.basicConfig(level=logging.INFO)

API_TOKEN = "8096079559:AAFg_Yn4P4RA0RdYw4B9GQJuvdLpZoFi84s"
dp = Dispatcher(storage=MemoryStorage())
router = Router()

# Database connection
connector = psycopg2.connect(
    host='localhost',
    port=5432,
    database='forbot',
    user='postgres',
    password='1602'
)
cursor = connector.cursor()

# Directories for saving files
PHOTO_DESTINATION = r'D:\ForInfo\ForPhoto'
LETTER = r'D:\ForInfo\ForMotL'
RESUME = r'D:\ForInfo\ForResume'

# Define registration states
class Registration(StatesGroup):
    Ism = State()
    Familya = State()
    Yosh = State()
    Telefon_Raqam = State()
    Resume = State()
    MotivatsionXat = State()
    Photo = State()

# Start command handler
@router.message(Command("start"))
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Ro'yxatdan o'tish")]
    ], resize_keyboard=True)
    await message.answer("Ro'yxatdan o'tish uchun tugmani bosing", reply_markup=keyboard)

# Registration process: Request first name
@router.message(F.text == "Ro'yxatdan o'tish")
async def register(message: Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.Ism)

# First name handler
@router.message(StateFilter(Registration.Ism))
async def get_first_name(message: Message, state: FSMContext):
    if message.text.isalpha():
        cursor.execute("SELECT * FROM ForTelegramBot WHERE ism = %s AND familya = %s", (message.text, None))
        if cursor.fetchone():
            await message.answer("Bu ism bilan foydalanuvchi allaqachon mavjud.")
            return
        await state.update_data(ism=message.text)
        await message.answer("Familiyangizni kiriting:")
        await state.set_state(Registration.Familya)
    else:
        await message.answer("Ism faqat harflardan iborat bo'lishi kerak!")

# Last name handler
@router.message(StateFilter(Registration.Familya))
async def get_last_name(message: Message, state: FSMContext):
    if message.text.isalpha():
        user_data = await state.get_data()
        cursor.execute("SELECT * FROM ForTelegramBot WHERE ism = %s AND familya = %s", (user_data['ism'], message.text))
        if cursor.fetchone():
            await message.answer("Bu ism va familiya bilan foydalanuvchi allaqachon mavjud.")
            return
        await state.update_data(familya=message.text)
        await message.answer("Yoshingizni kiriting:")
        await state.set_state(Registration.Yosh)
    else:
        await message.answer("Familiya faqat harflardan iborat bo'lishi kerak!")

# Age handler
@router.message(StateFilter(Registration.Yosh))
async def get_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(yosh=int(message.text))
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Telefon raqamni jo'natish", request_contact=True)]
        ], resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Telefon raqamingizni jo'nating:", reply_markup=keyboard)
        await state.set_state(Registration.Telefon_Raqam)
    else:
        await message.answer("Yosh raqamlardan iborat bo'lishi kerak!")

# Phone number handler
@router.message(StateFilter(Registration.Telefon_Raqam), F.contact)
async def get_phone_number(message: Message, state: FSMContext):
    user_data = await state.get_data()
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    registration_date = datetime.now()

    # Insert user data into the database
    cursor.execute('''INSERT INTO ForTelegramBot (user_id, ism, familya, yosh, telefon_raqam, registration_date)
                      VALUES (%s, %s, %s, %s, %s, %s)''',
                   (user_id, user_data['ism'], user_data['familya'], user_data['yosh'], phone_number, registration_date))
    connector.commit()

    await message.answer("Resume faylini jo'nating:")
    await state.set_state(Registration.Resume)


@router.message(Registration.Resume, F.document)
async def get_resume(message: Message, state: FSMContext):
    user_data = await state.get_data()

    if user_data.get('resume_received', False):
        return  # Skip further documents


    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    file_extension = os.path.splitext(message.document.file_name)[1]
    resume_filename = f"{file.file_unique_id}{file_extension}"
    file_path = os.path.join(RESUME, resume_filename)


    await message.bot.download_file(file.file_path, file_path)
    await state.update_data(resume_filename=resume_filename, resume_received=True)
    await message.answer("Motivatsion xatni jo'nating:")
    await state.set_state(Registration.MotivatsionXat)


# Motivational letter handler
@router.message(Registration.MotivatsionXat)
async def get_motivation_letter(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file = await message.bot.get_file(file_id)
    motivational_filename = f"{file.file_unique_id}.pdf"
    file_path = os.path.join(LETTER, motivational_filename)
    await message.bot.download_file(file.file_path, file_path)

    await state.update_data(photo_path=file_path, motivational_filename=motivational_filename)
    await message.answer("Rasmingizni jo'nating:")
    await state.set_state(Registration.Photo)

# Photo handler
@router.message(StateFilter(Registration.Photo), F.photo)
async def get_photo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    photo_id = message.photo[-1].file_id
    file = await message.bot.get_file(photo_id)
    file_path = os.path.join(PHOTO_DESTINATION, f"{file.file_unique_id}.jpg")
    await message.bot.download_file(file.file_path, file_path)

    await state.update_data(photo_path=file_path)

    await message.answer("Ro'yxatdan muvaffaqiyatli o'tdingiz! Akkaunt haqida bilish uchun tugmani bosing.")
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Akkaunt haqida bilish")]
    ], resize_keyboard=True)
    await message.answer("Akkaunt haqida bilish uchun tugmani bosing:", reply_markup=keyboard)

# Account info handler
@router.message(F.text == "Akkaunt haqida bilish")
async def get_account_info(message: Message):
    user_id = message.from_user.id
    cursor.execute('''SELECT ism, familya, yosh, telefon_raqam, registration_date, 
                             motivatsion_xat_filename, resume_filename 
                      FROM ForTelegramBot WHERE user_id = %s''', (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        ism, familya, yosh, telefon_raqam, registration_date, motivational_filename, resume_filename = user_data

        # Send text details
        await message.answer(f"Ism: {ism}\n"
                             f"Familya: {familya}\n"
                             f"Yosh: {yosh}\n"
                             f"Telefon: {telefon_raqam}\n"
                             f"Registration Date: {registration_date}\n")

        # Send Motivational Letter PDF if it exists
        motivatsion_xat_path = os.path.join(LETTER, motivational_filename)
        if motivational_filename and os.path.exists(motivatsion_xat_path):
            await message.answer_document(InputFile(motivatsion_xat_path))
        else:
            await message.answer("Motivatsion xat topilmadi.")

        # Send Resume PDF if it exists
        resume_path = os.path.join(RESUME, resume_filename)
        if resume_filename and os.path.exists(resume_path):
            await message.answer_document(InputFile(resume_path))
        else:
            await message.answer("Resume topilmadi.")

        # Create buttons to resend files
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            KeyboardButton(text="Motivatsion xatni qaytarish"),
            KeyboardButton(text="Resume faylini qaytarish")
        ]
        keyboard.add(*buttons)

        await message.answer("Fayllarni qaytarish uchun quyidagi tugmalardan foydalaning:", reply_markup=keyboard)
    else:
        await message.answer("Foydalanuvchi ma'lumotlari topilmadi.")

# Resend motivational letter
@router.message(F.text == "Motivatsion xatni qaytarish")
async def resend_motivation_letter(message: Message):
    user_id = message.from_user.id
    cursor.execute('''SELECT motivatsion_xat_filename FROM ForTelegramBot WHERE user_id = %s''', (user_id,))
    motivational_filename = cursor.fetchone()

    if motivational_filename:
        motivatsion_xat_path = os.path.join(LETTER, motivational_filename[0])
        if os.path.exists(motivatsion_xat_path):
            await message.answer_document(InputFile(motivatsion_xat_path))
        else:
            await message.answer("Motivatsion xat topilmadi.")
    else:
        await message.answer("Foydalanuvchi ma'lumotlari topilmadi.")

# Resend resume file
@router.message(F.text == "Resume faylini qaytarish")
async def resend_resume_file(message: Message):
    user_id = message.from_user.id
    cursor.execute('''SELECT resume_filename FROM ForTelegramBot WHERE user_id = %s''', (user_id,))
    resume_filename = cursor.fetchone()

    if resume_filename:
        resume_path = os.path.join(RESUME, resume_filename[0])
        if os.path.exists(resume_path):
            await message.answer_document(InputFile(resume_path))
        else:
            await message.answer("Resume fayli topilmadi.")
    else:
        await message.answer("Foydalanuvchi ma'lumotlari topilmadi.")

# Start the bot
async def main():
    bot = Bot(token=API_TOKEN)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
