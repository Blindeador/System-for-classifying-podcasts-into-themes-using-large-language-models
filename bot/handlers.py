from telegram import Update
from telegram.ext import CallbackContext
from models.transcriber import transcribe_audio
from models.classifier import classify_content

def start(update: Update, context: CallbackContext):
    update.message.reply_text("¡Hola! Envíame un archivo de audio para analizar.")

def handle_audio(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file_path = 'data/audio.ogg'
    file.download(file_path)

    # Transcripción y clasificación
    transcription = transcribe_audio(file_path)
    classification = classify_content(transcription)

    update.message.reply_text(f"Transcripción (resumida): {transcription[:100]}...")
    update.message.reply_text(f"Clasificación: {classification}")