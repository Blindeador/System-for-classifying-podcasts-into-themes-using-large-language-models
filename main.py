import logging
from bot.bot import main as start_bot

# Configuración del logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Punto de entrada del sistema de clasificación de podcasts."""
    logging.info("Iniciando el sistema de clasificación de podcasts...")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Llama a la función principal del bot
    start_bot()

if __name__ == "__main__":
    main()