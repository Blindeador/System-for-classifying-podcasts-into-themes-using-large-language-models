from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from bot.handlers import start, handle_audio

def main():
    from config import TELEGRAM_BOT_TOKEN

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Registra comandos y manejadores
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, handle_audio))

    updater.start_polling()
    updater.idle()