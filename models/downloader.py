import aiohttp
import yt_dlp
import aiofiles
import os
from pydub import AudioSegment

# async def download_audio(url: str, save_path: str) -> bool:
#     """
#     Descarga un archivo de audio desde una URL en streaming y lo guarda localmente.
#     """
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url) as response:
#                 if response.status != 200:
#                     print(f"Error al descargar el audio: {response.status}")
#                     return False

#                 # Guardar en el disco en modo streaming
#                 async with aiofiles.open(save_path, 'wb') as f:
#                     async for chunk in response.content.iter_any():
#                         await f.write(chunk)

#         print(f"Archivo descargado en: {save_path}")
#         return True
#     except Exception as e:
#         print(f"Error en la descarga: {e}")
#         return False
    


# def download_audio_from_url(url: str, output_path: str) -> bool:
#     """
#     Descarga el audio de una URL (YouTube, Spotify, etc.) y lo guarda en formato WAV.
#     """
#     try:
#         # Opciones de yt-dlp
#         ydl_opts = {
#             "format": "bestaudio/best",
#             "outtmpl": output_path.replace(".wav", ".%(ext)s"),  # Guarda en el formato original
#             "postprocessors": [
#                 {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
#             ],
#         }

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             ydl.download([url])  # Descargar el archivo

#         # Buscar el archivo descargado
#         base_name = output_path.replace(".wav", "")
#         downloaded_file = None

#         for ext in ["mp3", "m4a", "webm", "opus"]:
#             if os.path.exists(f"{base_name}.{ext}"):
#                 downloaded_file = f"{base_name}.{ext}"
#                 break

#         if not downloaded_file:
#             print("No se encontró el archivo descargado.")
#             return False

#         # Convertir a WAV
#         audio = AudioSegment.from_file(downloaded_file)
#         audio.export(output_path, format="wav")
#         os.remove(downloaded_file)  # Eliminar archivo original

#         print(f"Audio guardado en: {output_path}")
#         return True

#     except Exception as e:
#         print(f"Error en la descarga: {e}")
#         return False