import os
import json
from aiogram import Bot, Dispatcher, types, executor
from config import BOT_TOKEN, UPI_ID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

USER_DATA_FILE = "data/users.json"

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f)

users = load_users()

@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    users[str(msg.from_user.id)] = users.get(str(msg.from_user.id), {"premium": False})
    save_users(users)
    await msg.answer("📚 Welcome to CS Study Library!\nUse /books to view available books.")

@dp.message_handler(commands=['books'])
async def books(msg: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📖 Free Books", callback_data="free"),
        InlineKeyboardButton("🔐 Premium Books", callback_data="premium")
    )
    await msg.answer("Choose book type:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ["free", "premium"])
async def show_books(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    access = users.get(user_id, {}).get("premium", False)
    book_type = callback.data
    path = f"cs_study_books/{book_type}"

    if book_type == "premium" and not access:
        await callback.message.answer(
            f"🔒 Premium access required.\nSend ₹199 to this UPI ID:\n\n`{UPI_ID}`\n\nThen reply `/verify` after payment."
        )
        return

    msg = "📚 Available Books:\n\n"
    for root, _, files in os.walk(path):
        for file in files:
            name = file.replace("__", " ₹").replace(".pdf", "")
            msg += f"• {name}\n"
    await callback.message.answer(msg)

@dp.message_handler(commands=['verify'])
async def verify(msg: types.Message):
    users[str(msg.from_user.id)] = {"premium": True}
    save_users(users)
    await msg.answer("✅ Premium access approved. Use /books to view premium books.")

@dp.message_handler(commands=['help'])
async def help_msg(msg: types.Message):
    await msg.answer("📌 Use /books to browse and download books.\nFor premium books, pay first and then /verify.")

@dp.message_handler(commands=['myid'])
async def myid(msg: types.Message):
    await msg.answer(f"Your Telegram ID: `{msg.from_user.id}`", parse_mode='Markdown')
