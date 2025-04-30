"""
Funciones de utilidad para el bot de análisis de podcasts.
"""

import re
import logging
from config import MAX_LENGTH

# Configuración de logging
logger = logging.getLogger(__name__)

# Diccionario global para almacenar datos por usuario
# En una implementación más robusta, esto debería ser una base de datos
user_data = {}

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