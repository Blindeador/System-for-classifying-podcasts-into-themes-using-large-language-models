# System-for-classifying-podcasts-into-themes-using-large-language-models
# 🎙 Podcast Classifier Bot  
Un sistema para la **clasificación automática de podcasts** mediante el uso de **modelos grandes de lenguaje (LLMs)**, desplegado en un **bot de Telegram**.

## 🚀 Funcionalidades
- **Selección de Podcast:** En base a un nombre da a elegir al usuario Podcasta los que puede referirse gracias a la **Api-spotify**.
- **Transcripción de audio:** Convierte archivos de podcast en texto utilizando [Faster-Whisper].
- **Clasificación automática:** Clasifica el contenido del podcast en temáticas y genera resúmenes, analisis por segmento usando **Llama-Maverick**.
- **Recomendaciones automáticas:** Recomienda en base al podcast seleccionado usando **Api-spotify** y **Llama-Maverick**.
- **Interfaz de usuario:** Consulta información sobre los podcasts a través de un **bot de Telegram**.

---

## 🛠️ Tecnologías utilizadas
- **Python** (backend y lógica del bot)
- **Api-spotify** (Búsqueda y recomendación de podcast)
- **Faster-Whisper** (transcripción de audio)
- **Llama-Maverick** (análisis semántico)
- **python-telegram-bot** (interacción con Telegram)
- **FastAPI (opcional)** (para futuras integraciones)
- **SQLite/PostgreSQL (opcional)** (almacenamiento de datos)

---

## 📦 Estructura del proyecto
```plaintext
podcast-classifier-bot/
├── bot/                     # Lógica de procesamiento y manejo de solicitudes
│   ├── audio.py             # Funciones relacionadas con el análisis de audio
│   ├── handlers.py          # Controladores para manejar flujos de datos
│   └── utils.py             # Funciones que sirven de utilidad
├── data/                    # Archivos de datos (transcripciones, audios, etc.)
│   └── transcription.srt    # Ejemplo de transcripción en formato SRT
├── models/                  # Modelos y lógica de clasificación
│   ├── classifier.py        # Clasificación, análisis y recomendaciones
│   └── transcriber.py       # Transcripción del audio
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Documentación del proyecto
├── config.py                # Configuración de variables de entorno
├── main.py                  # Punto de entrada del sistema
└── .gitignore               
```

## Requisitos previos
Antes de comenzar, asegúrate de tener instalado lo siguiente:

- Python 3.8 o superior
- Pip para la gestión de paquetes
- Una cuenta en OpenRouter para acceder a la API de modelos de lenguaje
- Credenciales de cliente de Spotify (Client ID y Client Secret)

---

## Instalación
1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/system-for-classifying-podcasts-into-themes-using-large-language-models.git
cd system-for-classifying-podcasts-into-themes-using-large-language-models
```
2. Crea un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
3. Instala las dependencias:
```bash
pip install -r requirements.txt
```
4. Configura las credenciales:
- Crea un archivo config.py en la raíz del proyecto con el siguiente contenido:
```bash
TELEGRAM_BOT_TOKEN = "tu_clave_del_bot_telegram"
OPENROUTER_API_KEY = "tu_clave_de_openrouter"
SPOTIFY_CLIENT_ID = "tu_client_id_de_spotify"
SPOTIFY_CLIENT_SECRET = "tu_client_secret_de_spotify"
AUDIO_PATH = "ruta_al_archivo_de_audio.mp3"  # Cambia esto según tu archivo de audio
TRANSCRIPT_PATH = "ruta_al_archivo_de_transcripcion.srt" # Cambia esto según tu archivo srt
MAX_LENGTH = 4000  # Longitud máxima del mensaje de Telegram
MAX_SEARCH_RESULTS = 3  # Número máximo de resultados de búsqueda a mostrar
```

## Ejecución

1. Ejecuta el análisis de un podcast: Asegúrate de que el archivo de audio esté configurado en config.py y ejecuta el script principal:

```bash
python main.py
```

2. Resultados esperados:

Clasificación temática: Género principal, subgéneros, público objetivo y nivel de complejidad.
Resumen ejecutivo: Un resumen breve con los puntos clave del episodio.
Análisis por segmentos: División del contenido en segmentos con frases temáticas y subtemas.
Recomendaciones: Podcasts similares encontrados en Spotify.