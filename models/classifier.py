import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def classify_content(text: str) -> str:
    prompt = f"Clasifica el siguiente contenido en temáticas y resume brevemente: {text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except openai.error.RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        return "Error: Se ha excedido el límite de uso de la API de OpenAI. Por favor, verifica tu plan y detalles de facturación."
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Error: Ocurrió un problema con la API de OpenAI."