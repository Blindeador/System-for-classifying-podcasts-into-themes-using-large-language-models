import asyncio
import os
import yt_dlp
import mimetypes
from telegram import Update
from telegram.ext import ContextTypes
from models.transcriber import transcribe_audio_to_srt
from models.classifier import classify_content, summarize_content
from telegram.error import BadRequest

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("¡Hola! Envíame la URL del podcast para analizarlo.")


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Maneja la entrada de una URL de podcast, descarga el audio y lo transcribe.
    """
    print("Manejando audio...")
    podcast_url = update.message.text.strip()
    file_path = "data/audio.wav"  # Siempre usar el mismo nombre para el archivo de salida

    await update.message.reply_text("Descargando el audio...")
    success = await download_audio_from_url(podcast_url, file_path)

    if not success:
        await update.message.reply_text("Error al descargar el archivo. Asegúrate de que la URL es correcta.")
        return

    await update.message.reply_text("Audio descargado. Transcribiendo...")
    try:
        # Transcribir el audio
        transcription = transcribe_audio_to_srt(file_path, output_srt_path='data/transcription.srt')

        with open('data/transcription.srt', 'r', encoding='utf-8') as file:
            transcription = file.read()

        classification = classify_content(transcription)
        resumen = summarize_content(transcription)

        await update.message.reply_text(f"Transcripción (resumida): {resumen[:400]}...")  # Evitar mensajes largos
        await update.message.reply_text(f"Clasificación: {classification}")

    except Exception as e:
        print(f"Error en el proceso: {e}")
        await update.message.reply_text("Hubo un error procesando el audio.")


async def download_audio_from_url(url: str, output_path: str) -> bool:
    """
    Descarga el audio de una URL usando yt-dlp y lo convierte a WAV.
    """
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path.replace(".wav", ".%(ext)s"),
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }

        # Ejecutar yt-dlp en un hilo separado para no bloquear el bot
        await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).download([url]))

        # Buscar el archivo descargado
        base_name = output_path.replace(".wav", "")
        downloaded_file = None

        for ext in ["mp3", "m4a", "webm", "opus"]:
            if os.path.exists(f"{base_name}.{ext}"):
                downloaded_file = f"{base_name}.{ext}"
                break

        if not downloaded_file:
            print("No se encontró el archivo descargado.")
            return False

        # Verificar si el archivo descargado es válido
        mime_type, _ = mimetypes.guess_type(downloaded_file)
        if mime_type is None or "audio" not in mime_type:
            print(f"El archivo descargado no es un archivo de audio válido: {downloaded_file}")
            return False

        # Sobrescribir el archivo existente con el nombre 'audio.wav'
        if os.path.exists(output_path):
            os.remove(output_path)  # Eliminar si existe un archivo con el mismo nombre

        # Renombrar el archivo descargado a 'audio.wav'
        os.rename(downloaded_file, output_path)

        print(f"Audio guardado en: {output_path}")
        return True

    except Exception as e:
        print(f"Error en la descarga: {e}")
        return False