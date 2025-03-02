from telegram import Update
from telegram.ext import ContextTypes
from models.transcriber import transcribe_audio_to_srt
from models.classifier import classify_content, summarize_content
from telegram.error import BadRequest

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("¡Hola! Envíame un archivo de audio para analizar.")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("handle_audio called")  # Mensaje de depuración
    if update.message.audio:
        print("Audio file received")  # Mensaje de depuración
        if update.message.audio.file_size > MAX_FILE_SIZE:
            await update.message.reply_text("El archivo de audio es demasiado grande. Por favor, envía un archivo de menos de 20 MB.")
            return
        
        await update.message.reply_text("Archivo de audio recibido. Procesando...")
        
        try:
            file = await update.message.audio.get_file()
            file_path = 'data/audio.ogg'
            await file.download_to_drive(file_path)

            # Transcripción y clasificación
            transcription = transcribe_audio_to_srt(file_path, output_srt_path='data/transcription.srt')
            # Leer el archivo .srt
            with open('data/transcription.srt', 'r', encoding='utf-8') as file:
                transcription = file.read()
            classification = classify_content(transcription)
            print("Clasificación:", classification)
            resumen = summarize_content(transcription)
            print("Resumen:", resumen)

            if transcription:
                await update.message.reply_text(f"Transcripción (resumida): {resumen}...")
                await update.message.reply_text(f"Clasificación: {classification}")
            else:
                await update.message.reply_text("Error: No se pudo obtener la transcripción.")
                
        except BadRequest as e:
            print(f"Error downloading file: {e}")
            await update.message.reply_text("Hubo un error al descargar el archivo de audio.")
    else:
        print("No audio file received")  # Mensaje de depuración
        await update.message.reply_text("No se recibió un archivo de audio.")