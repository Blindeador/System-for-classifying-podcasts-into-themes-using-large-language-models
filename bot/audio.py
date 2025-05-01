"""
Módulo para el procesamiento de audio de podcasts.
"""

import os
import asyncio
import mimetypes
import logging
import yt_dlp
from config import AUDIO_PATH, TRANSCRIPT_PATH
from bot.youtube import get_spotify_metadata
from models.transcriber import transcribe_audio_to_srt
from models.classifier import classify_content
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Configuración de logging
logger = logging.getLogger(__name__)

async def download_audio_from_url(url: str, output_path: str = AUDIO_PATH) -> bool:
    """
    Descarga el audio de una URL usando yt-dlp y lo convierte a formato apropiado.
    
    Args:
        url (str): URL del audio a descargar
        output_path (str): Ruta donde guardar el archivo de audio
        
    Returns:
        bool: True si la descarga fue exitosa, False en caso contrario
    """
    try:
        # Asegurar que existe el directorio
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        base_name = output_path.replace(".wav", "")
        
        def attempt_download(download_url):
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": base_name + ".%(ext)s",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
                "quiet": True,
            }
            yt_dlp.YoutubeDL(ydl_opts).download([download_url])

        # Primer intento: descargar desde la URL original
        try:
            await asyncio.to_thread(lambda: attempt_download(url)) # Ejecutar yt-dlp en un hilo separado para no bloquear
        except Exception as e:
            logger.warning(f"Descarga desde URL original falló: {e}")
            # Fallback a YouTube si es un enlace de Spotify
            if "spotify.com" in url:
                try:
                    title, podcast = get_spotify_metadata(url)
                    if not title:
                        return False
                    query = f"{title} {podcast}"
                    yt_url = f"ytsearch1:{query}"
                    
                    if not yt_url:
                        return False
                    logger.info(f"URL alternativa encontrada en YouTube: {yt_url}")
                    await asyncio.to_thread(lambda: attempt_download(yt_url))
                except Exception as inner_e:
                    logger.error(f"Fallo también el intento desde YouTube: {inner_e}")
                    return False
            else:
                return False
            
        # Buscar el archivo descargado
        downloaded_file = None

        for ext in ["mp3", "m4a", "webm", "opus"]:
            if os.path.exists(f"{base_name}.{ext}"):
                downloaded_file = f"{base_name}.{ext}"
                break

        if not downloaded_file:
            logger.error(f"No se encontró el archivo descargado para {url}")
            return False

        # Verificar si el archivo descargado es válido
        mime_type, _ = mimetypes.guess_type(downloaded_file)
        if mime_type is None or "audio" not in mime_type:
            logger.error(f"El archivo descargado no es un archivo de audio válido: {downloaded_file}")
            return False

        # Sobrescribir el archivo existente
        if os.path.exists(output_path):
            os.remove(output_path)

        # Renombrar el archivo a formato WAV para procesamiento
        os.rename(downloaded_file, output_path)
        logger.info(f"Audio guardado en: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error en la descarga: {e}", exc_info=True)
        return False

def transcribe_audio(audio_path: str = AUDIO_PATH, output_path: str = TRANSCRIPT_PATH) -> str:
    """
    Transcribe un archivo de audio a texto y lo guarda en formato SRT.
    
    Args:
        audio_path (str): Ruta al archivo de audio
        output_path (str): Ruta donde guardar la transcripción
        
    Returns:
        str: Texto de la transcripción
    """
    try:
        # Transcribir el audio
        transcribe_audio_to_srt(audio_path, output_srt_path=output_path)
        
        # Leer la transcripción generada
        with open(output_path, 'r', encoding='utf-8') as file:
            transcription = file.read()
            
        logger.info(f"Transcripción generada en {output_path}")
        return transcription
        
    except Exception as e:
        logger.error(f"Error en la transcripción: {e}", exc_info=True)
        raise

def analyze_content(transcription: str):
    """
    Analiza el contenido de la transcripción para clasificarlo.
    
    Args:
        transcription (str): Texto de la transcripción
        
    Returns:
        str: Resultado del análisis y clasificación
    """
    try:
        # Clasificar contenido
        classification = classify_content(transcription, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        logger.info("Análisis de contenido completado")
        return classification
        
    except Exception as e:
        logger.error(f"Error en el análisis: {e}", exc_info=True)
        raise