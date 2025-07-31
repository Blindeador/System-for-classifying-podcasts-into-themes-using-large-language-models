# System for Classifying Podcasts into Themes using Large Language Models  
# 🎙 Podcast Classifier Bot  

A system for **automatically classifying podcasts** using **Large Language Models (LLMs)**, deployed through a **Telegram bot**.

---

## 🚀 Features

- **Podcast Selection:** Based on a user query, it suggests matching podcasts using the **Spotify API**.
- **Audio Transcription:** Converts podcast audio files into text using [Faster-Whisper].
- **Automatic Classification:** Categorizes podcast content into themes, generates summaries, and performs segment-level analysis using **Llama-Maverick**.
- **Recommendations:** Suggests related podcasts using **Spotify API** and **Llama-Maverick**.
- **User Interface:** Access podcast information through a **Telegram bot**.

---

## 🛠️ Technologies Used

- **Python** – backend logic and bot core
- **Spotify API** – podcast search and recommendations
- **Faster-Whisper** – audio transcription
- **Llama-Maverick** – semantic analysis and classification
- **python-telegram-bot** – Telegram bot integration
- **FastAPI (optional)** – for future web-based services
- **SQLite/PostgreSQL (optional)** – data storage and querying

---

## 📦 Project Structure

```plaintext
podcast-classifier-bot/
├── bot/                     # Processing logic and user interaction
│   ├── audio.py             # Audio analysis functions
│   ├── handlers.py          # Handlers for data flow and bot responses
│   └── utils.py             # General utility functions
├── data/                    # Data files (transcripts, audio, etc.)
│   └── transcription.srt    # Sample transcription in SRT format
├── models/                  # Core classification and transcription logic
│   ├── classifier.py        # Classification, analysis, and recommendations
│   └── transcriber.py       # Audio transcription module
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── config.py                # Environment variable configuration
├── main.py                  # System entry point
└── .gitignore               
```

## Prerequisites
Antes de comenzar, asegúrate de tener instalado lo siguiente:

Make sure you have the following installed and available before starting:

  - 🐍 Python 3.8 or later
  
  - 📦 Pip (Python package manager)
  
  - 🔑 An account on OpenRouter for LLM API access
  
  - 🎧 Spotify API credentials (Client ID and Client Secret)

---

##  Installation
1. Clone the repository:
```bash
git clone https://github.com/tu-usuario/system-for-classifying-podcasts-into-themes-using-large-language-models.git
cd system-for-classifying-podcasts-into-themes-using-large-language-models
```
2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Configure your credentials:
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

## Running the Bot

1. Ejecuta el análisis de un podcast: Asegúrate de que el archivo de audio esté configurado en config.py y ejecuta el script principal:

```bash
python main.py
```

2. Expected Outputs:

  -🎯 Topic Classification: Detects main genre, sub-genres, target audience, and complexity.
  
  -📄 Executive Summary: Concise summary with key takeaways from the episode.
  
  -🧩 Segment Analysis: Breaks content into sections with thematic and topical labeling.
  
  -🎙 Podcast Recommendations: Recommends similar content using Spotify and LLM results.
