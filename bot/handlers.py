import logging
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config import MAX_SEARCH_RESULTS
from bot.utils import is_url, extract_section, format_long_message, store_user_data, get_user_data, clear_user_data, search_spotify_episodes
from bot.audio import download_audio_from_url, transcribe_audio, analyze_content
from models.classifier import get_spotify_token
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Configuración de logging
logger = logging.getLogger(__name__)

# Manejadores de comandos

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start."""
    welcome_text = (
        "👋 ¡Bienvenido al Analizador de Podcasts!\n\n"
        "Puedes usar este bot de dos maneras 🤖:\n"
        "1️⃣ Envía el nombre de un podcast para buscar en Spotify\n"
        "2️⃣ Envía directamente la URL de un episodio para analizarlo\n\n"
        "¿Con qué podcast te gustaría comenzar hoy?"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /help."""
    help_text = (
        "🔍 *Cómo usar el Analizador de Podcasts*\n\n"
        "*Opciones disponibles:*\n"
        "• Envía el *nombre* de un podcast para buscarlo en Spotify\n"
        "• Envía una *URL* de un episodio para analizarlo directamente\n\n"
        "*Comandos:*\n"
        "/start - Inicia el bot\n"
        "/help - Muestra este mensaje de ayuda\n\n"
        "*Una vez analizado un podcast, podrás ver:*\n"
        "• 🎬 Resumen Ejecutivo\n"
        "• 🧩 Análisis por Segmentos\n"
        "• 💡 Recomendaciones"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Manejadores principales

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Punto de entrada unificado para manejar la entrada del usuario.
    Maneja tanto URLs directas como términos de búsqueda.
    """
    text = update.message.text.strip()
    
    try:
        if is_url(text):
            # URL directa: procesar como podcast
            await process_podcast_url(text, update, context)
        else:
            # Búsqueda por término
            await search_podcasts(text, update, context)
            
    except Exception as e:
        logger.error(f"Error al manejar la entrada: {e}", exc_info=True)
        await update.message.reply_text(
            "⚠️ Ocurrió un error inesperado. Por favor, intenta de nuevo más tarde."
        )

async def search_podcasts(query: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Busca podcasts en Spotify según un término de búsqueda."""
    await update.message.reply_text("🔍 Buscando podcasts relacionados...")
    
    try:
        token = get_spotify_token(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET)
        results = search_spotify_episodes(query, token)

        if not results:
            await update.message.reply_text("❌ No se encontraron resultados. ¿Puedes intentar con otro nombre?")
            return
        
        # Guardar resultados temporalmente por usuario
        context.user_data["spotify_results"] = results

        # Mostrar nombre del episodio y podcast
        keyboard = [
            [InlineKeyboardButton(
                f"{item.get('episode_title', 'Sin título')} – {item.get('podcast_name', 'Sin podcast')}",
                callback_data=f"select_{i}"
            )]
            for i, item in enumerate(results[:MAX_SEARCH_RESULTS])
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Verificar si el teclado tiene opciones
        if keyboard:
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Selecciona un podcast para analizar:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ No se encontraron episodios en los resultados.")
    
    except Exception as e:
        logger.error(f"Error en la búsqueda: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Ocurrió un error durante la búsqueda. Intenta de nuevo más tarde.")

async def process_podcast_url(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa una URL de podcast: descarga, transcribe y clasifica."""
    chat_id = update.effective_chat.id
    
    # Limpiar datos anteriores antes de procesar un nuevo podcast
    context.user_data.pop("classification", None)
    
    try:
        # Mensaje de descarga
        status_message = await context.bot.send_message(
            chat_id=chat_id, 
            text="📥 Descargando el audio..."
        )
        
        # Descargar audio
        success = await download_audio_from_url(url)
        # Fallback a YouTube si es un enlace de Spotify
        if not success and "open.spotify.com" in url:
            # Intentar obtener el nombre del podcast desde los datos guardados
            spotify_results = context.user_data.get("spotify_results", [])
            selected_index = next(
                (i for i, item in enumerate(spotify_results) if item.get("spotify_url") == url),
                None
            )

            if selected_index is not None:
                podcast_name = spotify_results[selected_index].get("episode_title")
                
                youtube_url = f"ytsearch1:{podcast_name}"

                print(f"URL alternativa encontrada en YouTube: {youtube_url}")
                
                if youtube_url:
                    success = await download_audio_from_url(youtube_url)

        if not success:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text="⚠️ No pude descargar audio ni desde Spotify ni desde YouTube. Intenta con otro podcast."
            )
            return

        # Actualizar estado a transcripción
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="Audio descargado.📝 Transcribiendo..."
        )
        
        # Transcribir audio
        transcription = transcribe_audio()
        
        # Actualizar estado a análisis
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text="🧠 Transcripción completada. Analizando contenido..."
        )
        
        # Clasificar contenido
        classification = analyze_content(transcription)
        
        # Guardar el resultado completo para este usuario
        store_user_data(chat_id, classification)
        
        # Extraer la sección de clasificación
        summary = extract_section(classification, 1)
        
        # Crear menú de opciones
        keyboard = [
            [InlineKeyboardButton("🎬 Resumen Ejecutivo", callback_data='resumen')],
            [InlineKeyboardButton("🧩 Análisis por Segmentos", callback_data='segmentos')],
            [InlineKeyboardButton("💡 Recomendaciones", callback_data='recomendaciones')],
            [InlineKeyboardButton("🎙️ Analizar nuevo podcast", callback_data='nuevo_podcast')],
            [InlineKeyboardButton("🚪 Terminar", callback_data='fin')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Enviar resultado al usuario
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"<b>🎙️ Clasificación del podcast:</b>\n\n{summary}",
            parse_mode='HTML'
        )
        
        # Enviar menú de opciones
        await context.bot.send_message(
            chat_id=chat_id,
            text="¿Qué más deseas ver?",
            reply_markup=reply_markup
        )
    
    except Exception as e:
        logger.error(f"Error en el procesamiento: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=chat_id,
            text="⚠️ Ocurrió un error durante el procesamiento. Intenta de nuevo más tarde."
        )

# Manejadores de callbacks

async def handle_podcast_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja la selección de un podcast de los resultados de búsqueda."""
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("select_"):
        return

    try:
        index = int(query.data.split("_")[1])
        results = context.user_data.get("spotify_results", [])

        if not results or index >= len(results):
            await query.edit_message_text("❌ No se pudo recuperar el episodio seleccionado.")
            return

        selected_episode = results[index]
        episode_name = selected_episode.get("episode_title", "Sin nombre")
        podcast_name = selected_episode.get("podcast_name", "Sin nombre")
        external_url = selected_episode.get("spotify_url")

        if not external_url:
            await query.edit_message_text("❌ No se pudo obtener la URL del episodio en Spotify.")
            return

        await query.edit_message_text(
            f"🔗 Episodio seleccionado: <b>{episode_name}</b>\nPodcast: <b>{podcast_name}</b>\n⏳ Procesando...",
            parse_mode='HTML'
        )
        
        # Procesar la URL del podcast seleccionado
        await process_podcast_url(external_url, update, context)

    except Exception as e:
        logger.error(f"Error al procesar la selección: {e}", exc_info=True)
        await query.edit_message_text("⚠️ Ocurrió un error. Intenta seleccionar otro podcast.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja los botones interactivos del menú."""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    result = get_user_data(chat_id)
    
    if not result and query.data != "nuevo_podcast":
        await query.edit_message_text("❌ No se encontró información. ¿Podrías enviar otra URL?")
        return
    
    # Procesar según la opción seleccionada
    if query.data == "resumen":
        text = extract_section(result, 2)
        title = "🎬 Resumen Ejecutivo"
    elif query.data == "segmentos":
        text = extract_section(result, 3)
        title = "🧩 Análisis por Segmentos"
    elif query.data == "recomendaciones":
        text = extract_section(result, 4)
        title = "💡 Recomendaciones"
    elif query.data == "nuevo_podcast":
        # Limpiar datos previos del usuario
        clear_user_data(chat_id)
        await query.edit_message_text("¡Perfecto! Envíame la URL o el nombre del nuevo podcast que quieres analizar.")
        return
    elif query.data == "fin":
        clear_user_data(chat_id)
        await query.edit_message_text("Gracias por usar el analizador de podcasts 🎧. ¡Hasta la próxima!")
        return
    else:
        text = "Opción no válida."
        title = "⚠️ Error"
    
    # Formatear el mensaje si es demasiado largo
    text = format_long_message(text)
    
    # Enviar la sección solicitada
    await query.edit_message_text(f"<b>{title}</b>\n\n{text}", parse_mode='HTML')
    
    # Mostrar botones de nuevo para seguir navegando
    keyboard = [
        [InlineKeyboardButton("🎬 Resumen Ejecutivo", callback_data='resumen')],
        [InlineKeyboardButton("🧩 Análisis por Segmentos", callback_data='segmentos')],
        [InlineKeyboardButton("💡 Recomendaciones", callback_data='recomendaciones')],
        [InlineKeyboardButton("🎙️ Analizar nuevo podcast", callback_data='nuevo_podcast')],
        [InlineKeyboardButton("🚪 Terminar", callback_data='fin')]
    ]
    await query.message.reply_text(
        "¿Deseas ver otra sección o analizar un nuevo podcast?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Función para configurar los manejadores

def setup_handlers(application):
    """Configura los manejadores para el bot."""
    # Comandos básicos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Manejar entradas de texto (URLs o términos de búsqueda)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    
    # Manejar callbacks de selección de podcasts 
    application.add_handler(CallbackQueryHandler(handle_podcast_selection, pattern=r'^select_\d+$'))
    
    # Manejar otros callbacks
    application.add_handler(CallbackQueryHandler(button_handler))
    
    return application