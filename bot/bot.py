from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.handlers import start, handle_audio, button_handler 
from telegram.ext import CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN

def main():

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra comandos y manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_audio))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Handlers registered")

    application.run_polling(poll_interval=5)