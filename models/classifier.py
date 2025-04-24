""" Gpt Open AI """
# import openai
# from config import OPENAI_API_KEY

# openai.api_key = OPENAI_API_KEY

# def classify_content(text: str) -> str:
        # prompt = f"Eres un experto en análisis de contenido de podcasts. Te proporcionaré la transcripción de un episodio completo. Tu tarea es:

        #         1. CLASIFICACIÓN:
        #         - Identifica el género principal y subgéneros del podcast
        #         - Determina el público objetivo
        #         - Establece un nivel de complejidad (básico, intermedio, avanzado)

        #         2. RESUMEN EJECUTIVO:
        #         - Crea un resumen conciso (máximo 150 palabras) que capture la esencia del episodio
        #         - Incluye los 3-5 puntos clave discutidos

        #         3. ANÁLISIS POR SEGMENTOS:
        #         - Divide el contenido en segmentos de 10 minutos
        #         - Para cada segmento, proporciona:
        #             * Una frase temática que capture la idea principal (máximo 15 palabras)
        #             * Los subtemas o puntos importantes mencionados

        #         4. RECOMENDACIONES:
        #         - Basándote en la temática y/o autor, sugiere 3-5 podcasts similares que podrían interesar al oyente
        #         - Para cada recomendación incluye:
        #             * Título del podcast
        #             * Breve descripción (1-2 frases)
        #             * Por qué es relevante para quien escuchó este episodio

        #         La transcripción es la siguiente:{text}"
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         print(response)
#         return response['choices'][0]['message']['content']
#     except openai.error.RateLimitError as e:
#         print(f"Rate limit exceeded: {e}")
#         return "Error: Se ha excedido el límite de uso de la API de OpenAI. Por favor, verifica tu plan y detalles de facturación."
#     except openai.error.OpenAIError as e:
#         print(f"OpenAI API error: {e}")
#         return "Error: Ocurrió un problema con la API de OpenAI."

""" Modelo preentrenado de Hugging Face para clasificación y resumen """
# from transformers import pipeline

# def classify_content(text: str) -> str:
#     classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#     candidate_labels = ["technology", "sports", "politics", "business", "entertainment", "health"]
#     result = classifier(text, candidate_labels)
    
#     # Extraer la etiqueta con la puntuación más alta
#     highest_score_index = result['scores'].index(max(result['scores']))
#     highest_score_label = result['labels'][highest_score_index]
    
#     return highest_score_label

# def summarize_content(text: str) -> str:
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
#     # Truncar el texto de entrada si es demasiado largo
#     max_input_length = 1024  # Longitud máxima permitida por el modelo
#     truncated_text = text[:max_input_length]
    
#     summary = summarizer(truncated_text, max_length=130, min_length=30, do_sample=False)
#     return summary[0]['summary_text']

# # # Leer el archivo .srt
# # with open('data/transcription.srt', 'r', encoding='utf-8') as file:
# #     transcription = file.read()

# # # Clasificar el contenido del archivo .srt
# # classification_result = classify_content(transcription)
# # print("Clasificación:", classification_result)

# # # Resumir el contenido del archivo .srt
# # summary_result = summarize_content(transcription)
# # print("Resumen:", summary_result)

""" Modelo GRATUITO lLAMA (META)"""

# import requests
# import json

# def classify_content(text: str) -> str:
#     prompt = f"""Eres un experto en análisis de contenido de podcasts. Te proporcionaré la transcripción de un episodio completo. Tu tarea es:

#             1. CLASIFICACIÓN:
#             - Identifica el género principal y subgéneros del podcast
#             - Determina el público objetivo
#             - Establece un nivel de complejidad (básico, intermedio, avanzado)

#             2. RESUMEN EJECUTIVO:
#             - Crea un resumen conciso (máximo 150 palabras) que capture la esencia del episodio
#             - Incluye los 3-5 puntos clave discutidos

#             3. ANÁLISIS POR SEGMENTOS:
#             - Divide el contenido en segmentos de 10 minutos
#             - Para cada segmento, proporciona:
#                 * Una frase temática que capture la idea principal (máximo 15 palabras)
#                 * Los subtemas o puntos importantes mencionados

#             4. RECOMENDACIONES:
#             - Basándote en la temática y/o autor, sugiere 3-5 podcasts similares que podrían interesar al oyente
#             - Para cada recomendación incluye:
#                 * Título del podcast
#                 * Breve descripción (1-2 frases)
#                 * Por qué es relevante para quien escuchó este episodio

#             La transcripción es la siguiente:{text}"""

#     headers = {'Content-Type': 'application/json'}
#     data = json.dumps({"text": prompt})

#     response = requests.post('https://api.meta.ai/v1/chat', headers=headers, data=data)

#     if response.status_code == 200:
#         return response.json()['response']
#     else:
#         return f"Error: {response.status_code}"


""" Modelo GRATUITO llama-4-maverick """

import requests


def classify_content(text: str) -> str:
    # prompt = f"""Eres un experto en análisis de contenido de podcasts. Te proporcionaré la transcripción de un episodio completo...
    # La transcripción es la siguiente:\n{text}
    # """
    prompt = f"""Eres un experto en análisis de contenido de podcasts. Te proporcionaré la transcripción de un episodio completo. Tu tarea es:

    1. CLASIFICACIÓN:
    - Identifica el género principal y subgéneros del podcast
    - Determina el público objetivo
    - Establece un nivel de complejidad (básico, intermedio, avanzado)
    Usa este formato exacto para la sección: **CLASIFICACIÓN**

    2. RESUMEN EJECUTIVO:
    - Crea un resumen conciso (máximo 150 palabras) que capture la esencia del episodio
    - Incluye los 3-5 puntos clave discutidos
    Usa este formato exacto para la sección: **RESUMEN EJECUTIVO**

    3. ANÁLISIS POR SEGMENTOS:
    - Divide el contenido en segmentos de 10 minutos
    - Para cada segmento, proporciona:
        * Una frase temática que capture la idea principal (máximo 15 palabras)
        * Los subtemas o puntos importantes mencionados
    Usa este formato exacto para la sección: **ANÁLISIS POR SEGMENTOS**

    4. RECOMENDACIONES:
    - Basándote en la temática y/o autor, sugiere 3-5 podcasts similares que podrían interesar al oyente
    - Para cada recomendación incluye:
        * Título del podcast
        * Breve descripción (1-2 frases)
        * Por qué es relevante para quien escuchó este episodio
    Usa este formato exacto para la sección: **RECOMENDACIONES**

    MUY IMPORTANTE: Mantén exactamente el formato de los encabezados de sección como se muestra arriba.
                    Ademas, sé conciso y asegúrate de que cada sección tenga menos de 4000 caracteres en total.

    La transcripción es la siguiente:{text}"""

    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }

    body = {
        "model": "meta-llama/llama-4-maverick:free",  
        # "model": "shisa-ai/shisa-v2-llama3.3-70b:free",
        # "model": "microsoft/mai-ds-r1:free",
        "messages": [
            {"role": "system", "content": "Eres un experto analista de contenido de audio y medios."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=body, headers=headers)
    response_json = response.json()

    # Debug: mostrar respuesta completa
    print("DEBUG JSON Response:")
    print(response_json)

    if 'choices' in response_json:
        return response_json['choices'][0]['message']['content']
    elif 'error' in response_json:
        return f"Error en la API: {response_json['error']['message']}"
    else:
        return "Error desconocido: no se recibió una respuesta válida."
