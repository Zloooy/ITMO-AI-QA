from yandex_cloud_ml_sdk import YCloudML
from yandex_cloud_ml_sdk.auth import IAMTokenAuth
from config import YANDEX_FOLDER_ID, YGPT_SERVICE_ACCOUNT_KEY_FILE_CREDENTIALS, TELEGRAM_BOT_TOKEN
from utils import get_iam
from aiogram import Bot, Dispatcher, types, executor
from agent import RAG

sdk = YCloudML(
    folder_id=YANDEX_FOLDER_ID,
    auth=IAMTokenAuth(get_iam(YGPT_SERVICE_ACCOUNT_KEY_FILE_CREDENTIALS)),
)
doc_model = sdk.models.text_embeddings("doc")
query_model = sdk.models.text_embeddings("query")

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
rag_model = RAG()

@dp.message_handler()
async def handle_message(message: types.Message):
    user_question = message.text
    response = rag_model.forward(user_question)
    await message.reply(response.answer)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
