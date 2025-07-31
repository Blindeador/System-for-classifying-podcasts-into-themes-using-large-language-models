from config import OPENROUTER_API_KEY, AUDIO_PATH
from bot.utils import get_spotify_token, search_spotify_podcasts
import requests
import re
from pydub import AudioSegment

audio = AudioSegment.from_file(AUDIO_PATH)
total_duration = len(audio) / 1000  # Duración total en segundos


#  Llamada a Maverick para clasificación + resumen
def analyze_with_maverick(transcription: str) -> str:
    
    prompt = f"""Eres un experto en análisis de contenido de podcasts. Te proporcionaré la transcripción de un episodio completo. Tu tarea es:

    1. **CLASIFICACIÓN**:
    - Género principal: [Especificar la temática principal del podcast solo una entre(humor y entretenimiento, 
    música, cine y TV, cultura y sociedad, historia y humanidades, noticias y política, misterio, deportes,
    ciencia y medicina, salud y bienestar, empresa, tecnología, educación, finanzas y arte)Si hay dos o más géneros con porcentajes de selección similares, prioriza el género más específico sobre el más general. Por ejemplo, si "historia y humanidades" y "cultura y sociedad" están empatados, elige "historia y humanidades". Aplica este criterio especialmente cuando la diferencia entre los porcentajes sea menor al 5%.]
    - Enumera subgéneros específicos relacionados con el contenido.
    - Determina el público objetivo.
    - Establece un nivel de complejidad (básico, intermedio, avanzado).
    Usa este formato exacto para la sección: **CLASIFICACIÓN**

    2. **RESUMEN EJECUTIVO**:
    - Crea un resumen conciso (máximo 150 palabras) que capture la esencia del episodio.
    - Incluye los 3-5 puntos clave discutidos.
    Usa este formato exacto para la sección: **RESUMEN EJECUTIVO**

    3. **ANÁLISIS POR SEGMENTOS**:
    - Divide el episodio en un máximo de 10 segmentos equilibrados.
    - Para cada segmento, proporciona:
      * Una frase temática que capture la idea principal (máximo 15 palabras).
      * Los subtemas o puntos importantes mencionados.
    Usa este formato exacto para la sección: **ANÁLISIS POR SEGMENTOS**

    4. **RECOMENDACIONES**:
    - Esta sección se completará más tarde automáticamente.
    - Simplemente escribe "**RECOMENDACIONES**" al final del documento.

    MUY IMPORTANTE:
    - Mantén exactamente el formato de los encabezados de sección como se muestra arriba.
    - Sé conciso y asegúrate de que cada sección tenga menos de 4000 caracteres en total (incluyendo etiquetas).
    - En caso de que la transcripción sea muy larga, prioriza la claridad y la cobertura general frente al detalle excesivo.

    La transcripción es la siguiente:
    {transcription}
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "meta-llama/llama-4-maverick:free",
        "messages": [
            {"role": "system", "content": """Actúa como un experto analista de contenido de audio 
             con experiencia en clasificación temática, resúmenes ejecutivos y segmentación estructurada de medios.
             Prioriza la claridad, síntesis y adecuación al formato requerido.
             """},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
    return response.json()['choices'][0]['message']['content']

# Extraer término ideal para buscar en Spotify
def extract_query_for_spotify(analysis_text: str) -> str:
    prompt = f"""A partir del siguiente análisis de contenido de un pódcast, indica el mejor término o frase de búsqueda para encontrar podcasts similares en Spotify. Solo responde con la frase, sin explicaciones.

    Análisis:
    {analysis_text}
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "meta-llama/llama-4-maverick:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
    return response.json()['choices'][0]['message']['content'].strip()

# Pedirle a la IA que genere recomendaciones a partir de resultados reales de Spotify
def format_recommendations_with_maverick(query: str, spotify_results) -> str:
    spotify_summaries = "\n".join(
        f"- {s['name']}: {s['description'][:200]}" for s in spotify_results
    )

    prompt = f"""Aquí tienes una lista de podcasts encontrados en Spotify sobre "{query}":

{spotify_summaries}

Redacta una sección de **RECOMENDACIONES** siguiendo explicitamente este formato:

- **Título del podcast**
  Descripción (1-2 frases)
  Por qué es relevante para quien escuchó este episodio.
"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "meta-llama/llama-4-maverick:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
     # Log de la respuesta
    print(f"Respuesta de la API: {response.status_code} - {response.text}")

    if response.status_code != 200:
        print(f"Error en la API: {response.status_code} - {response.text}")
        raise ValueError("Error en la API al generar recomendaciones.")

    response_json = response.json()
    if 'choices' not in response_json:
        print(f"La respuesta no contiene 'choices': {response_json}")
        raise KeyError("'choices' no está presente en la respuesta de la API.")

    return response.json()['choices'][0]['message']['content'].strip()

#  Función principal final
def classify_content(transcription: str, client_id: str, client_secret: str) -> str:
    # Análisis inicial
    analysis = analyze_with_maverick(transcription)
    print("\n Análisis inicial generado.")

    # Obtener término de búsqueda
    query = extract_query_for_spotify(analysis)
    print(f"\n Término de búsqueda Spotify: '{query}'")

    # Paso C: buscar podcasts en Spotify
    token = get_spotify_token(client_id, client_secret)
    spotify_results = search_spotify_podcasts(query, token)

    # Generar recomendaciones enriquecidas
    recommendations = format_recommendations_with_maverick(query, spotify_results)
    print("\n Recomendaciones enriquecidas generadas.")

    # Insertar recomendaciones en el análisis
    final_result = re.sub(
        r"\*\*RECOMENDACIONES\*\*", recommendations, analysis, flags=re.DOTALL
    )

    print("\n✅ RESULTADO FINAL LISTO")
    return final_result
