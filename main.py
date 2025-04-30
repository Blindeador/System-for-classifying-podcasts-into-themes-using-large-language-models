"""
Bot de Telegram para análisis de podcasts
-----------------------------------------
Este bot permite buscar podcasts por nombre o analizar desde URL,
transcribiendo y clasificando su contenido.
"""

import logging
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
from bot.handlers import setup_handlers

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main() -> None:
    """Inicializa y ejecuta el bot de Telegram."""
    logger.info("Iniciando el bot de análisis de podcasts...")
    
    # Crear la aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Configurar manejadores
    setup_handlers(application)
    
    # Iniciar el bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")
    application.run_polling(poll_interval=5)

if __name__ == '__main__':
    main()