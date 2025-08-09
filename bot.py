from config import TELEGRAM_BOT_TOKEN
from aiogram import Bot, Dispatcher, types
from agent import RAG

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
rag_model = RAG()

@dp.message_handler()
async def handle_message(message: types.Message):
    user_question = message.text
    response = rag_model.forward(user_question)
    await message.reply(response.answer)
