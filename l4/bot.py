import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
# basedir = os.path.abspath(os.path.dirname(__file__))
# basedir = os.path.split(basedir)[0]
# load_dotenv(os.path.join(basedir, '.env'))
load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# MODEL = "test-text-davinci"
MODEL = os.getenv("ENGINE")
OPENAI_NAME = os.getenv("OPENAI_NAME")
API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://{}.openai.azure.com/openai/deployments/{}/chat/completions?api-version=2023-12-01-preview".format(OPENAI_NAME, MODEL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot powered by Azure OpenAI, please talk to me!")

async def photo(update, context):
    if update.message.photo:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Complete this function')

async def echo(update, context):
    preprompt = os.getenv("PREPROMPT")
    data = {
        "messages": [
            {"role": "system", "content": preprompt},
            {"role": "user", "content": update.message.text}
        ],
        "max_tokens": 100,
        "temperature": 1,
        "frequency_penalty": 2,
        "presence_penalty": 2,
        "top_p": 0.5,
        "n": 1,
        "stop": ["User:"]
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, data=json.dumps(data)) as response:
            print(response)
            if response.status == 200:
                result = (await response.json())['choices'][0]['message']['content']
                text_parts = result.split("\n", 1)
                new_text = text_parts[1] if len(text_parts) > 1 else text_parts
                await context.bot.send_message(chat_id=update.effective_chat.id, text=new_text)
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't understand your question.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("TG_BOT_TOKEN")).build()
    
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    photo_handler = MessageHandler(filters.PHOTO, photo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(photo_handler)
    
    application.run_polling()
