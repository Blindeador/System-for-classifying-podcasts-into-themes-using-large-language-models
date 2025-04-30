import os

# Tokens y claves de API
#Telegram Bot Token 
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8107776185:AAH6Etmw07GDhwmmOLr3PuXpv5krkNPi2bg")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "b642f85fd62b4400b6f44b729dc0c4da")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "147d056dbf354443872a8a1eff0b7c40")

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# Rutas de archivos
BASE_DATA_DIR = "data"
AUDIO_PATH = os.path.join(BASE_DATA_DIR, "audio.wav")
TRANSCRIPT_PATH = os.path.join(BASE_DATA_DIR, "transcription.srt")

# Constantes generales
MAX_LENGTH = 4000  # Longitud máxima del mensaje de Telegram
MAX_SEARCH_RESULTS = 3  # Número máximo de resultados de búsqueda a mostrar

# Asegurar que existen los directorios necesarios
os.makedirs(BASE_DATA_DIR, exist_ok=True)