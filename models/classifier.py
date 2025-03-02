import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# def classify_content(text: str) -> str:
#     prompt = f"Clasifica el siguiente contenido en temáticas y resume brevemente: {text}"
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
    
from transformers import pipeline

def classify_content(text: str) -> str:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    candidate_labels = ["technology", "sports", "politics", "business", "entertainment", "health"]
    result = classifier(text, candidate_labels)
    
    # Extraer la etiqueta con la puntuación más alta
    highest_score_index = result['scores'].index(max(result['scores']))
    highest_score_label = result['labels'][highest_score_index]
    
    return highest_score_label

def summarize_content(text: str) -> str:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Truncar el texto de entrada si es demasiado largo
    max_input_length = 1024  # Longitud máxima permitida por el modelo
    truncated_text = text[:max_input_length]
    
    summary = summarizer(truncated_text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

# # Leer el archivo .srt
# with open('data/transcription.srt', 'r', encoding='utf-8') as file:
#     transcription = file.read()

# # Clasificar el contenido del archivo .srt
# classification_result = classify_content(transcription)
# print("Clasificación:", classification_result)

# # Resumir el contenido del archivo .srt
# summary_result = summarize_content(transcription)
# print("Resumen:", summary_result)