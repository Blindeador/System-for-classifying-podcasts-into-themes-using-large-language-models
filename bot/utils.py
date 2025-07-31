"""
Funciones de utilidad para el bot de análisis de podcasts.
"""

import re
import requests
import logging
from bs4 import BeautifulSoup
from config import MAX_LENGTH

# Configuración de logging
logger = logging.getLogger(__name__)

# Diccionario global para almacenar datos por usuario
# En una implementación más robusta, esto debería ser una base de datos
user_data = {}

#  Obtener token de Spotify
def get_spotify_token(client_id, client_secret):
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(client_id, client_secret)
    )
    return auth_response.json().get('access_token')

# Buscar podcasts en Spotify
def search_spotify_podcasts(query, token):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'show', 'limit': 5}
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    return response.json().get('shows', {}).get('items', [])

# def get_spotify_metadata(spotify_url):
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }
#     response = requests.get(spotify_url, headers=headers)
#     if response.status_code != 200:
#         return None, None

#     html = BeautifulSoup(response.text, 'html.parser')
#     title_tag = html.find("meta", {"property": "og:title"})
#     podcast_tag = html.find("meta", {"property": "og:description"})

#     if title_tag and podcast_tag:
#         title = title_tag["content"]
#         podcast = podcast_tag["content"].split("·")[0].strip()
#         return title, podcast
#     return None, None

def search_spotify_episodes(query, token):
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'episode', 'limit': 5}
    search_response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

    if search_response.status_code != 200:
        return []

    raw_episodes = search_response.json().get('episodes', {}).get('items', [])
    episodes = []

    for ep in raw_episodes:
        href = ep.get('href')
        if not href:
            continue

        # Segunda petición para obtener datos completos del episodio
        full_response = requests.get(href, headers=headers)
        if full_response.status_code != 200:
            continue

        full_data = full_response.json()

        episodes.append({
            'episode_title': full_data.get('name'),
            'podcast_name': full_data.get('show', {}).get('name'),
            'publisher': full_data.get('show', {}).get('publisher'),
            'spotify_url': full_data.get('external_urls', {}).get('spotify'),
            'duration_ms': full_data.get('duration_ms'),
            'audio_preview_url': full_data.get('audio_preview_url'),
        })

    return episodes

def is_url(text: str) -> bool:
    """
    Verifica si el texto es una URL.
    
    Args:
        text (str): Texto a verificar
        
    Returns:
        bool: True si es una URL, False en caso contrario
    """
    url_pattern = r'^https?://'
    return re.match(url_pattern, text.strip()) is not None

def extract_section(full_text: str, section_number: int) -> str:
    """
    Extrae una sección específica del texto completo según encabezados.
    
    Args:
        full_text (str): Texto completo que contiene múltiples secciones
        section_number (int): Número de sección a extraer (1-based)
        
    Returns:
        str: Contenido de la sección solicitada
    """
    # Patrones de encabezado para las secciones
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
    for i, (num, start) in enumerate(sections):
        if num == section_number:
            # Calcular el final (inicio de la siguiente sección o fin del texto)
            end = sections[i+1][1] if i < len(sections)-1 else len(full_text)
            return full_text[start:end].strip()
    
    # Si no se encontró la sección
    found_sections = [f"Sección {num} en posición {pos}" for num, pos in sections]
    logger.warning(f"No se encontró la sección {section_number}. Secciones encontradas: {found_sections}")
    return f"No se encontró la sección {section_number}. Por favor, inténtalo de nuevo con otro contenido."

def format_long_message(text: str) -> str:
    """
    Formatea un mensaje largo para cumplir con los límites de Telegram.
    
    Args:
        text (str): Texto posiblemente largo
        
    Returns:
        str: Texto acortado si excede el límite
    """
    SUFFIX = "\n\n[...] (contenido recortado)"
    
    if len(text) > MAX_LENGTH:
        # Restar la longitud del sufijo para que el total sea exactamente MAX_LENGTH
        available_length = MAX_LENGTH - len(SUFFIX)
        return text[:available_length] + SUFFIX
    
    return text

def store_user_data(user_id, data):
    """
    Almacena datos asociados a un usuario.
    
    Args:
        user_id: Identificador único del usuario
        data: Datos a almacenar
    """
    user_data[user_id] = data
    
def get_user_data(user_id):
    """
    Recupera datos asociados a un usuario.
    
    Args:
        user_id: Identificador único del usuario
        
    Returns:
        Los datos almacenados o None si no existen
    """
    return user_data.get(user_id)
    
def clear_user_data(user_id):
    """
    Elimina los datos asociados a un usuario.
    
    Args:
        user_id: Identificador único del usuario
    """
    if user_id in user_data:
        del user_data[user_id]