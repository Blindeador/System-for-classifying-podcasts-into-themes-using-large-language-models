import asyncio
import os
import yt_dlp
import mimetypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.transcriber import transcribe_audio_to_srt
from models.classifier import classify_content
from models.preprocess import preprocess_podcast_transcript, extract_key_features
from telegram.error import BadRequest

MAX_LENGTH = 4000 # Longitud máxima del mensaje de Telegram
user_data = {} # Diccionario temporal para almacenar resultados por usuario

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

        # Sin idioma
        with open('data/transcription.srt', 'r', encoding='utf-8') as file:
            transcription = file.read()

        classification = classify_content(transcription)
        print(classification)
        # Guardamos el resultado completo
        user_data[update.effective_user.id] = classification
         # Mostramos solo la parte de clasificación
        seccion_1 = extract_section(classification, 1)  # Función que separa la sección que quieras

        # Enviar la clasificación al usuario
        await update.message.reply_text(f"<b>🎙️ Clasificación del podcast:</b>\n\n{seccion_1}", parse_mode='HTML')

        # Mostrar opciones
        keyboard = [
            [InlineKeyboardButton("📄 Resumen Ejecutivo", callback_data='resumen')],
            [InlineKeyboardButton("📊 Análisis por Segmentos", callback_data='segmentos')],
            [InlineKeyboardButton("💡 Recomendaciones", callback_data='recomendaciones')],
            [InlineKeyboardButton("🆕 Analizar nuevo podcast", callback_data='nuevo_podcast')],
            [InlineKeyboardButton("❌ Terminar", callback_data='fin')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("¿Qué más deseas ver?", reply_markup=reply_markup)

        # resumen = summarize_content(transcription)

        # # Con idioma
        # # Usar el idioma detectado
        # language = transcription['language']
        # language_probability = transcription['language_probability']
        
        # # Preprocesar con el idioma detectado
        # processed_text = preprocess_podcast_transcript(
        #     'data/transcription.srt',
        #     language=language,
        # )
        
        # # Extraer características
        # key_features = extract_key_features(
        #     processed_text, 
        #     language=language
        # )
        # # Imprimir características para depuración
        # print("Características principales:")
        # for feature, score in key_features:
        #     print(f"{feature}: {score}")

        # with open('data/processed_transcription.txt', 'w', encoding='utf-8') as file:
        #     file.write(processed_text)
        
        # classification = classify_content(processed_text)
        # resumen = summarize_content(processed_text)

        # await update.message.reply_text(f"Transcripción (resumida): {resumen[:400]}...")  # Evitar mensajes largos
        # await update.message.reply_text(f"Clasificación: {classification}")

        # Opcional: Enviar características clave
        # features_text = "\n".join([f"{feature}: {score:.2f}" for feature, score in key_features])
        # await update.message.reply_text(f"Características principales:\n{features_text}")

    except Exception as e:
        print(f"Error en el proceso: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error durante el procesamiento. Intenta de nuevo más tarde.")


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
    
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    result = user_data.get(user_id, "")

    if not result and query.data != "nuevo_podcast":
        await query.edit_message_text("No se encontró información. ¿Podrías enviar otra URL?")
        return

    if query.data == "resumen":
        text = extract_section(result, 2)
    elif query.data == "segmentos":
        text = extract_section(result, 3)
    elif query.data == "recomendaciones":
        text = extract_section(result, 4)
    elif query.data == "nuevo_podcast":
        # Limpiar datos previos del usuario
        user_data.pop(user_id, None)
        await query.edit_message_text("¡Perfecto! Envíame la URL del nuevo podcast que quieres analizar.")
        return
    elif query.data == "fin":
        user_data.pop(user_id, None)
        await query.edit_message_text("Gracias por usar el analizador de podcasts 🎧. ¡Hasta la próxima!")
        return
    else:
        text = "Opción no válida."

    SUFFIX = "\n\n[...] (contenido recortado)"

    if len(text) > MAX_LENGTH:
        # Restar la longitud del sufijo para que el total sea exactamente MAX_LENGTH
        available_length = MAX_LENGTH - len(SUFFIX)
        text = text[:available_length] + SUFFIX

    await query.edit_message_text(f"📌 Resultado:\n\n{text}", parse_mode='HTML')

     # Mostrar botones de nuevo para seguir navegando
    keyboard = [
        [InlineKeyboardButton("2️⃣ Resumen Ejecutivo", callback_data='resumen')],
        [InlineKeyboardButton("3️⃣ Análisis por Segmentos", callback_data='segmentos')],
        [InlineKeyboardButton("4️⃣ Recomendaciones", callback_data='recomendaciones')],
        [InlineKeyboardButton("🆕 Analizar nuevo podcast", callback_data='nuevo_podcast')],
        [InlineKeyboardButton("❌ Terminar", callback_data='fin')]
    ]
    await query.message.reply_text(
         "¿Deseas ver otra sección o analizar un nuevo podcast?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def extract_section(full_text: str, section_number: int) -> str:
    import re
    
    # Estos son los patrones de encabezado en el nuevo formato
    section_headers = [
        "**CLASIFICACIÓN**",
        "**RESUMEN EJECUTIVO**",
        "**ANÁLISIS POR SEGMENTOS**",
        "**RECOMENDACIONES**"
    ]
    
    # Buscar las posiciones de inicio de cada sección
    sections = []
    for i, header in enumerate(section_headers, 1):
        match = re.search(re.escape(header), full_text)
        if match:
            sections.append((i, match.start()))
    
    # Ordenar por posición en el texto
    sections.sort(key=lambda x: x[1])
    
    # Buscar la sección solicitada
    section_found = False
    for i, (num, start) in enumerate(sections):
        if num == section_number:
            section_found = True
            # Calcular el final (inicio de la siguiente sección o fin del texto)
            end = sections[i+1][1] if i < len(sections)-1 else len(full_text)
            return full_text[start:end].strip()
    
    if not section_found:
        # Si no se encontró la sección, mostrar lo que se encontró para diagnóstico
        found_sections = [f"Sección {num} en posición {pos}" for num, pos in sections]
        return f"No se encontró la sección {section_number}. Secciones encontradas: {found_sections}"