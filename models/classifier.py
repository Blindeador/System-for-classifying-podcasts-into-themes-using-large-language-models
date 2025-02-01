import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def classify_content(text: str) -> str:
    prompt = f"Clasifica el siguiente contenido en temáticas y resume brevemente: {text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']