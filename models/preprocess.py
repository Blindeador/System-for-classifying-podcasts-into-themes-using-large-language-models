import re
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

def preprocess_podcast_transcript(
    srt_path: str, 
    language: str = 'es', 
    remove_timestamps: bool = True,
    use_key_features: bool = True
) -> str:
    """
    Preprocesa la transcripción de un podcast con soporte multilingüe.
    
    Args:
        srt_path (str): Ruta al archivo SRT
        language (str): Código de idioma (defecto 'es')
        remove_timestamps (bool): Eliminar marcadores de tiempo (defecto True)
    
    Returns:
        str: Texto preprocesado
    """
    try:
        # Diccionario de modelos de spaCy por idioma
        spacy_models = {
            'es': 'es_core_news_sm',
            'ca': 'ca_core_news_sm',
            'en': 'en_core_web_sm',
            'fr': 'fr_core_news_sm',
            'de': 'de_core_news_sm',
            'it': 'it_core_news_sm',
            'pt': 'pt_core_news_sm'
            # Añadir más modelos según necesidad
        }
        
        # Seleccionar modelo de spaCy
        model_name = spacy_models.get(language, 'en_core_web_sm')
        
        try:
            nlp = spacy.load(model_name)
        except OSError:
            raise RuntimeError(f"Modelo {model_name} no encontrado. Instálalo con: python -m spacy download {model_name}")
        
        # Leer el contenido del archivo SRT
        with open(srt_path, 'r', encoding='utf-8') as file:
            transcript = file.read()
        
        # Opcional: Eliminar marcadores de tiempo SRT
        if remove_timestamps:
            transcript = re.sub(r'\d+:\d+:\d+ --> \d+:\d+:\d+\n', '', transcript)
        
        # Convertir a minúsculas
        transcript = transcript.lower()
        
        # Procesar texto con spaCy
        doc = nlp(transcript)
        
        # Filtrar tokens relevantes
        # Los criterios pueden ajustarse según el idioma
        tokens = [
            token.lemma_ for token in doc 
            if (not token.is_stop and 
                token.is_alpha and 
                len(token.lemma_) > 1)
        ]
        
        # Unir tokens preprocesados
        processed_text = ' '.join(tokens)

        # 🚀 Extraer características clave
        if use_key_features:
            key_features = extract_key_features(processed_text, language, max_features=50)
            key_terms = set(word for word, _ in key_features)
            # 🔥 Filtrar el texto usando solo palabras clave
            processed_text = ' '.join([word for word in tokens if word in key_terms])
        
        return processed_text
    
    except Exception as e:
        print(f"Error en preprocesamiento: {e}")
        return ""

def extract_key_features(processed_text, language, max_features=20):
    try:
        # Cargar el modelo de spaCy correspondiente al idioma
        spacy_models = {
            'es': 'es_core_news_sm',
            'ca': 'ca_core_news_sm',
            'en': 'en_core_web_sm',
            'fr': 'fr_core_news_sm',
            'de': 'de_core_news_sm',
            'it': 'it_core_news_sm',
            'pt': 'pt_core_news_sm'
        }
        
        model_name = spacy_models.get(language, 'en_core_web_sm')

        try:
            nlp = spacy.load(model_name)
        except OSError:
            print(f"Modelo {model_name} no encontrado. Usando inglés por defecto.")
            nlp = spacy.load('en_core_web_sm')

        # Procesar texto con spaCy para eliminar stopwords
        doc = nlp(processed_text)
        filtered_text = " ".join([token.text for token in doc if not token.is_stop])

        # Vectorización TF-IDF sin stopwords
        vectorizer = TfidfVectorizer(max_features=max_features)
        tfidf_matrix = vectorizer.fit_transform([filtered_text])

        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]

        # Ordenar características por puntuación
        top_features = sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)[:max_features]

        return top_features

    except Exception as e:
        print(f"Error en extracción de características: {e}")
        return []
# Función para recuperar el idioma
def get_detected_language(language_file='data/language_info.txt'):
    try:
        with open(language_file, 'r', encoding='utf-8') as lang_file:
            lines = lang_file.readlines()
            language = lines[0].strip()
            probability = float(lines[1].strip()) if len(lines) > 1 else None
        return language, probability
    except Exception as e:
        print(f"Error al leer idioma: {e}")
        return None, None

# import re
# import spacy
# import json
# import os
# from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, ENGLISH_STOP_WORDS
# from sklearn.decomposition import LatentDirichletAllocation
# from symspellpy import SymSpell

# def preprocess_podcast_transcript(srt_path: str, language: str = 'es') -> dict:
#     try:
#         spacy_models = {'es': 'es_core_news_sm', 'en': 'en_core_web_sm'}
#         model_name = spacy_models.get(language, 'en_core_web_sm')
        
#         try:
#             nlp = spacy.load(model_name)
#         except OSError:
#             import subprocess
#             subprocess.run(f"python -m spacy download {model_name}", shell=True)
#             nlp = spacy.load(model_name)
        
#         with open(srt_path, 'r', encoding='utf-8') as file:
#             transcript = file.read()
        
#         transcript = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', transcript)
#         transcript = re.sub(r'\n+', '\n', transcript).lower()
        
#         doc = nlp(transcript)
#         tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha and len(token.lemma_) > 1]
#         processed_text = ' '.join(tokens)
        
#         key_features = extract_key_features(processed_text, language)
#         topics = extract_topics(processed_text, language)
        
#         return {"processed_text": processed_text, "key_features": key_features, "topics": topics}
#     except Exception as e:
#         return {"error": str(e)}

# def extract_key_features(text, language, max_features=20):
#     try:
#         custom_stopwords = {"es": set(), "en": ENGLISH_STOP_WORDS}
#         stop_language = custom_stopwords.get(language, None)
        
#         vectorizer = TfidfVectorizer(max_features=max_features, stop_words=stop_language)
#         tfidf_matrix = vectorizer.fit_transform([text])
#         feature_names = vectorizer.get_feature_names_out()
#         tfidf_scores = tfidf_matrix.toarray()[0]
        
#         return sorted(zip(feature_names, tfidf_scores), key=lambda x: x[1], reverse=True)[:max_features]
#     except Exception as e:
#         return []

# def extract_topics(text, language, n_topics=3):
#     try:
#         custom_stopwords = {"es": set(), "en": ENGLISH_STOP_WORDS}
#         stop_language = custom_stopwords.get(language, None)
        
#         vectorizer = CountVectorizer(max_features=1000, stop_words=stop_language)
#         X = vectorizer.fit_transform([text])
        
#         actual_topics = min(n_topics, max(1, len(vectorizer.get_feature_names_out()) // 10))
#         lda = LatentDirichletAllocation(n_components=actual_topics, random_state=42)
#         lda.fit(X)
        
#         topic_terms = lda.components_.argsort()[:, -10:][:, ::-1]
#         terms = vectorizer.get_feature_names_out()
        
#         return [[terms[i] for i in topic] for topic in topic_terms]
#     except Exception as e:
#         return []

# # Función adicional para integrar con faster_whisper
# def process_transcription(audio_path, output_srt_path, language='auto'):
#     """
#     Procesa un archivo de audio usando faster_whisper y luego preprocesa la transcripción.
    
#     Args:
#         audio_path: Ruta al archivo de audio
#         output_srt_path: Ruta donde guardar el archivo SRT
#         language: Idioma para transcripción ('auto', 'en', 'es', 'fr')
    
#     Returns:
#         dict: Resultado del preprocesamiento
#     """
#     try:
#         from whisper_processing import transcribe_audio_to_srt
        
#         # Transcribir audio
#         result = transcribe_audio_to_srt(audio_path, output_srt_path)
        
#         # Usar el idioma detectado
#         detected_language = result.get('language', 'en')
        
#         # Si se detectó catalán (ca) pero solo queremos trabajar con inglés, español o francés
#         # usar el lenguaje permitido con mayor probabilidad como ya implementaste
#         allowed_languages = {'en', 'es', 'fr'}
#         if detected_language not in allowed_languages:
#             print(f"Idioma detectado ({detected_language}) no está entre los permitidos. Usando inglés por defecto.")
#             detected_language = 'en'
        
#         # Preprocesar la transcripción
#         preprocessing_result = preprocess_podcast_transcript(
#             srt_path=output_srt_path,
#             language=detected_language,
#             remove_timestamps=True,
#             correct_errors=True,
#             detect_topics=True
#         )
        
#         return preprocessing_result
#     except Exception as e:
#         import traceback
#         print(f"Error en el proceso: {e}")
#         print(traceback.format_exc())
#         return {"error": str(e)}