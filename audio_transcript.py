# import os
# import subprocess
# import json
# from pydub import AudioSegment
# import tempfile

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds_int = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path, model_size="base"):
#     """Transcribe un archivo de audio usando whisper.cpp y guarda en un archivo SRT con segmentos de 5 minutos."""
    
#     # Verifica que el archivo exista
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"El archivo {file_path} no existe")
    
#     # Ruta al ejecutable whisper.cpp (ajusta según tu instalación)
#     whisper_cpp_path = '/c/Users/casa/Desktop/Universidad/TFG/System-for-classifying-podcasts-into-themes-using-large-language-models/whisper.cpp/models/ggml-base.bin'  # Cambia esto a la ruta donde tienes el ejecutable de whisper.cpp

#     # Ruta al modelo (ajusta según tu instalación)
#     model_path = f"C:/Users/casa/Desktop/Universidad/TFG/System-for-classifying-podcasts-into-themes-using-large-language-models/whisper.cpp/models/ggml-base.bin"  # Cambia esto a la ruta donde tienes los modelos
    
#     # Crear un archivo temporal para la salida JSON
#     with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
#         json_output_path = tmp_file.name
    
#     # Comando para ejecutar whisper.cpp con salida JSON
#     cmd = [
#         whisper_cpp_path,
#         "-m", model_path,
#         "-f", file_path,
#         "-oj", json_output_path,
#         "-l", "auto",  # Detección automática de idioma
#         "-pc",  # Mostrar progreso en la consola
#         "-pp",  # Procesar palabras por separado para mejor precisión
#         "-of", "srt"  # Formato de salida
#     ]
    
#     print(f"Ejecutando transcripción con whisper.cpp...")
#     process = subprocess.run(cmd, capture_output=True, text=True)
    
#     if process.returncode != 0:
#         print(f"Error al ejecutar whisper.cpp: {process.stderr}")
#         return None
    
#     # Leer el JSON de salida
#     with open(json_output_path, 'r', encoding='utf-8') as f:
#         result = json.load(f)
    
#     # Obtener la duración total del audio
#     audio = AudioSegment.from_file(file_path)
#     total_duration = len(audio) / 1000  # Convertir de ms a segundos
    
#     # Agrupar los segmentos en intervalos de 5 minutos
#     five_minutes_in_seconds = 5 * 60
#     five_minute_segments = {}
    
#     for segment in result.get('segments', []):
#         # Determinar a qué intervalo de 5 minutos pertenece este segmento
#         start_time = segment.get('start', 0)
#         interval_start = (int(start_time) // five_minutes_in_seconds) * five_minutes_in_seconds
        
#         # Si este intervalo no existe todavía, crearlo
#         if interval_start not in five_minute_segments:
#             five_minute_segments[interval_start] = []
        
#         # Añadir el texto a este intervalo
#         text = segment.get('text', '').strip()
#         if text:
#             five_minute_segments[interval_start].append(text)
    
#     # Crear el contenido SRT
#     srt_content = []
#     current_index = 1
#     sorted_intervals = sorted(five_minute_segments.keys())
    
#     for i, interval_start in enumerate(sorted_intervals):
#         start_time = format_time_srt(interval_start)
        
#         # El final de este intervalo es el inicio del siguiente, o la duración total
#         if i < len(sorted_intervals) - 1:
#             end_time = format_time_srt(sorted_intervals[i+1])
#         else:
#             end_time = format_time_srt(total_duration)
        
#         # Unir todos los textos de este intervalo
#         text = " ".join(five_minute_segments[interval_start])
        
#         # Crear la entrada SRT
#         srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#         current_index += 1
    
#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)
    
#     print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
#     # Limpiar el archivo temporal
#     os.unlink(json_output_path)
    
#     # Devolver el texto completo
#     all_texts = []
#     for interval in sorted_intervals:
#         all_texts.extend(five_minute_segments[interval])
#     return " ".join(all_texts)

# # Ejemplo de uso
# if __name__ == "__main__":
#     audio_file = "data/audio.wav"  # Cambia esto a la ruta de tu archivo de audio
#     output_file = "transcripcion.srt"     # Nombre del archivo de salida
#     transcribe_audio_to_srt(audio_file, output_file)

# import os
# import whisperx
# import torch
# from pydub import AudioSegment

# def format_time_srt(seconds):
#     """Convierte segundos a formato SRT hh:mm:ss,ms"""
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     seconds_int = int(seconds % 60)
#     milliseconds = int((seconds % 1) * 1000)
#     return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

# def transcribe_audio_to_srt(file_path, output_srt_path, model_size="base"):
#     """Transcribe un archivo de audio usando WhisperX y guarda en un archivo SRT con segmentos de 5 minutos."""
    
#     # Verifica que el archivo exista
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"El archivo {file_path} no existe")
    
#     # Determinar el dispositivo a usar
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     compute_type = "float16" if device == "cuda" else "int8"
    
#     print(f"Cargando modelo WhisperX {model_size}...")
#     # Cargar el modelo WhisperX
#     model = whisperx.load_model(model_size, device, compute_type=compute_type)
    
#     print(f"Transcribiendo audio con WhisperX...")
#     # Transcribir el audio
#     result = whisperx.transcribe(model, file_path, language="auto")
    
#     # Cargar el audio para obtener la duración total
#     audio = AudioSegment.from_file(file_path)
#     total_duration = len(audio) / 1000  # Convertir de ms a segundos
    
#     # Agrupar los segmentos en intervalos de 5 minutos
#     five_minutes_in_seconds = 5 * 60
#     five_minute_segments = {}
    
#     # Los segmentos en WhisperX están en result['segments']
#     for segment in result.get('segments', []):
#         # Determinar a qué intervalo de 5 minutos pertenece este segmento
#         start_time = segment.get('start', 0)
#         interval_start = (int(start_time) // five_minutes_in_seconds) * five_minutes_in_seconds
        
#         # Si este intervalo no existe todavía, crearlo
#         if interval_start not in five_minute_segments:
#             five_minute_segments[interval_start] = []
        
#         # Añadir el texto a este intervalo
#         text = segment.get('text', '').strip()
#         if text:
#             five_minute_segments[interval_start].append(text)
    
#     # Crear el contenido SRT
#     srt_content = []
#     current_index = 1
#     sorted_intervals = sorted(five_minute_segments.keys())
    
#     for i, interval_start in enumerate(sorted_intervals):
#         start_time = format_time_srt(interval_start)
        
#         # El final de este intervalo es el inicio del siguiente, o la duración total
#         if i < len(sorted_intervals) - 1:
#             end_time = format_time_srt(sorted_intervals[i+1])
#         else:
#             end_time = format_time_srt(total_duration)
        
#         # Unir todos los textos de este intervalo
#         text = " ".join(five_minute_segments[interval_start])
        
#         # Crear la entrada SRT
#         srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
#         current_index += 1
    
#     # Guardar en archivo SRT
#     with open(output_srt_path, "w", encoding="utf-8") as srt_file:
#         srt_file.writelines(srt_content)
    
#     print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")
    
#     # Devolver el texto completo
#     all_texts = []
#     for interval in sorted_intervals:
#         all_texts.extend(five_minute_segments[interval])
#     return " ".join(all_texts)

# # Ejemplo de uso
# if __name__ == "__main__":
#     audio_file = "data/audio.wav"  # Cambia esto a la ruta de tu archivo de audio
#     output_file = "transcripcion.srt"     # Nombre del archivo de salida
#     transcribe_audio_to_srt(audio_file, output_file)

import os
import whisperx
import torch
from pydub import AudioSegment

def format_time_srt(seconds):
    """Convierte segundos a formato SRT hh:mm:ss,ms"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds_int = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"

def transcribe_audio_to_srt(file_path, output_srt_path, model_size="base"):
    """Transcribe un archivo de audio usando WhisperX y guarda en un archivo SRT con segmentos de 5 minutos."""

    # Verifica que el archivo exista
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")

    # Determinar el dispositivo a usar
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"

    print(f"Cargando modelo WhisperX {model_size}...")
    # Cargar el modelo WhisperX
    model = whisperx.load_model(model_size, device=device, compute_type=compute_type)

    print(f"Transcribiendo audio con WhisperX...")
    # Transcribir el audio
    result = model.transcribe(file_path)

    # Cargar el audio para obtener la duración total
    audio = AudioSegment.from_file(file_path)
    total_duration = len(audio) / 1000  # Convertir de ms a segundos

    # Agrupar los segmentos en intervalos de 5 minutos
    five_minutes_in_seconds = 5 * 60
    five_minute_segments = {}

    # Los segmentos en WhisperX están en result['segments']
    for segment in result.get('segments', []):
        # Determinar a qué intervalo de 5 minutos pertenece este segmento
        start_time = segment.get('start', 0)
        interval_start = (int(start_time) // five_minutes_in_seconds) * five_minutes_in_seconds

        # Si este intervalo no existe todavía, crearlo
        if interval_start not in five_minute_segments:
            five_minute_segments[interval_start] = []

        # Añadir el texto a este intervalo
        text = segment.get('text', '').strip()
        if text:
            five_minute_segments[interval_start].append(text)

    # Crear el contenido SRT
    srt_content = []
    current_index = 1
    sorted_intervals = sorted(five_minute_segments.keys())

    for i, interval_start in enumerate(sorted_intervals):
        start_time = format_time_srt(interval_start)

        # El final de este intervalo es el inicio del siguiente, o la duración total
        if i < len(sorted_intervals) - 1:
            end_time = format_time_srt(sorted_intervals[i+1])
        else:
            end_time = format_time_srt(total_duration)

        # Unir todos los textos de este intervalo
        text = " ".join(five_minute_segments[interval_start])

        # Crear la entrada SRT
        srt_content.append(f"{current_index}\n{start_time} --> {end_time}\n{text}\n\n")
        current_index += 1

    # Guardar en archivo SRT
    with open(output_srt_path, "w", encoding="utf-8") as srt_file:
        srt_file.writelines(srt_content)

    print(f"Transcripción en segmentos de 5 minutos guardada en {output_srt_path}")

    # Devolver el texto completo
    all_texts = []
    for interval in sorted_intervals:
        all_texts.extend(five_minute_segments[interval])
    return " ".join(all_texts)

# Ejemplo de uso
if __name__ == "__main__":
    audio_file = "data/audio.wav"  # Cambia esto a la ruta de tu archivo de audio
    output_file = "transcripcion.srt"     # Nombre del archivo de salida
    transcribe_audio_to_srt(audio_file, output_file)
