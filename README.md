# System-for-classifying-podcasts-into-themes-using-large-language-models
# 🎙 Podcast Classifier Bot  
Un sistema para la **clasificación automática de podcasts** mediante el uso de **modelos grandes de lenguaje (LLMs)**, desplegado en un **bot de Telegram**.

## 🚀 Funcionalidades
- **Transcripción de audio:** Convierte archivos de podcast en texto utilizando [OpenAI Whisper](https://github.com/openai/whisper).
- **Clasificación automática:** Clasifica el contenido del podcast en temáticas y genera resúmenes usando **OpenAI GPT**.
- **Interfaz de usuario:** Consulta información sobre los podcasts a través de un **bot de Telegram**.

---

## 🛠️ Tecnologías utilizadas
- **Python** (backend y lógica del bot)
- **OpenAI Whisper** (transcripción de audio)
- **OpenAI GPT** (análisis semántico)
- **python-telegram-bot** (interacción con Telegram)
- **FastAPI (opcional)** (para futuras integraciones)
- **SQLite/PostgreSQL (opcional)** (almacenamiento de datos)

---

## 📦 Estructura del proyecto
```plaintext
podcast-classifier-bot/
├── bot/                      # Lógica del bot de Telegram
│   ├── bot.py                 # Código principal del bot
│   └── handlers.py            # Manejadores de eventos del bot
├── models/                    # Modelos de transcripción y clasificación
│   ├── transcriber.py         # Transcripción del audio
│   └── classifier.py          # Clasificación del contenido
├── data/                      # Archivos de entrada/salida
├── api/                       # API REST (opcional)
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación del proyecto
├── config.py                  # Configuración de variables de entorno
└── main.py                    # Punto de entrada del sistema

libraries: 
instalar todas pip install -r requirements.txt

execute:
python main.py