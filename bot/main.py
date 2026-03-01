import os
import asyncio
import logging
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
BOT_SECRET = os.getenv("BOT_OTP_SECRET")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# telefon so'rash keyboard
kb = ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(
    KeyboardButton(
        text="📱 Telefon yuborish",
        request_contact=True
    )
)


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "Login uchun telefon yuboring",
        reply_markup=kb
    )


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(msg: types.Message):

    phone = msg.contact.phone_number
    username = msg.from_user.username

    try:

        r = requests.post(
            API_URL,
            json={
                "phone": phone,
                "username": username
            },
            headers={
                "X-BOT-SECRET": BOT_SECRET
            },
            timeout=10
        )

        data = r.json()

        code = data["code"]

        await msg.answer(
            f"🔑 Login code:\n\n{code}"
        )

    except Exception as e:

        await msg.answer("Xatolik yuz berdi")


if __name__ == "__main__":

    executor.start_polling(dp, skip_updates=True)